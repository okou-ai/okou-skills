"""Offline tests: no model calls, network requests or credentials."""
import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

SPEC = importlib.util.spec_from_file_location("thumbnail", Path(__file__).with_name("thumbnail.py"))
thumbnail = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(thumbnail)
ROOT = Path(__file__).resolve().parents[1]


class PromptTests(unittest.TestCase):
    def setUp(self):
        self.brief = json.loads((ROOT / "templates/examples/tech-after-hours.json").read_text())

    def test_every_template_has_one_compilable_example(self):
        seen = set()
        for path in (ROOT / "templates/examples").glob("*.json"):
            data = json.loads(path.read_text())
            prompt = thumbnail.compile_prompt(data)
            seen.add(data["template_id"])
            self.assertIn("16:9", prompt)
            self.assertIn("168x94", prompt)
            for line in data["overlay_lines"]:
                self.assertIn(line, prompt)
            self.assertNotIn("TODO", prompt)
        self.assertEqual(seen, set(thumbnail.catalog()))

    def test_compilation_is_deterministic_and_does_not_mutate_input(self):
        original = copy.deepcopy(self.brief)
        first = thumbnail.compile_prompt(self.brief)
        self.assertEqual(first, thumbnail.compile_prompt(self.brief))
        self.assertEqual(self.brief, original)

    def test_visual_only(self):
        self.brief["overlay_lines"] = []
        self.assertIn("no lettering", thumbnail.compile_prompt(self.brief))

    def test_palette_override(self):
        self.brief["brand_colors"] = ["#ABCDEF"]
        self.assertIn("#ABCDEF", thumbnail.compile_prompt(self.brief))

    def test_literal_slash_is_not_a_line_separator(self):
        self.brief["overlay_lines"] = ["A/B", "24/7"]
        prompt = thumbnail.compile_prompt(self.brief)
        self.assertIn('["A/B", "24/7"]', prompt)
        self.assertIn("literal slash", prompt)
        self.assertNotIn("slash above as a line separator", prompt)

    def test_visual_only_editorial_does_not_require_headline(self):
        self.brief["template_id"] = "bold-editorial"
        self.brief["overlay_lines"] = []
        self.brief["scene_details"] = ""
        prompt = thumbnail.compile_prompt(self.brief)
        self.assertIn("otherwise leave that area empty", prompt)
        self.assertIn("no lettering", prompt)
        self.assertNotIn("Integrate an oversized clean headline", prompt)

    def test_layout_instructions_are_not_visible_content(self):
        prompt = thumbnail.compile_prompt(self.brief)
        self.assertIn("Do not visualize layout instructions", prompt)
        self.assertNotIn("18 percent", prompt)

    def test_invalid_briefs(self):
        cases = [
            ("template_id", "../../other"), ("video_title", " "),
            ("audience", 7), ("overlay_lines", "not a list"),
            ("overlay_lines", ["one", "two", "three"]),
            ("overlay_lines", ["broken\nline"]),
            ("overlay_lines", ["one two three four five six seven"]),
            ("overlay_lines", ["这是一行非常非常非常非常非常长而且完全不适合缩略图的文字"]),
            ("brand_colors", ["red"]), ("brand_colors", ["#123456"] * 4),
            ("scene_details", None), ("typo_field", "unexpected"),
        ]
        for field, value in cases:
            data = copy.deepcopy(self.brief)
            data[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                thumbnail.compile_prompt(data)

    def test_list_cli_returns_catalog_successfully(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/thumbnail.py"), "list"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({entry["id"] for entry in json.loads(result.stdout)}, set(thumbnail.catalog()))

    def test_non_object_brief(self):
        with self.assertRaises(ValueError):
            thumbnail.compile_prompt([])

    def test_catalog_source_ids(self):
        allowed = {"baoyu", "nanothumbnail", "swyxio"}
        for template in thumbnail.catalog().values():
            self.assertTrue(template["source_ids"])
            self.assertTrue(set(template["source_ids"]) <= allowed)


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.input = self.root / "input.png"
        self.output = self.root / "thumb.jpg"
        self.qa = self.root / "qa"
        Image.new("RGB", (1376, 768), "#122333").save(self.input)

    def tearDown(self):
        self.temp.cleanup()

    def test_near_ratio_export_and_mobile_preview(self):
        result = thumbnail.export_image(self.input, self.output, self.qa)
        self.assertTrue(result["technical_pass"])
        self.assertEqual(result["source_size"], [1376, 768])
        self.assertTrue(result["near_ratio_crop"])
        with Image.open(result["mobile_preview"]) as preview:
            self.assertEqual(preview.size, (168, 94))
        self.assertEqual(len(result["sha256"]), 64)
        self.assertEqual(result["ctr_effectiveness"], "not measured")

    def test_exact_ratio_export(self):
        Image.new("RGB", (1280, 720), "white").save(self.input)
        result = thumbnail.export_image(self.input, self.output, self.qa)
        self.assertFalse(result["near_ratio_crop"])

    def test_alpha_flattens_to_jpeg(self):
        Image.new("RGBA", (1280, 720), (0, 0, 0, 0)).save(self.input)
        thumbnail.export_image(self.input, self.output, self.qa)
        with Image.open(self.output) as image:
            self.assertEqual(image.mode, "RGB")
            self.assertEqual(image.getpixel((0, 0)), (255, 255, 255))

    def test_grayscale_alpha_flattens_consistently(self):
        Image.new("LA", (1280, 720), (0, 0)).save(self.input)
        thumbnail.export_image(self.input, self.output, self.qa)
        with Image.open(self.output) as image:
            self.assertEqual(image.getpixel((0, 0)), (255, 255, 255))

    def test_png_is_source_not_final_jpeg(self):
        Image.new("RGB", (1280, 720), "white").save(self.input)
        result = thumbnail.check_image(self.input)
        self.assertTrue(result["supported_format"])
        self.assertFalse(result["final_jpeg"])
        self.assertFalse(result["technical_pass"])

    def test_preview_write_failure_rolls_back_output(self):
        preview = self.qa / "thumb-168x94.jpg"
        original_open = Path.open
        def blocked(path, *args, **kwargs):
            if path == preview and args and args[0] == "xb":
                raise PermissionError("simulated QA write failure")
            return original_open(path, *args, **kwargs)
        with patch.object(Path, "open", new=blocked):
            with self.assertRaises(PermissionError):
                thumbnail.export_image(self.input, self.output, self.qa)
        self.assertFalse(self.output.exists())
        self.assertFalse(preview.exists())
        self.assertTrue(thumbnail.export_image(self.input, self.output, self.qa)["technical_pass"])

    def test_raced_in_preview_is_preserved(self):
        preview = self.qa / "thumb-168x94.jpg"
        original_open = Path.open
        def race(path, *args, **kwargs):
            if path == preview and args and args[0] == "xb":
                with original_open(path, "w") as handle:
                    handle.write("someone else's file")
                raise FileExistsError("simulated race")
            return original_open(path, *args, **kwargs)
        with patch.object(Path, "open", new=race):
            with self.assertRaises(FileExistsError):
                thumbnail.export_image(self.input, self.output, self.qa)
        self.assertFalse(self.output.exists())
        self.assertEqual(preview.read_text(), "someone else's file")

    def test_pillow_bomb_error_is_a_handled_input_error(self):
        with patch.object(Image, "open", side_effect=Image.DecompressionBombError("too large")):
            with self.assertRaisesRegex(ValueError, "safe pixel limit"):
                thumbnail.image_info(self.input)

    def test_wrong_ratio_requires_explicit_crop(self):
        Image.new("RGB", (1280, 1280), "red").save(self.input)
        with self.assertRaisesRegex(ValueError, "not near 16:9"):
            thumbnail.export_image(self.input, self.output, self.qa)
        self.assertFalse(self.output.exists())
        result = thumbnail.export_image(self.input, self.output, self.qa, allow_crop=True)
        self.assertTrue(result["technical_pass"])
        self.assertTrue(result["large_crop_explicitly_allowed"])

    def test_no_silent_upscale(self):
        Image.new("RGB", (640, 360), "red").save(self.input)
        with self.assertRaisesRegex(ValueError, "smaller"):
            thumbnail.export_image(self.input, self.output, self.qa)

    def test_no_overwrite(self):
        self.output.write_text("keep me")
        with self.assertRaisesRegex(ValueError, "overwrite"):
            thumbnail.export_image(self.input, self.output, self.qa)
        self.assertEqual(self.output.read_text(), "keep me")

    def test_corrupt_image(self):
        self.input.write_text("not an image")
        with self.assertRaises(OSError):
            thumbnail.check_image(self.input)

    def test_bad_output_extension(self):
        with self.assertRaisesRegex(ValueError, ".jpg"):
            thumbnail.export_image(self.input, self.root / "out.png", self.qa)

    def test_wrong_dimensions_fail_check(self):
        result = thumbnail.check_image(self.input)
        self.assertFalse(result["technical_pass"])

    def test_cli_failure_exit_code(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/thumbnail.py"), "check", str(self.input)],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["technical_pass"])

    def test_compile_cli_does_not_overwrite(self):
        out = self.root / "prompt.txt"
        out.write_text("keep me")
        result = subprocess.run([
            sys.executable, str(ROOT / "scripts/thumbnail.py"), "compile",
            "--brief", str(ROOT / "templates/examples/tech-after-hours.json"), "--out", str(out),
        ], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(out.read_text(), "keep me")


if __name__ == "__main__":
    unittest.main()
