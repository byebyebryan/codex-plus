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
                if 'thread_id' in payload and payload['thread_id'] != thread_id:
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
