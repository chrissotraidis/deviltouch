#!/usr/bin/env python3
"""Package a clean unsigned device build for recipient signing in AltStore Classic."""
import argparse, hashlib, json, os, pathlib, plistlib, shutil, subprocess, tempfile, zipfile
root = pathlib.Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('build_dir', type=pathlib.Path)
p.add_argument('output', type=pathlib.Path)
a = p.parse_args()
if a.output.exists() or os.environ.get('DEVILTOUCH_REBUILD_LGPL'):
    raise SystemExit('Use a new output path and an unmodified release build')
subprocess.run(['python3', str(root/'scripts/verify-sources.py')], check=True)
if subprocess.check_output(['git','-C',str(root),'status','--porcelain']).strip():
    raise SystemExit('Release packaging requires a clean app commit')
app = a.build_dir/'Release-iphoneos/devilutionx.app'
stamp = json.loads((app.parent/'deviltouch-build.json').read_text())
commit = subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
if stamp.get('dirty') or stamp['app_commit'] != commit or stamp['executable_sha256'] != hashlib.sha256((app/'devilutionx').read_bytes()).hexdigest():
    raise SystemExit('Rebuild from the current clean commit before packaging')
info = plistlib.loads((app/'Info.plist').read_bytes())
if (info['CFBundleShortVersionString'], info['CFBundleVersion']) != ('1.5.5','2'):
    raise SystemExit('Unexpected release version')
if 'arm64' not in subprocess.check_output(['lipo','-archs',str(app/'devilutionx')],text=True):
    raise SystemExit('Expected ARM64 device binary')
if (app/'embedded.mobileprovision').exists() or (app/'_CodeSignature').exists():
    raise SystemExit('Build unsigned for AltStore; do not publish personal signing material')
if any(x.suffix.lower() in ('.mpq','.sv','.hsv','.dsv','.key','.p12') for x in app.rglob('*')):
    raise SystemExit('Unexpected game archive, save or signing input in app')
project = (a.build_dir/'DevilutionX.xcodeproj/project.pbxproj').read_text()
if 'liblibmpq.a' in project or not (a.build_dir/'_deps/mpqfs-src/LICENSE').is_file():
    raise SystemExit('Unqualified archive reader graph')
with tempfile.TemporaryDirectory() as temp:
    payload = pathlib.Path(temp)/'Payload'; payload.mkdir()
    staged = payload/app.name; shutil.copytree(app, staged, symlinks=True)
    notices = staged/'Notices'; notices.mkdir()
    for name in ['LICENSE.md','NOTICE.md','doc/RELEASE_RIGHTS.md','doc/REBUILDING.md']:
        shutil.copy2(root/name, notices/pathlib.Path(name).name)
    inputs = [('engine',root/'upstream/DevilutionX')]
    inputs += [(x.name[:-4],x) for x in sorted((a.build_dir/'_deps').glob('*-src'))]
    for component, source in inputs:
        for file in source.rglob('*'):
            if not file.is_file() or '.git' in file.parts: continue
            if file.name.lower().startswith(('license','copying','copyright','notice','authors')):
                target = notices/component/file.relative_to(source)
                target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(file,target)
    # Embedded permissive notices and LGPL copyright statements live in source files.
    for rel in ['3rdParty/PicoSHA2/picosha2.h','3rdParty/hoehrmann_utf8/hoehrmann_utf8.h','3rdParty/tl/expected.hpp','3rdParty/tl/function_ref.hpp','3rdParty/PKWare/implode.cpp','3rdParty/PKWare/explode.cpp','Source/DiabloUI/credits_lines.cpp']:
        target=notices/'engine'/rel; target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(root/'upstream/DevilutionX'/rel,target)
    for name, rel in [('sdl_audiolib','src/stream.cpp'),('libsmackerdec','src/SmackerDecoder.cpp')]:
        shutil.copy2(a.build_dir/'_deps'/(name+'-src')/rel,notices/name/pathlib.Path(rel).name)
    for file in (root/'doc/licenses').glob('*'):
        shutil.copy2(file,notices/file.name)
    provenance = {'app_commit':subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip(), 'sources':json.loads((root/'sources.lock.json').read_text()),'version':info['CFBundleShortVersionString'],'build':info['CFBundleVersion'],'bundle_identifier':info['CFBundleIdentifier'],'minimum_os':info['MinimumOSVersion'],'signing':'Unsigned; recipient signs with AltStore Classic','executable_sha256':hashlib.sha256((staged/'devilutionx').read_bytes()).hexdigest(),'xcode':subprocess.check_output(['xcodebuild','-version'],text=True).strip(),'sdk':subprocess.check_output(['xcrun','--sdk','iphoneos','--show-sdk-version'],text=True).strip()}
    (staged/'BUILD_PROVENANCE.json').write_text(json.dumps(provenance,indent=2)+'\n')
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(a.output,'w',zipfile.ZIP_DEFLATED) as archive:
        for file in sorted(payload.rglob('*')):
            if file.is_file(): archive.write(file,file.relative_to(payload.parent))
    a.output.with_suffix('.provenance.json').write_text(json.dumps(provenance,indent=2)+'\n')
print(a.output)
print(hashlib.sha256(a.output.read_bytes()).hexdigest())
