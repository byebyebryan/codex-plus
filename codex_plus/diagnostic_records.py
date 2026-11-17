"""Pure accounting for explicitly selected native Codex turns.

The caller owns episode selection, native-history reading, and parent/child
boundary checks.  ``summarize`` consumes already parsed records and does not
read files or infer which turns belong to an episode.

Schema version 1 returns per-thread and per-turn usage, explicit coverage,
event evidence, and aggregates by the actual turn-context model/effort.  Usage
category totals contain an ``unambiguous_sum`` of identified, valid,
non-conflicting response records.  ``complete`` says whether that category is
present for every supplied per-response record in the selected turn(s); a
partial sum is never presented as an exact total.  A null sum means there was
no unambiguous value to sum.  These checks describe only the records supplied
by the caller and do not establish that the source files or episode boundaries
were complete.

Only ``payload.usage`` on ``token_usage_record`` contributes consumption.
Cumulative snapshots and token-count notifications are counted as evidence,
but never added to response usage.  The other native cumulative usage fields
are ignored.
"""

from collections import Counter
from collections.abc import Iterable, Mapping


TOKEN_CATEGORIES = (
    "input_tokens",
    "cached_input_tokens",
    "cache_write_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
    "total_tokens",
)

_MISSING = object()
_EVENT_STATES = {
    "task_started": "started",
    "task_complete": "completed",
    "turn_aborted": "aborted",
    "error": "error",
    "turn_error": "error",
}


def summarize(records_by_thread, selected_turns, *, primary_thread_id):
    """Summarize usage and event evidence for explicitly selected turns.

    Args:
        records_by_thread: Mapping of native thread IDs to one-pass iterables
            of parsed native JSONL dictionaries.
        selected_turns: Mapping of included thread IDs to explicit turn-ID
            iterables.  Records for all other turns and threads are ignored.
        primary_thread_id: Thread ID whose selected turns are primary work;
            every other selected thread is reported as a worker.

    The response identity is the owning thread, selected turn, and response
    ID.  A supplied or preceding ``session_meta.payload.id`` is checked as an
    additional identity component.  Exact repeats count once.  A changed
    usage payload or session identity for the same response is a conflict and
    the response is excluded from unambiguous usage.

    The input records must be native-shaped mappings.  Invalid records are
    represented by fixed issue codes; argument/container contract violations
    raise ``TypeError`` or ``ValueError``.
    """
    _validate_inputs(records_by_thread, selected_turns, primary_thread_id)

    selected = {}
    for thread_id, turns in selected_turns.items():
        # Selection sets are intentionally small; materializing only the
        # caller-selected IDs keeps the history side streaming.
        turn_ids = list(turns)
        for turn_id in turn_ids:
            if not _usable_id(turn_id):
                raise ValueError("selected turn IDs must be nonempty strings")
        unique_turns = set(turn_ids)
        selected[thread_id] = {
            turn_id: _new_turn(turn_id) for turn_id in sorted(unique_turns)
        }

    thread_data = {}
    for thread_id in sorted(selected):
        turns = selected[thread_id]
        thread_issues = Counter()
        thread_events = Counter()
        unscoped_events = Counter()
        cumulative_snapshots = 0
        current_session_id = None
        thread_data[thread_id] = {
            "turns": turns,
            "issues": thread_issues,
            "events": thread_events,
            "unscoped_events": unscoped_events,
            "cumulative_snapshots": 0,
            "unjoined_usage_gap_count": 0,
        }

        stream = records_by_thread.get(thread_id, ())
        try:
            iterator = iter(stream)
        except TypeError:
            thread_issues[("invalid_record_stream", None)] += 1
            continue

        for record in iterator:
            if not isinstance(record, Mapping):
                thread_issues[("malformed_record", None)] += 1
                thread_data[thread_id]["unjoined_usage_gap_count"] += 1
                continue

            record_type = record.get("type")
            payload = record.get("payload", {})
            if not isinstance(payload, Mapping):
                payload = {}

            if record_type == "session_meta":
                meta_thread = payload.get("thread_id", record.get("thread_id", _MISSING))
                if meta_thread is not _MISSING and meta_thread != thread_id:
                    thread_issues[("foreign_thread_session_identity", None)] += 1
                    continue
                session_id = payload.get("id", payload.get("session_id", _MISSING))
                if _usable_id(session_id):
                    current_session_id = session_id
                elif session_id is not _MISSING and session_id is not None:
                    thread_issues[("invalid_session_identity", None)] += 1
                    current_session_id = None
                continue

            if record_type == "turn_context":
                turn_id = payload.get("turn_id")
                if not _usable_id(turn_id) or turn_id not in turns:
                    continue
                context_thread = payload.get("thread_id", _MISSING)
                if context_thread is not _MISSING and context_thread != thread_id:
                    thread_issues[("foreign_thread_context", None)] += 1
                    continue
                turns[turn_id]["context_values"]["model"].append(
                    _context_text(payload.get("model", _MISSING))
                )
                turns[turn_id]["context_values"]["effort"].append(
                    _context_text(payload.get("effort", _MISSING))
                )
                continue

            if record_type == "token_usage_record":
                supplied_thread = payload.get("thread_id", _MISSING)
                thread_identity_valid = _usable_id(supplied_thread)
                if thread_identity_valid and supplied_thread != thread_id:
                    thread_issues[("foreign_thread_usage", None)] += 1
                    continue

                turn_id = payload.get("turn_id")
                if not _usable_id(turn_id):
                    thread_issues[("missing_turn_identity", None)] += 1
                    if not thread_identity_valid:
                        issue = "missing_thread_identity" if supplied_thread is _MISSING else "invalid_thread_identity"
                        thread_issues[(issue, None)] += 1
                    thread_data[thread_id]["unjoined_usage_gap_count"] += 1
                    continue
                if turn_id not in turns:
                    continue
                if not thread_identity_valid:
                    issue = "missing_thread_identity" if supplied_thread is _MISSING else "invalid_thread_identity"
                    thread_issues[(issue, None)] += 1
                    thread_data[thread_id]["unjoined_usage_gap_count"] += 1
                    continue

                turn = turns[turn_id]
                turn["record_count"] += 1
                raw_usage = payload.get("usage", _MISSING)
                values, missing_fields, invalid_fields, inconsistent_fields, shape_invalid = (
                    _validate_usage(raw_usage)
                )
                response_id = payload.get("response_id", _MISSING)
                if not _usable_id(response_id):
                    turn["missing_identity_record_count"] += 1
                    turn["issues"][("missing_response_identity", None)] += 1
                    _add_usage_issues(
                        turn["issues"], missing_fields, invalid_fields,
                        inconsistent_fields, shape_invalid,
                    )
                    if invalid_fields or inconsistent_fields or shape_invalid:
                        turn["invalid_unidentified_usage_count"] += 1
                    continue

                session_present = "session_id" in payload
                explicit_session = payload.get("session_id", _MISSING)
                if session_present:
                    if _usable_id(explicit_session):
                        session_id = explicit_session
                        if current_session_id is not None and session_id != current_session_id:
                            turn["issues"][("session_context_mismatch", None)] += 1
                    else:
                        session_id = None
                        if explicit_session is not None:
                            turn["issues"][("invalid_session_identity", None)] += 1
                else:
                    session_id = current_session_id

                signature = _usage_signature(raw_usage)
                group = turn["responses"].get(response_id)
                validation_issues = _usage_issue_keys(
                    missing_fields, invalid_fields, inconsistent_fields, shape_invalid
                )
                if group is None:
                    turn["responses"][response_id] = {
                        "signature": signature,
                        "session_id": session_id,
                        "values": values,
                        "missing_fields": set(missing_fields),
                        "invalid": bool(invalid_fields or inconsistent_fields or shape_invalid),
                        "conflict": False,
                        "exact_duplicate_count": 0,
                        "conflicting_duplicate_count": 0,
                        "issues": Counter(validation_issues),
                    }
                else:
                    same_payload = _same_signature(group["signature"], signature)
                    same_session = group["session_id"] == session_id
                    if same_payload and same_session:
                        group["exact_duplicate_count"] += 1
                    else:
                        group["conflict"] = True
                        group["conflicting_duplicate_count"] += 1
                        group["issues"][("conflicting_duplicate_response", None)] += 1
                    group["issues"].update(validation_issues)
                    group["missing_fields"].update(missing_fields)
                    if invalid_fields or inconsistent_fields or shape_invalid:
                        group["invalid"] = True
                continue

            event_type, event_payload = _event_payload(record_type, record, payload)
            candidate_turn_id = event_payload.get("turn_id")
            if _usable_id(candidate_turn_id) and candidate_turn_id not in turns:
                continue
            if event_type is not None and not isinstance(event_type, str):
                event_thread = event_payload.get("thread_id", _MISSING)
                if event_thread is not _MISSING and event_thread != thread_id:
                    thread_issues[("foreign_thread_event", None)] += 1
                    continue
                thread_issues[("malformed_event_type", None)] += 1
                continue
            if record_type == "event_msg" and event_type is None:
                event_thread = event_payload.get("thread_id", _MISSING)
                if event_thread is not _MISSING and event_thread != thread_id:
                    thread_issues[("foreign_thread_event", None)] += 1
                    continue
                thread_issues[("malformed_event_type", None)] += 1
                continue
            if event_type == "token_count":
                event_thread = event_payload.get("thread_id", _MISSING)
                if event_thread is not _MISSING and event_thread != thread_id:
                    thread_issues[("foreign_thread_event", None)] += 1
                    continue
                cumulative_snapshots += 1
                thread_data[thread_id]["cumulative_snapshots"] = cumulative_snapshots
                event_turn_id = event_payload.get("turn_id")
                if _usable_id(event_turn_id) and event_turn_id in turns:
                    turns[event_turn_id]["cumulative_snapshot_count"] += 1
                continue

            state = _EVENT_STATES.get(event_type)
            if state is None:
                continue
            event_thread = event_payload.get("thread_id", _MISSING)
            if event_thread is not _MISSING and event_thread != thread_id:
                thread_issues[("foreign_thread_event", None)] += 1
                continue
            turn_id = event_payload.get("turn_id")
            if not _usable_id(turn_id):
                unscoped_events[state] += 1
                thread_issues[("unscoped_event_without_turn_id", None)] += 1
                continue
            if turn_id not in turns:
                continue
            turns[turn_id]["events"][state] = True
            turns[turn_id]["event_occurrences"][state] += 1
            thread_events[state] += 1

    # Resolve model/effort context only from matching selected turn_context
    # records.  Missing and conflicting fields remain unknown.
    for thread_id, data in thread_data.items():
        for turn_id, turn in data["turns"].items():
            model, model_status = _resolve_context(turn["context_values"]["model"])
            effort, effort_status = _resolve_context(turn["context_values"]["effort"])
            turn["model"] = model
            turn["effort"] = effort
            turn["model_context_status"] = model_status
            turn["effort_context_status"] = effort_status
            if model_status == "conflict":
                turn["issues"][("conflicting_model_context", None)] += 1
            elif model_status == "missing":
                turn["issues"][("missing_model_context", None)] += 1
            if effort_status == "conflict":
                turn["issues"][("conflicting_effort_context", None)] += 1
            elif effort_status == "missing":
                turn["issues"][("missing_effort_context", None)] += 1
            if model_status == "conflict" or effort_status == "conflict":
                turn["context_status"] = "conflict"
            elif model_status == "known" and effort_status == "known":
                turn["context_status"] = "known"
            else:
                turn["context_status"] = "missing"

            if turn["record_count"] == 0:
                turn["issues"][("no_per_response_usage_records", None)] += 1

            for group in turn["responses"].values():
                if group["conflict"]:
                    group["issues"][("conflicting_duplicate_response", None)] += 0
                if group["conflict"] or group["invalid"]:
                    continue
                if not any(category in group["values"] for category in TOKEN_CATEGORIES):
                    continue
                if model_status != "known":
                    turn["issues"][("valid_usage_missing_model_join", None)] += 1
                if effort_status != "known":
                    turn["issues"][("valid_usage_missing_effort_join", None)] += 1

            turn["category_summary"] = _summarize_categories(turn)
            turn["usage_status"] = _usage_status(turn)
            reasons = []
            if turn["record_count"] == 0:
                reasons.append("no_per_response_usage_records")
            if turn["usage_status"] != "complete":
                reasons.append("usage_incomplete")
            if turn["context_status"] == "missing":
                reasons.append("model_effort_context_missing")
            elif turn["context_status"] == "conflict":
                reasons.append("model_effort_context_conflict")
            turn["coverage"] = {
                "status": "complete" if not reasons else "incomplete",
                "usage_status": turn["usage_status"],
                "context_status": turn["context_status"],
                "reason_codes": sorted(set(reasons)),
            }

    return _build_summary(thread_data, primary_thread_id)


def _validate_inputs(records_by_thread, selected_turns, primary_thread_id):
    if not isinstance(records_by_thread, Mapping):
        raise TypeError("records_by_thread must be a mapping")
    if not isinstance(selected_turns, Mapping):
        raise TypeError("selected_turns must be a mapping")
    if not _usable_id(primary_thread_id):
        raise ValueError("primary_thread_id must be a nonempty string")
    for thread_id in selected_turns:
        if not _usable_id(thread_id):
            raise ValueError("selected thread IDs must be nonempty strings")
        turns = selected_turns[thread_id]
        if isinstance(turns, (str, bytes)) or not isinstance(turns, Iterable):
            raise TypeError("selected turns must be iterables of turn IDs")
    for thread_id in records_by_thread:
        if not _usable_id(thread_id):
            raise ValueError("record thread IDs must be nonempty strings")


def _new_turn(turn_id):
    return {
        "turn_id": turn_id,
        "context_values": {"model": [], "effort": []},
        "responses": {},
        "record_count": 0,
        "missing_identity_record_count": 0,
        "invalid_unidentified_usage_count": 0,
        "cumulative_snapshot_count": 0,
        "events": {state: False for state in ("started", "completed", "aborted", "error")},
        "event_occurrences": Counter(),
        "issues": Counter(),
    }


def _usable_id(value):
    return isinstance(value, str) and bool(value.strip())


def _context_text(value):
    return value if _usable_id(value) else None


def _resolve_context(candidates):
    if not candidates:
        return None, "missing"
    known = {value for value in candidates if value is not None}
    if len(known) > 1:
        return None, "conflict"
    if len(known) == 1 and all(value is not None for value in candidates):
        return next(iter(known)), "known"
    return None, "missing"


def _event_payload(record_type, record, payload):
    if record_type == "event_msg":
        return payload.get("type"), payload
    # Also accept a minimal adapter projection that flattens the event name.
    if isinstance(record_type, str) and (record_type == "token_count" or record_type in _EVENT_STATES):
        return record_type, record
    return None, {}


def _validate_usage(raw_usage):
    if not isinstance(raw_usage, Mapping):
        return {}, [], [], [], True

    values = {}
    missing_fields = []
    invalid_fields = []
    for category in TOKEN_CATEGORIES:
        if category not in raw_usage:
            missing_fields.append(category)
            continue
        value = raw_usage[category]
        if type(value) is not int or value < 0:
            invalid_fields.append(category)
            continue
        values[category] = value

    inconsistent_fields = []
    input_tokens = values.get("input_tokens")
    cached_tokens = values.get("cached_input_tokens")
    output_tokens = values.get("output_tokens")
    reasoning_tokens = values.get("reasoning_output_tokens")
    total_tokens = values.get("total_tokens")
    if input_tokens is not None and cached_tokens is not None and input_tokens < cached_tokens:
        inconsistent_fields.append("input_tokens")
    if output_tokens is not None and reasoning_tokens is not None and output_tokens < reasoning_tokens:
        inconsistent_fields.append("output_tokens")
    if input_tokens is not None and output_tokens is not None and total_tokens is not None:
        if total_tokens != input_tokens + output_tokens:
            inconsistent_fields.append("total_tokens")
    return values, missing_fields, invalid_fields, inconsistent_fields, False


def _usage_signature(raw_usage):
    if raw_usage is _MISSING:
        return ("missing_usage",)
    if not isinstance(raw_usage, Mapping):
        return ("invalid_shape", type(raw_usage).__name__, raw_usage)
    return tuple(
        (
            category,
            category in raw_usage,
            type(raw_usage.get(category)).__name__ if category in raw_usage else None,
            raw_usage.get(category) if category in raw_usage else None,
        )
        for category in TOKEN_CATEGORIES
    )


def _same_signature(left, right):
    try:
        return left == right
    except Exception:
        return False


def _usage_issue_keys(missing_fields, invalid_fields, inconsistent_fields, shape_invalid):
    result = Counter()
    if shape_invalid:
        result[("invalid_usage_shape", None)] += 1
    for field in missing_fields:
        result[("missing_token_category", field)] += 1
    for field in invalid_fields:
        result[("invalid_token_category", field)] += 1
    for field in inconsistent_fields:
        result[("inconsistent_token_categories", field)] += 1
    if invalid_fields or inconsistent_fields or shape_invalid:
        result[("invalid_usage", None)] += 1
    return result


def _add_usage_issues(counter, missing_fields, invalid_fields, inconsistent_fields, shape_invalid):
    counter.update(_usage_issue_keys(missing_fields, invalid_fields, inconsistent_fields, shape_invalid))


def _summarize_categories(turn):
    groups = list(turn["responses"].values())
    has_unidentified = turn["missing_identity_record_count"] > 0
    category_summary = {}
    for category in TOKEN_CATEGORIES:
        observed = []
        complete = turn["record_count"] > 0 and not has_unidentified
        for group in groups:
            if group["conflict"] or group["invalid"]:
                complete = False
                continue
            if category not in group["values"]:
                complete = False
                continue
            observed.append(group["values"][category])
        category_summary[category] = {
            "unambiguous_sum": sum(observed) if observed else None,
            "complete": bool(complete),
        }
    return category_summary


def _usage_status(turn):
    if turn["record_count"] == 0:
        return "no_per_response_usage_records"
    if all(item["complete"] for item in turn["category_summary"].values()):
        return "complete"
    return "incomplete"


def _sum_category_summaries(summaries, *, require_nonempty=True):
    result = {}
    summaries = list(summaries)
    for category in TOKEN_CATEGORIES:
        values = [summary[category]["unambiguous_sum"] for summary in summaries]
        known_values = [value for value in values if value is not None]
        complete = bool(summaries) and all(
            summary[category]["complete"] for summary in summaries
        )
        if require_nonempty and not summaries:
            complete = False
        result[category] = {
            "unambiguous_sum": sum(known_values) if known_values else None,
            "complete": complete,
        }
    return result


def _issue_rows(counter):
    rows = []
    for (code, field), count in sorted(counter.items(), key=lambda item: (item[0][0], item[0][1] or "")):
        if not count:
            continue
        row = {"code": code, "count": count}
        if field is not None:
            row["field"] = field
        rows.append(row)
    return rows


def _counter_for(turn):
    counter = Counter(turn["issues"])
    response_groups = list(turn["responses"].values())
    for group in response_groups:
        counter.update(group["issues"])
    return counter


def _turn_usage_output(turn):
    responses = list(turn["responses"].values())
    return {
        "per_response_record_count": turn["record_count"],
        "unique_response_count": len(responses),
        "exact_duplicate_record_count": sum(
            group["exact_duplicate_count"] for group in responses
        ),
        "conflicting_duplicate_record_count": sum(
            group["conflicting_duplicate_count"] for group in responses
        ),
        "conflicting_response_count": sum(1 for group in responses if group["conflict"]),
        "invalid_usage_response_count": sum(1 for group in responses if group["invalid"]),
        "missing_response_identity_record_count": turn["missing_identity_record_count"],
        "invalid_unidentified_usage_record_count": turn["invalid_unidentified_usage_count"],
        "cumulative_snapshot_count": turn["cumulative_snapshot_count"],
        "categories": turn["category_summary"],
    }


def _build_summary(thread_data, primary_thread_id):
    thread_rows = []
    all_turns = []
    global_issues = Counter()
    global_event_occurrences = Counter()
    global_unscoped_events = Counter()
    context_groups = {}

    for thread_id in sorted(thread_data):
        data = thread_data[thread_id]
        actor = "primary" if thread_id == primary_thread_id else "worker"
        turn_rows = []
        turn_category_summaries = []
        thread_issue_counts = Counter(data["issues"])
        thread_event_occurrences = Counter(data["events"])
        for turn_id in sorted(data["turns"]):
            turn = data["turns"][turn_id]
            turn_issue_counts = _counter_for(turn)
            thread_issue_counts.update(turn_issue_counts)
            turn_categories = turn["category_summary"]
            turn_category_summaries.append(turn_categories)
            all_turns.append(turn)

            global_event_occurrences.update(turn["event_occurrences"])
            context_key = (
                actor,
                turn["model"],
                turn["effort"],
                turn["context_status"],
            )
            context_group = context_groups.setdefault(context_key, {
                "actor": actor,
                "model": turn["model"],
                "effort": turn["effort"],
                "context_status": turn["context_status"],
                "turn_summaries": [],
                "selected_turn_count": 0,
                "valid_response_count": 0,
                "per_response_record_count": 0,
            })
            context_group["turn_summaries"].append(turn_categories)
            context_group["selected_turn_count"] += 1
            context_group["valid_response_count"] += sum(
                1 for group in turn["responses"].values()
                if not group["conflict"] and not group["invalid"]
                and any(category in group["values"] for category in TOKEN_CATEGORIES)
            )
            context_group["per_response_record_count"] += turn["record_count"]

            turn_rows.append({
                "turn_id": turn_id,
                "model": turn["model"],
                "effort": turn["effort"],
                "model_context_status": turn["model_context_status"],
                "effort_context_status": turn["effort_context_status"],
                "context_status": turn["context_status"],
                "events": dict(turn["events"]),
                "coverage": turn["coverage"],
                "usage_status": turn["usage_status"],
                "usage": _turn_usage_output(turn),
                "issues": _issue_rows(turn_issue_counts),
            })

        global_issues.update(thread_issue_counts)
        global_unscoped_events.update(data["unscoped_events"])
        selected_turn_count = len(turn_rows)
        complete_turn_count = sum(
            1 for turn in data["turns"].values()
            if turn["coverage"]["status"] == "complete"
        )
        thread_coverage = _coverage_summary(selected_turn_count, complete_turn_count)
        if data["unjoined_usage_gap_count"]:
            thread_coverage = _coverage_with_unjoined_gap(
                thread_coverage, data["unjoined_usage_gap_count"]
            )
        thread_categories = _sum_category_summaries(turn_category_summaries)
        if data["unjoined_usage_gap_count"]:
            _mark_categories_incomplete(thread_categories)
        thread_rows.append({
            "thread_id": thread_id,
            "actor": actor,
            "selected_turn_count": selected_turn_count,
            "coverage": thread_coverage,
            "usage": {
                "categories": thread_categories,
            },
            "events": {
                "observed_counts": dict(sorted(thread_event_occurrences.items())),
                "selected_turn_counts": _event_turn_counts(data["turns"].values()),
                "unscoped_counts": dict(sorted(data["unscoped_events"].items())),
            },
            "turns": turn_rows,
            "issues": _issue_rows(thread_issue_counts),
        })

    context_rows = []
    for key in sorted(context_groups, key=lambda value: tuple("" if part is None else str(part) for part in value)):
        group = context_groups[key]
        context_rows.append({
            "actor": group["actor"],
            "model": group["model"],
            "effort": group["effort"],
            "context_status": group["context_status"],
            "selected_turn_count": group["selected_turn_count"],
            "per_response_record_count": group["per_response_record_count"],
            "valid_response_count": group["valid_response_count"],
            "categories": _sum_category_summaries(group["turn_summaries"]),
        })

    selected_turn_count = len(all_turns)
    complete_turn_count = sum(
        1 for turn in all_turns if turn["coverage"]["status"] == "complete"
    )
    top_coverage = _coverage_summary(selected_turn_count, complete_turn_count)
    all_category_summaries = [turn["category_summary"] for turn in all_turns]
    total_categories = _sum_category_summaries(all_category_summaries)
    unjoined_usage_gaps = sum(
        data["unjoined_usage_gap_count"] for data in thread_data.values()
    )
    if unjoined_usage_gaps:
        top_coverage = _coverage_with_unjoined_gap(top_coverage, unjoined_usage_gaps)
        _mark_categories_incomplete(total_categories)
    cumulative_snapshot_count = sum(
        data["cumulative_snapshots"] for data in thread_data.values()
    )
    return {
        "schema_version": 1,
        "scope": "explicit_selected_turns_only",
        "primary_thread_id": primary_thread_id,
        "coverage": top_coverage,
        "usage": {"categories": total_categories},
        "usage_by_context": context_rows,
        "events": {
            "observed_counts": dict(sorted(global_event_occurrences.items())),
            "selected_turn_counts": _event_turn_counts(all_turns),
            "unscoped_counts": dict(sorted(global_unscoped_events.items())),
            "cumulative_snapshot_count": cumulative_snapshot_count,
        },
        "threads": thread_rows,
        "issues": _issue_rows(global_issues),
    }


def _coverage_summary(selected_turn_count, complete_turn_count):
    if selected_turn_count == 0:
        status = "incomplete"
        reasons = ["no_selected_turns"]
    else:
        status = "complete" if complete_turn_count == selected_turn_count else "incomplete"
        reasons = [] if status == "complete" else ["selected_turn_coverage_incomplete"]
    return {
        "status": status,
        "basis": "supplied_records_only",
        "selected_turn_count": selected_turn_count,
        "complete_turn_count": complete_turn_count,
        "incomplete_turn_count": selected_turn_count - complete_turn_count,
        "reason_codes": reasons,
    }


def _coverage_with_unjoined_gap(coverage, count):
    result = dict(coverage)
    result["status"] = "incomplete"
    result["unjoined_usage_record_count"] = count
    result["reason_codes"] = sorted(set(result["reason_codes"] + ["unjoined_usage_record"]))
    return result


def _mark_categories_incomplete(categories):
    for category in TOKEN_CATEGORIES:
        categories[category]["complete"] = False


def _event_turn_counts(turns):
    turns = list(turns)
    return {
        state: sum(1 for turn in turns if turn["events"][state])
        for state in ("started", "completed", "aborted", "error")
    }
