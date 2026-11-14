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
if os.environ.get('DEVILTOUCH_REBUILD_LGPL'):
    raise SystemExit('Personal modified-library builds are not release artifacts')
subprocess.run(['python3', str(root / 'scripts/verify-sources.py')], check=True)
if git(root, 'status', '--porcelain', '--untracked-files=all').strip():
    raise SystemExit('Commit intended app changes before exporting source')
if args.output.exists():
    raise SystemExit('Refusing to overwrite an existing artifact')
sources = {p.name[:-4]: p for p in (args.build_dir / '_deps').glob('*-src')}
# iOS builds take SDL from the pinned scene SDL checkout; CMake records which one.
for line in (args.build_dir / 'CMakeCache.txt').read_text().splitlines():
    if line.startswith('FETCHCONTENT_SOURCE_DIR_SDL2:') and line.split('=', 1)[1]:
        sdl = pathlib.Path(line.split('=', 1)[1])
        if git(sdl, 'rev-parse', 'HEAD').decode().strip() != json.loads((root/'sources.lock.json').read_text())['ios_sdl']['commit']:
            raise SystemExit('Configured SDL is not the pinned iOS SDL')
        sources['sdl2'] = sdl
required = {'asio','libfmt','mpqfs','libpng','libsmackerdec','libsodium','sdl2','sdl_audiolib','sdl_image','simpleini'}
if set(sources) != required:
    raise SystemExit('Configured dependency set differs from the qualified Apple source graph')
with tempfile.TemporaryDirectory() as temp:
    stage = pathlib.Path(temp) / 'deviltouch-source'
    stage.mkdir()
    for source, destination in [(root, stage), (root / 'upstream/DevilutionX', stage / 'upstream/DevilutionX')]:
        destination.mkdir(parents=True, exist_ok=True)
        with tarfile.open(fileobj=io.BytesIO(git(source, 'archive', 'HEAD'))) as archive:
            # The archive is generated directly from the reviewed local Git commit.
            for member in archive.getmembers():
                if pathlib.PurePosixPath(member.name).is_absolute() or '..' in pathlib.PurePosixPath(member.name).parts:
                    raise SystemExit('Unsafe Git archive member')
            archive.extractall(destination)
    cache = ['# Exact local sources; no FetchContent download is needed.']
    for name, source in sorted(sources.items()):
        shutil.copytree(source, stage / 'dependencies' / name, symlinks=True,
                        ignore=shutil.ignore_patterns('.git', '.DS_Store'))
        cache.append('set(FETCHCONTENT_SOURCE_DIR_' + name.upper() + ' "${CMAKE_CURRENT_LIST_DIR}/dependencies/' + name + '" CACHE PATH "" FORCE)')
    cache.append('set(FETCHCONTENT_FULLY_DISCONNECTED ON CACHE BOOL "" FORCE)')
    (stage / 'dependencies.cmake').write_text('\n'.join(cache) + '\n')
    (stage / 'SOURCE_PROVENANCE.json').write_text(json.dumps({'app_commit': git(root, 'rev-parse', 'HEAD').decode().strip(), 'engine': json.loads((root/'sources.lock.json').read_text())['engine'], 'release_status': 'Free non-commercial DevilTouch release; component terms and rebuild instructions in doc/RELEASE_RIGHTS.md'}, indent=2)+'\n')
    # Git archives may use group-writable modes; normalize for ordinary tar/umask restoration.
    for file in stage.rglob('*'):
        if file.is_file() and not file.is_symlink():
            file.chmod(0o755 if file.stat().st_mode & 0o111 else 0o644)
    (stage / 'SOURCE_MANIFEST.json').write_text(json.dumps(manifest(stage), indent=2)+'\n')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(args.output, 'w:gz') as archive:
        archive.add(stage, arcname=stage.name)
print(args.output)
print(hashlib.sha256(args.output.read_bytes()).hexdigest())
