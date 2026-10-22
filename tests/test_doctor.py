import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from codex_plus import doctor, package


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
        result = doctor.diagnose(check_native=False, run=forbidden)
        self.assertEqual(result['native']['state'], 'not_checked')
        self.assertEqual({row['state'] for row in result['components'].values()}, {'not_installed'})
        self.assertFalse(result['loaded_processes_checked'])
        self.assertFalse((self.root / 'home').exists())

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
