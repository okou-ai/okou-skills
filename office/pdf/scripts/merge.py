#!/usr/bin/env python3
"""
merge.py — Merge cover.pdf + body.pdf → final.pdf and print a QA report.

Usage:
    python3 merge.py --cover cover.pdf --body body.pdf --out final.pdf
    python3 merge.py --cover cover.pdf --body body.pdf --out final.pdf --title "My Report"

Exit codes: 0 success, 1 bad args/missing file, 2 missing dep, 3 merge error
"""

import argparse
import json
import os
import sys
import tempfile

from pdf_runtime import DependencyError, require_dependency, require_distinct_output, require_file


def merge(cover_path: str, body_path: str, out_path: str, title: str = "") -> dict:
    require_file(cover_path)
    require_file(body_path)
    require_distinct_output(out_path, cover_path, body_path)
    pypdf = require_dependency("pypdf")
    PdfReader, PdfWriter = pypdf.PdfReader, pypdf.PdfWriter
    cover = PdfReader(cover_path)
    body = PdfReader(body_path)
    cover_pages = len(cover.pages)
    body_pages = len(body.pages)
    if cover_pages != 1 or not body_pages:
        raise ValueError(
            f"Expected one cover page and at least one body page, got {cover_pages} cover and {body_pages} body"
        )

    writer = PdfWriter()
    for reader in (cover, body):
        for page in reader.pages:
            writer.add_page(page)
    if title:
        writer.add_metadata({"/Title": title})

    total_pages = cover_pages + body_pages
    directory = os.path.dirname(os.path.abspath(out_path))
    os.makedirs(directory, exist_ok=True)
    candidate = tempfile.NamedTemporaryFile(dir=directory, prefix=".pdf-", suffix=".tmp", delete=False)
    try:
        with candidate:
            writer.write(candidate)
        if len(PdfReader(candidate.name).pages) != total_pages:
            raise ValueError("Merged PDF page count does not match the input PDFs")
        size_kb = os.path.getsize(candidate.name) // 1024
        os.replace(candidate.name, out_path)
    finally:
        if os.path.exists(candidate.name):
            os.remove(candidate.name)

    warnings = []
    # File size sanity
    if size_kb < 20:
        warnings.append(f"Output is very small ({size_kb} KB) — may have blank pages")
    if size_kb > 50_000:
        warnings.append(f"Output is very large ({size_kb} KB) — consider compressing images")

    report = {
        "status":       "ok",
        "out":          out_path,
        "total_pages":  total_pages,
        "cover_pages":  cover_pages,
        "body_pages":   body_pages,
        "size_kb":      size_kb,
    }
    if warnings:
        report["warnings"] = warnings

    return report


def main():
    parser = argparse.ArgumentParser(description="Merge cover + body PDFs")
    parser.add_argument("--cover", required=True)
    parser.add_argument("--body",  required=True)
    parser.add_argument("--out",   required=True)
    parser.add_argument("--title", default="")
    args = parser.parse_args()

    try:
        require_file(args.cover)
        require_file(args.body)
        require_distinct_output(args.out, args.cover, args.body)
    except ValueError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        sys.exit(1)

    try:
        result = merge(args.cover, args.body, args.out, args.title)
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2 if isinstance(exc, DependencyError) else 3)

    print(json.dumps(result))

    # Human-readable QA summary
    print(f"\n── Build complete ──────────────────────────────────────")
    print(f"  Output  : {result['out']}")
    print(f"  Pages   : {result['total_pages']} total (1 cover + {result['body_pages']} body)")
    print(f"  Size    : {result['size_kb']} KB")
    if result.get("warnings"):
        print(f"  ⚠  Warnings:")
        for w in result["warnings"]:
            print(f"     • {w}")
    print(f"────────────────────────────────────────────────────────\n")


if __name__ == "__main__":
    main()
