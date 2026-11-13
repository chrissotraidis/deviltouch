import pathlib
import shutil
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
HEADER = ROOT / 'upstream/DevilutionX/Source/controls/touch/visibility.hpp'


class TouchOverlayVisibility(unittest.TestCase):
    def test_default_auto_hide_and_show_decision(self):
        compiler = shutil.which('c++') or shutil.which('clang++') or shutil.which('g++')
        if compiler is None:
            self.skipTest('no C++ compiler')
        self.assertTrue(HEADER.exists(), 'engine submodule is not checked out')
        with tempfile.TemporaryDirectory() as temp:
            binary = pathlib.Path(temp) / 'touch_visibility_test'
            subprocess.run([compiler, '-std=c++17', '-Wall', '-Wextra', '-Werror',
                            str(ROOT / 'tests/touch_visibility_test.cpp'), '-o', str(binary)], check=True)
            result = subprocess.run([str(binary)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
