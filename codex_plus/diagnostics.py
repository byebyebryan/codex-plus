"""Read-only native usage snapshots and opt-in private routing studies."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import fcntl
import json
import os
from pathlib import Path
import secrets
import sqlite3
import stat
import tempfile
import uuid

from . import VERSION
from .context import absolute, primary_selection, resolve
from .diagnostic_source import MAX_THREADS, NativeRecords, identity, start_time, turns
from .worker_models import family_for_model

POLICY = 'adaptive-sol-luna-v1'
VERSION_POLICY = 'record-per-episode'
FROZEN_VERSION_POLICY = 'freeze-first-primary'
LEGACY_VERSION_POLICY = 'legacy-fixed-gpt-6.1-sol'
LEGACY_PRIMARY_SELECTION = {'model': 'gpt-6.1-sol', 'effort': 'xhigh'}
OUTCOMES = ('accepted_first_review', 'minor_correction', 'substantial_repair',
            'primary_takeover', 'unresolved', 'cancelled')

ASTRA_STUDY_POLICY = 'adaptive-astra-primary-v1'
ASTRA_STUDY_MODEL = 'gpt-6.2-astra'
ASTRA_STUDY_EFFORT = 'xhigh'
ASTRA_STUDY_CONTEXT_LIMIT = 12
ASTRA_STUDY_INTAKE_DAYS = 14
ASTRA_STUDY_FOLLOWUP_DAYS = 2
ASTRA_STUDY_MAX_BYTES = 2 * 1024 * 1024
ASTRA_STUDY_MAX_TEXT_BYTES = 512
ASTRA_STUDY_MAX_NOTES = 32
ASTRA_STUDY_ARMS = ('A', 'B')


def _version_policy(study):
    return study.get('version_policy', LEGACY_VERSION_POLICY)


def _study_primary_selection(study):
    if 'version_policy' not in study:
        return dict(LEGACY_PRIMARY_SELECTION)
    selection = study.get('primary_selection')
    return dict(selection) if isinstance(selection, dict) else None


def _sol_primary(model, effort):
    return family_for_model(model) == 'sol' and effort == 'xhigh'


def now():
    return datetime.now(timezone.utc)


def stamp(value):
    return value.isoformat()


def private_file(path, flags):
    fd = os.open(path, flags | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
    info = os.fstat(fd)
    if not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid() or info.st_mode & 0o077:
        os.close(fd)
        raise ValueError('diagnostic files must be owned private regular files')
    return fd


def check_private_directory(path, label='diagnostic directory'):
    info = Path(path).lstat()
    if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid()
            or info.st_mode & 0o077 or Path(path).resolve() != Path(path)):
        raise ValueError(f'{label} must be owned, private and without symlinks')


@contextmanager
def private_directory_write(root, check, read):
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    check()
    fd = private_file(root / '.lock', os.O_RDWR | os.O_CREAT)
    with os.fdopen(fd, 'w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        yield read()


def atomic_private_json(root, filename, value, *, max_bytes=None):
    payload = (json.dumps(value, sort_keys=True, indent=2) + '\n').encode('utf-8')
    if max_bytes is not None and len(payload) > max_bytes:
        raise ValueError('private study exceeds its serialized size bound')
    fd, name = tempfile.mkstemp(prefix='.study-', dir=root)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'wb') as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, root / filename)
        directory_fd = os.open(root, os.O_RDONLY | getattr(os, 'O_DIRECTORY', 0))
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if os.path.exists(name):
            os.unlink(name)


class Ledger:
    def __init__(self, root=None, home=None):
        self.context = resolve()
        self.home = Path(home).resolve() if home else self.context.home
        self.root = absolute(root) if root else self.context.state_root() / 'diagnostics'

    def read(self):
        if not self.root.exists() and not self.root.is_symlink():
            return None
        self.check_root()
        try:
            fd = private_file(self.root / 'study.json', os.O_RDONLY)
        except FileNotFoundError:
            return None
        with os.fdopen(fd) as stream:
            text = stream.read(2 * 1024 * 1024 + 1)
        if len(text) > 2 * 1024 * 1024:
            raise ValueError('diagnostic ledger exceeds size bound')
        study = json.loads(text)
        if (not isinstance(study, dict) or study.get('schema') != 1 or study.get('policy') != POLICY
                or study.get('native_home') != str(self.home)
                or not isinstance(study.get('episodes'), dict)):
            raise ValueError('diagnostic schema, policy or environment mismatch')
        if 'version_policy' in study:
            selection = study.get('primary_selection')
            if (study['version_policy'] not in (VERSION_POLICY, FROZEN_VERSION_POLICY)
                    or ('primary_selection' not in study)
                    or (study['version_policy'] == VERSION_POLICY and selection is not None)
                    or (selection is not None and (
                        not isinstance(selection, dict)
                        or set(selection) != {'model', 'effort'}
                        or not _sol_primary(selection.get('model'), selection.get('effort'))))):
                raise ValueError('diagnostic primary version policy is invalid')
        elif 'primary_selection' in study:
            raise ValueError('diagnostic primary version policy is incomplete')
        return study

    def check_root(self):
        check_private_directory(self.root)

    @contextmanager
    def write(self):
        with private_directory_write(self.root, self.check_root, self.read) as study:
            yield study

    def save(self, study):
        atomic_private_json(self.root, 'study.json', study)

    def start(self):
        with self.write() as previous:
            if previous is not None:
                raise ValueError('a study already exists; preserve it, do not silently extend or replace it')
            started = now()
            study = {'schema': 1, 'id': uuid.uuid4().hex, 'policy': POLICY,
                     'runtime_version': VERSION, 'native_home': str(self.home),
                     'version_policy': VERSION_POLICY, 'primary_selection': None,
                     'started_at': stamp(started), 'enrollment_until': stamp(started + timedelta(days=7)),
                     'observation_until': stamp(started + timedelta(days=7)),
                     'goal_limit': 8, 'closed_at': None, 'episodes': {}}
            self.save(study)
            return study

    def status(self):
        study = self.read()
        if study is None:
            return {'configured': False, 'enrollment_open': False}
        return {'configured': True, 'study': study['id'], 'policy': POLICY,
                'version_policy': _version_policy(study),
                'primary_selection': _study_primary_selection(study),
                'runtime_version': study['runtime_version'], 'goals': len(study['episodes']),
                'goal_limit': study['goal_limit'], 'enrollment_until': study['enrollment_until'],
                'observation_until': study['observation_until'],
                'episodes': [{'episode': key, 'lineage': value['lineage'],
                              'outcome': value['outcome']['result'] if value['outcome'] else None}
                             for key, value in study['episodes'].items()],
                'enrollment_open': self.open(study), 'closed_at': study['closed_at']}

    @staticmethod
    def open(study):
        return (not study['closed_at'] and now() < datetime.fromisoformat(study['enrollment_until'])
                and len(study['episodes']) < study['goal_limit'])

    def allow_model_upgrades(self):
        """Explicitly enable per-episode versions without rewriting past goals."""
        if self.read() is None:
            raise ValueError('an existing study is required')
        changed = False
        with self.write() as study:
            if study is None:
                raise ValueError('study disappeared before policy update')
            if _version_policy(study) != VERSION_POLICY:
                if study['closed_at']:
                    raise ValueError('preserve closed study history')
                changes = study.get('version_policy_changes', [])
                if not isinstance(changes, list):
                    raise ValueError('invalid study policy history')
                backup = 'study.before-model-upgrades-' + uuid.uuid4().hex + '.json'
                with os.fdopen(private_file(self.root / 'study.json', os.O_RDONLY), 'rb') as source:
                    original = source.read(2 * 1024 * 1024 + 1)
                if len(original) > 2 * 1024 * 1024:
                    raise ValueError('diagnostic ledger exceeds size bound')
                with os.fdopen(private_file(self.root / backup, os.O_WRONLY | os.O_CREAT | os.O_EXCL), 'wb') as saved:
                    saved.write(original); saved.flush(); os.fsync(saved.fileno())
                study['version_policy_changes'] = [*changes, {
                    'recorded_at': stamp(now()), 'runtime_version': VERSION,
                    'previous_version_policy': _version_policy(study),
                    'previous_primary_selection': _study_primary_selection(study),
                    'existing_goals': len(study['episodes']),
                    'existing_episodes': sorted(study['episodes']), 'backup': backup,
                }]
                study['version_policy'] = VERSION_POLICY
                study['primary_selection'] = None
                self.save(study)
                changed = True
        return {**self.status(), 'version_policy_updated': changed}

    def enroll(self, thread_id, *, if_open=False, acceptance_ref=None, routing_not_started=False,
               loaded_selection=None):
        # The no-study path is a read-only no-op, including on worker-only installs.
        study = self.read()
        existing = next(((k, e) for k, e in (study or {}).get('episodes', {}).items()
                         if e['thread_id'] == thread_id and not e['outcome']), None)
        if existing:
            return {'enrolled': True, 'episode': existing[0], 'existing': True}
        if study is None or not self.open(study):
            if if_open:
                return {'enrolled': False, 'reason': 'enrollment_closed_or_unconfigured'}
            raise ValueError('start an open study before enrolling')
        identity(thread_id)
        source = NativeRecords(self.home)
        records, gaps, parent = source.read(thread_id)
        available = turns(records)
        if parent or not available:
            raise ValueError('enrollment requires an independent primary with a native turn start')
        turn_id = available[-1]
        if any(r['type'] == 'event_msg' and r['payload'].get('turn_id') == turn_id
               and r['payload'].get('type') in ('task_complete', 'turn_aborted', 'error')
               for r in records):
            raise ValueError('enroll in the active starting turn, never retrospectively')
        contexts = [r['payload'] for r in records if r['type'] == 'turn_context'
                    and r['payload'].get('turn_id') == turn_id]
        selections = {(r.get('model'), r.get('effort')) for r in contexts}
        if len(selections) != 1:
            raise ValueError('enrollment requires one unambiguous native primary selection')
        model, effort = next(iter(selections))
        observed_selection = {'model': model, 'effort': effort}
        if not _sol_primary(model, effort):
            raise ValueError('this A study requires a supported Sol XHigh primary context')
        if loaded_selection is not None:
            if (not isinstance(loaded_selection, dict)
                    or set(loaded_selection) != {'model', 'effort'}
                    or not _sol_primary(loaded_selection.get('model'), loaded_selection.get('effort'))):
                raise ValueError('this A study requires a supported loaded Sol XHigh primary')
            if loaded_selection != observed_selection:
                raise ValueError('loaded and recorded primary selections changed during enrollment')
        expected = _study_primary_selection(study)
        if expected is not None and observed_selection != expected:
            raise ValueError('primary selection differs from the study version cohort')
        with self.write() as study:
            if study is None:
                raise ValueError('study disappeared before admission')
            for key, episode in study['episodes'].items():
                if episode['thread_id'] == thread_id and not episode['outcome']:
                    return {'enrolled': True, 'episode': key, 'existing': True}
                if episode['thread_id'] == thread_id and episode['outcome']['end_turn'] == turn_id:
                    raise ValueError('one native turn cannot be allocated to two episodes')
            if not self.open(study):
                raise ValueError('enrollment closed before admission')
            if _version_policy(study) == FROZEN_VERSION_POLICY:
                frozen = study['primary_selection']
                if frozen is not None and observed_selection != frozen:
                    raise ValueError('primary selection changed before the study cohort was frozen')
                if frozen is None:
                    study['primary_selection'] = dict(observed_selection)
            elif (_version_policy(study) == LEGACY_VERSION_POLICY
                  and observed_selection != LEGACY_PRIMARY_SELECTION):
                raise ValueError('legacy study requires its original Sol XHigh primary selection')
            key = uuid.uuid4().hex
            episode = {
                'thread_id': thread_id, 'lineage': thread_id, 'start_turn': turn_id,
                'native_start_time': start_time(records, turn_id),
                'enrolled_at': stamp(now()), 'runtime_version': VERSION,
                'acceptance_ref': reference(acceptance_ref) or f'native-turn:{thread_id}/{turn_id}',
                'source_gaps': gaps,
                'assignments': [], 'outcome': None,
                'scope': 'entire_start_turn_included',
                'routing_not_started_attested': bool(routing_not_started),
            }
            if _version_policy(study) in (VERSION_POLICY, FROZEN_VERSION_POLICY):
                episode['primary_selection'] = dict(observed_selection)
            study['episodes'][key] = episode
            self.save(study)
        return {'enrolled': True, 'episode': key, 'existing': False}

    def link(self, key, thread_id, turn_id, *, route, contract_ref=None, status='returned',
             first_result='unknown', worker=None):
        if worker is not None:
            if thread_id is not None or turn_id is not None:
                raise ValueError('select either explicit identities or a native worker path')
            episode = episode_for(self.read(), key)
            source = NativeRecords(self.home)
            thread_id = source.worker(episode['thread_id'], worker)
            records, _, _ = source.read(thread_id)
            linked = {a['turn_id'] for a in episode['assignments'] if a['thread_id'] == thread_id}
            candidates = [turn for turn in turns(records) if turn not in linked
                          and start_time(records, turn) is not None
                          and episode['native_start_time'] is not None
                          and start_time(records, turn) >= episode['native_start_time']]
            if len(candidates) != 1:
                raise ValueError('worker turn is missing or ambiguous; use explicit native identities')
            turn_id = candidates[0]
        missing = status in ('controls_missing', 'spawn_rejected')
        if missing:
            if thread_id is not None or turn_id is not None or route == 'primary':
                raise ValueError('a non-started worker assignment has no native worker identity')
            parent = None
        else:
            identity(thread_id); identity(turn_id)
            records, assignment_gaps, parent = NativeRecords(self.home).read(thread_id)
        with self.write() as study:
            episode = episode_for(study, key)
            if episode['outcome']:
                raise ValueError('record assignments before closing the episode')
            root = episode['thread_id']
            if not missing and thread_id != root and parent != root:
                raise ValueError('assignment is not a direct child of this primary')
            if not missing and (route == 'primary') != (thread_id == root):
                raise ValueError('route and thread ownership disagree')
            if not missing:
                started = start_time(records, turn_id)
                if started is None or episode['native_start_time'] is None:
                    assignment_gaps.append('assignment_turn_boundary_unavailable')
                elif started < episode['native_start_time']:
                    raise ValueError('assignment predates this episode')
            assignment = {'thread_id': thread_id, 'turn_id': turn_id, 'route': route,
                          'contract_ref': reference(contract_ref), 'recorded_at': stamp(now()),
                          'status': status, 'first_result': first_result,
                          'source_gaps': [] if missing else assignment_gaps}
            if not missing and any(a['thread_id'] == thread_id and a['turn_id'] == turn_id
                   for a in episode['assignments']):
                raise ValueError('assignment already linked')
            if not missing and any(
                    a['thread_id'] == thread_id and a['turn_id'] == turn_id
                    for other_key, other in study['episodes'].items() if other_key != key
                    for a in other['assignments']):
                raise ValueError('a worker response cannot be allocated to two episodes')
            if len(episode['assignments']) >= MAX_THREADS:
                raise ValueError('assignment bound reached')
            episode['assignments'].append(assignment)
            self.save(study)
        return {'linked': True, 'episode': key, 'thread_id': thread_id, 'turn_id': turn_id}

    def outcome(self, key, result, evidence_ref=None, *, children_reviewed=False,
                user_intervention='unknown'):
        if result not in OUTCOMES:
            raise ValueError('unknown outcome')
        with self.write() as study:
            episode = episode_for(study, key)
            if episode['outcome']:
                raise ValueError('outcome already recorded')
            records, gaps, _ = NativeRecords(self.home).read(episode['thread_id'])
            available = turns(records)
            if not available or episode['start_turn'] not in available:
                raise ValueError('native episode boundaries unavailable; retain unresolved episode')
            episode['outcome'] = {'result': result, 'evidence_ref': reference(evidence_ref),
                                  'recorded_at': stamp(now()), 'end_turn': available[-1],
                                  'children_reviewed_attested': bool(children_reviewed),
                                  'user_intervention': user_intervention,
                                  'after_observation_cutoff': now() > datetime.fromisoformat(study['observation_until'])}
            episode['source_gaps'] = sorted(set(episode['source_gaps'] + gaps))
            self.save(study)
        return {'recorded': True, 'episode': key, 'outcome': result}

    def close(self):
        with self.write() as study:
            if study is None:
                raise ValueError('study unavailable')
            study['closed_at'] = study['closed_at'] or stamp(now())
            self.save(study)
        return self.status()

    def collect(self, key):
        from .diagnostic_records import summarize
        study = self.read()
        episode = episode_for(study, key)
        source = NativeRecords(self.home)
        root = episode['thread_id']
        records, gaps, _ = source.read(root)
        gaps = set(gaps + episode['source_gaps'])
        ordered = turns(records)
        end = episode['outcome']['end_turn'] if episode['outcome'] else (ordered[-1] if ordered else None)
        if episode['start_turn'] not in ordered or end not in ordered:
            gaps.add('primary_turn_boundary_unavailable'); selected = []
        else:
            selected = ordered[ordered.index(episode['start_turn']):ordered.index(end) + 1]
        by_thread, selected_turns = {root: records}, {root: selected}
        for assignment in episode['assignments']:
            gaps.update(assignment['source_gaps'])
            thread = assignment['thread_id']
            if thread is None:
                continue
            if thread == root:
                if assignment['turn_id'] not in selected:
                    gaps.add('primary_assignment_outside_episode')
                continue
            if thread not in by_thread:
                try:
                    child_records, child_gaps, parent = source.read(thread)
                    if parent != root:
                        raise ValueError('ancestry changed')
                    by_thread[thread] = child_records
                    gaps.update(child_gaps)
                except (OSError, ValueError, sqlite3.Error):
                    by_thread[thread] = []; gaps.add('linked_child_records_unavailable')
            selected_turns.setdefault(thread, []).append(assignment['turn_id'])
        # Coverage is an explicit operator assertion, never inferred from titles
        # or from all historical descendants. A partial result stays partial.
        if not episode['outcome'] or not episode['outcome']['children_reviewed_attested']:
            gaps.add('child_assignment_coverage_requires_review')
        if not episode['routing_not_started_attested']:
            gaps.add('prospective_routing_boundary_unverified')
        if VERSION != episode['runtime_version'] or VERSION != study['runtime_version']:
            gaps.add('runtime_version_changed')
        if any(a['route'] not in ('primary', 'luna') for a in episode['assignments']):
            gaps.add('policy_deviation_recorded')
        result = summarize(by_thread, selected_turns, primary_thread_id=root)
        all_turns = [turn for thread in result['threads'] for turn in thread['turns']]
        settled = bool(all_turns) and all(
            any(turn['events'][state] for state in ('completed', 'aborted', 'error'))
            for turn in all_turns)
        if not settled:
            gaps.add('selected_turn_terminal_evidence_missing')
        version_policy = _version_policy(study)
        study_primary_selection = _study_primary_selection(study)
        episode_primary_selection = episode.get('primary_selection') or study_primary_selection
        selection_source = ('episode_enrollment' if episode.get('primary_selection') else
                            'study_enrollment_contract' if study_primary_selection else None)
        if version_policy == FROZEN_VERSION_POLICY:
            if study_primary_selection is None or episode_primary_selection is None:
                gaps.add('primary_selection_unfrozen_or_unknown')
            elif episode_primary_selection != study_primary_selection:
                gaps.add('primary_selection_cohort_mismatch')
        elif version_policy == LEGACY_VERSION_POLICY:
            episode_primary_selection = dict(LEGACY_PRIMARY_SELECTION)
        elif episode_primary_selection is None:
            # Older episode dictionaries remain immutable during policy updates.
            # Recover their starting selection from their own native turn only.
            starting = {(r['payload'].get('model'), r['payload'].get('effort'))
                        for r in records if r['type'] == 'turn_context'
                        and r['payload'].get('turn_id') == episode['start_turn']}
            if len(starting) == 1:
                model, effort = next(iter(starting))
                if _sol_primary(model, effort):
                    episode_primary_selection = {'model': model, 'effort': effort}
                    selection_source = 'native_start_context'
            if episode_primary_selection is None:
                gaps.add('primary_start_selection_unknown')
                for change in study.get('version_policy_changes', []):
                    if not isinstance(change, dict) or key not in change.get('existing_episodes', []):
                        continue
                    previous = change.get('previous_primary_selection')
                    if isinstance(previous, dict) and _sol_primary(previous.get('model'), previous.get('effort')):
                        episode_primary_selection = dict(previous)
                        selection_source = 'prior_enrollment_contract'
                        break
        expected_primary = episode_primary_selection or {}
        luna_threads = {a['thread_id'] for a in episode['assignments']
                        if a['route'] == 'luna' and a['thread_id'] is not None}
        luna_models, primary_models = set(), set()
        for thread in result['threads']:
            if thread['thread_id'] == root:
                for turn in thread['turns']:
                    model, effort = turn.get('model'), turn.get('effort')
                    if isinstance(model, str) and model:
                        primary_models.add(model)
                    supported = (_sol_primary(model, effort) if version_policy == VERSION_POLICY else
                                 (model, effort) == (expected_primary.get('model'), expected_primary.get('effort')))
                    if not supported:
                        gaps.add('primary_selection_changed_or_unknown')
            if thread['thread_id'] in luna_threads:
                for turn in thread['turns']:
                    model, effort = turn.get('model'), turn.get('effort')
                    if isinstance(model, str) and model:
                        luna_models.add(model)
                    if version_policy == LEGACY_VERSION_POLICY:
                        supported = (model, effort) == ('gpt-6-luna', 'max')
                    else:
                        supported = family_for_model(model) == 'luna' and effort == 'max'
                    if not supported:
                        gaps.add('luna_selection_mismatch_or_unknown')
        if len(luna_models) > 1 and version_policy != VERSION_POLICY:
            gaps.add('luna_model_versions_mixed')
        time_evidence = []
        for thread, included in selected_turns.items():
            for turn in sorted(set(included)):
                starts, completions = set(), set()
                for record in by_thread[thread]:
                    payload = record['payload']
                    if record['type'] != 'event_msg' or payload.get('turn_id') != turn:
                        continue
                    if payload.get('type') == 'task_started':
                        value = payload.get('started_at') or record.get('timestamp')
                        if isinstance(value, str): starts.add(value)
                    if payload.get('type') == 'task_complete':
                        value = payload.get('completed_at') or record.get('timestamp')
                        if isinstance(value, str): completions.add(value)
                time_evidence.append({'thread_id': thread, 'turn_id': turn,
                                      'native_start_times': sorted(starts),
                                      'native_completion_times': sorted(completions)})
        return {'schema': 1, 'policy': POLICY, 'episode': key,
                'runtime_version': VERSION, 'study_runtime_version': study['runtime_version'],
                'version_policy': version_policy,
                'study_primary_selection': study_primary_selection,
                'episode_primary_selection': episode_primary_selection,
                'episode_primary_selection_source': selection_source,
                'model_observations': {'primary_models': sorted(primary_models),
                                       'luna_models': sorted(luna_models),
                                       'versions_changed_within_episode': len(primary_models) > 1 or len(luna_models) > 1,
                                       'analysis_groups': 'accounting.usage_by_context'},
                'source_gaps': sorted(gaps), 'measurement_scope': episode['scope'],
                'selected_turns_have_terminal_evidence': settled,
                'acceptance': episode['outcome'], 'assignments': episode['assignments'],
                'accounting': result, 'native_turn_times': time_evidence,
                'claims': {'billing': False, 'causal_comparison': False,
                           'complete_workflow': False}}


class AstraStudy:
    """Private prospective assignments for an explicitly invoked Astra workflow."""

    def __init__(self, root=None, home=None):
        base = Ledger(root, home)
        self.context = base.context
        self.home = base.home
        self.base = base.root
        self.root = self.base / 'astra-study'

    def check_base(self):
        if self.base.exists() or self.base.is_symlink():
            Ledger(self.base, self.home).check_root()

    def check_root(self):
        self.check_base()
        check_private_directory(self.root, 'Astra study directory')

    def read(self):
        if not self.base.exists() and not self.base.is_symlink():
            return None
        self.check_base()
        if not self.root.exists() and not self.root.is_symlink():
            return None
        self.check_root()
        try:
            fd = private_file(self.root / 'study.json', os.O_RDONLY)
        except FileNotFoundError:
            return None
        with os.fdopen(fd) as stream:
            text = stream.read(ASTRA_STUDY_MAX_BYTES + 1)
        if len(text) > ASTRA_STUDY_MAX_BYTES:
            raise ValueError('Astra study exceeds its private size bound')
        study = json.loads(text)
        self.validate(study)
        return study

    def validate(self, study):
        if (not isinstance(study, dict) or study.get('schema') != 1
                or study.get('policy') != ASTRA_STUDY_POLICY
                or study.get('native_home') != str(self.home)
                or not isinstance(study.get('contexts'), dict)):
            raise ValueError('Astra study schema, policy or native home mismatch')
        selection = study.get('primary_selection')
        if (not isinstance(selection, dict) or set(selection) != {'model', 'effort'}
                or family_for_model(selection.get('model')) != 'astra'
                or selection.get('effort') != ASTRA_STUDY_EFFORT):
            raise ValueError('Astra study primary selection is invalid')
        sequence = study.get('sequence')
        if (not isinstance(sequence, list) or len(sequence) != ASTRA_STUDY_CONTEXT_LIMIT
                or any(arm not in ASTRA_STUDY_ARMS for arm in sequence)):
            raise ValueError('Astra study allocation sequence is invalid')
        if (study.get('context_limit') != ASTRA_STUDY_CONTEXT_LIMIT
                or study.get('followup_days') != ASTRA_STUDY_FOLLOWUP_DAYS):
            raise ValueError('Astra study context or follow-up bound is invalid')
        for offset in range(0, ASTRA_STUDY_CONTEXT_LIMIT, 4):
            block = sequence[offset:offset + 4]
            if block.count('A') != 2 or block.count('B') != 2:
                raise ValueError('Astra study allocation block is not balanced')
        started = _study_time(study.get('started_at'))
        intake_until = _study_time(study.get('intake_until'))
        if intake_until != started + timedelta(days=ASTRA_STUDY_INTAKE_DAYS):
            raise ValueError('Astra study intake window is invalid')
        closed_at = study.get('intake_closed_at')
        if closed_at is not None:
            parsed_closed = _study_time(closed_at)
            if parsed_closed < started or parsed_closed > intake_until:
                raise ValueError('Astra study intake closure is invalid')
        contexts = study['contexts']
        if len(contexts) > ASTRA_STUDY_CONTEXT_LIMIT:
            raise ValueError('Astra study context cap is exceeded')
        indices = set()
        for thread_id, context in contexts.items():
            identity(thread_id)
            if not isinstance(context, dict) or context.get('thread_id') != thread_id:
                raise ValueError('Astra study context identity is invalid')
            index = context.get('index')
            if type(index) is not int or not 1 <= index <= ASTRA_STUDY_CONTEXT_LIMIT or index in indices:
                raise ValueError('Astra study context index is invalid')
            indices.add(index)
            if context.get('arm') != sequence[index - 1]:
                raise ValueError('Astra study context arm differs from its allocation')
            if context.get('workflow') not in ('task', 'goal'):
                raise ValueError('Astra study workflow is invalid')
            _study_text(context.get('check'), 'acceptance check')
            assigned_at = _study_time(context.get('assigned_at'))
            if assigned_at < started or assigned_at >= intake_until:
                raise ValueError('Astra study context was assigned outside intake')
            identity(context.get('initiating_turn'))
            notes = context.get('notes')
            if not isinstance(notes, list) or len(notes) > ASTRA_STUDY_MAX_NOTES:
                raise ValueError('Astra study note count exceeds its bound')
            final_notes = 0
            for note in notes:
                if not isinstance(note, dict) or type(note.get('final')) is not bool:
                    raise ValueError('Astra study note metadata is invalid')
                _study_time(note.get('recorded_at'))
                _study_text(note.get('text'), 'private note')
                final_notes += note['final']
            if final_notes > 1:
                raise ValueError('Astra study context has multiple final notes')
        if len(contexts) == ASTRA_STUDY_CONTEXT_LIMIT and closed_at is None:
            raise ValueError('Astra study at its context cap must have closed intake')
        return study

    @contextmanager
    def write(self):
        self.base.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.check_base()
        with private_directory_write(self.root, self.check_root, self.read) as study:
            yield study

    def save(self, study):
        self.validate(study)
        atomic_private_json(self.root, 'study.json', study,
                            max_bytes=ASTRA_STUDY_MAX_BYTES)

    @staticmethod
    def allocation_sequence():
        sequence = []
        for _ in range(ASTRA_STUDY_CONTEXT_LIMIT // 4):
            block = ['A', 'A', 'B', 'B']
            secrets.SystemRandom().shuffle(block)
            sequence.extend(block)
        return sequence

    def start(self, model=ASTRA_STUDY_MODEL, effort=ASTRA_STUDY_EFFORT):
        if family_for_model(model) != 'astra' or effort != ASTRA_STUDY_EFFORT:
            raise ValueError('Astra studies require a supported Astra XHigh selection')
        with self.write() as previous:
            if previous is not None:
                if previous['primary_selection'] != {'model': model, 'effort': effort}:
                    raise ValueError('an Astra study already exists with a different pinned selection')
                return {**self.status(), 'created': False}
            started = now()
            study = {
                'schema': 1, 'id': uuid.uuid4().hex, 'policy': ASTRA_STUDY_POLICY,
                'runtime_version': VERSION, 'native_home': str(self.home),
                'primary_selection': {'model': model, 'effort': effort},
                'started_at': stamp(started),
                'intake_until': stamp(started + timedelta(days=ASTRA_STUDY_INTAKE_DAYS)),
                'intake_closed_at': None,
                'context_limit': ASTRA_STUDY_CONTEXT_LIMIT,
                'followup_days': ASTRA_STUDY_FOLLOWUP_DAYS,
                'sequence': self.allocation_sequence(), 'contexts': {},
            }
            self.save(study)
        return {**self.status(), 'created': True}

    @staticmethod
    def effective_intake_close(study):
        if study['intake_closed_at'] is not None:
            return _study_time(study['intake_closed_at'])
        return _study_time(study['intake_until'])

    @classmethod
    def intake_open(cls, study, at=None):
        at = at or now()
        return (study['intake_closed_at'] is None
                and len(study['contexts']) < ASTRA_STUDY_CONTEXT_LIMIT
                and _study_time(study['started_at']) <= at < _study_time(study['intake_until']))

    @classmethod
    def followup_complete(cls, study, at=None):
        at = at or now()
        intake_open = cls.intake_open(study, at)
        if intake_open:
            return False
        return at >= cls.effective_intake_close(study) + timedelta(days=ASTRA_STUDY_FOLLOWUP_DAYS)

    def status(self):
        study = self.read()
        if study is None:
            return {'configured': False, 'intake_open': False, 'assigned_contexts': 0,
                    'followup_complete': False, 'recorded_final_notes': 0,
                    'contexts_without_final_note': 0, 'contexts': []}
        at = now()
        followup_complete = self.followup_complete(study, at)
        intake_open = self.intake_open(study, at)
        contexts = []
        for context in sorted(study['contexts'].values(), key=lambda item: item['index']):
            final_recorded = any(note['final'] for note in context['notes'])
            readiness = ('recorded' if final_recorded else
                         'needs_final_note' if followup_complete else
                         'in_progress' if intake_open else 'follow_up')
            contexts.append({'index': context['index'], 'arm': context['arm'],
                             'workflow': context['workflow'], 'assigned_at': context['assigned_at'],
                             'note_count': len(context['notes']),
                             'final_note_recorded': final_recorded,
                             'outcome_readiness': readiness})
        final_notes = sum(context['final_note_recorded'] for context in contexts)
        return {'configured': True, 'study': study['id'], 'policy': ASTRA_STUDY_POLICY,
                'primary_selection': dict(study['primary_selection']),
                'started_at': study['started_at'], 'intake_until': study['intake_until'],
                'followup_until': stamp(self.effective_intake_close(study)
                                        + timedelta(days=ASTRA_STUDY_FOLLOWUP_DAYS)),
                'intake_open': intake_open,
                'assigned_contexts': len(contexts), 'context_limit': ASTRA_STUDY_CONTEXT_LIMIT,
                'arm_counts': {arm: sum(context['arm'] == arm for context in contexts)
                               for arm in ASTRA_STUDY_ARMS},
                'followup_complete': followup_complete,
                'recorded_final_notes': final_notes,
                'contexts_without_final_note': len(contexts) - final_notes,
                'contexts': contexts}

    def needs_primary_verification(self, thread_id):
        study = self.read()
        if study is None:
            return False
        context = study['contexts'].get(thread_id)
        if context is not None:
            if any(note['final'] for note in context['notes']):
                return False
            if now() >= self.effective_intake_close(study) + timedelta(days=ASTRA_STUDY_FOLLOWUP_DAYS):
                return False
            return True
        return self.intake_open(study)

    def verify_initiating_context(self, thread_id, loaded_selection, study):
        identity(thread_id)
        if (not isinstance(loaded_selection, dict) or loaded_selection.get('status') != 'known'
                or loaded_selection.get('model') != study['primary_selection']['model']
                or loaded_selection.get('reasoning_effort', loaded_selection.get('effort'))
                != study['primary_selection']['effort']):
            raise ValueError('loaded initiating Astra model and effort must match the study pin')
        records, _, parent = NativeRecords(self.home).read(thread_id)
        if parent is not None:
            raise ValueError('Astra study assignments require the owned native primary thread')
        started = turns(records)
        terminal = {record['payload'].get('turn_id') for record in records
                    if record['type'] == 'event_msg'
                    and record['payload'].get('type') in ('task_complete', 'turn_aborted',
                                                         'error', 'turn_error')}
        active = [turn for turn in started if turn not in terminal]
        if len(active) != 1 or not started or active[0] != started[-1]:
            raise ValueError('Astra assignment requires the current active native primary turn')
        selections = {(record['payload'].get('model'), record['payload'].get('effort'))
                      for record in records if record['type'] == 'turn_context'
                      and record['payload'].get('turn_id') == active[0]}
        if selections != {(study['primary_selection']['model'], study['primary_selection']['effort'])}:
            raise ValueError('native initiating turn model and effort must match the study pin')
        return active[0]

    def assign(self, thread_id, workflow, check, *, loaded_selection=None):
        study = self.read()
        if study is None:
            return {'assigned': False, 'reason': 'study_unconfigured'}
        if not isinstance(thread_id, str) or not thread_id:
            if self.intake_open(study):
                raise ValueError('assign only the invoking native primary thread')
            return {'assigned': False, 'reason': 'intake_closed'}
        identity(thread_id)
        existing = study['contexts'].get(thread_id)
        if existing is None and not self.intake_open(study):
            return {'assigned': False, 'reason': 'intake_closed'}
        if existing is not None:
            if any(note['final'] for note in existing['notes']):
                return {'assigned': False, 'reason': 'context_finalized',
                        'index': existing['index'], 'existing': True}
            if now() >= self.effective_intake_close(study) + timedelta(days=ASTRA_STUDY_FOLLOWUP_DAYS):
                return {'assigned': False, 'reason': 'context_window_expired',
                        'index': existing['index'], 'existing': True}
        if existing is None:
            if workflow not in ('task', 'goal'):
                raise ValueError('workflow must be task or goal')
            _study_text(check, 'acceptance check')
        initiating_turn = self.verify_initiating_context(thread_id, loaded_selection, study)
        with self.write() as current:
            if current is None:
                raise ValueError('Astra study disappeared before assignment')
            existing = current['contexts'].get(thread_id)
            if existing is not None:
                if any(note['final'] for note in existing['notes']):
                    return {'assigned': False, 'reason': 'context_finalized',
                            'index': existing['index'], 'existing': True}
                if now() >= self.effective_intake_close(current) + timedelta(days=ASTRA_STUDY_FOLLOWUP_DAYS):
                    return {'assigned': False, 'reason': 'context_window_expired',
                            'index': existing['index'], 'existing': True}
                return self.assignment_result(existing, existing=True)
            if not self.intake_open(current):
                return {'assigned': False, 'reason': 'intake_closed'}
            index = len(current['contexts']) + 1
            arm = current['sequence'][index - 1]
            assigned_at = now()
            context = {'thread_id': thread_id, 'index': index, 'arm': arm,
                       'workflow': workflow, 'check': check,
                       'initiating_turn': initiating_turn, 'assigned_at': stamp(assigned_at),
                       'notes': []}
            current['contexts'][thread_id] = context
            if index == ASTRA_STUDY_CONTEXT_LIMIT:
                current['intake_closed_at'] = stamp(assigned_at)
            self.save(current)
        return self.assignment_result(context, existing=False)

    @staticmethod
    def assignment_result(context, *, existing):
        return {'assigned': True, 'index': context['index'], 'arm': context['arm'],
                'workflow': context['workflow'], 'existing': existing}

    def note(self, thread_id, text, *, final=False):
        _study_text(text, 'private note')
        if type(final) is not bool:
            raise ValueError('final note marker must be boolean')
        study = self.read()
        if study is None or not isinstance(thread_id, str) or not thread_id:
            raise ValueError('a current enrolled Astra context is required')
        identity(thread_id)
        context = study['contexts'].get(thread_id)
        if context is None:
            raise ValueError('notes can be added only to the current enrolled thread')
        _, _, parent = NativeRecords(self.home).read(thread_id)
        if parent is not None:
            raise ValueError('notes require the enrolled native primary thread')
        if now() >= self.effective_intake_close(study) + timedelta(days=ASTRA_STUDY_FOLLOWUP_DAYS):
            return {'noted': False, 'reason': 'followup_closed'}
        with self.write() as current:
            if current is None or thread_id not in current['contexts']:
                raise ValueError('enrolled Astra context is unavailable')
            if now() >= self.effective_intake_close(current) + timedelta(days=ASTRA_STUDY_FOLLOWUP_DAYS):
                return {'noted': False, 'reason': 'followup_closed'}
            context = current['contexts'][thread_id]
            has_final = any(note['final'] for note in context['notes'])
            note_limit = ASTRA_STUDY_MAX_NOTES if final or has_final else ASTRA_STUDY_MAX_NOTES - 1
            if len(context['notes']) >= note_limit:
                raise ValueError('Astra context note limit reached')
            if final and has_final:
                raise ValueError('a final outcome note is already recorded')
            note = {'recorded_at': stamp(now()), 'text': text, 'final': final}
            context['notes'].append(note)
            self.save(current)
            number = len(context['notes'])
        return {'noted': True, 'index': context['index'], 'note': number,
                'final_note': final}

    def close(self):
        if self.read() is None:
            raise ValueError('Astra study unavailable')
        with self.write() as study:
            if study is None:
                raise ValueError('Astra study unavailable')
            if study['intake_closed_at'] is None:
                closed = min(now(), _study_time(study['intake_until']))
                study['intake_closed_at'] = stamp(closed)
                self.save(study)
        return self.status()


def _study_time(value):
    if not isinstance(value, str):
        raise ValueError('Astra study timestamp is invalid')
    parsed = datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        raise ValueError('Astra study timestamps must include a timezone')
    return parsed


def _study_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{label} must be nonempty text')
    try:
        size = len(value.encode('utf-8'))
    except UnicodeEncodeError as error:
        raise ValueError(f'{label} is invalid text') from error
    if size > ASTRA_STUDY_MAX_TEXT_BYTES:
        raise ValueError(f'{label} exceeds its private size bound')
    return value


def reference(value):
    if value is not None and (not isinstance(value, str) or not value.strip() or len(value) > 512):
        raise ValueError('use a short private artifact or message reference')
    return value


def episode_for(study, key):
    if study is None or key not in study['episodes']:
        raise ValueError('unknown private episode')
    return study['episodes'][key]


def _turn_roots(records):
    roots = {}
    for record in records:
        payload = record['payload']
        if record['type'] == 'event_msg' and payload.get('type') == 'task_started':
            turn = payload.get('turn_id')
            root = payload.get('root_turn_id')
            if isinstance(turn, str) and turn:
                roots.setdefault(turn, set()).add(root if isinstance(root, str) and root else None)
    return roots


def current_usage(worker_paths):
    """Measure the live native root and explicitly named direct workers."""
    from .diagnostic_records import summarize

    paths = dict.fromkeys(worker_paths)
    if len(paths) >= MAX_THREADS:
        raise ValueError('too many worker references')
    primary = identity(os.environ.get('CODEX_THREAD_ID'))
    source = NativeRecords(resolve().home)
    records, reader_gaps, parent = source.read(primary)
    if parent is not None:
        raise ValueError('usage requires the invoking native primary')
    roots = _turn_roots(records)
    terminal = {record['payload'].get('turn_id') for record in records
                if record['type'] == 'event_msg'
                and record['payload'].get('type') in ('task_complete', 'turn_aborted')
                and isinstance(record['payload'].get('turn_id'), str)}
    live_turns = roots.keys() - terminal
    if len(live_turns) != 1:
        raise ValueError('current native turn is unavailable or ambiguous')
    current = roots[next(iter(live_turns))]
    if len(current) != 1 or None in current:
        raise ValueError('current native root is unavailable or ambiguous')
    root = next(iter(current))
    primary_turns = {turn for turn, observed in roots.items() if observed == current}
    gaps = {'primary': set(reader_gaps) | {'current_turn_in_progress'}, 'worker': set()}
    if roots.get(root) != current or any(root in observed and observed != current for observed in roots.values()):
        gaps['primary'].add('primary_root_history_incomplete')
    records_by_thread = {primary: records}
    selected = {primary: primary_turns}
    related = primary_turns | current
    for path in paths:
        try:
            thread = source.worker(primary, path)
            child_records, child_gaps, owner = source.read(thread)
            if owner != primary or thread == primary:
                raise ValueError('worker ancestry does not match the primary')
        except (OSError, ValueError, sqlite3.Error):
            gaps['worker'].add('named_worker_unavailable')
            continue
        child_roots = _turn_roots(child_records)
        child_turns = {turn for turn, observed in child_roots.items()
                       if len(observed) == 1 and observed <= related}
        gaps['worker'].update(child_gaps)
        if not child_turns or any(len(observed) != 1 or None in observed for observed in child_roots.values()):
            gaps['worker'].add('worker_turn_scope_incomplete')
        if child_turns:
            records_by_thread[thread] = child_records
            selected[thread] = child_turns

    accounting = summarize(records_by_thread, selected, primary_thread_id=primary)
    for thread in accounting['threads']:
        if thread['coverage'].get('unjoined_usage_record_count'):
            gaps[thread['actor']].add('unjoined_usage_records')
        if thread['actor'] == 'worker' and any(
                not (turn['events']['completed'] or turn['events']['aborted']) for turn in thread['turns']):
            gaps['worker'].add('selected_turn_terminal_evidence_missing')
    rows = accounting['usage_by_context']
    for row in rows:
        if row['context_status'] != 'known':
            gaps[row['actor']].add('model_or_effort_unattributed')
    for row in rows:
        total = row['categories']['total_tokens']
        row['coverage'] = ('unavailable' if total['unambiguous_sum'] is None else
                           'partial' if gaps[row['actor']] or not total['complete'] else 'recorded')
    return {'scope': 'current_native_root_and_named_workers', 'usage_by_context': rows,
            'source_gaps': {actor: sorted(codes) for actor, codes in gaps.items()}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-root', type=Path, help='Private diagnostics directory; not a native home')
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('start', 'status', 'close'):
        sub.add_parser(name)
    sub.add_parser('allow-model-upgrades', help='Record versions per episode in an existing study; preserve history and bounds')
    enroll = sub.add_parser('enroll')
    enroll.add_argument('--thread', default=os.environ.get('CODEX_THREAD_ID'))
    enroll.add_argument('--if-open', action='store_true')
    enroll.add_argument('--acceptance-ref')
    enroll.add_argument('--routing-not-started', action='store_true',
                        help='Attest enrollment precedes routing; does not prove it from native data')
    link = sub.add_parser('link')
    link.add_argument('episode'); link.add_argument('--thread')
    link.add_argument('--turn')
    link.add_argument('--worker', help='Exact native task path; resolves only one unlinked turn in this episode')
    link.add_argument('--route', choices=('primary', 'luna', 'other'), required=True,
                      help='Observed route only; other preserves a policy deviation and grants no delegation permission')
    link.add_argument('--contract-ref')
    link.add_argument('--status', choices=('returned', 'execution_failed', 'controls_missing',
                                         'spawn_rejected', 'cancelled', 'unresolved'), default='returned')
    link.add_argument('--first-result', choices=('accepted', 'correction', 'rejected', 'unknown'),
                      default='unknown')
    outcome = sub.add_parser('outcome')
    outcome.add_argument('episode'); outcome.add_argument('result', choices=OUTCOMES)
    outcome.add_argument('--evidence-ref')
    outcome.add_argument('--children-reviewed', action='store_true')
    outcome.add_argument('--user-intervention', choices=('none', 'clarification', 'correction',
                                                       'rescue', 'unknown'), default='unknown')
    collect = sub.add_parser('collect'); collect.add_argument('episode')
    usage = sub.add_parser('usage', help='Summarize native usage for the current run without a study')
    usage.add_argument('--worker', action='append', default=[], metavar='PATH',
                       help='Exact native collaboration task path (repeat for workers in this run)')
    astra = sub.add_parser('astra-study', help='Private prospective assignments for explicit adaptive Astra workflows')
    astra_commands = astra.add_subparsers(dest='astra_command', required=True)
    astra_start = astra_commands.add_parser('start', help='Start or inspect the pinned 12-context, 14-day study')
    astra_start.add_argument('--model', default=ASTRA_STUDY_MODEL,
                             help='Exact supported Astra model ID (default: gpt-6.2-astra)')
    astra_start.add_argument('--effort', choices=(ASTRA_STUDY_EFFORT,), default=ASTRA_STUDY_EFFORT,
                             help='Pinned Astra reasoning effort (xhigh)')
    astra_commands.add_parser('status', help='Read assigned arms and final-note counts, not success counts or private text')
    astra_assign = astra_commands.add_parser(
        'assign', help='Call only from an explicitly invoked adaptive skill before routing ordinary work')
    astra_assign.add_argument('--workflow', choices=('task', 'goal'), required=True)
    astra_assign.add_argument('--check', required=True, help='Private acceptance check for this context')
    astra_note = astra_commands.add_parser('note', help='Append a bounded private note to the current enrolled thread')
    astra_note.add_argument('--text', required=True, help='Private outcome, usage evidence, or reference note')
    astra_note.add_argument('--final', action='store_true',
                            help='Record the final outcome, including unresolved; this does not imply success')
    astra_commands.add_parser('close', help='Close new assignments and start the two-day follow-up window')
    args = parser.parse_args(argv)
    try:
        if args.command == 'usage':
            print(json.dumps(current_usage(args.worker), sort_keys=True))
            return 0
        if args.command == 'astra-study':
            study = AstraStudy(args.state_root)
            if args.astra_command == 'start':
                result = study.start(args.model, args.effort)
            elif args.astra_command == 'status':
                result = study.status()
            elif args.astra_command == 'close':
                result = study.close()
            elif args.astra_command == 'assign':
                thread_id = os.environ.get('CODEX_THREAD_ID')
                selection = primary_selection() if study.needs_primary_verification(thread_id) else None
                result = study.assign(thread_id, args.workflow, args.check,
                                      loaded_selection=selection)
            elif args.astra_command == 'note':
                result = study.note(os.environ.get('CODEX_THREAD_ID'), args.text,
                                    final=args.final)
            else:
                raise ValueError('unknown Astra study operation')
            print(json.dumps(result, sort_keys=True))
            return 0
        ledger = Ledger(args.state_root)
        if args.command == 'allow-model-upgrades':
            result = ledger.allow_model_upgrades()
        elif args.command == 'enroll':
            loaded_selection = None
            if ledger.status()['enrollment_open']:
                if not args.thread or args.thread != os.environ.get('CODEX_THREAD_ID'):
                    raise ValueError('enroll only the invoking native primary')
                selection = primary_selection()
                if (selection.get('status') != 'known'
                        or not _sol_primary(selection.get('model'), selection.get('reasoning_effort'))):
                    raise ValueError('loaded initiating supported Sol XHigh primary unavailable')
                loaded_selection = {'model': selection['model'], 'effort': selection['reasoning_effort']}
            result = ledger.enroll(args.thread, if_open=args.if_open, acceptance_ref=args.acceptance_ref,
                                   routing_not_started=args.routing_not_started,
                                   loaded_selection=loaded_selection)
        elif args.command == 'link':
            result = ledger.link(args.episode, args.thread, args.turn, route=args.route,
                                 contract_ref=args.contract_ref, status=args.status,
                                 first_result=args.first_result, worker=args.worker)
        elif args.command == 'outcome':
            result = ledger.outcome(args.episode, args.result, args.evidence_ref,
                                    children_reviewed=args.children_reviewed,
                                    user_intervention=args.user_intervention)
        elif args.command == 'collect':
            result = ledger.collect(args.episode)
        else:
            result = getattr(ledger, args.command)()
        print(json.dumps(result, sort_keys=True))
        return 0
    except (OSError, ValueError, sqlite3.Error, KeyError, TypeError):
        # Error text can contain private paths or SQLite data. Keep it local.
        print(json.dumps({'error': 'diagnostics unavailable or request invalid; native state was not changed'}))
        return 1
