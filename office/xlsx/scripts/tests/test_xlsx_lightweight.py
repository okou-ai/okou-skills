#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Stdlib-only reader regression tests; run directly or with unittest discovery."""
import contextlib
import csv
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import xlsx_lightweight as light
import xlsx_reader as reader

S = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
P = 'http://schemas.openxmlformats.org/package/2006/relationships'


def workbook(path):
    parts = {
        '_rels/.rels': f'<Relationships xmlns="{P}"><Relationship Id="office" Type="{R}/officeDocument" Target="custom/book.xml"/></Relationships>',
        'custom/book.xml': f'<workbook xmlns="{S}" xmlns:r="{R}"><workbookPr date1904="1"/><sheets><sheet name="财务" sheetId="91" r:id="rZ"/><sheet name="Other" sheetId="2" r:id="rA"/></sheets></workbook>',
        'custom/_rels/book.xml.rels': f'<Relationships xmlns="{P}"><Relationship Id="rA" Type="{R}/worksheet" Target="/tabs/second.xml"/><Relationship Id="rZ" Type="{R}/worksheet" Target="../tabs/not-sheet1.xml"/><Relationship Id="strings" Type="{R}/sharedStrings" Target="../data/text.xml"/><Relationship Id="styles" Type="{R}/styles" Target="../data/style.xml"/></Relationships>',
        'data/text.xml': f'<sst xmlns="{S}"><si><r><t>编号</t></r><r><t>甲</t></r><rPh><t>NOT TEXT</t></rPh></si><si><t>00001234567890123456789</t></si></sst>',
        'data/style.xml': f'<styleSheet xmlns="{S}"><numFmts count="1"><numFmt numFmtId="164" formatCode="000000"/></numFmts><cellXfs count="4"><xf numFmtId="0"/><xf numFmtId="14"/><xf numFmtId="164"/><xf numFmtId="999"/></cellXfs></styleSheet>',
        'tabs/not-sheet1.xml': f'<worksheet xmlns="{S}"><sheetData><row r="1"><c r="A1" t="s"><v>0</v></c><c r="B1" t="inlineStr"><is><t>00123 中文</t></is></c></row><row r="3"><c r="B3" t="s"><v>1</v></c><c r="D3" s="2"><v>123</v></c><c r="F3"><f>SUM(A1:B1)</f><v/></c><c r="G3"><f>1+1</f></c><c r="H3"><f>1-1</f><v>0</v></c></row><row r="8"><c r="C8" s="1"><v>45292</v></c><c r="D8" s="3"><v>3</v></c><c r="E8" t="alien"><v>99</v></c><c r="F8" t="b"><v>1</v></c><c r="G8" t="d"><v>2024-01-01</v></c></row><row r="9000"><c r="A9000"><v>99</v></c></row></sheetData></worksheet>',
        'tabs/second.xml': f'<worksheet xmlns="{S}"><sheetData><row r="7"><c r="C7" t="inlineStr"><is><t>second</t></is></c></row></sheetData></worksheet>',
        'xl/vbaProject.bin': b'opaque VBA bytes, never executed',
    }
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as package:
        for name, value in parts.items():
            package.writestr(name, value)


class ReaderTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'book.xlsm'
        workbook(self.path)

    def test_inventory_never_opens_worksheets_strings_or_styles(self):
        original = zipfile.ZipFile.open
        def guard(package, name, *args, **kwargs):
            self.assertNotIn(str(name), ['tabs/not-sheet1.xml', 'tabs/second.xml', 'data/text.xml', 'data/style.xml'])
            return original(package, name, *args, **kwargs)
        with mock.patch.object(zipfile.ZipFile, 'open', guard):
            data = light.inspect_file(self.path, inventory=True)
        self.assertEqual([s['name'] for s in data['sheets']], ['财务', 'Other'])
        self.assertEqual(data['sheets'][0]['part'], 'tabs/not-sheet1.xml')
        self.assertEqual(data['date_system'], '1904')
        self.assertFalse(data['previews'])

    def test_default_and_cli_work_without_site_packages(self):
        before = self.path.read_bytes()
        result = subprocess.run([sys.executable, '-S', str(SCRIPTS / 'xlsx_reader.py'), str(self.path), '--json'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(list(data['previews']), ['财务'])
        cells = {c['address']: c for c in data['previews']['财务']['cells']}
        self.assertEqual(cells['A1']['value'], '编号甲')
        self.assertEqual(cells['B1']['value'], '00123 中文')
        self.assertNotIn('C8', cells)
        self.assertEqual(before, self.path.read_bytes())

    def test_range_addresses_identifiers_formats_and_unknown_caches(self):
        data = light.inspect_file(self.path, cell_range='$B$3:H8')
        cells = {c['address']: c for c in data['previews']['财务']['cells']}
        self.assertEqual(cells['B3']['value'], '00001234567890123456789')
        self.assertEqual(cells['D3']['number_format'], '000000')
        self.assertEqual(cells['D3']['value'], '123')  # not invented 000123 identifier
        self.assertEqual(cells['F3']['cache_status'], 'blank')
        self.assertEqual(cells['G3']['cache_status'], 'missing')
        self.assertIsNone(cells['F3']['value'])
        self.assertEqual(cells['H3']['value'], '0')
        self.assertEqual(cells['C8']['value'], '45292')  # no guessed date conversion
        self.assertEqual(cells['C8']['num_fmt_id'], 14)
        self.assertFalse(cells['D8']['format_known'])
        self.assertIsNone(cells['E8']['value'])
        self.assertEqual(cells['E8']['raw_value'], '99')
        self.assertIs(cells['F8']['value'], True)
        self.assertEqual(cells['G8']['value'], '2024-01-01')
        self.assertNotIn('A9000', cells)

    def test_other_sheet_relationship_and_sparse_rows(self):
        data = light.inspect_file(self.path, sheet_name='Other', cell_range='C7')
        self.assertEqual(data['previews']['Other']['cells'][0]['value'], 'second')
        with self.assertRaisesRegex(ValueError, 'Unknown sheet'):
            light.inspect_file(self.path, sheet_name='Nope')
        for value in ('XFE1', 'A0', 'A1048577', 'D3:A1', 'A1:ZZ10000'):
            with self.subTest(value=value), self.assertRaises(ValueError):
                light.bounds(value)

    def test_preview_stops_before_unrequested_trailing_xml(self):
        # Invalid late rows must not be parsed by a first-row-only preview.
        path = Path(self.tmp.name) / 'stop.xlsx'
        workbook(path)
        with zipfile.ZipFile(path) as package:
            payloads = {name: package.read(name) for name in package.namelist()}
        payloads['tabs/not-sheet1.xml'] = f'<worksheet xmlns="{S}"><sheetData><row r="1"><c r="A1"><v>7</v></c></row>' + (' ' * 100000) + '<row r="9000"><BROKEN'
        with zipfile.ZipFile(path, 'w') as package:
            for name, data in payloads.items():
                package.writestr(name, data)
        data = light.inspect_file(path, rows=1)
        self.assertEqual(data['previews']['财务']['cells'][0]['value'], '7')

    def test_last_requested_cell_stops_within_row(self):
        path = Path(self.tmp.name) / 'within-row.xlsx'
        workbook(path)
        with zipfile.ZipFile(path) as package:
            payloads = {name: package.read(name) for name in package.namelist()}
        payloads['tabs/not-sheet1.xml'] = f'<worksheet xmlns="{S}"><sheetData><row r="1"><c r="A1"><v>8</v></c>' + (' ' * 100000) + '<c r="B1"><BROKEN'
        with zipfile.ZipFile(path, 'w') as package:
            for name, data in payloads.items():
                package.writestr(name, data)
        cells = light.inspect_file(path, cell_range='A1')['previews']['财务']['cells']
        self.assertEqual(cells[0]['value'], '8')

    def test_shared_formula_metadata_and_cached_boolean(self):
        path = Path(self.tmp.name) / 'shared.xlsx'
        workbook(path)
        with zipfile.ZipFile(path) as package:
            payloads = {name: package.read(name) for name in package.namelist()}
        payloads['tabs/not-sheet1.xml'] = f'<worksheet xmlns="{S}"><sheetData><row r="5"><c r="D5"><f t="shared" si="7"/><v/></c><c r="E5" t="b"><f>1=1</f><v>1</v></c></row></sheetData></worksheet>'
        with zipfile.ZipFile(path, 'w') as package:
            for name, data in payloads.items():
                package.writestr(name, data)
        cells = light.inspect_file(path, cell_range='D5:E5')['previews']['财务']['cells']
        self.assertIsNone(cells[0]['formula'])
        self.assertEqual(cells[0]['formula_attributes'], {'t': 'shared', 'si': '7'})
        self.assertEqual(cells[0]['cache_status'], 'blank')
        self.assertIs(cells[1]['value'], True)

    def test_csv_tsv_strings_and_bounded_records(self):
        path = Path(self.tmp.name) / 'ids.tsv'
        path.write_text('编号\t文本\n000123\t中文\n999\t后续\n"bad unterminated', encoding='utf-8')
        result = light.inspect_file(path, rows=2)
        self.assertEqual([c['value'] for c in result['previews']['ids']['cells']], ['编号', '文本', '000123', '中文'])
        with mock.patch.object(Path, 'open', side_effect=AssertionError('must not open CSV inventory')):
            light.inspect_file(path, inventory=True)

    def test_csv_only_decode_errors_retry(self):
        path = Path(self.tmp.name) / 'bad.csv'
        path.write_text('"unterminated', encoding='utf-8')
        original = Path.open
        opens = []
        def counted(p, *a, **kw):
            opens.append(kw.get('encoding'))
            return original(p, *a, **kw)
        with mock.patch.object(Path, 'open', counted), self.assertRaises(csv.Error):
            light.csv_preview(path, light.bounds())
        self.assertEqual(opens, ['utf-8-sig'])
        with mock.patch.object(Path, 'open', side_effect=PermissionError('denied')) as opened:
            with self.assertRaises(PermissionError):
                light.csv_preview(path, light.bounds())
            self.assertEqual(opened.call_count, 1)
        path.write_bytes('中文'.encode('gbk'))
        values, encoding = light.csv_preview(path, light.bounds())
        self.assertEqual(encoding, 'gbk')
        self.assertEqual(values[0]['value'], '中文')

    def test_full_analysis_and_quality_are_explicit_compatible_modes(self):
        for flag, stats_expected in [('--analyze', True), ('--quality', False)]:
            with mock.patch.object(sys, 'argv', ['reader', str(self.path), flag, '--sheet', '财务', '--json']), \
                 mock.patch.object(reader, 'detect_and_load', return_value={'财务': object()}) as load, \
                 mock.patch.object(reader, 'explore_structure', return_value={'财务': {}}), \
                 mock.patch.object(reader, 'audit_quality', return_value={'财务': []}) as quality, \
                 mock.patch.object(reader, 'compute_stats', return_value={}) as stats, \
                 contextlib.redirect_stdout(io.StringIO()) as output:
                reader.main()
                load.assert_called_once_with(str(self.path), sheet_name_filter='财务')
                quality.assert_called_once()
                self.assertEqual(stats.called, stats_expected)
                self.assertIn('structure', json.loads(output.getvalue()))

    def test_full_csv_does_not_retry_parser_errors(self):
        path = Path(self.tmp.name) / 'data.csv'
        path.write_text('a\n1\n')
        pandas = mock.Mock()
        pandas.read_csv.side_effect = ValueError('bad parser configuration')
        with mock.patch.dict(sys.modules, {'pandas': pandas}), self.assertRaisesRegex(ValueError, 'bad parser'):
            reader.detect_and_load(str(path))
        self.assertEqual(pandas.read_csv.call_count, 1)


if __name__ == '__main__':
    unittest.main()
