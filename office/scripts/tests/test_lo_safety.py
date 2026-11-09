"""Stdlib fixtures/fake runners only; no LibreOffice/AI/network needed."""
import importlib.util
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET
import zipfile

OFFICE = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(OFFICE / 'scripts'))
import lo_safety as safety


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, OFFICE / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


calc = load('test_calc', 'xlsx/scripts/libreoffice_recalc.py')
writer = load('test_writer', 'docx/scripts/render_docx.py')


def rewrite(path, additions):
    with zipfile.ZipFile(path) as package:
        parts = {i.filename: package.read(i) for i in package.infolist()}
    parts.update(additions)
    with zipfile.ZipFile(path, 'w') as package:
        for name, value in parts.items():
            package.writestr(name, value)


def docx(path):
    with zipfile.ZipFile(path, 'w') as package:
        package.writestr('[Content_Types].xml', '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        package.writestr('_rels/.rels', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="r1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        package.writestr('word/document.xml', '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body/></w:document>')


class SafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.xlsx = self.root / 'source.xlsx'
        calc._write_preflight_workbook(self.xlsx)

    def test_plain_and_copy_preserve_source(self):
        before = self.xlsx.read_bytes()
        copied = safety.prepare_input(self.xlsx, self.root / 'private')
        self.assertNotEqual(copied, self.xlsx)
        self.assertEqual(before, self.xlsx.read_bytes())
        self.assertEqual(before, copied.read_bytes())

    def test_profiles_disable_macros_and_links_retain_recalc(self):
        profile = self.root / 'profile'
        safety.configure_lo_profile(profile, calc_recalculate=True)
        root = ET.parse(profile / 'user/registrymodifications.xcu').getroot()
        ns = '{http://openoffice.org/2001/registry}'
        values = {(i.get(ns+'path'), p.get(ns+'name')): p.findtext('value')
                  for i in root for p in i}
        scripting = '/org.openoffice.Office.Common/Security/Scripting'
        self.assertEqual(values[scripting, 'DisableMacrosExecution'], 'true')
        self.assertEqual(values[scripting, 'DisableActiveContent'], 'true')
        self.assertEqual(values['/org.openoffice.Office.Calc/Content/Update', 'Link'], '1')
        self.assertEqual(values['/org.openoffice.Office.Writer/Content/Update', 'Link'], '2')
        self.assertEqual(values['/org.openoffice.Office.Calc/Formula/Load', 'OOXMLRecalcMode'], '0')
        with self.assertRaises(FileExistsError):
            safety.configure_lo_profile(profile)

    def test_existing_same_symlink_and_hardlink_outputs_untouched(self):
        for target in [self.xlsx, self.root / 'existing.xlsx', self.root / 'symbolic.xlsx', self.root / 'hard.xlsx']:
            if target.name == 'existing.xlsx':
                target.write_bytes(b'precious')
            elif target.name == 'symbolic.xlsx':
                target.symlink_to(self.root / 'absent.xlsx')
            elif target.name == 'hard.xlsx':
                target.hardlink_to(self.xlsx)
            before = self.xlsx.read_bytes()
            with self.assertRaises((OSError, safety.SafetyError)):
                with safety.reserve_output(target, source=self.xlsx):
                    self.fail('must refuse existing destination')
            self.assertEqual(self.xlsx.read_bytes(), before)
        self.assertEqual((self.root / 'existing.xlsx').read_bytes(), b'precious')
        self.assertFalse((self.root / 'absent.xlsx').exists())

    def test_failure_removes_only_reservation_and_publish(self):
        output = self.root / 'out.xlsx'
        with self.assertRaises(RuntimeError):
            with safety.reserve_output(output):
                raise RuntimeError('engine failed')
        self.assertFalse(output.exists())
        with safety.reserve_output(output) as reserved:
            reserved.publish(self.xlsx)
        self.assertEqual(output.read_bytes(), self.xlsx.read_bytes())

    def test_active_and_malformed_packages_refused(self):
        for part, content in [('xl/vbaProject.bin', b'x'), ('xl/embeddings/object.bin', b'x'),
                              ('xl/connections.xml', b'<connections/>'), ('../evil.xml', b'<x/>'),
                              ('evil.xml', b'<!DOCTYPE x [<!ENTITY y "x">]><x>&y;</x>')]:
            with self.subTest(part=part):
                calc._write_preflight_workbook(self.xlsx)
                rewrite(self.xlsx, {part: content})
                with self.assertRaises(safety.SafetyError):
                    safety.validate_ooxml(self.xlsx)

    def test_external_resources_refused_but_hyperlinks_allowed(self):
        for kind, target, allowed in [('hyperlink', 'https://example.com/', True),
                                      ('hyperlink', 'mailto:test@example.com', True),
                                      ('image', 'https://example.com/pixel.png', False),
                                      ('attachedTemplate', 'https://example.com/a.dotm', False),
                                      ('hyperlink', 'file:///tmp/local', False)]:
            with self.subTest(kind=kind, target=target):
                rel = f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="r1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/{kind}" Target="{target}" TargetMode="External"/></Relationships>'
                calc._write_preflight_workbook(self.xlsx)
                rewrite(self.xlsx, {'xl/_rels/extra.xml.rels': rel})
                if allowed:
                    safety.validate_ooxml(self.xlsx)
                else:
                    with self.assertRaises(safety.SafetyError):
                        safety.validate_ooxml(self.xlsx)

    def test_split_word_field_refused(self):
        path = self.root / 'input.docx'
        docx(path)
        rewrite(path, {'word/document.xml': '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:instrText>INCLUDE</w:instrText><w:instrText>TEXT "http://example.com"</w:instrText></w:document>'})
        with self.assertRaises(safety.SafetyError):
            safety.validate_ooxml(path)

    def test_replaced_reservation_is_not_deleted_or_overwritten(self):
        output = self.root / 'out.xlsx'
        with safety.reserve_output(output) as reserved:
            output.unlink()
            output.write_bytes(b'another writer')
            with self.assertRaises(safety.SafetyError):
                reserved.publish(self.xlsx)
        self.assertEqual(output.read_bytes(), b'another writer')

    def test_external_formula_refused(self):
        with zipfile.ZipFile(self.xlsx) as package:
            sheet = package.read('xl/worksheets/sheet1.xml')
        rewrite(self.xlsx, {'xl/worksheets/sheet1.xml': sheet.replace(b'SUM(A1:B1)', b'WEBSERVICE("https://example.com")')})
        with self.assertRaises(safety.SafetyError):
            safety.validate_ooxml(self.xlsx)

    def test_fake_calc_copy_cannot_pass_preflight(self):
        calls = []
        def fake(cmd, timeout):
            copied = Path(cmd[-1])
            self.assertEqual(copied.name, 'input.xlsx')
            calls.append(cmd)
            out = Path(cmd[cmd.index('--outdir')+1]) / 'input.xlsx'
            shutil.copyfile(copied, out)
            return subprocess.CompletedProcess(cmd, 0, b'copied', b'')
        with patch.object(calc, 'find_soffice', return_value='fake'), patch.object(calc, 'get_libreoffice_version', return_value='fake'), patch.object(calc, '_run_soffice', side_effect=fake):
            status, message = calc.preflight()
        self.assertEqual(status, 1, message)
        self.assertIn('cache', message)
        self.assertEqual(len(calls), 1)

    def test_fake_calc_no_output_fails_and_cleans_reservation(self):
        out = self.root / 'out.xlsx'
        with patch.object(calc, 'find_soffice', return_value='fake'), patch.object(calc, 'get_libreoffice_version', return_value='fake'), patch.object(calc, '_run_soffice', return_value=subprocess.CompletedProcess([], 0, b'', b'')):
            ok, message = calc.recalculate(str(self.xlsx), str(out))
        self.assertFalse(ok, message)
        self.assertFalse(out.exists())

    def test_preflight_fake_numeric_without_live_formula_refused(self):
        with zipfile.ZipFile(self.xlsx) as package:
            sheet = package.read('xl/worksheets/sheet1.xml')
        rewrite(self.xlsx, {'xl/worksheets/sheet1.xml': sheet.replace(b'<ns0:f>SUM(A1:B1)</ns0:f>', b'').replace(b'<ns0:v />', b'<ns0:v>42</ns0:v>')})
        with self.assertRaises(ValueError):
            calc._verify_preflight_output(self.xlsx)

    def test_writer_uses_copy_profile_and_new_output(self):
        source, output = self.root / 'source.docx', self.root / 'out.pdf'
        docx(source)
        before = source.read_bytes()
        def fake(cmd, **kwargs):
            copied = Path(cmd[-1])
            self.assertNotEqual(copied, source)
            self.assertEqual(copied.read_bytes(), before)
            profile = Path(cmd[1].split('file://', 1)[1])
            self.assertIn('DisableMacrosExecution', (profile / 'user/registrymodifications.xcu').read_text())
            (Path(cmd[cmd.index('--outdir')+1]) / 'input.pdf').write_bytes(b'%PDF-1.4\nfixture')
            return subprocess.CompletedProcess(cmd, 0, '', '')
        with patch.object(writer.shutil, 'which', return_value='fake'), patch.object(writer.subprocess, 'run', side_effect=fake):
            writer.render(source, output)
        self.assertEqual(source.read_bytes(), before)
        self.assertTrue(output.read_bytes().startswith(b'%PDF-'))
        with patch.object(writer.subprocess, 'run') as runner:
            with self.assertRaises(FileExistsError):
                writer.render(source, output)
            runner.assert_not_called()


if __name__ == '__main__':
    unittest.main()
