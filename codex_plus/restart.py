"""Plan bounded observation continuity; never replay old events or messages."""

from __future__ import annotations

import json
import math
import time
import uuid

from .peers import PeerReader
from .store import Store, validate_spec


MAX_REGISTRATIONS = 1000


def plan(connection, old, current, client, *, now, preview, monotonic=None, boot=None):
    """Read a frozen journal. Unknown effects stay in its immutable archive."""
    from .owner_recovery import _confirmed_withdrawal, kernel_boot_id
    monotonic_now = time.monotonic() if monotonic is None else monotonic
    deadline = time.monotonic() + 5
    boot = kernel_boot_id() if boot is None else boot
    jobs = [dict(row) for row in connection.execute('SELECT * FROM jobs ORDER BY id LIMIT ?', (MAX_REGISTRATIONS + 1,))]
    if len(jobs) > MAX_REGISTRATIONS:
        raise ValueError('restart registration scan exceeds its bound')
    by_id = {row['id']: row for row in jobs}
    pending_renewal = {row[0] for row in connection.execute("SELECT parent_id FROM renewals WHERE state='pending'")}
    rows, continuations, peers = [], [], {}
    for job in jobs:
        if job['intent'] != 'active':
            continue
        reason = None
        spec = json.loads(job['spec'])
        expires = job['expires']
        if not isinstance(expires, (float, int)) or not math.isfinite(expires):
            raise ValueError('registration expiry is invalid')
        if expires <= now:
            reason = 'lease_expired'
        elif (job.get('lease_boot') != boot or
              type(job.get('lease_deadline')) not in (float, int) or
              not math.isfinite(job['lease_deadline']) or
              job['kind'] == 'wake' and (type(job.get('wake_deadline')) not in (float, int) or
                                        not math.isfinite(job['wake_deadline']))):
            reason = 'original_monotonic_lease_unavailable'
        elif job['lease_deadline'] <= monotonic_now:
            reason = 'original_monotonic_lease_expired'
        elif job['root_id'] not in by_id or by_id[job['root_id']]['intent'] == 'cancelled':
            reason = 'lineage_unavailable_or_cancelled'
        elif job['id'] in pending_renewal:
            reason = 'renewal_unresolved'
        elif job['kind'] not in ('watch', 'wake'):
            reason = 'messages_are_never_replayed'
        events = [dict(row) for row in connection.execute('SELECT * FROM events WHERE job_id=?', (job['id'],))]
        # Even an acknowledged old callback may still be executing. Do not
        # manufacture a successor inspection while its final outcome is unknown.
        if not reason and any(
                event['delivery'] in ('pending', 'dispatching', 'uncertain') or
                event['delivery'] == 'native_queued' and
                not _confirmed_withdrawal(event) and
                (not event['acknowledged'] or event['turn_outcome'] is None)
                for event in events):
            reason = 'old_event_outcome_unresolved'
        if not reason and job['kind'] == 'wake' and events:
            reason = 'reminder_already_emitted'
        if not reason and job['kind'] == 'watch':
            if job['source_state'] not in ('pending', 'starting', 'running', 'lost'):
                reason = 'source_already_ended_or_stopping'
            elif job['event_count'] >= spec['event_limit']:
                reason = 'event_allowance_exhausted'
            elif spec.get('restart', 'resume' if spec.get('peer') else 'manual') != 'resume':
                reason = 'source_requires_explicit_recovery'
            elif spec.get('peer'):
                peer = spec['peer']
                if {key: value for key, value in peer.items() if key != 'thread_id'} != {
                        key: value for key, value in old.items() if key != 'thread_id'}:
                    reason = 'peer_original_owner_mismatch'
                else:
                    try:
                        target = peer['thread_id']
                        if target not in peers:
                            if len(peers) >= 20:
                                raise ValueError('restart peer scan exceeds its bound')
                            remaining = deadline - time.monotonic()
                            if remaining <= 0:
                                raise TimeoutError('restart peer scan deadline exceeded')
                            frozen = client.bind(target, timeout=min(2, remaining))
                            remaining = deadline - time.monotonic()
                            if remaining <= 0:
                                raise TimeoutError('restart peer scan deadline exceeded')
                            PeerReader(client).validate(frozen, timeout=min(2, remaining))
                            if {key: value for key, value in frozen.items() if key != 'thread_id'} != {
                                    key: value for key, value in current.items() if key != 'thread_id'}:
                                raise ValueError('peer successor owner differs')
                            peers[target] = frozen
                        spec['peer'] = peers[target]
                    except (OSError, ValueError, KeyError, RuntimeError, TimeoutError):
                        reason = 'peer_not_positively_available_in_successor'
        if not reason:
            try:
                spec = validate_spec(job['kind'], spec)
            except (OSError, ValueError, KeyError, TypeError):
                reason = 'source_spec_no_longer_valid'
        new_id = str(uuid.uuid5(uuid.NAMESPACE_URL, preview + '/' + job['id'])) if not reason else None
        rows.append({'previous_id': job['id'], 'new_id': new_id,
                     'kind': job['kind'], 'expires': expires,
                     'state': 'continue' if new_id else 'quarantined', 'reason': reason})
        if new_id:
            continuations.append({**job, 'id': new_id, 'spec': spec})
    # bind() may have inspected a peer; restore the exact caller selection.
    if client.bind(current['thread_id'], timeout=max(0.001, min(2, deadline - time.monotonic()))) != current:
        raise ValueError('native owner changed while planning restart')
    return {'registrations': rows, 'continuations': continuations}


def seed(state, prepared):
    """Populate an unselected epoch once. No source start, native call or event copy."""
    store = Store(state)
    try:
        with store.transaction():
            for job in prepared['continuations']:
                if store.db.execute('SELECT 1 FROM jobs WHERE id=?', (job['id'],)).fetchone():
                    raise ValueError('restart state already contains an unexpected registration')
                store.create(job['kind'], job['spec'], job_id=job['id'])
                store.db.execute('''UPDATE jobs SET created=?,expires=?,due=?,event_count=?,
                    notice_count=?,baseline=?,control_reason=?,source_detail=?,
                    lease_boot=?,lease_deadline=?,wake_deadline=? WHERE id=?''',
                    (job['created'], job['expires'], job['due'], job['event_count'],
                     job['notice_count'], job['baseline'],
                     'daemon_restart_observation_gap; historical events were not replayed',
                     'verified successor; observation gap after daemon restart',
                     job['lease_boot'], job['lease_deadline'], job['wake_deadline'], job['id']))
    finally:
        store.close()


def verify(state, prepared, highwater):
    """Reject a modified or conflicting unselected continuation journal on retry."""
    from .owner_recovery import _state_snapshot
    with _state_snapshot(state) as connection:
        if any(connection.execute('SELECT COUNT(*) FROM ' + table).fetchone()[0]
               for table in ('events', 'renewals', 'turn_receipts', 'model_refs', 'model_responses')):
            raise ValueError('unselected restart state contains unexpected activity')
        actual = {row['id']: dict(row) for row in connection.execute('SELECT * FROM jobs')}
        if set(actual) != {job['id'] for job in prepared['continuations']}:
            raise ValueError('prepared restart registrations changed')
        counters = {row['kind']: row['next_value'] for row in connection.execute('SELECT * FROM model_ref_counters')}
        if counters != highwater:
            raise ValueError('prepared reference high-water counters changed')
        for job in prepared['continuations']:
            row = actual[job['id']]
            for key in ('kind', 'created', 'expires', 'due', 'event_count', 'notice_count', 'baseline',
                        'lease_boot', 'lease_deadline', 'wake_deadline'):
                if row[key] != job[key]:
                    raise ValueError('prepared restart bounds changed')
            if (json.loads(row['spec']) != job['spec'] or row['intent'] != 'active' or
                    row['root_id'] != job['id'] or row['parent_id'] is not None or
                    row['source_state'] != ('pending' if job['kind'] == 'watch' else 'none') or
                    row['generation'] is not None or row['recover_requested'] != 0 or
                    row['control_reason'] != 'daemon_restart_observation_gap; historical events were not replayed' or
                    row['source_detail'] != 'verified successor; observation gap after daemon restart'):
                raise ValueError('prepared restart intent changed')
