#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Control/receipt tests mock the engine; no native packages or applications needed."""
from pathlib import Path
from contextlib import ExitStack
import sys
import tempfile
import unittest
from unittest import mock
import xml.etree.ElementTree as ET
import zipfile

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import libreoffice_recalc as calc


def calculated_control(source, output, **kwargs):
    with zipfile.ZipFile(source) as original, zipfile.ZipFile(output, 'w') as result:
        for name in original.namelist():
            data = original.read(name)
            if name == 'xl/worksheets/sheet1.xml':
                root = ET.fromstring(data)
                cell = root.find(f'{calc.S}sheetData/{calc.S}row/{calc.S}c[@r="C1"]')
                cell.find(f'{calc.S}v').text = '42'
                data = ET.tostring(root)
            result.writestr(name, data)
    return True, 'mock engine executed'


class CalculationSessionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.receipt = self.root / 'task-control.json'

    def install(self):
        program = self.root / 'install/program'
        registry = self.root / 'install/share/registry'
        program.mkdir(parents=True)
        registry.mkdir(parents=True)
        for path in (program / 'soffice', program / 'soffice.bin', registry / 'calc.xcd'):
            path.write_text('installed component')
        return program / 'soffice'

    def test_fingerprint_has_no_tree_scan_commands_or_full_environment_collection(self):
        binary = self.install()
        class AllowlistedEnvironment(dict):
            def forbidden(self, *args, **kwargs):
                raise AssertionError('full environment collection forbidden')
            __iter__ = items = keys = values = forbidden
        environment = AllowlistedEnvironment(LANG='C', SECRET_TOKEN='private', UNRELATED='first')
        with ExitStack() as stack:
            for target, name in ((Path, 'rglob'), (Path, 'glob'), (Path, 'iterdir'),
                                 (Path, 'read_bytes'), (Path, 'read_text'),
                                 (calc.os, 'walk'), (calc.os, 'scandir'), (calc.os, 'listdir'),
                                 (calc.subprocess, 'run'), (calc.subprocess, 'Popen'),
                                 (calc, '_run_soffice'), (calc, 'get_libreoffice_version')):
                stack.enter_context(mock.patch.object(target, name, side_effect=AssertionError(name)))
            stack.enter_context(mock.patch.object(calc.os, 'environ', environment))
            session = calc.CalculationSession(task_id='task')
            first = session.fingerprint(str(binary))
            self.assertIsNotNone(first)
            session.record(first, 'version-label')
            environment['SECRET_TOKEN'] = 'changed private value'
            environment['UNRELATED'] = 'changed irrelevant setting'
            second = session.fingerprint(str(binary))
            self.assertEqual(first, second)
            self.assertIsNotNone(session.load(second))
            environment['LANG'] = 'changed-locale'
            self.assertNotEqual(first, session.fingerprint(str(binary)))

    def test_fingerprint_stat_work_is_fixed_even_with_large_install_tree(self):
        binary = self.install()
        # These files must never be enumerated; only the fixed directory stat is sampled.
        extras = binary.parent / 'unrelated'
        extras.mkdir()
        for index in range(150):
            (extras / str(index)).write_text('irrelevant')
        original_stat, original_lstat = Path.stat, Path.lstat
        with mock.patch.object(Path, 'stat', autospec=True, side_effect=original_stat) as stats, \
             mock.patch.object(Path, 'lstat', autospec=True, side_effect=original_lstat) as lstats:
            self.assertIsNotNone(calc.CalculationSession().fingerprint(str(binary)))
            # Path.lstat delegates to Path.stat on some Python versions, so this
            # conservative bound includes both wrappers, not just OS syscalls.
            self.assertLessEqual(stats.call_count + lstats.call_count, 96)
            self.assertFalse(any(extras in call.args[0].parents for call in lstats.call_args_list))

    def test_fixed_engine_registry_bootstrap_and_script_changes_invalidate(self):
        binary = self.install()
        script = self.root / 'control.py'
        script.write_text('control implementation')
        session = calc.CalculationSession(task_id='task')
        paths = (binary, binary.parent / 'soffice.bin',
                 binary.parent.parent / 'share/registry/calc.xcd',
                 binary.parent / 'bootstraprc', binary.parent / 'libscfiltlo.so', script)
        with mock.patch.object(calc, '__file__', str(script)):
            for path in paths:
                with self.subTest(path=path.name):
                    before = session.fingerprint(str(binary))
                    self.assertIsNotNone(before)
                    session.record(before, 'v')
                    path.write_text('changed identity with a different size')
                    after = session.fingerprint(str(binary))
                    self.assertNotEqual(before, after)
                    self.assertIsNone(session.load(after))

    def test_package_manager_and_linker_identity_changes_invalidate(self):
        binary = self.install()
        standin = self.root / 'system-metadata'
        original_lstat = Path.lstat
        for filename in ('/etc/ld.so.cache', '/var/lib/dpkg/status',
                         '/var/lib/rpm/rpmdb.sqlite', '/lib/apk/db/installed'):
            with self.subTest(path=filename):
                standin.write_text('old metadata')
                def sampled(path):
                    return original_lstat(standin if str(path) == filename else path)
                with mock.patch.object(Path, 'lstat', autospec=True, side_effect=sampled):
                    session = calc.CalculationSession()
                    before = session.fingerprint(str(binary))
                    self.assertIsNotNone(before)
                    standin.write_text('new package/linker metadata with different size')
                    self.assertNotEqual(before, session.fingerprint(str(binary)))

    def test_loader_locale_temp_backend_settings_invalidate(self):
        binary = self.install()
        session = calc.CalculationSession()
        for name in ('LD_LIBRARY_PATH', 'LD_PRELOAD', 'DYLD_LIBRARY_PATH',
                     'LANG', 'LC_NUMERIC', 'LC_TIME', 'TZ', 'TMPDIR',
                     'SAL_USE_VCLPLUGIN', 'SAL_DISABLE_OPENCL'):
            with self.subTest(setting=name), mock.patch.dict(calc.os.environ, {name: 'first'}):
                before = session.fingerprint(str(binary))
                self.assertIsNotNone(before)
                calc.os.environ[name] = 'second'
                self.assertNotEqual(before, session.fingerprint(str(binary)))

    def test_unknown_layout_and_bootstrap_overrides_have_no_fingerprint(self):
        binary = self.install()
        opaque = self.root / 'opaque-soffice'
        opaque.write_text('custom forwarding script')
        session = calc.CalculationSession()
        self.assertIsNone(session.fingerprint(str(opaque)))
        self.assertIsNone(session.fingerprint(str(self.root / 'missing')))
        for name in ('URE_BOOTSTRAP', 'UNO_SERVICES', 'UNO_TYPES', 'UNO_PATH',
                     'URE_MORE_SERVICES', 'URE_MORE_TYPES', 'BRAND_BASE_DIR',
                     'BRAND_INI_DIR', 'SAL_CONFIGFILE'):
            with self.subTest(override=name), mock.patch.dict(calc.os.environ, {name: ''}):
                self.assertIsNone(session.fingerprint(str(binary)))

    def test_uninspectable_or_dangling_install_identity_is_unknown(self):
        binary = self.install()
        bootstrap = binary.parent / 'bootstraprc'
        original_lstat = Path.lstat
        def uninspectable(path):
            if path == bootstrap:
                raise PermissionError('cannot inspect bootstrap')
            return original_lstat(path)
        with mock.patch.object(Path, 'lstat', autospec=True, side_effect=uninspectable):
            self.assertIsNone(calc.CalculationSession().fingerprint(str(binary)))
        bootstrap.symlink_to(self.root / 'missing-target')
        self.assertIsNone(calc.CalculationSession().fingerprint(str(binary)))

    def test_unknown_fingerprint_never_records_or_reuses_success(self):
        session = calc.CalculationSession(str(self.receipt), 'task')
        session.record(None, 'v')
        self.assertFalse(self.receipt.exists())
        self.assertEqual(session.passed, {})
        session.record('previous-known-identity', 'v')
        with mock.patch.object(calc, 'find_soffice', return_value='/fake/soffice'), \
             mock.patch.object(session, 'fingerprint', return_value=None), \
             mock.patch.object(calc, 'get_libreoffice_version', return_value='version-only'), \
             mock.patch.object(calc, 'recalculate', side_effect=calculated_control) as run:
            for _ in range(2):
                code, message = calc.preflight(session=session)
                self.assertEqual(code, 0)
                self.assertNotIn('REUSED', message)
            self.assertEqual(run.call_count, 2)
        self.assertIsNone(session.load(None))
        self.assertFalse(self.receipt.exists())
        self.assertEqual(session.passed, {})

    def test_environment_change_during_control_never_records_success(self):
        session = calc.CalculationSession(str(self.receipt), 'task')
        with mock.patch.object(calc, 'find_soffice', return_value='/fake/soffice'), \
             mock.patch.object(session, 'fingerprint', side_effect=['before', 'after']), \
             mock.patch.object(calc, 'recalculate', side_effect=calculated_control):
            self.assertEqual(calc.preflight(session=session)[0], 1)
        self.assertFalse(self.receipt.exists())
        self.assertEqual(session.passed, {})

    def test_no_receipt_candidates_skip_capability_fingerprint_and_always_execute(self):
        binary = self.install()
        candidate = self.root / 'candidate.xlsx'
        candidate.write_bytes(b'candidate input')
        session = calc.CalculationSession()
        def conversion(cmd, **kwargs):
            outdir = Path(cmd[cmd.index('--outdir') + 1])
            (outdir / 'candidate.xlsx').write_bytes(Path(cmd[-1]).read_bytes())
            return calc.subprocess.CompletedProcess(cmd, 0, b'', b'')
        with mock.patch.object(calc, 'find_soffice', return_value=str(binary)), \
             mock.patch.object(session, 'fingerprint', side_effect=AssertionError('unneeded fingerprint')), \
             mock.patch.object(calc, 'get_libreoffice_version', return_value='version-only') as version, \
             mock.patch.object(calc, '_run_soffice', side_effect=conversion) as engine:
            for name in ('first.xlsx', 'second.xlsx'):
                self.assertTrue(calc.recalculate(str(candidate), str(self.root / name), session=session)[0])
            self.assertEqual(engine.call_count, 2)
            version.assert_called_once()
        self.assertEqual(session.passed, {})  # A version/output is not control evidence.

    def test_version_cache_is_session_local_and_invalidates_on_executable_change(self):
        binary = self.install()
        session = calc.CalculationSession(task_id='task')
        with mock.patch.object(calc, 'get_libreoffice_version', return_value='version-only') as version:
            session.version(str(binary))
            session.version(str(binary))
            self.assertEqual(version.call_count, 1)
            binary.write_text('changed executable and size')
            session.version(str(binary))
            self.assertEqual(version.call_count, 2)
            calc.CalculationSession(task_id='other-task').version(str(binary))
            self.assertEqual(version.call_count, 3)
        self.assertEqual(session.passed, {})

    def test_real_control_verifier_requires_live_formula_and_nonzero_cache(self):
        original, output = self.root / 'input.xlsx', self.root / 'output.xlsx'
        calc._write_preflight_workbook(original)
        with self.assertRaisesRegex(ValueError, 'numeric cache'):
            calc._verify_preflight_output(original)  # copying empty cache cannot pass
        calculated_control(original, output)
        calc._verify_preflight_output(output)
        with zipfile.ZipFile(output) as package:
            payloads = {name: package.read(name) for name in package.namelist()}
        for altered in (b'<v>0</v>', b'<v>42</v>'):
            root = ET.fromstring(payloads['xl/worksheets/sheet1.xml'])
            cell = root.find(f'{calc.S}sheetData/{calc.S}row/{calc.S}c[@r="C1"]')
            if altered == b'<v>0</v>':
                cell.find(f'{calc.S}v').text = '0'
            else:
                cell.remove(cell.find(f'{calc.S}f'))
            with zipfile.ZipFile(output, 'w') as package:
                for name, data in payloads.items():
                    package.writestr(name, ET.tostring(root) if name.endswith('sheet1.xml') else data)
            with self.assertRaises(ValueError):
                calc._verify_preflight_output(output)

    def test_success_receipt_reused_only_same_task_and_fingerprint(self):
        first = calc.CalculationSession(str(self.receipt), 'task-A')
        with mock.patch.object(calc, 'find_soffice', return_value='/fake/soffice'), \
             mock.patch.object(calc.CalculationSession, 'fingerprint', return_value='environment-1'), \
             mock.patch.object(calc, 'get_libreoffice_version', return_value='test-version') as version, \
             mock.patch.object(calc, 'recalculate', side_effect=calculated_control) as run:
            self.assertEqual(calc.preflight(session=first)[0], 0)
            code, message = calc.preflight(session=calc.CalculationSession(str(self.receipt), 'task-A'))
            self.assertEqual(code, 0)
            self.assertIn('REUSED', message)
            self.assertEqual(run.call_count, 1)
            self.assertEqual(version.call_count, 1)
            self.assertEqual(calc.preflight(session=calc.CalculationSession(str(self.receipt), 'task-B'))[0], 0)
            self.assertEqual(run.call_count, 2)
        with mock.patch.object(calc, 'find_soffice', return_value='/fake/soffice'), \
             mock.patch.object(calc.CalculationSession, 'fingerprint', return_value='environment-2'), \
             mock.patch.object(calc, 'get_libreoffice_version', return_value='test-version'), \
             mock.patch.object(calc, 'recalculate', side_effect=calculated_control) as run:
            self.assertEqual(calc.preflight(session=calc.CalculationSession(str(self.receipt), 'task-B'))[0], 0)
            self.assertEqual(run.call_count, 1)

    def test_failure_invalidates_and_never_creates_success_receipt(self):
        session = calc.CalculationSession(str(self.receipt), 'task')
        with mock.patch.object(calc, 'find_soffice', return_value='/fake/soffice'), \
             mock.patch.object(session, 'fingerprint', return_value='fingerprint'), \
             mock.patch.object(calc, 'recalculate', return_value=(False, 'no output')) as run:
            self.assertEqual(calc.preflight(session=session)[0], 1)
            self.assertFalse(self.receipt.exists())
            self.assertEqual(run.call_count, 1)
        session.record('fingerprint', 'v')
        with mock.patch.object(calc, '_recalculate', return_value=(False, 'candidate failed')):
            self.assertFalse(calc.recalculate('input', 'output', session=session)[0])
        self.assertFalse(self.receipt.exists())

    def test_copy_only_or_source_modified_control_cannot_create_receipt(self):
        session = calc.CalculationSession(str(self.receipt), 'task')
        def copy_only(source, output, **kwargs):
            Path(output).write_bytes(Path(source).read_bytes())
            return True, 'only copied input'
        def modifies_source(source, output, **kwargs):
            result = calculated_control(source, output)
            Path(source).write_bytes(b'changed original')
            return result
        for engine in (copy_only, modifies_source):
            with mock.patch.object(calc, 'find_soffice', return_value='/fake/soffice'), \
                 mock.patch.object(session, 'fingerprint', return_value='fingerprint'), \
                 mock.patch.object(calc, 'recalculate', side_effect=engine):
                self.assertEqual(calc.preflight(session=session)[0], 1)
                self.assertFalse(self.receipt.exists())

    def test_candidates_are_never_reused_and_version_is_cached_in_explicit_session(self):
        session = calc.CalculationSession()
        candidate = self.root / 'candidate.xlsx'
        candidate.write_bytes(b'first input')
        with mock.patch.object(session, 'fingerprint', return_value='same'), \
             mock.patch.object(calc, 'get_libreoffice_version', return_value='v') as version:
            self.assertEqual(session.version('soffice'), 'v')
            self.assertEqual(session.version('soffice'), 'v')
            version.assert_called_once()
        with mock.patch.object(calc, '_recalculate', return_value=(True, 'actually executed')) as run:
            calc.recalculate(str(candidate), 'out1', session=session)
            candidate.write_bytes(b'changed input/formulas after save')
            calc.recalculate(str(candidate), 'out2', session=session)
            self.assertEqual(run.call_count, 2)

    def test_fingerprint_changes_for_engine_calc_registry_and_environment(self):
        program = self.root / 'install/program'
        registry = self.root / 'install/share/registry'
        program.mkdir(parents=True)
        registry.mkdir(parents=True)
        binary = program / 'soffice'
        binary.write_text('engine')
        component = registry / 'calc.xcd'
        component.write_text('Calc component')
        session = calc.CalculationSession(task_id='one')
        first = session.fingerprint(str(binary))
        component.write_text('changed installed Calc component')
        second = session.fingerprint(str(binary))
        self.assertNotEqual(first, second)
        with mock.patch.dict(calc.os.environ, {'LANG': 'test-locale'}):
            self.assertNotEqual(second, session.fingerprint(str(binary)))
        self.assertNotEqual(second, calc.CalculationSession(task_id='two').fingerprint(str(binary)))

    def test_malformed_expired_and_mismatched_receipts_are_not_success(self):
        session = calc.CalculationSession(str(self.receipt), 'task')
        with self.assertRaises(ValueError):
            calc.CalculationSession(str(self.receipt))
        for value in ('[]', '{}', '{"checked_at":"bad"}', 'not json'):
            self.receipt.write_text(value)
            self.assertIsNone(session.load('fingerprint'))
        self.receipt.unlink()
        with mock.patch.object(calc.time, 'time', return_value=1000):
            session.record('fingerprint', 'version')
        with mock.patch.object(calc.time, 'time', return_value=10000):
            self.assertIsNone(session.load('fingerprint'))

    def test_receipt_cannot_overwrite_or_delete_candidate_or_unrelated_file(self):
        source = self.root / 'source.xlsx'
        source.write_bytes(b'preserve original workbook')
        session = calc.CalculationSession(str(source), 'task')
        with mock.patch.object(calc, '_recalculate', side_effect=AssertionError('must not execute')):
            self.assertFalse(calc.recalculate(str(source), str(self.root / 'output.xlsx'), session=session)[0])
        session.invalidate()
        self.assertEqual(source.read_bytes(), b'preserve original workbook')
        with self.assertRaisesRegex(ValueError, 'refusing overwrite'):
            session.record('fingerprint', 'version')
        self.assertEqual(source.read_bytes(), b'preserve original workbook')

    def test_recalculation_refuses_source_path_and_hardlink(self):
        source = self.root / 'source.xlsx'
        source.write_bytes(b'preserve me')
        alias = self.root / 'alias.xlsx'
        alias.hardlink_to(source)
        with mock.patch.object(calc, 'find_soffice', side_effect=AssertionError('must stop before engine')):
            self.assertFalse(calc.recalculate(str(source), str(source))[0])
            self.assertFalse(calc.recalculate(str(source), str(alias))[0])
        self.assertEqual(source.read_bytes(), b'preserve me')


if __name__ == '__main__':
    unittest.main()
