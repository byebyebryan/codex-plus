"""One reproducible release for workers, monitoring and reporting."""
from __future__ import annotations

import argparse
import ast
import gzip
import io
import json
from pathlib import Path
import tarfile

from . import VERSION, package
from .reports import package as reports


WORKER_FILES = ('LICENSE', 'docs/worker-routing-design.md', 'docs/worker-routing-study.md',
                'agents/luna-max.toml', 'agents/sol-xhigh.toml', 'legacy/agents/terra-xhigh.toml',
                *(f'skills/{name}/{file}' for name in ('luna-task', 'luna-goal-loop', 'worker-task', 'worker-goal-loop')
                  for file in ('SKILL.md', 'agents/openai.yaml')),
                *(f'legacy/skills/{name}/{file}' for name in ('terra-task', 'terra-goal-loop')
                  for file in ('SKILL.md', 'agents/openai.yaml')))
COMPONENTS = {'workers': 'codex-plus-workers', 'monitoring': 'codex-plus-runtime', 'reporting': 'codex-plus-report'}


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + '\n').encode()


def workers(root, output, revision):
    content = {name: package.git(root, 'show', revision + ':' + name) for name in WORKER_FILES}
    metadata = {'schema': 1, 'name': 'codex-plus-workers', 'version': VERSION, 'source_revision': revision,
                'compatibility': {'agent': 'native Codex custom agents and skills', 'legacy': 'explicit optional installation'},
                'files': {name: {'sha256': package.sha(data), 'mode': 0o644} for name, data in sorted(content.items())}}
    content['workers.json'] = encoded(metadata)
    with output.open('xb') as destination:
        with gzip.GzipFile(filename='', fileobj=destination, mode='wb', mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode='w', format=tarfile.USTAR_FORMAT) as archive:
                for name, data in sorted(content.items()):
                    entry = tarfile.TarInfo('codex-plus-workers/' + name)
                    entry.size, entry.mode, entry.mtime = len(data), 0o644, 0
                    archive.addfile(entry, io.BytesIO(data))
    return metadata


def read_workers(path):
    if path.stat().st_size > package.MAX_ARCHIVE_BYTES:
        raise ValueError('worker artifact exceeds size bound')
    content = {}
    with tarfile.open(path, 'r:gz') as archive:
        for entry in archive:
            prefix = 'codex-plus-workers/'
            name = entry.name.removeprefix(prefix)
            if (not entry.name.startswith(prefix) or name not in (*WORKER_FILES, 'workers.json')
                    or name in content or not entry.isfile() or entry.mode != 0o644
                    or not 0 <= entry.size <= package.MAX_FILE_BYTES):
                raise ValueError('unexpected, duplicate, linked or oversized worker member')
            content[name] = archive.extractfile(entry).read(package.MAX_FILE_BYTES + 1)
            if len(content[name]) != entry.size: raise ValueError('worker member size mismatch')
    if set(content) != {*WORKER_FILES, 'workers.json'}:
        raise ValueError('worker inventory differs')
    metadata = json.loads(content.pop('workers.json'))
    if (set(metadata) != {'schema', 'name', 'version', 'source_revision', 'compatibility', 'files'}
            or metadata['schema'] != 1 or metadata['name'] != 'codex-plus-workers' or metadata['version'] != VERSION
            or set(metadata['files']) != set(content)):
        raise ValueError('invalid worker manifest')
    package.revision(metadata['source_revision'])
    for name, data in content.items():
        if metadata['files'][name] != {'sha256': package.sha(data), 'mode': 0o644}:
            raise ValueError('worker content/mode mismatch: ' + name)
    return metadata


def build(root, output):
    root, output = Path(root).resolve(), Path(output).resolve()
    if output.is_relative_to(root): raise ValueError('write releases outside the source checkout')
    if package.git(root, 'status', '--porcelain', '--untracked-files=all').strip():
        raise ValueError('release build requires a clean committed checkout')
    revision = package.git(root, 'rev-parse', 'HEAD').decode().strip()
    tree = ast.parse(package.git(root, 'show', revision + ':codex_plus/__init__.py'))
    versions = [ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign)
                and any(isinstance(target, ast.Name) and target.id == 'VERSION' for target in node.targets)]
    if versions != [VERSION]: raise ValueError('builder and committed product version differ')
    output.mkdir(parents=True, exist_ok=False)
    result = {'schema': 1, 'name': 'codex-plus', 'version': VERSION, 'tag': 'v' + VERSION,
              'source_revision': revision, 'components': {}}
    for name, archive_root in COMPONENTS.items():
        path = output / (archive_root + '-' + VERSION + '.tar.gz')
        if name == 'workers': metadata = workers(root, path, revision)
        elif name == 'monitoring': metadata = package.build(root, path)
        else: metadata = reports.build(root, path)
        if metadata['version'] != VERSION or metadata['source_revision'] != revision:
            raise ValueError('component version/revision differs from the product release')
        result['components'][name] = {'artifact': path.name, 'sha256': package.sha(path.read_bytes()),
                                     'bytes': path.stat().st_size, 'compatibility': metadata['compatibility']}
    (output / 'release.json').write_bytes(encoded(result))
    (output / 'SHA256SUMS').write_text(''.join(package.sha(path.read_bytes()) + '  ' + path.name + '\n'
        for path in sorted(output.iterdir())))
    verify(output)
    return result


def verify(root):
    root = Path(root)
    manifest = root / 'release.json'
    if manifest.is_symlink() or manifest.stat().st_size > 65536:
        raise ValueError('release manifest must be a bounded regular file')
    result = json.loads(manifest.read_text())
    if (set(result) != {'schema', 'name', 'version', 'tag', 'source_revision', 'components'}
            or result['schema'] != 1 or result['name'] != 'codex-plus' or result['version'] != VERSION
            or result['tag'] != 'v' + VERSION or set(result['components']) != set(COMPONENTS)):
        raise ValueError('invalid unified release manifest')
    package.revision(result['source_revision'])
    expected = {'release.json', 'SHA256SUMS'}
    for name, archive_root in COMPONENTS.items():
        component = result['components'][name]
        filename = archive_root + '-' + VERSION + '.tar.gz'
        if set(component) != {'artifact', 'sha256', 'bytes', 'compatibility'} or component['artifact'] != filename:
            raise ValueError('unexpected release component path or metadata')
        expected.add(filename)
        path = root / filename
        if path.is_symlink() or not path.is_file() or not 0 < path.stat().st_size <= package.MAX_ARCHIVE_BYTES:
            raise ValueError('component artifact must be a bounded regular file')
        if path.stat().st_size != component['bytes'] or package.sha(path.read_bytes()) != component['sha256']:
            raise ValueError('release artifact size/checksum mismatch')
        if name == 'workers': metadata = read_workers(path)
        elif name == 'monitoring': metadata = package.read_archive(path)[0]
        else: metadata = reports.read_archive(path)[0]
        if (metadata['version'] != VERSION or metadata['source_revision'] != result['source_revision']
                or metadata['compatibility'] != component['compatibility']):
            raise ValueError('component identity/compatibility differs from the release')
    if {path.name for path in root.iterdir()} != expected:
        raise ValueError('release directory inventory differs')
    sums = root / 'SHA256SUMS'
    if sums.is_symlink() or sums.stat().st_size > 4096:
        raise ValueError('invalid checksum file')
    calculated = ''.join(package.sha((root / name).read_bytes()) + '  ' + name + '\n'
                         for name in sorted(expected - {'SHA256SUMS'}))
    if sums.read_text() != calculated:
        raise ValueError('release checksum file differs')
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='operation', required=True)
    make = commands.add_parser('build'); make.add_argument('--source', type=Path, default=Path(__file__).resolve().parents[1])
    make.add_argument('--output', type=Path, required=True)
    check = commands.add_parser('verify'); check.add_argument('directory', type=Path)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(build(args.source, args.output) if args.operation == 'build' else verify(args.directory), indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError, tarfile.TarError) as error:
        print(json.dumps({'error': str(error)})); return 1
