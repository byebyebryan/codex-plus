import contextlib
from datetime import timedelta
import io
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch

from codex_plus import diagnostics as d
from codex_plus.diagnostic_source import NativeRecords, normalized_time


def record(kind, **payload):
    return {'type': kind, 'timestamp': '2030-01-01T00:00:00Z', 'payload': payload}


def run_records(turn='turn-one', model='gpt-6.1-sol', effort='xhigh', thread='parent-a'):
    return [record('event_msg', type='task_started', turn_id=turn),
            record('turn_context', turn_id=turn, model=model, effort=effort),
            record('token_usage_record', thread_id=thread, turn_id=turn,
                   response_id=turn + '-response', session_id='session-a', usage={
                       'input_tokens': 10, 'cached_input_tokens': 2, 'cache_write_input_tokens': 0,
                       'output_tokens': 4, 'reasoning_output_tokens': 1, 'total_tokens': 14}),
            record('event_msg', type='task_complete', turn_id=turn,
                   last_agent_message='PRIVATE MESSAGE CONTENT')]


class DiagnosticTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.home = self.base / 'native'; self.home.mkdir(mode=0o700)
        self.root = self.base / 'private'
        self.database = self.home / 'state_5.sqlite'
        with contextlib.closing(sqlite3.connect(self.database)) as connection, connection:
            connection.executescript('CREATE TABLE threads (id TEXT PRIMARY KEY, rollout_path TEXT, '
                                     'attached_thread_parent_id TEXT, agent_path TEXT); CREATE TABLE thread_spawn_edges '
                                     '(parent_thread_id TEXT, child_thread_id TEXT);')
        self.ledger = d.Ledger(self.root, self.home)
        self.add_thread('parent-a', run_records()[:-1])

    def add_thread(self, name, records, parent=None):
        path = self.home / (name + '.jsonl')
        path.write_text(''.join(json.dumps(r) + '\n' for r in records))
        with contextlib.closing(sqlite3.connect(self.database)) as connection, connection:
            connection.execute('INSERT OR REPLACE INTO threads VALUES (?,?,?,?)',
                               (name, str(path), parent, '/root/' + name))
            connection.execute('DELETE FROM thread_spawn_edges WHERE child_thread_id=?', (name,))
            if parent:
                connection.execute('INSERT INTO thread_spawn_edges VALUES (?,?)', (parent, name))
        return path

    def enroll(self):
        self.ledger.start()
        return self.ledger.enroll('parent-a', routing_not_started=True)['episode']

    def test_opt_out_is_read_only_and_start_is_bounded_private_and_not_replaceable(self):
        self.assertFalse(self.ledger.status()['configured'])
        self.assertFalse(self.ledger.enroll('parent-a', if_open=True)['enrolled'])
        self.assertFalse(self.root.exists())
        study = self.ledger.start()
        duration = d.datetime.fromisoformat(study['enrollment_until']) - d.datetime.fromisoformat(study['started_at'])
        self.assertEqual(duration, timedelta(days=7)); self.assertEqual(study['goal_limit'], 8)
        self.assertEqual(self.root.stat().st_mode & 0o777, 0o700)
        for file in self.root.iterdir():
            self.assertEqual(file.stat().st_mode & 0o777, 0o600)
        before = (self.root / 'study.json').read_bytes()
        with self.assertRaises(ValueError): self.ledger.start()
        self.assertEqual((self.root / 'study.json').read_bytes(), before)

    def test_repeated_invocation_reuses_episode_even_when_admission_closes(self):
        key = self.enroll()
        self.ledger.close()
        self.assertFalse(self.ledger.status()['enrollment_open'])
        self.assertEqual(self.ledger.enroll('parent-a', if_open=True)['episode'], key)
        self.assertEqual(len(self.ledger.read()['episodes']), 1)
        self.assertEqual(self.ledger.status()['episodes'][0]['episode'], key)

    def test_expiry_cap_and_close_do_not_stop_or_delete_native_work(self):
        study = self.ledger.start()
        with patch.object(d, 'now', return_value=d.datetime.fromisoformat(study['enrollment_until'])):
            self.assertFalse(self.ledger.enroll('parent-a', if_open=True)['enrolled'])
        for number in range(8):
            name = 'primary-' + str(number)
            self.add_thread(name, run_records(thread=name)[:-1])
            self.ledger.enroll(name)
        self.assertFalse(self.ledger.enroll('parent-a', if_open=True)['enrolled'])
        before = self.database.read_bytes()
        self.ledger.close()
        self.assertEqual(self.database.read_bytes(), before)

    def test_wrong_model_child_missing_context_and_wrong_environment_do_not_enroll(self):
        self.ledger.start()
        for name, records, parent in (
                ('terra', run_records(model='gpt-6.1-terra'), None),
                ('child', run_records(model='gpt-6-luna', effort='max'), 'parent-a'),
                ('no-context', [record('event_msg', type='task_started', turn_id='a')], None)):
            self.add_thread(name, records, parent)
            with self.assertRaises(ValueError): self.ledger.enroll(name)
        other = self.base / 'other'; other.mkdir()
        with self.assertRaises(ValueError): d.Ledger(self.root, other).read()

    def test_new_study_freezes_first_supported_primary_and_refuses_other_version_without_mutation(self):
        self.ledger.start()
        self.add_thread('primary-62', run_records('first-62', 'gpt-6.2-sol', 'xhigh', 'primary-62')[:-1])
        first = self.ledger.enroll('primary-62')
        self.assertFalse(first['existing'])
        self.assertEqual(self.ledger.read()['version_policy'], 'freeze-first-primary')
        self.assertEqual(self.ledger.read()['primary_selection'],
                         {'model': 'gpt-6.2-sol', 'effort': 'xhigh'})
        self.assertEqual(self.ledger.read()['episodes'][first['episode']]['primary_selection'],
                         {'model': 'gpt-6.2-sol', 'effort': 'xhigh'})

        self.add_thread('primary-61', run_records('first-61', 'gpt-6.1-sol', 'xhigh', 'primary-61')[:-1])
        before = (self.root / 'study.json').read_bytes()
        with self.assertRaises(ValueError):
            self.ledger.enroll('primary-61')
        self.assertEqual((self.root / 'study.json').read_bytes(), before)

    def test_unversioned_legacy_study_keeps_exact_sol_61_expectation_without_migration(self):
        self.ledger.start()
        path = self.root / 'study.json'
        legacy = json.loads(path.read_text())
        legacy.pop('version_policy')
        legacy.pop('primary_selection')
        path.write_text(json.dumps(legacy))
        self.add_thread('legacy-primary', run_records('legacy-turn', 'gpt-6.1-sol', 'xhigh',
                                                      'legacy-primary')[:-1])
        enrolled = self.ledger.enroll('legacy-primary')
        saved = self.ledger.read()
        self.assertNotIn('version_policy', saved)
        self.assertNotIn('primary_selection', saved)
        self.assertNotIn('primary_selection', saved['episodes'][enrolled['episode']])
        self.assertEqual(self.ledger.status()['version_policy'], d.LEGACY_VERSION_POLICY)
        self.assertEqual(self.ledger.status()['primary_selection'],
                         {'model': 'gpt-6.1-sol', 'effort': 'xhigh'})

        self.add_thread('legacy-newer', run_records('newer-turn', 'gpt-6.2-sol', 'xhigh',
                                                    'legacy-newer')[:-1])
        before = path.read_bytes()
        with self.assertRaises(ValueError):
            self.ledger.enroll('legacy-newer')
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(len(self.ledger.read()['episodes']), 1)

    def test_concurrent_first_enrollments_freeze_one_native_snapshot(self):
        self.ledger.start()
        self.add_thread('primary-62', run_records('first-62', 'gpt-6.2-sol', 'xhigh', 'primary-62')[:-1])
        self.add_thread('primary-63', run_records('first-63', 'gpt-6.3-sol', 'xhigh', 'primary-63')[:-1])
        original_read = self.ledger.read
        barrier = threading.Barrier(2)
        local = threading.local()

        def synchronized_read():
            study = original_read()
            if not getattr(local, 'initial_snapshot', False):
                local.initial_snapshot = True
                barrier.wait(timeout=5)
            return study

        def enroll(name):
            try:
                return ('enrolled', self.ledger.enroll(name))
            except ValueError:
                return ('refused', None)

        with patch.object(self.ledger, 'read', side_effect=synchronized_read):
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = [pool.submit(enroll, name) for name in ('primary-62', 'primary-63')]
                outcomes = [future.result(timeout=10) for future in results]
        self.assertEqual([state for state, _ in outcomes].count('enrolled'), 1)
        self.assertEqual([state for state, _ in outcomes].count('refused'), 1)
        study = original_read()
        self.assertEqual(len(study['episodes']), 1)
        frozen = study['primary_selection']['model']
        self.assertIn(frozen, ('gpt-6.2-sol', 'gpt-6.3-sol'))
        self.assertEqual(next(iter(study['episodes'].values()))['primary_selection']['model'], frozen)

    def test_mid_episode_primary_upgrade_is_reported_against_frozen_selection(self):
        self.ledger.start()
        self.add_thread('parent-a', run_records('turn-62', 'gpt-6.2-sol', 'xhigh')[:-1])
        key = self.ledger.enroll('parent-a', routing_not_started=True)['episode']
        self.add_thread('parent-a', run_records('turn-62', 'gpt-6.2-sol', 'xhigh') +
                        run_records('turn-63', 'gpt-6.3-sol', 'xhigh'))
        self.assertTrue(self.ledger.enroll('parent-a')['existing'])
        result = self.ledger.collect(key)
        self.assertIn('primary_selection_changed_or_unknown', result['source_gaps'])
        self.assertEqual(result['version_policy'], 'freeze-first-primary')
        self.assertEqual(result['study_primary_selection'], {'model': 'gpt-6.2-sol', 'effort': 'xhigh'})
        turns = result['accounting']['threads'][0]['turns']
        self.assertEqual({turn['model'] for turn in turns}, {'gpt-6.2-sol', 'gpt-6.3-sol'})

    def test_luna_new_versions_remain_visible_and_mixed_versions_are_a_gap(self):
        key = self.enroll()
        worker_records = (run_records('luna-61', 'gpt-6.1-luna', 'max', 'worker-a') +
                          run_records('luna-62', 'gpt-6.2-luna', 'max', 'worker-a'))
        self.add_thread('worker-a', worker_records, 'parent-a')
        self.ledger.link(key, 'worker-a', 'luna-61', route='luna')
        self.ledger.link(key, 'worker-a', 'luna-62', route='luna')
        result = self.ledger.collect(key)
        self.assertIn('luna_model_versions_mixed', result['source_gaps'])
        self.assertNotIn('luna_selection_mismatch_or_unknown', result['source_gaps'])
        worker = next(thread for thread in result['accounting']['threads']
                      if thread['thread_id'] == 'worker-a')
        self.assertEqual({turn['model'] for turn in worker['turns']},
                         {'gpt-6.1-luna', 'gpt-6.2-luna'})

    def test_legacy_study_preserves_exact_luna_6_expectation(self):
        self.ledger.start()
        path = self.root / 'study.json'
        legacy = json.loads(path.read_text())
        legacy.pop('version_policy')
        legacy.pop('primary_selection')
        path.write_text(json.dumps(legacy))
        key = self.ledger.enroll('parent-a')['episode']
        self.add_thread('worker-a', run_records('luna-61', 'gpt-6.1-luna', 'max', 'worker-a'), 'parent-a')
        self.ledger.link(key, 'worker-a', 'luna-61', route='luna')
        result = self.ledger.collect(key)
        self.assertIn('luna_selection_mismatch_or_unknown', result['source_gaps'])

    def test_parent_continuations_child_reuse_and_explicit_outcome(self):
        key = self.enroll()
        self.add_thread('worker-a', run_records('child-one', 'gpt-6-luna', 'max', 'worker-a') +
                        run_records('child-two', 'gpt-6-luna', 'max', 'worker-a'), 'parent-a')
        self.ledger.link(key, 'worker-a', 'child-two', route='luna', first_result='correction')
        self.ledger.link(key, None, None, route='luna', status='spawn_rejected')
        self.ledger.link(key, 'parent-a', 'turn-one', route='primary')
        self.add_thread('parent-a', run_records() + run_records('turn-two'))
        self.ledger.outcome(key, 'minor_correction', 'artifact:check', children_reviewed=True)
        before = {p: p.read_bytes() for p in self.home.iterdir() if p.is_file()}
        result = self.ledger.collect(key)
        self.assertEqual(result['acceptance']['result'], 'minor_correction')
        self.assertFalse(result['claims']['billing']); self.assertFalse(result['claims']['causal_comparison'])
        self.assertEqual(len(result['assignments']), 3)
        self.assertEqual(result['accounting']['usage']['categories']['total_tokens']['unambiguous_sum'], 42)
        self.assertNotIn('PRIVATE MESSAGE CONTENT', json.dumps(result))
        self.assertEqual(before, {p: p.read_bytes() for p in self.home.iterdir() if p.is_file()})

    def test_completed_history_and_shared_native_turn_cannot_be_new_enrollments(self):
        self.ledger.start()
        self.add_thread('finished', run_records(thread='finished'))
        with self.assertRaises(ValueError): self.ledger.enroll('finished')
        key = self.ledger.enroll('parent-a')['episode']
        self.ledger.outcome(key, 'unresolved')
        with self.assertRaises(ValueError): self.ledger.enroll('parent-a')

    def test_cli_open_study_requires_this_loaded_sol_primary(self):
        self.ledger.start()
        before = (self.root / 'study.json').read_bytes()
        with patch.dict(os.environ, {'CODEX_HOME': str(self.home), 'CODEX_THREAD_ID': 'parent-a'}):
            for selection in ({'status': 'unknown'}, {'status': 'known', 'model': 'gpt-6.1-terra',
                                                    'reasoning_effort': 'xhigh'},
                              {'status': 'known', 'model': 'gpt-6-astra',
                               'reasoning_effort': 'xhigh'},
                              {'status': 'known', 'model': 'gpt-6-luna',
                               'reasoning_effort': 'max'}):
                with patch.object(d, 'primary_selection', return_value=selection), contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(d.main(['--state-root', str(self.root), 'enroll']), 1)
        self.assertEqual((self.root / 'study.json').read_bytes(), before)

    def test_cli_loaded_guard_accepts_supported_sol_62_and_records_its_native_selection(self):
        self.ledger.start()
        self.add_thread('parent-a', run_records('turn-62', 'gpt-6.2-sol', 'xhigh')[:-1])
        output = io.StringIO()
        selection = {'status': 'known', 'model': 'gpt-6.2-sol', 'reasoning_effort': 'xhigh'}
        with (patch.dict(os.environ, {'CODEX_HOME': str(self.home), 'CODEX_THREAD_ID': 'parent-a'}),
              patch.object(d, 'primary_selection', return_value=selection),
              contextlib.redirect_stdout(output)):
            self.assertEqual(d.main(['--state-root', str(self.root), 'enroll']), 0)
        self.assertTrue(json.loads(output.getvalue())['enrolled'])
        self.assertEqual(self.ledger.status()['primary_selection'],
                         {'model': 'gpt-6.2-sol', 'effort': 'xhigh'})

    def test_old_worker_turn_and_shared_worker_turn_are_not_reassigned(self):
        key = self.enroll()
        old = run_records('old', 'gpt-6-luna', 'max', 'worker-a')
        for r in old: r['timestamp'] = '2029-01-01T00:00:00Z'
        self.add_thread('worker-a', old + run_records('new', 'gpt-6-luna', 'max', 'worker-a'), 'parent-a')
        with self.assertRaises(ValueError): self.ledger.link(key, 'worker-a', 'old', route='luna')
        self.ledger.link(key, 'worker-a', 'new', route='luna')
        self.ledger.outcome(key, 'accepted_first_review')
        self.add_thread('parent-a', run_records('turn-two')[:-1])
        another = self.ledger.enroll('parent-a')['episode']
        with self.assertRaises(ValueError): self.ledger.link(another, 'worker-a', 'new', route='luna')

    def test_exact_worker_path_resolves_only_unambiguous_owned_new_turn(self):
        key = self.enroll()
        old = run_records('old', 'gpt-6-luna', 'max', 'worker-a')
        for r in old: r['timestamp'] = '2029-01-01T00:00:00Z'
        self.add_thread('worker-a', old + run_records('new', 'gpt-6-luna', 'max', 'worker-a'), 'parent-a')
        result = self.ledger.link(key, None, None, route='luna', worker='/root/worker-a')
        self.assertEqual((result['thread_id'], result['turn_id']), ('worker-a', 'new'))
        with self.assertRaises(ValueError):
            self.ledger.link(key, None, None, route='luna', worker='/root/worker-a')
        self.add_thread('worker-a', run_records('next') + run_records('another'), 'parent-a')
        with self.assertRaises(ValueError):
            self.ledger.link(key, None, None, route='luna', worker='/root/worker-a')
        self.add_thread('foreign', run_records('x'), 'another-parent')
        with self.assertRaises(ValueError):
            self.ledger.link(key, None, None, route='luna', worker='/root/foreign')

    def test_foreign_records_cannot_supply_enrollment_context_or_window(self):
        original = run_records()[:-1]
        copied = [record('event_msg', type='task_started', turn_id='foreign-turn', thread_id='foreign'),
                  record('turn_context', turn_id='foreign-turn', thread_id='foreign',
                         model='gpt-6.1-sol', effort='xhigh')]
        self.add_thread('parent-a', original + copied)
        key = self.enroll()
        episode = self.ledger.read()['episodes'][key]
        self.assertEqual(episode['start_turn'], 'turn-one')
        self.assertIn('foreign_thread_native_record', episode['source_gaps'])
        self.ledger.outcome(key, 'unresolved')
        foreign_context = record('turn_context', turn_id='own-turn', thread_id='foreign',
                                 model='gpt-6.1-sol', effort='xhigh')
        self.add_thread('another', [record('event_msg', type='task_started', turn_id='own-turn'), foreign_context])
        with self.assertRaises(ValueError): self.ledger.enroll('another')

    def test_timestamp_projection_normalizes_valid_and_omits_arbitrary_private_text(self):
        key = self.enroll()
        records = run_records()
        records[0]['payload']['started_at'] = 'PRIVATE TIMESTAMP CONTENT'
        records[-1]['payload']['completed_at'] = 'PRIVATE TIMESTAMP CONTENT'
        records[-1]['timestamp'] = 'PRIVATE TIMESTAMP CONTENT'
        self.add_thread('parent-a', records)
        result = self.ledger.collect(key)
        self.assertIn('invalid_native_timestamp', result['source_gaps'])
        self.assertNotIn('PRIVATE TIMESTAMP CONTENT', json.dumps(result))
        times = result['native_turn_times'][0]
        self.assertEqual(times['native_start_times'], ['2030-01-01T00:00:00+00:00'])
        self.assertEqual(times['native_completion_times'], [])

    def test_native_nullable_unix_seconds_preserve_precision_and_reject_other_values(self):
        records = run_records()
        records[0]['timestamp'] = '2030-01-01T00:00:00.125Z'
        records[0]['payload']['started_at'] = 1893456000
        records[-1]['payload']['started_at'] = None
        records[-1]['payload']['completed_at'] = 1893456001
        self.add_thread('parent-a', records[:-1])
        key = self.enroll()
        self.add_thread('parent-a', records)
        result = self.ledger.collect(key)
        self.assertNotIn('invalid_native_timestamp', result['source_gaps'])
        self.assertEqual(result['native_turn_times'][0]['native_start_times'], ['2030-01-01T00:00:00+00:00'])
        self.assertEqual(result['native_turn_times'][0]['native_completion_times'], ['2030-01-01T00:00:01+00:00'])
        from codex_plus.diagnostic_source import start_time
        projected, _, _ = NativeRecords(self.home).read('parent-a')
        self.assertEqual(start_time(projected, 'turn-one'), '2030-01-01T00:00:00.125000+00:00')
        older = run_records('older-child', 'gpt-6-luna', 'max', 'worker-a')
        older[0]['timestamp'] = '2030-01-01T00:00:00.100Z'
        older[0]['payload']['started_at'] = 1893456000
        self.add_thread('worker-a', older, 'parent-a')
        with self.assertRaises(ValueError):
            self.ledger.link(key, 'worker-a', 'older-child', route='luna')
        self.assertIsNone(normalized_time(1893456000))
        self.assertEqual(normalized_time(0, unix_seconds=True), '1970-01-01T00:00:00+00:00')
        for value in (True, False, 1893456000.0, 10 ** 30, 'private timing text'):
            with self.subTest(value_type=type(value).__name__):
                self.assertIsNone(normalized_time(value, unix_seconds=True))

    def test_cutoff_and_changed_model_are_visible_without_dropping_usage(self):
        key = self.enroll()
        self.add_thread('worker-a', run_records('child', 'gpt-6.1-terra', 'xhigh', 'worker-a'), 'parent-a')
        self.ledger.link(key, 'worker-a', 'child', route='other')
        cutoff = d.datetime.fromisoformat(self.ledger.read()['observation_until'])
        with patch.object(d, 'now', return_value=cutoff + timedelta(days=1)):
            self.ledger.outcome(key, 'unresolved')
        result = self.ledger.collect(key)
        self.assertTrue(result['acceptance']['after_observation_cutoff'])
        self.assertIn('policy_deviation_recorded', result['source_gaps'])
        self.assertIn('selected_turn_terminal_evidence_missing', result['source_gaps'])
        self.assertEqual(result['accounting']['usage']['categories']['total_tokens']['unambiguous_sum'], 28)

    def test_foreign_child_duplicate_links_and_post_outcome_writes_rejected(self):
        key = self.enroll()
        self.add_thread('foreign', run_records('x'), 'another-parent')
        with self.assertRaises(ValueError): self.ledger.link(key, 'foreign', 'x', route='luna')
        with self.assertRaises(ValueError): self.ledger.link(key, 'parent-a', 'turn-one', route='luna')
        self.ledger.link(key, 'parent-a', 'turn-one', route='primary')
        with self.assertRaises(ValueError): self.ledger.link(key, 'parent-a', 'turn-one', route='primary')
        self.ledger.outcome(key, 'unresolved')
        with self.assertRaises(ValueError): self.ledger.outcome(key, 'accepted_first_review')
        with self.assertRaises(ValueError): self.ledger.link(key, None, None, route='luna', status='controls_missing')

    def test_completion_does_not_create_acceptance_or_hide_missing_coverage(self):
        key = self.enroll()
        result = self.ledger.collect(key)
        self.assertIsNone(result['acceptance'])
        self.assertIn('child_assignment_coverage_requires_review', result['source_gaps'])
        self.assertFalse(result['claims']['complete_workflow'])

    def test_symlinks_public_modes_and_native_path_escape_rejected(self):
        self.root.symlink_to(self.home)
        with self.assertRaises(ValueError): self.ledger.start()
        self.root.unlink(); self.ledger.start()
        (self.root / 'study.json').chmod(0o644)
        with self.assertRaises(ValueError): self.ledger.read()
        (self.root / 'study.json').unlink(); (self.root / 'study.json').symlink_to(self.database)
        with self.assertRaises(OSError): self.ledger.read()
        outside = self.base / 'outside.jsonl'; outside.write_text('{}\n')
        with contextlib.closing(sqlite3.connect(self.database)) as connection, connection:
            connection.execute('UPDATE threads SET rollout_path=? WHERE id=?', (str(outside), 'parent-a'))
        with self.assertRaises(ValueError): NativeRecords(self.home).read('parent-a')

    def test_malformed_partial_and_large_records_report_gaps_without_raw_data(self):
        path = self.home / 'parent-a.jsonl'
        with path.open('ab') as stream:
            stream.write(b'not json\n' + b'x' * 50 + b'\n' + b'{"private":"tail"}')
        with patch('codex_plus.diagnostic_source.MAX_LINE', 40):
            records, gaps, parent = NativeRecords(self.home).read('parent-a')
        self.assertIn('malformed_native_line', gaps)
        self.assertIn('oversized_native_line', gaps)
        self.assertIn('incomplete_native_line', gaps)
        self.assertIsNone(parent)
        self.assertNotIn('PRIVATE', json.dumps(records))

    def test_read_budget_is_bounded_and_native_index_is_query_only(self):
        source = NativeRecords(self.home)
        source.remaining = 0
        self.assertEqual(source.read('parent-a')[1], ['read_budget_exhausted'])
        connection = source.connect(); self.addCleanup(connection.close)
        with self.assertRaises(sqlite3.OperationalError): connection.execute('DELETE FROM threads')

    def test_cli_failure_redacts_private_paths_and_opt_out_needs_no_native_owner(self):
        output = io.StringIO()
        with patch.dict(os.environ, {'CODEX_HOME': str(self.home)}), contextlib.redirect_stdout(output):
            status = d.main(['--state-root', str(self.root), 'enroll', '--if-open'])
        self.assertEqual(status, 0); self.assertFalse(self.root.exists())
        self.assertFalse(json.loads(output.getvalue())['enrolled'])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = d.main(['--state-root', str(self.root), 'collect', 'unknown'])
        self.assertEqual(status, 1); self.assertNotIn(str(self.base), output.getvalue())


if __name__ == '__main__':
    unittest.main()
