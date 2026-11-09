#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
style_audit.py — Limited style diagnostics for xlsx files.

Audits an xlsx file (or an unpacked xlsx directory) and reports:
1. Selected style counts: fonts, fills, and cellXfs counts match their elements
2. Explicit RGB convention: blue formulas; possible black numeric inputs (warning)
3. Year-like values with comma formats (heuristic, not business-role validation)
4. Percentage-formatted values > 1 (warning, not necessarily an error)
5. Invalid/out-of-range style and font references on explicitly styled cells
6. fills[0]/fills[1] presence and base-pattern checks

Usage:
    python3 style_audit.py input.xlsx                  # audit a packed xlsx
    python3 style_audit.py /tmp/xlsx_work/             # audit an unpacked directory
    python3 style_audit.py input.xlsx --json           # machine-readable output
    python3 style_audit.py input.xlsx --summary        # counts and scope, no detail
    python3 style_audit.py input.xlsx --json --summary # machine-readable counts and scope

These are structural checks and formatting heuristics, not business, visual, or
complete financial-role validation. Theme/indexed colors are not resolved.

Exit code:
    0 — no implemented-check violations found (warnings may need review)
    1 — violations detected, or input cannot be loaded/audited
"""

import sys
import os
import zipfile
import xml.etree.ElementTree as ET
import json
import re
import posixpath
from pathlib import Path
from urllib.parse import unquote, urlsplit
import tempfile
import shutil

NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NSP = f"{{{NS}}}"

AUDIT_SCOPE = (
    "Implemented checks: selected style counts, required base fills, referenced "
    "style/font indices, explicit RGB font conventions, and simple year/percentage "
    "format heuristics for explicitly styled cells; no business, visual, or full "
    "financial-role validation. Theme/indexed colors are not resolved."
)

# Predefined style index semantics from minimal_xlsx template.
# Maps cellXfs index -> (role, font_color_expectation, numFmt_type)
# role: "input" = blue expected, "formula" = black/green expected, "header" = any, "any" = skip
TEMPLATE_SLOT_ROLES = {
    0:  ("any",     None,    None),
    1:  ("input",   "blue",  "general"),
    2:  ("formula", "black", "general"),
    3:  ("formula", "green", "general"),
    4:  ("any",     None,    "general"),   # header
    5:  ("input",   "blue",  "currency"),
    6:  ("formula", "black", "currency"),
    7:  ("input",   "blue",  "percent"),
    8:  ("formula", "black", "percent"),
    9:  ("input",   "blue",  "integer"),
    10: ("formula", "black", "integer"),
    11: ("input",   "blue",  "year"),
    12: ("input",   "blue",  "general"),   # highlight
}

# Normalize 6-digit RGB and OOXML's 8-digit AARRGGBB for role comparisons;
# the alpha prefix does not change the RGB font-role convention checked here.
BLUE_RGB  = "0000ff"
BLACK_RGB = "000000"
GREEN_RGB = "008000"
RED_RGB   = "ff0000"

# Only built-in IDs have stable meanings. Custom IDs (>=164) are workbook-local.
PERCENT_FMT_IDS = {9, 10}
COMMA_FMT_IDS = {3, 4}  # #,##0 style — 4-digit years would show as 2,024


def _parse_styles(styles_xml: bytes) -> dict:
    """Parse styles.xml and return structured data."""
    root = ET.fromstring(styles_xml)

    def find(tag):
        return root.find(f"{NSP}{tag}")

    # numFmts
    num_fmts = {}  # id -> formatCode
    nf_elem = find("numFmts")
    if nf_elem is not None:
        declared_count = int(nf_elem.get("count", "0"))
        actual_count = len(nf_elem)
        for nf in nf_elem:
            fid = int(nf.get("numFmtId", "0"))
            num_fmts[fid] = nf.get("formatCode", "")
    else:
        declared_count = 0
        actual_count = 0

    # fonts — extract color and bold flag
    fonts = []
    fonts_elem = find("fonts")
    fonts_declared = 0
    if fonts_elem is not None:
        fonts_declared = int(fonts_elem.get("count", "0"))
        for font in fonts_elem:
            color_elem = font.find(f"{NSP}color")
            bold_elem = font.find(f"{NSP}b")
            if color_elem is not None:
                rgb = color_elem.get("rgb", "").lower()
                theme = color_elem.get("theme")
            else:
                rgb = ""
                theme = None
            fonts.append({
                "rgb": rgb,
                "theme": theme,
                "bold": (bold_elem is not None
                         and bold_elem.get("val", "1").lower() not in ("0", "false")),
            })

    # fills
    fills = []
    fills_elem = find("fills")
    fills_declared = 0
    if fills_elem is not None:
        fills_declared = int(fills_elem.get("count", "0"))
        for fill in fills_elem:
            pf = fill.find(f"{NSP}patternFill")
            pattern_type = pf.get("patternType", "none") if pf is not None else ""
            fills.append({"patternType": pattern_type})

    # cellXfs
    xfs = []
    xfs_elem = find("cellXfs")
    xfs_declared = 0
    if xfs_elem is not None:
        xfs_declared = int(xfs_elem.get("count", "0"))
        for xf in xfs_elem:
            xfs.append({
                "numFmtId": int(xf.get("numFmtId", "0")),
                "fontId":   int(xf.get("fontId", "0")),
                "fillId":   int(xf.get("fillId", "0")),
                "borderId": int(xf.get("borderId", "0")),
            })

    return {
        "num_fmts": num_fmts,
        "num_fmts_declared": declared_count,
        "num_fmts_actual": actual_count,
        "fonts": fonts,
        "fonts_declared": fonts_declared,
        "fonts_actual": len(fonts),
        "fills": fills,
        "fills_declared": fills_declared,
        "fills_actual": len(fills),
        "xfs": xfs,
        "xfs_declared": xfs_declared,
        "xfs_actual": len(xfs),
    }


def _normalize_rgb(rgb: str) -> str:
    """Return RRGGBB for supported explicit RGB encodings, else unknown (empty)."""
    if not re.fullmatch(r"(?:[0-9a-fA-F]{6}|[0-9a-fA-F]{8})", rgb):
        return ""
    return rgb[-6:].lower()


def _is_blue_font(font: dict) -> bool:
    return _normalize_rgb(font["rgb"]) == BLUE_RGB


def _is_black_font(font: dict) -> bool:
    # A theme/indexed color needs workbook theme/palette resolution; do not guess.
    return _normalize_rgb(font["rgb"]) == BLACK_RGB


def _is_green_font(font: dict) -> bool:
    return _normalize_rgb(font["rgb"]) == GREEN_RGB


def _fmt_is_percent(num_fmt_id: int, num_fmts: dict) -> bool:
    if num_fmt_id < 164:
        return num_fmt_id in PERCENT_FMT_IDS
    fmt_code = num_fmts.get(num_fmt_id, "")
    return "%" in fmt_code


def _fmt_is_comma(num_fmt_id: int, num_fmts: dict) -> bool:
    if num_fmt_id < 164:
        return num_fmt_id in COMMA_FMT_IDS
    fmt_code = num_fmts.get(num_fmt_id, "")
    # formatCode has comma separator if it contains #,##0 but not a trailing , (scale)
    return "#,##" in fmt_code and not fmt_code.endswith(",") and not fmt_code.endswith(",\"M\"") and not fmt_code.endswith(",\"K\"")


def _looks_like_year(value_text: str) -> bool:
    """True if value is a 4-digit year between 1900 and 2100."""
    try:
        v = int(float(value_text))
        return 1900 <= v <= 2100
    except (ValueError, TypeError, OverflowError):
        return False


def _audit(styles_xml: bytes, sheet_xmls: list[tuple[str, bytes]]) -> dict:
    """
    Run the implemented structural checks and formatting heuristics.

    Args:
        styles_xml: content of xl/styles.xml
        sheet_xmls: list of (sheet_name, xml_bytes) for each worksheet

    Returns:
        dict with violations and summary
    """
    results = {
        "scope": AUDIT_SCOPE,
        "violations": [],
        "warnings": [],
        "summary": {},
    }
    v = results["violations"]
    w = results["warnings"]

    styles = _parse_styles(styles_xml)
    fonts  = styles["fonts"]
    xfs    = styles["xfs"]
    num_fmts = styles["num_fmts"]

    # ── Check A: count attribute integrity ──────────────────────────────────
    if styles["fonts_declared"] != styles["fonts_actual"]:
        v.append({
            "type": "count_mismatch",
            "element": "fonts",
            "declared": styles["fonts_declared"],
            "actual": styles["fonts_actual"],
            "fix": f"Update <fonts count=\"{styles['fonts_actual']}\">",
        })
    if styles["fills_declared"] != styles["fills_actual"]:
        v.append({
            "type": "count_mismatch",
            "element": "fills",
            "declared": styles["fills_declared"],
            "actual": styles["fills_actual"],
            "fix": f"Update <fills count=\"{styles['fills_actual']}\">",
        })
    if styles["xfs_declared"] != styles["xfs_actual"]:
        v.append({
            "type": "count_mismatch",
            "element": "cellXfs",
            "declared": styles["xfs_declared"],
            "actual": styles["xfs_actual"],
            "fix": f"Update <cellXfs count=\"{styles['xfs_actual']}\">",
        })

    # ── Check B: fills[0] and fills[1] presence ──────────────────────────────
    fills = styles["fills"]
    if len(fills) < 2:
        v.append({
            "type": "missing_required_fills",
            "detail": "fills[0] (none) and fills[1] (gray125) are required by OOXML spec",
            "fix": "Prepend <fill><patternFill patternType='none'/></fill> and <fill><patternFill patternType='gray125'/></fill>",
        })
    else:
        if fills[0].get("patternType") != "none":
            v.append({
                "type": "fills_0_corrupted",
                "detail": f"fills[0] patternType='{fills[0].get('patternType')}', must be 'none'",
                "fix": "Set fills[0] patternFill patternType to 'none'",
            })
        if fills[1].get("patternType") != "gray125":
            v.append({
                "type": "fills_1_corrupted",
                "detail": f"fills[1] patternType='{fills[1].get('patternType')}', must be 'gray125'",
                "fix": "Set fills[1] patternFill patternType to 'gray125'",
            })

    # ── Check C: per-cell style violations ───────────────────────────────────
    total_cells = 0
    formula_cells = 0
    input_cells = 0

    for sheet_name, sheet_xml in sheet_xmls:
        ws = ET.fromstring(sheet_xml)

        for cell in ws.findall(f".//{NSP}c"):
            cell_ref = cell.get("r", "?")
            s_attr = cell.get("s")
            has_formula = cell.find(f"{NSP}f") is not None
            v_elem = cell.find(f"{NSP}v")
            value_text = v_elem.text if v_elem is not None else None
            total_cells += 1
            if has_formula:
                formula_cells += 1
            elif value_text is not None:
                input_cells += 1

            # Skip cells with no explicit style
            if s_attr is None:
                continue

            try:
                s_idx = int(s_attr)
            except ValueError:
                v.append({
                    "type": "invalid_style_index",
                    "sheet": sheet_name,
                    "cell": cell_ref,
                    "s": s_attr,
                    "fix": "Use a non-negative integer s attribute referencing cellXfs.",
                })
                continue

            # Check C1: s index out of range
            if s_idx < 0 or s_idx >= len(xfs):
                v.append({
                    "type": "style_index_out_of_range",
                    "sheet": sheet_name,
                    "cell": cell_ref,
                    "s": s_idx,
                    "cellXfs_count": len(xfs),
                    "fix": f"s={s_idx} is outside cellXfs range 0..{len(xfs) - 1}; use a valid style reference",
                })
                continue

            xf = xfs[s_idx]
            font_id = xf["fontId"]
            num_fmt_id = xf["numFmtId"]

            if font_id < 0 or font_id >= len(fonts):
                v.append({
                    "type": "font_index_out_of_range",
                    "sheet": sheet_name,
                    "cell": cell_ref,
                    "fontId": font_id,
                    "fonts_count": len(fonts),
                    "fix": f"fontId={font_id} is outside fonts range 0..{len(fonts) - 1}; use a valid font reference",
                })
                continue

            font = fonts[font_id]

            # Check C2: color-role violation — formula cell with blue font
            if has_formula and _is_blue_font(font):
                f_elem = cell.find(f"{NSP}f")
                formula_text = f_elem.text if f_elem is not None else ""
                v.append({
                    "type": "formula_cell_blue_font",
                    "sheet": sheet_name,
                    "cell": cell_ref,
                    "s": s_idx,
                    "formula": formula_text,
                    "fix": "Under the input/formula font convention, use an appropriate black-font "
                           "formula or green-font cross-sheet style. Style indices are workbook-local.",
                })

            # Check C3: color-role violation — non-formula cell with explicit black
            # (only flag if it looks like it should be an input — has a numeric value)
            if (not has_formula and _is_black_font(font)
                    and value_text is not None
                    and not font.get("bold")
                    and num_fmt_id not in (0,)   # skip general-format black (could be label)
            ):
                try:
                    float(value_text)
                    # It's a numeric value with black font — possible missing blue input marker
                    w.append({
                        "type": "numeric_input_may_lack_blue",
                        "sheet": sheet_name,
                        "cell": cell_ref,
                        "s": s_idx,
                        "value": value_text,
                        "note": "Hardcoded numeric value has black font — if this is a user-editable "
                                "assumption under the input/formula font convention, use an appropriate "
                                "blue-font input style. Style indices are workbook-local.",
                    })
                except (ValueError, TypeError):
                    pass

            # Check C4: year value with comma-formatted numFmt
            if value_text and _looks_like_year(value_text) and _fmt_is_comma(num_fmt_id, num_fmts):
                v.append({
                    "type": "year_with_comma_format",
                    "sheet": sheet_name,
                    "cell": cell_ref,
                    "s": s_idx,
                    "value": value_text,
                    "numFmtId": num_fmt_id,
                    "fix": "If this value is a year, use a plain integer format ('0') rather than a "
                           "thousands separator, so it displays as 2024 not 2,024.",
                })

            # Check C5: percentage format with value > 1 (likely 8 instead of 0.08)
            if value_text and _fmt_is_percent(num_fmt_id, num_fmts):
                try:
                    pct_val = float(value_text)
                    if pct_val > 1.0:
                        w.append({
                            "type": "percent_value_gt_1",
                            "sheet": sheet_name,
                            "cell": cell_ref,
                            "s": s_idx,
                            "value": value_text,
                            "displayed_as": f"{pct_val * 100:.0f}%",
                            "note": f"Value {value_text} with percentage format displays as {pct_val*100:.0f}%. "
                                    "If intended rate is ~{:.0f}%, store as {:.4f} instead.".format(
                                        pct_val, pct_val / 100
                                    ),
                        })
                except (ValueError, TypeError):
                    pass

    results["summary"] = {
        "total_cells_inspected": total_cells,
        "formula_cells": formula_cells,
        "input_cells": input_cells,
        "violations": len(v),
        "warnings": len(w),
    }

    return results


def _worksheet_parts(workbook_xml: bytes, relationships_xml: bytes):
    """Resolve internal worksheet targets; never silently omit a referenced part."""
    workbook = ET.fromstring(workbook_xml)
    rels = ET.fromstring(relationships_xml)
    rel_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    by_id = {rel.get("Id"): rel for rel in rels}
    for sheet in workbook.findall(f"{NSP}sheets/{NSP}sheet"):
        name = sheet.get("name", "")
        rel = by_id.get(sheet.get(f"{{{rel_ns}}}id"))
        if rel is None:
            raise ValueError(f"Missing relationship for sheet {name!r}")
        if rel.get("TargetMode") == "External":
            raise ValueError(f"External worksheet relationship for {name!r}")
        kind = rel.get("Type", "").rsplit("/", 1)[-1]
        if kind == "chartsheet":
            continue  # Chart-only sheets contain no worksheet cells to audit.
        if kind != "worksheet":
            raise ValueError(f"Unsupported sheet relationship type for {name!r}: {kind!r}")
        target = rel.get("Target", "")
        uri = urlsplit(target)
        if not target or uri.scheme or uri.netloc or uri.query or uri.fragment:
            raise ValueError(f"Invalid internal worksheet target: {target!r}")
        target = unquote(uri.path)
        part = posixpath.normpath(target.lstrip("/") if target.startswith("/")
                                 else posixpath.join("xl", target))
        if part in (".", "..") or part.startswith("../") or "\\" in part:
            raise ValueError(f"Worksheet target escapes package: {target!r}")
        yield name, part


def _load_from_xlsx(xlsx_path: str) -> tuple[bytes, list[tuple[str, bytes]]]:
    """Load styles and every referenced worksheet, including package-absolute targets."""
    with zipfile.ZipFile(xlsx_path, "r") as package:
        styles_xml = package.read("xl/styles.xml")
        parts = _worksheet_parts(package.read("xl/workbook.xml"),
                                 package.read("xl/_rels/workbook.xml.rels"))
        return styles_xml, [(name, package.read(part)) for name, part in parts]


def _load_from_dir(unpacked_dir: str) -> tuple[bytes, list[tuple[str, bytes]]]:
    """Apply the same target resolution to a bounded unpacked package directory."""
    root = Path(unpacked_dir).resolve()
    styles_xml = (root / "xl/styles.xml").read_bytes()
    parts = _worksheet_parts((root / "xl/workbook.xml").read_bytes(),
                             (root / "xl/_rels/workbook.xml.rels").read_bytes())
    sheets = []
    for name, part in parts:
        path = (root / part).resolve()
        if not path.is_relative_to(root):
            raise ValueError(f"Worksheet path escapes unpacked package: {part!r}")
        sheets.append((name, path.read_bytes()))
    return styles_xml, sheets


def main() -> None:
    if "--help" in sys.argv or "-h" in sys.argv:
        print(__doc__)
        return
    use_json = "--json" in sys.argv
    summary_only = "--summary" in sys.argv

    args_clean = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args_clean:
        usage = "Usage: style_audit.py <input.xlsx | unpacked_dir/> [--json] [--summary]"
        print(json.dumps({"error": usage, "scope": AUDIT_SCOPE}) if use_json else usage)
        sys.exit(1)

    target = args_clean[0]

    try:
        if os.path.isdir(target):
            styles_xml, sheet_xmls = _load_from_dir(target)
        elif target.endswith(".xlsx") or target.endswith(".xlsm"):
            styles_xml, sheet_xmls = _load_from_xlsx(target)
        else:
            raise ValueError(f"unrecognized target '{target}' — must be .xlsx/.xlsm file or unpacked directory")
        results = _audit(styles_xml, sheet_xmls)
    except Exception as e:
        error = f"ERROR loading or auditing file: {e}"
        print(json.dumps({"error": error, "scope": AUDIT_SCOPE}) if use_json else error)
        sys.exit(1)

    if use_json:
        output = {"scope": results["scope"], "summary": results["summary"]} if summary_only else results
        print(json.dumps(output, indent=2, ensure_ascii=False))
        sys.exit(1 if results["summary"]["violations"] > 0 else 0)

    # Human-readable output
    s = results["summary"]
    print(f"Target  : {target}")
    print(f"Cells   : {s['total_cells_inspected']} inspected  "
          f"({s['formula_cells']} formula, {s['input_cells']} non-formula with value)")
    print(f"Violations : {s['violations']}")
    print(f"Warnings   : {s['warnings']}")

    if not summary_only:
        if results["violations"]:
            print("\n── Violations (must fix) ──")
            for item in results["violations"]:
                t = item["type"]
                if t == "count_mismatch":
                    print(f"  [FAIL] {item['element']} count mismatch: declared={item['declared']}, "
                          f"actual={item['actual']}")
                    print(f"         Fix: {item['fix']}")
                elif t == "missing_required_fills":
                    print(f"  [FAIL] {item['detail']}")
                    print(f"         Fix: {item['fix']}")
                elif t in ("fills_0_corrupted", "fills_1_corrupted"):
                    print(f"  [FAIL] {item['detail']}")
                    print(f"         Fix: {item['fix']}")
                elif t == "formula_cell_blue_font":
                    print(f"  [FAIL] [{item['sheet']}!{item['cell']}] formula cell has blue font "
                          f"(role=input, but cell contains formula: {item.get('formula', '')})")
                    print(f"         Fix: {item['fix']}")
                elif t == "invalid_style_index":
                    print(f"  [FAIL] [{item['sheet']}!{item['cell']}] invalid s={item['s']!r}")
                    print(f"         Fix: {item['fix']}")
                elif t == "style_index_out_of_range":
                    print(f"  [FAIL] [{item['sheet']}!{item['cell']}] s={item['s']} but "
                          f"cellXfs count={item['cellXfs_count']}")
                    print(f"         Fix: {item['fix']}")
                elif t == "font_index_out_of_range":
                    print(f"  [FAIL] [{item['sheet']}!{item['cell']}] fontId={item['fontId']} but "
                          f"fonts count={item['fonts_count']}")
                    print(f"         Fix: {item['fix']}")
                elif t == "year_with_comma_format":
                    print(f"  [FAIL] [{item['sheet']}!{item['cell']}] year value {item['value']} "
                          f"uses comma-format (numFmtId={item['numFmtId']}) — will display as "
                          f"{int(float(item['value'])):,}")
                    print(f"         Fix: {item['fix']}")
                else:
                    print(f"  [FAIL] {item}")

        if results["warnings"] and not summary_only:
            print("\n── Warnings (review recommended) ──")
            for item in results["warnings"]:
                t = item["type"]
                if t == "numeric_input_may_lack_blue":
                    print(f"  [WARN] [{item['sheet']}!{item['cell']}] numeric value={item['value']} "
                          f"has black font — if user-editable assumption, use blue-font input style")
                elif t == "percent_value_gt_1":
                    print(f"  [WARN] [{item['sheet']}!{item['cell']}] percent-format cell has "
                          f"value={item['value']} (displays as {item['displayed_as']}) — "
                          f"likely should be stored as decimal (e.g. 0.08 for 8%)")
                else:
                    print(f"  [WARN] {item}")

    print()
    print(f"Scope: {results['scope']}")
    if s["violations"] == 0:
        print("PASS — No violations detected by implemented style checks")
        if s["warnings"]:
            print(f"REVIEW — {s['warnings']} warning(s) need review")
    else:
        print(f"FAIL — Implemented style checks found {s['violations']} violation(s)")
        sys.exit(1)


if __name__ == "__main__":
    main()
