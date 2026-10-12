"""Bounded passive discovery and reads from one existing native daemon."""

from __future__ import annotations

import json
import time
import uuid

from .native import RpcError, listener_identity


ORIGINS = {'cli', 'vscode', 'exec', 'appServer'}
READ_METHODS = {'thread/loaded/list', 'thread/read', 'thread/turns/list', 'thread/goal/get'}
SIGNALS = {'phase', 'needs_input', 'goal', 'reply', 'progress', 'turn'}
DEFAULT_SIGNALS = ['reply', 'needs_input', 'goal']


def thread_id(value):
    if not isinstance(value, str):
        raise ValueError('an exact thread UUID is required')
    uuid.UUID(value)
    return value


def bounded_text(value, limit):
    if not isinstance(value, str):
        return '', False
    raw = value.encode('utf-8')
    return raw[:limit].decode('utf-8', errors='ignore'), len(raw) > limit


def classification(thread):
    """Use native provenance; analytics source and fork ancestry are not ownership."""
    source = thread.get('source')
    parent = thread.get('parentThreadId')
    child = isinstance(source, dict) and set(source) == {'subAgent'} and isinstance(source['subAgent'], (str, dict))
    nested = None
    if child and isinstance(source['subAgent'], dict):
        spawn = source['subAgent'].get('thread_spawn')
        if isinstance(spawn, dict):
            nested = spawn.get('parent_thread_id')
    try:
        for value in (parent, nested):
            if value is not None:
                thread_id(value)
    except ValueError:
        return {'kind': 'unknown', 'parent_id': None, 'reason': 'invalid_parent'}
    if parent and nested and parent != nested:
        return {'kind': 'unknown', 'parent_id': None, 'reason': 'conflicting_parents'}
    parent = parent or nested
    ordinary = isinstance(source, str) and source in ORIGINS
    if ordinary and parent:
        return {'kind': 'unknown', 'parent_id': parent, 'reason': 'conflicting_provenance'}
    if child or parent:
        return {'kind': 'subagent', 'parent_id': parent, 'reason': 'native_delegation'}
    if ordinary:
        return {'kind': 'independent', 'parent_id': None, 'reason': 'native_ordinary_origin'}
    return {'kind': 'unknown', 'parent_id': None, 'reason': 'provenance_unavailable'}


def metadata(thread):
    identity = thread_id(thread.get('id'))
    status = thread.get('status')
    if not isinstance(status, dict):
        status = {'type': 'unknown'}
    name, name_cut = bounded_text(thread.get('name'), 512)
    cwd, cwd_cut = bounded_text(thread.get('cwd'), 1024)
    return {'thread_id': identity, **classification(thread), 'name': name, 'cwd': cwd,
            'context_truncated': name_cut or cwd_cut, 'status': status,
            'forked_from': thread.get('forkedFromId'),
            'direct_input': thread.get('canAcceptDirectInput'),
            'updated_at': thread.get('updatedAt')}


class PeerReader:
    def __init__(self, client, *, monotonic=time.monotonic):
        self.client = client
        self.monotonic = monotonic
        self.owner = dict(client.identity)

    def remaining(self, deadline):
        remaining = deadline - self.monotonic()
        if remaining <= 0:
            raise TimeoutError('peer read budget ended')
        return remaining

    def check_owner(self):
        if listener_identity(self.owner['requested_socket']) != self.owner:
            raise RpcError('peer daemon owner changed')

    def rpc(self, method, params, deadline):
        if method not in READ_METHODS:
            raise ValueError('peer reader permits only passive native reads')
        result = self.client.call(method, params, timeout=self.remaining(deadline))
        self.remaining(deadline)
        return result

    def loaded(self, deadline):
        ids, seen, cursors = [], set(), set()
        cursor = None
        for _ in range(20):
            params = {'limit': 100}
            if cursor:
                params['cursor'] = cursor
            page = self.rpc('thread/loaded/list', params, deadline)
            rows = page.get('data')
            if not isinstance(rows, list) or len(rows) > 100:
                raise RpcError('invalid or oversized loaded inventory')
            for value in rows:
                thread_id(value)
                if value in seen:
                    return ids, False, 'loaded inventory changed or duplicated'
                seen.add(value); ids.append(value)
            cursor = page.get('nextCursor')
            if cursor is None:
                return ids, True, ''
            if not isinstance(cursor, str) or not cursor or cursor in cursors:
                return ids, False, 'loaded inventory cursor unresolved'
            cursors.add(cursor)
        return ids, False, 'loaded inventory page limit reached'

    def discover(self, *, caller=None, limit=100, timeout=10):
        if caller is not None:
            thread_id(caller)
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 1000:
            raise ValueError('metadata limit must be 1 through 1000')
        deadline = self.monotonic() + timeout
        self.check_owner()
        ids, complete, detail = self.loaded(deadline)
        targets = [tid for tid in ids if tid != caller]
        peers, children, unknown = [], [], []
        for tid in targets[:limit]:
            try:
                thread = self.rpc('thread/read', {'threadId': tid}, deadline)['thread']
                if thread.get('id') != tid:
                    raise RpcError('peer metadata identity mismatch')
                row = metadata(thread)
                phase = row['status'].get('type')
                if row['kind'] == 'independent' and phase in ('idle', 'active'):
                    peers.append(row)
                elif row['kind'] == 'subagent':
                    children.append(row)
                else:
                    unknown.append(row)
            except (OSError, ValueError, KeyError, RpcError, TimeoutError) as error:
                complete = False
                unknown.append({'thread_id': tid, 'kind': 'unknown',
                                'reason': 'metadata_unavailable', 'detail': str(error)[:200]})
        if len(targets) > limit:
            complete = False; detail = 'metadata limit reached'
        self.check_owner()
        return {'owner': self.owner, 'peers': peers, 'children': children,
                'unclassified': unknown, 'complete': complete, 'detail': detail,
                'loaded_count': len(ids), 'observed_at': time.time(),
                'scope': 'current daemon loaded inventory', 'caller_excluded': caller is not None}

    def resolve(self, *, target=None, name=None, caller=None, timeout=10):
        if (target is None) == (name is None):
            raise ValueError('select an exact UUID or exact independent-session name')
        if name is not None and (not isinstance(name, str) or not name.strip()):
            raise ValueError('an independent-session name must be nonempty')
        if target is not None:
            thread_id(target)
            if target == caller:
                raise ValueError('the calling session is not a peer')
            return self.validate({**self.owner, 'thread_id': target}, timeout=timeout)['binding']
        inventory = self.discover(caller=caller, timeout=timeout)
        if not inventory['complete']:
            raise ValueError('inventory incomplete; resolve an exact verified UUID')
        matches = [row for row in inventory['peers'] if row['name'] == name]
        if len(matches) != 1:
            raise ValueError('independent-session name is missing or ambiguous; select an exact UUID')
        return {**self.owner, 'thread_id': matches[0]['thread_id']}

    def validate(self, frozen, *, timeout=5, deadline=None):
        deadline = deadline if deadline is not None else self.monotonic() + timeout
        target = thread_id(frozen.get('thread_id'))
        if frozen != {**self.owner, 'thread_id': target}:
            raise RpcError('frozen peer owner differs from connected owner')
        self.check_owner()
        ids, complete, _ = self.loaded(deadline)
        if target not in ids:
            raise RpcError('peer not positively loaded; inventory ' + ('complete' if complete else 'incomplete'))
        thread = self.rpc('thread/read', {'threadId': target}, deadline)['thread']
        if thread.get('id') != target:
            raise RpcError('peer metadata identity mismatch')
        row = metadata(thread)
        if row['kind'] != 'independent':
            raise RpcError('peer is not a verified independent session: ' + row['reason'])
        if row['status'].get('type') not in ('idle', 'active'):
            raise RpcError('peer runtime unavailable; no load or resume attempted')
        self.check_owner()
        return {'binding': dict(frozen), 'peer': row}

    def read(self, frozen, *, turn_limit=3, history=True, goal=True, timeout=5):
        if isinstance(turn_limit, bool) or not isinstance(turn_limit, int) or not 1 <= turn_limit <= 10:
            raise ValueError('turn window must be 1 through 10')
        deadline = self.monotonic() + timeout
        result = self.validate(frozen, deadline=deadline)
        target = frozen['thread_id']
        turns, clipped = [], False
        if history:
            page = self.rpc('thread/turns/list', {'threadId': target, 'limit': turn_limit,
                'itemsView': 'summary', 'sortDirection': 'desc'}, deadline)
            if not isinstance(page.get('data'), list) or len(page['data']) > turn_limit:
                raise RpcError('invalid or oversized peer turn window')
            for turn in page['data']:
                items = []
                # Tool outputs and user prompts are deliberately not exported here.
                relevant = [item for item in turn.get('items', [])
                            if item.get('type') in ('agentMessage', 'plan')]
                for item in relevant[-6:]:
                    text, cut = bounded_text(item.get('text'), 1024)
                    items.append({'id': item['id'], 'type': item['type'],
                                  'phase': item.get('phase'), 'text': text, 'text_truncated': cut})
                    clipped |= cut
                clipped |= len(relevant) > 6
                turns.append({'id': turn['id'], 'status': turn['status'], 'items': items})
        goal_state = 'not_requested'
        if goal:
            response = self.rpc('thread/goal/get', {'threadId': target}, deadline)
            if 'goal' not in response:
                raise RpcError('peer goal state unavailable')
            native_goal = response['goal']
            if native_goal is not None and (not isinstance(native_goal, dict) or native_goal.get('threadId') != target):
                raise RpcError('peer goal identity mismatch')
            goal_state = native_goal.get('status', 'unknown') if native_goal is not None else None
        self.check_owner()
        result.update(turns=turns, goal_status=goal_state, observed_at=time.time(),
                      coverage={'mode': 'bounded_snapshot', 'lossless': False,
                                'turn_window': turn_limit if history else 0,
                                'content_truncated': clipped})
        return result


def snapshot(read, signals, *, gap=False):
    if not isinstance(signals, list) or not signals or len(signals) != len(set(signals)) or set(signals) - SIGNALS:
        raise ValueError('select distinct supported peer signals')
    result = {'peer_id': read['peer']['thread_id'],
              'coverage': {**read['coverage'], 'observation_gap': gap},
              'task_outcome': 'unknown'}
    status = read['peer']['status']
    if 'phase' in signals:
        result['phase'] = status
    if 'needs_input' in signals:
        flags = status.get('activeFlags') if status.get('type') == 'active' else []
        result['needs_input'] = ([flag for flag in flags if flag in ('waitingOnApproval', 'waitingOnUserInput')]
                                 if isinstance(flags, list) else 'unknown')
    if 'goal' in signals:
        result['goal'] = read['goal_status']
    turns = read['turns']
    if 'turn' in signals:
        result['turn'] = {'id': turns[0]['id'], 'status': turns[0]['status']} if turns else None
    for signal in ('reply', 'progress'):
        if signal not in signals:
            continue
        matches = []
        maximum = 1 if signal == 'reply' else 3
        for turn in turns:
            for item in reversed(turn['items']):
                final = item['type'] == 'agentMessage' and item['phase'] == 'final_answer'
                if signal == 'reply' and not (final and turn['status'] == 'completed'):
                    continue
                if signal == 'progress' and not (item['type'] == 'plan' or
                        item['type'] == 'agentMessage' and item['phase'] == 'commentary'):
                    continue
                text, cut = bounded_text(item['text'], 384)
                matches.append({'turn_id': turn['id'], 'turn_status': turn['status'],
                    'item_id': item['id'], 'text': text,
                    'text_truncated': cut or item['text_truncated']})
            if len(matches) >= maximum:
                break
        result[signal] = matches[:maximum]
    result['coverage']['content_truncated'] = any(
        item['text_truncated'] for signal in ('reply', 'progress')
        for item in result.get(signal, []))
    if len(json.dumps(result, ensure_ascii=False).encode()) > 4096:
        raise ValueError('selected peer snapshot exceeds 4 KiB')
    return result
