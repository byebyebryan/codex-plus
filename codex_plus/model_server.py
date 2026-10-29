"""Small source-local MCP stdio bridge; no daemon or global configuration setup."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys

from .model import MODEL_GUIDANCE, ModelAPI, native_context, tool_definitions, validate_arguments
from .owner_recovery import Recovery, OwnerRecoveryError
from . import VERSION
from .context import existing_socket as environment_socket, resolve
from .peers import thread_id
from .presentation import clean_text


def existing_socket(explicit=None):
    return environment_socket(explicit, run=subprocess.run)


def default_state_root():
    return resolve().state_root()


class Server:
    def __init__(self, root, socket, *, allowlist=None, max_duration=86400, max_events=1000, api_factory=ModelAPI,
                 recovery_factory=Recovery):
        self.root, self.socket, self.allowlist = root, socket, allowlist
        self.max_duration, self.max_events = max_duration, max_events
        self.api_factory = api_factory
        self.recovery_factory = recovery_factory

    def handle(self, request):
        if not isinstance(request, dict) or request.get('jsonrpc') != '2.0' or not isinstance(request.get('method'), str):
            return {'jsonrpc': '2.0', 'id': request.get('id') if isinstance(request, dict) else None,
                    'error': {'code': -32600, 'message': 'invalid request'}}
        if 'id' not in request: return None
        method, params = request['method'], request.get('params', {})
        if method == 'initialize':
            version = params.get('protocolVersion') if isinstance(params, dict) else None
            result = {'protocolVersion': version if version in ('2024-11-05', '2025-03-26', '2025-06-18') else '2025-06-18',
                      'capabilities': {'tools': {}}, 'instructions': MODEL_GUIDANCE,
                      'serverInfo': {'name': 'codex-plus', 'version': VERSION}}
        elif method == 'ping':
            result = {}
        elif method == 'tools/list':
            result = {'tools': tool_definitions(self.max_duration, self.max_events)}
        elif method == 'tools/call':
            try:
                if not isinstance(params, dict): raise ValueError('tool parameters must be an object')
                name = params.get('name')
                definition = next((tool for tool in tool_definitions(self.max_duration, self.max_events) if tool['name'] == name), None)
                if definition is None: raise ValueError('unknown model operation')
                arguments = params.get('arguments', {})
                validate_arguments(definition['inputSchema'], arguments)
                context = native_context(params.get('_meta'))
                allowed = None
                if self.allowlist:
                    values = json.loads(Path(self.allowlist).read_text())
                    if not isinstance(values, list): raise ValueError('allowlist must be a JSON list of thread identities')
                    for value in values: thread_id(value)
                    allowed = set(values)
                    if context['thread_id'] not in allowed: raise ValueError('model capabilities are not enabled for this caller')
                requested = existing_socket(self.socket)
                if name in ('owner_status', 'owner_recover'):
                    with self.recovery_factory(Path(self.root), requested, context) as api:
                        text = api.call(name, arguments)
                else:
                    with self.api_factory(Path(self.root), requested, context, allowed=allowed,
                                          max_duration=self.max_duration, max_events=self.max_events) as api:
                        text = api.call(name, arguments)
                result = {'content': [{'type': 'text', 'text': text}], 'isError': False}
            except (OSError, ValueError, KeyError, RuntimeError, TimeoutError, sqlite3.Error, subprocess.SubprocessError) as error:
                result = {'content': [{'type': 'text', 'text': clean_text(str(error), 1024)}], 'isError': True}
                if isinstance(error, OwnerRecoveryError):
                    result['structuredContent'] = {'owner_state': error.code, 'role': error.role,
                        'caller_thread': error.caller, 'recipient_thread': error.recipient,
                        'intent_registered': False}
        else:
            return {'jsonrpc': '2.0', 'id': request['id'], 'error': {'code': -32601, 'message': 'unknown method'}}
        return {'jsonrpc': '2.0', 'id': request['id'], 'result': result}

    def serve(self, source=sys.stdin, destination=sys.stdout):
        while True:
            line = source.readline(256 * 1024 + 1)
            if not line: break
            if len(line.encode('utf-8')) > 256 * 1024:
                while not line.endswith('\n'):
                    line = source.readline(256 * 1024 + 1)
                    if not line: break
                response = {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32600, 'message': 'request exceeds bound'}}
            else:
                try: response = self.handle(json.loads(line))
                except (ValueError, RecursionError):
                    response = {'jsonrpc': '2.0', 'id': None, 'error': {'code': -32700, 'message': 'invalid JSON'}}
            if response is not None:
                destination.write(json.dumps(response) + '\n'); destination.flush()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-root', type=Path, help='Private state root; otherwise environment override or home-scoped default')
    parser.add_argument('--socket', help='Existing Unix endpoint; otherwise resolve lazily from Codex daemon status')
    parser.add_argument('--allowlist', type=Path, help='Optional private JSON list restricting experimental callers/messages')
    parser.add_argument('--max-duration', type=float, default=86400)
    parser.add_argument('--max-events', type=int, default=1000)
    args = parser.parse_args(argv)
    if not 0 < args.max_duration <= 86400 or not 1 <= args.max_events <= 1000:
        parser.error('invalid operation bounds')
    if args.socket and not Path(args.socket.removeprefix('unix://')).is_absolute(): parser.error('an absolute existing Unix socket is required')
    root = resolve().state_root(args.state_root)
    if not root.is_absolute(): parser.error('an absolute private state root is required')
    os.umask(0o077)
    Server(root, args.socket, allowlist=args.allowlist, max_duration=args.max_duration,
           max_events=args.max_events).serve()
    return 0
