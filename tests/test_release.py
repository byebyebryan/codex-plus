import json
import posixpath
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tarfile
import tomllib
import unittest
from urllib.parse import unquote, urlsplit

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

    def test_worker_archive_carries_exact_native_role_pins_and_explicit_invocation_metadata(self):
        output = self.root / 'release'; result = release.build(self.source, output)
        path = output / result['components']['workers']['artifact']
        expected = {'luna-max': ('gpt-6-luna', 'max'),
                    'sol-xhigh': ('gpt-6.1-sol', 'xhigh'),
                    'astra-xhigh': ('gpt-6-astra', 'xhigh')}
        with tarfile.open(path, 'r:gz') as archive:
            for role, (model, effort) in expected.items():
                member = 'codex-plus-workers/agents/' + role + '.toml'
                data = archive.extractfile(member).read()
                selection = tomllib.loads(data.decode())
                self.assertEqual(selection['name'], role)
                self.assertEqual((selection['model'], selection['model_reasoning_effort']), (model, effort))
                self.assertEqual(data, (self.source / 'agents' / (role + '.toml')).read_bytes())
            # Packaging preserves native activation settings and exact skill bytes,
            # independently of any prose used to describe routing.
            for skill in ('luna-task', 'luna-goal-loop', 'adaptive-task', 'adaptive-goal-loop',
                          'worker-task', 'worker-goal-loop'):
                for file in ('SKILL.md', 'agents/openai.yaml'):
                    name = 'skills/' + skill + '/' + file
                    self.assertEqual(archive.extractfile('codex-plus-workers/' + name).read(),
                                     (self.source / name).read_bytes())
        self.assertIn('agents/astra-xhigh.toml', release.read_workers(path)['files'])

    def test_reporting_only_primary_selection_is_structured_without_monitoring_or_owner(self):
        output = self.root / 'release'; result = release.build(self.source, output)
        component = result['components']['reporting']
        installed = reports.install(output / component['artifact'], self.root / 'report-only', component['sha256'])
        self.assertFalse((installed / 'codex_plus/native.py').exists())
        environment = {'PATH': '/unavailable', 'PYTHONPATH': '', 'PYTHONDONTWRITEBYTECODE': '1',
                       'CODEX_HOME': str(self.root / 'absent-native-home'),
                       'XDG_CONFIG_HOME': str(self.root / 'config')}
        script = installed / 'scripts/codex-plus-context'
        paths = subprocess.run([sys.executable, '-B', str(script)], cwd=self.root,
                               env=environment, capture_output=True, text=True)
        self.assertEqual(paths.returncode, 0, paths.stderr)
        self.assertFalse(json.loads(paths.stdout)['daemon_checked'])
        for caller, reason in (('', 'caller_thread_unavailable'),
                               ('01a00000-0000-7000-8000-000000000001', 'native_component_unavailable')):
            with self.subTest(caller=bool(caller)):
                primary = subprocess.run([sys.executable, '-B', str(script), '--primary'], cwd=self.root,
                    env={**environment, 'CODEX_THREAD_ID': caller}, capture_output=True, text=True)
                self.assertEqual(primary.returncode, 0, primary.stderr)
                self.assertEqual(primary.stderr, '')
                self.assertEqual(json.loads(primary.stdout), {'status': 'unknown',
                    'source': 'loaded_thread_configuration', 'execution_verified': False, 'reason': reason})
        self.assertFalse((self.root / 'absent-native-home').exists())

    def test_worker_archive_relative_document_links_resolve_inside_the_artifact(self):
        output = self.root / 'release'; result = release.build(self.source, output)
        with tarfile.open(output / result['components']['workers']['artifact'], 'r:gz') as archive:
            prefix = 'codex-plus-workers/'
            content = {member.name.removeprefix(prefix): archive.extractfile(member).read()
                       for member in archive if member.isfile()}
        self.assertIn('docs/worker-escalation-results.md', set(content))
        links = 0
        for name, data in content.items():
            if not name.endswith('.md'):
                continue
            for target in re.findall(r'\]\(([^)\s]+)\)', data.decode()):
                url = urlsplit(target)
                if url.scheme or url.netloc or not url.path:
                    continue
                resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(url.path)))
                with self.subTest(document=name, target=target):
                    self.assertIn(resolved, set(content))
                links += 1
        self.assertGreater(links, 0)

    def test_relocated_compatibility_entries_resolve_to_canonical_workflows(self):
        output = self.root / 'release'; result = release.build(self.source, output)
        relocated = self.root / 'relocated' / 'workers'
        with tarfile.open(output / result['components']['workers']['artifact'], 'r:gz') as archive:
            for member in archive:
                relative = member.name.removeprefix('codex-plus-workers/')
                destination = relocated / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(archive.extractfile(member).read())
        for old, canonical in (('worker-task', 'adaptive-task'),
                               ('worker-goal-loop', 'adaptive-goal-loop')):
            entry = relocated / 'skills' / old / 'SKILL.md'
            targets = re.findall(r'\]\(([^)\s]+)\)', entry.read_text())
            self.assertEqual(len(targets), 1)
            target = (entry.parent / unquote(urlsplit(targets[0]).path)).resolve()
            self.assertTrue(target.is_relative_to(relocated))
            self.assertEqual(target, relocated / 'skills' / canonical / 'SKILL.md')
            self.assertRegex(target.read_text(), rf'(?m)^name: {canonical}$')
            self.assertEqual(target.read_bytes(),
                             (self.source / 'skills' / canonical / 'SKILL.md').read_bytes())

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
