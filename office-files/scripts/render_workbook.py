#!/usr/bin/env python3
"""Export the verified XLSX candidate once and prepare a batch visual review.

The PDF uses the workbook's print settings in LibreOffice Calc. It is not a
native Excel screenshot or a second numeric verification. Existing valid
previews are reused without clearing handwritten review observations.
"""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import pymupdf
from openpyxl import load_workbook

from check_workbook import fingerprint, load_verified_report, validate_preview, write_json
import page_gallery


LIMITATIONS = [
    "These are LibreOffice Calc print previews, not native Microsoft Excel screenshots; native Excel appearance was not verified.",
    "The PDF follows visible sheets and their print areas. Check that the intended workbook content is included; hidden or nonprinting content is outside this visual review.",
]


def sheet_scope(candidate):
    workbook = load_workbook(candidate, data_only=False)
    try:
        return [
            {"name": sheet.title, "state": sheet.sheet_state,
             "print_area": str(sheet.print_area) if sheet.print_area else "automatic used area",
             "used_range": sheet.calculate_dimension(), "charts": len(sheet._charts)}
            for sheet in workbook
        ]
    finally:
        workbook.close()


def render(qa, dpi=144):
    qa = Path(qa).resolve(strict=True)
    report = load_verified_report(qa)
    output = qa / "preview"
    if not 72 <= dpi <= 240:
        raise ValueError("Choose 72–240 DPI for a readable preview.")
    if output.exists():
        validate_preview(qa, report, require_review=False)
        return {"status": "NEEDS_VISUAL_REVIEW", "reused": True,
                "gallery": str(output / "gallery/index.html"), "review": str(output / "review.json")}
    engine = shutil.which("soffice")
    if not engine:
        raise ValueError("Install libreoffice-calc to render workbook previews.")
    candidate = Path(report["candidate"]["path"])
    inputs = {
        "candidate": report["candidate"], "verification": fingerprint(qa / "verification.json"),
        "renderer": fingerprint(__file__), "gallery_builder": fingerprint(page_gallery.__file__),
    }
    scopes = sheet_scope(candidate)
    with tempfile.TemporaryDirectory(prefix=".workbook-preview-", dir=qa) as temporary:
        temporary = Path(temporary)
        stage = temporary / "preview"
        stage.mkdir()
        command = [engine, f"-env:UserInstallation={(temporary / 'libreoffice-profile').as_uri()}",
                   "--headless", "--convert-to", "pdf:calc_pdf_Export", "--outdir", str(stage), str(candidate)]
        process = subprocess.run(command, capture_output=True, text=True, timeout=120, check=False)
        converted = stage / candidate.with_suffix(".pdf").name
        if process.returncode or not converted.is_file() or not converted.stat().st_size:
            raise ValueError(f"Calc did not produce a PDF preview. {process.stdout.strip()} {process.stderr.strip()}")
        pdf = stage / "preview.pdf"
        if converted != pdf:
            converted.rename(pdf)
        inputs["pdf"] = {"path": str(output / pdf.name), "sha256": fingerprint(pdf)["sha256"]}
        pages = []
        with pymupdf.open(pdf) as document:
            for index, page in enumerate(document, 1):
                image = stage / f"page-{index:03d}.png"
                page.get_pixmap(dpi=dpi, alpha=False).save(image)
                pages.append({"number": index, "image": {"path": image.name, "sha256": fingerprint(image)["sha256"]},
                              "width_pt": round(page.rect.width, 2), "height_pt": round(page.rect.height, 2)})
        if not pages:
            raise ValueError("Calc produced an empty preview; check the workbook's print areas.")
        preview = {
            "schema_version": 1, "kind": "office-workbook-preview", "status": "needs-review",
            "created_at": datetime.now(timezone.utc).isoformat(), "inputs": inputs,
            "sheets": scopes, "page_count": len(pages), "pages": pages, "dpi": dpi,
            "engine": {"command": command, "returncode": process.returncode,
                       "stdout": process.stdout, "stderr": process.stderr},
            "limitations": LIMITATIONS,
        }
        write_json(stage / "inspection.json", preview)
        review = {
            "schema_version": 1, "kind": "office-workbook-review",
            "inspection_sha256": fingerprint(stage / "inspection.json")["sha256"],
            "instructions": "Use the contact sheets for an overview, then inspect every page at readable size. Record a short observation about text clipping/wrapping, table and number-format readability, and any chart labels/overlap. Set status to pass only after reviewing that page. Confirm the printed scope covers the intended visible content. This does not establish native Excel appearance.",
            "pages": [{"number": page["number"], "image_sha256": page["image"]["sha256"],
                       "status": "pending", "observations": ""} for page in pages],
        }
        write_json(stage / "review.json", review)
        page_gallery.build_gallery(stage)
        # Do not bind a preview to data that changed during export or image creation.
        load_verified_report(qa)
        for role in ("candidate", "verification", "renderer", "gallery_builder"):
            if fingerprint(inputs[role]["path"]) != inputs[role]:
                raise ValueError(f"The {role} changed during preview creation; render the current candidate.")
        stage.replace(output)
    return {"status": "NEEDS_VISUAL_REVIEW", "reused": False, "pages": len(pages),
            "pdf": str(output / "preview.pdf"), "gallery": str(output / "gallery/index.html"),
            "review": str(output / "review.json"), "print_scope": scopes, "limitations": LIMITATIONS}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--qa", required=True, type=Path, help="QA directory with a successful verification.json.")
    parser.add_argument("--dpi", type=int, default=144, help="PNG resolution, 72–240; default 144.")
    args = parser.parse_args()
    try:
        print(json.dumps(render(args.qa, args.dpi), ensure_ascii=False))
        return 0
    except (ValueError, OSError, KeyError, TypeError, subprocess.TimeoutExpired) as error:
        print(json.dumps({"status": "PREVIEW_FAILED", "error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
