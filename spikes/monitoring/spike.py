"""Temporary monitor/timer coordinator for a single-host study, not a release."""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path
import socket
import sqlite3
import subprocess
import sys
import time
import uuid

from native import Client, RpcError


class NotSubmitted(RuntimeError):
    """A preflight failure known to occur before the native queue command."""


class Lines:
    def __init__(self, limit: int = 4096):
        self.limit = limit
        self.buffer = b''

    def feed(self, data: bytes, *, eof: bool = False) -> list[str]:
        self.buffer += data
        parts = self.buffer.split(b'\n')
        self.buffer = b'' if eof else parts.pop()
        if len(self.buffer) > self.limit or any(len(p) > self.limit for p in parts):
            raise ValueError('event exceeds byte limit')
        return [p.decode('utf-8') for p in parts if p.strip()]


class Journal:
    def __init__(self, path: Path, clock=time.time):
        self.clock = clock
        self.db = sqlite3.connect(path, timeout=5)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS jobs (
              id TEXT PRIMARY KEY, kind TEXT, state TEXT, expires REAL, due REAL,
              event_limit INTEGER, baseline TEXT, spec TEXT, detail TEXT);
            CREATE TABLE IF NOT EXISTS events (
              id TEXT PRIMARY KEY, job_id TEXT, kind TEXT, observation TEXT,
              state TEXT, native_id TEXT, detail TEXT);
        ''')

    def create(self, kind: str, spec: dict, duration: float = 120,
               event_limit: int = 2, after: float | None = None) -> str:
        if not 0 < duration <= 120 or not 1 <= event_limit <= 2:
            raise ValueError('spike duration/event bounds exceeded')
        if kind not in ('watch', 'wake') or kind == 'wake' and (after is None or not 0 <= after < duration):
            raise ValueError('invalid kind or wakeup deadline')
        job_id = str(uuid.uuid4())
        with self.db:
            self.db.execute('INSERT INTO jobs VALUES (?, ?, ?, ?, ?, ?, NULL, ?, NULL)',
                            (job_id, kind, 'active', self.clock() + duration,
                             self.clock() + after if after is not None else None,
                             1 if kind == 'wake' else event_limit, json.dumps(spec)))
        return job_id

    def job(self, job_id: str) -> dict:
        row = self.db.execute('SELECT * FROM jobs WHERE id=?', (job_id,)).fetchone()
        if row is None:
            raise ValueError('unknown job')
        return dict(row)

    def state(self, job_id: str, state: str, detail: str = '') -> None:
        with self.db:
            self.db.execute("UPDATE jobs SET state=?, detail=? WHERE id=? AND state='active'",
                            (state, detail, job_id))

    def live(self, job_id: str) -> bool:
        row = self.job(job_id)
        if row['state'] != 'active':
            return False
        if self.clock() >= row['expires']:
            self.state(job_id, 'expired')
            return False
        return True

    def emit(self, job_id: str, observation: str, kind: str = 'source',
             baseline: str | None = None) -> str | None:
        if len(observation.encode()) > 4096:
            raise ValueError('event exceeds byte limit')
        event_id = str(uuid.uuid4())
        with self.db:
            # Reserve the write transaction before reading state: cancellation and
            # event/baseline recording have a definite order across processes.
            self.db.execute('UPDATE jobs SET id=id WHERE id=?', (job_id,))
            row = self.job(job_id)
            if row['state'] != 'active' or self.clock() >= row['expires']:
                return None
            count = self.db.execute('SELECT COUNT(*) FROM events WHERE job_id=?', (job_id,)).fetchone()[0]
            if count >= row['event_limit'] or baseline is not None and baseline == row['baseline']:
                return None
            if baseline is not None:
                self.db.execute('UPDATE jobs SET baseline=? WHERE id=?', (baseline, job_id))
            self.db.execute('INSERT INTO events VALUES (?, ?, ?, ?, ?, NULL, NULL)',
                            (event_id, job_id, kind, observation, 'pending'))
        return event_id

    def cancel(self, job_id: str) -> list[dict]:
        with self.db:
            self.job(job_id)
            self.db.execute('UPDATE jobs SET state=? WHERE id=?', ('cancelled', job_id))
            self.db.execute("UPDATE events SET state='cancelled' WHERE job_id=? AND state='pending'", (job_id,))
        # Requests already dispatching are explicitly in flight; cancel cannot
        # retract them or imply that they were never submitted.
        return self.events(job_id)

    def events(self, job_id: str) -> list[dict]:
        return [dict(r) for r in self.db.execute('SELECT * FROM events WHERE job_id=? ORDER BY rowid', (job_id,))]

    def wake_due(self, job_id: str) -> str | None:
        job = self.job(job_id)
        if job['kind'] != 'wake' or self.clock() < job['due'] or not self.live(job_id):
            return None
        return self.emit(job_id, json.loads(job['spec'])['prompt'], 'wake')

    def dispatch(self, event_id: str, sink) -> None:
        with self.db:
            self.db.execute('UPDATE events SET id=id WHERE id=?', (event_id,))
            event = dict(self.db.execute('SELECT * FROM events WHERE id=?', (event_id,)).fetchone())
            if event['state'] != 'pending':
                return
            job = self.job(event['job_id'])
            if job['state'] != 'active' or self.clock() >= job['expires']:
                self.db.execute("UPDATE events SET state='cancelled' WHERE id=?", (event_id,))
                return
            self.db.execute("UPDATE events SET state='dispatching' WHERE id=?", (event_id,))
        try:
            native_id = sink(event)
        except NotSubmitted as error:
            state, native_id, detail = 'not_submitted', None, str(error)[:1024]
            self.state(event['job_id'], 'suspended', detail)
        except Exception as error:
            state, native_id, detail = 'uncertain', None, str(error)[:1024]
            self.state(event['job_id'], 'suspended', detail)
        else:
            state, detail = 'native_queued', ''
        with self.db:
            self.db.execute('UPDATE events SET state=?, native_id=?, detail=? WHERE id=?',
                            (state, native_id, detail, event_id))

    def reconcile_crash(self) -> None:
        with self.db:
            self.db.execute("UPDATE events SET state='uncertain', detail='worker stopped during dispatch' WHERE state='dispatching'")


def deliver(client: Client, binding: dict, followup: str, event: dict) -> str | None:
    try:
        if client.bind(binding['thread_id']) != binding:
            raise RpcError('frozen binding changed')
        # This study does not qualify goal coexistence. Fail closed rather than
        # submitting user-shaped input to a paused/budget-limited/active goal.
        if client.call('thread/goal/get', {'threadId': binding['thread_id']}).get('goal') is not None:
            raise RpcError('goal coexistence is unqualified; automatic delivery suspended')
        if any(e.get('method') == 'turn/completed' and
               e['params']['turn'].get('status') == 'interrupted' for e in client.events):
            raise RpcError('observed native interruption; automatic delivery suspended')
    except Exception as error:
        raise NotSubmitted(str(error)) from error
    message = json.dumps({'codex_plus_spike': True, 'event_id': event['id'],
                          'job_id': event['job_id'], 'kind': event['kind'],
                          'observation': event['observation'], 'followup': followup})
    result = subprocess.run(['rtk', 'proxy', 'codex', 'queue', '--remote',
                             'unix://' + binding['requested_socket'], '--thread',
                             binding['thread_id'], '--message', message],
                            capture_output=True, text=True, timeout=10)
    if result.returncode:
        raise RpcError('native queue command failed; submission outcome not assumed')
    words = result.stdout.split()
    return words[2] if len(words) > 2 and words[:2] == ['Queued', 'message'] else None


def worker(path: Path, job_id: str) -> None:
    journal = Journal(path)
    job = journal.job(job_id)
    spec = json.loads(job['spec'])
    try:
        with Client(spec['binding']['requested_socket'], experimental=True) as client:
            if client.bind(spec['binding']['thread_id']) != spec['binding']:
                raise RpcError('frozen binding changed')
            client.call('thread/resume', {'threadId': spec['binding']['thread_id']})
            if not journal.live(job_id):
                return
            def sink(event):
                return deliver(client, spec['binding'], spec['followup'], event)
            if job['kind'] == 'wake':
                while journal.live(job_id) and time.time() < job['due']:
                    try:
                        client.receive(min(0.1, max(0.001, job['due'] - time.time())))
                    except socket.timeout:
                        pass
                    if any(e.get('method') == 'turn/completed' and
                           e['params']['turn'].get('status') == 'interrupted' for e in client.events):
                        journal.state(job_id, 'suspended', 'observed native turn interruption')
                if journal.live(job_id):
                    event = journal.wake_due(job_id)
                    if event:
                        journal.dispatch(event, sink)
                if journal.live(job_id):
                    journal.state(job_id, 'completed')
                return
            pid = 'monitor-' + job_id
            rid = client.submit('command/exec', {
                'command': spec['command'], 'cwd': spec['cwd'],
                'sandboxPolicy': {'type': 'readOnly'}, 'processId': pid,
                'streamStdoutStderr': True, 'timeoutMs': int(max(1, job['expires'] - time.time()) * 1000),
                'outputBytesCap': 65536})
            lines = Lines()
            diagnostic_bytes = 0
            consumed = 0
            try:
                while journal.live(job_id) and rid not in client.responses:
                    try:
                        client.receive(0.2)
                    except socket.timeout:
                        continue
                    while consumed < len(client.events):
                        event = client.events[consumed]
                        consumed += 1
                        params = event.get('params', {})
                        if event.get('method') == 'turn/completed' and params['turn'].get('status') == 'interrupted':
                            journal.state(job_id, 'suspended', 'observed native turn interruption')
                            break
                        if event.get('method') != 'command/exec/outputDelta' or params['processId'] != pid:
                            continue
                        if params['capReached']:
                            raise ValueError('native output cap reached; truncated output rejected')
                        data = base64.b64decode(params['deltaBase64'], validate=True)
                        if params['stream'] == 'stderr':
                            diagnostic_bytes += len(data)
                            if diagnostic_bytes > 16384:
                                raise ValueError('diagnostic byte limit exceeded')
                            continue
                        for observation in lines.feed(data):
                            emitted = journal.emit(job_id, observation)
                            if emitted:
                                journal.dispatch(emitted, sink)
                            if len(journal.events(job_id)) >= job['event_limit']:
                                journal.state(job_id, 'limit_reached')
                                break
                if rid in client.responses and journal.live(job_id):
                    result = client.result(rid)
                    for observation in lines.feed(b'', eof=True):
                        emitted = journal.emit(job_id, observation)
                        if emitted:
                            journal.dispatch(emitted, sink)
                    journal.state(job_id, 'completed' if result['exitCode'] == 0 else 'source_error',
                                  'source exit ' + str(result['exitCode']))
            finally:
                if rid not in client.responses:
                    client.call('command/exec/terminate', {'processId': pid})
                    client.result(rid)
    except Exception as error:
        # Keep cancellation authoritative if the transport fails during cleanup.
        if journal.job(job_id)['state'] == 'active':
            journal.state(job_id, 'source_error', str(error)[:1024])
        raise
    finally:
        journal.db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', type=Path, required=True)
    sub = parser.add_subparsers(dest='operation', required=True)
    for name in ('watch_start', 'wake_schedule'):
        p = sub.add_parser(name)
        p.add_argument('--binding', type=Path, required=True)
        p.add_argument('--duration', type=float, default=120)
        p.add_argument('--limit', type=int, default=2)
        p.add_argument('--followup', default='Inspect the synthetic observation and report useful changes.')
        if name == 'watch_start':
            p.add_argument('--cwd', required=True)
            p.add_argument('command', nargs=argparse.REMAINDER)
        else:
            p.add_argument('--after', type=float, required=True)
            p.add_argument('--prompt', required=True)
    for name in ('status', 'cancel', 'worker'):
        sub.add_parser(name).add_argument('id')
    sub.add_parser('list')
    args = parser.parse_args()
    journal = Journal(args.db)
    if args.operation in ('watch_start', 'wake_schedule'):
        binding = json.loads(args.binding.read_text())
        spec = {'binding': binding, 'followup': args.followup}
        if args.operation == 'watch_start':
            command = args.command[1:] if args.command[:1] == ['--'] else args.command
            if not command:
                parser.error('watch_start requires a source argv')
            spec.update(command=command, cwd=str(Path(args.cwd).resolve()))
        else:
            spec['prompt'] = args.prompt
        with Client(binding['requested_socket']) as client:
            if client.bind(binding['thread_id']) != binding:
                raise RpcError('frozen binding changed')
        job_id = journal.create('watch' if args.operation == 'watch_start' else 'wake', spec,
                                args.duration, args.limit, getattr(args, 'after', None))
        with args.db.with_suffix('.worker.log').open('ab') as log:
            child = subprocess.Popen([sys.executable, '-B', __file__, '--db', str(args.db),
                                      'worker', job_id], stdin=subprocess.DEVNULL,
                                     stdout=log, stderr=log, start_new_session=True)
        print(json.dumps({'id': job_id, 'state': 'registered', 'worker_pid': child.pid,
                          'destination': binding, 'duration': args.duration,
                          'event_limit': 1 if args.operation == 'wake_schedule' else args.limit,
                          'lifecycle_notices': False}))
    elif args.operation == 'worker':
        journal.db.close()
        worker(args.db, args.id)
        return
    elif args.operation == 'cancel':
        print(json.dumps({'state': 'cancelled', 'events': journal.cancel(args.id)}))
    elif args.operation == 'status':
        print(json.dumps({'job': journal.job(args.id), 'events': journal.events(args.id)}))
    else:
        print(json.dumps([dict(r) for r in journal.db.execute('SELECT * FROM jobs ORDER BY rowid')]))
    journal.db.close()


if __name__ == '__main__':
    main()
