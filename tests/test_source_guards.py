import hashlib
import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]

class SourceGuards(unittest.TestCase):
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

if __name__=='__main__':
    unittest.main()
