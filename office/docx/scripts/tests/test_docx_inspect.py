"""Stdlib fixtures exercise the explicit stored-OOXML inspector CLI, without .NET."""
from collections import Counter
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile


SCRIPTS = Path(__file__).resolve().parents[1]
SCRIPT = SCRIPTS / "docx_inspect.py"
SPEC = importlib.util.spec_from_file_location("docx_inspect", SCRIPT)
INSPECT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSPECT)
W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
P = "http://schemas.openxmlformats.org/package/2006/relationships"


class InspectTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="docx-read-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source 中文 with spaces.docx"
        paragraphs = "\n".join(f"<w:p><w:r><w:t>Line {index:03d}{'x' * 1000 if index == 5 else ''}</w:t></w:r></w:p>" for index in range(160))
        document = f'''<w:document xmlns:w="{W}" xmlns:r="{R}"><w:body>
<w:p><w:pPr><w:pStyle w:val="1"/></w:pPr><w:r><w:rPr><w:rStyle w:val="Emphasis"/></w:rPr><w:t xml:space="preserve"> Hello &amp; &lt;世界&gt; </w:t></w:r><w:r><w:t>joined</w:t><w:tab/><w:t>tabbed</w:t><w:br/><w:t>new line</w:t><w:cr/><w:t>carriage</w:t><w:br w:type="page"/><w:br w:type="column"/><w:footnoteReference w:id="2"/></w:r><w:del><w:r><w:delText>deleted</w:delText></w:r></w:del><w:moveFrom><w:r><w:t>moved away</w:t></w:r></w:moveFrom><w:r><w:instrText>HIDDEN FIELD CODE</w:instrText><w:t>cached result</w:t></w:r></w:p>
<w:tbl><w:tblPr><w:tblStyle w:val="Grid"/></w:tblPr><w:tr><w:tc><w:p><w:r><w:t>A1</w:t></w:r></w:p><w:p><w:r><w:t>A2</w:t></w:r></w:p></w:tc><w:tc><w:p><w:r><w:t>B1</w:t></w:r></w:p></w:tc></w:tr><w:tr><w:tc><w:p><w:r><w:t>C1</w:t></w:r></w:p></w:tc><w:tc><w:p/></w:tc></w:tr></w:tbl>
<w:p><w:pPr><w:sectPr><w:headerReference r:id="h1"/><w:pgSz w:w="11906"/></w:sectPr></w:pPr><w:hyperlink r:id="link1"><w:r><w:t>linked</w:t></w:r></w:hyperlink><w:r><w:drawing r:embed="missingId"/></w:r></w:p>
{paragraphs}
<w:sectPr><w:type w:val="nextPage"/></w:sectPr></w:body></w:document>'''
        with ZipFile(self.source, "w") as package:
            package.writestr("word/document.xml", document)
            package.writestr("word/styles.xml", f'''<w:styles xmlns:w="{W}"><w:style w:type="paragraph" w:styleId="a" w:default="1"><w:name w:val="Normal"/></w:style><w:style w:type="paragraph" w:styleId="1"><w:name w:val="heading 1"/><w:basedOn w:val="a"/></w:style><w:style w:type="character" w:styleId="Emphasis"><w:name w:val="Emphasis"/></w:style><w:style w:type="table" w:styleId="Grid"><w:name w:val="Table Grid"/></w:style></w:styles>''')
            package.writestr("word/header1.xml", f'<w:hdr xmlns:w="{W}"><w:p><w:r><w:t>HEADER ONLY</w:t></w:r></w:p></w:hdr>')
            package.writestr("word/footer1.xml", f'<w:ftr xmlns:w="{W}"><w:p><w:r><w:t>FOOTER ONLY</w:t></w:r></w:p></w:ftr>')
            package.writestr("word/footnotes.xml", f'<w:footnotes xmlns:w="{W}" xmlns:r="{R}"><w:footnote w:id="2"><w:p><w:hyperlink r:id="noteLink"><w:r><w:t>NOTE ONLY</w:t></w:r></w:hyperlink></w:p></w:footnote></w:footnotes>')
            package.writestr("word/endnotes.xml", f'<w:endnotes xmlns:w="{W}"><w:endnote w:id="4"><w:p><w:r><w:t>ENDNOTE ONLY</w:t></w:r></w:p></w:endnote></w:endnotes>')
            package.writestr("word/numbering.xml", f'<w:numbering xmlns:w="{W}"/>')
            package.writestr("word/_rels/document.xml.rels", f'''<Relationships xmlns="{P}"><Relationship Id="h1" Type="{R}/header" Target="header1.xml"/><Relationship Id="link1" Type="{R}/hyperlink" Target="https://example.com/" TargetMode="External"/><Relationship Id="gone" Type="{R}/image" Target="media/missing.png"/><Relationship Id="image" Type="{R}/image" Target="/word/media/picture%20one.png"/></Relationships>''')
            package.writestr("word/_rels/footnotes.xml.rels", f'<Relationships xmlns="{P}"><Relationship Id="noteLink" Type="{R}/hyperlink" Target="https://example.com/note" TargetMode="External"/></Relationships>')
            package.writestr("word/media/picture one.png", b"not-an-image-but-preserve-the-bytes")
        self.original = self.source.read_bytes()
        self.stat = self.source.stat()

    def cli(self, *args):
        result = subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                                capture_output=True, text=True, encoding="utf-8", timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def test_full_body_run_break_escaping_cjk_and_over_100_lines(self):
        result = self.cli("text", self.source)
        self.assertIn(" Hello & <世界> joined\ttabbed\nnew line\ncarriage", result.stdout)
        self.assertIn("[PAGE BREAK]", result.stdout)
        self.assertIn("[COLUMN BREAK]", result.stdout)
        self.assertIn("[FOOTNOTE:2]cached result", result.stdout)
        self.assertIn("[TABLE]\nA1\nA2\tB1\nC1\t\n[END TABLE]", result.stdout)
        self.assertIn("Line 000", result.stdout)
        self.assertIn("Line 159", result.stdout)
        self.assertNotIn("HEADER ONLY", result.stdout)
        self.assertNotIn("NOTE ONLY", result.stdout)
        self.assertNotIn("deleted", result.stdout)
        self.assertNotIn("moved away", result.stdout)
        self.assertNotIn("HIDDEN FIELD CODE", result.stdout)
        self.assertIn("not rendered pages or lossless extraction", result.stderr)
        self.assertEqual(self.source.read_bytes(), self.original)
        self.assertEqual(self.source.stat().st_mtime_ns, self.stat.st_mtime_ns)
        self.assertEqual(list(self.root.iterdir()), [self.source])

    def test_part_boundaries_and_explicit_selection(self):
        all_text = self.cli("text", self.source, "--part", "all").stdout
        self.assertLess(all_text.index("[END BODY:"), all_text.index("HEADER ONLY"))
        for label in ("HEADER ONLY", "FOOTER ONLY", "NOTE ONLY", "ENDNOTE ONLY",
                      "[FOOTNOTE id=2]", "[END FOOTNOTE]", "[ENDNOTE id=4]"):
            self.assertIn(label, all_text)
        notes = self.cli("text", self.source, "--part", "footnotes").stdout
        self.assertIn("NOTE ONLY", notes)
        self.assertNotIn("[BODY:", notes)
        self.assertNotIn("HEADER ONLY", notes)

    def test_explicit_body_range_is_zero_based_end_exclusive(self):
        result = self.cli("text", self.source, "--start", "3", "--end", "5")
        self.assertIn("RANGE: 3:5", result.stdout)
        self.assertIn("Line 000\nLine 001", result.stdout)
        self.assertNotIn("Line 002", result.stdout)
        self.assertNotIn(" Hello", result.stdout)

    def test_inventory_retains_style_ids_names_bases_text_sections_and_relationships(self):
        result = json.loads(self.cli("inventory", self.source, "--full", "--xml", "--hash-parts").stdout)
        self.assertEqual(result["body_coverage"]["total"], 164)
        self.assertTrue(result["body_coverage"]["complete"])
        self.assertEqual(result["body_coverage"]["text_mode"], "full")
        self.assertIn("x" * 1000, result["body_elements"][8]["text"])
        self.assertIn("xml", result["body_elements"][0])
        styles = {style["styleId"]: style for style in result["styles"]}
        self.assertIn("xml", styles["1"])
        self.assertEqual(styles["1"]["name"], "heading 1")
        self.assertEqual(styles["1"]["basedOn"], "a")
        self.assertEqual(styles["Emphasis"]["type"], "character")
        self.assertEqual(result["used_styles"]["word/document.xml"]["pStyle"], {"1": 1})
        self.assertEqual(result["used_styles"]["word/document.xml"]["rStyle"], {"Emphasis": 1})
        self.assertEqual(result["used_styles"]["word/document.xml"]["tblStyle"], {"Grid": 1})
        self.assertEqual(result["body_elements"][1]["kind"], "tbl")
        self.assertIn("B1", result["body_elements"][1]["text"])
        self.assertIn("Line 159", result["body_elements"][-2]["text"])
        self.assertEqual(result["body_elements"][-1]["kind"], "sectPr")
        self.assertEqual(len(result["sections"]), 2)
        self.assertIn("11906", result["sections"][0]["xml"])
        relationships = {entry["Id"]: entry for entry in result["relationships"]}
        self.assertEqual(relationships["h1"]["status"], "present")
        self.assertEqual(relationships["link1"]["status"], "external (not fetched)")
        self.assertEqual(relationships["gone"]["status"], "missing")
        self.assertEqual(relationships["image"]["status"], "present")
        refs = {ref["id"]: ref for ref in result["relationship_references"]}
        self.assertFalse(refs["missingId"]["relationship_present"])
        self.assertTrue(refs["noteLink"]["relationship_present"])
        manifest = {part["part"]: part for part in result["parts"]}
        self.assertEqual(manifest["word/media/picture one.png"]["sha256"],
                         hashlib.sha256(b"not-an-image-but-preserve-the-bytes").hexdigest())
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_inventory_reads_each_member_once(self):
        package = INSPECT.Package(self.source)
        self.addCleanup(package.close)
        with patch.object(package.zip, "read", wraps=package.zip.read) as read:
            INSPECT.inventory(package, full=True, xml=True, hash_parts=True)
        names = [call.args[0].filename if hasattr(call.args[0], "filename") else call.args[0]
                 for call in read.call_args_list]
        self.assertEqual(Counter(names), Counter({name: 1 for name in package.names}))

    def test_default_inventory_is_bounded_without_xml_hashes_or_binary_reads(self):
        package = INSPECT.Package(self.source)
        self.addCleanup(package.close)
        original_read = package.zip.read
        def checked_read(name, *args, **kwargs):
            path = name.filename if hasattr(name, "filename") else name
            self.assertNotIn("/media/", path)
            self.assertNotEqual(path, "word/numbering.xml")
            return original_read(name, *args, **kwargs)
        with patch.object(package.zip, "read", side_effect=checked_read) as read:
            result = INSPECT.inventory(package)
        self.assertEqual(read.call_count, 8)
        coverage = result["body_coverage"]
        self.assertEqual((coverage["total"], coverage["start"], coverage["end"], coverage["returned"]),
                         (164, 0, 50, 50))
        self.assertFalse(coverage["complete"])
        self.assertIn("--full", coverage["expand"])
        self.assertTrue(result["body_elements"][8]["text_truncated"])
        self.assertEqual(len(result["body_elements"][8]["text"]), 160)
        for entry in result["body_elements"] + result["styles"] + result["sections"]:
            self.assertNotIn("xml", entry)
        self.assertTrue(all("sha256" not in part for part in result["parts"]))
        self.assertIn("11906", json.dumps(result["sections"][0]["properties"]))
        parts = {part["part"]: part for part in result["parts"]}
        self.assertEqual(parts["word/media/picture one.png"]["size"],
                         len(b"not-an-image-but-preserve-the-bytes"))
        self.assertIn("compressed_size", parts["word/media/picture one.png"])
        # A preview must not build the remainder of an oversized body element.
        def oversized_chunks():
            yield "x" * 161
            self.fail("preview consumed the rest of an oversized element")
        with patch.object(INSPECT, "block_chunks", return_value=oversized_chunks()):
            self.assertEqual(INSPECT.text_summary(None), ("x" * 160, True))
        with patch.object(INSPECT, "block_chunks", return_value=iter(["x" * 160])):
            self.assertEqual(INSPECT.text_summary(None), ("x" * 160, False))

    def test_inventory_range_xml_and_full_flags_are_independent_real_cli_options(self):
        result = json.loads(self.cli("inventory", self.source, "--start", 160, "--end", 164, "--xml").stdout)
        self.assertEqual([entry["index"] for entry in result["body_elements"]], [160, 161, 162, 163])
        self.assertIn("Line 159", result["body_elements"][-2]["text"])
        self.assertIn("xml", result["body_elements"][-1])
        self.assertFalse(result["detail"]["hash_parts"])
        result = json.loads(self.cli("inventory", self.source, "--full").stdout)
        self.assertTrue(result["body_coverage"]["complete"])
        self.assertIn("x" * 1000, result["body_elements"][8]["text"])
        self.assertNotIn("xml", result["body_elements"][0])
        hashes = json.loads(self.cli("inventory", self.source, "--hash-parts").stdout)
        self.assertEqual(len(hashes["body_elements"]), 50)
        self.assertTrue(all("sha256" in entry for entry in hashes["parts"]))

    def test_invalid_internal_relationship_targets_are_not_reported_present(self):
        targets = ["", "//host/word/document.xml", "https://host/file", "header1.xml\\\\oops",
                   "header1.xml%5Coops", "http://[broken", "header1.xml%zz", "../../outside.xml",
                   "header1.xml?query", "header1.xml\n", "%00header1.xml", "%2f%2fhost/file"]
        for target in targets:
            with self.subTest(target=target):
                self.assertIsNone(INSPECT.internal_target("word/document.xml", target))
        self.assertEqual(INSPECT.internal_target("word/document.xml", "header1.xml"), "word/header1.xml")
        self.assertEqual(INSPECT.internal_target("word/document.xml", "/word/header1.xml"), "word/header1.xml")
        source = self.root / "invalid-rels.docx"
        with ZipFile(source, "w") as package:
            package.writestr("word/document.xml", f'<w:document xmlns:w="{W}"><w:body/></w:document>')
            package.writestr("word/_rels/document.xml.rels", f'<Relationships xmlns="{P}"><Relationship Id="bad" Target="//host/word/document.xml"/><Relationship Id="broken" Target="http://[broken"/></Relationships>')
        result = json.loads(self.cli("inventory", source).stdout)
        self.assertTrue(all(entry["status"] == "invalid internal target" for entry in result["relationships"]))

    def test_block_level_deletion_and_move_from_never_reintroduce_text(self):
        source = self.root / "revisions.docx"
        with ZipFile(source, "w") as package:
            package.writestr("word/document.xml", f'''<w:document xmlns:w="{W}"><w:body>
<w:del><w:p><w:r><w:t>BLOCK DELETED</w:t></w:r></w:p></w:del>
<w:sdt><w:sdtContent><w:moveFrom><w:tbl><w:tr><w:tc><w:p><w:r><w:t>BLOCK MOVED</w:t></w:r></w:p></w:tc></w:tr></w:tbl></w:moveFrom><w:p><w:r><w:t>KEPT</w:t></w:r></w:p></w:sdtContent></w:sdt>
</w:body></w:document>''')
        text = self.cli("text", source)
        self.assertIn("KEPT", text.stdout)
        self.assertNotIn("BLOCK DELETED", text.stdout)
        self.assertNotIn("BLOCK MOVED", text.stdout)
        result = json.loads(self.cli("inventory", source, "--full", "--xml").stdout)
        self.assertEqual(result["body_elements"][0]["text"], "")
        self.assertNotIn("BLOCK MOVED", result["body_elements"][1]["text"])
        self.assertIn("BLOCK DELETED", result["body_elements"][0]["xml"])
        self.assertIn("not full revision/render semantics", text.stderr)

    def test_part_command_is_real_and_read_only(self):
        result = self.cli("part", self.source, "word/numbering.xml")
        self.assertIn("numbering", result.stdout)
        self.assertEqual(self.source.read_bytes(), self.original)

    def test_strict_namespace_text(self):
        source = self.root / "strict.docx"
        with ZipFile(source, "w") as package:
            package.writestr("word/document.xml", '<w:document xmlns:w="http://purl.oclc.org/ooxml/wordprocessingml/main"><w:body><w:p><w:r><w:t>严格 中文</w:t></w:r></w:p></w:body></w:document>')
        self.assertIn("严格 中文", self.cli("text", source).stdout)

    def test_bad_input_missing_part_and_invalid_range_fail_cleanly(self):
        for arguments in (("text", "missing.docx"), ("part", self.source, "absent.xml"),
                          ("text", self.source, "--start", "-1"),
                          ("text", self.source, "--part", "footnotes", "--end", "1"),
                          ("inventory", self.source, "--start", "-1"),
                          ("inventory", self.source, "--start", "5", "--end", "2"),
                          ("inventory", self.source, "--full", "--end", "2")):
            with self.subTest(arguments=arguments):
                result = subprocess.run([sys.executable, str(SCRIPT), *map(str, arguments)],
                                        capture_output=True, text=True, timeout=15)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Traceback", result.stderr)
        source = self.root / "broken.docx"
        source.write_bytes(b"not zip")
        result = subprocess.run([sys.executable, str(SCRIPT), "text", str(source)],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 1)
        self.assertNotIn("Traceback", result.stderr)

    def test_explicit_inspector_text_needs_no_dotnet_pandoc_or_unzip(self):
        commands = self.root / "commands"
        commands.mkdir()
        result = subprocess.run([sys.executable, str(SCRIPT), "text", str(self.source)],
                                env={**os.environ, "PATH": str(commands), "LANG": "C.UTF-8"},
                                capture_output=True, text=True, encoding="utf-8", timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Line 159", result.stdout)


if __name__ == "__main__":
    unittest.main()
