import copy
import json
import re
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from bind_tokens import compile_theme, CORE
from build_preview import token, build
from inspect_pptx import inspect, canvas_transform


class ContractTest(unittest.TestCase):
    def setUp(self):
        self.theme = json.loads((ROOT / "examples/minimal.tokens.json").read_text())

    def test_six_core_tokens_without_dictionary_completion(self):
        self.assertEqual(len(self.theme["$tokens"]), 6)
        css, report = compile_theme(self.theme)
        self.assertIn("--okp-type-body-font-size: 32px", css)
        self.assertNotIn("type.body.line-height", report["resolved"])
        self.assertEqual(len(self.theme["$tokens"]), 6)  # compilation is non-mutating

    def test_aliases_are_inferred_roles_not_new_observations(self):
        _, report = compile_theme(self.theme)
        self.assertEqual(report["resolved"]["type.metric-value.font-size"]["value"], 56)
        self.assertEqual(report["origins"]["type.metric-value.font-size"]["kind"], "inferred")
        self.assertEqual(report["roleMap"]["caption"], "body")
        self.assertEqual(report["resolved"]["color.on-surface.canvas.secondary"], "#20252a")

    def test_explicit_optional_role_is_preserved(self):
        self.theme["$tokens"]["type.caption.font-size"] = token("dimension", {"value": 18, "unit": "px"})
        _, report = compile_theme(self.theme)
        self.assertEqual(report["resolved"]["type.caption.font-size"]["value"], 18)
        self.assertEqual(report["roleMap"]["caption"], "caption")

    def test_literal_source_provenance(self):
        self.theme["$tokens"]["type.title.font-size"]["$extensions"]["origin"] = {"kind": "extracted", "documentId": "fixture", "location": "ppt/slideMasters/slideMaster1.xml/defRPr@sz"}
        _, report = compile_theme(self.theme)
        self.assertEqual(report["origins"]["type.title.font-size"]["kind"], "extracted")

    def test_extension_role_requires_explicit_bindings(self):
        with self.assertRaisesRegex(ValueError, "explicit font bindings"):
            compile_theme(self.theme, roles=["quote"])
        for prop in ("font-family", "font-size"):
            self.theme["$tokens"][f"type.quote.{prop}"] = {"$type": self.theme["$tokens"][f"type.body.{prop}"]["$type"], "$value": "{type.body." + prop + "}"}
        css, _ = compile_theme(self.theme, roles=["quote"])
        self.assertIn('[data-text-role="quote"]', css)

    def test_unknown_component_style_does_not_reset_user_css(self):
        css, _ = compile_theme(self.theme)
        self.assertNotIn("border-radius:", css)
        self.assertNotIn("padding:", css)
        self.assertNotIn(".okp-theme figure", css)
        self.assertIn("background-color:", css)
        self.assertNotIn("background:", css)

    def test_background_never_guesses_white_foreground(self):
        self.theme["$tokens"]["color.surface.canvas"]["$value"] = "#f5ce22"
        _, report = compile_theme(self.theme)
        self.assertEqual(report["resolved"]["color.on-surface.canvas.primary"], "#20252a")

    def test_context_selection_and_surface_separation(self):
        self.theme["contexts"] = {"profiles": {"cover": {"$tokens": {"type.title.font-size": token("dimension", {"value": 80, "unit": "px"})}}}, "surfaces": {"dark": {"$tokens": {"color.surface.canvas": token("color", "#111111"), "color.on-surface.canvas.primary": token("color", "#eeeeee"), "color.on-surface.canvas.secondary": token("color", "#cccccc"), "color.border.canvas": token("color", "#555555")}}}}
        css, report = compile_theme(self.theme, profile="cover", surface="dark")
        self.assertIn('.okp-theme[data-type-profile="cover"][data-surface="dark"]', css)
        self.assertEqual(report["resolved"]["type.title.font-size"]["value"], 80)
        self.assertEqual(report["resolved"]["type.body.font-size"]["value"], 32)
        self.assertEqual(report["resolved"]["color.surface.canvas"], "#111111")
        partial = copy.deepcopy(self.theme)
        del partial["contexts"]["surfaces"]["dark"]["$tokens"]["color.border.canvas"]
        with self.assertRaisesRegex(ValueError, "SURFACE_OVERRIDE_PAIR_INCOMPLETE"):
            compile_theme(partial, surface="dark")
        self.theme["contexts"]["surfaces"]["dark"]["$tokens"]["type.body.font-size"] = token("dimension", {"value": 16, "unit": "px"})
        with self.assertRaisesRegex(ValueError, "Surface overrides"):
            compile_theme(self.theme, surface="dark")

    def test_schema_requires_only_the_core(self):
        schema = json.loads((ROOT / "references/token-contract.schema.json").read_text())
        self.assertEqual(set(schema["properties"]["$tokens"]["required"]), set(CORE))

    def test_surface_pair_is_required(self):
        self.theme["$tokens"]["color.surface.panel"] = token("color", "#aaaaaa")
        with self.assertRaisesRegex(ValueError, "SURFACE_PAIR_INCOMPLETE"):
            compile_theme(self.theme)

    def test_component_color_pair_is_bound_together(self):
        for name, value in {"color.surface.panel": "#dce5cc", "color.on-surface.panel.primary": "#102030", "color.on-surface.panel.secondary": "#405040", "color.border.panel": "#506050"}.items():
            self.theme["$tokens"][name] = token("color", value)
        self.theme["$tokens"]["component.card.surface-role"] = token("string", "panel")
        css, _ = compile_theme(self.theme)
        self.assertIn("--okp-current-text-secondary: var(--okp-color-on-surface-panel-secondary)", css)
        self.assertIn("color: var(--okp-current-text-secondary)", css)

    def test_chart_palette_entity_order(self):
        for i, color in enumerate(["#aa2200", "#0033aa"]): self.theme["$tokens"][f"ref.color.series-{i}"] = token("color", color)
        self.theme["$tokens"]["chart.series.colors"] = token("color-list", ["{ref.color.series-0}", "{ref.color.series-1}"])
        _, report = compile_theme(self.theme)
        self.assertEqual(report["resolved"]["chart.series.colors"], ["#aa2200", "#0033aa"])

    def test_font_string_cannot_close_style(self):
        self.theme["$tokens"]["type.body.font-family"]["$value"] = ['</style><script>alert(1)</script>']
        css, _ = compile_theme(self.theme)
        self.assertNotIn("</style>", css)

    def test_negative_cases(self):
        cases = []
        bad = copy.deepcopy(self.theme); del bad["$tokens"]["type.title.font-size"]; cases.append((bad, "Missing core"))
        bad = copy.deepcopy(self.theme); bad["$tokens"]["type.title.font-size"]["$value"] = "{ref.missing.size}"; cases.append((bad, "TOKEN_REF_MISSING"))
        bad = copy.deepcopy(self.theme); bad["$tokens"]["type.title.font-size"]["$value"] = "{type.body.font-size}"; bad["$tokens"]["type.body.font-size"]["$value"] = "{type.title.font-size}"; cases.append((bad, "TOKEN_REF_CYCLE"))
        bad = copy.deepcopy(self.theme); bad["$tokens"]["type.title.font-size"]["$value"] = "{type.title.font-family}"; cases.append((bad, "TOKEN_TYPE_MISMATCH"))
        bad = copy.deepcopy(self.theme); bad["$tokens"]["type.title.font-size"]["$value"] = "{runtime.title.font-size}"; cases.append((bad, "TOKEN_LAYER_VIOLATION"))
        bad = copy.deepcopy(self.theme); bad["$tokens"]["type.title.font-size"]["$value"] = {"value": 24, "unit": "pt"}; cases.append((bad, "normalized px"))
        bad = copy.deepcopy(self.theme); bad["$tokens"]["type.title.font-size"]["$value"]["value"] = 0; cases.append((bad, "Non-positive"))
        bad = copy.deepcopy(self.theme); bad["$tokens"]["type.title.font-size"]["$value"]["value"] = float("nan"); cases.append((bad, "Invalid dimension"))
        bad = copy.deepcopy(self.theme); del bad["$tokens"]["type.title.font-size"]["$extensions"]; cases.append((bad, "TOKEN_ORIGIN_MISSING"))
        bad = copy.deepcopy(self.theme); bad["$tokens"]["type.title.font-size"]["$extensions"]["origin"] = {"kind": "extracted"}; cases.append((bad, "source location"))
        bad = copy.deepcopy(self.theme); bad["$tokens"]["type.title.font-size"]["$extensions"]["origin"] = {"kind": "inferred"}; cases.append((bad, "Inference needs"))
        bad = copy.deepcopy(self.theme); bad["$tokens"]["type.title.font-size"]["$value"] = "{type.body.font-size}"; bad["$tokens"]["type.title.font-size"]["$extensions"]["origin"] = {"kind": "unknown"}; cases.append((bad, "TOKEN_ORIGIN_MISSING"))
        bad = copy.deepcopy(self.theme); bad["$tokens"]["color.surface.canvas"]["$value"] = "url(https://example.com)"; cases.append((bad, "Invalid color"))
        bad = copy.deepcopy(self.theme); bad["$tokens"]["type.bad_name.font-size"] = token("dimension", {"value": 24, "unit": "px"}); cases.append((bad, "TOKEN_NAME_INVALID"))
        bad = copy.deepcopy(self.theme); bad["$tokens"]["type.a-b.font-size"] = token("dimension", {"value": 24, "unit": "px"}); bad["$tokens"]["type.a.b-font-size"] = token("dimension", {"value": 24, "unit": "px"}); cases.append((bad, "TOKEN_CSS_NAME_COLLISION"))
        bad = copy.deepcopy(self.theme); bad["$tokens"]["component.card.padding"] = {"$type": "dimension", "$value": "{ref.padding.value}"}; bad["$tokens"]["ref.padding.value"] = token("dimension", {"value": 24, "unit": "px"}); cases.append((bad, "semantic roles"))
        bad = copy.deepcopy(self.theme); bad["$tokens"]["component.card.padding"] = token("number", 24); cases.append((bad, "Wrong component property type"))
        for theme, message in cases:
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message): compile_theme(theme)

    def test_catalog_and_theme_independence(self):
        catalog = json.loads((ROOT / "references/catalog.json").read_text())
        self.assertEqual(len(catalog["layouts"]), 6)
        for layout in catalog["layouts"]:
            path = ROOT / "references" / layout["file"]
            fragment = path.read_text()
            tree = ET.fromstring(fragment)
            self.assertEqual(tree.attrib["data-layout"], layout["id"])
            self.assertEqual(set(re.findall(r'data-text-role="([^"]+)"', fragment)), set(layout["roles"]))
            self.assertNotRegex(fragment, r"https?://|<style|<script|style=|font-family|#[0-9a-fA-F]{3,8}")
        geometry = (ROOT / "styles/geometry.css").read_text()
        self.assertNotRegex(geometry, r"font(?:-family|-size|-weight)\s*:|(?:background|color|border-radius)\s*:|https?://|#[0-9a-fA-F]{3,8}")

    def test_preview_is_materialized_and_self_contained(self):
        with tempfile.TemporaryDirectory() as out:
            build(out)
            html = (Path(out) / "deck.html").read_text()
            self.assertNotIn("{{", html)
            self.assertNotIn("data-repeat=", html)
            self.assertNotRegex(html, r'(?:src|href)="https?://')
            self.assertEqual(html.count('class="slide"'), 12)

    def test_native_pptx_evidence_not_role_extraction(self):
        with tempfile.TemporaryDirectory() as out:
            source = Path(out) / "fixture.pptx"
            with ZipFile(source, "w") as archive:
                archive.writestr("ppt/presentation.xml", '<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:sldSz cx="12192000" cy="6858000"/></p:presentation>')
                archive.writestr("ppt/slides/slide1.xml", '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><a:rPr sz="2400"><a:latin typeface="+mn-lt"/><a:srgbClr val="ABCDEF"><a:alpha val="50000"/></a:srgbClr></a:rPr><a:normAutofit fontScale="80000"/></p:sld>')
            report = inspect(source)
            self.assertEqual(report["slideCount"], 1)
            size = next(r for r in report["observations"] if r["property"] == "font-size")
            self.assertEqual(size["value"], 24)
            self.assertEqual(size["normalized"]["value"], 40)
            self.assertFalse(size["effective"])
            self.assertEqual(report["counts"]["source-autofit"], 1)
            self.assertIn("Effective run/placeholder/layout/master/theme inheritance", report["unknown"])

    def test_units_use_single_uniform_transform(self):
        transform = canvas_transform({"widthPt": 960, "heightPt": 540}, 1600, 900)
        self.assertAlmostEqual(transform["scalePxPerPt"], 1600 / 960)
        self.assertEqual(transform["offsetXPx"], 0)
        self.assertEqual(transform["offsetYPx"], 0)


if __name__ == "__main__":
    unittest.main()
