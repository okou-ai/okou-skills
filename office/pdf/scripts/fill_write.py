#!/usr/bin/env python3
"""
fill_write.py — Write values into PDF form fields.

Usage:
    # From a JSON data file
    python3 fill_write.py --input form.pdf --data values.json --out filled.pdf

    # Inline JSON
    python3 fill_write.py --input form.pdf --out filled.pdf \
        --values '{"FirstName": "Jane", "Agree": "true"}'

values format:
    {
      "FieldName":  "text value",          # text field
      "CheckBox1":  "true",                # checkbox  (true / false)
      "Dropdown1":  "OptionValue",         # dropdown  (must match an existing choice value)
      "Radio1":     "/Choice2"             # radio     (must match a radio value)
    }

Exit codes: 0 success, 1 bad args, 2 dep missing, 3 read/write error, 4 validation error
"""

import argparse
import json
import os
import sys
import tempfile

from pdf_runtime import DependencyError, require_dependency, require_distinct_output, require_file


# ── Field helpers ─────────────────────────────────────────────────────────────
def _field_type(field) -> str:
    ft = str(field.get("/FT", ""))
    if ft == "/Tx":  return "text"
    if ft == "/Btn":
        ff = int(field.get("/Ff", 0))
        return "radio" if ff & (1 << 15) else "checkbox"
    if ft == "/Ch":
        ff = int(field.get("/Ff", 0))
        return "dropdown" if ff & (1 << 17) else "listbox"
    return "unknown"


def _get_checkbox_on_value(field) -> str:
    """Return the /AP /N key that means 'checked' (anything except /Off)."""
    ap = field.get("/AP")
    if ap:
        ap = ap.get_object()
    if ap and "/N" in ap:
        for k in ap["/N"]:
            if str(k) != "/Off":
                return str(k)
    return "/Yes"


def _get_dropdown_values(field) -> list[str]:
    opt = field.get("/Opt")
    if not opt:
        return []
    values = []
    for item in opt:
        if isinstance(item, list) and len(item) >= 1:
            values.append(str(item[0]))
        else:
            values.append(str(item))
    return values


# ── Walk + fill ───────────────────────────────────────────────────────────────
def _walk_and_fill(fields, data: dict, filled: list, errors: list, parent: str = ""):
    from pypdf.generic import NameObject, TextStringObject

    for field in fields:
        field = field.get_object()
        name = str(field.get("/T", ""))
        full = f"{parent}.{name}" if parent else name

        # Recurse into named groups
        kids = field.get("/Kids")
        if kids:
            named = [k for k in kids if "/T" in k.get_object()]
            if named:
                _walk_and_fill(named, data, filled, errors, full)
                continue

        if full not in data:
            continue

        value   = data[full]
        ftype   = _field_type(field)

        if ftype == "text":
            field.update({
                NameObject("/V"):  TextStringObject(str(value)),
                NameObject("/DV"): TextStringObject(str(value)),
            })
            filled.append(full)

        elif ftype == "checkbox":
            normalized = str(value).lower()
            if normalized not in ("true", "1", "yes", "on", "false", "0", "no", "off"):
                errors.append({"field": full, "error": "Checkbox requires true or false"})
                continue
            truthy = normalized in ("true", "1", "yes", "on")
            on_val = _get_checkbox_on_value(field)
            pdf_val = on_val if truthy else "/Off"
            field.update({
                NameObject("/V"):  NameObject(pdf_val),
                NameObject("/AS"): NameObject(pdf_val),
            })
            filled.append(full)

        elif ftype in ("dropdown", "listbox"):
            allowed = _get_dropdown_values(field)
            if allowed and str(value) not in allowed:
                errors.append({
                    "field": full,
                    "error": f"Value '{value}' not in allowed choices: {allowed}"
                })
                continue
            field.update({NameObject("/V"): TextStringObject(str(value))})
            filled.append(full)

        elif ftype == "radio":
            # Radio value must start with /
            pdf_val = str(value) if str(value).startswith("/") else f"/{value}"
            widgets = [kid.get_object() for kid in kids] if kids else [field]
            allowed = set()
            for widget in widgets:
                appearance = widget.get("/AP")
                if appearance:
                    allowed.update(str(key) for key in appearance.get_object().get("/N", {}) if str(key) != "/Off")
            if not allowed or pdf_val not in allowed:
                errors.append({"field": full, "error": f"Radio value must match one of: {sorted(allowed)}"})
                continue
            for widget in widgets:
                appearance = widget.get("/AP")
                states = appearance.get_object().get("/N", {}) if appearance else {}
                widget.update({NameObject("/AS"): NameObject(pdf_val if pdf_val in states else "/Off")})
            field.update({
                NameObject("/V"):  NameObject(pdf_val),
                NameObject("/AS"): NameObject(pdf_val),
            })
            filled.append(full)

        else:
            errors.append({"field": full, "error": f"Unsupported field type: {ftype}"})


def fill(pdf_path: str, out_path: str, data: dict) -> dict:
    require_file(pdf_path, (".pdf",))
    require_distinct_output(out_path, pdf_path)
    if not isinstance(data, dict) or not data:
        raise ValueError("Field values must be a nonempty JSON object")
    pypdf = require_dependency("pypdf")
    from pypdf.generic import NameObject, BooleanObject

    PdfReader, PdfWriter = pypdf.PdfReader, pypdf.PdfWriter
    try:
        reader = PdfReader(pdf_path)
    except Exception as e:
        return {"status": "error", "error": str(e)}

    writer = PdfWriter()
    writer.clone_document_from_reader(reader)

    acroform = writer._root_object.get("/AcroForm")  # type: ignore[attr-defined]
    if acroform is not None:
        acroform = acroform.get_object()
    if acroform is None or "/Fields" not in acroform:
        return {
            "status": "error",
            "error":  "This PDF has no fillable form fields.",
            "hint":   "Run fill_inspect.py first to confirm the PDF has fields.",
        }

    # Enable appearance regeneration so viewers show the new values
    acroform.update({NameObject("/NeedAppearances"): BooleanObject(True)})

    filled: list[str] = []
    errors: list[dict] = []
    _walk_and_fill(list(acroform["/Fields"]), data, filled, errors)

    # Warn about requested fields that were never found
    not_found = [k for k in data if k not in filled and not any(e["field"] == k for e in errors)]

    if errors or not_found:
        return {"status": "error", "error": "Requested fields did not validate; output unchanged",
                "validation_errors": errors, "not_found": not_found, "exit_code": 4}

    directory = os.path.dirname(os.path.abspath(out_path))
    os.makedirs(directory, exist_ok=True)
    candidate = tempfile.NamedTemporaryFile(dir=directory, prefix=".pdf-fill-", suffix=".tmp", delete=False)
    try:
        with candidate:
            writer.write(candidate)
        reopened = PdfReader(candidate.name)
        if len(reopened.pages) != len(reader.pages):
            raise ValueError("Filled PDF page count changed")
        actual = reopened.get_fields() or {}
        expected = writer.get_fields() or {}
        for name in data:
            if name not in actual or str(actual[name].get("/V")) != str(expected[name].get("/V")):
                raise ValueError(f"Stored value did not verify for field: {name}")
        os.replace(candidate.name, out_path)
    except Exception as e:
        return {"status": "error", "error": f"Write/verification failed: {e}"}
    finally:
        if os.path.exists(candidate.name):
            os.remove(candidate.name)

    result = {
        "status":        "ok",
        "out":           out_path,
        "filled_count":  len(filled),
        "filled_fields": filled,
        "size_kb":       os.path.getsize(out_path) // 1024,
    }
    if errors:
        result["validation_errors"] = errors
    if not_found:
        result["not_found"] = not_found
        result["hint"] = "Run fill_inspect.py to see all available field names."
    return result


def main():
    parser = argparse.ArgumentParser(description="Fill PDF form fields")
    parser.add_argument("--input",  required=True, help="Input PDF with form fields")
    parser.add_argument("--out",    required=True, help="Output PDF path")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--data",   help="Path to JSON file with field values")
    group.add_argument("--values", help="Inline JSON string with field values")
    args = parser.parse_args()

    try:
        require_file(args.input, (".pdf",))
        require_distinct_output(args.out, args.input)
        if args.data:
            require_file(args.data, (".json",))
    except ValueError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        sys.exit(1)

    # Load data before loading any PDF dependencies.
    try:
        if args.data:
            with open(args.data) as f:
                data = json.load(f)
        else:
            data = json.loads(args.values)
        if not isinstance(data, dict) or not data:
            raise ValueError("Field values must be a nonempty JSON object")
    except Exception as e:
        print(json.dumps({"status": "error", "error": f"JSON parse error: {e}"}),
              file=sys.stderr)
        sys.exit(1)

    try:
        result = fill(args.input, args.out, data)
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr)
        sys.exit(2 if isinstance(exc, DependencyError) else 3)
    print(json.dumps(result, indent=2, ensure_ascii=False))

    if result["status"] == "ok":
        print(f"\n── Fill complete ───────────────────────────────────────",
              file=sys.stderr)
        print(f"  Output : {result['out']}", file=sys.stderr)
        print(f"  Filled : {result['filled_count']} field(s)", file=sys.stderr)
        if result.get("validation_errors"):
            print(f"  Errors :", file=sys.stderr)
            for e in result["validation_errors"]:
                print(f"    • {e['field']}: {e['error']}", file=sys.stderr)
        if result.get("not_found"):
            print(f"  Not found: {result['not_found']}", file=sys.stderr)
        print("", file=sys.stderr)
    else:
        sys.exit(result.get("exit_code", 3))


if __name__ == "__main__":
    main()
