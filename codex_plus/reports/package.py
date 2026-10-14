"""Reproducible report-component artifacts and immutable isolated installations."""

from __future__ import annotations

import argparse
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import uuid

from . import VERSION
from .store import no_links


NAME = "codex-plus-report"
FILES = (
    "LICENSE", "codex_plus/__init__.py", "codex_plus/reports/__init__.py",
    "codex_plus/reports/config.py", "codex_plus/reports/catalog.py",
    "codex_plus/reports/store.py", "codex_plus/reports/hosting.py",
    "codex_plus/reports/cli.py", "codex_plus/reports/mcp.py", "codex_plus/reports/package.py", "codex_plus/reports/server.py",
    "scripts/codex-plus-report", "scripts/codex-plus-report-mcp", "scripts/codex-plus-report-package", "scripts/code-report-server",
    "skills/html-report/SKILL.md", "skills/html-report/agents/openai.yaml",
)
COMPATIBILITY = {"os": "linux", "python": ">=3.11", "agent_owner": "not required",
                 "hosting": "configured static HTTP/HTTPS endpoint", "server_control": "optional tmux >=2.9"}
MAX_FILE = 2 * 1024 * 1024
MAX_ARCHIVE = 8 * 1024 * 1024


def sha(data): return hashlib.sha256(data).hexdigest()


def revision(value):
    if not isinstance(value, str) or not re.fullmatch(r"[0-9a-f]{40}", value):
        raise ValueError("a full committed source revision is required")
    return value


def mode(name): return 0o755 if name.startswith("scripts/") else 0o644


def plugins():
    portable = {"$schema": "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json",
                "name": "html-report", "version": VERSION,
                "description": "Static HTML report presentation with the installed codex-plus-report component."}
    legacy = {"name": "html-report", "version": VERSION,
              "description": portable["description"], "skills": "./skills/"}
    return {"plugin.json": (json.dumps(portable, indent=2) + "\n").encode(),
            ".codex-plugin/plugin.json": (json.dumps(legacy, indent=2) + "\n").encode()}


def manifest(files, source_revision):
    return {"schema": 1, "name": NAME, "version": VERSION,
            "source_revision": revision(source_revision), "compatibility": COMPATIBILITY,
            "files": {name: {"sha256": sha(data), "mode": mode(name)} for name, data in sorted(files.items())}}


def git(root, *args):
    return subprocess.check_output(["rtk", "proxy", "git", "-C", str(root), *args])


def build(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    if output.is_relative_to(root): raise ValueError("write artifacts outside the source checkout")
    if git(root, "status", "--porcelain", "--untracked-files=all").strip():
        raise ValueError("report package build requires a clean committed checkout")
    source_revision = git(root, "rev-parse", "HEAD").decode().strip()
    content = {name: git(root, "show", source_revision + ":" + name) for name in FILES}
    content.update(plugins())
    metadata = manifest(content, source_revision)
    content["report.json"] = (json.dumps(metadata, sort_keys=True, indent=2) + "\n").encode()
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as destination:
        with gzip.GzipFile(filename="", fileobj=destination, mode="wb", mtime=0) as compressed:
            with tarfile.open(fileobj=compressed, mode="w", format=tarfile.USTAR_FORMAT) as archive:
                for name, data in sorted(content.items()):
                    member = tarfile.TarInfo(NAME + "/" + name)
                    member.size, member.mode, member.mtime = len(data), mode(name), 0
                    archive.addfile(member, io.BytesIO(data))
    return {**metadata, "artifact_sha256": sha(output.read_bytes())}


def validate(metadata, content, modes):
    if (not isinstance(metadata, dict)
            or set(metadata) != {"schema", "name", "version", "source_revision", "compatibility", "files"}
            or metadata["schema"] != 1 or metadata["name"] != NAME or metadata["version"] != VERSION
            or metadata["compatibility"] != COMPATIBILITY):
        raise ValueError("unsupported report package manifest/compatibility")
    revision(metadata["source_revision"])
    if set(content) != {*FILES, *plugins()} or set(metadata["files"]) != set(content):
        raise ValueError("report package inventory differs")
    for name, data in content.items():
        if metadata["files"][name] != {"sha256": sha(data), "mode": mode(name)} or modes[name] != mode(name):
            raise ValueError("report package content/mode mismatch: " + name)
    if any(content[name] != data for name, data in plugins().items()):
        raise ValueError("report plugin manifests differ from the component")
    return metadata


def read_archive(path, expected_sha=None):
    path = Path(path)
    if path.stat().st_size > MAX_ARCHIVE: raise ValueError("report archive exceeds size bound")
    payload = path.read_bytes()
    if expected_sha and sha(payload) != expected_sha: raise ValueError("report archive checksum mismatch")
    content, modes = {}, {}
    allowed = {*FILES, *plugins(), "report.json"}
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
        for member in archive:
            prefix = NAME + "/"
            if not member.name.startswith(prefix): raise ValueError("invalid report archive root")
            name = member.name[len(prefix):]
            if (name not in allowed or name in content or not member.isfile()
                    or not 0 <= member.size <= MAX_FILE):
                raise ValueError("unexpected, duplicate, linked or oversized report archive member")
            with archive.extractfile(member) as stream:
                content[name] = stream.read(MAX_FILE + 1)
            if len(content[name]) != member.size: raise ValueError("report member size differs")
            modes[name] = member.mode
    if "report.json" not in content or modes.pop("report.json") != 0o644:
        raise ValueError("report package manifest is missing or unsafe")
    metadata = json.loads(content.pop("report.json"))
    validate(metadata, content, modes)
    return metadata, content


def verify_install(root):
    root = Path(root); no_links(root)
    if not root.is_dir(): raise ValueError("report release directory is missing")
    paths = [p for p in root.rglob("*") if not p.is_dir() or p.is_symlink()]
    if any(p.is_symlink() for p in paths) or {p.relative_to(root).as_posix() for p in paths} != {*FILES, *plugins(), "report.json"}:
        raise ValueError("installed report inventory differs")
    content = {name: (root / name).read_bytes() for name in (*FILES, *plugins())}
    modes = {name: stat.S_IMODE((root / name).stat().st_mode) for name in content}
    if stat.S_IMODE((root / "report.json").stat().st_mode) != 0o644:
        raise ValueError("installed report manifest mode differs")
    return validate(json.loads((root / "report.json").read_text()), content, modes)


def prefix_path(prefix, create=False):
    prefix = Path(prefix)
    if not prefix.is_absolute(): raise ValueError("an absolute report installation prefix is required")
    no_links(prefix)
    if create: prefix.mkdir(parents=True, mode=0o755, exist_ok=True)
    if not prefix.is_dir() or prefix.stat().st_uid != os.getuid() or prefix.stat().st_mode & 0o022:
        raise ValueError("report install prefix must be owned and not writable by others")
    return prefix


def install(archive, prefix, expected_sha=None):
    metadata, content = read_archive(archive, expected_sha)
    prefix = prefix_path(prefix, True); releases = prefix / "releases"
    no_links(releases); releases.mkdir(mode=0o755, exist_ok=True)
    prefix_path(releases)
    target = releases / metadata["source_revision"]
    if target.exists() or target.is_symlink():
        if verify_install(target) != metadata: raise ValueError("immutable report release has different bytes")
        return target
    temporary = Path(tempfile.mkdtemp(prefix=".install-", dir=releases))
    try:
        for name, data in content.items():
            destination = temporary / name; destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data); destination.chmod(mode(name))
        (temporary / "report.json").write_text(json.dumps(metadata, sort_keys=True, indent=2) + "\n")
        (temporary / "report.json").chmod(0o644)
        verify_install(temporary); temporary.rename(target)
    finally:
        if temporary.exists(): shutil.rmtree(temporary)
    return target


def activate(prefix, source_revision):
    prefix = prefix_path(prefix); target = prefix / "releases" / revision(source_revision)
    verify_install(target)
    current = prefix / "current"
    if current.exists() and not current.is_symlink(): raise ValueError("report selection must be a managed symlink")
    temporary = prefix / (".current-" + uuid.uuid4().hex)
    try:
        temporary.symlink_to("releases/" + source_revision); temporary.replace(current)
    finally: temporary.unlink(missing_ok=True)
    return target


def mcp_config(prefix, config=None, *, enabled=True):
    prefix = Path(prefix)
    if not prefix.is_absolute(): raise ValueError("an absolute report install prefix is required")
    if enabled: verify_install((prefix / "current").resolve(strict=True))
    args = ["-B", str(prefix / "current/scripts/codex-plus-report-mcp")]
    if config is not None:
        if not Path(config).is_absolute(): raise ValueError("an absolute report config path is required")
        args += ["--config", str(config)]
    return {"command": sys.executable, "args": args, "enabled": enabled, "required": False,
            "default_tools_approval_mode": "writes"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    make = commands.add_parser("build"); make.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[2]); make.add_argument("--output", type=Path, required=True)
    verify = commands.add_parser("verify"); verify.add_argument("archive", type=Path); verify.add_argument("--sha256")
    put = commands.add_parser("install"); put.add_argument("archive", type=Path); put.add_argument("--prefix", type=Path, required=True); put.add_argument("--sha256")
    select = commands.add_parser("activate"); select.add_argument("--prefix", type=Path, required=True); select.add_argument("--revision", required=True)
    installed = commands.add_parser("verify-install"); installed.add_argument("root", type=Path)
    config = commands.add_parser("mcp-config"); config.add_argument("--prefix", type=Path, required=True); config.add_argument("--config", type=Path); config.add_argument("--disabled", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "build": result = build(args.source, args.output)
        elif args.command == "verify": result = {**read_archive(args.archive, args.sha256)[0], "artifact_sha256": sha(Path(args.archive).read_bytes())}
        elif args.command == "install": result = {"installed": str(install(args.archive, args.prefix, args.sha256))}
        elif args.command == "activate": result = {"selected": str(activate(args.prefix, args.revision))}
        elif args.command == "verify-install": result = verify_install(args.root)
        else: result = {"mcp_servers": {"html_report": mcp_config(args.prefix, args.config, enabled=not args.disabled)}}
        print(json.dumps(result, indent=2)); return 0
    except (OSError, ValueError, TypeError, KeyError, subprocess.SubprocessError, tarfile.TarError) as error:
        print(json.dumps({"error": str(error)[:1024]}), file=sys.stderr); return 1
