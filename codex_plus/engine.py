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
from .peers import PeerReader, snapshot, classification
from .presentation import render_event
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
        self.peer_polls: dict[str, dict] = {}
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
        self.peer_polls.clear()
        self.store.reconcile()
        self.next_connect = self.monotonic() + 2

    def _control(self):
        if self.client.bind(self.binding['thread_id']) != self.binding:
            raise RpcError('frozen binding changed')
        thread = self.client.call('thread/read', {'threadId': self.binding['thread_id']})['thread']
        goal = self.client.call('thread/goal/get', {'threadId': self.binding['thread_id']})
        return thread, delivery_decision(self.binding['thread_id'], thread, goal)

    def _start_source(self, job):
        if job['spec'].get('peer') is not None:
            peer = job['spec']['peer']
            if peer['thread_id'] == self.binding['thread_id'] or {
                    key: value for key, value in peer.items() if key != 'thread_id'} != {
                    key: value for key, value in self.binding.items() if key != 'thread_id'}:
                self.store.source(job['id'], 'error', 'peer must be distinct and in the same frozen daemon')
                self.store.notice(job['id'], 'invalid_peer_binding')
                return
            gap = job['source_state'] == 'lost'
            if not self.store.source(job['id'], 'starting', generation=self.generation):
                return
            self.peer_polls[job['id']] = {'due': self.monotonic(), 'gap': gap}
            self.store.db.execute('UPDATE jobs SET recover_requested=0 WHERE id=?', (job['id'],))
            return
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

    def _stop_source(self, job_id, reason, deadline=None):
        if self.store.job(job_id)['spec'].get('peer') is not None:
            self.peer_polls.pop(job_id, None)
            self.store.source(job_id, 'stopped', reason, self.generation)
            return
        source = self.sources.get(job_id)
        if source is None:
            job = self.store.job(job_id)
            if job['source_state'] in ('pending', 'starting', 'stop_requested'):
                self.store.source(job_id, 'stopped', reason, self.generation)
            return
        if source.stop_reason is not None:
            return
        source.stop_reason = reason
        timeout = 10 if deadline is None else self._remaining(deadline)
        self.client.call('command/exec/terminate', {'processId': source.process_id}, timeout=timeout)
        self.store.source(job_id, 'stop_requested', reason, self.generation)

    def _poll_peer(self, job):
        poll = self.peer_polls[job['id']]
        if self.monotonic() < poll['due']:
            return
        try:
            spec = job['spec']
            reader = PeerReader(self.client, monotonic=self.monotonic)
            read = reader.read(spec['peer'], turn_limit=spec['turn_limit'],
                history=bool(set(spec['signals']) & {'turn', 'reply', 'progress'}),
                goal='goal' in spec['signals'],
                timeout=min(5, self._remaining(self.deadlines[job['id']])))
            # Native reads can yield while the CLI cancels or the lease ends.
            if self.monotonic() >= self.deadlines[job['id']]:
                self.store.expire(job['id'])
                self._stop_source(job['id'], 'expired')
                return
            if not self.store.source(job['id'], 'running',
                    'bounded passive peer snapshots' + ('; observation gap after recovery' if poll['gap'] else ''),
                    self.generation):
                self._stop_source(job['id'], 'intent_changed_during_read')
                return
            self.store.emit(job['id'], json.dumps(snapshot(read, spec['signals'], gap=poll['gap']),
                                                ensure_ascii=False))
            poll['due'] = self.monotonic() + spec['interval']
        except (OSError, ValueError, KeyError, RpcError, TimeoutError) as error:
            self.peer_polls.pop(job['id'], None)
            self.store.source(job['id'], 'lost', 'peer read unavailable: ' + str(error), self.generation)
            self.store.notice(job['id'], 'peer_observation_unavailable')

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
        job = self.store.job(event['job_id'])
        if job['kind'] == 'message' and classification(thread)['kind'] != 'independent':
            self.store.control(event['job_id'], 'peer_provenance_unavailable')
            return
        if not self._message_sender(job):
            return
        self.store.control(event['job_id'], decision.reason)
        if not decision.allowed or not self.store.reserve(event['id']):
            return
        try:
            queued = self.client.call('thread/queue/add', {
                'threadId': self.binding['thread_id'], 'clientUserMessageId': event['id'],
                'input': [{'type': 'text', 'text': render_event(event, job)}]})['queuedSubmission']
        except Exception as error:
            self.store.uncertain(event['id'], 'native admission outcome unknown: ' + str(error))
            raise
        self.store.admitted(event['id'], queued['id'])

    def _message_sender(self, job):
        sender = job['spec'].get('sender') if job['kind'] == 'message' else None
        if sender is None:
            return True  # Legacy messages have no attributed origin.
        if sender['thread_id'] == self.binding['thread_id'] or {
                key: value for key, value in sender.items() if key != 'thread_id'} != {
                key: value for key, value in self.binding.items() if key != 'thread_id'}:
            self.store.control(job['id'], 'sender_owner_unavailable')
            return False
        try:
            PeerReader(self.client).validate(sender)
        except (OSError, ValueError, KeyError, RpcError, TimeoutError):
            self.store.control(job['id'], 'sender_provenance_unavailable')
            return False
        return True

    def _start_admitted(self, event, cleanup_deadline=None):
        if not event['native_id']:
            return
        job = self.store.job(event['job_id'])
        if (job['intent'] in ('cancelled', 'replaced', 'replacing') or
                self.store.clock() >= event['expires']):
            self._withdraw(event, cleanup_deadline)
            return
        if event['start_state'] != 'pending':
            return
        thread, decision = self._control()
        if job['kind'] == 'message' and classification(thread)['kind'] != 'independent':
            self.store.control(event['job_id'], 'peer_provenance_unavailable')
            return
        if not self._message_sender(job):
            return
        if not decision.allowed or thread['status']['type'] != 'idle':
            return
        try:
            own, head = self._queue_find(event, self.monotonic() + 5)
        except Exception as error:
            self.store.db.execute('UPDATE events SET detail=? WHERE id=?', ('queue lookup unresolved: ' + str(error)[:900], event['id']))
            return
        if own is None:
            self.store.db.execute("UPDATE events SET start_state='not_in_queue' WHERE id=?", (event['id'],))
            return
        if head != own['id']:
            return  # Never start past an earlier user input.
        if not self.store.reserve_start(event['id']):
            current = self.store.job(event['job_id'])
            if current['intent'] in ('cancelled', 'replaced', 'replacing') or self.store.clock() >= event['expires']:
                self._withdraw(self.store.event(event['id']), cleanup_deadline)
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

    def _remaining(self, deadline):
        remaining = deadline - self.monotonic()
        if remaining <= 0:
            raise TimeoutError('total reconciliation deadline ended')
        return min(10, remaining)

    def _queue_find(self, event, deadline):
        cursor, head, seen = None, None, set()
        for _ in range(20):
            params = {'threadId': self.binding['thread_id'], 'limit': 100}
            if cursor is not None:
                params['cursor'] = cursor
            page = self.client.call('thread/queue/list', params, timeout=self._remaining(deadline))
            rows = page['data']
            if head is None and rows:
                head = rows[0]['id']
            own = next((row for row in rows if row['id'] == event['native_id'] and
                        row['clientUserMessageId'] == event['id']), None)
            if own is not None:
                return own, head
            cursor = page.get('nextCursor')
            if cursor is None:
                return None, head
            if not isinstance(cursor, str) or cursor in seen:
                raise RpcError('queue pagination incomplete or repeated cursor')
            seen.add(cursor)
        raise RpcError('queue pagination bound reached; membership unknown')

    def _withdraw(self, event, deadline=None):
        if not event['native_id'] or event['withdraw_state'] == 'withdrawn':
            return
        if event['turn_id']:
            self.store.withdrawal(event['id'], 'consumed', 'known native turn is preserved')
            return
        deadline = self.monotonic() + 5 if deadline is None else deadline
        try:
            if self.client.bind(self.binding['thread_id'], timeout=self._remaining(deadline)) != self.binding:
                raise RpcError('frozen binding changed; withdrawal refused')
            own, _ = self._queue_find(event, deadline)
            if own is None:
                self.store.withdrawal(event['id'], 'not_pending', 'owned input absent from complete queue scan; turn outcome remains unknown')
                return
            result = self.client.call('thread/queue/delete', {'threadId': self.binding['thread_id'],
                'queuedSubmissionId': event['native_id']}, timeout=self._remaining(deadline))
            if result.get('deleted') is True:
                self.store.withdrawal(event['id'], 'withdrawn', 'exact owned pending native input withdrawn')
            else:
                self.store.withdrawal(event['id'], 'unknown', 'delete refused or input consumed during cleanup; no retraction proved')
        except Exception as error:
            self.store.withdrawal(event['id'], 'unknown', str(error))

    def _remember_deadline(self, job):
        if job['id'] in self.deadlines:
            return
        remaining = min(job['spec']['duration'], max(0, job['expires'] - self.store.clock()))
        self.deadlines[job['id']] = self.monotonic() + remaining
        if job['kind'] == 'wake':
            delay = min(job['spec']['after'], max(0, job['due'] - self.store.clock()))
            self.wake_due[job['id']] = self.monotonic() + delay

    def _expire_renewals(self):
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

    def tick(self, *, receive=True):
        self.store.expire_pending_events()
        self._expire_renewals()
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
                if job['intent'] == 'active' and self.monotonic() >= self.deadlines[job['id']]:
                    self.store.expire(job['id'])
                    job = self.store.job(job['id'])
                if job['intent'] != 'active':
                    self._stop_source(job['id'], job['intent'])
                    if job['intent'] == 'replacing':
                        self._expire_renewals()
                        self.store.finish_renewal(job['id'])
                    continue
                if job['kind'] == 'wake':
                    if self.monotonic() >= self.wake_due[job['id']]:
                        self.store.emit(job['id'], job['spec']['prompt'], 'wake')
                elif job['source_state'] == 'pending' or job['source_state'] == 'lost' and job['recover_requested']:
                    if len(self.sources) + len(self.peer_polls) < 16:
                        self._start_source(job)
                elif job['id'] in self.sources or job['id'] in self.peer_polls:
                    if job['event_count'] >= job['spec']['event_limit']:
                        self._stop_source(job['id'], 'event_limit_reached')
                    elif job['id'] in self.peer_polls:
                        self._poll_peer(job)
            self._drain()
            if self.monotonic() >= self.next_delivery:
                self.next_delivery = self.monotonic() + 1
                cleanup_deadline = self.monotonic() + 5
                for event in self.store.events():
                    if event['delivery'] == 'pending':
                        self._admit(event)
                    elif event['delivery'] == 'native_queued':
                        self._start_admitted(event, cleanup_deadline)
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
        deadline = self.monotonic() + 5
        events = []
        try:
            for job_id in list(self.peer_polls):
                self._stop_source(job_id, 'coordinator_shutdown', deadline)
            events = [event for event in self.store.events() if event['delivery'] == 'native_queued' and
                      self.store.job(event['job_id'])['intent'] in ('cancelled', 'replaced', 'replacing', 'expired')]
            needs_lookup = any(not event['turn_id'] and event['withdraw_state'] != 'withdrawn' for event in events)
            if self.client is None and needs_lookup:
                # Explicit cleanup can connect to a positively loaded owner, never
                # resume a cold target or restart observation just to cancel it.
                self.client = Client(self.binding['requested_socket'], experimental=True, timeout=self._remaining(deadline))
            if self.client:
                for job_id in list(self.sources):
                    self._stop_source(job_id, 'coordinator_shutdown', deadline)
            for event in events:
                self._withdraw(event, deadline)
            if self.client:
                while self.sources and self.monotonic() < deadline:
                    try:
                        self.client.receive(min(0.2, self._remaining(deadline)))
                    except socket.timeout:
                        pass
                    self._drain()
        except Exception as error:
            for event in events:
                if event['delivery'] == 'native_queued' and not event['turn_id'] and event['withdraw_state'] != 'withdrawn':
                    self.store.withdrawal(event['id'], 'unknown', 'cleanup unresolved: ' + str(error))
        finally:
            if self.client:
                self.client.close()
            for job_id in self.sources:
                self.store.source(job_id, 'lost', 'shutdown without final source receipt', self.generation)
            self.sources.clear()
