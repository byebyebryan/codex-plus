import io
import json
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile
import unittest

from codex_plus.reports import package


class ReportPackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        source = Path(__file__).resolve().parents[1]
        self.content = {name: (source / name).read_bytes() for name in package.FILES}
        self.content.update(package.plugins())
        self.metadata = package.manifest(self.content, "1" * 40)

    def archive(self, extra=None, changed=None):
        content = dict(self.content); content.update(changed or {})
        content["report.json"] = json.dumps(self.metadata).encode()
        target = self.root / ("archive-" + str(len(list(self.root.glob("archive-*")))) + ".tar.gz")
        with tarfile.open(target, "w:gz") as archive:
            for name, data in content.items():
                member = tarfile.TarInfo(package.NAME + "/" + name)
                member.mode, member.size = package.mode(name), len(data)
                archive.addfile(member, io.BytesIO(data))
            if extra: archive.addfile(extra, io.BytesIO(b""))
        return target

    def test_relocated_install_publishes_without_source_native_owner_or_codex(self):
        archive = self.archive(); prefix = self.root / "relocated installation"
        release = package.install(archive, prefix, package.sha(archive.read_bytes()))
        package.activate(prefix, "1" * 40)
        source = self.root / "report.html"; source.write_text("<h1>Installed report</h1>")
        result = subprocess.run([sys.executable, "-B", str(prefix / "current/scripts/codex-plus-report"),
            "--config", str(self.root / "missing.toml"), "--data-root", str(self.root / "data"), "--json",
            "publish", "--source", str(source), "--title", "Installed report"],
            cwd=self.root, env={"PATH": "/unavailable", "PYTHONPATH": "", "PYTHONDONTWRITEBYTECODE": "1"},
            text=True, capture_output=True, timeout=5, check=True)
        self.assertEqual(json.loads(result.stdout)["publication"], "created")
        self.assertEqual(package.verify_install(release), self.metadata)
        self.assertFalse((release / "codex_plus/native.py").exists())
        config = package.mcp_config(prefix)
        response = subprocess.run([config["command"], *config["args"]],
            input=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/list"}) + "\n",
            env={"PATH": "/unavailable", "PYTHONPATH": "", "PYTHONDONTWRITEBYTECODE": "1"},
            cwd=self.root, text=True, capture_output=True, timeout=5, check=True)
        self.assertEqual(len(json.loads(response.stdout)["result"]["tools"]), 4)

    def test_previous_preview_seven_archive_remains_verifiable_and_selectable(self):
        self.content = {name: value for name, value in self.content.items()
                        if name in package.PREVIOUS_FILES}
        self.content['codex_plus/reports/__init__.py'] = b'VERSION = "0.1.0-preview.7"\n'
        self.content.update(package.plugins('0.1.0-preview.7'))
        self.metadata = package.manifest(self.content, '7' * 40)
        self.metadata['version'] = '0.1.0-preview.7'
        archive = self.archive()
        prefix = self.root / 'old'
        installed = package.install(archive, prefix)
        package.activate(prefix, '7' * 40)
        self.assertEqual(package.verify_install(installed), self.metadata)

    def test_previous_preview_eight_archive_remains_verifiable_and_selectable(self):
        self.content = {name: value for name, value in self.content.items() if name in package.PREVIEW_EIGHT_FILES}
        self.content['codex_plus/reports/__init__.py'] = b'VERSION = "0.1.0-preview.8"\n'
        self.content['codex_plus/__init__.py'] = b'VERSION = "0.1.0-preview.3"\n'
        self.content.update(package.plugins('0.1.0-preview.8'))
        self.metadata = package.manifest(self.content, '8' * 40); self.metadata['version'] = '0.1.0-preview.8'
        prefix = self.root / 'preview-eight'
        installed = package.install(self.archive(), prefix); package.activate(prefix, '8' * 40)
        self.assertEqual(package.verify_install(installed)['version'], '0.1.0-preview.8')

    def test_checksums_manifest_and_linked_members_fail_before_install(self):
        archive = self.archive()
        with self.assertRaises(ValueError): package.install(archive, self.root / "wrong", "0" * 64)
        self.assertFalse((self.root / "wrong").exists())
        with self.assertRaises(ValueError): package.read_archive(self.archive(changed={"LICENSE": b"different"}))
        for name, kind in (("../escape", tarfile.REGTYPE), ("scripts/codex-plus-report", tarfile.SYMTYPE), ("LICENSE", tarfile.REGTYPE)):
            member = tarfile.TarInfo(package.NAME + "/" + name); member.type = kind; member.linkname = "/tmp/escape"
            with self.assertRaises(ValueError): package.read_archive(self.archive(extra=member))

    def test_selected_release_is_verified_and_old_path_survives_selection(self):
        archive = self.archive(); prefix = self.root / "installed"
        release = package.install(archive, prefix); package.activate(prefix, "1" * 40)
        captured = (prefix / "current/scripts/codex-plus-report").resolve()
        self.assertEqual(captured.parents[1], release)
        (release / "LICENSE").write_text("modified")
        with self.assertRaises(ValueError): package.install(archive, prefix)
        with self.assertRaises(ValueError): package.activate(prefix, "1" * 40)
        self.assertTrue(captured.exists())

    def test_disabled_mcp_configuration_needs_no_installation(self):
        value = package.mcp_config(self.root / "missing", enabled=False)
        self.assertFalse(value["enabled"])
        self.assertFalse((self.root / "missing").exists())

    def test_artifact_build_is_reproducible_and_rejects_dirty_source(self):
        repo = self.root / "source"; repo.mkdir()
        for name in package.FILES:
            target = repo / name; target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(self.content[name])
        def git(*args):
            subprocess.run(["git", "-C", str(repo), *args], check=True, capture_output=True)
        git("init", "-q"); git("add", ".")
        git("-c", "user.name=Report Test", "-c", "user.email=report-test@example.invalid", "commit", "-qm", "fixture")
        first = self.root / "one.tar.gz"; second = self.root / "two.tar.gz"
        package.build(repo, first); package.build(repo, second)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        (repo / "LICENSE").write_text("dirty")
        with self.assertRaises(ValueError): package.build(repo, self.root / "dirty.tar.gz")


if __name__ == "__main__": unittest.main()
