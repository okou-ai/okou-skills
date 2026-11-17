"""Exercise explicit read-only tool entry points outside the skill directory."""

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile


OFFICE = Path(__file__).resolve().parents[1]
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
DOCREL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


class ReadOnlyRouteTests(unittest.TestCase):
    def setUp(self):
        work = tempfile.TemporaryDirectory(prefix="office-read-only-")
        self.addCleanup(work.cleanup)
        self.work = Path(work.name)
        guard = self.work / "guard"
        guard.mkdir()
        self.marker = self.work / "unexpected-setup.txt"
        (guard / "sitecustomize.py").write_text(
            "import os, sys\n"
            "class NoAuthoringDependencies:\n"
            "    def find_spec(self, fullname, path=None, target=None):\n"
            "        if fullname.split('.')[0] in {'pandas','openpyxl','reportlab','pypdf','pip'}:\n"
            "            with open(os.environ['OFFICE_FORBIDDEN_CALLS'], 'a') as stream:\n"
            "                stream.write(fullname + '\\n')\n"
            "            raise ImportError('Authoring dependency blocked by read-only regression')\n"
            "sys.meta_path.insert(0, NoAuthoringDependencies())\n",
            encoding="utf-8",
        )
        tools = self.work / "tools"
        tools.mkdir()
        for name in ("dotnet", "pip", "pip3", "libreoffice", "soffice", "chromium", "pandoc"):
            tool = tools / name
            tool.write_text('#!/bin/sh\nprintf "%s\\n" "$0" >> "$OFFICE_FORBIDDEN_CALLS"\nexit 95\n')
            tool.chmod(0o755)
        self.env = {**os.environ, "PYTHONPATH": str(guard), "PYTHONDONTWRITEBYTECODE": "1",
                    "PATH": str(tools) + os.pathsep + os.environ.get("PATH", ""),
                    "OFFICE_FORBIDDEN_CALLS": str(self.marker)}

    def run_reader(self, command, source):
        before = hashlib.sha256(source.read_bytes()).hexdigest()
        result = subprocess.run(command, cwd=self.work, env=self.env,
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), before)
        self.assertFalse(self.marker.exists(), self.marker.read_text() if self.marker.exists() else "")
        return result.stdout

    def test_explicit_docx_inspector_text_needs_no_authoring_setup(self):
        source = self.work / "input.docx"
        with ZipFile(source, "w") as package:
            package.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
            package.writestr("_rels/.rels", f'<Relationships xmlns="{REL}"><Relationship Id="r1" Type="{DOCREL}/officeDocument" Target="word/document.xml"/></Relationships>')
            package.writestr("word/document.xml", '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>Budget observation: 缺失不是零</w:t></w:r></w:p></w:body></w:document>')
        output = self.run_reader([sys.executable, str(OFFICE / "docx/scripts/docx_inspect.py"),
                                  "text", str(source)], source)
        self.assertIn("Budget observation: 缺失不是零", output)

    def test_xlsx_range_needs_no_dataframe_or_calculation_engine(self):
        source = self.work / "input.xlsx"
        with ZipFile(source, "w") as package:
            package.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/costs-data.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
            package.writestr("_rels/.rels", f'<Relationships xmlns="{REL}"><Relationship Id="r1" Type="{DOCREL}/officeDocument" Target="xl/workbook.xml"/></Relationships>')
            package.writestr("xl/workbook.xml", f'<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="{DOCREL}"><sheets><sheet name="Costs" sheetId="7" r:id="costs"/></sheets></workbook>')
            package.writestr("xl/_rels/workbook.xml.rels", f'<Relationships xmlns="{REL}"><Relationship Id="costs" Type="{DOCREL}/worksheet" Target="worksheets/costs-data.xml"/></Relationships>')
            package.writestr("xl/worksheets/costs-data.xml", '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row r="2"><c r="A2"><v>10</v></c><c r="B2"><f>A2+1</f></c><c r="C2" t="inlineStr"><is><t>00123</t></is></c></row></sheetData></worksheet>')
        output = self.run_reader([sys.executable, str(OFFICE / "xlsx/scripts/xlsx_reader.py"),
                                  str(source), "--sheet", "Costs", "--range", "A1:C2", "--json"], source)
        result = json.loads(output)
        self.assertEqual(result["mode"], "preview")
        cells = {cell["address"]: cell for cell in result["previews"]["Costs"]["cells"]}
        self.assertEqual(cells["C2"]["value"], "00123")
        self.assertIsNone(cells["B2"]["value"])
        self.assertEqual(cells["B2"]["cache_status"], "missing")


if __name__ == "__main__":
    unittest.main()
