#!/usr/bin/env python3
"""
fill_inspect.py — Inspect form fields in an existing PDF.

Usage:
    python3 fill_inspect.py --input form.pdf
    python3 fill_inspect.py --input form.pdf --out fields.json

Outputs a JSON summary of every fillable field: name, type, current value,
allowed values (for checkboxes / dropdowns), and page number.

Exit codes: 0 success, 1 bad args / file not found, 2 dep missing, 3 read error
"""

import argparse
import json
import sys
from pdf_runtime import DependencyError, require_dependency, require_distinct_output, require_file


# ── Field type resolution ──────────────────────────────────────────────────────
def _field_type(field) -> str:
    ft = field.get("/FT")
    if ft is None:
        return "unknown"
    ft = str(ft)
    if ft == "/Tx":
        return "text"
    if ft == "/Btn":
        ff = int(field.get("/Ff", 0))
        return "radio" if ff & (1 << 15) else "checkbox"
    if ft == "/Ch":
        ff = int(field.get("/Ff", 0))
        return "dropdown" if ff & (1 << 17) else "listbox"
    if ft == "/Sig":
        return "signature"
    return "unknown"


def _field_value(field) -> str | None:
    v = field.get("/V")
    return str(v) if v is not None else None


def _field_options(field, ftype: str) -> dict:
    extra = {}
    if ftype in ("checkbox",):
        ap = field.get("/AP")
        if ap:
            ap = ap.get_object()
        if ap and "/N" in ap:
            states = [str(k) for k in ap["/N"]]
            extra["states"] = states
            checked = next((s for s in states if s != "/Off"), None)
            if checked:
                extra["checked_value"] = checked
    if ftype in ("dropdown", "listbox"):
        opt = field.get("/Opt")
        if opt:
            choices = []
            for item in opt:
                if isinstance(item, list) and len(item) >= 2:
                    choices.append({"value": str(item[0]), "label": str(item[1])})
                else:
                    choices.append({"value": str(item), "label": str(item)})
            extra["choices"] = choices
    if ftype == "radio":
        kids = field.get("/Kids")
        if kids:
            values = []
            for kid in kids:
                ap = kid.get_object().get("/AP")
                if ap:
                    ap = ap.get_object()
                if ap and "/N" in ap:
                    for k in ap["/N"]:
                        if str(k) != "/Off":
                            values.append(str(k))
            extra["radio_values"] = values
    return extra


def _walk_fields(fields, page_map: dict, parent_name: str = "") -> list:
    """Recursively collect all leaf fields."""
    result = []
    for field in fields:
        field = field.get_object()
        name = str(field.get("/T", ""))
        full = f"{parent_name}.{name}" if parent_name else name

        kids = field.get("/Kids")
        # Kids that have /T are sub-fields (groups), not widget annotations
        if kids:
            named_kids = [k for k in kids if "/T" in k.get_object()]
            if named_kids:
                result.extend(_walk_fields(named_kids, page_map, full))
                continue

        ftype = _field_type(field)
        if ftype == "unknown":
            continue

        entry = {
            "name":  full,
            "type":  ftype,
            "value": _field_value(field),
        }
        entry.update(_field_options(field, ftype))

        # Page lookup via /P indirect reference
        p_ref = field.get("/P")
        if p_ref and hasattr(p_ref, "idnum"):
            entry["page"] = page_map.get(p_ref.idnum, "?")

        result.append(entry)
    return result


def inspect(pdf_path: str) -> dict:
    require_file(pdf_path, (".pdf",))
    PdfReader = require_dependency("pypdf").PdfReader
    try:
        reader = PdfReader(pdf_path)
    except Exception as e:
        return {"status": "error", "error": str(e)}

    # Build page-number lookup: {object_id: 1-based page number}
    page_map = {}
    for i, page in enumerate(reader.pages):
        if hasattr(page, "indirect_reference") and page.indirect_reference:
            page_map[page.indirect_reference.idnum] = i + 1

    acroform = reader.trailer["/Root"].get("/AcroForm")
    if acroform is not None:
        acroform = acroform.get_object()
    if acroform is None or "/Fields" not in acroform:
        return {
            "status":     "ok",
            "has_fields": False,
            "field_count": 0,
            "fields":     [],
            "note":       "This PDF has no fillable form fields.",
        }

    fields = _walk_fields(list(acroform["/Fields"]), page_map)

    return {
        "status":      "ok",
        "has_fields":  bool(fields),
        "field_count": len(fields),
        "fields":      fields,
    }


def main():
    parser = argparse.ArgumentParser(description="Inspect PDF form fields")
    parser.add_argument("--input", required=True, help="PDF file to inspect")
    parser.add_argument("--out",   default="",    help="Write JSON to file (optional)")
    args = parser.parse_args()

    try:
        require_file(args.input, (".pdf",))
        if args.out:
            require_distinct_output(args.out, args.input)
    except ValueError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        sys.exit(1)

    try:
        result = inspect(args.input)
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        sys.exit(2 if isinstance(exc, DependencyError) else 3)
    if result["status"] != "ok":
        print(json.dumps(result), file=sys.stderr)
        sys.exit(3)

    output = json.dumps(result, indent=2, ensure_ascii=False)

    if args.out:
        with open(args.out, "w") as f:
            f.write(output)

    print(output)

    # Human-readable summary
    if result["status"] == "ok" and result["has_fields"]:
        print(f"\n── Fields in {args.input} ──────────────────────────────",
              file=sys.stderr)
        for f in result["fields"]:
            pg  = f"  p.{f['page']}" if "page" in f else ""
            val = f"  = {f['value']}" if f.get("value") else ""
            extra = ""
            if "choices" in f:
                extra = f"  [{', '.join(c['value'] for c in f['choices'][:4])}{'…' if len(f['choices'])>4 else ''}]"
            elif "states" in f:
                extra = f"  {f['states']}"
            print(f"  {f['type']:12}  {f['name']}{pg}{val}{extra}", file=sys.stderr)
        print("", file=sys.stderr)


if __name__ == "__main__":
    main()
