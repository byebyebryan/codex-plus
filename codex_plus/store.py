"""Private transactional intent, observation and native receipt journal."""

from __future__ import annotations

from contextlib import contextmanager
import json
import os
from pathlib import Path
import sqlite3
import time
import uuid

from .peers import DEFAULT_SIGNALS, SIGNALS, thread_id


MAX_DURATION = 86400
MAX_EVENTS = 1000
RECORD_BYTES = 4096


def private_directory(path: Path) -> Path:
    if path.is_symlink():
        raise ValueError('state directory must not be a symlink')
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    path = path.resolve()
    info = path.stat()
    if info.st_uid != os.getuid() or info.st_mode & 0o077:
        raise ValueError('state directory must be owned by this user and private (0700)')
    return path


def validate_spec(kind: str, spec: dict) -> dict:
    spec = dict(spec)
    supported = {'duration', 'event_limit', 'followup', 'notify_end', 'command', 'cwd',
                 'snapshot_fields', 'quiet_initial', 'after', 'prompt',
                 'peer', 'interval', 'signals', 'turn_limit', 'label',
                 'sender', 'sender_label', 'message_kind'}
    if set(spec) - supported:
        raise ValueError('unsupported registration fields: ' + ', '.join(sorted(set(spec) - supported)))
    duration = spec.get('duration', 120)
    limit = spec.get('event_limit', 2)
    if isinstance(duration, bool) or not isinstance(duration, (int, float)) or not 0 < duration <= MAX_DURATION:
        raise ValueError('duration must be positive and at most 86400 seconds')
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_EVENTS:
        raise ValueError('event limit must be an integer from 1 to 1000')
    spec.update(duration=duration, event_limit=1 if kind in ('wake', 'message') else limit)
    followup = spec.get('followup', 'Inspect this observation under the existing request.')
    if not isinstance(followup, str) or not followup.strip() or len(followup.encode()) > 16384:
        raise ValueError('follow-up must be nonempty and at most 16 KiB')
    spec['followup'] = followup
    for key in ('label', 'sender_label'):
        if key in spec and (not isinstance(spec[key], str) or not spec[key].strip()
                            or len(spec[key].encode()) > 512):
            raise ValueError(key + ' must be nonempty and at most 512 bytes')
    if any(key in spec for key in ('sender', 'sender_label', 'message_kind')) and kind != 'message':
        raise ValueError('sender/message fields require a message registration')
    if kind == 'message':
        if spec.get('message_kind', 'information') not in ('information', 'request'):
            raise ValueError('message kind must be information or request')
        sender = spec.get('sender')
        if spec.get('message_kind') == 'request' and sender is None:
            raise ValueError('an action request requires a frozen sender binding')
        if sender is not None:
            if not isinstance(sender, dict) or set(sender) != {
                    'host', 'uid', 'pid_namespace', 'requested_socket', 'resolved_socket',
                    'pid', 'start_ticks', 'executable', 'thread_id'}:
                raise ValueError('sender must contain an exact frozen native binding')
            thread_id(sender['thread_id'])
        if spec.get('sender_label') and sender is None:
            raise ValueError('a sender label requires a frozen sender binding')
    if kind == 'watch':
        if spec.get('peer') is not None:
            peer = spec['peer']
            if not isinstance(peer, dict) or set(peer) != {
                    'host', 'uid', 'pid_namespace', 'requested_socket', 'resolved_socket',
                    'pid', 'start_ticks', 'executable', 'thread_id'}:
                raise ValueError('peer must contain an exact frozen native binding')
            thread_id(peer['thread_id'])
            if any(spec.get(key) is not None for key in ('command', 'cwd')):
                raise ValueError('choose a peer source or a command source')
            interval = spec.get('interval', 5)
            if isinstance(interval, bool) or not isinstance(interval, (int, float)) or not 1 <= interval <= 3600:
                raise ValueError('peer interval must be 1 through 3600 seconds')
            signals = spec.get('signals', DEFAULT_SIGNALS)
            if not isinstance(signals, list) or not signals or any(not isinstance(s, str) for s in signals) or len(signals) != len(set(signals)) or set(signals) - SIGNALS:
                raise ValueError('select distinct supported peer signals')
            turns = spec.get('turn_limit', 3)
            if isinstance(turns, bool) or not isinstance(turns, int) or not 1 <= turns <= 10:
                raise ValueError('peer turn window must be 1 through 10')
            fields = ['peer_id', 'coverage', 'task_outcome', *signals]
            if spec.get('snapshot_fields') is not None and spec['snapshot_fields'] != fields:
                raise ValueError('peer projection is defined by selected signals')
            spec.update(interval=interval, signals=list(signals), turn_limit=turns,
                        snapshot_fields=fields)
        else:
            if any(key in spec for key in ('interval', 'signals', 'turn_limit')):
                raise ValueError('peer options require a peer binding')
            command = spec.get('command')
            if not isinstance(command, list) or not command or any(
                not isinstance(arg, str) or '\0' in arg for arg in command
            ) or not command[0]:
                raise ValueError('source command must be a nonempty argv without NUL bytes')
            cwd = spec.get('cwd')
            if not isinstance(cwd, str) or not Path(cwd).is_absolute() or not Path(cwd).is_dir():
                raise ValueError('source cwd must be an existing absolute directory')
        fields = spec.get('snapshot_fields')
        if fields is not None and (not isinstance(fields, list) or not fields or
                any(not isinstance(field, str) or not field for field in fields) or
                len(fields) != len(set(fields))):
            raise ValueError('snapshot fields must be distinct nonempty top-level names')
    elif kind in ('wake', 'message'):
        if spec.get('peer') is not None:
            raise ValueError('peer observation requires a watch registration')
        if kind == 'wake':
            after = spec.get('after')
            if isinstance(after, bool) or not isinstance(after, (int, float)) or not 0 <= after < duration:
                raise ValueError('wakeup delay must be nonnegative and before expiry')
        if not isinstance(spec.get('prompt'), str) or not spec['prompt'].strip():
            raise ValueError('wakeup prompt must be nonempty')
        if len(spec['prompt'].encode()) > RECORD_BYTES:
            raise ValueError('wakeup prompt exceeds 4 KiB')
    else:
        raise ValueError('unknown registration kind')
    return spec


class Store:
    def __init__(self, root: Path, clock=time.time):
        self.root = private_directory(root)
        self.clock = clock
        path = self.root / 'journal.sqlite3'
        if path.is_symlink():
            raise ValueError('journal must not be a symlink')
        try:
            fd = os.open(path, os.O_CREAT | os.O_EXCL | os.O_RDWR, 0o600)
        except FileExistsError:
            if path.stat().st_uid != os.getuid() or path.stat().st_mode & 0o077:
                raise ValueError('journal must be private and owned by this user')
        else:
            os.close(fd)
        self.db = sqlite3.connect(path, timeout=5, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.executescript('''
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY, kind TEXT NOT NULL, intent TEXT NOT NULL,
                created REAL NOT NULL, expires REAL NOT NULL, due REAL,
                spec TEXT NOT NULL, parent_id TEXT REFERENCES jobs(id), root_id TEXT NOT NULL,
                source_state TEXT NOT NULL, source_detail TEXT NOT NULL DEFAULT '',
                control_reason TEXT NOT NULL DEFAULT '', baseline TEXT,
                event_count INTEGER NOT NULL DEFAULT 0, notice_count INTEGER NOT NULL DEFAULT 0,
                recover_requested INTEGER NOT NULL DEFAULT 0, generation TEXT);
            CREATE UNIQUE INDEX IF NOT EXISTS one_successor ON jobs(parent_id) WHERE parent_id IS NOT NULL;
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY, job_id TEXT NOT NULL REFERENCES jobs(id),
                sequence INTEGER NOT NULL, kind TEXT NOT NULL, observation TEXT NOT NULL,
                created REAL NOT NULL, expires REAL NOT NULL, delivery TEXT NOT NULL,
                native_id TEXT, start_state TEXT NOT NULL DEFAULT 'pending',
                turn_id TEXT, turn_outcome TEXT, turn_error TEXT,
                acknowledged INTEGER NOT NULL DEFAULT 0, detail TEXT NOT NULL DEFAULT '',
                UNIQUE(job_id, sequence));
            CREATE UNIQUE INDEX IF NOT EXISTS one_wake ON events(job_id) WHERE kind='wake';
            CREATE UNIQUE INDEX IF NOT EXISTS one_message ON events(job_id) WHERE kind='message';
            CREATE TABLE IF NOT EXISTS turn_receipts (
                turn_id TEXT PRIMARY KEY, outcome TEXT NOT NULL, error TEXT);
            CREATE TABLE IF NOT EXISTS renewals (
                parent_id TEXT PRIMARY KEY REFERENCES jobs(id), new_id TEXT NOT NULL,
                spec TEXT NOT NULL, state TEXT NOT NULL, detail TEXT NOT NULL DEFAULT '');
        ''')
        try:
            self._migrate_journal()
        except BaseException:
            self.db.close()
            raise

    def _migrate_journal(self):
        """Keep legacy IDs/receipts; allow multiple failed attempts per parent."""
        with self.transaction():
            columns = {row['name'] for row in self.db.execute('PRAGMA table_info(renewals)')}
            if 'deadline' not in columns:
                self.db.execute('''CREATE TABLE renewals_next (
                    parent_id TEXT NOT NULL REFERENCES jobs(id), new_id TEXT PRIMARY KEY,
                    spec TEXT NOT NULL, state TEXT NOT NULL, detail TEXT NOT NULL DEFAULT '',
                    created REAL, deadline REAL)''')
                self.db.execute('''INSERT INTO renewals_next
                    SELECT r.parent_id,r.new_id,r.spec,r.state,r.detail,NULL,
                        CASE WHEN r.state='pending' THEN MIN(j.expires,?) ELSE NULL END
                    FROM renewals r JOIN jobs j ON j.id=r.parent_id''', (self.clock() + 10,))
                if self.db.execute('SELECT COUNT(*) FROM renewals_next').fetchone()[0] != self.db.execute('SELECT COUNT(*) FROM renewals').fetchone()[0]:
                    raise ValueError('legacy renewal has no valid parent; journal migration refused')
                self.db.execute('DROP TABLE renewals')
                self.db.execute('ALTER TABLE renewals_next RENAME TO renewals')
            self.db.execute("CREATE UNIQUE INDEX IF NOT EXISTS one_pending_renewal ON renewals(parent_id) WHERE state='pending'")
            event_columns = {row['name'] for row in self.db.execute('PRAGMA table_info(events)')}
            for column in ('withdraw_state', 'withdraw_detail'):
                if column not in event_columns:
                    default = 'none' if column == 'withdraw_state' else ''
                    self.db.execute(f"ALTER TABLE events ADD COLUMN {column} TEXT NOT NULL DEFAULT '{default}'")
            if 'withdraw_state' not in event_columns:
                self.db.execute("UPDATE events SET withdraw_state='withdrawn',withdraw_detail='legacy confirmed withdrawal receipt' WHERE start_state='withdrawn'")
            self.db.execute('PRAGMA user_version=2')

    @contextmanager
    def transaction(self):
        if self.db.in_transaction:
            yield
            return
        self.db.execute('BEGIN IMMEDIATE')
        try:
            yield
        except BaseException:
            self.db.execute('ROLLBACK')
            raise
        else:
            self.db.execute('COMMIT')

    def close(self):
        self.db.close()

    def _job(self, row):
        result = dict(row)
        result['spec'] = json.loads(result['spec'])
        return result

    def job(self, job_id: str) -> dict:
        row = self.db.execute('SELECT * FROM jobs WHERE id=?', (job_id,)).fetchone()
        if row is None:
            raise ValueError('unknown registration')
        return self._job(row)

    def jobs(self) -> list[dict]:
        return [self._job(row) for row in self.db.execute('SELECT * FROM jobs ORDER BY created,id')]

    def event(self, event_id: str) -> dict:
        row = self.db.execute('SELECT * FROM events WHERE id=?', (event_id,)).fetchone()
        if row is None:
            raise ValueError('unknown event')
        return dict(row)

    def events(self, job_id: str | None = None) -> list[dict]:
        if job_id is None:
            rows = self.db.execute('SELECT * FROM events ORDER BY created,sequence,id')
        else:
            self.job(job_id)
            rows = self.db.execute('SELECT * FROM events WHERE job_id=? ORDER BY sequence', (job_id,))
        return [dict(row) for row in rows]

    def create(self, kind: str, spec: dict, *, parent_id: str | None = None,
               job_id: str | None = None) -> str:
        spec = validate_spec(kind, spec)
        job_id = job_id or str(uuid.uuid4())
        with self.transaction():
            if parent_id:
                parent = self.job(parent_id)
                root = self.job(parent['root_id'])
                if root['intent'] == 'cancelled' or parent['intent'] == 'cancelled':
                    raise ValueError('cancelled supervision cannot be renewed')
                root_id = parent['root_id']
            else:
                root_id = job_id
            now = self.clock()
            self.db.execute('''INSERT INTO jobs
                (id,kind,intent,created,expires,due,spec,parent_id,root_id,source_state)
                VALUES (?,?,?,?,?,?,?,?,?,?)''', (job_id, kind, 'active', now,
                now + spec['duration'], now + spec['after'] if kind == 'wake' else None,
                json.dumps(spec), parent_id, root_id, 'pending' if kind == 'watch' else 'none'))
        return job_id

    def source(self, job_id: str, state: str, detail: str = '', generation: str | None = None):
        with self.transaction():
            job = self.job(job_id)
            if state in ('starting', 'running') and job['intent'] != 'active':
                return False
            self.db.execute('UPDATE jobs SET source_state=?,source_detail=?,generation=? WHERE id=?',
                (state, detail[:1024], generation, job_id))
        return True

    def control(self, job_id: str, reason: str):
        self.db.execute('UPDATE jobs SET control_reason=? WHERE id=?', (reason, job_id))

    def _insert_event(self, job: dict, observation: str, kind: str, expires: float) -> str:
        event_id = str(uuid.uuid4())
        sequence = self.db.execute('SELECT COUNT(*) FROM events WHERE job_id=?', (job['id'],)).fetchone()[0] + 1
        self.db.execute('''INSERT INTO events
            (id,job_id,sequence,kind,observation,created,expires,delivery)
            VALUES (?,?,?,?,?,?,?,?)''', (event_id, job['id'], sequence, kind,
                observation, self.clock(), expires, 'pending'))
        return event_id

    def emit(self, job_id: str, observation: str, kind: str = 'source') -> str | None:
        if len(observation.encode('utf-8')) > RECORD_BYTES:
            raise ValueError('observation exceeds 4 KiB')
        with self.transaction():
            job = self.job(job_id)
            if job['intent'] != 'active' or self.clock() >= job['expires']:
                return None
            if kind in ('wake', 'message'):
                if job['kind'] != kind or self.db.execute(
                        'SELECT 1 FROM events WHERE job_id=? AND kind=?', (job_id, kind)).fetchone():
                    return None
            elif kind == 'source':
                if job['kind'] != 'watch' or job['event_count'] >= job['spec']['event_limit']:
                    return None
                fields = job['spec'].get('snapshot_fields')
                if fields:
                    def invalid_constant(value):
                        raise ValueError('non-JSON numeric constant')
                    parsed = json.loads(observation, parse_constant=invalid_constant)
                    if not isinstance(parsed, dict) or any(field not in parsed for field in fields):
                        raise ValueError('snapshot is not an object containing the selected fields')
                    observation = json.dumps({field: parsed[field] for field in fields},
                        sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False)
                    previous = job['baseline']
                    self.db.execute('UPDATE jobs SET baseline=? WHERE id=?', (observation, job_id))
                    if observation == previous or previous is None and job['spec'].get('quiet_initial', False):
                        return None
                self.db.execute('UPDATE jobs SET event_count=event_count+1 WHERE id=?', (job_id,))
            else:
                raise ValueError('unknown observation kind')
            return self._insert_event(job, observation, kind, job['expires'])

    def notice(self, job_id: str, reason: str) -> str | None:
        with self.transaction():
            job = self.job(job_id)
            if not job['spec'].get('notify_end') or job['notice_count'] or job['intent'] in ('cancelled', 'replaced', 'replacing'):
                return None
            self.db.execute('UPDATE jobs SET notice_count=1 WHERE id=?', (job_id,))
            data = json.dumps({'source_lifecycle': reason[:512], 'watched_job_outcome': 'unknown'})
            return self._insert_event(job, data, 'lifecycle', self.clock() + 30)

    def cancel(self, job_id: str) -> dict:
        with self.transaction():
            try:
                job = self.job(job_id)
            except ValueError:
                job = self.job(self.renewal(job_id)['parent_id'])
            ids = [row[0] for row in self.db.execute('SELECT id FROM jobs WHERE root_id=?', (job['root_id'],))]
            for target in ids:
                current = self.job(target)
                state = current['source_state']
                if state in ('pending', 'lost'):
                    state = 'stopped'
                elif state in ('starting', 'running'):
                    state = 'stop_requested'
                self.db.execute("UPDATE jobs SET intent='cancelled',source_state=? WHERE id=?", (state, target))
                self.db.execute("UPDATE events SET delivery='cancelled',detail='explicit supervision cancellation' WHERE job_id=? AND delivery='pending'", (target,))
                self.db.execute("UPDATE renewals SET state='cancelled',detail='explicit supervision cancellation' WHERE parent_id=? AND state='pending'", (target,))
        return {'cancelled': ids, 'events': [e for e in self.events() if e['job_id'] in ids]}

    def expire(self, job_id: str):
        with self.transaction():
            job = self.job(job_id)
            if job['intent'] != 'active':
                return
            self.db.execute("UPDATE jobs SET intent='expired' WHERE id=?", (job_id,))
            self.db.execute("UPDATE events SET delivery='expired',detail='registration expired before admission' WHERE job_id=? AND delivery='pending'", (job_id,))
            self.notice(job_id, 'expired')

    def reserve(self, event_id: str) -> bool:
        with self.transaction():
            event = self.event(event_id)
            job = self.job(event['job_id'])
            eligible = job['intent'] == 'active' or event['kind'] == 'lifecycle' and job['intent'] == 'expired'
            if event['delivery'] != 'pending' or not eligible:
                return False
            if self.clock() >= event['expires']:
                self.db.execute("UPDATE events SET delivery='expired' WHERE id=?", (event_id,))
                return False
            self.db.execute("UPDATE events SET delivery='dispatching' WHERE id=?", (event_id,))
        return True

    def expire_pending_events(self):
        """Bound delivery windows even when native control cannot be read."""
        self.db.execute("UPDATE events SET delivery='expired',detail='delivery window ended before admission' WHERE delivery='pending' AND expires<=?", (self.clock(),))

    def reserve_start(self, event_id: str) -> bool:
        """Recheck cancellation and lease after native queue inspection."""
        with self.transaction():
            event = self.event(event_id)
            job = self.job(event['job_id'])
            eligible = job['intent'] == 'active' or event['kind'] == 'lifecycle' and job['intent'] == 'expired'
            if (event['delivery'] != 'native_queued' or event['start_state'] != 'pending'
                    or event['turn_id'] or not eligible or self.clock() >= event['expires']):
                return False
            self.db.execute("UPDATE events SET start_state='starting' WHERE id=?", (event_id,))
        return True

    def admitted(self, event_id: str, native_id: str | None):
        self.db.execute("UPDATE events SET delivery='native_queued',native_id=? WHERE id=?", (native_id, event_id))

    def uncertain(self, event_id: str, reason: str):
        self.db.execute("UPDATE events SET delivery='uncertain',detail=? WHERE id=?", (reason[:1024], event_id))

    def withdrawal(self, event_id: str, state: str, detail: str):
        with self.transaction():
            self.db.execute('UPDATE events SET withdraw_state=?,withdraw_detail=? WHERE id=?', (state, detail[:1024], event_id))
            if state == 'withdrawn':
                self.db.execute("UPDATE events SET start_state='withdrawn' WHERE id=? AND turn_id IS NULL", (event_id,))

    def link_turn(self, event_id: str, turn_id: str):
        with self.transaction():
            event = self.event(event_id)
            if event['delivery'] not in ('dispatching', 'native_queued', 'uncertain'):
                return
            self.db.execute("UPDATE events SET delivery='native_queued',turn_id=?,start_state='started' WHERE id=?", (turn_id, event_id))
            receipt = self.db.execute('SELECT * FROM turn_receipts WHERE turn_id=?', (turn_id,)).fetchone()
            if receipt:
                self.db.execute('UPDATE events SET turn_outcome=?,turn_error=? WHERE id=?',
                    (receipt['outcome'], receipt['error'], event_id))

    def turn_completed(self, turn_id: str, outcome: str, error=None):
        if outcome not in ('completed', 'failed', 'interrupted'):
            return
        encoded = json.dumps(error)[:2048] if error is not None else None
        with self.transaction():
            self.db.execute('INSERT OR REPLACE INTO turn_receipts VALUES (?,?,?)', (turn_id, outcome, encoded))
            self.db.execute('UPDATE events SET turn_outcome=?,turn_error=? WHERE turn_id=?', (outcome, encoded, turn_id))

    def acknowledge(self, event_id: str) -> dict:
        with self.transaction():
            event = self.event(event_id)
            if event['delivery'] != 'native_queued':
                raise ValueError('event has no known native admission to acknowledge')
            self.db.execute('UPDATE events SET acknowledged=1 WHERE id=?', (event_id,))
        return self.event(event_id)

    def request_renewal(self, parent_id: str, spec: dict) -> str:
        with self.transaction():
            parent = self.job(parent_id)
            if parent['kind'] != 'watch' or parent['intent'] in ('cancelled', 'replaced', 'replacing') or self.job(parent['root_id'])['intent'] == 'cancelled':
                raise ValueError('registration cannot be renewed')
            if parent['source_state'] == 'lost':
                raise ValueError('source is lost; explicitly recover its remaining lease or cancel and register fresh observation')
            spec = validate_spec('watch', spec)
            if parent['spec'].get('peer') != spec.get('peer'):
                raise ValueError('renewal cannot change the observed peer identity or source type')
            final = parent['source_state'] in ('stopped', 'completed', 'error')
            now = self.clock()
            deadline = now + 10 if final else min(parent['expires'], now + 10)
            if deadline <= now:
                raise ValueError('source lease expired without a confirmed stop')
            new_id = str(uuid.uuid4())
            self.db.execute('INSERT INTO renewals VALUES (?,?,?,?,?,?,?)',
                (parent_id, new_id, json.dumps(spec), 'pending', '', now, deadline))
            self.db.execute("UPDATE jobs SET intent='replacing' WHERE id=?", (parent_id,))
            self.db.execute("UPDATE events SET delivery='cancelled',detail='predecessor replaced' WHERE job_id=? AND delivery='pending'", (parent_id,))
            if final:
                self.finish_renewal(parent_id)
        return new_id

    def renewals(self, parent_id: str | None = None) -> list[dict]:
        rows = self.db.execute('SELECT * FROM renewals ORDER BY rowid' if parent_id is None
            else 'SELECT * FROM renewals WHERE parent_id=? ORDER BY rowid',
            () if parent_id is None else (parent_id,))
        return [self._job(row) for row in rows]

    def renewal(self, new_id: str) -> dict:
        row = self.db.execute('SELECT * FROM renewals WHERE new_id=?', (new_id,)).fetchone()
        if row is None:
            raise ValueError('unknown registration or renewal attempt')
        return self._job(row)

    def _end_renewal(self, row, state, detail):
        self.db.execute('UPDATE renewals SET state=?,detail=? WHERE new_id=?', (state, detail, row['new_id']))
        parent = self.job(row['parent_id'])
        if parent['intent'] == 'replacing':
            intent = 'expired' if self.clock() >= parent['expires'] else 'active'
            self.db.execute('UPDATE jobs SET intent=? WHERE id=?', (intent, parent['id']))

    def expire_renewals(self, expired_ids=()):
        with self.transaction():
            for row in self.db.execute("SELECT * FROM renewals WHERE state='pending'").fetchall():
                if self.clock() >= row['deadline'] or row['new_id'] in expired_ids:
                    self._end_renewal(row, 'expired', 'renewal handshake deadline ended without a confirmed stop')

    def finish_renewal(self, parent_id: str) -> str | None:
        with self.transaction():
            row = self.db.execute("SELECT * FROM renewals WHERE parent_id=? AND state='pending'", (parent_id,)).fetchone()
            if not row:
                return None
            parent = self.job(parent_id)
            if parent['intent'] == 'cancelled' or self.job(parent['root_id'])['intent'] == 'cancelled':
                self.db.execute("UPDATE renewals SET state='cancelled' WHERE new_id=?", (row['new_id'],))
                return None
            if self.clock() >= row['deadline']:
                self._end_renewal(row, 'expired', 'stop receipt arrived after renewal deadline')
                return None
            if parent['source_state'] == 'lost':
                self._end_renewal(row, 'interrupted', 'source owner lost during renewal; explicit recovery required')
                return None
            if parent['source_state'] not in ('stopped', 'completed', 'error'):
                return None
            new_id = self.create('watch', json.loads(row['spec']), parent_id=parent_id, job_id=row['new_id'])
            self.db.execute("UPDATE jobs SET intent='replaced' WHERE id=?", (parent_id,))
            self.db.execute("UPDATE renewals SET state='done' WHERE new_id=?", (row['new_id'],))
            return new_id

    def reconcile(self):
        with self.transaction():
            self.db.execute("UPDATE events SET delivery='uncertain',detail='coordinator stopped during admission' WHERE delivery='dispatching'")
            self.db.execute("UPDATE events SET start_state='unknown',detail='coordinator stopped during queue start' WHERE start_state='starting'")
            self.db.execute("UPDATE jobs SET source_state='lost',source_detail='previous coordinator connection ended' WHERE source_state IN ('starting','running','stop_requested')")
            for row in self.db.execute("SELECT * FROM renewals WHERE state='pending'").fetchall():
                parent = self.job(row['parent_id'])
                if parent['source_state'] == 'lost':
                    self._end_renewal(row, 'interrupted', 'source owner lost during renewal; explicit recovery required')
            self.expire_renewals()

    def request_recovery(self, job_id: str):
        with self.transaction():
            job = self.job(job_id)
            if job['intent'] != 'active' or job['source_state'] != 'lost' or self.clock() >= job['expires']:
                raise ValueError('only an unexpired lost source can be explicitly recovered')
            self.db.execute('UPDATE jobs SET recover_requested=1 WHERE id=?', (job_id,))

    def settle(self, job_id: str):
        """End fulfilled observation intent without claiming a watched-job outcome."""
        with self.transaction():
            job = self.job(job_id)
            if job['intent'] != 'active':
                return
            if job['kind'] == 'watch' and job['source_state'] not in ('completed', 'error', 'stopped'):
                return
            events = self.events(job_id)
            if job['kind'] == 'wake' and not events:
                return
            if any(event['delivery'] in ('pending', 'dispatching') or
                   event['delivery'] == 'native_queued' and not event['acknowledged'] and
                   event['turn_outcome'] is None for event in events):
                return
            self.db.execute("UPDATE jobs SET intent='completed' WHERE id=?", (job_id,))
