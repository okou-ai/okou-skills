"""Offline regression contract; run with ``python3 -m unittest discover``.

Every script is imported from a temporary relocated skill, with bytecode disabled.
Fixtures and outputs are temporary. Browser/raster backends and pdffonts are mocked;
no optional dependencies or external executables are needed. Intentionally failing
negative regressions are real product defects, not expectedFailure annotations.
"""
import argparse
import ast
import base64
import builtins
from contextlib import ExitStack, redirect_stdout, redirect_stderr
import hashlib
from html.parser import HTMLParser
import importlib.util
import io
import json
import os
from pathlib import Path
import re
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import types
import unittest
from unittest import mock
from urllib.parse import quote
import zlib

SOURCE = Path(__file__).resolve().parents[1]
IDS = {"old-money-book": 8, "sport-ivory": 12, "sport-night": 12}
SCRIPT_NAMES = ("document", "colors", "kit", "preflight", "render", "generate_newsprint")
HEADER = ("name                                 type              encoding         emb sub uni object ID\n"
          "------------------------------------ ----------------- ---------------- --- --- --- ---------\n")


def digest_tree(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(root.rglob("*")) if p.is_file()}


class Tags(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.tags = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))

    handle_startendtag = handle_starttag


class IsolatedBrochure(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="brochure unittest ")
        self.addCleanup(self.temp.cleanup)
        self.area = Path(self.temp.name)
        self.root = self.area / "relocated skill with spaces"
        shutil.copytree(SOURCE, self.root, ignore=shutil.ignore_patterns("tests", "__pycache__", "*.pyc"))
        self.scripts = self.root / "scripts"
        self.project = self.area / "client project with spaces"
        self.project.mkdir()
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.stack.enter_context(mock.patch.object(sys, "dont_write_bytecode", True))
        self.stack.enter_context(mock.patch.object(sys, "path", [str(self.scripts)] + list(sys.path)))
        self.stack.enter_context(mock.patch.dict(sys.modules))
        self.stack.enter_context(mock.patch.dict(os.environ, HOME=str(self.area / "fake home"),
                                                  USERPROFILE=str(self.area / "fake home")))
        for target in ("socket.create_connection", "socket.socket.connect", "urllib.request.urlopen",
                       "subprocess.Popen", "subprocess.run", "os.system", "pathlib.Path.home",
                       "os.path.expanduser"):
            self.stack.enter_context(mock.patch(target, side_effect=AssertionError("Forbidden external/home operation: " + target)))
        # Guard actual writes as well as home resolution: only this test's temp tree
        # may be written. The originals, the real home, and global /tmp are read-only.
        def guarded_open(original):
            def call(file, mode="r", *args, **kwargs):
                if isinstance(file, (str, bytes, os.PathLike)) and any(c in mode for c in "wax+"):
                    path = Path(os.fsdecode(file)).resolve()
                    if not path.is_relative_to(self.area):
                        raise AssertionError("Write escaped temporary fixture: " + str(path))
                return original(file, mode, *args, **kwargs)
            return call
        self.stack.enter_context(mock.patch("builtins.open", guarded_open(builtins.open)))
        self.stack.enter_context(mock.patch("io.open", guarded_open(io.open)))
        self.modules = {}
        for name in SCRIPT_NAMES:
            spec = importlib.util.spec_from_file_location(name, self.scripts / (name + ".py"))
            module = importlib.util.module_from_spec(spec)
            sys.modules[name] = module
            spec.loader.exec_module(module)
            self.modules[name] = module
        self.kit = self.modules["kit"]
        self.document = self.modules["document"]
        self.preflight = self.modules["preflight"]
        self.palette = self.modules["colors"]
        self.render = self.modules["render"]

    def args(self, **kw):
        values = dict(id="old-money-book", project=str(self.area / "fresh project"),
                      name=None, brand=None, accent=None)
        values.update(kw)
        return argparse.Namespace(**values)

    def create(self, **kw):
        with redirect_stdout(io.StringIO()):
            return self.kit.create(self.args(**kw))

    def html(self, content, name="document.html"):
        path = self.project / name
        path.write_text(content, encoding="utf-8")
        return path

    def validate(self, content):
        return self.document.validate_document(self.html(content))


class KitTests(IsolatedBrochure):
    def test_imports_are_lazy_offline_and_leave_no_bytecode(self):
        self.assertEqual(self.kit.ROOT, self.root)
        self.assertFalse((self.root / "data").exists())
        self.assertFalse(any(self.root.rglob("*.pyc")))
        # No import request for these packages may occur for core list/new.
        original_import = builtins.__import__
        def no_optional(name, *a, **kw):
            if name.split(".")[0] in {"playwright", "PIL", "pypdfium2"}:
                raise AssertionError("Core CLI imported optional dependency: " + name)
            return original_import(name, *a, **kw)
        with mock.patch("builtins.__import__", side_effect=no_optional):
            output = io.StringIO()
            with mock.patch.object(sys, "argv", ["kit.py", "list"]), redirect_stdout(output):
                self.kit.main()
            for identifier in IDS:
                self.assertIn(identifier, output.getvalue())
            dest = self.create()
        self.assertTrue((dest / "old-money-book.html").is_file())

    def test_main_new_works_without_browser_and_uses_custom_name(self):
        out = self.area / "new cli project"
        with mock.patch.object(sys, "argv", ["kit.py", "new", "sport-ivory", str(out), "--name", "client-book"]), redirect_stdout(io.StringIO()):
            self.kit.main()
        self.assertTrue((out / "client-book.html").exists())
        self.assertIn('href="client-book.css"', (out / "client-book.html").read_text())
        self.assertFalse((out / "kit.css").exists())

    def test_all_three_kits_page_counts_local_closure_and_originals_unchanged(self):
        before = digest_tree(self.root)
        for identifier, count in IDS.items():
            with self.subTest(kit=identifier):
                dest = self.create(id=identifier, project=str(self.area / identifier), name="brochure")
                html = dest / "brochure.html"
                tags = Tags(html.read_text()).tags
                pages = [a for _, a in tags if "page" in a.get("class", "").split()]
                self.assertEqual(len(pages), count)
                self.assertEqual(int(self.kit.meta(self.root / "kits" / identifier)["pages"]), count)
                self.assertEqual(self.document.validate_document(html), html)
                self.assertEqual(digest_tree(dest / "fonts"), digest_tree(self.root / "assets" / "fonts"))
                self.assertIn("Nothing was downloaded", (dest / "SLOTS.md").read_text())
                for _, attrs in tags:
                    if "portrait" in attrs.get("src", "").lower():
                        self.assertIn("data-kit-sample", attrs)
                self.assertNotIn(str(self.root), html.read_text())
                self.assertNotRegex((dest / "brochure.css").read_text(), r"https?://")
        self.assertEqual(before, digest_tree(self.root))

    def test_relocating_assembled_project_preserves_resource_closure(self):
        out = self.create(id="sport-night", name="book")
        new = self.area / "another location with spaces" / "project"
        new.parent.mkdir()
        out.rename(new)
        self.assertEqual(self.document.validate_document(new / "book.html"), new / "book.html")

    def test_existing_directory_is_rejected_without_any_overwrite(self):
        out = self.area / "fresh project"
        out.mkdir()
        (out / "keep.txt").write_text("must survive")
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.create()
        self.assertEqual((out / "keep.txt").read_text(), "must survive")
        self.assertEqual(len(list(out.iterdir())), 1)

    def test_existing_empty_directory_and_file_are_rejected(self):
        for name, directory in (("empty", True), ("file", False)):
            out = self.area / name
            out.mkdir() if directory else out.write_text("retained")
            with self.subTest(directory=directory), self.assertRaises(ValueError):
                self.create(project=str(out))

    def test_invalid_ids_and_path_traversal_rejected_before_creation(self):
        for identifier in ("", "../sport-night", "sport/night", "/tmp/evil", "SPORT", "two words", "-bad", "bad-", "a--b", "a\\b"):
            with self.subTest(id=identifier), self.assertRaises(ValueError):
                self.create(id=identifier)
        self.assertFalse((self.area / "fresh project").exists())

    def test_unknown_slug_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unknown curated kit"):
            self.create(id="not-a-bundled-kit")

    def test_invalid_names_rejected(self):
        for name in ("../escape", "a/b", "a\\b", "two words", "Upper", "-bad", "a--b", "x.html"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.create(name=name)
        self.assertFalse((self.area / "fresh project").exists())

    def test_invalid_palette_colours_rejected(self):
        for colour in ("red", "#abc", "123456", "#12345678", "#zzzzzz", " #aabbcc", "#aabbcc;", "#aabbcc\n"):
            for key in ("brand", "accent"):
                with self.subTest(colour=colour, key=key), self.assertRaises(ValueError):
                    self.create(**{key: colour})
        self.assertFalse((self.area / "fresh project").exists())

    def test_installed_skill_destination_rejected(self):
        for target in (self.root, self.root / "nested new folder"):
            with self.subTest(target=target), self.assertRaisesRegex(ValueError, "installed skill"):
                self.create(project=str(target))

    def test_symlink_destination_existing_and_dangling_rejected(self):
        for target in (self.project, self.area / "absent"):
            link = self.area / "link"
            link.symlink_to(target, target_is_directory=True)
            with self.subTest(target=target), self.assertRaisesRegex(ValueError, "symlink"):
                self.create(project=str(link))
            link.unlink()
        self.assertFalse((self.area / "absent").exists())

    def test_symlink_bundled_asset_is_rejected_without_copy(self):
        (self.root / "kits" / "old-money-book" / "assets" / "escape.svg").symlink_to(self.project / "outside.svg")
        with self.assertRaisesRegex(ValueError, "symlink"):
            self.create()
        self.assertFalse((self.area / "fresh project").exists())

    def test_failed_validation_rolls_back_partial_project(self):
        with mock.patch.object(self.document, "validate_document", side_effect=ValueError("invalid asset")):
            with self.assertRaisesRegex(ValueError, "invalid asset"):
                self.create()
        self.assertFalse((self.area / "fresh project").exists())

    def test_palette_mapping_is_simultaneous_not_cascading(self):
        theme = {"brand": "#111111", "accent": "#222222"}
        self.assertEqual(self.kit.swap("#111111 #222222 #333333 #111111", theme,
                                       {"brand": "#222222", "accent": "#111111"}),
                         "#222222 #111111 #333333 #222222")

    def test_palette_derived_brand_roles_keep_oklch_offsets(self):
        theme = {"brand": "#50755b", "brand-deep": "#294331", "brand-tint": "#d9e2db", "accent": "#cc8844"}
        new = {"brand": "#a13d52"}
        b0 = self.palette.rgb2oklch(self.palette.hex2rgb(theme["brand"]))
        bn = self.palette.rgb2oklch(self.palette.hex2rgb(new["brand"]))
        expected = []
        for key in theme:
            if key == "brand":
                value = new["brand"]
            elif key.startswith("brand-"):
                old = self.palette.rgb2oklch(self.palette.hex2rgb(theme[key]))
                value = self.palette.lch(max(0, min(1, bn[0] + old[0] - b0[0])), max(0, bn[1] + old[1] - b0[1]), bn[2])
            else:
                value = theme[key]
            expected.append(value.lower())
        self.assertEqual(self.kit.swap(" ".join(theme.values()), theme, new), " ".join(expected))

    def test_create_brand_and_accent_updates_css_and_svg_without_source_mutation(self):
        before = digest_tree(self.root)
        out = self.create(id="sport-night", brand="#123456", accent="#654321")
        css = (out / "sport-night.css").read_text().lower()
        self.assertIn("#123456", css)
        self.assertIn("#654321", css)
        self.assertEqual(before, digest_tree(self.root))


class MarkTests(IsolatedBrochure):
    def test_nested_and_tail_text_each_mark_own_element(self):
        result = self.kit.mark('<main><p id="outer">Before <em id="inner">inside</em> tail</p><p id="tail"><b></b>tail only</p></main>')
        by_id = {a["id"]: a for _, a in Tags(result).tags if "id" in a}
        for identifier in ("outer", "inner", "tail"):
            self.assertIn("data-kit-sample", by_id[identifier])
        self.assertNotIn("data-kit-sample", Tags(result).tags[0][1])

    def test_mark_idempotent_with_existing_flags_and_self_closing_images(self):
        text = '<p data-kit-sample="approved">Text <b>nested</b> tail</p><img src="portrait.svg"/><br><p>Next</p>'
        once = self.kit.mark(text)
        self.assertEqual(self.kit.mark(once), once)
        self.assertIn('data-kit-sample="approved"', once)
        self.assertEqual(once.count("data-kit-sample"), 4)

    def test_all_portrait_and_placeholder_image_names_are_marked(self):
        names = ("portrait-rect.svg", "portrait-circle.svg", "PORTRAIT.PNG", "slot-photo.svg", "slot-mark.svg", "logo-placeholder-w.svg")
        marked = Tags(self.kit.mark("\n".join(f'<img src="assets/{n}">' for n in names))).tags
        for (_, attrs), name in zip(marked, names):
            with self.subTest(image=name):
                self.assertIn("data-kit-sample", attrs)
        attrs = Tags(self.kit.mark('<img src="verified-client-photo.png">')).tags[0][1]
        self.assertNotIn("data-kit-sample", attrs)

    def test_ordinary_marked_html_is_idempotent(self):
        text = '<p>Before <em>inside</em> tail</p><img src="portrait.svg">'
        marked = self.kit.mark(text)
        self.assertEqual(self.kit.mark(marked), marked)
        self.assertEqual(marked.count("data-kit-sample"), 3)

    def test_head_style_title_script_and_whitespace_are_not_demo_copy(self):
        text = '<head><title>Title</title><style>p{color:red}</style><script>ignored</script></head><main> \n <br></main>'
        self.assertEqual(self.kit.mark(text), text)

    def test_mark_calls_do_not_share_unclosed_parser_stack(self):
        self.kit.mark('<div id="dangling">unclosed')
        self.assertEqual(self.kit.mark("tail outside any element"), "tail outside any element")


class FontBundleTests(IsolatedBrochure):
    def test_all_22_fonts_have_pinned_hashes_sizes_and_no_unlisted_font(self):
        fonts = self.root / "assets" / "fonts"
        manifest = json.loads((fonts / "manifest.json").read_text())
        self.assertEqual(manifest["fontFileCount"], 22)
        self.assertEqual(len(manifest["files"]), 22)
        listed = set()
        for row in manifest["files"]:
            with self.subTest(font=row["file"]):
                path = self.document.project_file(row["file"], fonts, fonts)
                listed.add(path)
                data = path.read_bytes()
                self.assertTrue(data.startswith(b"wOF2"))
                self.assertEqual(len(data), row["bytes"])
                self.assertEqual(hashlib.sha256(data).hexdigest(), row["sha256"])
        self.assertEqual(listed, set(fonts.rglob("*.woff2")))
        self.assertEqual(sum(p.stat().st_size for p in listed), manifest["fontBytes"])

    def test_font_license_copyright_and_notice_paths_are_local_and_preserved(self):
        fonts = self.root / "assets" / "fonts"
        manifest = json.loads((fonts / "manifest.json").read_text())
        notice = (fonts / "FONT-LICENSES.md").read_text()
        self.assertEqual(len(manifest["packages"]), 4)
        for row in manifest["files"] + manifest["packages"]:
            with self.subTest(font=row.get("file", row.get("slug"))):
                self.assertEqual(row["license"], "OFL-1.1")
                license_path = self.document.project_file(row["licenseFile"], fonts, fonts)
                copyright_path = self.document.project_file(row["copyrightFile"], fonts, fonts)
                self.assertIn("SIL OPEN FONT LICENSE", license_path.read_text().upper())
                self.assertIn("DISCLAIMER", license_path.read_text().upper())
                self.assertTrue(copyright_path.read_text().strip())
                self.assertIn(row["licenseFile"], notice)
                self.assertIn(row["copyrightFile"], notice)
                for copyright_text in row.get("copyright", row.get("copyrightNotices", [])):
                    self.assertIn(copyright_text, copyright_path.read_text())

    def test_runtime_font_css_references_exactly_the_22_manifest_files(self):
        fonts = self.root / "assets" / "fonts"
        css = re.sub(r"/\*.*?\*/", "", (fonts / "fonts.css").read_text(), flags=re.S)
        manifest = json.loads((fonts / "manifest.json").read_text())
        paths = {str(Path(next(v for v in m.groups() if v is not None))) for m in self.document.URLS.finditer(css)}
        self.assertEqual(paths, {row["file"] for row in manifest["files"]})
        self.assertNotRegex(css, r"(?i)https?://|@import|local\(")
        self.assertEqual(css.count("@font-face"), 22)


class CopyTests(IsolatedBrochure):
    def test_missing_full_suffix_not_hidden_by_long_matching_prefix(self):
        prefix = "An approved required sentence with the first part repeated in the document. " * 5
        result = self.preflight.copy_coverage(prefix + "MANDATORY FINAL SUFFIX", prefix)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["found"], 0)
        self.assertTrue(result["missing"][0].endswith("mandatory final suffix"))

    def test_short_names_and_contact_omissions_are_errors(self):
        result = self.preflight.copy_coverage("Jane\na@b.co\n+86 123\nCompany profile", "Company profile")
        self.assertEqual(result["required"], 4)
        self.assertEqual(result["found"], 1)
        self.assertEqual(result["missing"], ["jane", "a@b.co", "+86 123"])
        self.assertEqual(result["coverage_pct"], 25)

    def test_empty_and_blank_copy_rejected(self):
        for text in ("", " ", "\n\t\n"):
            with self.subTest(copy=text), self.assertRaisesRegex(ValueError, "empty"):
                self.preflight.copy_coverage(text, "Anything")

    def test_complete_normalized_copy_deduplicates_and_passes(self):
        result = self.preflight.copy_coverage("Jane\nJANE\n‘Hello’ world\nHyphenated", "JANE\n'Hello'   world Hyphen-\nated")
        self.assertEqual(result, {"status": "passed", "required": 3, "found": 3, "coverage_pct": 100.0, "missing": []})

    def test_client_copy_tells_are_exempt_but_added_copy_is_reported(self):
        source = "It’s not just a school, it’s a family."
        self.assertEqual(self.preflight.copy_tells([source], src=source), [])
        codes = {x["code"] for x in self.preflight.copy_tells([source + " A seamless campus."])}
        self.assertIn("ai-contrast", codes)
        self.assertIn("generic-copy", codes)


class PDFFontTests(IsolatedBrochure):
    def report(self, output=HEADER, returncode=0, expected=()):
        issues = []
        with mock.patch.object(subprocess, "run", return_value=types.SimpleNamespace(stdout=output, stderr="", returncode=returncode)) as run:
            result = self.preflight.pdf_checks(self.project / "report with spaces.pdf", issues, expected)
        run.assert_called_once_with(["pdffonts", str(self.project / "report with spaces.pdf")], capture_output=True, text=True, timeout=60)
        return result, issues

    def test_missing_pdffonts_fails_closed(self):
        issues = []
        with mock.patch.object(subprocess, "run", side_effect=FileNotFoundError("pdffonts")):
            result = self.preflight.pdf_checks(self.project / "doc.pdf", issues)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(issues[0]["code"], "pdf-font-check")
        self.assertEqual(issues[0]["level"], "ERROR")

    def test_pdffonts_timeout_fails_closed(self):
        issues = []
        with mock.patch.object(subprocess, "run", side_effect=subprocess.TimeoutExpired(["pdffonts"], 60)):
            result = self.preflight.pdf_checks(self.project / "doc.pdf", issues)
        self.assertEqual(result["status"], "failed")
        self.assertIn("TimeoutExpired", issues[0]["msg"])

    def test_nonzero_pdffonts_exit_fails_closed_even_with_valid_stdout(self):
        result, issues = self.report(HEADER + "ABCDEF+BodoniModa Type1 Custom yes yes yes 1 0\n", returncode=1)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(issues[0]["code"], "pdf-font-check")

    def test_missing_or_malformed_report_fails_closed(self):
        for output in ("", "junk", "name without separators", HEADER + "not a font\n", HEADER + "Font Type1 Custom maybe yes yes 1 0\n"):
            with self.subTest(output=output):
                result, issues = self.report(output)
                self.assertEqual(result["status"], "failed")
                self.assertTrue(any(i["level"] == "ERROR" for i in issues))

    def test_malformed_header_only_report_must_not_claim_verification(self):
        result, issues = self.report("name\n---\n")
        self.assertEqual(result["status"], "failed", "BUG: malformed header-only output currently passes")
        self.assertTrue(issues)

    def test_malformed_row_with_missing_columns_must_fail_closed(self):
        result, issues = self.report(HEADER + "Font yes yes yes 1 0\n")
        self.assertEqual(result["status"], "failed", "BUG: six-token row lacks type and encoding but passes")
        self.assertTrue(issues)

    def test_embedded_font_report_handles_multitoken_type_and_existing_issues(self):
        stdout = HEADER + "ABCDEF+BodoniModa CID TrueType Identity-H yes yes yes 7 0\nGHIJKL+SourceSerif4 Type 1C Custom yes no yes 8 0\n"
        result, issues = self.report(stdout)
        self.assertEqual(result, {"status": "passed", "backend": "pdffonts", "fonts": [
            {"name": "ABCDEF+BodoniModa", "embedded": True}, {"name": "GHIJKL+SourceSerif4", "embedded": True}]})
        self.assertEqual(issues, [])
        prior = [{"level": "WARN", "code": "unrelated"}]
        with mock.patch.object(subprocess, "run", return_value=types.SimpleNamespace(stdout=stdout, returncode=0)):
            self.assertEqual(self.preflight.pdf_checks("doc.pdf", prior)["status"], "passed")
        self.assertEqual(len(prior), 1)

    def test_unembedded_and_unexpected_fallback_are_errors(self):
        result, issues = self.report(HEADER + "ABCDEF+DejaVuSans TrueType WinAnsi no yes yes 7 0\n")
        self.assertEqual(result["status"], "failed")
        self.assertEqual({i["code"] for i in issues}, {"fallback-font", "font-not-embedded"})

    def test_explicit_intended_brand_font_exempts_fallback_name_not_embedding(self):
        result, issues = self.report(HEADER + "ABCDEF+DejaVuSans TrueType WinAnsi yes yes yes 7 0\n", expected=("DejaVu Sans",))
        self.assertEqual(result["status"], "passed")
        self.assertEqual(issues, [])
        result, issues = self.report(HEADER + "ABCDEF+DejaVuSans TrueType WinAnsi no yes yes 7 0\n", expected=("DejaVu Sans",))
        self.assertEqual({i["code"] for i in issues}, {"font-not-embedded"})


class LoaderTests(IsolatedBrochure):
    def test_active_html_elements_rejected(self):
        for tag in ("script", "iframe", "base", "object", "embed", "form", "foreignObject"):
            with self.subTest(tag=tag), self.assertRaises(ValueError):
                self.validate(f'<html><{tag}></{tag}><section class="page">x</section></html>')

    def test_events_and_unsupported_attributes_rejected(self):
        for attr in ('onclick="alert(1)"', 'onerror="alert(1)"', 'ONLOAD="run()"', 'srcset="remote.png 1x"', 'srcdoc="content"', 'ping="https://example.invalid"'):
            with self.subTest(attr=attr), self.assertRaises(ValueError):
                self.validate(f"<div {attr}>Text</div>")

    def test_refresh_and_nonstylesheet_links_rejected(self):
        for content in ('<meta http-equiv="refresh" content="0;url=https://example.invalid">', '<link rel="preload" href="x">'):
            with self.subTest(content=content), self.assertRaises(ValueError):
                self.validate(content)

    def test_remote_images_css_urls_imports_and_stylesheets_rejected(self):
        samples = ('<img src="https://example.invalid/photo.png">', '<img src="//example.invalid/photo.png">',
                   '<link rel="stylesheet" href="https://example.invalid/style.css">',
                   '<style>@import "https://example.invalid/theme.css";</style>',
                   '<style>@import url(https://example.invalid/theme.css);</style>',
                   '<p style="background:url(https://example.invalid/a.png)">x</p>',
                   '<img src="file:///etc/passwd">')
        for content in samples:
            with self.subTest(content=content), self.assertRaises(ValueError):
                self.validate(content)

    def test_nested_css_remote_asset_rejected(self):
        (self.project / "one.css").write_text('@import "two.css";')
        (self.project / "two.css").write_text('body {background: url(https://example.invalid/asset.png)}')
        with self.assertRaises(ValueError):
            self.validate('<link rel="stylesheet" href="one.css">')

    def test_remote_and_active_svg_assets_rejected(self):
        bodies = ('<image href="https://example.invalid/photo.png"/>', '<script>run()</script>',
                  '<rect onclick="run()"/>', '<foreignObject/>', '<style>@import "https://example.invalid/style.css";</style>',
                  '<rect fill="url(https://example.invalid/paint.svg#p)"/>',
                  '<!DOCTYPE svg [<!ENTITY x SYSTEM "file:///etc/passwd">]><svg/>')
        for body in bodies:
            (self.project / "image.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg">' + body + '</svg>')
            with self.subTest(body=body), self.assertRaises(ValueError):
                self.validate('<img src="image.svg">')

    def test_inline_data_svg_active_content_rejected_both_encodings(self):
        for body in ('<script>run()</script>', '<rect onload="run()"/>', '<image href="https://example.invalid/x.png"/>'):
            svg = '<svg xmlns="http://www.w3.org/2000/svg">' + body + '</svg>'
            for value in ("data:image/svg+xml," + quote(svg), "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()):
                with self.subTest(body=body, encoding=value[:40]), self.assertRaises(ValueError):
                    self.validate(f'<img src="{value}">')

    def test_unsupported_data_asset_and_invalid_base64_rejected(self):
        for value in ("data:text/html,evil", "data:image/svg+xml;base64,%%%", "data:image/png"):
            with self.subTest(value=value), self.assertRaises((ValueError, zlib.error)):
                self.validate(f'<img src="{value}">')

    def test_parent_traversal_encoded_traversal_absolute_and_symlink_escapes_rejected(self):
        outside = self.area / "outside.png"
        outside.write_bytes(b"not used by browser")
        (self.project / "escape.png").symlink_to(outside)
        for value in ("../outside.png", "%2e%2e/outside.png", str(outside), "escape.png", "..\\outside.png"):
            with self.subTest(path=value), self.assertRaises(ValueError):
                self.validate(f'<img src="{value}">')

    def test_css_and_svg_symlink_escapes_rejected(self):
        outside = self.area / "outside.svg"
        outside.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        (self.project / "escape.svg").symlink_to(outside)
        for content in ('<style>div{background:url(escape.svg)}</style>', '<svg><image href="escape.svg"/></svg>'):
            with self.subTest(content=content), self.assertRaises(ValueError):
                self.validate(content)

    def test_positive_nested_local_css_svg_fonts_data_and_spaced_paths(self):
        (self.project / "assets with spaces").mkdir()
        assets = self.project / "assets with spaces"
        (assets / "pixel.png").write_bytes(b"PNG fixture (not rendered)")
        (assets / "font.woff2").write_bytes(b"font fixture (not rendered)")
        (assets / "art.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"><image href="pixel.png"/><rect fill="url(#paint)"/></svg>')
        (assets / "nested.css").write_text('@font-face{font-family:test;src:url(font.woff2)}')
        (self.project / "style.css").write_text('@import "assets%20with%20spaces/nested.css"; p{background:url("assets with spaces/art.svg")}')
        content = ('<link rel="stylesheet" href="style.css"><section class="page"><img src="assets%20with%20spaces/pixel.png">'
                   '<img src="data:image/svg+xml,%3Csvg%20xmlns=%22http://www.w3.org/2000/svg%22/%3E">'
                   '<a href="https://example.invalid">reference</a><a href="mailto:a@example.invalid">contact</a></section>')
        self.assertEqual(self.validate(content), self.project / "document.html")

    def test_stylesheet_cycles_are_finite(self):
        (self.project / "a.css").write_text('@import "b.css";')
        (self.project / "b.css").write_text('@import "a.css";')
        self.validate('<link rel="stylesheet" href="a.css">')

    def test_no_page_static_validation_is_not_browser_page_validation(self):
        # This loader performs static safety validation only. The actual no-.page
        # rejection belongs to open_document's browser layer, tested separately.
        self.assertEqual(self.validate("<html><p>no browser here</p></html>"), self.project / "document.html")

    def test_wrong_extension_missing_document_and_missing_asset_rejected(self):
        for path in (self.project / "absent.html", self.html("text", "not-html.txt")):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.document.validate_document(path)
        with self.assertRaises(ValueError):
            self.validate('<img src="missing.png">')

    def test_active_css_expression_and_binding_rejected(self):
        for css in ("p{width:expression(run())}", "p{-moz-binding:url(#x)}"):
            with self.subTest(css=css), self.assertRaises(ValueError):
                self.validate('<style>' + css + '</style>')

    def test_css_escaped_remote_url_must_be_rejected(self):
        # Browser CSS tokenization recognizes escapes; regex-only scanning does not.
        for css in (r'p{background:u\72l(https://example.invalid/image.png)}', r'@im\70ort "https://example.invalid/remote.css";'):
            with self.subTest(css=css), self.assertRaises(ValueError):
                self.validate('<style>' + css + '</style>')

    def test_size_limits_enforced_without_large_fixtures(self):
        (self.project / "asset.png").write_bytes(b"12345")
        path = self.html('<img src="asset.png">')
        with mock.patch.object(self.document, "MAX_ASSET_BYTES", len(path.read_bytes()) - 1), self.assertRaisesRegex(ValueError, "HTML exceeds"):
            self.document.validate_document(path)
        with mock.patch.object(self.document, "MAX_ASSET_BYTES", 4), self.assertRaisesRegex(ValueError, "Asset exceeds"):
            self.document.project_file("asset.png", self.project, self.project)


class OutputTests(IsolatedBrochure):
    def test_output_confined_to_project_and_root_itself_rejected(self):
        self.assertEqual(self.document.output_path(self.project / "out" / "report.json", self.project), self.project / "out" / "report.json")
        for value in (self.project, self.project / ".." / "escape.json", self.area / "outside.json"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.document.output_path(value, self.project)

    def test_output_symlink_escape_and_prefix_sibling_rejected(self):
        (self.project / "out-link").symlink_to(self.area, target_is_directory=True)
        sibling = self.area / (self.project.name + "-sibling")
        sibling.mkdir()
        for value in (self.project / "out-link" / "report.json", sibling / "report.json"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.document.output_path(value, self.project)

    def render_args(self, **kw):
        values = dict(html=str(self.html('<section class="page">x</section>')), out=str(self.project / "out"),
                      dpi=110, bleed=0, single=False, png_only=False)
        values.update(kw)
        return argparse.Namespace(**values)

    def test_render_rejects_outside_output_without_backend_calls(self):
        backend = types.ModuleType("pypdfium2")
        backend.PdfDocument = mock.Mock(side_effect=AssertionError("backend should not be called"))
        with mock.patch.dict(sys.modules, pypdfium2=backend), mock.patch.object(self.render, "open_document", side_effect=AssertionError("browser should not be called")):
            with self.assertRaises(ValueError):
                self.render.render(self.render_args(out=str(self.area / "escape")))
        backend.PdfDocument.assert_not_called()
        self.assertFalse((self.area / "escape").exists())

    def test_render_rejects_nonempty_output_without_overwrite(self):
        out = self.project / "out"
        out.mkdir()
        (out / "retained").write_text("safe")
        with mock.patch.dict(sys.modules, pypdfium2=types.ModuleType("pypdfium2")):
            with self.assertRaises(ValueError):
                self.render.render(self.render_args())
        self.assertEqual((out / "retained").read_text(), "safe")

    def test_render_invalid_dpi_bleed_before_browser(self):
        for kwargs in ({"dpi": 71}, {"dpi": 301}, {"bleed": -1}, {"bleed": 11}):
            with self.subTest(kwargs=kwargs), mock.patch.dict(sys.modules, pypdfium2=types.ModuleType("pypdfium2")):
                with self.assertRaises(ValueError):
                    self.render.render(self.render_args(**kwargs))
        self.assertFalse((self.project / "out").exists())

    def test_render_backend_failure_does_not_leave_deliverables(self):
        with mock.patch.dict(sys.modules, pypdfium2=types.ModuleType("pypdfium2")), mock.patch.object(self.render, "open_document", side_effect=ValueError("mock backend failure")):
            with self.assertRaisesRegex(ValueError, "mock backend failure"):
                self.render.render(self.render_args())
        self.assertFalse((self.project / "out").exists())
        self.assertEqual(list(self.project.glob(".brochure-render-*")), [])

    def fake_render_backends(self, boxes=None, pdf_count=1):
        """Faithful interfaces only: no real PDF, pixels or optional dependencies."""
        boxes = boxes if boxes is not None else [{"w": 100, "h": 150, "tw": 100, "th": 150, "b": 0}]
        page = mock.MagicMock()
        page.evaluate.return_value = boxes
        page.pdf.side_effect = lambda **kw: Path(kw["path"]).write_bytes(b"mock PDF")
        browser = mock.MagicMock()
        browser.__enter__.return_value = page
        self.stack.enter_context(mock.patch.object(self.render, "open_document", return_value=browser))
        self.stack.enter_context(mock.patch.object(self.render, "add_style"))
        image = mock.MagicMock()
        image.width, image.height = 100, 150
        image.convert.return_value = image
        image.crop.return_value = image
        image.save.side_effect = lambda path, **kw: Path(path).write_bytes(b"mock PNG")
        bitmap = mock.MagicMock()
        bitmap.to_pil.return_value = image
        pdf_page = mock.MagicMock()
        pdf_page.render.return_value = bitmap
        pdf = mock.MagicMock()
        pdf.__len__.return_value = pdf_count
        pdf.__getitem__.return_value = pdf_page
        context = mock.MagicMock()
        context.__enter__.return_value = pdf
        backend = types.ModuleType("pypdfium2")
        backend.PdfDocument = mock.Mock(return_value=context)
        self.stack.enter_context(mock.patch.dict(sys.modules, pypdfium2=backend))
        sheet = self.stack.enter_context(mock.patch.object(self.render, "contact_sheet", side_effect=lambda paths, dest, **kw: Path(dest).write_bytes(b"mock contact sheet")))
        return page, pdf_page, bitmap, image, sheet

    def test_render_success_uses_staging_then_commits_project_outputs(self):
        page, pdf_page, bitmap, image, sheet = self.fake_render_backends()
        with redirect_stdout(io.StringIO()):
            result = self.render.render(self.render_args())
        self.assertEqual(result["pages"], 1)
        self.assertEqual(result["preview_dpi"], 110)
        self.assertEqual((self.project / "out" / "document.pdf").read_bytes(), b"mock PDF")
        self.assertEqual((self.project / "out" / "pages" / "page-001.png").read_bytes(), b"mock PNG")
        self.assertTrue((self.project / "out" / "contact.png").is_file())
        self.assertEqual(list(self.project.glob(".brochure-render-*")), [])
        page.emulate_media.assert_called_once_with(media="print")
        pdf_page.close.assert_called_once()
        bitmap.close.assert_called_once()
        image.close.assert_called_once()

    def test_render_png_only_omits_pdf_and_requests_single_contact(self):
        *_, sheet = self.fake_render_backends()
        with redirect_stdout(io.StringIO()):
            result = self.render.render(self.render_args(png_only=True))
        self.assertNotIn("pdf", result)
        self.assertEqual(list((self.project / "out").glob("*.pdf")), [])
        self.assertTrue(sheet.call_args.kwargs["single"])
        self.assertTrue((self.project / "out" / "pages" / "page-001.png").exists())

    def test_render_pdf_page_count_mismatch_rolls_back_all_outputs(self):
        self.fake_render_backends(pdf_count=2)
        with self.assertRaisesRegex(ValueError, "page mismatch"):
            self.render.render(self.render_args())
        self.assertFalse((self.project / "out").exists())
        self.assertEqual(list(self.project.glob(".brochure-render-*")), [])

    def test_render_inconsistent_page_geometry_rolls_back(self):
        self.fake_render_backends(boxes=[{"w": 100, "h": 150, "tw": 100, "th": 150, "b": 0},
                                        {"w": 200, "h": 150, "tw": 200, "th": 150, "b": 0}])
        with self.assertRaisesRegex(ValueError, "same paper size"):
            self.render.render(self.render_args())
        self.assertFalse((self.project / "out").exists())
        self.assertEqual(list(self.project.glob(".brochure-render-*")), [])

    def test_preflight_json_output_escape_rejected_before_browser(self):
        html = self.html("<p>x</p>")
        with mock.patch.object(sys, "argv", ["preflight.py", str(html), "--json", str(self.area / "escape.json")]), mock.patch.object(self.document, "open_document", side_effect=AssertionError("browser called")):
            with self.assertRaises(ValueError):
                self.preflight.main()
        self.assertFalse((self.area / "escape.json").exists())


class ColourTests(IsolatedBrochure):
    def test_gamut_mapping_retains_valid_srgb_at_extreme_chroma(self):
        for hue in (0, 60, 120, 180, 240, 300):
            with self.subTest(hue=hue):
                result = self.palette.lch(0.55, 0.8, hue)
                self.assertRegex(result, r"^#[0-9a-f]{6}$")
                values = self.palette.hex2rgb(result)
                self.assertTrue(all(0 <= value <= 1 for value in values))
                self.assertAlmostEqual(self.palette.rgb2oklch(values)[0], 0.55, delta=0.01)

    def test_colour_round_trip_and_known_white(self):
        self.assertEqual(self.palette.hex2rgb("#fff"), (1, 1, 1))
        for hx in ("#123456", "#abcdef", "#ffffff", "#000000"):
            self.assertEqual(self.palette.rgb2hex(self.palette.oklch2rgb(*self.palette.rgb2oklch(self.palette.hex2rgb(hx)))), hx)

    def test_only_runtime_math_is_shipped_not_catalogues_or_generator(self):
        for name in ("DATA", "search", "roles", "swatches", "from_image", "main"):
            self.assertFalse(hasattr(self.palette, name), name)
        for name in ("data", "library", "references", "assets/fonts/metadata", "scripts/palette.py"):
            self.assertFalse((self.root / name).exists(), name)


class DistributionTests(IsolatedBrochure):
    def test_current_name_page_css_and_assembly_paths_match(self):
        self.assertIn("name: brochure-design", (self.root / "SKILL.md").read_text())
        self.assertTrue((self.root / "assets/pages.css").is_file())
        out = self.create(name="book")
        self.assertIn('href="pages.css"', (out / "book.html").read_text())
        self.assertTrue((out / "pages.css").is_file())
        self.assertFalse((out / "folio.css").exists())
        loader = (self.scripts / "document.py").read_text()
        self.assertIn('os.environ.get("BROCHURE_CHROMIUM")', loader)
        self.assertNotIn("FOLIO_CHROMIUM", loader)

    def test_font_sources_and_asset_hashes_have_no_removed_local_receipts(self):
        manifest = json.loads((self.root / "assets/fonts/manifest.json").read_text())
        for package in manifest["packages"]:
            self.assertNotIn("metadataFile", package)
            self.assertTrue(package["tarball"].startswith("https://registry.npmjs.org/"))
            self.assertTrue(package["integrity"].startswith("sha512-"))
        for row in manifest["files"]:
            self.assertNotIn("sourceCss", row)
            self.assertTrue(row["sourceCssArchivePath"].startswith("package/"))
        assets = json.loads((self.root / "ASSET-MANIFEST.json").read_text())
        self.assertEqual(assets["assetCount"], len(assets["assets"]))
        for row in assets["assets"]:
            data = (self.root / row["path"]).read_bytes()
            self.assertEqual(len(data), row["bytes"])
            self.assertEqual(hashlib.sha256(data).hexdigest(), row["sha256"])


class NewsprintTests(IsolatedBrochure):
    def test_generation_is_byte_reproducible_and_equals_bundled_original(self):
        generator = self.modules["generate_newsprint"]
        one, two = generator.generate(), generator.generate()
        bundled = (self.root / "kits" / "sport-night" / "assets" / "newsprint.png").read_bytes()
        self.assertEqual(one, two)
        self.assertEqual(one, bundled)
        self.assertEqual(hashlib.sha256(one).hexdigest(), "151333a2a9f1b554dc1320eef921585f4c1e62eae00b580a5b6b6bb533ea6aae")

    def test_png_crc_dimensions_filter_and_monochrome_pixels(self):
        data = self.modules["generate_newsprint"].generate()
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        offset, compressed, kinds = 8, bytearray(), []
        while offset < len(data):
            size = struct.unpack(">I", data[offset:offset + 4])[0]
            kind = data[offset + 4:offset + 8]
            payload = data[offset + 8:offset + 8 + size]
            crc = struct.unpack(">I", data[offset + 8 + size:offset + 12 + size])[0]
            self.assertEqual(crc, zlib.crc32(kind + payload) & 0xffffffff)
            kinds.append(kind)
            if kind == b"IHDR":
                self.assertEqual(struct.unpack(">IIBBBBB", payload), (512, 512, 8, 0, 0, 0, 0))
            if kind == b"IDAT":
                compressed.extend(payload)
            offset += 12 + size
        self.assertEqual(kinds, [b"IHDR", b"IDAT", b"IEND"])
        raw = zlib.decompress(compressed)
        self.assertEqual(len(raw), 512 * 513)
        for y in range(512):
            self.assertEqual(raw[y * 513], 0)
            self.assertEqual(set(raw[y * 513 + 1:(y + 1) * 513]), {0, 255})

    def test_all_curated_scripts_parse_as_python_312_without_compilation(self):
        for path in self.scripts.glob("*.py"):
            with self.subTest(script=path.name):
                ast.parse(path.read_text(), filename=str(path), feature_version=(3, 12))


if __name__ == "__main__":
    unittest.main()
