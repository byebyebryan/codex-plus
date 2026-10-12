"""Controllable synthetic run; never contacts or operates a real job."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile
import time


def read(root: Path) -> dict:
    return json.loads((root / 'status.json').read_text())


def publish(root: Path, state: dict) -> None:
    fd, name = tempfile.mkstemp(prefix='.status-', dir=root)
    try:
        with os.fdopen(fd, 'w') as stream:
            json.dump(state, stream, sort_keys=True)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, root / 'status.json')
    finally:
        if os.path.exists(name):
            os.unlink(name)


def step(root: Path, action: str, *, amount: int = 10, message: str = '') -> dict:
    root = root.resolve()
    if action == 'init':
        root.mkdir(parents=True, exist_ok=True)
        if (root / 'status.json').exists():
            raise ValueError('fixture already initialized')
        (root / 'events.jsonl').touch()
        state = {'status': 'running', 'remaining': 100, 'progress': 0,
                 'throughput': 10, 'errors': 0, 'revision': 0, 'sequence': 0}
    else:
        state = read(root)
        if action == 'advance':
            if amount < 0 or state['status'] != 'running':
                raise ValueError('advance needs a running fixture and nonnegative amount')
            change = min(amount, state['remaining'])
            state['remaining'] -= change
            state['progress'] += change
        elif action == 'stall':
            state['throughput'] = 0
        elif action == 'recover':
            state['throughput'] = 10
        elif action == 'complete':
            state.update(status='completed', remaining=0, progress=100, throughput=0)
        elif action == 'fail':
            state.update(status='failed', throughput=0, errors=state['errors'] + 1)
        elif action == 'append-event':
            state['sequence'] += 1
            with (root / 'events.jsonl').open('a') as stream:
                stream.write(json.dumps({'sequence': state['sequence'], 'text': message}) + '\n')
        elif action != 'noise':
            raise ValueError('unknown fixture action')
    state['revision'] += 1
    state['updated_at'] = time.time()
    publish(root, state)
    return state


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('action', choices=['init', 'read', 'advance', 'stall', 'recover',
                                         'complete', 'fail', 'noise', 'append-event'])
    parser.add_argument('--amount', type=int, default=10)
    parser.add_argument('--message', default='')
    args = parser.parse_args()
    result = read(args.root) if args.action == 'read' else step(
        args.root, args.action, amount=args.amount, message=args.message)
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
