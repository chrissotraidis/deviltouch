import pathlib
import shutil
import subprocess
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
XCODE_STOP = 73


class BuildIosDeviceJobs(unittest.TestCase):
    def run_entrypoint(self, overrides, signed, configure_status=0):
        with tempfile.TemporaryDirectory(prefix='deviltouch-jobs-') as temp:
            root = pathlib.Path(temp)
            scripts = root / 'scripts'
            scripts.mkdir()
            shutil.copy2(ROOT / 'scripts/build-ios-device.sh', scripts)
            commands = root / 'commands'
            commands.mkdir()
            log = root / 'commands.log'
            argv = root / 'xcode.argv'
            build = root / 'output with spaces'
            derived = root / 'derived with spaces'

            def fixture(path, body):
                path.write_text('#!/bin/sh\nset -eu\n' + body)
                path.chmod(0o755)

            fixture(scripts / 'configure-ios-device.sh',
                    'printf "configure\\n" >> "$FIXTURE_LOG"\n'
                    'exit "$FIXTURE_CONFIGURE_STATUS"\n')
            fixture(commands / 'dirname',
                    'printf "dirname\\n" >> "$FIXTURE_LOG"\n'
                    'exec /usr/bin/dirname "$@"\n')
            fixture(commands / 'xcodebuild',
                    'printf "xcodebuild\\n" >> "$FIXTURE_LOG"\n'
                    'printf "%s\\n" "$@" > "$FIXTURE_ARGV"\n'
                    f'exit {XCODE_STOP}\n')
            # Any attempt to continue into verification/packaging is a failure.
            for name in ('file', 'grep', 'codesign', 'python3', 'cmake', 'git', 'xcrun'):
                fixture(commands / name,
                        f'printf "unexpected {name}\\n" >> "$FIXTURE_LOG"\n'
                        'exit 99\n')

            env = {
                'PATH': str(commands),
                'LC_ALL': 'C',
                'BUILD_DIR': str(build),
                'DERIVED_DATA_DIR': str(derived),
                'FIXTURE_LOG': str(log),
                'FIXTURE_ARGV': str(argv),
                'FIXTURE_CONFIGURE_STATUS': str(configure_status),
            }
            if signed:
                env['DEVELOPMENT_TEAM'] = 'FIXTURE123'
            env.update(overrides)
            result = subprocess.run(
                ['/bin/sh', str(scripts / 'build-ios-device.sh')],
                env=env, capture_output=True, text=True,
            )
            calls = log.read_text().splitlines() if log.exists() else []
            args = argv.read_text().splitlines() if argv.exists() else []
            self.assertFalse(build.exists(), 'fixture must not create build output')
            self.assertFalse(derived.exists(), 'fixture must not create derived data')
            return result, calls, args, build, derived

    def assert_forwarded(self, overrides, signed, expected_jobs):
        result, calls, args, build, derived = self.run_entrypoint(overrides, signed)
        self.assertEqual(result.returncode, XCODE_STOP, result.stderr)
        self.assertEqual(result.stdout, '')
        self.assertEqual(result.stderr, '')
        self.assertEqual(calls, ['dirname', 'configure', 'xcodebuild'])
        expected = [
            '-project', str(build / 'DevilutionX.xcodeproj'),
            '-scheme', 'devilutionx',
            '-configuration', 'Release',
            '-destination', 'generic/platform=iOS',
            '-derivedDataPath', str(derived),
        ]
        if signed:
            expected += [
                '-allowProvisioningUpdates', 'DEVELOPMENT_TEAM=FIXTURE123',
                'CODE_SIGN_STYLE=Automatic',
                'CODE_SIGNING_ALLOWED=YES', 'CODE_SIGNING_REQUIRED=YES',
            ]
        else:
            expected += ['CODE_SIGNING_ALLOWED=NO', 'CODE_SIGNING_REQUIRED=NO']
        expected += ['-quiet', '-jobs', expected_jobs, 'build']
        self.assertEqual(args, expected)

    def test_cmake_two_job_limit_signed_and_unsigned(self):
        for signed in (False, True):
            with self.subTest(signed=signed):
                self.assert_forwarded({'CMAKE_BUILD_PARALLEL_LEVEL': '2'}, signed, '2')

    def test_manual_jobs_take_precedence_signed_and_unsigned(self):
        for signed in (False, True):
            for cmake in (None, '', '2', 'invalid'):
                with self.subTest(signed=signed, cmake=cmake):
                    env = {'JOBS': '3'}
                    if cmake is not None:
                        env['CMAKE_BUILD_PARALLEL_LEVEL'] = cmake
                    self.assert_forwarded(env, signed, '3')

    def test_default_eight_with_unset_or_empty_limits(self):
        for signed in (False, True):
            for env in ({}, {'JOBS': ''}, {'CMAKE_BUILD_PARALLEL_LEVEL': ''},
                        {'JOBS': '', 'CMAKE_BUILD_PARALLEL_LEVEL': ''}):
                with self.subTest(signed=signed, env=env):
                    self.assert_forwarded(env, signed, '8')

    def test_empty_jobs_use_cmake_limit_signed_and_unsigned(self):
        for signed in (False, True):
            with self.subTest(signed=signed):
                self.assert_forwarded(
                    {'JOBS': '', 'CMAKE_BUILD_PARALLEL_LEVEL': '2'}, signed, '2')

    def test_invalid_selected_limit_fails_before_configure_output_or_tools(self):
        invalid = ('0', '00', '02', '-2', '+2', '2.0', '2e1', ' 2', '2 ',
                   '2\n', 'two', '２', '2;exit 0')
        for signed in (False, True):
            for value in invalid:
                for env in (
                    {'JOBS': value, 'CMAKE_BUILD_PARALLEL_LEVEL': '2'},
                    {'CMAKE_BUILD_PARALLEL_LEVEL': value},
                    {'JOBS': '', 'CMAKE_BUILD_PARALLEL_LEVEL': value},
                ):
                    with self.subTest(signed=signed, env=env):
                        result, calls, args, _, _ = self.run_entrypoint(env, signed)
                        self.assertEqual(result.returncode, 1)
                        self.assertIn('positive whole number without leading zeros', result.stderr)
                        self.assertEqual(result.stdout, '')
                        self.assertEqual(calls, [])
                        self.assertEqual(args, [])

    def test_configure_failure_remains_fail_closed_signed_and_unsigned(self):
        for signed in (False, True):
            with self.subTest(signed=signed):
                result, calls, args, _, _ = self.run_entrypoint(
                    {'CMAKE_BUILD_PARALLEL_LEVEL': '2'}, signed, configure_status=23)
                self.assertEqual(result.returncode, 23)
                self.assertEqual(calls, ['dirname', 'configure'])
                self.assertEqual(args, [])
                self.assertEqual(result.stdout, '')
                self.assertEqual(result.stderr, '')


if __name__ == '__main__':
    unittest.main()
