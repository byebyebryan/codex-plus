"""Opt-in private A-policy bookkeeping and read-only native usage collection."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import fcntl
import json
import os
from pathlib import Path
import sqlite3
import stat
import tempfile
import uuid

from . import VERSION
from .context import absolute, primary_selection, resolve
from .diagnostic_source import MAX_THREADS, NativeRecords, identity, start_time, turns
from .worker_models import family_for_model

POLICY = 'adaptive-sol-luna-v1'
VERSION_POLICY = 'freeze-first-primary'
LEGACY_VERSION_POLICY = 'legacy-fixed-gpt-6.1-sol'
LEGACY_PRIMARY_SELECTION = {'model': 'gpt-6.1-sol', 'effort': 'xhigh'}
OUTCOMES = ('accepted_first_review', 'minor_correction', 'substantial_repair',
            'primary_takeover', 'unresolved', 'cancelled')


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
            if (study['version_policy'] != VERSION_POLICY
                    or ('primary_selection' not in study)
                    or (selection is not None and (
                        not isinstance(selection, dict)
                        or set(selection) != {'model', 'effort'}
                        or not _sol_primary(selection.get('model'), selection.get('effort'))))):
                raise ValueError('diagnostic primary version policy is invalid')
        elif 'primary_selection' in study:
            raise ValueError('diagnostic primary version policy is incomplete')
        return study

    def check_root(self):
        info = self.root.lstat()
        if (not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid()
                or info.st_mode & 0o077 or self.root.resolve() != self.root):
            raise ValueError('diagnostic directory must be owned, private and without symlinks')

    @contextmanager
    def write(self):
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.check_root()
        fd = private_file(self.root / '.lock', os.O_RDWR | os.O_CREAT)
        with os.fdopen(fd, 'w') as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            study = self.read()
            yield study

    def save(self, study):
        fd, name = tempfile.mkstemp(prefix='.study-', dir=self.root)
        try:
            with os.fdopen(fd, 'w') as stream:
                json.dump(study, stream, sort_keys=True, indent=2)
                stream.write('\n'); stream.flush(); os.fsync(stream.fileno())
            os.replace(name, self.root / 'study.json')
        finally:
            if os.path.exists(name):
                os.unlink(name)

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
        expected = (_study_primary_selection(study) if _version_policy(study) == VERSION_POLICY
                    else dict(LEGACY_PRIMARY_SELECTION))
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
            if _version_policy(study) == VERSION_POLICY:
                frozen = study['primary_selection']
                if frozen is not None and observed_selection != frozen:
                    raise ValueError('primary selection changed before the study cohort was frozen')
                if frozen is None:
                    study['primary_selection'] = dict(observed_selection)
            elif observed_selection != LEGACY_PRIMARY_SELECTION:
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
            if _version_policy(study) == VERSION_POLICY:
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
        if version_policy == VERSION_POLICY:
            if study_primary_selection is None or episode_primary_selection is None:
                gaps.add('primary_selection_unfrozen_or_unknown')
            elif episode_primary_selection != study_primary_selection:
                gaps.add('primary_selection_cohort_mismatch')
        else:
            episode_primary_selection = dict(LEGACY_PRIMARY_SELECTION)
        expected_primary = episode_primary_selection or {}
        luna_threads = {a['thread_id'] for a in episode['assignments']
                        if a['route'] == 'luna' and a['thread_id'] is not None}
        luna_models = set()
        for thread in result['threads']:
            if thread['thread_id'] == root and any(
                    (turn.get('model'), turn.get('effort')) !=
                    (expected_primary.get('model'), expected_primary.get('effort'))
                    for turn in thread['turns']):
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
        if len(luna_models) > 1:
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
                'source_gaps': sorted(gaps), 'measurement_scope': episode['scope'],
                'selected_turns_have_terminal_evidence': settled,
                'acceptance': episode['outcome'], 'assignments': episode['assignments'],
                'accounting': result, 'native_turn_times': time_evidence,
                'claims': {'billing': False, 'causal_comparison': False,
                           'complete_workflow': False}}


def reference(value):
    if value is not None and (not isinstance(value, str) or not value.strip() or len(value) > 512):
        raise ValueError('use a short private artifact or message reference')
    return value


def episode_for(study, key):
    if study is None or key not in study['episodes']:
        raise ValueError('unknown private episode')
    return study['episodes'][key]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-root', type=Path, help='Private diagnostics directory; not a native home')
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('start', 'status', 'close'):
        sub.add_parser(name)
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
    args = parser.parse_args(argv)
    try:
        ledger = Ledger(args.state_root)
        if args.command == 'enroll':
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
