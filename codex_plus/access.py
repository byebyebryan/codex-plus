"""Source execution uses verified native caller permissions, never server defaults."""

from __future__ import annotations

import copy
import json
from pathlib import Path


def policy(value):
    if not isinstance(value, dict):
        raise ValueError('native source policy unavailable')
    result = copy.deepcopy(value)
    kind = result.get('type')
    fields = {
        'dangerFullAccess': {'type'},
        'readOnly': {'type', 'networkAccess'},
        'workspaceWrite': {'type', 'writableRoots', 'networkAccess',
                           'excludeTmpdirEnvVar', 'excludeSlashTmp'},
    }
    if kind not in fields or set(result) - fields[kind]:
        raise ValueError('native source policy cannot be represented by this runtime')
    if kind != 'dangerFullAccess':
        result.setdefault('networkAccess', False)
        if not isinstance(result['networkAccess'], bool):
            raise ValueError('native network permission is not a boolean')
    if kind == 'workspaceWrite':
        roots = result.get('writableRoots', [])
        if not isinstance(roots, list) or any(not isinstance(p, str) or not Path(p).is_absolute() for p in roots):
            raise ValueError('native writable roots unavailable')
        result['writableRoots'] = roots
        for name in ('excludeTmpdirEnvVar', 'excludeSlashTmp'):
            if name in result and not isinstance(result[name], bool):
                raise ValueError('native temporary-path permission unavailable')
    return result


def snapshot(response):
    """Only inspect a positively loaded caller; do not resume a cold source/peer."""
    native = policy(response.get('sandbox'))
    cwd = response.get('cwd')
    if not isinstance(cwd, str) or not Path(cwd).is_absolute():
        raise ValueError('native permission working directory unavailable')
    profile = response.get('activePermissionProfile')
    if profile is not None and (not isinstance(profile, dict) or not isinstance(profile.get('id'), str) or not profile['id']):
        raise ValueError('native permission profile provenance unavailable')
    return {'sandbox': native, 'profile': copy.deepcopy(profile), 'cwd': cwd}


def effective(native, cwd, source_access='session', network_access='inherit'):
    if source_access not in ('session', 'read_only') or network_access not in ('inherit', 'off', 'required'):
        raise ValueError('unsupported source access choice')
    sandbox = policy(native['sandbox'])
    network = sandbox['type'] == 'dangerFullAccess' or sandbox.get('networkAccess', False)
    if network_access == 'required' and not network:
        raise ValueError('this session does not authorize network access for the source')
    profile = native.get('profile')
    if profile:
        if str(Path(cwd).resolve()) != str(Path(native['cwd']).resolve()):
            raise ValueError('a named source profile must retain its native working directory')
        if (source_access == 'read_only' and sandbox['type'] != 'readOnly'
                or network_access == 'off' and network):
            raise ValueError('this profile cannot be narrowed through the legacy policy; select an appropriate native profile')
        return {'permissionProfile': profile['id']}
    if source_access == 'read_only':
        sandbox = {'type': 'readOnly', 'networkAccess': network}
    if network_access == 'off':
        if sandbox['type'] == 'dangerFullAccess':
            raise ValueError('network-off needs read_only source access for a full-access session')
        sandbox['networkAccess'] = False
    return {'sandboxPolicy': sandbox}


def resolve(client, frozen, cwd, source_access='session', network_access='inherit'):
    if client.bind(frozen['thread_id']) != frozen:
        raise ValueError('source permission owner changed')
    # The coordinator already uses this qualified subscription route. Supply no
    # configuration overrides and positively check loaded membership first.
    response = client.call('thread/resume', {'threadId': frozen['thread_id'], 'excludeTurns': True})
    if response.get('thread', {}).get('id') != frozen['thread_id']:
        raise ValueError('native permission response belongs to another thread')
    native = snapshot(response)
    request = effective(native, cwd, source_access, network_access)
    return {'native': native, 'request': request,
            'source_access': source_access, 'network_access': network_access}


def validate_grant(grant, cwd):
    if not isinstance(grant, dict) or set(grant) != {'native', 'request', 'source_access', 'network_access'}:
        raise ValueError('invalid native source execution grant')
    native = grant['native']
    if not isinstance(native, dict) or set(native) != {'sandbox', 'profile', 'cwd'}:
        raise ValueError('invalid native source permission snapshot')
    checked = snapshot({'sandbox': native['sandbox'], 'activePermissionProfile': native['profile'], 'cwd': native['cwd']})
    expected = effective(checked, cwd, grant['source_access'], grant['network_access'])
    if grant['request'] != expected:
        raise ValueError('source request does not match its native permission snapshot')
    return grant


def current(client, frozen, grant, cwd):
    validated = resolve(client, frozen, cwd, grant['source_access'], grant['network_access'])
    if validated != grant:
        raise ValueError('native source permissions changed; register or renew explicitly')
    return grant['request']


def mcp_spec(server, tool, arguments):
    for value in (server, tool):
        if not isinstance(value, str) or not value.strip() or len(value.encode()) > 256 or any(ord(c) < 32 for c in value):
            raise ValueError('MCP server/tool must be a bounded configured name')
    if not isinstance(arguments, dict):
        raise ValueError('MCP inspection arguments must be an object')
    try:
        raw = json.dumps(arguments, allow_nan=False)
    except (ValueError, TypeError, RecursionError) as error:
        raise ValueError('MCP inspection arguments must be finite bounded JSON') from error
    if len(raw.encode()) > 4096:
        raise ValueError('MCP inspection arguments exceed 4 KiB')
    return {'server': server, 'tool': tool, 'arguments': copy.deepcopy(arguments)}


def configured_mcp(client, frozen, spec):
    """Inspect availability only. Direct RPC invocation bypasses model approvals."""
    if client.bind(frozen['thread_id']) != frozen:
        raise ValueError('MCP inspection owner changed')
    page = client.call('mcpServerStatus/list', {'threadId': frozen['thread_id'],
        'serverName': spec['server'], 'detail': 'toolsAndAuthOnly', 'limit': 100})
    if page.get('nextCursor'):
        raise ValueError('MCP inspection inventory incomplete')
    rows = [row for row in page['data'] if row.get('name') == spec['server']]
    if len(rows) != 1 or spec['tool'] not in rows[0].get('tools', {}):
        raise ValueError('selected MCP server/tool is unavailable or disabled')
    return {'type': 'nativeModelInspection', 'server': spec['server'],
            'tool': spec['tool'], 'uses_model_turn': True}
