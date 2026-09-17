#!/usr/bin/env python3
"""Reject mismatched or dirty maintained engine sources before configuring."""
import hashlib, json, os, pathlib, subprocess, sys
root = pathlib.Path(__file__).resolve().parents[1]
lock = json.loads((root / 'sources.lock.json').read_text())['engine']
engine = root / lock['path']
def git(*args):
    return subprocess.check_output(['git', '-C', str(engine), *args], text=True).strip()
try:
    archive_manifest = root / 'SOURCE_MANIFEST.json'
    if archive_manifest.exists():
        modified_lgpl = os.environ.get('DEVILTOUCH_REBUILD_LGPL') == '1'
        for name, expected in json.loads(archive_manifest.read_text()).items():
            if modified_lgpl and name.startswith(('dependencies/sdl_audiolib/', 'dependencies/libsmackerdec/')):
                continue
            file = root / name
            if 'link' in expected:
                if not file.is_symlink() or os.readlink(file) != expected['link']:
                    raise ValueError('Source archive symlink mismatch: ' + name)
            elif not file.is_file() or hashlib.sha256(file.read_bytes()).hexdigest() != expected['sha256'] or file.stat().st_mode & 0o777 != expected['mode']:
                raise ValueError('Source archive mismatch: ' + name)
        print('Verified restored source archive' if not modified_lgpl else 'Personal LGPL rebuild: library edits allowed; remaining source verified')
        sys.exit(0)
    if not (engine / 'CMakeLists.txt').exists():
        raise ValueError('Initialize sources with git submodule update --init --recursive')
    index = subprocess.check_output(['git', '-C', str(root), 'ls-files', '--stage', lock['path']], text=True).split()
    if len(index) < 2 or index[0] != '160000' or index[1] != lock['commit']:
        raise ValueError('App gitlink differs from sources.lock.json')
    if git('rev-parse', 'HEAD') != lock['commit']:
        raise ValueError('Engine commit differs from sources.lock.json')
    if git('status', '--porcelain', '--untracked-files=all'):
        raise ValueError('Engine has local changes; preserve them in a separate branch before building')
    print('Verified maintained engine ' + lock['commit'])
except (ValueError, subprocess.CalledProcessError) as error:
    sys.exit(str(error))
