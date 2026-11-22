"""Bounded, read-only projections of native records; never resume a thread."""
from __future__ import annotations

import json
import os
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sqlite3
import stat

MAX_BYTES = 64 * 1024 * 1024
MAX_LINE = 1024 * 1024
MAX_THREADS = 32
_NON_TURN_ENDING_ERROR_CODES = {'threadrollbackfailed', 'activeturnnotsteerable'}


def _error_terminal_classification(event_type, payload):
    """Project only whether an error ends its native turn; never retain details."""
    error = payload.get('error')
    for details in (payload, error):
        if not isinstance(details, dict):
            continue
        for key in ('codex_error_info', 'codexErrorInfo'):
            code = details.get(key)
            if isinstance(code, dict) and len(code) == 1:
                code = next(iter(code))
            if isinstance(code, str) and code.lower().replace('_', '') in _NON_TURN_ENDING_ERROR_CODES:
                return False

    retry = [payload[key] for key in ('will_retry', 'willRetry') if key in payload]
    if retry:
        # A retry or an inconsistent marker cannot establish a terminal error.
        if any(value is True for value in retry):
            return False
        return True if all(value is False for value in retry) else None
    return True if event_type == 'turn_error' else None


def identity(value):
    if not isinstance(value, str) or not value or len(value) > 128 or any(
            not (c.isalnum() or c in '-_.:') for c in value):
        raise ValueError('invalid native identity')
    return value


class NativeRecords:
    """One environment, no credential reads, no native writes or owner discovery."""
    def __init__(self, home):
        self.home = Path(home).resolve()
        self.remaining = 2 * MAX_BYTES

    def connect(self):
        path = self.home / 'state_5.sqlite'
        if path.is_symlink() or not path.is_file():
            raise ValueError('native index unavailable')
        connection = sqlite3.connect(path.as_uri() + '?mode=ro', uri=True, timeout=2)
        connection.execute('PRAGMA query_only=ON')
        return connection

    def thread(self, thread_id):
        identity(thread_id)
        with closing(self.connect()) as connection:
            row = connection.execute(
                'SELECT rollout_path, attached_thread_parent_id FROM threads WHERE id=?',
                (thread_id,)).fetchone()
            edge = connection.execute(
                'SELECT parent_thread_id FROM thread_spawn_edges WHERE child_thread_id=?',
                (thread_id,)).fetchall()
        if row is None or len(edge) > 1:
            raise ValueError('native thread identity or ancestry unavailable')
        parents = {p for p in [row[1], *(e[0] for e in edge)] if p}
        if len(parents) > 1:
            raise ValueError('native ancestry conflicts')
        path = Path(row[0])
        if path.is_symlink() or not path.resolve().is_relative_to(self.home):
            raise ValueError('native record path is outside selected environment')
        return path, next(iter(parents), None)

    def read(self, thread_id):
        path, parent = self.thread(thread_id)
        records, gaps = [], set()
        allowed = min(MAX_BYTES, self.remaining)
        if not allowed:
            return [], ['read_budget_exhausted'], parent
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        with os.fdopen(fd, 'rb') as stream:
            info = os.fstat(stream.fileno())
            if not stat.S_ISREG(info.st_mode):
                raise ValueError('native records must be a regular file')
            size = info.st_size
            start = max(0, size - allowed)
            stream.seek(start)
            if start:
                self.remaining -= len(stream.readline(MAX_LINE + 1))
                gaps.add('record_prefix_outside_read_bound')
            while stream.tell() < size:
                line = stream.readline(min(MAX_LINE + 1, size - stream.tell()))
                if not line:
                    gaps.add('native_file_shortened_during_read')
                    break
                self.remaining -= len(line)
                if len(line) > MAX_LINE:
                    gaps.add('oversized_native_line')
                    while line and not line.endswith(b'\n') and stream.tell() < size:
                        line = stream.readline(min(MAX_LINE + 1, size - stream.tell()))
                        self.remaining -= len(line)
                    continue
                if not line.endswith(b'\n'):
                    gaps.add('incomplete_native_line')
                    continue
                try:
                    record = json.loads(line)
                except (ValueError, UnicodeError):
                    gaps.add('malformed_native_line')
                    continue
                if not isinstance(record, dict) or not isinstance(record.get('type'), str):
                    gaps.add('malformed_native_record')
                    continue
                kind = record['type']
                if kind not in ('turn_context', 'token_usage_record', 'session_meta', 'event_msg'):
                    continue
                payload = record.get('payload')
                if not isinstance(payload, dict):
                    gaps.add('malformed_native_record'); continue
                thread_keys = ('thread_id', 'threadId') if kind == 'event_msg' else ('thread_id',)
                if any(key in payload and payload[key] != thread_id for key in thread_keys):
                    gaps.add('foreign_thread_native_record'); continue
                keys = {
                    'turn_context': ('thread_id', 'turn_id', 'root_turn_id', 'model', 'effort'),
                    'token_usage_record': ('thread_id', 'turn_id', 'session_id', 'root_turn_id',
                                           'response_id', 'usage'),
                    'session_meta': ('id', 'thread_id'),
                }.get(kind)
                if kind == 'event_msg':
                    keys = ('type', 'thread_id', 'turn_id', 'root_turn_id', 'started_at', 'completed_at')
                    if payload.get('type') not in ('task_started', 'task_complete', 'turn_aborted',
                                                   'error', 'turn_error', 'token_count'):
                        continue
                if keys:
                    projected = {k: payload[k] for k in keys if k in payload}
                    if kind == 'event_msg':
                        for snake, camel in (('thread_id', 'threadId'), ('turn_id', 'turnId')):
                            if snake not in projected and camel in payload:
                                projected[snake] = payload[camel]
                        if ('turn_id' in payload and 'turnId' in payload
                                and payload['turn_id'] != payload['turnId']):
                            projected.pop('turn_id', None)
                            gaps.add('conflicting_native_turn_identity')
                        if payload.get('type') in ('error', 'turn_error'):
                            classification = _error_terminal_classification(payload['type'], payload)
                            if classification is not None:
                                projected['error_terminal'] = classification
                    observed = normalized_time(record.get('timestamp'))
                    if record.get('timestamp') is not None and observed is None:
                        gaps.add('invalid_native_timestamp')
                    for key in ('started_at', 'completed_at'):
                        if key in projected:
                            raw = projected.pop(key)
                            if raw is None:
                                continue
                            value = normalized_time(raw, unix_seconds=True)
                            if value is None:
                                gaps.add('invalid_native_timestamp')
                            else:
                                projected[key] = value
                    records.append({'type': kind, 'timestamp': observed, 'payload': projected})
        return records, sorted(gaps), parent

    def worker(self, parent_id, agent_path):
        if not isinstance(agent_path, str) or not agent_path.startswith('/') or len(agent_path) > 512:
            raise ValueError('use the exact native collaboration task path')
        with closing(self.connect()) as connection:
            rows = connection.execute(
                'SELECT t.id FROM threads t JOIN thread_spawn_edges e ON e.child_thread_id=t.id '
                'WHERE e.parent_thread_id=? AND t.agent_path=? LIMIT 2',
                (parent_id, agent_path)).fetchall()
        if len(rows) != 1:
            raise ValueError('native worker path is missing or ambiguous')
        return rows[0][0]


def terminal_turn_ids(records):
    """Find settled turns in one thread's normalized NativeRecords projection."""
    terminal = set()
    pending_errors = {}
    last_start = -1
    for index, record in enumerate(records):
        payload = record['payload']
        turn = payload.get('turn_id')
        if not isinstance(turn, str) or not turn.strip():
            continue
        # Further evidence for this turn supersedes an unclassified error.
        pending_errors.pop(turn, None)
        if record['type'] != 'event_msg':
            continue
        event = payload.get('type')
        if event == 'task_started':
            last_start = index
        elif event in ('task_complete', 'turn_aborted'):
            terminal.add(turn)
        elif event in ('error', 'turn_error'):
            disposition = payload.get('error_terminal')
            if disposition is True:
                terminal.add(turn)
            elif disposition is None:
                pending_errors[turn] = index
    # A new, distinct start corroborates an older error only while the errored
    # turn has no subsequent activity. A retryable error never enters this set.
    terminal.update(turn for turn, index in pending_errors.items() if index < last_start)
    return terminal


def turns(records):
    """Ordered explicit native starts; context and cumulative usage are not starts."""
    result = []
    for record in records:
        payload = record.get('payload', {})
        if record.get('type') == 'event_msg' and payload.get('type') == 'task_started':
            value = payload.get('turn_id')
            if isinstance(value, str) and value and value not in result:
                result.append(value)
    return result


def start_time(records, turn_id):
    values = set()
    for record in records:
        payload = record['payload']
        if (record['type'] == 'event_msg' and payload.get('type') == 'task_started'
                and payload.get('turn_id') == turn_id):
            # The outer record retains its native RFC3339 precision. Timeline
            # integer seconds are a fallback for the turn-selection boundary.
            value = record.get('timestamp') or payload.get('started_at')
            parsed = normalized_time(value)
            if parsed is not None:
                values.add(parsed)
    return next(iter(values)) if len(values) == 1 else None


def normalized_time(value, *, unix_seconds=False):
    try:
        if unix_seconds and type(value) is int:
            parsed = datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=value)
        else:
            parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is not None:
            return parsed.astimezone(timezone.utc).isoformat()
    except (TypeError, ValueError, OverflowError):
        pass
    return None
