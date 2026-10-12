"""Reproduce source-lifetime probes without creating threads or model turns."""

from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import uuid

from native import Client


def command(code: str, process_id: str, cwd: Path, timeout: int = 5000,
            cap: int = 4096) -> dict:
    return {'command': ['rtk', 'proxy', sys.executable, '-B', '-u', '-c', code],
            'cwd': str(cwd), 'sandboxPolicy': {'type': 'readOnly'},
            'processId': process_id, 'streamStdoutStderr': True,
            'timeoutMs': timeout, 'outputBytesCap': cap}


def owned_python(code: str) -> list[tuple[Path, str]]:
    """Map an exact unique argv to host PID/start ticks, never a sandbox PID."""
    matches = []
    for process in Path('/proc').iterdir():
        if not process.name.isdecimal():
            continue
        try:
            args = (process / 'cmdline').read_bytes().split(b'\0')
            if args[-2:] == [code.encode(), b''] and 'python' in Path(os.readlink(process / 'exe')).name:
                ticks = (process / 'stat').read_text().rsplit(')', 1)[1].split()[19]
                matches.append((process, ticks))
        except OSError:
            continue
    return matches


def running(identities: list[tuple[Path, str]]) -> int:
    count = 0
    for process, ticks in identities:
        try:
            tail = (process / 'stat').read_text().rsplit(')', 1)[1].split()
            count += tail[19] == ticks and tail[0] != 'Z'
        except OSError:
            continue
    return count


def probes(requested_socket: str, root: Path) -> list[dict]:
    rows = []
    with Client(requested_socket) as client:
        started = time.monotonic()
        rid = client.submit('command/exec', command(
            'import sys,time;print("FIRST",flush=True);print("DIAGNOSTIC",file=sys.stderr,flush=True);'
            'time.sleep(1);print("LAST",flush=True)', 'source-stream', root))
        first = None
        while rid not in client.responses:
            message = client.receive(8)
            if message.get('method') == 'command/exec/outputDelta' and first is None:
                first = time.monotonic() - started
        result = client.result(rid)
        chunks = [e['params'] for e in client.events if e.get('method') == 'command/exec/outputDelta']
        rows.append({'probe': 'stream', 'exit_code': result['exitCode'],
                     'first_output_seconds': first, 'finish_seconds': time.monotonic() - started,
                     'streams': sorted({p['stream'] for p in chunks})})
    with Client(requested_socket) as client:
        rid = client.submit('command/exec', command(
            'import time;print("READY",flush=True);time.sleep(5)', 'source-cancel', root))
        while not client.events:
            client.receive(8)
        client.call('command/exec/terminate', {'processId': 'source-cancel'})
        rows.append({'probe': 'cancel', 'exit_code': client.result(rid)['exitCode']})
    with Client(requested_socket) as client:
        result = client.call('command/exec', command('import time;time.sleep(3)',
                                                    'source-timeout', root, timeout=300))
        rows.append({'probe': 'timeout', 'exit_code': result['exitCode']})
    with Client(requested_socket) as client:
        result = client.call('command/exec', command('import time;print("X"*8192,flush=True);'
                                                    'time.sleep(1)', 'source-cap', root, cap=128))
        chunks = [e['params'] for e in client.events if e.get('method') == 'command/exec/outputDelta']
        rows.append({'probe': 'cap', 'exit_code': result['exitCode'],
                     'cap_reached': any(p['capReached'] for p in chunks),
                     'bytes': sum(len(base64.b64decode(p['deltaBase64'])) for p in chunks)})
    code = 'import time;print(' + repr('codex_plus_disconnect_' + uuid.uuid4().hex) + ',flush=True);time.sleep(3)'
    with Client(requested_socket) as client:
        client.submit('command/exec', command(code, 'source-disconnect', root))
        while not client.events:
            client.receive(8)
        identities = owned_python(code)
    time.sleep(0.5)
    rows.append({'probe': 'disconnect', 'identified_children': len(identities),
                 'running_after_disconnect': running(identities)})
    with Client(requested_socket) as client:
        target = root / 'forbidden-write'
        result = client.call('command/exec', command(
            'from pathlib import Path;Path(' + repr(str(target)) + ').write_text("forbidden")',
            'source-readonly', root))
        rows.append({'probe': 'read_only', 'exit_code': result['exitCode'],
                     'write_created': target.exists()})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--socket', required=True, help='Explicit existing-owner Unix socket')
    args = parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='codex-plus-source-probe-') as root:
        for row in probes(args.socket, Path(root)):
            print(json.dumps(row))


if __name__ == '__main__':
    main()
