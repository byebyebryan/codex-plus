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


def run_records(turn='turn-one', model='gpt-6.1-sol', effort='xhigh', thread='parent-a', *, root=None):
    records = [record('event_msg', type='task_started', turn_id=turn),
            record('turn_context', turn_id=turn, model=model, effort=effort),
            record('token_usage_record', thread_id=thread, turn_id=turn,
                   response_id=turn + '-response', session_id='session-a', usage={
                       'input_tokens': 10, 'cached_input_tokens': 2, 'cache_write_input_tokens': 0,
                       'output_tokens': 4, 'reasoning_output_tokens': 1, 'total_tokens': 14}),
            record('event_msg', type='task_complete', turn_id=turn,
                   last_agent_message='PRIVATE MESSAGE CONTENT')]
    if root is not None:
        records[0]['payload']['root_turn_id'] = root
    return records


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

    def astra_study(self):
        return d.AstraStudy(self.root, self.home)

    def add_astra_primary(self, name, turn='astra-turn', *, model='gpt-6.2-astra', effort='xhigh'):
        return self.add_thread(name, run_records(turn, model, effort, name)[:-1])

    @staticmethod
    def loaded_astra(model='gpt-6.2-astra', effort='xhigh'):
        return {'status': 'known', 'model': model, 'reasoning_effort': effort,
                'source': 'loaded_thread_configuration', 'execution_verified': False}

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

    def test_new_study_records_different_primary_versions_without_freezing(self):
        self.ledger.start()
        for suffix in ('61', '62', '63'):
            model='gpt-6.'+suffix[-1]+'-sol'
            name='primary-'+suffix
            self.add_thread(name, run_records('first-'+suffix, model, 'xhigh', name)[:-1])
            self.ledger.enroll(name)
        study=self.ledger.read()
        self.assertEqual(study['version_policy'], d.VERSION_POLICY)
        self.assertIsNone(study['primary_selection'])
        self.assertEqual({e['primary_selection']['model'] for e in study['episodes'].values()},
                         {'gpt-6.1-sol','gpt-6.2-sol','gpt-6.3-sol'})

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

    def test_concurrent_different_versions_keep_both_exact_selections(self):
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
        self.assertEqual([state for state, _ in outcomes].count('enrolled'), 2)
        self.assertEqual([state for state, _ in outcomes].count('refused'), 0)
        study = original_read()
        self.assertEqual(len(study['episodes']), 2)
        self.assertIsNone(study['primary_selection'])
        self.assertEqual({e['primary_selection']['model'] for e in study['episodes'].values()},
                         {'gpt-6.2-sol','gpt-6.3-sol'})

    def test_mid_episode_upgrade_is_an_observation_with_separate_usage_groups(self):
        self.ledger.start()
        self.add_thread('parent-a', run_records('turn-62', 'gpt-6.2-sol', 'xhigh')[:-1])
        key = self.ledger.enroll('parent-a', routing_not_started=True)['episode']
        self.add_thread('parent-a', run_records('turn-62', 'gpt-6.2-sol', 'xhigh') +
                        run_records('turn-63', 'gpt-6.3-sol', 'xhigh'))
        self.assertTrue(self.ledger.enroll('parent-a')['existing'])
        result = self.ledger.collect(key)
        self.assertNotIn('primary_selection_changed_or_unknown', result['source_gaps'])
        self.assertEqual(result['version_policy'], d.VERSION_POLICY)
        self.assertIsNone(result['study_primary_selection'])
        self.assertEqual(result['episode_primary_selection'], {'model':'gpt-6.2-sol','effort':'xhigh'})
        self.assertTrue(result['model_observations']['versions_changed_within_episode'])
        groups=result['accounting']['usage_by_context']
        self.assertEqual({g['model'] for g in groups}, {'gpt-6.2-sol','gpt-6.3-sol'})
        self.assertEqual([g['categories']['total_tokens']['unambiguous_sum'] for g in groups], [14,14])
        turns = result['accounting']['threads'][0]['turns']
        self.assertEqual({turn['model'] for turn in turns}, {'gpt-6.2-sol', 'gpt-6.3-sol'})

    def test_luna_versions_remain_separate_without_becoming_coverage_errors(self):
        key = self.enroll()
        worker_records = (run_records('luna-61', 'gpt-6.1-luna', 'max', 'worker-a') +
                          run_records('luna-62', 'gpt-6.2-luna', 'max', 'worker-a'))
        self.add_thread('worker-a', worker_records, 'parent-a')
        self.ledger.link(key, 'worker-a', 'luna-61', route='luna')
        self.ledger.link(key, 'worker-a', 'luna-62', route='luna')
        result = self.ledger.collect(key)
        self.assertNotIn('luna_model_versions_mixed', result['source_gaps'])
        self.assertTrue(result['model_observations']['versions_changed_within_episode'])
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

    def test_explicit_update_preserves_legacy_goals_outcomes_bounds_and_native_files(self):
        self.ledger.start()
        path=self.root/'study.json'
        legacy=json.loads(path.read_text())
        legacy.pop('version_policy');legacy.pop('primary_selection')
        path.write_text(json.dumps(legacy))
        key=self.ledger.enroll('parent-a')['episode']
        self.add_thread('parent-a',run_records())
        self.ledger.outcome(key,'minor_correction','artifact:review',children_reviewed=True)
        before=self.ledger.read()
        original_bytes=path.read_bytes()
        native={p:p.read_bytes() for p in self.home.iterdir() if p.is_file()}
        result=self.ledger.allow_model_upgrades()
        after=self.ledger.read()
        self.assertTrue(result['version_policy_updated'])
        for name,value in before.items():
            self.assertEqual(after[name],value)
        self.assertEqual(after['version_policy'],d.VERSION_POLICY)
        self.assertEqual(after['version_policy_changes'][0]['previous_version_policy'],d.LEGACY_VERSION_POLICY)
        backup=self.root/after['version_policy_changes'][0]['backup']
        self.assertEqual(backup.read_bytes(),original_bytes)
        self.assertEqual(backup.stat().st_mode&0o777,0o600)
        self.assertEqual(native,{p:p.read_bytes() for p in native})
        snapshot=path.read_bytes()
        self.assertFalse(self.ledger.allow_model_upgrades()['version_policy_updated'])
        self.assertEqual(path.read_bytes(),snapshot)
        self.assertEqual(len(list(self.root.glob('study.before-model-upgrades-*.json'))),1)
        self.add_thread('parent-a',run_records()+run_records('next-turn','gpt-6.2-sol','xhigh')[:-1])
        second=self.ledger.enroll('parent-a')['episode']
        self.assertNotEqual(second,key)
        self.assertEqual(self.ledger.read()['episodes'][key],before['episodes'][key])
        old=self.ledger.collect(key)
        self.assertEqual(old['episode_primary_selection'],{'model':'gpt-6.1-sol','effort':'xhigh'})
        self.assertEqual(old['model_observations']['primary_models'],['gpt-6.1-sol'])
        self.assertEqual(old['episode_primary_selection_source'],'native_start_context')
        self.add_thread('parent-a',[r for r in run_records() if r['type']!='turn_context'])
        missing=self.ledger.collect(key)
        self.assertEqual(missing['episode_primary_selection'],{'model':'gpt-6.1-sol','effort':'xhigh'})
        self.assertEqual(missing['episode_primary_selection_source'],'prior_enrollment_contract')
        self.assertIn('primary_start_selection_unknown',missing['source_gaps'])
        self.assertEqual(missing['model_observations']['primary_models'],[])

    def test_frozen_study_remains_frozen_until_explicitly_updated(self):
        self.ledger.start()
        with self.ledger.write() as study:
            study['version_policy']=d.FROZEN_VERSION_POLICY
            self.ledger.save(study)
        key=self.ledger.enroll('parent-a')['episode']
        self.add_thread('other',run_records('other-turn','gpt-6.2-sol','xhigh','other')[:-1])
        before=(self.root/'study.json').read_bytes()
        with self.assertRaises(ValueError):self.ledger.enroll('other')
        self.assertEqual((self.root/'study.json').read_bytes(),before)
        episode=self.ledger.read()['episodes'][key]
        self.ledger.allow_model_upgrades()
        self.assertEqual(self.ledger.read()['episodes'][key],episode)
        self.assertTrue(self.ledger.enroll('other')['enrolled'])
        self.assertIsNone(self.ledger.status()['primary_selection'])

    def test_cli_explicit_policy_update_does_not_start_or_extend_study(self):
        self.ledger.start()
        with self.ledger.write() as study:
            study['version_policy']=d.FROZEN_VERSION_POLICY
            self.ledger.save(study)
        before=self.ledger.read()
        output=io.StringIO()
        with patch.dict(os.environ,{'CODEX_HOME':str(self.home)}), contextlib.redirect_stdout(output):
            self.assertEqual(d.main(['--state-root',str(self.root),'allow-model-upgrades']),0)
        result=json.loads(output.getvalue())
        self.assertTrue(result['version_policy_updated'])
        self.assertEqual(result['version_policy'],d.VERSION_POLICY)
        after=self.ledger.read()
        for name in ('id','episodes','started_at','enrollment_until','observation_until','goal_limit'):
            self.assertEqual(after[name],before[name])

    def test_update_never_reopens_closed_or_extends_expired_study(self):
        with self.assertRaises(ValueError):self.ledger.allow_model_upgrades()
        self.assertFalse(self.root.exists())
        self.ledger.start()
        with self.ledger.write() as study:
            study['version_policy']=d.FROZEN_VERSION_POLICY
            self.ledger.save(study)
        before=self.ledger.read()
        with patch.object(d,'now',return_value=d.datetime.fromisoformat(before['enrollment_until'])):
            self.ledger.allow_model_upgrades()
            self.assertFalse(self.ledger.status()['enrollment_open'])
            self.assertFalse(self.ledger.enroll('parent-a',if_open=True)['enrolled'])
        after=self.ledger.read()
        for name in ('id','started_at','enrollment_until','observation_until','goal_limit'):
            self.assertEqual(after[name],before[name])
        with self.ledger.write() as study:
            study['version_policy']=d.FROZEN_VERSION_POLICY
            self.ledger.save(study)
        self.ledger.close()
        snapshot=(self.root/'study.json').read_bytes()
        with self.assertRaises(ValueError):self.ledger.allow_model_upgrades()
        self.assertEqual((self.root/'study.json').read_bytes(),snapshot)

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
        self.assertIsNone(self.ledger.status()['primary_selection'])
        self.assertEqual(next(iter(self.ledger.read()['episodes'].values()))['primary_selection'],
                         {'model': 'gpt-6.2-sol', 'effort': 'xhigh'})

    def test_usage_reads_current_root_and_named_workers_without_touching_study(self):
        primary = (run_records('old', root='old') + run_records('goal', root='goal')
                   + run_records('continued', root='goal')[:-1])
        self.add_thread('parent-a', primary)
        luna = run_records('past-luna', 'gpt-6-luna', 'max', 'luna', root='old')
        luna += run_records('related-luna', 'gpt-6-luna', 'max', 'luna', root='goal')
        luna += run_records('correction', 'gpt-6-luna', 'max', 'luna', root='continued')
        self.add_thread('luna', luna, 'parent-a')
        self.add_thread('astra', run_records('review', 'gpt-6.2-astra', 'xhigh', 'astra', root='goal'), 'parent-a')
        self.add_thread('unrelated', run_records('unused', thread='unrelated', root='goal'), 'parent-a')
        before = {path: path.read_bytes() for path in self.home.iterdir()}
        output = io.StringIO()
        with (patch.dict(os.environ, {'CODEX_HOME': str(self.home), 'CODEX_THREAD_ID': 'parent-a'}),
              contextlib.redirect_stdout(output)):
            self.assertEqual(d.main(['--state-root', str(self.root), 'usage', '--worker', '/root/luna',
                                     '--worker', '/root/astra', '--worker', '/root/luna']), 0)
        rows = json.loads(output.getvalue())['usage_by_context']
        self.assertEqual({(r['actor'], r['model'], r['effort']):
                          (r['categories']['total_tokens']['unambiguous_sum'], r['coverage']) for r in rows},
                         {('primary', 'gpt-6.1-sol', 'xhigh'): (28, 'partial'),
                          ('worker', 'gpt-6-luna', 'max'): (28, 'recorded'),
                          ('worker', 'gpt-6.2-astra', 'xhigh'): (14, 'recorded')})
        self.assertEqual({path: path.read_bytes() for path in self.home.iterdir()}, before)
        self.assertFalse(self.root.exists())
        self.assertNotIn('PRIVATE MESSAGE CONTENT', output.getvalue())

    def test_usage_marks_unavailable_or_unrelated_named_workers_and_missing_counts(self):
        self.add_thread('parent-a', run_records('active', root='active')[:-1])
        self.add_thread('unsettled', run_records('worker', 'gpt-6-luna', 'max', 'unsettled', root='active')[:2], 'parent-a')
        self.add_thread('old', run_records('worker', thread='old', root='other'), 'parent-a')
        self.add_thread('foreign', run_records('worker', thread='foreign', root='active'), 'other-parent')
        with patch.dict(os.environ, {'CODEX_HOME': str(self.home), 'CODEX_THREAD_ID': 'parent-a'}):
            result = d.current_usage(['/root/old', '/root/foreign', '/root/unsettled'])
        worker_rows = [row for row in result['usage_by_context'] if row['actor'] == 'worker']
        self.assertEqual([(r['model'], r['coverage'], r['categories']['total_tokens']['unambiguous_sum'])
                          for r in worker_rows], [('gpt-6-luna', 'unavailable', None)])
        self.assertEqual(set(result['source_gaps']['worker']), {
            'named_worker_unavailable', 'worker_turn_scope_incomplete', 'selected_turn_terminal_evidence_missing'})

    def test_usage_refuses_to_guess_the_current_native_root(self):
        for records in (run_records('unlinked')[:-1], run_records('finished', root='finished'),
                        run_records('first', root='first')[:-1] + run_records('second', root='second')[:-1]):
            self.add_thread('parent-a', records)
            with (patch.dict(os.environ, {'CODEX_HOME': str(self.home), 'CODEX_THREAD_ID': 'parent-a'}),
                  self.assertRaisesRegex(ValueError, 'current native (root|turn)')):
                d.current_usage([])

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

    def test_astra_study_start_is_idempotent_private_and_separate_from_sol_ledger(self):
        sol = self.ledger.start()
        sol_bytes = (self.root / 'study.json').read_bytes()
        study = self.astra_study()
        started = study.start()
        snapshot = (study.root / 'study.json').read_bytes()
        repeated = study.start()
        data = study.read()
        self.assertTrue(started['created'])
        self.assertFalse(repeated['created'])
        self.assertEqual(snapshot, (study.root / 'study.json').read_bytes())
        self.assertEqual(data['primary_selection'], {'model': 'gpt-6.2-astra', 'effort': 'xhigh'})
        self.assertEqual(len(data['sequence']), 12)
        for offset in range(0, 12, 4):
            self.assertEqual(data['sequence'][offset:offset + 4].count('A'), 2)
            self.assertEqual(data['sequence'][offset:offset + 4].count('B'), 2)
        self.assertEqual(sol_bytes, (self.root / 'study.json').read_bytes())
        self.assertNotEqual(self.root / 'study.json', study.root / 'study.json')
        self.assertEqual(study.root.stat().st_mode & 0o777, 0o700)
        for path in study.root.iterdir():
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
        self.assertEqual(self.ledger.read()['id'], sol['id'])
        with self.assertRaises(ValueError):
            study.start('gpt-6.3-astra')
        self.assertEqual(snapshot, (study.root / 'study.json').read_bytes())

    def test_astra_assignment_requires_loaded_and_native_model_and_owned_active_thread(self):
        study = self.astra_study()
        study.start()
        self.add_astra_primary('astra-primary')
        path = study.root / 'study.json'
        before = path.read_bytes()
        for selection in (None, {'status': 'unknown'},
                          self.loaded_astra('gpt-6.1-astra'),
                          self.loaded_astra('gpt-6.2-astra', 'high')):
            with self.assertRaises(ValueError):
                study.assign('astra-primary', 'task', 'private check',
                             loaded_selection=selection)
            self.assertEqual(path.read_bytes(), before)
        self.add_astra_primary('wrong-native-model', model='gpt-6.1-sol')
        with self.assertRaises(ValueError):
            study.assign('wrong-native-model', 'task', 'private check',
                         loaded_selection=self.loaded_astra())
        self.add_thread('astra-child', run_records('child-turn', 'gpt-6.2-astra', 'xhigh',
                                                   'astra-child')[:-1], 'astra-primary')
        with self.assertRaises(ValueError):
            study.assign('astra-child', 'task', 'private check',
                         loaded_selection=self.loaded_astra())
        self.assertEqual(path.read_bytes(), before)

    def test_astra_assignment_is_sticky_final_note_is_not_success_and_status_hides_text(self):
        study = self.astra_study()
        study.start()
        self.add_astra_primary('astra-primary')
        assigned = study.assign('astra-primary', 'task', 'private acceptance check',
                                loaded_selection=self.loaded_astra())
        retry = study.assign('astra-primary', 'goal', 'later overridden check',
                             loaded_selection=self.loaded_astra())
        self.assertTrue(assigned['assigned'])
        self.assertFalse(assigned['existing'])
        self.assertTrue(retry['existing'])
        self.assertEqual(retry['arm'], assigned['arm'])
        self.assertEqual(retry['workflow'], 'task')
        note = study.note('astra-primary', 'unresolved: independent evidence is incomplete', final=True)
        self.assertTrue(note['final_note'])
        status = study.status()
        serialized = json.dumps(status)
        self.assertEqual(status['recorded_final_notes'], 1)
        self.assertEqual(status['contexts_without_final_note'], 0)
        self.assertTrue(status['contexts'][0]['final_note_recorded'])
        self.assertEqual(status['contexts'][0]['outcome_readiness'], 'recorded')
        self.assertNotIn('private acceptance check', serialized)
        self.assertNotIn('later overridden check', serialized)
        self.assertNotIn('independent evidence is incomplete', serialized)
        self.assertNotIn('success', serialized.lower())
        final_retry = study.assign('astra-primary', 'task', 'another check',
                                   loaded_selection=None)
        self.assertFalse(final_retry['assigned'])
        self.assertEqual(final_retry['reason'], 'context_finalized')
        self.assertNotIn('arm', final_retry)
        self.assertEqual(len(study.read()['contexts']['astra-primary']['notes']), 1)

    def test_astra_concurrent_assignments_cap_at_twelve_balanced_contexts_with_duplicate_retries(self):
        study = self.astra_study()
        study.start()
        names = [f'astra-primary-{number}' for number in range(13)]
        for number, name in enumerate(names):
            self.add_astra_primary(name, turn=f'astra-turn-{number}')

        def assign(name):
            return name, study.assign(name, 'task', f'private check for {name}',
                                      loaded_selection=self.loaded_astra())

        attempts = ['astra-primary-0', 'astra-primary-0', *names]
        with ThreadPoolExecutor(max_workers=len(attempts)) as pool:
            results = list(pool.map(assign, attempts))
        saved = study.read()
        self.assertEqual(len(saved['contexts']), 12)
        self.assertEqual(sorted(context['index'] for context in saved['contexts'].values()),
                         list(range(1, 13)))
        for offset in range(0, 12, 4):
            block = [saved['sequence'][offset + index] for index in range(4)]
            self.assertEqual(block.count('A'), 2)
            self.assertEqual(block.count('B'), 2)
        by_thread = {}
        for name, result in results:
            if result['assigned']:
                by_thread.setdefault(name, set()).add((result['index'], result['arm']))
        self.assertTrue(any(not result['assigned'] for _, result in results))
        self.assertTrue(all(len(values) == 1 for values in by_thread.values()))
        self.assertEqual(set(by_thread), set(saved['contexts']))

    def test_astra_close_dates_followup_cutoff_and_expired_assignments_are_side_effect_free(self):
        study = self.astra_study()
        start = d.datetime(2030, 1, 1, tzinfo=d.timezone.utc)
        with patch.object(d, 'now', return_value=start):
            study.start()
        current = study.read()
        with patch.object(d, 'now', return_value=start - d.timedelta(seconds=1)):
            self.assertFalse(study.intake_open(current))
            before_start = study.assign('not-started', 'task', 'not retained',
                                        loaded_selection=None)
        self.assertFalse(before_start['assigned'])
        with patch.object(d, 'now', return_value=start):
            self.assertTrue(study.intake_open(current))
        with patch.object(d, 'now', return_value=start + d.timedelta(days=14)):
            self.assertFalse(study.intake_open(current))
        self.add_astra_primary('astra-primary')
        with patch.object(d, 'now', return_value=start + d.timedelta(hours=1)):
            study.assign('astra-primary', 'goal', 'private goal check',
                         loaded_selection=self.loaded_astra())
        self.add_astra_primary('next-primary', turn='next-turn')
        with patch.object(d, 'now', return_value=start + d.timedelta(days=1)):
            closed = study.close()
        intake_until = d.datetime.fromisoformat(closed['intake_until'])
        followup_until = d.datetime.fromisoformat(closed['followup_until'])
        self.assertEqual(intake_until, start + d.timedelta(days=14))
        self.assertEqual(followup_until, start + d.timedelta(days=3))
        self.assertFalse(closed['intake_open'])
        self.assertFalse(closed['followup_complete'])
        state_path = study.root / 'study.json'
        closed_bytes = state_path.read_bytes()
        with patch.object(d, 'now', return_value=start + d.timedelta(days=1)):
            skipped = study.assign('next-primary', 'task', 'not enrolled',
                                   loaded_selection=None)
        self.assertFalse(skipped['assigned'])
        self.assertEqual(skipped['reason'], 'intake_closed')
        self.assertEqual(state_path.read_bytes(), closed_bytes)
        boundary = d.datetime.fromisoformat(closed['followup_until'])
        with patch.object(d, 'now', side_effect=(boundary - d.timedelta(seconds=1), boundary)):
            skipped_note = study.note('astra-primary', 'late final', final=True)
        self.assertFalse(skipped_note['noted'])
        self.assertEqual(skipped_note['reason'], 'followup_closed')
        self.assertEqual(state_path.read_bytes(), closed_bytes)
        with patch.object(d, 'now', return_value=boundary):
            expired = study.assign('astra-primary', 'goal', 'retry after follow-up',
                                   loaded_selection=None)
            ready = study.status()
        self.assertFalse(expired['assigned'])
        self.assertEqual(expired['reason'], 'context_window_expired')
        self.assertNotIn('arm', expired)
        self.assertTrue(ready['followup_complete'])
        self.assertEqual(state_path.read_bytes(), closed_bytes)

    def test_astra_close_without_a_study_does_not_create_private_state(self):
        study = self.astra_study()
        with self.assertRaises(ValueError):
            study.close()
        self.assertFalse(self.root.exists())

    def test_astra_note_bound_reserves_final_slot_and_serialized_size_is_checked(self):
        study = self.astra_study()
        study.start()
        self.add_astra_primary('astra-primary')
        study.assign('astra-primary', 'task', 'private acceptance check',
                     loaded_selection=self.loaded_astra())
        private_control_text = '\x01' * d.ASTRA_STUDY_MAX_TEXT_BYTES
        for _ in range(d.ASTRA_STUDY_MAX_NOTES - 1):
            self.assertTrue(study.note('astra-primary', private_control_text)['noted'])
        state_path = study.root / 'study.json'
        before = state_path.read_bytes()
        with self.assertRaises(ValueError):
            study.note('astra-primary', 'one too many ordinary notes')
        self.assertEqual(state_path.read_bytes(), before)
        self.assertTrue(study.note('astra-primary', private_control_text, final=True)['final_note'])
        self.assertLess(len(state_path.read_bytes()), d.ASTRA_STUDY_MAX_BYTES)
        before = state_path.read_bytes()
        oversized = study.read()
        oversized['untrusted_extra'] = '\x01' * d.ASTRA_STUDY_MAX_BYTES
        with self.assertRaises(ValueError):
            study.save(oversized)
        self.assertEqual(state_path.read_bytes(), before)

    def test_astra_assignment_cli_uses_loaded_primary_and_status_redacts_private_text(self):
        study = self.astra_study()
        output = io.StringIO()
        with (patch.dict(os.environ, {'CODEX_HOME': str(self.home)}),
              contextlib.redirect_stdout(output)):
            self.assertEqual(d.main(['--state-root', str(self.root), 'astra-study', 'start']), 0)
        self.add_astra_primary('cli-primary')
        output = io.StringIO()
        environment = {'CODEX_HOME': str(self.home), 'CODEX_THREAD_ID': 'cli-primary'}
        with (patch.dict(os.environ, environment),
              patch.object(d, 'primary_selection', return_value=self.loaded_astra()),
              contextlib.redirect_stdout(output)):
            self.assertEqual(d.main(['--state-root', str(self.root), 'astra-study', 'assign',
                                     '--workflow', 'goal', '--check', 'private CLI check']), 0)
        self.assertTrue(json.loads(output.getvalue())['assigned'])
        output = io.StringIO()
        with (patch.dict(os.environ, environment), contextlib.redirect_stdout(output)):
            self.assertEqual(d.main(['--state-root', str(self.root), 'astra-study', 'note',
                                     '--text', 'private CLI unresolved result', '--final']), 0)
        output = io.StringIO()
        with (patch.dict(os.environ, environment), contextlib.redirect_stdout(output)):
            self.assertEqual(d.main(['--state-root', str(self.root), 'astra-study', 'status']), 0)
        status_text = output.getvalue()
        status = json.loads(status_text)
        self.assertEqual(status['recorded_final_notes'], 1)
        self.assertNotIn('private CLI check', status_text)
        self.assertNotIn('private CLI unresolved result', status_text)


if __name__ == '__main__':
    unittest.main()
