#!/usr/bin/env python3
"""Export clean app/engine source plus all configured dependency sources."""
import argparse, hashlib, io, json, os, pathlib, shutil, subprocess, tarfile, tempfile
root = pathlib.Path(__file__).resolve().parents[1]
def git(path, *args):
    return subprocess.check_output(['git', '-C', str(path), *args])
def manifest(path):
    result = {}
    for file in sorted(path.rglob('*')):
        if file.is_symlink():
            result[str(file.relative_to(path))] = {'link': os.readlink(file)}
        elif file.is_file() and file.name != 'SOURCE_MANIFEST.json':
            result[str(file.relative_to(path))] = {'sha256': hashlib.sha256(file.read_bytes()).hexdigest(), 'mode': file.stat().st_mode & 0o777}
    return result
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('build_dir', type=pathlib.Path)
parser.add_argument('output', type=pathlib.Path)
args = parser.parse_args()
subprocess.run(['python3', str(root / 'scripts/verify-sources.py')], check=True)
if git(root, 'status', '--porcelain', '--untracked-files=all').strip():
    raise SystemExit('Commit intended app changes before exporting source')
if args.output.exists():
    raise SystemExit('Refusing to overwrite an existing artifact')
sources = sorted((args.build_dir / '_deps').glob('*-src'))
required = {'asio','libfmt','libmpq','libpng','libsmackerdec','libsodium','sdl2','sdl_audiolib','sdl_image','simpleini'}
if {p.name[:-4] for p in sources} != required:
    raise SystemExit('Configured dependency set differs from the qualified Apple source graph')
with tempfile.TemporaryDirectory() as temp:
    stage = pathlib.Path(temp) / 'deviltouch-source'
    stage.mkdir()
    for source, destination in [(root, stage), (root / 'upstream/DevilutionX', stage / 'upstream/DevilutionX')]:
        destination.mkdir(parents=True, exist_ok=True)
        with tarfile.open(fileobj=io.BytesIO(git(source, 'archive', 'HEAD'))) as archive:
            archive.extractall(destination, filter='data')
    cache = ['# Exact local sources; no FetchContent download is needed.']
    for source in sources:
        name = source.name[:-4]
        shutil.copytree(source, stage / 'dependencies' / name, symlinks=True,
                        ignore=shutil.ignore_patterns('.git', '.DS_Store'))
        cache.append('set(FETCHCONTENT_SOURCE_DIR_' + name.upper() + ' "${CMAKE_CURRENT_LIST_DIR}/dependencies/' + name + '" CACHE PATH "" FORCE)')
    cache.append('set(FETCHCONTENT_FULLY_DISCONNECTED ON CACHE BOOL "" FORCE)')
    (stage / 'dependencies.cmake').write_text('\n'.join(cache) + '\n')
    (stage / 'SOURCE_PROVENANCE.json').write_text(json.dumps({'app_commit': git(root, 'rev-parse', 'HEAD').decode().strip(), 'engine': json.loads((root/'sources.lock.json').read_text())['engine'], 'release_status': 'Not qualified for binary publication; see doc/RELEASE_RIGHTS.md'}, indent=2)+'\n')
    (stage / 'SOURCE_MANIFEST.json').write_text(json.dumps(manifest(stage), indent=2)+'\n')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(args.output, 'w:gz') as archive:
        archive.add(stage, arcname=stage.name)
print(args.output)
print(hashlib.sha256(args.output.read_bytes()).hexdigest())
