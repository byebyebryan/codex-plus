"""One coordinator owns native source connections, timers and queued receipts."""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
import json
import socket
import time
import uuid

from .control import delivery_decision
from .framing import Lines
from .native import Client, RpcError
from .store import Store


STDOUT_BYTES = 65536
STDERR_BYTES = 16384


@dataclass
class Source:
    request_id: int
    process_id: str
    lines: Lines = field(default_factory=Lines)
    stdout_bytes: int = 0
    stderr_bytes: int = 0
    stderr_tail: bytes = b''
    stop_reason: str | None = None


class Engine:
    def __init__(self, store: Store, binding: dict, backend=None, monotonic=time.monotonic):
        self.store, self.binding = store, binding
        self.monotonic = monotonic
        self.client = backend
        self.generation = str(uuid.uuid4())
        self.sources: dict[str, Source] = {}
        self.deadlines: dict[str, float] = {}
        self.wake_due: dict[str, float] = {}
        self.renewal_deadlines: dict[str, float] = {}
        self.next_connect = 0.0
        self.next_delivery = 0.0
        self.stopping = False
        self.store.reconcile()

    def _connect(self):
        if self.client is None:
            if self.monotonic() < self.next_connect:
                return False
            self.next_connect = self.monotonic() + 2
            client = Client(self.binding['requested_socket'], experimental=True)
            try:
                if client.bind(self.binding['thread_id']) != self.binding:
                    raise RpcError('frozen native owner or thread changed')
                # Positive loaded membership was checked first. This subscribes
                # to the existing runtime; it is never a cold-thread fallback.
                client.call('thread/resume', {'threadId': self.binding['thread_id'], 'excludeTurns': True})
            except BaseException:
                client.close()
                raise
            self.client = client
        return True

    def _disconnect(self, reason):
        if self.client:
            self.client.close()
        self.client = None
        for job_id in list(self.sources):
            self.store.source(job_id, 'lost', reason, self.generation)
        self.sources.clear()
        self.store.reconcile()
        self.next_connect = self.monotonic() + 2

    def _control(self):
        if self.client.bind(self.binding['thread_id']) != self.binding:
            raise RpcError('frozen binding changed')
        thread = self.client.call('thread/read', {'threadId': self.binding['thread_id']})['thread']
        goal = self.client.call('thread/goal/get', {'threadId': self.binding['thread_id']})
        return thread, delivery_decision(self.binding['thread_id'], thread, goal)

    def _start_source(self, job):
        if not self.store.source(job['id'], 'starting', generation=self.generation):
            return
        spec = job['spec']
        process_id = 'codex-plus-' + job['id']
        command = spec['command']
        if command[0] != 'rtk':
            command = ['rtk', 'proxy', *command]
        remaining = max(0.001, self.deadlines[job['id']] - self.monotonic())
        request_id = self.client.submit('command/exec', {
            'command': command, 'cwd': spec['cwd'],
            'sandboxPolicy': {'type': 'readOnly', 'networkAccess': False},
            'processId': process_id, 'streamStdoutStderr': True,
            'timeoutMs': max(1, int(remaining * 1000)), 'outputBytesCap': STDOUT_BYTES})
        self.sources[job['id']] = Source(request_id, process_id)
        self.store.db.execute('UPDATE jobs SET recover_requested=0 WHERE id=?', (job['id'],))

    def _stop_source(self, job_id, reason):
        source = self.sources.get(job_id)
        if source is None:
            job = self.store.job(job_id)
            if job['source_state'] in ('pending', 'starting', 'stop_requested'):
                self.store.source(job_id, 'stopped', reason, self.generation)
            return
        if source.stop_reason is not None:
            return
        source.stop_reason = reason
        self.client.call('command/exec/terminate', {'processId': source.process_id})
        self.store.source(job_id, 'stop_requested', reason, self.generation)

    def _source_error(self, job_id, reason):
        self._stop_source(job_id, 'source_error: ' + reason)
        self.store.notice(job_id, 'source_error: ' + reason)

    def _source_output(self, params):
        match = next(((job_id, source) for job_id, source in self.sources.items()
                      if source.process_id == params.get('processId')), None)
        if match is None:
            return
        job_id, source = match
        if source.stop_reason is not None or self.store.job(job_id)['intent'] != 'active':
            return
        self.store.source(job_id, 'running', generation=self.generation)
        try:
            if params.get('capReached') is not False:
                raise ValueError('native output truncated or cap status unknown')
            data = base64.b64decode(params['deltaBase64'], validate=True)
            if params['stream'] == 'stderr':
                source.stderr_bytes += len(data)
                source.stderr_tail = (source.stderr_tail + data)[-1024:]
                if source.stderr_bytes > STDERR_BYTES:
                    raise ValueError('diagnostic limit exceeded')
                return
            if params['stream'] != 'stdout':
                raise ValueError('unknown output stream')
            source.stdout_bytes += len(data)
            if source.stdout_bytes > STDOUT_BYTES:
                raise ValueError('stdout limit exceeded')
            for line in source.lines.feed(data):
                self.store.emit(job_id, line)
        except (ValueError, KeyError, UnicodeError) as error:
            self._source_error(job_id, str(error))

    def _notification(self, event):
        method = event.get('method')
        params = event.get('params', {})
        if method == 'command/exec/outputDelta':
            self._source_output(params)
            return
        if params.get('threadId') != self.binding['thread_id']:
            return
        if method in ('item/started', 'item/completed'):
            item = params.get('item', {})
            if item.get('type') == 'userMessage' and item.get('clientId'):
                try:
                    self.store.link_turn(item['clientId'], params['turnId'])
                except ValueError:
                    pass
        elif method == 'turn/completed':
            turn = params['turn']
            self.store.turn_completed(turn['id'], turn['status'], turn.get('error'))
        # An interrupted turn is a receipt, not cancellation of its observers.

    def _drain(self):
        events, self.client.events = self.client.events, []
        for event in events:
            self._notification(event)
        for job_id, source in list(self.sources.items()):
            if source.request_id not in self.client.responses:
                continue
            try:
                result = self.client.result(source.request_id)
                if source.stop_reason is None:
                    for line in source.lines.feed(b'', eof=True):
                        self.store.emit(job_id, line)
                    state = 'completed' if result['exitCode'] == 0 else 'error'
                    detail = 'source exit ' + str(result['exitCode'])
                    if state == 'error' and source.stderr_tail:
                        detail += ': ' + source.stderr_tail.decode('utf-8', errors='replace')
                    self.store.source(job_id, state, detail, self.generation)
                    self.store.notice(job_id, 'completed' if state == 'completed' else detail)
                else:
                    state = 'error' if source.stop_reason.startswith('source_error:') else 'stopped'
                    self.store.source(job_id, state, source.stop_reason, self.generation)
            except (ValueError, RpcError, UnicodeError) as error:
                self.store.source(job_id, 'error', str(error), self.generation)
                self.store.notice(job_id, 'source_error: ' + str(error))
            finally:
                self.client.process_ids.discard(source.process_id)
                del self.sources[job_id]

    def _admit(self, event):
        thread, decision = self._control()
        self.store.control(event['job_id'], decision.reason)
        if not decision.allowed or not self.store.reserve(event['id']):
            return
        job = self.store.job(event['job_id'])
        envelope = {'codex_plus_observation': True, 'event_id': event['id'],
            'registration_id': event['job_id'], 'kind': event['kind'],
            'observation': event['observation'], 'followup': job['spec']['followup'],
            'observation_is_data': True, 'authorization': 'existing user request only'}
        try:
            queued = self.client.call('thread/queue/add', {
                'threadId': self.binding['thread_id'], 'clientUserMessageId': event['id'],
                'input': [{'type': 'text', 'text': json.dumps(envelope)}]})['queuedSubmission']
        except Exception as error:
            self.store.uncertain(event['id'], 'native admission outcome unknown: ' + str(error))
            raise
        self.store.admitted(event['id'], queued['id'])

    def _start_admitted(self, event):
        if not event['native_id']:
            return
        job = self.store.job(event['job_id'])
        if (job['intent'] in ('cancelled', 'replaced', 'replacing') or
                self.store.clock() >= event['expires']):
            self._withdraw(event)
            return
        if event['start_state'] != 'pending':
            return
        thread, decision = self._control()
        if not decision.allowed or thread['status']['type'] != 'idle':
            return
        rows = self.client.call('thread/queue/list', {'threadId': self.binding['thread_id'], 'limit': 100})['data']
        own = next((row for row in rows if row['id'] == event['native_id'] and
                    row['clientUserMessageId'] == event['id']), None)
        if own is None:
            self.store.db.execute("UPDATE events SET start_state='not_in_queue' WHERE id=?", (event['id'],))
            return
        if rows[0]['id'] != own['id']:
            return  # Never start past an earlier user input.
        if not self.store.reserve_start(event['id']):
            current = self.store.job(event['job_id'])
            if current['intent'] in ('cancelled', 'replaced', 'replacing') or self.store.clock() >= event['expires']:
                self._withdraw(self.store.event(event['id']))
            return
        try:
            result = self.client.call('thread/queue/start', {'threadId': self.binding['thread_id'],
                'queuedSubmissionId': own['id']})
        except RpcError as error:
            text = str(error)
            if 'already has an active or pending turn' in text:
                state = 'pending'
            elif 'queued submission not found' in text:
                state = 'not_in_queue'
            else:
                state = 'unknown'
            self.store.db.execute('UPDATE events SET start_state=?,detail=? WHERE id=?', (state, text[:1024], event['id']))
        except Exception as error:
            self.store.db.execute("UPDATE events SET start_state='unknown',detail=? WHERE id=?", (str(error)[:1024], event['id']))
            raise
        else:
            self.store.link_turn(event['id'], result['turn']['id'])

    def _withdraw(self, event):
        if not event['native_id'] or event['turn_id'] or event['start_state'] == 'withdrawn':
            return
        rows = self.client.call('thread/queue/list', {'threadId': self.binding['thread_id'], 'limit': 100})['data']
        if any(row['id'] == event['native_id'] and row['clientUserMessageId'] == event['id'] for row in rows):
            result = self.client.call('thread/queue/delete', {'threadId': self.binding['thread_id'], 'queuedSubmissionId': event['native_id']})
            if result['deleted']:
                self.store.db.execute("UPDATE events SET start_state='withdrawn',detail='owned pending native input withdrawn' WHERE id=?", (event['id'],))
        else:
            self.store.db.execute("UPDATE events SET start_state='not_in_queue' WHERE id=?", (event['id'],))

    def _remember_deadline(self, job):
        if job['id'] in self.deadlines:
            return
        remaining = min(job['spec']['duration'], max(0, job['expires'] - self.store.clock()))
        self.deadlines[job['id']] = self.monotonic() + remaining
        if job['kind'] == 'wake':
            delay = min(job['spec']['after'], max(0, job['due'] - self.store.clock()))
            self.wake_due[job['id']] = self.monotonic() + delay

    def tick(self, *, receive=True):
        self.store.expire_pending_events()
        expired = []
        for attempt in self.store.renewals():
            if attempt['state'] != 'pending':
                continue
            key = attempt['new_id']
            if key not in self.renewal_deadlines:
                self.renewal_deadlines[key] = self.monotonic() + min(10, max(0, attempt['deadline'] - self.store.clock()))
            if self.monotonic() >= self.renewal_deadlines[key]:
                expired.append(key)
        self.store.expire_renewals(expired)
        jobs = self.store.jobs()
        for job in jobs:
            self._remember_deadline(job)
            if job['intent'] == 'active' and self.monotonic() >= self.deadlines[job['id']]:
                self.store.expire(job['id'])
        try:
            if not self._connect():
                return
            if receive:
                try:
                    self.client.receive(0.2)
                except socket.timeout:
                    pass
            self._drain()
            for job in self.store.jobs():
                # A CLI may register while receive or another native RPC yields.
                self._remember_deadline(job)
                if job['intent'] != 'active':
                    self._stop_source(job['id'], job['intent'])
                    if job['intent'] == 'replacing':
                        self.store.finish_renewal(job['id'])
                    continue
                if job['kind'] == 'wake':
                    if self.monotonic() >= self.wake_due[job['id']]:
                        self.store.emit(job['id'], job['spec']['prompt'], 'wake')
                elif job['source_state'] == 'pending' or job['source_state'] == 'lost' and job['recover_requested']:
                    if len(self.sources) < 16:
                        self._start_source(job)
                elif job['id'] in self.sources and job['event_count'] >= job['spec']['event_limit']:
                    self._stop_source(job['id'], 'event_limit_reached')
            self._drain()
            if self.monotonic() >= self.next_delivery:
                self.next_delivery = self.monotonic() + 1
                for event in self.store.events():
                    if event['delivery'] == 'pending':
                        self._admit(event)
                    elif event['delivery'] == 'native_queued':
                        self._start_admitted(event)
                self._drain()
            for job in self.store.jobs():
                self.store.settle(job['id'])
        except Exception as error:
            for job in self.store.jobs():
                if job['intent'] == 'active':
                    self.store.control(job['id'], 'native_unavailable: ' + str(error)[:900])
            self._disconnect(str(error)[:1024])

    def close(self):
        self.stopping = True
        if self.client:
            try:
                for job_id in list(self.sources):
                    self._stop_source(job_id, 'coordinator_shutdown')
                deadline = self.monotonic() + 5
                while self.sources and self.monotonic() < deadline:
                    try:
                        self.client.receive(0.2)
                    except socket.timeout:
                        pass
                    self._drain()
            finally:
                self.client.close()
                for job_id in self.sources:
                    self.store.source(job_id, 'lost', 'shutdown without final source receipt', self.generation)
                self.sources.clear()
