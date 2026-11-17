#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Stdlib-only preservation and package-path regression tests."""
import contextlib
import io
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
from xlsx_package import replace_parts, pack_directory, safe_member
from xlsx_unpack import unpack


class NonSeekable(io.BytesIO):
    def seekable(self):
        return False
    def seek(self, *args):
        raise io.UnsupportedOperation()


def original(path):
    stream = NonSeekable()  # exercise unchanged data-descriptor flag/record preservation
    with zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED) as package:
        package.comment = b'archive comment'
        for name, value in {
            '[Content_Types].xml': b'<Types/>',
            'xl/workbook.xml': b'<?xml version="1.0"?><workbook   keep="spacing" />',
            'xl/worksheets/main.xml': b'<worksheet><f>SUM(A1:B1)</f><v>42</v></worksheet>',
            'xl/vbaProject.bin': bytes(range(256)) * 30,
            'xl/media/image.png': b'opaque image bytes',
        }.items():
            info = zipfile.ZipInfo(name, (2020, 2, 3, 4, 5, 6))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.comment = b'member comment'
            info.extra = b'\xfe\xca\x02\x00xy'
            info.external_attr = 0o100640 << 16
            package.writestr(info, value)
    path.write_bytes(stream.getvalue())


def records(path):
    raw = path.read_bytes()
    with zipfile.ZipFile(path) as package:
        infos = sorted(package.infolist(), key=lambda i: i.header_offset)
        return {i.filename: raw[i.header_offset:(infos[n + 1].header_offset if n + 1 < len(infos) else package.start_dir)]
                for n, i in enumerate(infos)}


class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.base = self.root / 'source.xlsm'
        original(self.base)
        self.replacement = self.root / 'new.xml'
        self.replacement.write_bytes(b'<worksheet><f>SUM(A1:B1)</f><v>44</v></worksheet>')
        self.output = self.root / 'result.xlsm'

    def test_unchanged_content_metadata_and_local_records_survive(self):
        before = self.base.read_bytes()
        replace_parts(str(self.base), {'xl/worksheets/main.xml': str(self.replacement)}, str(self.output))
        self.assertEqual(self.base.read_bytes(), before)
        source_records, output_records = records(self.base), records(self.output)
        with zipfile.ZipFile(self.base) as source, zipfile.ZipFile(self.output) as result:
            self.assertIsNone(result.testzip())
            self.assertEqual(source.comment, result.comment)
            for name in source.namelist():
                if name == 'xl/worksheets/main.xml':
                    self.assertIn(b'<f>SUM(A1:B1)</f>', result.read(name))
                    continue
                self.assertEqual(source.read(name), result.read(name))
                self.assertEqual(source_records[name], output_records[name])
                a, b = source.getinfo(name), result.getinfo(name)
                for field in ('date_time', 'compress_type', 'comment', 'extra', 'create_system', 'external_attr', 'internal_attr', 'flag_bits', 'CRC', 'file_size', 'compress_size'):
                    self.assertEqual(getattr(a, field), getattr(b, field), (name, field))

    def test_non_ascii_local_and_directory_names_keep_encoding_and_flags(self):
        class LegacyNameInfo(zipfile.ZipInfo):
            def _encodeFilenameFlags(self):
                return self.filename.encode('cp437'), self.flag_bits

        names = ('xl/media/café.bin', 'xl/media/中文.bin')
        with zipfile.ZipFile(self.base, 'a') as package:
            package.writestr(LegacyNameInfo(names[0]), b'legacy opaque member')
            package.writestr(names[1], b'utf8 opaque member')
        before = self.base.read_bytes()
        source_records = records(self.base)
        replace_parts(str(self.base), {'xl/worksheets/main.xml': str(self.replacement)}, str(self.output))
        self.assertEqual(self.base.read_bytes(), before)
        output_records = records(self.output)
        with zipfile.ZipFile(self.base) as source, zipfile.ZipFile(self.output) as result:
            self.assertIsNone(result.testzip())
            for name in names:
                self.assertEqual(source.read(name), result.read(name))
                self.assertEqual(source_records[name], output_records[name])
                self.assertEqual(source.getinfo(name).flag_bits, result.getinfo(name).flag_bits)

    def test_invalid_replacement_never_creates_or_overwrites_target(self):
        self.replacement.write_text('<broken')
        with self.assertRaises(ValueError):
            replace_parts(str(self.base), {'xl/worksheets/main.xml': str(self.replacement)}, str(self.output))
        self.assertFalse(self.output.exists())
        self.output.write_bytes(b'existing sentinel')
        with self.assertRaises(ValueError):
            replace_parts(str(self.base), {'xl/worksheets/main.xml': str(self.replacement)}, str(self.output))
        self.assertEqual(self.output.read_bytes(), b'existing sentinel')

    def test_refuses_source_overwrite_missing_parts_and_traversal(self):
        before = self.base.read_bytes()
        for name in ('../escape.xml', '/absolute.xml', 'a\\b.xml', 'a/./b.xml', 'a//b.xml', 'C:/x.xml', 'missing.xml'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                replace_parts(str(self.base), {name: str(self.replacement)}, str(self.output))
        with self.assertRaises(ValueError):
            replace_parts(str(self.base), {'xl/worksheets/main.xml': str(self.replacement)}, str(self.base))
        self.assertEqual(self.base.read_bytes(), before)
        self.assertFalse(self.output.exists())

    def test_rejects_unsafe_duplicate_and_symlink_zip_members(self):
        for mode in ('unsafe', 'duplicate', 'symlink'):
            bad = self.root / (mode + '.xlsx')
            with warnings.catch_warnings(), zipfile.ZipFile(bad, 'w') as package:
                warnings.simplefilter('ignore', UserWarning)
                if mode == 'unsafe':
                    package.writestr('../escape.xml', '<a/>')
                elif mode == 'duplicate':
                    package.writestr('same.xml', '<a/>')
                    package.writestr('same.xml', '<a/>')
                else:
                    info = zipfile.ZipInfo('link.xml')
                    info.create_system = 3
                    info.external_attr = (stat.S_IFLNK | 0o777) << 16
                    package.writestr(info, 'target')
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                unpack(str(bad), str(self.root / ('out-' + mode)))
            self.assertFalse((self.root / 'escape.xml').exists())

    def test_legacy_unpack_pack_no_pretty_reserialization(self):
        directory = self.root / 'unpacked'
        unpack(str(self.base), str(directory))
        with zipfile.ZipFile(self.base) as package:
            for name in package.namelist():
                self.assertEqual((directory / name).read_bytes(), package.read(name))
        self.assertEqual(pack_directory(str(directory), str(self.output)), 5)
        with self.assertRaises(ValueError):
            unpack(str(self.base), str(directory))
        with self.assertRaises(ValueError):
            pack_directory(str(directory), str(directory / 'nested.xlsx'))
        with zipfile.ZipFile(self.output) as package:
            self.assertIn(b'keep="spacing"', package.read('xl/workbook.xml'))

    def test_pretty_is_opt_in_and_legacy_cli_is_usable(self):
        directory = self.root / 'pretty'
        unpack(str(self.base), str(directory), pretty=True)
        self.assertIn(b'\n', (directory / 'xl/workbook.xml').read_bytes())
        result = subprocess.run([sys.executable, '-S', str(SCRIPTS / 'xlsx_pack.py'), str(directory), str(self.output)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f'python3 formula_check.py {self.output}', result.stdout)
        fresh = self.root / 'scoped.xlsx'
        result = subprocess.run([sys.executable, '-S', str(SCRIPTS / 'xlsx_pack.py'), '--base', str(self.base), '--part', 'xl/worksheets/main.xml=' + str(self.replacement), str(fresh)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(f'python3 formula_check.py {fresh}', result.stdout)

    def test_unpack_retains_key_file_inventory_and_detected_risk_warnings(self):
        with zipfile.ZipFile(self.base, 'a') as package:
            package.writestr('xl/pivotTables/pivot1.xml', '<pivot/>')
            package.writestr('xl/charts/chart1.xml', '<chart/>')
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            unpack(str(self.base), str(self.root / 'inventory'))
        summary = output.getvalue()
        for expected in ('Key files to inspect/edit:', '[Package root]', '[Workbook]',
                         'xl/workbook.xml', 'xl/worksheets/main.xml',
                         'VBA macros — DO NOT modify', 'Pivot tables — update source ranges',
                         'Charts — update data ranges'):
            with self.subTest(expected=expected):
                self.assertIn(expected, summary)

    def test_source_symlinks_and_duplicate_cli_parts_rejected(self):
        directory = self.root / 'source-dir'
        directory.mkdir()
        (directory / '[Content_Types].xml').write_text('<Types/>')
        (directory / 'outside.xml').symlink_to(self.replacement)
        with self.assertRaises(ValueError):
            pack_directory(str(directory), str(self.output))
        part = 'xl/worksheets/main.xml=' + str(self.replacement)
        result = subprocess.run([sys.executable, '-S', str(SCRIPTS / 'xlsx_pack.py'), '--base', str(self.base), '--part', part, '--part', part, str(self.output)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.output.exists())


if __name__ == '__main__':
    unittest.main()
