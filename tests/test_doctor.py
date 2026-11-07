from contextlib import redirect_stdout
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from codex_plus import doctor, package
from codex_plus.native import RpcError
from test_peers import A


class DoctorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        env = {key: value for key, value in os.environ.items() if not key.startswith(('CODEX_', 'XDG_'))}
        env['HOME'] = str(self.root / 'home')
        self.patch = patch.dict(os.environ, env, clear=True)
        self.patch.start(); self.addCleanup(self.patch.stop)

    def test_missing_install_is_readonly_and_does_not_query_native_when_disabled(self):
        def forbidden(*args, **kwargs): raise AssertionError('native command executed')
        result = doctor.diagnose(check_native=False, thread=A, run=forbidden, client_factory=forbidden)
        self.assertEqual(result['native']['state'], 'not_checked')
        self.assertEqual({row['state'] for row in result['components'].values()}, {'not_installed'})
        self.assertFalse(result['loaded_processes_checked'])
        self.assertFalse((self.root / 'home').exists())

    def test_loaded_mcp_versions_use_native_metadata_without_resume_or_configuration_details(self):
        calls = []
        class Native:
            def __init__(self, requested, **kwargs): calls.append(('connect', requested))
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def bind(self, identity, **kwargs): calls.append(('bind', identity))
            def call(self, method, params, **kwargs):
                calls.append((method, params))
                version = 'old-preview' if params['serverName'] == 'codex_plus' else 'current-preview'
                return {'data': [{'name': params['serverName'], 'runtimeStatus': 'connected',
                    'serverInfo': {'version': version, 'websiteUrl': 'must-never-appear'},
                    'tools': {'private_arguments': 'must-never-appear'}}]}
        components = {name: {'version': 'current-preview'} for name in ('monitoring', 'reporting')}
        result = doctor.loaded_mcp('/fixture/socket', A, components, client_factory=Native)
        self.assertEqual(result['state'], 'reported')
        self.assertEqual(result['servers']['codex_plus']['version_alignment'], 'different_reported_version')
        self.assertEqual(result['servers']['codex_plus']['diagnostic']['reason'], 'reported_version_differs_from_selected')
        self.assertTrue(result['servers']['codex_plus']['diagnostic']['action'])
        self.assertEqual(result['servers']['html_report']['version_alignment'], 'same_reported_version')
        self.assertNotIn('must-never-appear', json.dumps(result))
        self.assertEqual([method for method, _ in calls], ['connect', 'bind', 'mcpServerStatus/list', 'mcpServerStatus/list'])

    def test_loaded_mcp_missing_metadata_and_unloaded_thread_remain_unknown(self):
        class Native:
            def __init__(self, *args, **kwargs): pass
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def bind(self, *args, **kwargs): pass
            def call(self, method, params, **kwargs):
                return {'data': [{'name': params['serverName'], 'runtimeStatus': 'connected'}]}
        components = {name: {} for name in ('monitoring', 'reporting')}
        result = doctor.loaded_mcp('/fixture/socket', A, components, client_factory=Native)
        self.assertIsNone(result['servers']['codex_plus']['reported_version'])
        self.assertEqual(result['servers']['codex_plus']['version_alignment'], 'unknown')
        self.assertEqual(result['servers']['codex_plus']['diagnostic']['reason'], 'reported_server_version_unavailable')
        class Unloaded(Native):
            def bind(self, *args, **kwargs): raise RpcError('target not positively present in loaded inventory')
            def call(self, *args, **kwargs): raise AssertionError('unloaded thread queried')
        unloaded = doctor.loaded_mcp('/fixture/socket', A, components, client_factory=Unloaded)
        self.assertEqual(unloaded['state'], 'unavailable')
        self.assertEqual(unloaded['diagnostic']['reason'], 'requested_conversation_not_positively_loaded')
        self.assertIn('launch and endpoint options', unloaded['diagnostic']['action'])
        self.assertNotIn(A, json.dumps(unloaded))
        def forbidden(*args, **kwargs): raise AssertionError('connected without valid caller')
        self.assertEqual(doctor.loaded_mcp('/fixture/socket', None, components, client_factory=forbidden)['state'], 'not_checked')
        self.assertEqual(doctor.loaded_mcp('/fixture/socket', 'invalid', components, client_factory=forbidden)['state'], 'unavailable')

    def test_endpoint_missing_unresponsive_and_rpc_failures_have_safe_distinct_diagnoses(self):
        components = {name: {'version': 'preview'} for name in ('monitoring', 'reporting')}
        def missing(*args, **kwargs): raise FileNotFoundError('/private/native/socket')
        result = doctor.loaded_mcp('/private/native/socket', A, components, client_factory=missing)
        self.assertEqual(result['diagnostic']['reason'], 'native_endpoint_missing')
        self.assertEqual(result['detail'], 'FileNotFoundError')
        self.assertNotIn('/private/native/socket', json.dumps(result))

        existing_endpoint = self.root / 'native.sock'
        existing_endpoint.touch()
        def missing_proof(*args, **kwargs): raise FileNotFoundError('/proc/net/unix')
        result = doctor.loaded_mcp(str(existing_endpoint), A, components, client_factory=missing_proof)
        self.assertEqual(result['diagnostic']['reason'], 'native_endpoint_unverified')
        self.assertNotIn('/proc/net/unix', json.dumps(result))

        def refused(*args, **kwargs): raise ConnectionRefusedError('private endpoint detail')
        result = doctor.loaded_mcp('/private/native/socket', A, components, client_factory=refused)
        self.assertEqual(result['diagnostic']['reason'], 'native_endpoint_unresponsive')
        self.assertNotIn('private endpoint detail', json.dumps(result))

        class BrokenInventory:
            def __init__(self, *args, **kwargs): pass
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def bind(self, *args, **kwargs): raise RpcError('PRIVATE\n' + A + ' secret response')
        result = doctor.loaded_mcp('/fixture/socket', A, components, client_factory=BrokenInventory)
        self.assertEqual(result['diagnostic']['reason'], 'loaded_inventory_rpc_failed')
        self.assertNotIn('PRIVATE', json.dumps(result))
        self.assertNotIn(A, json.dumps(result))

        class BrokenStatus(BrokenInventory):
            def bind(self, *args, **kwargs): pass
            def call(self, *args, **kwargs): raise RpcError('PRIVATE status response')
        result = doctor.loaded_mcp('/fixture/socket', A, components, client_factory=BrokenStatus)
        self.assertEqual(result['diagnostic']['reason'], 'mcp_status_rpc_failed')
        self.assertNotIn('PRIVATE', json.dumps(result))

    def test_disconnected_and_missing_server_rows_report_reason_and_action(self):
        class Native:
            def __init__(self, *args, **kwargs): pass
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def bind(self, *args, **kwargs): pass
            def call(self, method, params, **kwargs):
                if params['serverName'] == 'codex_plus':
                    return {'data': [{'name': 'codex_plus', 'runtimeStatus': 'disconnected',
                                      'serverInfo': {'version': 'preview'}}]}
                return {'data': []}
        components = {name: {'version': 'preview'} for name in ('monitoring', 'reporting')}
        result = doctor.loaded_mcp('/fixture/socket', A, components, client_factory=Native)
        self.assertEqual(result['servers']['codex_plus']['state'], 'disconnected')
        self.assertEqual(result['servers']['codex_plus']['version_alignment'], 'unknown')
        self.assertEqual(result['servers']['codex_plus']['diagnostic']['reason'], 'server_not_connected')
        self.assertTrue(result['servers']['codex_plus']['diagnostic']['action'])
        self.assertEqual(result['servers']['html_report']['state'], 'not_reported')
        self.assertEqual(result['servers']['html_report']['diagnostic']['reason'], 'server_metadata_unavailable')

    def test_disconnected_cached_version_and_malformed_owner_status_are_not_loaded_proof(self):
        class Native:
            def __init__(self, *args, **kwargs): pass
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def bind(self, *args, **kwargs): pass
            def call(self, method, params, **kwargs):
                return {'data': [{'name': params['serverName'], 'runtimeStatus': 'disconnected',
                                  'serverInfo': {'version': 'preview'}}]}
        components = {name: {'version': 'preview'} for name in ('monitoring', 'reporting')}
        result = doctor.loaded_mcp('/fixture/socket', A, components, client_factory=Native)
        self.assertEqual(result['servers']['codex_plus']['version_alignment'], 'unknown')
        def malformed(argv, **kwargs):
            return subprocess.CompletedProcess(argv, 0, 'null')
        self.assertEqual(doctor.diagnose(run=malformed)['native']['owner_status']['state'], 'unavailable')

    def test_version_evidence_and_managed_path_overrides_do_not_expose_credentials(self):
        home = self.root / 'home/.codex'; home.mkdir(parents=True)
        private_state = str(self.root / 'selected-state')
        config = home / 'config.toml'
        config.write_text('[mcp_servers.codex_plus]\nenabled=true\nargs=["--state-root",' + json.dumps(private_state) +
                          ']\nenv={SECRET="must never appear"}\n[mcp_servers.html_report]\nenabled=false\n')
        calls = []
        def run(argv, **kwargs):
            calls.append(argv)
            output = 'codex-cli 0.163.0' if argv[-1] == '--version' else json.dumps({'status': 'running', 'appServerVersion': '0.163.0'})
            return subprocess.CompletedProcess(argv, 0, output)
        result = doctor.diagnose(run=run)
        self.assertEqual(result['environment']['state_root'], private_state)
        self.assertEqual(result['native']['client_version'], '0.163.0')
        self.assertEqual(result['native']['owner_status']['appServerVersion'], '0.163.0')
        self.assertEqual(result['native']['qualification'], 'not_established')
        self.assertTrue(result['mcp_configuration']['codex_plus']['enabled'])
        self.assertFalse(result['mcp_configuration']['html_report']['enabled'])
        summary = doctor.format_human(result)
        self.assertIn('codex_plus: enabled', summary)
        self.assertIn('html_report: disabled', summary)
        self.assertNotIn('must never appear', json.dumps(result))
        self.assertEqual(calls, [['rtk', 'proxy', 'codex', '--version'], ['rtk', 'proxy', 'codex', 'app-server', 'daemon', 'version']])
        self.assertFalse(Path(private_state).exists())

    def test_selected_manifest_integrity_mixed_legacy_versions_and_tampering(self):
        # Reuse archive fixtures, never import or start a selected runtime.
        from test_package import PackageTests
        from test_report_package import ReportPackageTests
        runtime = PackageTests(); runtime.setUp(); self.addCleanup(runtime.doCleanups)
        report = ReportPackageTests(); report.setUp(); self.addCleanup(report.doCleanups)
        runtime_prefix, report_prefix = self.root / 'runtime', self.root / 'reports'
        installed = package.install(runtime.archive(), runtime_prefix)
        package.activate(runtime_prefix, '1' * 40)
        from codex_plus.reports import package as reports
        reports.install(report.archive(), report_prefix); reports.activate(report_prefix, '1' * 40)
        result = doctor.diagnose(runtime_prefix=runtime_prefix, report_prefix=report_prefix, check_native=False)
        self.assertEqual(result['release_alignment'], 'aligned')
        self.assertEqual(result['components']['monitoring']['state'], 'manifest_verified')
        metadata = installed / 'runtime.json'; value = json.loads(metadata.read_text()); value['version'] = 'legacy-preview'
        metadata.write_text(json.dumps(value))
        self.assertEqual(doctor.diagnose(runtime_prefix=runtime_prefix, report_prefix=report_prefix, check_native=False)['release_alignment'], 'mixed')
        (installed / 'LICENSE').write_text('tampered')
        self.assertEqual(doctor.diagnose(runtime_prefix=runtime_prefix, check_native=False)['components']['monitoring']['state'], 'invalid')

    def test_invalid_configuration_and_unavailable_native_are_visible(self):
        home = self.root / 'home/.codex'; home.mkdir(parents=True)
        (home / 'config.toml').write_text('mcp_servers={codex_plus="invalid"}')
        def missing(*args, **kwargs): raise FileNotFoundError('no codex')
        result = doctor.diagnose(run=missing)
        self.assertEqual(result['config_state'], 'unreadable_or_invalid')
        self.assertEqual(result['native']['client_version'], 'unavailable')

    def test_human_output_keeps_alternate_environment_and_missing_evidence_explicit(self):
        alternate = self.root / 'work'
        with patch.dict(os.environ, {'CODEX_HOME': str(alternate)}):
            result = doctor.diagnose(check_native=False)
        summary = doctor.format_human(result)
        self.assertIn('Codex home: ' + str(alternate), summary)
        self.assertIn(result['environment']['state_root'], summary)
        self.assertIn('Selected components: unknown', summary)
        self.assertIn('not installed', summary)
        self.assertIn('Native: not checked', summary)
        self.assertIn('Loaded MCP metadata: not checked', summary)
        self.assertIn('do not prove', summary)
        self.assertFalse(alternate.exists())

    def test_human_output_distinguishes_mixed_invalid_and_reported_version_evidence(self):
        result = doctor.diagnose(check_native=False)
        result['release_alignment'] = 'mixed'
        result['components']['workers'].update(state='manifest_verified', version='one', source_revision='1' * 40)
        result['components']['monitoring'].update(state='invalid', detail='payload differs')
        result['loaded_mcp'] = {'state': 'reported', 'servers': {
            'codex_plus': {'state': 'connected', 'reported_version': 'one', 'selected_version': 'two',
                           'version_alignment': 'different_reported_version'},
            'html_report': {'state': 'connected', 'reported_version': None, 'selected_version': 'two',
                           'version_alignment': 'unknown'}}}
        summary = doctor.format_human(result)
        self.assertIn('Selected components: mixed', summary)
        self.assertIn('workers: one; manifest verified', summary)
        self.assertIn('monitoring: invalid', summary)
        self.assertIn('payload differs', summary)
        self.assertIn('reported one; selected two; different reported version', summary)
        self.assertIn('reported unknown; selected two; unknown', summary)

    def test_human_native_output_does_not_upgrade_unavailable_or_unqualified_evidence(self):
        def missing(*args, **kwargs): raise FileNotFoundError('no codex')
        result = doctor.diagnose(run=missing)
        summary = doctor.format_human(result)
        self.assertIn('Native client: unavailable', summary)
        self.assertIn('Native owner: unknown (unknown)', summary)
        self.assertIn('Client qualification: not established', summary)
        result['native'].update(client_version='0.166.0', qualified_version='0.162.1',
                                owner_status={'status': 'running', 'appServerVersion': '0.166.0'})
        summary = doctor.format_human(result)
        self.assertIn('Native client: 0.166.0', summary)
        self.assertIn('Native owner: 0.166.0 (running)', summary)
        self.assertIn('Recorded qualification baseline: 0.162.1', summary)
        self.assertIn('Client qualification: not established', summary)
        self.assertNotIn('version matches', summary)

    def test_human_and_default_cli_preserve_json_data_and_exit_status(self):
        result = doctor.diagnose(check_native=False)
        for invalid in (False, True):
            result['config_state'] = 'unreadable_or_invalid' if invalid else 'missing'
            for human in (False, True):
                with self.subTest(invalid=invalid, human=human), patch.object(doctor, 'diagnose', return_value=result) as diagnose:
                    output = io.StringIO()
                    with redirect_stdout(output):
                        code = doctor.main(['--no-native', *(['--human'] if human else [])])
                    self.assertEqual(code, int(invalid))
                    self.assertEqual(diagnose.call_args.kwargs['check_native'], False)
                    self.assertNotIn('human', diagnose.call_args.kwargs)
                    if human: self.assertIn(result['config_state'], output.getvalue())
                    else: self.assertEqual(json.loads(output.getvalue()), result)
        for human in (False, True):
            result['config_state'] = 'missing'
            result['components']['monitoring']['state'] = 'invalid'
            with patch.object(doctor, 'diagnose', return_value=result), redirect_stdout(io.StringIO()):
                self.assertEqual(doctor.main(['--human'] if human else []), 1)
            with patch.object(doctor, 'diagnose', side_effect=ValueError('bad path')):
                output = io.StringIO()
                with redirect_stdout(output):
                    self.assertEqual(doctor.main(['--human'] if human else []), 1)
                if human: self.assertIn('ERROR: bad path', output.getvalue())
                else: self.assertEqual(json.loads(output.getvalue()), {'error': 'bad path'})

    def test_human_metadata_cannot_add_lines_or_terminal_controls(self):
        result = doctor.diagnose(check_native=False)
        result['components']['workers'].update(state='manifest_verified', version='one\n\x1b[31m', source_revision='1' * 40)
        summary = doctor.format_human(result)
        self.assertIn(r'workers: one\x0a\x1b[31m; manifest verified', summary)
        self.assertNotIn('\x1b', summary)

    def test_loaded_status_probe_uses_only_read_only_inventory_and_mcp_metadata_calls(self):
        home = self.root / 'home/.codex'; home.mkdir(parents=True)
        config_path = home / 'config.toml'
        original = '[mcp_servers.codex_plus]\nenabled=true\n'
        config_path.write_text(original)
        calls = []
        commands = []
        class Native:
            def __init__(self, requested, **kwargs):
                calls.append(('connect', requested, kwargs))
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def bind(self, identity, **kwargs):
                calls.append(('thread/loaded/list', identity))
            def call(self, method, params, **kwargs):
                if method != 'mcpServerStatus/list':
                    raise AssertionError('non-diagnostic RPC submitted')
                calls.append((method, params, kwargs))
                return {'data': [{'name': params['serverName'], 'runtimeStatus': 'connected',
                                  'serverInfo': {'version': 'preview'}}]}
        def run(argv, **kwargs):
            commands.append(argv)
            output = 'codex-cli 0.163.0' if argv[-1] == '--version' else json.dumps({
                'status': 'running', 'appServerVersion': '0.163.0', 'socketPath': '/fixture/native.sock'})
            return subprocess.CompletedProcess(argv, 0, output)
        state_root = self.root / 'state-that-must-not-be-created'
        result = doctor.diagnose(thread=A, state_root=state_root, run=run,
                                 client_factory=Native)
        self.assertEqual(result['loaded_mcp']['state'], 'reported')
        self.assertEqual([row[0] for row in calls], [
            'connect', 'thread/loaded/list', 'mcpServerStatus/list', 'mcpServerStatus/list'])
        self.assertTrue(all(row[1]['threadId'] == A for row in calls if row[0] == 'mcpServerStatus/list'))
        self.assertEqual(commands, [
            ['rtk', 'proxy', 'codex', '--version'],
            ['rtk', 'proxy', 'codex', 'app-server', 'daemon', 'version']])
        self.assertEqual(config_path.read_text(), original)
        self.assertFalse(state_root.exists())
        self.assertNotIn('resume', json.dumps(calls).lower())
        self.assertNotIn('reload', json.dumps(calls).lower())

    def test_loaded_diagnostic_human_text_is_bounded_and_terminal_safe(self):
        class Native:
            def __init__(self, *args, **kwargs): pass
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def bind(self, *args, **kwargs): pass
            def call(self, method, params, **kwargs):
                return {'data': [{'name': params['serverName'], 'runtimeStatus': 'connected',
                                  'serverInfo': {'version': 'old\nINJECTED\x1b[31m'}}]}
        components = {name: {'version': 'selected'} for name in ('monitoring', 'reporting')}
        loaded = doctor.loaded_mcp('/fixture/socket', A, components, client_factory=Native)
        result = doctor.diagnose(check_native=False)
        result['loaded_mcp'] = loaded
        summary = doctor.format_human(result)
        self.assertIn(r'reported old\x0aINJECTED\x1b[31m', summary)
        self.assertNotIn('\x1b', summary)
        self.assertNotIn('\nINJECTED', summary)
        self.assertEqual(len(doctor.human_text('x' * 2000)), 512)
        self.assertNotIn(A, summary)


if __name__ == '__main__': unittest.main()
