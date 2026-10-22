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
        class Unloaded(Native):
            def bind(self, *args, **kwargs): raise RpcError('not loaded')
            def call(self, *args, **kwargs): raise AssertionError('unloaded thread queried')
        self.assertEqual(doctor.loaded_mcp('/fixture/socket', A, components, client_factory=Unloaded)['state'], 'unavailable')
        def forbidden(*args, **kwargs): raise AssertionError('connected without valid caller')
        self.assertEqual(doctor.loaded_mcp('/fixture/socket', None, components, client_factory=forbidden)['state'], 'not_checked')
        self.assertEqual(doctor.loaded_mcp('/fixture/socket', 'invalid', components, client_factory=forbidden)['state'], 'unavailable')

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


if __name__ == '__main__': unittest.main()
