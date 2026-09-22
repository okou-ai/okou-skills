#!/usr/bin/env python3
"""Render new Markdown, check independent expectations, and prepare page review.

This optional orchestration never writes passing review statuses or accepts a
document. Native Word/PDF and template-editing routes keep their existing tools.
"""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from time import perf_counter

import check_document
import render_document


def merge_expectations(authored, seed):
    """Supplement author checks from the Markdown AST, never from output text."""
    merged = {"not_applicable": dict(authored["not_applicable"])}
    for key in ("required_text", "same_page"):
        merged[key] = list(authored[key])
        if key not in merged["not_applicable"]:
            for item in seed[key]:
                if item not in merged[key]:
                    merged[key].append(item)
    return merged


def prepare(source, out, expectations, *, output_format="both", lang=None,
            reference=None, style=None, resources=(), table_widths="auto",
            review_format="compact"):
    source, out = Path(source).resolve(), Path(out).resolve()
    expected_path = Path(expectations).resolve(strict=True)
    if source.suffix.lower() not in {".md", ".markdown"}:
        raise ValueError("Preparation is for new Markdown. Use the native Word/PDF workflow for existing files.")
    authored = check_document.read_expectations(expected_path)
    if not authored["required_text"] and not authored["not_applicable"].get("required_text"):
        raise ValueError("Supply independent required_text expectations, or a concrete not_applicable reason, before rendering.")
    # Preserve all authored input files. This command owns its output directory;
    # author expectations/data/style outside it, including on repeated runs.
    inputs = [source, expected_path, *(Path(p).resolve(strict=True) for p in resources)]
    inputs.extend(Path(p).resolve(strict=True) for p in (reference, style) if p)
    if any(path == out or out in path.parents for path in inputs):
        raise ValueError("Keep source, expectations, style and resources outside --out; existing authored checks are never overwritten.")
    out.mkdir(parents=True, exist_ok=True)
    qa = out / "qa"
    (qa / "acceptance.json").unlink(missing_ok=True)
    record = {"status": "preparing", "started_at": datetime.now(timezone.utc).isoformat(),
              "stage_seconds": {}, "visual_review": "pending", "acceptance": "not-run"}
    summary_path = out / "prepare.json"
    started = perf_counter()

    def save():
        record["total_seconds"] = round(perf_counter() - started, 3)
        render_document.write_json(summary_path, record)

    def stage(name, action):
        clock = perf_counter()
        try:
            return action()
        finally:
            record["stage_seconds"][name] = round(perf_counter() - clock, 3)
            save()

    save()
    try:
        # Bind the orchestrator and the verification/rendering implementation,
        # not just the source data. Changed code invalidates previous evidence.
        scripts = Path(__file__).resolve().parent
        dependencies = [scripts / name for name in (
            "prepare_document.py", "render_document.py", "document_style.py",
            "check_document.py", "page_gallery.py")]
        manifest = stage("render", lambda: render_document.render(
            source, out, output_format, lang, reference,
            [*resources, expected_path, *dependencies], style, table_widths))
        # The original expectations are resource-bound by render.json. Check
        # that the in-memory values came from those exact bytes as well.
        if authored != check_document.read_expectations(expected_path):
            raise ValueError("Authored expectations changed during preparation; run again with stable inputs.")
        effective = out / "expectations.prepared.json"
        stage("expectations", lambda: render_document.write_json(effective, merge_expectations(
            authored, check_document.read_expectations(out / "expectations.seed.json"))))
        pdf = manifest["outputs"]["pdf"]["path"]
        docx = manifest["outputs"]["docx"]["path"]
        render_path = out / "render.json"
        report = stage("quick", lambda: check_document.quick(pdf, effective, docx, render_path))
        render_document.write_json(out / "quick.json", report)
        record.update({"outputs": manifest["outputs"], "deliver": manifest["deliver"],
                       "source": manifest["source"], "reference": manifest["reference"],
                       "resources": manifest["resources"],
                       "expectations": str(effective), "page_count": report["page_count"],
                       "quick": str(out / "quick.json")})
        if not report["passed"]:
            record.update({"status": "blocked", "findings": report["findings"],
                           "next": "Repair quick-check blockers and prepare again. Page review has not started."})
            save()
            return record
        inspection = stage("inspect", lambda: check_document.inspect(
            pdf, qa, docx, effective, render_path, review_format=review_format))
        blockers = [item for item in inspection["findings"] if item["severity"] == "blocker"]
        record.update({"status": "blocked" if blockers else "needs-visual-review",
                       "findings": inspection["findings"], "review": str(qa / "review.json"),
                       "gallery": str(qa / "gallery" / "index.html"),
                       "next": "Open every full page PNG, explicitly review all five criteria and every warning, then run check_document.py accept on the qa directory."})
        save()
        return record
    except Exception as error:
        record.update({"status": "failed", "error": str(error)})
        save()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="New Markdown document")
    parser.add_argument("--out", type=Path, required=True, help="Generated files and qa directory; separate from authored inputs")
    parser.add_argument("--expectations", type=Path, required=True, help="Existing task-specific expectations derived independently from request/data")
    parser.add_argument("--format", choices=("pdf", "docx", "both"), default="both")
    parser.add_argument("--lang")
    parser.add_argument("--reference", type=Path)
    parser.add_argument("--style", type=Path)
    parser.add_argument("--resource", type=Path, action="append", default=[], help="Bind calculation scripts, data, chart specs or assets; repeat as needed")
    parser.add_argument("--table-widths", choices=("auto", "source"), default="auto")
    parser.add_argument("--review-format", choices=("verbose", "compact"), default="compact")
    args = parser.parse_args()
    try:
        result = prepare(args.source, args.out, args.expectations, output_format=args.format,
                         lang=args.lang, reference=args.reference, style=args.style,
                         resources=args.resource, table_widths=args.table_widths,
                         review_format=args.review_format)
    except Exception as error:
        print(f"Document preparation failed: {error}", file=sys.stderr)
        return 2
    summary = {key: result[key] for key in (
        "status", "stage_seconds", "total_seconds", "page_count", "review", "gallery", "next") if key in result}
    summary.update({"record": str(args.out.resolve() / "prepare.json"),
                    "blockers": [item["code"] for item in result.get("findings", []) if item["severity"] == "blocker"],
                    "warnings": sum(item["severity"] == "warning" for item in result.get("findings", []))})
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "needs-visual-review" else 2


if __name__ == "__main__":
    sys.exit(main())
