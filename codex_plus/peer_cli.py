"""Passive discovery CLI. Sending and watching reuse the watch coordinator."""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

from .context import existing_socket
from .native import Client
from .peers import PeerReader


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--socket')
    parser.add_argument('--caller', default=os.environ.get('CODEX_THREAD_ID'))
    operations = parser.add_subparsers(dest='operation', required=True)
    listing = operations.add_parser('list')
    listing.add_argument('--include-children', action='store_true')
    listing.add_argument('--limit', type=int, default=100)
    resolve = operations.add_parser('resolve')
    choice = resolve.add_mutually_exclusive_group(required=True)
    choice.add_argument('--id')
    choice.add_argument('--name')
    read = operations.add_parser('read')
    read.add_argument('id')
    read.add_argument('--turn-limit', type=int, default=3)
    args = parser.parse_args(argv)
    requested = existing_socket(args.socket)
    with Client(requested, experimental=True) as client:
        reader = PeerReader(client)
        if args.operation == 'list':
            result = reader.discover(caller=args.caller, limit=args.limit)
            result['child_count'] = len(result['children'])
            if not args.include_children:
                del result['children']
        else:
            frozen = reader.resolve(target=args.id, name=args.name if args.operation == 'resolve' else None,
                                    caller=args.caller)
            result = ({'binding': frozen, 'state': 'resolved'} if args.operation == 'resolve'
                      else reader.read(frozen, turn_limit=args.turn_limit))
        print(json.dumps(result))
    return 0


def entrypoint():
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, RuntimeError, TimeoutError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        raise SystemExit(1)
