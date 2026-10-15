"""Read-only, bounded relations for outstanding completion cards only."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import socket
import time

from .native import Client, listener_identity
from .notification_protocol import event_id, native_id, validate

MAX_CARDS = 32


def default_socket():
    return str(Path(os.environ.get('CODEX_HOME') or Path.home() / '.codex').expanduser()
               / 'app-server-control/app-server-control.sock')


def source_identity(path):
    # A configured native instance, stable across daemon restarts. No PID/TTY inference.
    return socket.gethostname(), hashlib.sha256(str(Path(path).expanduser().absolute()).encode()).hexdigest()[:24]


def relation(page, previous):
    """Use native descending history; opaque IDs never establish chronology."""
    turns = page.get('data') if isinstance(page, dict) else None
    if not isinstance(turns, list) or len(turns) > 32:
        return 'unknown'
    ids = []
    for turn in turns:
        if not isinstance(turn, dict) or turn.get('status') not in ('completed', 'inProgress', 'interrupted', 'failed'):
            return 'unknown'
        try:
            ids.append(native_id(turn.get('id')))
        except ValueError:
            return 'unknown'
    if len(ids) != len(set(ids)) or previous not in ids:
        return 'unknown'
    index = ids.index(previous)
    if turns[index]['status'] != 'completed':
        return 'unknown'
    return 'superseded' if index > 0 else 'current'


def inspect(request, path, *, client_factory=Client, identity=listener_identity, timeout=6):
    if (not isinstance(request, dict) or set(request) != {'v', 'nonce', 'cards'}
            or request['v'] != 1 or type(request['v']) is not int
            or not isinstance(request['nonce'], str) or not re.fullmatch('[0-9a-f]{32}', request['nonce'])
            or not isinstance(request['cards'], list) or len(request['cards']) > MAX_CARDS):
        raise ValueError('invalid inspection request')
    cards = [validate(card) for card in request['cards']]
    host, instance = source_identity(path)
    results = {event_id(card): 'unknown' for card in cards}
    deadline = time.monotonic() + timeout
    try:
        with client_factory(path, experimental=True, timeout=timeout) as client:
            pages = {}
            for card in cards:
                if (card['host'], card['instance']) != (host, instance):
                    continue
                thread = card['thread']
                if thread not in pages:
                    pages[thread] = client.call('thread/turns/list', {
                        'threadId': thread, 'limit': 32, 'itemsView': 'summary', 'sortDirection': 'desc',
                    }, timeout=client.remaining(deadline))
                results[event_id(card)] = relation(pages[thread], card['turn'])
            if identity(path) != client.identity:
                results = dict.fromkeys(results, 'unknown')
    except (OSError, RuntimeError, ValueError, KeyError, TypeError, TimeoutError):
        results = dict.fromkeys(results, 'unknown')
    return {'v': 1, 'nonce': request['nonce'], 'host': host, 'instance': instance, 'results': results}


def main(path):
    import sys
    raw = sys.stdin.buffer.read(65537)
    if len(raw) > 65536:
        raise ValueError('inspection request exceeds bound')
    print(json.dumps(inspect(json.loads(raw), path), separators=(',', ':')))
