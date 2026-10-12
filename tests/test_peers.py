import copy
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from codex_plus.native import RpcError
from codex_plus.peers import PeerReader, classification, snapshot, READ_METHODS


A = '00000000-0000-4000-8000-000000000001'
B = '00000000-0000-4000-8000-000000000002'
CHILD = '00000000-0000-4000-8000-000000000003'
FORK = '00000000-0000-4000-8000-000000000004'
OTHER = '00000000-0000-4000-8000-000000000005'
OWNER = {'requested_socket': '/fixture/control', 'resolved_socket': '/fixture/resolved',
         'host': 'fixture', 'uid': 1, 'pid_namespace': 'pid:[1]', 'pid': 100,
         'start_ticks': '200', 'executable': '/fixture/codex'}


def ordinary(identity, name='B'):
    return {'id': identity, 'source': 'vscode', 'threadSource': 'user',
            'parentThreadId': None, 'forkedFromId': None, 'name': name,
            'cwd': '/fixture', 'canAcceptDirectInput': True, 'status': {'type': 'idle'},
            'updatedAt': 100}


class Backend:
    def __init__(self):
        self.identity = dict(OWNER)
        self.threads = {A: ordinary(A, 'A'), B: ordinary(B)}
        self.pages = [[A, B]]
        self.calls = []
        self.turns = [{'id': 'turn-B', 'status': 'completed', 'items': [
            {'id': 'private-user', 'type': 'userMessage', 'content': [{'text': 'private'}]},
            {'id': 'private-tool', 'type': 'commandExecution', 'aggregatedOutput': 'private'},
            {'id': 'reply-B', 'type': 'agentMessage', 'phase': 'final_answer', 'text': 'result'},
        ]}]
        self.goal = None

    def call(self, method, params, timeout=None):
        self.calls.append((method, copy.deepcopy(params), timeout))
        if method == 'thread/loaded/list':
            number = int(params.get('cursor', '0'))
            return {'data': self.pages[number], 'nextCursor': str(number + 1) if number + 1 < len(self.pages) else None}
        if method == 'thread/read':
            return {'thread': copy.deepcopy(self.threads[params['threadId']])}
        if method == 'thread/goal/get':
            return {'goal': copy.deepcopy(self.goal)}
        if method == 'thread/turns/list':
            return {'data': copy.deepcopy(self.turns[:params['limit']]), 'nextCursor': 'older'}
        raise AssertionError('unexpected write or subscription: ' + method)


class PeerTests(unittest.TestCase):
    def setUp(self):
        self.backend = Backend()
        self.owner_patch = patch('codex_plus.peers.listener_identity', return_value=dict(OWNER))
        self.owner_patch.start()
        self.addCleanup(self.owner_patch.stop)
        self.reader = PeerReader(self.backend)
        self.frozen = {**OWNER, 'thread_id': B}

    def test_cli_misclassification_and_fork_ancestry_do_not_hide_independent_peer(self):
        thread = ordinary(FORK)
        thread['forkedFromId'] = A
        self.assertEqual(classification(thread)['kind'], 'independent')
        self.backend.threads[FORK] = thread
        self.backend.pages = [[A], [B, FORK]]
        result = self.reader.discover(caller=A)
        self.assertEqual({row['thread_id'] for row in result['peers']}, {B, FORK})
        self.assertTrue(result['complete'])

    def test_every_native_subagent_variant_is_excluded_from_ordinary_name_matching(self):
        for variant in ('review', 'compact', 'memory_consolidation', {'other': 'future'},
                        {'thread_spawn': {'parent_thread_id': B, 'depth': 1}}):
            with self.subTest(variant=variant):
                child = ordinary(CHILD)
                child['source'] = {'subAgent': variant}
                self.backend.threads[CHILD] = child
                self.backend.pages = [[A, B, CHILD]]
                result = self.reader.discover(caller=A)
                self.assertEqual([row['thread_id'] for row in result['peers']], [B])
                self.assertEqual([row['thread_id'] for row in result['children']], [CHILD])
                self.assertEqual(self.reader.resolve(name='B', caller=A), self.frozen)
                with self.assertRaises(RpcError):
                    self.reader.resolve(target=CHILD, caller=A)

    def test_child_only_match_is_neither_selected_nor_redirected_to_parent(self):
        child = ordinary(CHILD, 'reviewer')
        child.update(source={'subAgent': {'thread_spawn': {'parent_thread_id': B, 'depth': 1}}})
        self.backend.threads[CHILD] = child; self.backend.pages = [[B, CHILD]]
        with self.assertRaises(ValueError):
            self.reader.resolve(name='reviewer', caller=A)

    def test_conflicting_and_missing_provenance_remain_unknown(self):
        for thread in ({'threadSource': 'user', 'parentThreadId': None},
                       {'source': 'unknown', 'forkedFromId': A},
                       {'source': 'vscode', 'parentThreadId': B},
                       {'source': {'subAgent': {'thread_spawn': {'parent_thread_id': B}}}, 'parentThreadId': A},
                       {'source': 'vscode', 'parentThreadId': 'not-a-uuid'}):
            self.assertEqual(classification(thread)['kind'], 'unknown')

    def test_duplicate_independent_names_require_exact_selection(self):
        self.backend.threads[OTHER] = ordinary(OTHER)
        self.backend.pages = [[B, OTHER]]
        with self.assertRaises(ValueError):
            self.reader.resolve(name='B', caller=A)
        self.assertEqual(self.reader.resolve(target=B, caller=A), self.frozen)

    def test_metadata_bound_prevents_false_unique_name_resolution(self):
        self.backend.pages = [[A, B, OTHER]]
        result = self.reader.discover(caller=A, limit=1)
        self.assertFalse(result['complete'])
        self.assertEqual(result['detail'], 'metadata limit reached')

    def test_incomplete_pagination_is_visible_and_not_a_unique_name_claim(self):
        original = self.backend.call
        def call(method, params, timeout=None):
            if method == 'thread/loaded/list':
                return {'data': [B] if not params.get('cursor') else [], 'nextCursor': 'same'}
            return original(method, params, timeout)
        self.backend.call = call
        self.assertFalse(self.reader.discover(caller=A)['complete'])
        with self.assertRaises(ValueError):
            self.reader.resolve(name='B', caller=A)

    def test_metadata_failure_and_notloaded_peer_remain_visible_but_ineligible(self):
        self.backend.pages = [[B, OTHER]]
        self.backend.threads[B]['status'] = {'type': 'notLoaded'}
        result = self.reader.discover(caller=A)
        self.assertFalse(result['complete'])
        self.assertEqual(result['peers'], [])
        self.assertEqual(len(result['unclassified']), 2)
        with self.assertRaises(RpcError):
            self.reader.resolve(target=B, caller=A)

    def test_passive_read_excludes_prompts_and_tool_outputs(self):
        result = self.reader.read(self.frozen)
        self.assertEqual([item['id'] for item in result['turns'][0]['items']], ['reply-B'])
        self.assertTrue({method for method, _, _ in self.backend.calls} <= READ_METHODS)
        self.assertFalse(result['coverage']['lossless'])
        self.assertEqual(result['goal_status'], None)

    def test_observer_never_rebinds_or_loads_missing_peer(self):
        with self.assertRaises(RpcError):
            self.reader.read({**self.frozen, 'pid': 101})
        self.assertEqual(self.backend.calls, [])
        self.backend.pages = [[A]]
        with self.assertRaises(RpcError):
            self.reader.read(self.frozen)
        self.assertEqual({method for method, _, _ in self.backend.calls}, {'thread/loaded/list'})

    def test_owner_replacement_and_goal_identity_mismatch_are_refused(self):
        with patch('codex_plus.peers.listener_identity', return_value={**OWNER, 'start_ticks': '201'}):
            with self.assertRaises(RpcError):
                self.reader.read(self.frozen)
        self.backend.goal = {'threadId': A, 'status': 'complete'}
        with self.assertRaises(RpcError):
            self.reader.read(self.frozen)

    def test_passive_reader_rejects_write_methods(self):
        with self.assertRaises(ValueError):
            self.reader.rpc('thread/resume', {'threadId': B}, 100000)
        self.assertEqual(self.backend.calls, [])

    def test_shared_rpc_budget_does_not_reset_for_history_or_goal(self):
        now = [0]
        original = self.backend.call
        def call(method, params, timeout=None):
            now[0] += 2
            return original(method, params, timeout)
        self.backend.call = call
        reader = PeerReader(self.backend, monotonic=lambda: now[0])
        with self.assertRaises(TimeoutError):
            reader.read(self.frozen, timeout=5)
        self.assertEqual([timeout for _, _, timeout in self.backend.calls], [5, 3, 1])

    def test_snapshot_ignores_timestamp_churn_and_does_not_invent_task_completion(self):
        first = snapshot(self.reader.read(self.frozen), ['reply', 'needs_input', 'goal'])
        self.backend.threads[B]['updatedAt'] = 999
        self.backend.threads[B]['name'] = 'new name'
        second = snapshot(self.reader.read(self.frozen), ['reply', 'needs_input', 'goal'])
        self.assertEqual(first, second)
        self.assertEqual(second['task_outcome'], 'unknown')
        self.backend.goal = {'threadId': B, 'status': 'complete'}
        third = snapshot(self.reader.read(self.frozen), ['goal', 'phase'])
        self.assertEqual(third['goal'], 'complete')
        self.assertEqual(third['task_outcome'], 'unknown')

    def test_reply_requires_completed_turn_and_explicit_final_phase(self):
        self.backend.turns[0]['status'] = 'interrupted'
        self.assertEqual(snapshot(self.reader.read(self.frozen), ['reply'])['reply'], [])
        self.backend.turns[0]['status'] = 'completed'
        self.backend.turns[0]['items'][-1]['phase'] = 'commentary'
        self.assertEqual(snapshot(self.reader.read(self.frozen), ['reply'])['reply'], [])

    def test_input_needed_and_bounded_text_have_truthful_receipts(self):
        self.backend.threads[B]['status'] = {'type': 'active', 'activeFlags': ['waitingOnApproval']}
        self.backend.turns[0]['items'][-1]['text'] = 'é' * 2000
        result = snapshot(self.reader.read(self.frozen), ['reply', 'needs_input'], gap=True)
        self.assertEqual(result['needs_input'], ['waitingOnApproval'])
        self.assertTrue(result['reply'][0]['text_truncated'])
        self.assertTrue(result['coverage']['observation_gap'])
        self.assertLessEqual(len(result['reply'][0]['text'].encode()), 384)


if __name__ == '__main__':
    unittest.main()
