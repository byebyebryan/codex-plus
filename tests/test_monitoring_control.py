"""Control-state cases distinct from worker metadata and watch framing tests."""

import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'spikes/monitoring'))
from control import delivery_decision
from native import RpcError
from spike import Journal, NotSubmitted, deliver
import tempfile


class ControlTests(unittest.TestCase):
    def setUp(self):
        self.thread = {'id': 'fixture-thread', 'canAcceptDirectInput': True,
                       'status': {'type': 'idle'}}
        self.goal = {'threadId': 'fixture-thread', 'status': 'active',
                     'objective': 'fixture', 'tokenBudget': 100}

    def decide(self, response=None):
        return delivery_decision('fixture-thread', self.thread,
                                 {'goal': None} if response is None else response)

    def test_active_and_completed_goals_do_not_block_or_mutate(self):
        for state in ('active', 'complete'):
            self.goal['status'] = state
            before = copy.deepcopy(self.goal)
            self.assertTrue(self.decide({'goal': self.goal}).allowed)
            self.assertEqual(self.goal, before)

    def test_each_stopped_goal_holds_delivery(self):
        for state in ('paused', 'blocked', 'usageLimited', 'budgetLimited'):
            with self.subTest(state=state):
                self.goal['status'] = state
                decision = self.decide({'goal': self.goal})
                self.assertFalse(decision.allowed)
                self.assertEqual(decision.reason, 'goal_' + state)

    def test_unknown_and_wrong_goal_never_supply_authority(self):
        for response in ({}, {'goal': False}, {'goal': {'status': 'active'}},
                         {'goal': {'threadId': 'other', 'status': 'active'}},
                         {'goal': {'threadId': 'fixture-thread', 'status': 'future-state'}}):
            self.assertFalse(self.decide(response).allowed)

    def test_live_busy_thread_can_queue_without_interrupting(self):
        self.thread['status'] = {'type': 'active', 'activeFlags': []}
        self.assertTrue(self.decide().allowed)
        for flags in (None, ['waitingOnApproval'], ['waitingOnUserInput'], ['futureFlag']):
            self.thread['status']['activeFlags'] = flags
            self.assertFalse(self.decide().allowed)

    def test_unavailable_runtime_and_ambiguous_input_capability_hold(self):
        for state in ('notLoaded', 'systemError', 'future-state'):
            self.thread['status'] = {'type': state}
            self.assertFalse(self.decide().allowed)
        self.thread['status'] = {'type': 'idle'}
        for capability in (None, False, 1, 'true'):
            self.thread['canAcceptDirectInput'] = capability
            self.assertFalse(self.decide().allowed)

    def test_thread_binding_and_turn_interruption_are_separate(self):
        self.thread['lastTurnStatus'] = 'interrupted'
        self.assertTrue(self.decide().allowed)
        self.thread['id'] = 'other'
        self.assertFalse(self.decide().allowed)

    def test_stopped_native_preflight_never_enqueues(self):
        client = FakeClient(self.thread, {'goal': {**self.goal, 'status': 'paused'}})
        with self.assertRaises(NotSubmitted):
            deliver(client, client.binding, 'inspect', {'id': 'event', 'job_id': 'watch',
                    'kind': 'source', 'observation': 'fixture'})
        self.assertNotIn('thread/queue/add', client.calls)

    def test_admission_survives_unknown_start_without_replay(self):
        with tempfile.TemporaryDirectory() as root:
            journal = Journal(Path(root) / 'state.db')
            watch = journal.create('watch', {})
            event = journal.emit(watch, 'fixture')
            client = FakeClient(self.thread, {'goal': None}, start_error=TimeoutError('unknown start'))
            journal.dispatch(event, lambda e: deliver(client, client.binding, 'inspect', e))
            journal.dispatch(event, lambda e: self.fail('known admission was replayed'))
            receipt = journal.events(watch)[0]
            self.assertEqual(receipt['state'], 'native_queued')
            self.assertEqual(receipt['native_id'], 'native-queue-id')
            self.assertIn('unknown start', receipt['detail'])
            self.assertEqual(client.calls.count('thread/queue/add'), 1)
            journal.db.close()

    def test_consumed_or_busy_start_keeps_admission_truthful(self):
        for error in ('queued submission not found', 'thread already has an active or pending turn'):
            client = FakeClient(self.thread, {'goal': None}, start_error=RpcError(error))
            event = {'id': 'event', 'job_id': 'watch', 'kind': 'source', 'observation': 'fixture'}
            self.assertEqual(deliver(client, client.binding, 'inspect', event), 'native-queue-id')
            self.assertIn(error, event['_native_start_detail'])
            self.assertEqual(client.input_id, 'event')


class FakeClient:
    binding = {'thread_id': 'fixture-thread'}

    def __init__(self, thread, goal, start_error=None):
        self.thread, self.goal, self.start_error = thread, goal, start_error
        self.calls = []
        self.events = [{'method': 'turn/completed', 'params': {
            'turn': {'status': 'interrupted'}}}]

    def bind(self, thread):
        return self.binding

    def call(self, method, params):
        self.calls.append(method)
        if method == 'thread/read':
            return {'thread': self.thread}
        if method == 'thread/goal/get':
            return self.goal
        if method == 'thread/queue/add':
            self.input_id = params['clientUserMessageId']
            return {'queuedSubmission': {'id': 'native-queue-id'}}
        if method == 'thread/queue/start':
            if self.start_error:
                raise self.start_error
            return {'turn': {'id': 'native-turn-id'}}
        raise AssertionError(method)


if __name__ == '__main__':
    unittest.main()
