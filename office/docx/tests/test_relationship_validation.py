"""Validate implicit DOCX relationships without hiding broken explicit references."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile


SKILL = Path(__file__).resolve().parents[1]
CLI = SKILL / "scripts/dotnet/Docx.Cli/bin/Debug/net8.0/Docx.Cli.dll"
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
RELS = "http://schemas.openxmlformats.org/package/2006/relationships"
CONTENT_TYPES = "http://schemas.openxmlformats.org/package/2006/content-types"


class RelationshipValidationTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="docx relationships ")
        self.addCleanup(self.directory.cleanup)
        self.work = Path(self.directory.name)
        self.document = self.work / "report.docx"
        result = self.run_cli(
            "create", "--title", "Relationship validation",
            "--header", "Report header", "--footer", "Report footer",
            "--output", str(self.document),
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def run_cli(self, *args):
        return subprocess.run(
            ["dotnet", str(CLI), *args], cwd=self.work,
            text=True, capture_output=True, timeout=30,
        )

    def read_parts(self):
        with ZipFile(self.document) as archive:
            return {name: archive.read(name) for name in archive.namelist()}

    def write_parts(self, parts):
        with ZipFile(self.document, "w", ZIP_DEFLATED) as archive:
            for name, data in parts.items():
                archive.writestr(name, data)

    def assert_valid_without_warnings(self):
        result = self.run_cli(
            "validate", "--input", str(self.document), "--business", "--json",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        validation = json.loads(result.stdout)
        self.assertTrue(validation["isValid"], validation)
        self.assertEqual(validation["errors"], [])
        self.assertEqual(validation["warnings"], [])

    def test_created_document_with_styles_and_header_footer_is_valid(self):
        self.assert_valid_without_warnings()

    def test_other_implicit_parts_do_not_require_explicit_references(self):
        parts = self.read_parts()
        relationships = ET.fromstring(parts["word/_rels/document.xml.rels"])
        content_types = ET.fromstring(parts["[Content_Types].xml"])
        for name, root_tag in (
            ("settings", "settings"), ("numbering", "numbering"), ("fontTable", "fonts"),
        ):
            parts[f"word/{name}.xml"] = ET.tostring(ET.Element(f"{{{W}}}{root_tag}"))
            ET.SubElement(relationships, f"{{{RELS}}}Relationship", {
                "Id": f"rId{name}", "Type": f"{R}/{name}", "Target": f"{name}.xml",
            })
            ET.SubElement(content_types, f"{{{CONTENT_TYPES}}}Override", {
                "PartName": f"/word/{name}.xml",
                "ContentType": f"application/vnd.openxmlformats-officedocument.wordprocessingml.{name}+xml",
            })
        ET.register_namespace("", RELS)
        parts["word/_rels/document.xml.rels"] = ET.tostring(relationships)
        ET.register_namespace("", CONTENT_TYPES)
        parts["[Content_Types].xml"] = ET.tostring(content_types)
        self.write_parts(parts)
        self.assert_valid_without_warnings()

    def test_missing_hyperlink_relationship_still_fails(self):
        parts = self.read_parts()
        document = ET.fromstring(parts["word/document.xml"])
        body = document.find(f"{{{W}}}body")
        paragraph = ET.Element(f"{{{W}}}p")
        hyperlink = ET.SubElement(paragraph, f"{{{W}}}hyperlink", {
            f"{{{R}}}id": "rMissingLink",
        })
        run = ET.SubElement(hyperlink, f"{{{W}}}r")
        ET.SubElement(run, f"{{{W}}}t").text = "Broken link"
        body.insert(0, paragraph)
        parts["word/document.xml"] = ET.tostring(document)
        self.write_parts(parts)

        result = self.run_cli(
            "validate", "--input", str(self.document), "--business", "--json",
        )
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        validation = json.loads(result.stdout)
        self.assertFalse(validation["isValid"], validation)
        self.assertIn(
            "Reference r:id='rMissingLink' has no matching relationship",
            [error["Message"] for error in validation["errors"]],
        )


if __name__ == "__main__":
    unittest.main()
