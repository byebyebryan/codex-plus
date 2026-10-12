import base64
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codex_plus.engine import Engine
from codex_plus.native import RpcError
from codex_plus.store import Store


class Backend:
    def __init__(self, binding):
        self.binding = binding
        self.events, self.responses, self.process_ids, self.queue = [], {}, set(), []
        self.sequence = 0
        self.commands, self.calls, self.closed = [], [], False
        self.goal = None
        self.runtime = {'type': 'idle'}
        self.add_error = None
        self.start_error = None

    def bind(self, thread):
        return self.binding

    def submit(self, method, params):
        self.sequence += 1
        self.commands.append((self.sequence, params))
        self.process_ids.add(params['processId'])
        return self.sequence

    def call(self, method, params):
        self.calls.append((method, params))
        if method == 'thread/read':
            return {'thread': {'id': self.binding['thread_id'], 'canAcceptDirectInput': True, 'status': self.runtime}}
        if method == 'thread/goal/get':
            return {'goal': self.goal}
        if method == 'thread/queue/add':
            if self.add_error:
                raise self.add_error
            row = {'id': 'native-' + params['clientUserMessageId'],
                   'clientUserMessageId': params['clientUserMessageId'], 'input': params['input']}
            self.queue.append(row)
            return {'queuedSubmission': row}
        if method == 'thread/queue/list':
            return {'data': list(self.queue)}
        if method == 'thread/queue/start':
            if self.start_error:
                raise self.start_error
            row = next(row for row in self.queue if row['id'] == params['queuedSubmissionId'])
            self.queue.remove(row)
            return {'turn': {'id': 'turn-' + row['clientUserMessageId']}}
        if method == 'thread/queue/delete':
            self.queue = [row for row in self.queue if row['id'] != params['queuedSubmissionId']]
            return {'deleted': True}
        if method == 'command/exec/terminate':
            for rid, command in self.commands:
                if command['processId'] == params['processId']:
                    self.responses[rid] = {'exitCode': 137}
            return {}
        raise AssertionError(method)

    def result(self, rid):
        return self.responses.pop(rid)

    def close(self):
        self.closed = True

    def receive(self, timeout):
        raise TimeoutError('no fake input')

    def output(self, process, data, *, cap=False):
        self.events.append({'method': 'command/exec/outputDelta', 'params': {
            'processId': process, 'stream': 'stdout', 'deltaBase64': base64.b64encode(data).decode(),
            'capReached': cap}})


class EngineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.now = 100.0
        self.store = Store(self.root / 'state', clock=lambda: self.now)
        self.binding = {'thread_id': 'fixture-thread', 'requested_socket': '/fixture/socket'}
        self.backend = Backend(self.binding)
        self.engine = Engine(self.store, self.binding, self.backend, monotonic=lambda: self.now)
        self.spec = {'command': ['rtk', 'proxy', 'fixture-reader'], 'cwd': str(self.root),
                     'duration': 120, 'event_limit': 2}

    def tearDown(self):
        self.engine.close()
        self.store.close()
        self.tmp.cleanup()

    def tick(self):
        self.engine.tick(receive=False)

    def source(self):
        job = self.store.create('watch', self.spec)
        self.tick()
        return job, self.backend.commands[-1][1]['processId']

    def test_paused_goal_holds_delivery_without_stopping_source(self):
        job, process = self.source()
        self.backend.goal = {'threadId': 'fixture-thread', 'status': 'paused'}
        self.backend.output(process, b'useful\n')
        self.now += 1; self.tick()
        self.assertEqual(self.store.job(job)['source_state'], 'running')
        self.assertEqual(self.store.events(job)[0]['delivery'], 'pending')
        self.assertFalse(any(method == 'thread/queue/add' for method, _ in self.backend.calls))
        self.backend.goal['status'] = 'active'
        self.now += 1; self.tick()
        self.assertEqual(self.store.events(job)[0]['delivery'], 'native_queued')
        self.assertFalse(any(method == 'thread/goal/set' for method, _ in self.backend.calls))

    def test_interruption_receipt_does_not_cancel_observation(self):
        job, process = self.source()
        self.backend.events.append({'method': 'turn/completed', 'params': {
            'threadId': 'fixture-thread', 'turn': {'id': 'ordinary-turn', 'status': 'interrupted'}}})
        self.tick()
        self.assertEqual(self.store.job(job)['intent'], 'active')
        self.assertEqual(self.store.job(job)['source_state'], 'running')

    def test_output_truncation_terminates_source_explicitly(self):
        job, process = self.source()
        self.backend.output(process, b'partial', cap=True)
        self.tick()
        self.assertTrue(any(method == 'command/exec/terminate' for method, _ in self.backend.calls))
        self.assertEqual(self.store.job(job)['source_state'], 'error')
        self.assertEqual(self.store.events(job), [])

    def test_cancel_inflight_native_admission_preserves_truth(self):
        job = self.store.create('watch', self.spec)
        event = self.store.emit(job, 'fixture')
        original = self.backend.call
        def call(method, params):
            result = original(method, params)
            if method == 'thread/queue/add':
                self.store.cancel(job)
            return result
        self.backend.call = call
        self.tick()
        self.assertEqual(self.store.job(job)['intent'], 'cancelled')
        self.assertEqual(self.store.event(event)['delivery'], 'native_queued')
        self.now += 1; self.tick()
        self.assertEqual(self.store.event(event)['start_state'], 'withdrawn')
        self.assertEqual(self.backend.queue, [])

    def test_source_error_is_not_watched_job_failure(self):
        job = self.store.create('watch', {**self.spec, 'notify_end': True})
        self.tick()
        rid = self.backend.commands[-1][0]
        self.backend.responses[rid] = {'exitCode': 2}
        self.now += 1; self.tick()
        self.assertEqual(self.store.job(job)['source_state'], 'error')
        notice = self.store.events(job)[0]
        self.assertEqual(notice['kind'], 'lifecycle')
        self.assertEqual(json.loads(notice['observation'])['watched_job_outcome'], 'unknown')

    def test_timeout_after_submission_is_uncertain_and_not_replayed(self):
        job = self.store.create('watch', self.spec)
        event = self.store.emit(job, 'fixture')
        self.backend.add_error = TimeoutError('lost reply')
        self.tick()
        self.assertEqual(self.store.event(event)['delivery'], 'uncertain')
        self.assertTrue(self.backend.closed)
        replacement = Backend(self.binding)
        self.engine.client = replacement
        self.now += 1; self.tick()
        self.assertFalse(any(method == 'thread/queue/add' for method, _ in replacement.calls))

    def test_uncertain_start_keeps_known_admission(self):
        job = self.store.create('watch', self.spec)
        event = self.store.emit(job, 'fixture')
        self.tick()
        self.backend.start_error = TimeoutError('start reply lost')
        self.now += 1; self.tick()
        self.assertEqual(self.store.event(event)['delivery'], 'native_queued')
        self.assertEqual(self.store.event(event)['start_state'], 'unknown')

    def test_busy_start_refusal_and_earlier_user_input_are_preserved(self):
        job = self.store.create('watch', self.spec)
        event = self.store.emit(job, 'fixture')
        self.backend.queue.append({'id': 'human-first', 'clientUserMessageId': 'human', 'input': []})
        self.tick(); self.now += 1; self.tick()
        self.assertFalse(any(method == 'thread/queue/start' for method, _ in self.backend.calls))
        self.backend.queue.pop(0)
        self.backend.start_error = RpcError('thread already has an active or pending turn')
        self.now += 1; self.tick()
        self.assertEqual(self.store.event(event)['start_state'], 'pending')
        self.assertEqual(self.store.event(event)['delivery'], 'native_queued')

    def test_live_correlation_does_not_claim_acknowledgement(self):
        job = self.store.create('watch', self.spec)
        event = self.store.emit(job, 'fixture')
        self.tick()
        self.backend.events.extend([
            {'method': 'item/started', 'params': {'threadId': 'fixture-thread', 'turnId': 'turn',
                'item': {'type': 'userMessage', 'clientId': event}}},
            {'method': 'turn/completed', 'params': {'threadId': 'fixture-thread',
                'turn': {'id': 'turn', 'status': 'completed'}}}])
        self.tick()
        receipt = self.store.event(event)
        self.assertEqual(receipt['turn_outcome'], 'completed')
        self.assertFalse(receipt['acknowledged'])

    def test_source_renewal_has_no_overlap(self):
        parent, process = self.source()
        child = self.store.request_renewal(parent, self.spec)
        self.now += 1; self.tick()
        self.now += 1; self.tick()
        self.assertEqual(self.store.job(parent)['source_state'], 'stopped')
        self.assertEqual(self.store.job(child)['source_state'], 'pending')
        self.now += 1; self.tick()
        self.assertEqual(len(self.engine.sources), 1)
        self.assertIn(child, self.engine.sources)


if __name__ == '__main__':
    unittest.main()
