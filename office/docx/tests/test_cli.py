"""Exercise the shipped .NET CLI, including exit codes and actual OOXML parts."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile

SKILL = Path(__file__).resolve().parents[1]
DLL = SKILL / "scripts/dotnet/Docx.Cli/bin/Debug/net8.0/Docx.Cli.dll"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


class DocxCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="docx test ")
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        self.docx = self.work / "report.docx"
        self.cli("create", "--output", self.docx, "--title", "Strategy review",
                 "--header", "Okou", "--footer", "Confidential", "--page-numbers")

    def cli(self, *args, expected=0):
        result = subprocess.run(
            (["dotnet", str(DLL)] if os.name == "nt" else
             ["bash", str(SKILL / "scripts/docx.sh")]) + list(map(str, args)), cwd=self.work,
            text=True, capture_output=True, timeout=60,
        )
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)
        return result

    def rewrite(self, part, change):
        with zipfile.ZipFile(self.docx) as package:
            entries = {name: package.read(name) for name in package.namelist()}
        root = ET.fromstring(entries[part])
        change(root)
        entries[part] = ET.tostring(root, encoding="utf-8")
        with zipfile.ZipFile(self.docx, "w") as package:
            for name, content in entries.items():
                package.writestr(name, content)

    def test_create_and_validate_relationships_and_xml_space(self):
        result = self.cli("validate", "--input", self.docx, "--business", "--xsd",
                          SKILL / "assets/xsd/wml-subset.xsd", "--json")
        self.assertTrue(json.loads(result.stdout)["isValid"])
        with zipfile.ZipFile(self.docx) as package:
            self.assertIn("word/header1.xml", package.namelist())
            self.assertIn("word/footer1.xml", package.namelist())

    def test_accepts_eleven_point_normal_style(self):
        def resize(root):
            normal = next(style for style in root.findall(f"{W}style")
                          if style.get(f"{W}styleId") == "Normal")
            normal.find(f"{W}rPr/{W}sz").set(f"{W}val", "22")
        self.rewrite("word/styles.xml", resize)
        result = self.cli("validate", "--input", self.docx, "--business", "--json")
        self.assertTrue(json.loads(result.stdout)["isValid"])

    def test_bad_structure_in_styles_part_returns_failure(self):
        def corrupt(root):
            ET.SubElement(root.find(f"{W}style/{W}rPr"), f"{W}notAWordElement")
        self.rewrite("word/styles.xml", corrupt)
        result = self.cli("validate", "--input", self.docx, "--json", expected=1)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["isValid"])
        self.assertTrue(any("/word/styles.xml" in error["Message"] for error in payload["errors"]))

    def test_missing_input_returns_failure(self):
        self.cli("validate", "--input", self.work / "missing.docx", expected=1)

    def test_invalid_schema_is_a_structured_failure(self):
        schema = self.work / "bad.xsd"
        schema.write_text('''<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
<xs:element name="document" type="missingType"/></xs:schema>''')
        result = self.cli("validate", "--input", self.docx, "--xsd", schema, "--json", expected=1)
        self.assertIn("Schema error", json.loads(result.stdout)["errors"][0]["Message"])

    def test_template_gate_accepts_template_docx(self):
        template = self.work / "template.docx"
        shutil.copyfile(self.docx, template)
        result = self.cli("validate", "--input", self.docx, "--gate-check", template, "--json")
        self.assertTrue(json.loads(result.stdout)["gateCheck"]["passed"])


if __name__ == "__main__":
    unittest.main()
