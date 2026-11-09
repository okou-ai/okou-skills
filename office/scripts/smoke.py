#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Reproducible tiny controls, not a business example or model benchmark.

Requires xlsx/requirements-authoring.txt in this interpreter. --with-pdf also
requires reportlab and Poppler; --with-calc requires a functioning Calc engine.
All generated fixtures, command audit receipts and results stay in a NEW --out.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--out", type=Path, required=True, help="New working directory; existing directories refused")
    p.add_argument("--with-calc", action="store_true", help="Actually run Calc control and candidate recalculation; unavailable/failure is nonzero")
    p.add_argument("--with-pdf", action="store_true", help="Create a one-page ReportLab control and actually run pdfinfo/Poppler (not Office-native QA)")
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    work = args.out.resolve()
    receipts = []

    def call(name, *arguments):
        argv = [sys.executable, str(HERE / "office.py"), *map(str, arguments)]
        result = subprocess.run(argv, capture_output=True, text=True, timeout=180)
        receipt = json.loads(result.stdout)
        receipt["invocation"] = argv
        receipt["process_exit"] = result.returncode
        receipt["process_stderr"] = result.stderr
        (work / f"{name}.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
        receipts.append({"name": name, "status": receipt["status"], "process_exit": result.returncode})
        return result.returncode == 0

    from openpyxl import Workbook, load_workbook
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Control"
    sheet["A1"], sheet["B1"], sheet["C1"] = 19, 23, "=SUM(A1:B1)"
    sheet.append(["A", "B", "Sum"])
    for column in "ABC":
        sheet.column_dimensions[column].width = 24
    source = work / "control.xlsx"
    workbook.save(source)
    original = hashlib.sha256(source.read_bytes()).hexdigest()
    plan = work / "style-plan.json"
    plan.write_text(json.dumps({"operations": [
        {"op": "style_value", "sheet": "Control", "cell": "A1", "role": "source", "kind": "integer"},
        {"op": "style_value", "sheet": "Control", "cell": "B1", "role": "source", "kind": "integer"},
        {"op": "style_value", "sheet": "Control", "cell": "C1", "role": "same_sheet", "kind": "integer"},
        {"op": "table_header", "sheet": "Control", "range": "A2:C2"},
        {"op": "report_band", "sheet": "Control", "range": "A4:C4", "text": "Mechanical control", "level": "title"},
        {"op": "report_page", "sheet": "Control", "range": "A1:C4", "orientation": "portrait"}
    ]}), encoding="utf-8")
    call("discover", "list")
    styled = work / "styled.xlsx"
    if call("style", "style", "--input", source, "--out", styled, "--plan", plan, "--use-finance-defaults"):
        call("static", "validate", "--input", styled, "--styles")
        check = load_workbook(styled)
        assert check["Control"]["C1"].value == "=SUM(A1:B1)"
        assert str(check["Control"].merged_cells) == "A4:C4"
        assert check["Control"].page_setup.fitToWidth == 1
        check.close()
    assert hashlib.sha256(source.read_bytes()).hexdigest() == original
    if args.with_calc:
        candidate = work / "recalculated.xlsx"
        if call("recalc", "recalc", "--input", styled, "--out", candidate, "--timeout", "30"):
            values = load_workbook(candidate, data_only=True)
            formulas = load_workbook(candidate, data_only=False)
            assert values["Control"]["C1"].value == 42
            assert formulas["Control"]["C1"].data_type == "f"
            values.close()
            formulas.close()
    if args.with_pdf:
        from reportlab.pdfgen import canvas
        pdf = work / "control.pdf"
        page = canvas.Canvas(str(pdf))
        page.drawString(72, 760, "Mechanical PDF control: 19 + 23 = 42")
        page.save()
        call("pdf-metadata", "validate", "--input", pdf)
        call("pdf-raster", "render", "--input", pdf, "--pages", work / "pages")
    result = {"status": "ok" if all(r["status"] == "ok" for r in receipts) else "failed",
              "source_preserved": True, "commands": receipts,
              "limits": "Synthetic controls only. Static scans and PDF rasterization are not business correctness or native Excel/Word approval."}
    (work / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
