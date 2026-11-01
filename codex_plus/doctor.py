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
import uuid

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


def loaded_mcp(requested, thread, components, *, client_factory=None):
    if not thread:
        return {'state': 'not_checked', 'detail': 'No loaded conversation selected; use CODEX_THREAD_ID or --thread.'}
    try:
        if not isinstance(thread, str): raise ValueError('expected a native thread identity')
        uuid.UUID(thread)
        if client_factory is None:
            try:
                from .native import Client
            except ImportError:
                return {'state': 'not_available', 'detail': 'The monitoring component supplies native MCP introspection.'}
            client_factory = Client
        servers = {}
        with client_factory(requested, experimental=True, timeout=5) as client:
            client.bind(thread, timeout=5)  # Positive loaded inventory only; never resume.
            for name, component in (('codex_plus', 'monitoring'), ('html_report', 'reporting')):
                page = client.call('mcpServerStatus/list', {'threadId': thread, 'serverName': name,
                    'detail': 'toolsAndAuthOnly'}, timeout=5)
                rows = page.get('data', [])
                if len(rows) != 1 or rows[0].get('name') != name or page.get('nextCursor'):
                    servers[name] = {'state': 'not_reported', 'version_alignment': 'unknown'}
                    continue
                row = rows[0]
                info = row.get('serverInfo')
                version = info.get('version') if isinstance(info, dict) else None
                if not isinstance(version, str) or not 1 <= len(version) <= 128: version = None
                selected_version = components[component].get('version')
                servers[name] = {'state': row.get('runtimeStatus') or 'unknown',
                    'reported_version': version, 'selected_version': selected_version,
                    'version_alignment': ('same_reported_version' if version == selected_version else 'different_reported_version')
                        if row.get('runtimeStatus') == 'connected' and version and selected_version else 'unknown'}
        return {'state': 'reported', 'scope': 'one positively loaded conversation', 'servers': servers,
                'note': 'Native MCP metadata reports versions; it does not verify loaded payload bytes or other conversations.'}
    except (OSError, ValueError, RuntimeError, TimeoutError) as error:
        return {'state': 'unavailable', 'detail': type(error).__name__,
                'note': 'No conversation was resumed, server refreshed or owner started.'}


def diagnose(*, runtime_prefix=None, report_prefix=None, worker_prefix=None,
             state_root=None, report_config=None, thread=None, check_native=True,
             run=subprocess.run, client_factory=None):
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
        'components': {}, 'loaded_processes_checked': False, 'loaded_mcp': {'state': 'not_checked'},
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
        status = {}
        try:
            status = json.loads(owner) if isinstance(owner, str) else owner
            if not isinstance(status, dict): raise ValueError('invalid native owner status')
            result['native']['owner_status'] = {key: status[key] for key in ('status', 'version', 'cliVersion', 'appServerVersion', 'managedCodexVersion') if key in status}
            owner_version = status.get('appServerVersion')
            result['native']['owner_qualification'] = ('version_matches_recorded_baseline'
                if owner_version and owner_version == qualified else 'not_established')
        except (ValueError, TypeError):
            status = {}
            result['native']['owner_status'] = {'state': 'unavailable'}
        requested = os.environ.get('CODEX_PLUS_SOCKET') or status.get('socketPath') or result['environment']['socket']
        result['loaded_mcp'] = loaded_mcp(str(requested).removeprefix('unix://'),
            thread or os.environ.get('CODEX_THREAD_ID'), result['components'], client_factory=client_factory)
    return result


def human_text(value):
    # Paths and reported metadata must stay on one inert terminal line.
    return re.sub(r'[\x00-\x1f\x7f-\x9f]', lambda match: '\\x%02x' % ord(match[0]), str(value))


def format_human(result):
    """Present the same diagnostic evidence without adding probes or conclusions."""
    environment = result['environment']
    lines = [f"Codex Plus doctor {human_text(result['tool_version'])}",
             f"Environment: {human_text(environment['environment_key'])}"]
    for label, key in (('Codex home', 'codex_home'), ('State', 'state_root'),
                       ('Report config', 'report_config'), ('Reports', 'report_data_root')):
        lines.append(f"  {label}: {human_text(environment[key])}")
    lines.extend([f"Configuration: {human_text(result['config_state'])}",
                  f"Selected components: {human_text(result['release_alignment'])}"])
    for name, row in result['components'].items():
        state = row['state']
        identity = f"{human_text(row['version'])}; " if state == 'manifest_verified' else ''
        lines.append(f"  {name}: {identity}{human_text(state).replace('_', ' ')}")
        if row.get('source_revision'):
            lines.append('    Source: ' + human_text(row['source_revision']))
        lines.append('    Path: ' + human_text(row.get('selected_path', row['prefix'])))
        if row.get('detail'): lines.append('    Detail: ' + human_text(row['detail']))
    native = result['native']
    if native.get('state') == 'not_checked':
        lines.append('Native: not checked (--no-native)')
    else:
        owner = native.get('owner_status', {})
        lines.extend([
            'Native client: ' + human_text(native['client_version']),
            'Native owner: ' + human_text(owner.get('appServerVersion', 'unknown'))
                + ' (' + human_text(owner.get('status', owner.get('state', 'unknown'))) + ')',
            '  Recorded qualification baseline: ' + human_text(native.get('qualified_version') or 'unknown'),
            '  Client qualification: ' + human_text(native['qualification']).replace('_', ' '),
            '  Owner qualification: ' + human_text(native.get('owner_qualification', 'not_established')).replace('_', ' '),
            '  ' + human_text(native['qualification_note']),
        ])
    lines.append('MCP configuration:')
    for name, row in result['mcp_configuration'].items():
        enabled = row['enabled']
        state = 'not configured' if not row['configured'] else (
            'enabled' if enabled is True else 'disabled' if enabled is False else 'unknown enabled setting')
        lines.append(f'  {name}: {state}')
    loaded = result['loaded_mcp']
    lines.append('Loaded MCP metadata: ' + human_text(loaded['state']).replace('_', ' '))
    for name, row in loaded.get('servers', {}).items():
        lines.append(f"  {name}: {human_text(row['state'])}; reported {human_text(row.get('reported_version') or 'unknown')}; "
                     f"selected {human_text(row.get('selected_version') or 'unknown')}; "
                     f"{human_text(row['version_alignment']).replace('_', ' ')}")
    if loaded.get('detail'): lines.append('  ' + human_text(loaded['detail']))
    if loaded.get('note'): lines.append('  ' + human_text(loaded['note']))
    lines.extend([human_text(result['integrity_note']), human_text(result['activation_note'])])
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for option in ('runtime-prefix', 'report-prefix', 'worker-prefix', 'state-root', 'report-config'):
        parser.add_argument('--' + option, type=Path)
    parser.add_argument('--no-native', action='store_true', help='Only inspect selected files and configuration')
    parser.add_argument('--human', action='store_true', help='Readable summary of the same evidence; default output is JSON')
    parser.add_argument('--thread', help='Inspect native MCP version metadata for this positively loaded conversation; defaults to CODEX_THREAD_ID')
    args = vars(parser.parse_args(argv))
    human = args.pop('human')
    args['check_native'] = not args.pop('no_native')
    try:
        result = diagnose(**args)
        print(format_human(result) if human else json.dumps(result, indent=2))
        return 1 if result['config_state'] == 'unreadable_or_invalid' or any(row['state'] == 'invalid' for row in result['components'].values()) else 0
    except (OSError, ValueError, TypeError) as error:
        print('Codex Plus doctor: ERROR: ' + human_text(error) if human else json.dumps({'error': str(error)})); return 1
