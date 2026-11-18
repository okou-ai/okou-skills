#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Bounded, read-only XLSX/XLSM and delimited-text inspection; stdlib only.

Numbers are returned as their exact XML lexical strings, not binary floats or
formatted display text. Dates/IDs are not guessed: report formats and date system.
Worksheet dimensions are deliberately absent from inventory (no sheet is opened).
"""

import csv
import itertools
from pathlib import Path
import posixpath
import re
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
import zipfile
from xlsx_package import checked_members, safe_member

MAX_ROW, MAX_COLUMN, MAX_CELLS = 1048576, 16384, 10000
BUILTIN_FORMATS = {
    0: "General", 1: "0", 2: "0.00", 3: "#,##0", 4: "#,##0.00",
    9: "0%", 10: "0.00%", 11: "0.00E+00", 12: "# ?/?", 13: "# ??/??",
    14: "mm-dd-yy", 15: "d-mmm-yy", 16: "d-mmm", 17: "mmm-yy",
    18: "h:mm AM/PM", 19: "h:mm:ss AM/PM", 20: "h:mm", 21: "h:mm:ss",
    22: "m/d/yy h:mm", 37: "#,##0 ;(#,##0)", 38: "#,##0 ;[Red](#,##0)",
    39: "#,##0.00;(#,##0.00)", 40: "#,##0.00;[Red](#,##0.00)",
    45: "mm:ss", 46: "[h]:mm:ss", 47: "mmss.0", 48: "##0.0E+0", 49: "@",
}


def local(tag):
    return tag.rsplit("}", 1)[-1]


def child(element, name):
    return next((e for e in element if local(e.tag) == name), None)


def column_number(letters):
    number = 0
    for letter in letters.upper():
        number = number * 26 + ord(letter) - 64
    return number


def column_name(number):
    result = ""
    while number:
        number, remainder = divmod(number - 1, 26)
        result = chr(65 + remainder) + result
    return result


def address(value):
    match = re.fullmatch(r"\$?([A-Za-z]{1,3})\$?([1-9][0-9]*)", value or "")
    if not match:
        raise ValueError(f"Invalid Excel cell address: {value!r}")
    col, row = column_number(match[1]), int(match[2])
    if col > MAX_COLUMN or row > MAX_ROW:
        raise ValueError(f"Excel address outside worksheet limits: {value!r}")
    return row, col


def bounds(cell_range=None, rows=5, columns=12):
    if cell_range:
        ends = cell_range.split(":")
        if len(ends) not in (1, 2):
            raise ValueError("Use a bounded A1 or A1:C8 range, without a sheet prefix")
        top, left = address(ends[0])
        bottom, right = address(ends[-1])
    else:
        top, left, bottom, right = 1, 1, rows, columns
    if not (1 <= top <= bottom <= MAX_ROW and 1 <= left <= right <= MAX_COLUMN):
        raise ValueError("Invalid/reversed preview bounds")
    if (bottom - top + 1) * (right - left + 1) > MAX_CELLS:
        raise ValueError(f"Requested slice exceeds {MAX_CELLS} cells; request smaller ranges")
    return top, left, bottom, right


def target_part(source, target):
    parsed = urlsplit(target)
    if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment or "\\" in target:
        raise ValueError(f"Unsupported internal relationship target: {target!r}")
    decoded = unquote(parsed.path)
    path = posixpath.normpath(decoded.lstrip("/") if decoded.startswith("/") else
                              posixpath.join(posixpath.dirname(source), decoded))
    safe_member(path)
    return path


def relationships(package, source):
    relpath = (posixpath.join(posixpath.dirname(source), "_rels", posixpath.basename(source) + ".rels")
               if source else "_rels/.rels")
    root = ET.fromstring(package.read(relpath))
    result = {}
    for rel in root:
        ident = rel.get("Id")
        if not ident or ident in result:
            raise ValueError(f"Missing/duplicate relationship ID in {relpath}")
        result[ident] = {"type": rel.get("Type", "").rsplit("/", 1)[-1],
                         "external": rel.get("TargetMode") == "External",
                         "target": rel.get("Target", "")}
    return result


def workbook_info(package):
    roots = relationships(package, "")
    offices = [r for r in roots.values() if r["type"] == "officeDocument" and not r["external"]]
    if len(offices) != 1:
        raise ValueError("Expected one internal officeDocument relationship")
    workbook_part = target_part("", offices[0]["target"])
    root = ET.fromstring(package.read(workbook_part))
    if local(root.tag) != "workbook":
        raise ValueError("Related part is not an XML workbook")
    rels = relationships(package, workbook_part)
    props = child(root, "workbookPr")
    date_system = "1904" if props is not None and props.get("date1904") in ("1", "true") else "1900"
    sheets = []
    names = set()
    collection = child(root, "sheets")
    for sheet in collection if collection is not None else []:
        name = sheet.get("name")
        if not name or name in names:
            raise ValueError("Missing/duplicate sheet name")
        names.add(name)
        rid = next((v for k, v in sheet.attrib.items() if k.endswith("}id")), None)
        rel = rels.get(rid)
        if not rel or rel["external"]:
            raise ValueError(f"Missing/internal sheet relationship for {name!r}")
        part = target_part(workbook_part, rel["target"])
        if part not in package.namelist():
            raise ValueError(f"Missing sheet part {part}")
        sheets.append({"name": name, "sheet_id": sheet.get("sheetId"),
                       "state": sheet.get("state", "visible"), "kind": rel["type"], "part": part})
    return sheets, rels, workbook_part, date_system


def related_part(rels, source, kind):
    matches = [r for r in rels.values() if r["type"] == kind and not r["external"]]
    if len(matches) > 1:
        raise ValueError(f"Multiple {kind} relationships")
    return target_part(source, matches[0]["target"]) if matches else None


def style_formats(package, part):
    if not part:
        return []
    root = ET.fromstring(package.read(part))
    custom = child(root, "numFmts")
    formats = {int(e.get("numFmtId")): e.get("formatCode")
               for e in (custom if custom is not None else [])}
    xfs = child(root, "cellXfs")
    result = []
    for xf in xfs if xfs is not None else []:
        number = int(xf.get("numFmtId", "0"))
        result.append({"num_fmt_id": number,
                       "number_format": formats.get(number, BUILTIN_FORMATS.get(number)),
                       "format_known": number in formats or number in BUILTIN_FORMATS})
    return result


def rich_text(element):
    """Join actual text/runs, not phonetic annotation rPh/t content."""
    if element is None:
        return ""
    return "".join((e.text or "") if local(e.tag) == "t" else
                   "".join(t.text or "" for t in e if local(t.tag) == "t")
                   for e in element if local(e.tag) in ("t", "r"))


def shared_values(package, part, wanted):
    if not wanted or not part:
        return {}
    result, index = {}, 0
    with package.open(part) as stream:
        context = ET.iterparse(stream, events=("start", "end"))
        _, root = next(context)
        for event, item in context:
            if event == "end" and local(item.tag) == "si":
                if index in wanted:
                    result[index] = rich_text(item)
                index += 1
                root.clear()
                if wanted <= result.keys():
                    break
    return result


def read_sheet(package, sheet, box, formats):
    top, left, bottom, right = box
    cells, last_row, inferred_column, row_number = [], 0, 0, 0
    with package.open(sheet["part"]) as stream:
        stack = []
        for event, item in ET.iterparse(stream, events=("start", "end")):
            tag = local(item.tag)
            if event == "start":
                stack.append(item)
                if tag == "row":
                    row_number = int(item.get("r", last_row + 1))
                    if row_number <= last_row or row_number > MAX_ROW:
                        raise ValueError("Rows must have increasing Excel addresses")
                    if row_number > bottom:
                        break  # do not parse any cells from subsequent rows
                    last_row, inferred_column = row_number, 0
                continue
            if tag == "c":
                ref = item.get("r")
                r, col = address(ref) if ref else (row_number, inferred_column + 1)
                if r != row_number or col <= inferred_column or col > MAX_COLUMN:
                    raise ValueError("Cell addresses must agree with their row and increase")
                inferred_column = col
                if top <= r <= bottom and left <= col <= right:
                    val, formula = child(item, "v"), child(item, "f")
                    raw = val.text if val is not None else None
                    kind = item.get("t", "n")
                    style = int(item.get("s", "0"))
                    cell = {"address": f"{column_name(col)}{r}", "row": r, "column": col,
                            "type": kind, "raw_value": raw, "value": None, "style_index": style,
                            "style_origin": "cell" if "s" in item.attrib else "default (inheritance not resolved)"}
                    if formats and 0 <= style < len(formats):
                        cell.update(formats[style])
                    elif style != 0:
                        cell["warning"] = "Unknown style index; number format not interpreted"
                    if formula is not None:
                        cell["formula"] = formula.text
                        cell["formula_attributes"] = dict(formula.attrib)
                        cell["cache_status"] = ("missing" if val is None else "blank" if raw is None or raw == "" else "present")
                    if kind == "inlineStr" and formula is None:
                        cell["value"] = rich_text(child(item, "is"))
                    elif kind == "b" and raw in ("0", "1"):
                        cell["value"] = raw == "1"
                    elif kind in ("n", "s", "str", "e", "d"):
                        cell["value"] = raw  # exact lexical number/date, no guessed conversion
                    elif raw is not None:
                        cell["warning"] = "Unsupported cell type/value; raw_value retained, not decoded"
                    if kind == "s" and raw is not None:
                        try:
                            index = int(raw)
                            if index < 0:
                                raise ValueError()
                            cell["shared_string_index"] = index
                            cell["value"] = None
                        except ValueError:
                            cell["value"] = None
                            cell["warning"] = "Invalid shared-string index"
                    if formula is not None and cell["cache_status"] != "present":
                        cell["value"] = None
                    cells.append(cell)
                item.clear()
                if r == bottom and col >= right:
                    break  # final requested row/column reached; ignore remaining cells
            if tag in ("row", "sheetData"):
                item.clear()
                if len(stack) > 1:
                    stack[-2].remove(item)
                if tag == "row" and row_number == bottom:
                    break
            stack.pop()
    return cells


def csv_preview(path, box, encoding=None):
    top, left, bottom, right = box
    encodings = [encoding] if encoding else ["utf-8-sig", "gbk", "latin-1"]
    last_error = None
    for enc in encodings:
        try:
            cells = []
            with path.open("r", encoding=enc, newline="") as stream:
                reader = csv.reader(stream, delimiter="\t" if path.suffix.lower() == ".tsv" else ",", strict=True)
                for row_number, row in enumerate(itertools.islice(reader, bottom), 1):
                    if row_number < top:
                        continue
                    for col, value in enumerate(row[left - 1:right], left):
                        cells.append({"address": f"{column_name(col)}{row_number}", "row": row_number,
                                      "column": col, "type": "text", "value": value})
            return cells, enc
        except UnicodeDecodeError as exc:
            last_error = exc  # never retry parser errors, permissions, missing files, etc.
    raise ValueError(f"Cannot decode {path}; tried {encodings}: {last_error}")


def inspect_file(filename, sheet_name=None, inventory=False, cell_range=None, rows=5, columns=12, encoding=None):
    path = Path(filename)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {filename}")
    suffix = path.suffix.lower()
    box = bounds(cell_range, rows, columns)
    result = {"file": str(filename), "mode": "inventory" if inventory else "preview", "sheets": [], "previews": {}}
    if suffix in (".csv", ".tsv"):
        if sheet_name and sheet_name != path.stem:
            raise ValueError(f"Unknown sheet: {sheet_name!r}; CSV/TSV sheet is {path.stem!r}")
        result["sheets"] = [{"name": path.stem, "kind": "delimited_text", "rows": None, "columns": None}]
        if not inventory:
            cells, selected_encoding = csv_preview(path, box, encoding)
            result["encoding"] = selected_encoding
            result["previews"][path.stem] = {"cells": cells, "bounds": box}
    elif suffix in (".xlsx", ".xlsm"):
        with zipfile.ZipFile(path) as package:
            checked_members(package)
            sheets, rels, workbook, date_system = workbook_info(package)
            selected = [s for s in sheets if s["name"] == sheet_name] if sheet_name else sheets
            if sheet_name and not selected:
                raise ValueError(f"Unknown sheet: {sheet_name!r}")
            result["sheets"], result["date_system"] = selected, date_system
            if not inventory:
                worksheets = [s for s in selected if s["kind"] == "worksheet"]
                if not worksheets:
                    raise ValueError("Selection contains no XML worksheet")
                selected_sheet = worksheets[0]  # default is bounded first-sheet preview, not every sheet
                formats = style_formats(package, related_part(rels, workbook, "styles"))
                cells = read_sheet(package, selected_sheet, box, formats)
                wanted = {c["shared_string_index"] for c in cells if "shared_string_index" in c}
                strings = shared_values(package, related_part(rels, workbook, "sharedStrings"), wanted)
                for cell in cells:
                    if "shared_string_index" in cell:
                        index = cell["shared_string_index"]
                        if index in strings:
                            cell["value"] = strings[index]
                        else:
                            cell["warning"] = "Missing shared string; value unknown"
                result["previews"][selected_sheet["name"]] = {"cells": cells, "bounds": box}
    else:
        raise ValueError(f"Unsupported format {suffix!r}; use XLSX/XLSM/CSV/TSV (not binary XLS)")
    result["limitations"] = ["Read-only slice, not a full row count or quality audit; no macros, save or recalculation.",
                              "Numeric/date XML values are exact lexical strings plus number-format metadata, not rendered display values.",
                              "Absent cells are omitted; absent/blank formula caches are unknown, never zero.",
                              "Style metadata does not resolve row/column inheritance, conditional formatting or locale-dependent display."]
    return result
