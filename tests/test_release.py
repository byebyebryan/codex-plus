import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from codex_plus import VERSION, package, release
from codex_plus.reports import VERSION as REPORT_VERSION, package as reports


class ReleaseTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.source = self.root / 'source'; self.source.mkdir()
        repo = Path(__file__).resolve().parents[1]
        for name in {*release.WORKER_FILES, *package.RUNTIME_FILES, *reports.FILES}:
            target = self.source / name; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(repo / name, target)
        self.git('init', '-q'); self.git('add', '.')
        self.git('-c', 'user.name=Release Fixture', '-c', 'user.email=fixture@example.invalid',
                 '-c', 'commit.gpgsign=false', 'commit', '-qm', 'fixture')

    def git(self, *args):
        return subprocess.check_output(['rtk', 'proxy', 'git', '-C', str(self.source), *args])

    def test_one_identity_reproducible_components_and_relocated_tool_versions(self):
        self.assertEqual(VERSION, REPORT_VERSION)
        first, second = self.root / 'first', self.root / 'second'
        result = release.build(self.source, first)
        release.build(self.source, second)
        for path in first.iterdir(): self.assertEqual(path.read_bytes(), (second / path.name).read_bytes())
        self.assertEqual(result['tag'], 'v' + VERSION)
        self.assertEqual(release.verify(first), result)
        for component, module, script in (('monitoring', package, 'codex-plus-model'), ('reporting', reports, 'codex-plus-report-mcp')):
            artifact = first / result['components'][component]['artifact']
            prefix = self.root / component
            installed = module.install(artifact, prefix, result['components'][component]['sha256'])
            module.activate(prefix, result['source_revision'])
            response = subprocess.check_output([sys.executable, '-B', str(installed / 'scripts' / script)],
                input=json.dumps({'jsonrpc': '2.0', 'id': 1, 'method': 'initialize'}) + '\n', text=True,
                cwd=self.root, env={'PATH': '/unavailable', 'PYTHONPATH': '', 'PYTHONDONTWRITEBYTECODE': '1'})
            self.assertEqual(json.loads(response)['result']['serverInfo']['version'], VERSION)
            doctor = subprocess.check_output([sys.executable, '-B', str(installed / 'scripts/codex-plus-doctor'),
                '--no-native', '--runtime-prefix', str(self.root / 'monitoring'), '--report-prefix', str(self.root / 'reporting')],
                cwd=self.root, text=True, env={'HOME': str(self.root / 'home'), 'PATH': '/unavailable', 'PYTHONPATH': ''})
            self.assertFalse(json.loads(doctor)['loaded_processes_checked'])
        self.assertEqual(release.read_workers(first / result['components']['workers']['artifact'])['version'], VERSION)

    def test_mixed_revision_paths_modified_bytes_and_checksum_file_are_rejected(self):
        output = self.root / 'release'; metadata = release.build(self.source, output)
        manifest = output / 'release.json'; original = manifest.read_bytes()
        metadata['source_revision'] = '0' * 40; manifest.write_bytes(release.encoded(metadata))
        with self.assertRaisesRegex(ValueError, 'identity'): release.verify(output)
        metadata['components']['workers']['artifact'] = '../escape'
        manifest.write_bytes(release.encoded(metadata))
        with self.assertRaisesRegex(ValueError, 'path'): release.verify(output)
        manifest.write_bytes(original)
        checksum = output / 'SHA256SUMS'; checksum.write_text('invalid')
        with self.assertRaisesRegex(ValueError, 'checksum file'): release.verify(output)
        path = output / metadata['components']['monitoring']['artifact']; path.write_bytes(path.read_bytes() + b'tampered')
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'): release.verify(output)

    def test_build_refuses_dirty_source_existing_output_and_wrong_builder_version(self):
        output = self.root / 'release'
        (self.source / 'LICENSE').write_text('uncommitted')
        with self.assertRaises(ValueError): release.build(self.source, output)
        self.assertFalse(output.exists())
        self.git('checkout', '--', 'LICENSE')
        output.mkdir()
        with self.assertRaises(FileExistsError): release.build(self.source, output)
        version_file = self.source / 'codex_plus/__init__.py'; version_file.write_text("VERSION = '99.0.0'\n")
        self.git('add', '.')
        self.git('-c', 'user.name=Release Fixture', '-c', 'user.email=fixture@example.invalid',
                 '-c', 'commit.gpgsign=false', 'commit', '-qm', 'different version')
        with self.assertRaisesRegex(ValueError, 'version differ'): release.build(self.source, self.root / 'other')


if __name__ == '__main__': unittest.main()
