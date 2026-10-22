"""Read-only selected installations and native version evidence; never starts services."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
import tomllib

from . import VERSION
from .context import absolute, describe, resolve


def bounded(path, maximum=65536):
    if path.is_symlink() or not path.is_file() or path.stat().st_size > maximum:
        raise ValueError('expected a bounded regular file')
    return path.read_bytes()


def selected(prefix, manifest, name):
    prefix = absolute(prefix)
    candidate = prefix / 'current'
    # Legacy workers are a direct managed tree; optional installs may be absent.
    if name == 'codex-plus-workers' and not candidate.exists() and not candidate.is_symlink():
        candidate = prefix
    if not candidate.exists() and not candidate.is_symlink():
        return {'state': 'not_installed', 'prefix': str(prefix)}
    root = candidate.resolve()
    if name == 'codex-plus-workers' and not (root / manifest).exists():
        return {'state': 'legacy_unversioned', 'prefix': str(prefix), 'selected_path': str(root)}
    try:
        metadata = json.loads(bounded(root / manifest, 256 * 1024))
        if (metadata.get('schema') != 1 or metadata.get('name') != name
                or not isinstance(metadata.get('version'), str)
                or not re.fullmatch('[0-9a-f]{40}', metadata.get('source_revision', ''))
                or not isinstance(metadata.get('files'), dict) or not 1 <= len(metadata['files']) <= 200):
            raise ValueError('invalid installed manifest identity/inventory')
        expected = {manifest}
        for filename, receipt in metadata['files'].items():
            parts = PurePosixPath(filename)
            if parts.is_absolute() or '..' in parts.parts or str(parts) != filename or not parts.parts:
                raise ValueError('unsafe manifest member path')
            member = root / filename
            if any(parent.is_symlink() for parent in (member, *member.parents) if parent != root and parent.is_relative_to(root)):
                raise ValueError('linked manifest member')
            payload = bounded(member, 2 * 1024 * 1024)
            if receipt != {'sha256': hashlib.sha256(payload).hexdigest(), 'mode': stat.S_IMODE(member.stat().st_mode)}:
                raise ValueError('installed content/mode differs: ' + filename)
            expected.add(filename)
        actual = {path.relative_to(root).as_posix() for path in root.rglob('*') if not path.is_dir() or path.is_symlink()}
        if actual != expected: raise ValueError('installed inventory differs')
        return {'state': 'manifest_verified', 'prefix': str(prefix), 'selected_path': str(root),
                'version': metadata['version'], 'source_revision': metadata['source_revision'],
                'compatibility': metadata.get('compatibility', {}), 'files': len(metadata['files'])}
    except (OSError, ValueError, KeyError, TypeError) as error:
        return {'state': 'invalid', 'prefix': str(prefix), 'selected_path': str(root), 'detail': str(error)}


def command_version(argv, *, run):
    try:
        result = run(['rtk', 'proxy', 'codex', *argv], capture_output=True, text=True,
                     check=True, timeout=5, env={**os.environ, 'CODEX_HOME': str(resolve().home)})
        return result.stdout
    except (OSError, subprocess.SubprocessError) as error:
        return {'state': 'unavailable', 'detail': type(error).__name__}


def diagnose(*, runtime_prefix=None, report_prefix=None, worker_prefix=None,
             state_root=None, report_config=None, check_native=True, run=subprocess.run):
    context = resolve()
    config_path = context.home / 'config.toml'
    try:
        config = tomllib.loads(bounded(config_path).decode()) if config_path.exists() else {}
        servers = config.get('mcp_servers', {})
        if not isinstance(servers, dict) or any(not isinstance(row, dict) for row in servers.values()):
            raise ValueError('invalid MCP server table')
        config_state = 'read' if config_path.exists() else 'missing'
    except (OSError, ValueError, TypeError):
        servers, config_state = {}, 'unreadable_or_invalid'
    # Reflect managed command-line path overrides without exposing other arguments.
    def override(server, flag):
        arguments = servers.get(server, {}).get('args', [])
        if isinstance(arguments, list) and flag in arguments:
            index = arguments.index(flag) + 1
            if index < len(arguments) and isinstance(arguments[index], str): return arguments[index]
        return None
    result = {'schema': 1, 'tool_version': VERSION, 'environment': describe(
        state_root=state_root or override('codex_plus', '--state-root'),
        report_config=report_config or override('html_report', '--config')),
        'config_state': config_state, 'mcp_configuration': {
            name: {'configured': name in servers, 'enabled': servers[name].get('enabled', True) if name in servers else False}
            for name in ('codex_plus', 'html_report')},
        'components': {}, 'loaded_processes_checked': False,
        'integrity_note': 'Manifest consistency is local integrity evidence; compare release checksums for published provenance.',
        'activation_note': 'Selected files and enabled configuration do not prove which release existing MCP processes loaded.'}
    for name, prefix, manifest, identity in (
            ('workers', worker_prefix or context.data_base / 'codex-worker-kit', 'workers.json', 'codex-plus-workers'),
            ('monitoring', runtime_prefix or context.data_base / 'codex-plus', 'runtime.json', 'codex-plus-runtime'),
            ('reporting', report_prefix or context.data_base / 'codex-plus-report', 'report.json', 'codex-plus-report')):
        result['components'][name] = selected(prefix, manifest, identity)
    identities = {(row['version'], row['source_revision']) for row in result['components'].values() if row['state'] == 'manifest_verified'}
    result['release_alignment'] = 'mixed' if len(identities) > 1 else 'aligned' if identities else 'unknown'
    result['native'] = {'state': 'not_checked'}
    if check_native:
        client = command_version(['--version'], run=run)
        owner = command_version(['app-server', 'daemon', 'version'], run=run)
        match = re.search(r'\b(\d+\.\d+\.\d+)\b', client) if isinstance(client, str) else None
        qualified = result['components']['monitoring'].get('compatibility', {}).get('codex')
        result['native'] = {'client_version': match.group(1) if match else 'unavailable',
                            'qualified_version': qualified,
                            'qualification': 'version_matches_recorded_baseline' if match and match.group(1) == qualified else 'not_established',
                            'qualification_note': 'A version match alone is not a new native acceptance test.'}
        try:
            status = json.loads(owner) if isinstance(owner, str) else owner
            result['native']['owner_status'] = {key: status[key] for key in ('status', 'version', 'cliVersion', 'appServerVersion', 'managedCodexVersion') if key in status}
            owner_version = status.get('appServerVersion')
            result['native']['owner_qualification'] = ('version_matches_recorded_baseline'
                if owner_version and owner_version == qualified else 'not_established')
        except (ValueError, TypeError): result['native']['owner_status'] = {'state': 'unavailable'}
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ('runtime-prefix', 'report-prefix', 'worker-prefix', 'state-root', 'report-config'):
        parser.add_argument('--' + option, type=Path)
    parser.add_argument('--no-native', action='store_true', help='Only inspect selected files and configuration')
    args = vars(parser.parse_args(argv))
    args['check_native'] = not args.pop('no_native')
    try:
        result = diagnose(**args)
        print(json.dumps(result, indent=2))
        return 1 if result['config_state'] == 'unreadable_or_invalid' or any(row['state'] == 'invalid' for row in result['components'].values()) else 0
    except (OSError, ValueError, TypeError) as error:
        print(json.dumps({'error': str(error)})); return 1
