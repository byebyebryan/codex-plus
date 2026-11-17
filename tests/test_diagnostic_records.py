import json
import unittest

from codex_plus.diagnostic_records import summarize


PRIMARY = "thread-maple"
CHILD = "thread-birch"
TURN_A = "turn-amber"
TURN_B = "turn-cobalt"
TURN_C = "turn-fern"


def usage_values(input_tokens=10, *, cached=3, cache_write=2, output=4, reasoning=1, total=None):
    if total is None:
        total = input_tokens + output
    return {
        "input_tokens": input_tokens,
        "cached_input_tokens": cached,
        "cache_write_input_tokens": cache_write,
        "output_tokens": output,
        "reasoning_output_tokens": reasoning,
        "total_tokens": total,
    }


def context(turn_id, model="sol-xhigh", effort="xhigh", *, thread_id=None):
    payload = {"turn_id": turn_id, "model": model, "effort": effort}
    if thread_id is not None:
        payload["thread_id"] = thread_id
    return {"type": "turn_context", "payload": payload}


def usage_record(turn_id, response_id="response-cedar", *, thread_id=PRIMARY,
                 values=None, session_id="session-neutral"):
    payload = {
        "thread_id": thread_id,
        "turn_id": turn_id,
        "response_id": response_id,
        "usage": usage_values() if values is None else dict(values),
    }
    if session_id is not None:
        payload["session_id"] = session_id
    return {"type": "token_usage_record", "payload": payload}


def event(kind, turn_id=None, *, message=None):
    payload = {"type": kind}
    if turn_id is not None:
        payload["turn_id"] = turn_id
    if message is not None:
        payload["message"] = message
    return {"type": "event_msg", "payload": payload}


def thread_row(result, thread_id):
    return next(row for row in result["threads"] if row["thread_id"] == thread_id)


def turn_row(result, thread_id, turn_id):
    return next(row for row in thread_row(result, thread_id)["turns"] if row["turn_id"] == turn_id)


def issue_codes(rows):
    return {row["code"] for row in rows}


class DiagnosticRecordTests(unittest.TestCase):
    def test_parent_and_child_multiturn_usage_sums_by_actor_and_actual_context(self):
        records = {
            PRIMARY: [
                context(TURN_A, "sol-xhigh", "xhigh"),
                context(TURN_B, "luna-max", "max"),
                usage_record(TURN_A, "response-cedar", values=usage_values(10)),
                usage_record(TURN_B, "response-elm", values=usage_values(20)),
                event("task_started", TURN_A),
                event("task_complete", TURN_A),
                event("task_started", TURN_B),
                event("task_complete", TURN_B),
            ],
            CHILD: [
                context(TURN_C, "luna-max", "max"),
                usage_record(TURN_C, "response-fir", thread_id=CHILD, values=usage_values(30)),
                event("task_complete", TURN_C),
            ],
        }
        result = summarize(
            records,
            {PRIMARY: [TURN_A, TURN_B], CHILD: [TURN_C]},
            primary_thread_id=PRIMARY,
        )

        self.assertEqual(result["schema_version"], 1)
        self.assertEqual(result["coverage"]["status"], "complete")
        self.assertEqual(result["usage"]["categories"]["input_tokens"], {
            "unambiguous_sum": 60, "complete": True,
        })
        self.assertEqual(thread_row(result, PRIMARY)["actor"], "primary")
        self.assertEqual(thread_row(result, CHILD)["actor"], "worker")
        self.assertEqual(turn_row(result, PRIMARY, TURN_A)["model"], "sol-xhigh")
        self.assertEqual(turn_row(result, PRIMARY, TURN_B)["model"], "luna-max")
        contexts = {
            (row["actor"], row["model"], row["effort"])
            for row in result["usage_by_context"]
        }
        self.assertEqual(contexts, {
            ("primary", "sol-xhigh", "xhigh"),
            ("primary", "luna-max", "max"),
            ("worker", "luna-max", "max"),
        })
        self.assertEqual(result["events"]["selected_turn_counts"]["completed"], 3)
        self.assertNotIn("accepted", result)
        json.dumps(result)

    def test_exact_duplicate_counts_once_and_conflicting_duplicate_is_excluded(self):
        records = [
            context(TURN_A),
            usage_record(TURN_A, "response-cedar", values=usage_values(10)),
            usage_record(TURN_A, "response-cedar", values=usage_values(10)),
            usage_record(TURN_A, "response-fir", values=usage_values(20)),
            usage_record(TURN_A, "response-fir", values=usage_values(21)),
        ]
        result = summarize({PRIMARY: records}, {PRIMARY: {TURN_A}}, primary_thread_id=PRIMARY)
        row = turn_row(result, PRIMARY, TURN_A)
        self.assertEqual(row["usage"]["per_response_record_count"], 4)
        self.assertEqual(row["usage"]["unique_response_count"], 2)
        self.assertEqual(row["usage"]["exact_duplicate_record_count"], 1)
        self.assertEqual(row["usage"]["conflicting_duplicate_record_count"], 1)
        self.assertEqual(row["usage"]["conflicting_response_count"], 1)
        self.assertEqual(row["usage"]["categories"]["input_tokens"], {
            "unambiguous_sum": 10, "complete": False,
        })
        self.assertIn("conflicting_duplicate_response", issue_codes(row["issues"]))

    def test_foreign_thread_copy_and_unselected_turn_are_not_attributed(self):
        copied = usage_record(TURN_A, "response-copied", thread_id=CHILD,
                              values=usage_values(999))
        records = [
            context(TURN_A),
            usage_record(TURN_A, "response-local", values=usage_values(10)),
            copied,
            usage_record("turn-earlier-unselected", "response-earlier", values=usage_values(700)),
            {"type": "token_usage_record", "payload": {
                "turn_id": "turn-unselected-without-owner",
                "response_id": "response-unselected",
                "usage": usage_values(800),
            }},
        ]
        result = summarize({PRIMARY: records}, {PRIMARY: [TURN_A]}, primary_thread_id=PRIMARY)
        self.assertEqual(result["usage"]["categories"]["input_tokens"], {
            "unambiguous_sum": 10, "complete": True,
        })
        self.assertIn("foreign_thread_usage", issue_codes(result["issues"]))
        self.assertEqual(turn_row(result, PRIMARY, TURN_A)["usage"]["unique_response_count"], 1)

    def test_cumulative_only_records_do_not_become_response_usage_or_exact_zero(self):
        records = [
            context(TURN_A),
            {"type": "event_msg", "payload": {
                "type": "token_count", "turn_id": TURN_A,
                "info": {"total_token_usage": usage_values(500)},
            }},
        ]
        result = summarize({PRIMARY: records}, {PRIMARY: [TURN_A]}, primary_thread_id=PRIMARY)
        row = turn_row(result, PRIMARY, TURN_A)
        self.assertEqual(row["usage_status"], "no_per_response_usage_records")
        self.assertEqual(row["usage"]["per_response_record_count"], 0)
        self.assertEqual(row["usage"]["cumulative_snapshot_count"], 1)
        self.assertIsNone(result["usage"]["categories"]["input_tokens"]["unambiguous_sum"])
        self.assertFalse(result["usage"]["categories"]["input_tokens"]["complete"])
        self.assertEqual(result["coverage"]["status"], "incomplete")
        self.assertIn("no_per_response_usage_records", issue_codes(row["issues"]))

    def test_mixed_model_contexts_missing_context_and_conflicting_context_are_visible(self):
        turn_missing = "turn-grove"
        turn_conflict = "turn-hazel"
        records = [
            context(TURN_A, "sol-xhigh", "xhigh"),
            context(TURN_B, "luna-max", "max"),
            context(turn_conflict, "sol-xhigh", "xhigh"),
            context(turn_conflict, "luna-max", "xhigh"),
            usage_record(TURN_A, "response-a", values=usage_values(10)),
            usage_record(TURN_B, "response-b", values=usage_values(20)),
            usage_record(turn_missing, "response-c", values=usage_values(30)),
            usage_record(turn_conflict, "response-d", values=usage_values(40)),
        ]
        result = summarize(
            {PRIMARY: records},
            {PRIMARY: [TURN_A, TURN_B, turn_missing, turn_conflict]},
            primary_thread_id=PRIMARY,
        )
        self.assertEqual(turn_row(result, PRIMARY, TURN_A)["model"], "sol-xhigh")
        self.assertEqual(turn_row(result, PRIMARY, TURN_B)["model"], "luna-max")
        self.assertEqual(turn_row(result, PRIMARY, turn_missing)["model_context_status"], "missing")
        self.assertEqual(turn_row(result, PRIMARY, turn_conflict)["model_context_status"], "conflict")
        self.assertEqual(result["usage"]["categories"]["input_tokens"]["unambiguous_sum"], 100)
        self.assertTrue(result["usage"]["categories"]["input_tokens"]["complete"])
        self.assertEqual(result["coverage"]["status"], "incomplete")
        self.assertIn("valid_usage_missing_model_join", issue_codes(result["issues"]))
        self.assertIn("conflicting_model_context", issue_codes(result["issues"]))
        self.assertIn("model_effort_context_missing", turn_row(result, PRIMARY, turn_missing)["coverage"]["reason_codes"])
        self.assertIn("model_effort_context_conflict", turn_row(result, PRIMARY, turn_conflict)["coverage"]["reason_codes"])

    def test_missing_category_is_unknown_while_supported_categories_remain_observed(self):
        partial = usage_values(10)
        del partial["cached_input_tokens"]
        result = summarize(
            {PRIMARY: [context(TURN_A), usage_record(TURN_A, values=partial)]},
            {PRIMARY: [TURN_A]},
            primary_thread_id=PRIMARY,
        )
        categories = turn_row(result, PRIMARY, TURN_A)["usage"]["categories"]
        self.assertEqual(categories["input_tokens"], {"unambiguous_sum": 10, "complete": True})
        self.assertEqual(categories["cached_input_tokens"], {"unambiguous_sum": None, "complete": False})
        self.assertEqual(categories["output_tokens"], {"unambiguous_sum": 4, "complete": True})
        self.assertIn("missing_token_category", issue_codes(turn_row(result, PRIMARY, TURN_A)["issues"]))

    def test_invalid_token_values_and_inconsistent_relations_are_excluded(self):
        cases = [
            ("boolean", {"input_tokens": True}, "input_tokens"),
            ("negative", {"input_tokens": -1}, "input_tokens"),
            ("noninteger", {"input_tokens": 1.5}, "input_tokens"),
            ("cached_exceeds_input", {"cached_input_tokens": 11}, "input_tokens"),
            ("reasoning_exceeds_output", {"reasoning_output_tokens": 5}, "output_tokens"),
            ("wrong_total", {"total_tokens": 99}, "total_tokens"),
        ]
        for name, replacements, field in cases:
            with self.subTest(name=name):
                values = usage_values(10)
                values.update(replacements)
                result = summarize(
                    {PRIMARY: [context(TURN_A), usage_record(TURN_A, values=values)]},
                    {PRIMARY: [TURN_A]},
                    primary_thread_id=PRIMARY,
                )
                row = turn_row(result, PRIMARY, TURN_A)
                self.assertEqual(row["usage"]["invalid_usage_response_count"], 1)
                self.assertIsNone(row["usage"]["categories"]["input_tokens"]["unambiguous_sum"])
                self.assertFalse(row["usage"]["categories"]["input_tokens"]["complete"])
                matching = [issue for issue in row["issues"] if issue.get("field") == field]
                self.assertTrue(matching)
                self.assertIn("invalid_usage", issue_codes(row["issues"]))

    def test_missing_response_identity_is_a_gap_and_not_usage(self):
        missing_id = usage_record(TURN_A, values=usage_values(15))
        del missing_id["payload"]["response_id"]
        result = summarize(
            {PRIMARY: [context(TURN_A), missing_id]},
            {PRIMARY: [TURN_A]},
            primary_thread_id=PRIMARY,
        )
        row = turn_row(result, PRIMARY, TURN_A)
        self.assertEqual(row["usage"]["missing_response_identity_record_count"], 1)
        self.assertIsNone(row["usage"]["categories"]["input_tokens"]["unambiguous_sum"])
        self.assertFalse(row["usage"]["categories"]["input_tokens"]["complete"])
        self.assertIn("missing_response_identity", issue_codes(row["issues"]))
        self.assertEqual(result["coverage"]["status"], "incomplete")

    def test_completion_is_not_acceptance_and_unscoped_abort_does_not_finish_selected_turn(self):
        records = [
            context(TURN_A),
            usage_record(TURN_A),
            event("task_complete", TURN_A),
            event("turn_aborted", message="invented diagnostic string"),
        ]
        result = summarize({PRIMARY: records}, {PRIMARY: [TURN_A]}, primary_thread_id=PRIMARY)
        turn = turn_row(result, PRIMARY, TURN_A)
        self.assertTrue(turn["events"]["completed"])
        self.assertFalse(turn["events"]["aborted"])
        self.assertNotIn("accepted", turn)
        self.assertEqual(result["events"]["unscoped_counts"]["aborted"], 1)
        self.assertIn("unscoped_event_without_turn_id", issue_codes(result["issues"]))
        self.assertNotIn("invented diagnostic string", json.dumps(result))

    def test_missing_payload_thread_identity_is_excluded_and_makes_coverage_incomplete(self):
        malformed = [
            ("missing", None, "missing_thread_identity"),
            ("null", None, "invalid_thread_identity"),
            ("wrong_type", [], "invalid_thread_identity"),
            ("blank", "  ", "invalid_thread_identity"),
        ]
        for name, thread_id, expected_issue in malformed:
            with self.subTest(name=name):
                record = usage_record(TURN_A)
                if name == "missing":
                    del record["payload"]["thread_id"]
                else:
                    record["payload"]["thread_id"] = thread_id
                result = summarize(
                    {PRIMARY: [context(TURN_A), record]},
                    {PRIMARY: [TURN_A]},
                    primary_thread_id=PRIMARY,
                )
                self.assertIsNone(result["usage"]["categories"]["input_tokens"]["unambiguous_sum"])
                self.assertFalse(result["usage"]["categories"]["input_tokens"]["complete"])
                self.assertEqual(result["coverage"]["status"], "incomplete")
                self.assertIn(expected_issue, issue_codes(result["issues"]))

    def test_malformed_event_type_cannot_complete_a_selected_turn(self):
        for malformed_type in (["task_complete"], {"name": "task_complete"}):
            with self.subTest(malformed_type=type(malformed_type).__name__):
                records = [
                    context(TURN_A),
                    usage_record(TURN_A),
                    {"type": "event_msg", "payload": {
                        "type": malformed_type, "turn_id": "turn-earlier-unselected",
                    }},
                    {"type": "event_msg", "payload": {
                        "type": malformed_type, "turn_id": TURN_A,
                    }},
                ]
                result = summarize({PRIMARY: records}, {PRIMARY: [TURN_A]}, primary_thread_id=PRIMARY)
                self.assertFalse(turn_row(result, PRIMARY, TURN_A)["events"]["completed"])
                self.assertIn("malformed_event_type", issue_codes(result["issues"]))
                self.assertEqual(
                    next(issue["count"] for issue in result["issues"] if issue["code"] == "malformed_event_type"),
                    1,
                )

    def test_session_meta_is_only_a_fallback_and_explicit_session_wins(self):
        records = [
            {"type": "session_meta", "payload": {"id": "session-copper"}},
            context(TURN_A),
            usage_record(TURN_A, "response-cedar", session_id=None, values=usage_values(10)),
            usage_record(TURN_A, "response-cedar", session_id="session-copper", values=usage_values(10)),
            usage_record(TURN_A, "response-fir", session_id="session-slate", values=usage_values(20)),
        ]
        result = summarize({PRIMARY: records}, {PRIMARY: [TURN_A]}, primary_thread_id=PRIMARY)
        row = turn_row(result, PRIMARY, TURN_A)
        self.assertEqual(row["usage"]["exact_duplicate_record_count"], 1)
        self.assertEqual(row["usage"]["categories"]["input_tokens"]["unambiguous_sum"], 30)
        self.assertIn("session_context_mismatch", issue_codes(row["issues"]))

    def test_streaming_record_iterable_is_consumed_once(self):
        consumed = []

        def record_stream():
            for record in (context(TURN_A), usage_record(TURN_A)):
                consumed.append(record["type"])
                yield record

        result = summarize(
            {PRIMARY: record_stream()},
            {PRIMARY: iter([TURN_A])},
            primary_thread_id=PRIMARY,
        )
        self.assertEqual(consumed, ["turn_context", "token_usage_record"])
        self.assertEqual(result["coverage"]["status"], "complete")


if __name__ == "__main__":
    unittest.main()
