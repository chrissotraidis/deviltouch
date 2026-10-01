import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class SourceGuards(unittest.TestCase):
    def test_readme_distinguishes_current_build_floor_from_preview(self):
        readme = (ROOT / 'README.md').read_text()
        floors = []
        for name in ('configure-ios-device.sh', 'configure-ios-simulator.sh'):
            script = (ROOT / 'scripts' / name).read_text()
            match = re.search(r'\$\{DEVILTOUCH_IOS_DEPLOYMENT_TARGET:-([0-9.]+)\}', script)
            self.assertIsNotNone(match, name)
            floors.append(match.group(1))
        self.assertEqual(floors[0], floors[1])
        self.assertIn('current source builds default to iOS ' + floors[0], readme)
        self.assertIn('currently published `v1.5.5-preview.1` IPA has a minimum iOS version of 13.0', readme)

    def test_readme_does_not_hide_the_public_unsigned_preview(self):
        readme = (ROOT / 'README.md').read_text()
        self.assertIn('An unsigned IPA preview is public', readme)
        self.assertIn('[Install on an iPad](#install-on-an-ipad)', readme)
        self.assertNotIn('there is currently no public IPA', readme)

    def test_dependency_patch_is_verified_idempotent_and_rejects_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp)
            (root / 'scripts').mkdir()
            shutil.copy(ROOT/'scripts/apply-dependency-patches.py', root/'scripts')
            target = root/'build/_deps/example-src/input.txt'
            target.parent.mkdir(parents=True)
            target.write_text('before\n')
            (root/'fix.patch').write_text('--- a/input.txt\n+++ b/input.txt\n@@ -1 +1 @@\n-before\n+after\n')
            (root/'sources.lock.json').write_text(json.dumps({'package_patch_exceptions':[{
                'name':'example','file':'input.txt','patch':'fix.patch',
                'before_sha256':hashlib.sha256(b'before\n').hexdigest(),
                'after_sha256':hashlib.sha256(b'after\n').hexdigest()}]}))
            command=['python3',str(root/'scripts/apply-dependency-patches.py'),str(root/'build')]
            for _ in range(2):
                self.assertEqual(subprocess.run(command,capture_output=True).returncode,0)
                self.assertEqual(target.read_bytes(),b'after\n')
            target.write_text('private change\n')
            self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)
            self.assertEqual(target.read_text(),'private change\n')

    def test_restored_archive_rejects_content_and_mode_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            root=pathlib.Path(temp)
            (root/'scripts').mkdir()
            shutil.copy(ROOT/'scripts/verify-sources.py',root/'scripts')
            (root/'sources.lock.json').write_text(json.dumps({'engine':{'path':'engine'}}))
            target=root/'input';target.write_text('original');target.chmod(0o644)
            (root/'SOURCE_MANIFEST.json').write_text(json.dumps({'input':{'sha256':hashlib.sha256(b'original').hexdigest(),'mode':0o644}}))
            command=['python3',str(root/'scripts/verify-sources.py')]
            self.assertEqual(subprocess.run(command,capture_output=True).returncode,0)
            target.chmod(0o755)
            self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)
            target.chmod(0o644);target.write_text('changed')
            self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)

    def test_personal_relink_only_exempts_lgpl_library_trees(self):
        with tempfile.TemporaryDirectory() as temp:
            root=pathlib.Path(temp)
            (root/'scripts').mkdir()
            shutil.copy(ROOT/'scripts/verify-sources.py',root/'scripts')
            (root/'sources.lock.json').write_text(json.dumps({'engine':{'path':'engine'}}))
            manifest={}
            for name in ['dependencies/sdl_audiolib/code.cpp','dependencies/libsmackerdec/code.cpp','engine/code.cpp']:
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
                target.write_text('original');target.chmod(0o644)
                manifest[name]={'sha256':hashlib.sha256(b'original').hexdigest(),'mode':0o644}
            (root/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest))
            command=['python3',str(root/'scripts/verify-sources.py')]
            for name in ['sdl_audiolib','libsmackerdec']:
                (root/'dependencies'/name/'code.cpp').write_text('modified')
            self.assertNotEqual(subprocess.run(command,capture_output=True).returncode,0)
            env=dict(os.environ,DEVILTOUCH_REBUILD_LGPL='1')
            self.assertEqual(subprocess.run(command,capture_output=True,env=env).returncode,0)
            (root/'engine/code.cpp').write_text('unexpected')
            self.assertNotEqual(subprocess.run(command,capture_output=True,env=env).returncode,0)

if __name__=='__main__':
    unittest.main()
