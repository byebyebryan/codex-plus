"""Control-state cases distinct from worker metadata and watch framing tests."""

import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'spikes/monitoring'))
from control import delivery_decision


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


if __name__ == '__main__':
    unittest.main()
