"""Reproducible preview artifacts and isolated immutable installations, stdlib only."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import math
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import uuid

from . import VERSION

RUNTIME_FILES = (
    'LICENSE', 'codex_plus/__init__.py', 'codex_plus/native.py', 'codex_plus/access.py',
    'codex_plus/control.py', 'codex_plus/framing.py', 'codex_plus/store.py',
    'codex_plus/engine.py', 'codex_plus/cli.py', 'codex_plus/peers.py',
    'codex_plus/peer_cli.py', 'codex_plus/presentation.py', 'codex_plus/model.py',
    'codex_plus/model_server.py', 'codex_plus/package.py',
    'scripts/codex-plus-watch', 'scripts/codex-plus-peer',
    'scripts/codex-plus-model', 'scripts/codex-plus-package',
)
COMPATIBILITY = {'os': 'linux', 'python': '>=3.11', 'codex': '0.162.1',
                 'rtk': 'required', 'transport': 'existing local Unix daemon'}
SCOPED_CONTROLS = ('watch_start', 'watch_cancel', 'watch_renew', 'watch_recover',
                   'wake_schedule', 'wake_cancel', 'event_ack')
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_ARCHIVE_BYTES = 8 * 1024 * 1024


def sha(data): return hashlib.sha256(data).hexdigest()


def file_mode(name): return 0o755 if name.startswith('scripts/') else 0o644


def revision(value):
    if not isinstance(value, str) or not re.fullmatch(r'[0-9a-f]{40}', value):
        raise ValueError('a full source revision is required')
    return value


def git(root, *args):
    return subprocess.run(['rtk', 'proxy', 'git', '-C', str(root), *args],
                          capture_output=True, check=True).stdout


def manifest(files, source_revision):
    return {'schema': 1, 'name': 'codex-plus-runtime', 'version': VERSION,
            'source_revision': revision(source_revision), 'compatibility': COMPATIBILITY,
            'files': {name: {'sha256': sha(data), 'mode': file_mode(name)}
                      for name, data in sorted(files.items())}}


def build(root, output):
    root, output = Path(root).resolve(), Path(output).absolute()
    if output.is_relative_to(root): raise ValueError('write artifacts outside the source checkout')
    if git(root, 'status', '--porcelain', '--untracked-files=all').strip():
        raise ValueError('build requires a clean committed checkout')
    source_revision = git(root, 'rev-parse', 'HEAD').decode().strip()
    files = {name: git(root, 'show', source_revision + ':' + name) for name in RUNTIME_FILES}
    metadata = manifest(files, source_revision)
    files['runtime.json'] = (json.dumps(metadata, sort_keys=True, indent=2) + '\n').encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    # Never overwrite a released artifact. Stable headers make builds reproducible.
    with output.open('xb') as destination:
        with gzip.GzipFile(filename='', fileobj=destination, mode='wb', mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode='w', format=tarfile.USTAR_FORMAT) as archive:
                for name, data in sorted(files.items()):
                    entry = tarfile.TarInfo('codex-plus-runtime/' + name)
                    entry.size, entry.mode, entry.mtime = len(data), file_mode(name), 0
                    archive.addfile(entry, io.BytesIO(data))
    return {**metadata, 'artifact_sha256': sha(output.read_bytes())}


def validate_manifest(metadata, files, modes):
    if not isinstance(metadata, dict) or set(metadata) != {'schema', 'name', 'version', 'source_revision', 'compatibility', 'files'}:
        raise ValueError('invalid runtime manifest')
    if metadata['schema'] != 1 or metadata['name'] != 'codex-plus-runtime' or metadata['version'] != VERSION:
        raise ValueError('unsupported runtime package/version')
    revision(metadata['source_revision'])
    if metadata['compatibility'] != COMPATIBILITY or set(files) != set(RUNTIME_FILES) or set(metadata['files']) != set(RUNTIME_FILES):
        raise ValueError('runtime inventory or compatibility does not match this installer')
    for name, data in files.items():
        if metadata['files'][name] != {'sha256': sha(data), 'mode': file_mode(name)} or modes[name] != file_mode(name):
            raise ValueError('runtime content/mode mismatch: ' + name)
    return metadata


def read_archive(archive_path, expected_sha=None):
    path = Path(archive_path)
    if path.stat().st_size > MAX_ARCHIVE_BYTES: raise ValueError('artifact exceeds size bound')
    payload = path.read_bytes()
    if expected_sha is not None and sha(payload) != expected_sha: raise ValueError('artifact checksum mismatch')
    files, modes = {}, {}
    with tarfile.open(fileobj=io.BytesIO(payload), mode='r:gz') as archive:
        for entry in archive:
            parts = PurePosixPath(entry.name).parts
            if len(parts) < 2 or parts[0] != 'codex-plus-runtime' or any(p in ('..', '.') for p in parts) or entry.name.startswith('/'):
                raise ValueError('unsafe artifact path')
            name = '/'.join(parts[1:])
            if name not in (*RUNTIME_FILES, 'runtime.json') or name in files or not entry.isfile() or not 0 <= entry.size <= MAX_FILE_BYTES:
                raise ValueError('unexpected, duplicate or unsafe artifact member')
            stream = archive.extractfile(entry)
            files[name], modes[name] = stream.read(MAX_FILE_BYTES + 1), entry.mode
            if len(files[name]) != entry.size: raise ValueError('artifact member size mismatch')
    if 'runtime.json' not in files or modes.pop('runtime.json') != 0o644: raise ValueError('runtime manifest missing or unsafe')
    metadata = json.loads(files.pop('runtime.json'))
    validate_manifest(metadata, files, modes)
    return metadata, files, payload


def verify_install(root):
    root = Path(root)
    if root.is_symlink() or not root.is_dir(): raise ValueError('release root must be a real directory')
    paths = [p for p in root.rglob('*') if not p.is_dir() or p.is_symlink()]
    if any(p.is_symlink() for p in paths) or {p.relative_to(root).as_posix() for p in paths} != {*RUNTIME_FILES, 'runtime.json'}:
        raise ValueError('installed inventory differs from the artifact')
    files = {name: (root / name).read_bytes() for name in RUNTIME_FILES}
    modes = {name: stat.S_IMODE((root / name).stat().st_mode) for name in RUNTIME_FILES}
    if stat.S_IMODE((root / 'runtime.json').stat().st_mode) != 0o644: raise ValueError('installed manifest mode mismatch')
    return validate_manifest(json.loads((root / 'runtime.json').read_text()), files, modes)


def install(archive_path, prefix, expected_sha=None):
    metadata, files, _ = read_archive(archive_path, expected_sha)
    prefix = Path(prefix)
    if not prefix.is_absolute() or prefix.is_symlink(): raise ValueError('a real absolute install prefix is required')
    prefix.mkdir(parents=True, exist_ok=True)
    if prefix.stat().st_uid != os.getuid() or prefix.stat().st_mode & 0o022:
        raise ValueError('install prefix must belong to this user and not be writable by others')
    releases = prefix / 'releases'
    if releases.is_symlink(): raise ValueError('release directory must not be a symlink')
    releases.mkdir(exist_ok=True)
    if releases.stat().st_uid != os.getuid() or releases.stat().st_mode & 0o022:
        raise ValueError('release directory must belong to this user and not be writable by others')
    target = releases / metadata['source_revision']
    if target.exists() or target.is_symlink():
        if verify_install(target) != metadata: raise ValueError('immutable release already exists with different content')
        return target
    temporary = Path(tempfile.mkdtemp(prefix='.install-', dir=releases))
    try:
        for name, data in files.items():
            destination = temporary / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data); destination.chmod(file_mode(name))
        (temporary / 'runtime.json').write_text(json.dumps(metadata, sort_keys=True, indent=2) + '\n')
        (temporary / 'runtime.json').chmod(0o644)
        verify_install(temporary)
        temporary.rename(target)
    finally:
        if temporary.exists(): shutil.rmtree(temporary)
    return target


def activate(prefix, source_revision):
    prefix = Path(prefix)
    if not prefix.is_absolute() or prefix.is_symlink() or prefix.stat().st_uid != os.getuid() or prefix.stat().st_mode & 0o022:
        raise ValueError('release selection requires an owned absolute prefix not writable by others')
    releases = prefix / 'releases'
    if releases.is_symlink() or releases.stat().st_uid != os.getuid() or releases.stat().st_mode & 0o022:
        raise ValueError('release selection requires an owned real release directory')
    target = prefix / 'releases' / revision(source_revision)
    verify_install(target)
    current = prefix / 'current'
    if current.exists() and not current.is_symlink(): raise ValueError('current must be an owned release-selection symlink')
    temporary = prefix / ('.current-' + str(uuid.uuid4()))
    try:
        temporary.symlink_to('releases/' + source_revision)
        temporary.replace(current)
    finally:
        temporary.unlink(missing_ok=True)
    return target


def mcp_config(prefix, *, enabled=True, allow_peer_send=False, state_root=None,
               socket=None, allowlist=None, max_duration=86400, max_events=1000):
    prefix = Path(prefix)
    current = prefix / 'current'
    if not prefix.is_absolute(): raise ValueError('an absolute installed prefix is required')
    if isinstance(max_duration, bool) or not isinstance(max_duration, (int, float)) or not math.isfinite(max_duration) or not 0 < max_duration <= 86400:
        raise ValueError('invalid configured duration bound')
    if isinstance(max_events, bool) or not isinstance(max_events, int) or not 1 <= max_events <= 1000:
        raise ValueError('invalid configured event bound')
    if enabled: verify_install(current.resolve(strict=True))
    args = ['-B', str(current / 'scripts/codex-plus-model')]
    for option, value in (('--state-root', state_root), ('--socket', socket), ('--allowlist', allowlist)):
        if value is not None: args += [option, str(value)]
    args += ['--max-duration', str(max_duration), '--max-events', str(max_events)]
    tools = {name: {'approval_mode': 'approve'} for name in SCOPED_CONTROLS}
    if allow_peer_send:
        tools.update({name: {'approval_mode': 'approve'} for name in ('peer_send', 'message_cancel')})
    return {'command': sys.executable, 'args': args, 'enabled': enabled, 'required': False,
            'default_tools_approval_mode': 'writes', 'tools': tools}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_subparsers(dest='action', required=True)
    make = actions.add_parser('build'); make.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1]); make.add_argument('--output', type=Path, required=True)
    verify = actions.add_parser('verify'); verify.add_argument('archive', type=Path); verify.add_argument('--sha256')
    put = actions.add_parser('install'); put.add_argument('archive', type=Path); put.add_argument('--prefix', type=Path, required=True); put.add_argument('--sha256')
    select = actions.add_parser('activate'); select.add_argument('--prefix', type=Path, required=True); select.add_argument('--revision', required=True)
    installed = actions.add_parser('verify-install'); installed.add_argument('root', type=Path)
    config = actions.add_parser('mcp-config'); config.add_argument('--prefix', type=Path, required=True); config.add_argument('--disabled', action='store_true'); config.add_argument('--allow-peer-send', action='store_true')
    for key in ('state-root', 'socket', 'allowlist'): config.add_argument('--' + key)
    config.add_argument('--max-duration', type=float, default=86400); config.add_argument('--max-events', type=int, default=1000)
    args = parser.parse_args(argv)
    try:
        if args.action == 'build': result = build(args.source, args.output)
        elif args.action == 'verify': result = {**read_archive(args.archive, args.sha256)[0], 'artifact_sha256': sha(args.archive.read_bytes())}
        elif args.action == 'install': result = {'installed': str(install(args.archive, args.prefix, args.sha256))}
        elif args.action == 'activate': result = {'selected': str(activate(args.prefix, args.revision))}
        elif args.action == 'verify-install': result = verify_install(args.root)
        else: result = {'mcp_servers': {'codex_plus': mcp_config(args.prefix, enabled=not args.disabled, allow_peer_send=args.allow_peer_send, state_root=args.state_root, socket=args.socket, allowlist=args.allowlist, max_duration=args.max_duration, max_events=args.max_events)}}
        print(json.dumps(result, indent=2)); return 0
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, subprocess.SubprocessError, tarfile.TarError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr); return 1
