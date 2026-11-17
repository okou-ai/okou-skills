# Edit, fill, or repair an existing workbook

Use for any change to an existing file, including template filling, formula
repair and formatting. Keep the source intact and work on a separate copy.
Preserve unrelated content and features; never create a replacement workbook
just to perform a narrow edit.

## 1. Inspect and identify the change

```bash
python3 "$SKILL_DIR/scripts/xlsx_reader.py" input.xlsx --inventory --json
python3 "$SKILL_DIR/scripts/xlsx_reader.py" input.xlsx --sheet Sales --range B3:D8 --json
```

Start with metadata and the relevant cells, not a full workbook analysis or
unpack. Resolve named tabs through workbook relationships (including the root
workbook relationship); `sheet1.xml` need not be the first named tab. Locate a
target row by its label, not an unverified row number. Identify formulas,
styles, shared/inline strings, named ranges, merged cells, controls, data
validation, conditional formatting, tables, charts and external dependencies
that may be affected.

Use targeted XML edits rather than a default general-library load/save round-trip
for feature-rich files: that can discard unsupported parts. For small edits,
extract only the identified part(s), edit them, then use `xlsx_pack.py --base/--part`
below. Unchanged local ZIP records, content and member metadata are copied without
XML reserialization; central-directory offsets necessarily change. Changed XML
and invalidated digital signatures still need review. Preserve XLSM file type/VBA;
never execute macros as part of inspection.

For broader changes the old directory workflow remains available:

```bash
python3 "$SKILL_DIR/scripts/xlsx_unpack.py" input.xlsx /tmp/new-xlsx-work
```

Use a new directory; existing targets are refused, not deleted. Default unpacking
retains raw part bytes. `--pretty` is an explicit readability transform that may
change every XML/rels part; do not use it as the small-edit preservation path.

## 2. Make the smallest correct edit

| Requested change | Edit |
| --- | --- |
| Numeric input | Change the target cell's value; preserve its style and correct data type |
| Text | Change that inline string, or append a shared string and update only the target cell's index |
| Formula | Change `<f>` without a leading `=`; clear the stale cached `<v>` and any stale error marker |
| Formatting | Reuse/append a style and assign it only to the intended range; do not change values or formulas |
| Sheet rename | Preserve its ID/part, and update affected formulas, defined names, chart references and other dependencies |
| Row/column change | Use the helpers when applicable, then review all dependent ranges below |

Never reorder/delete existing shared strings or style definitions. Shared
string usage counts are not the same as unique-entry counts. Formula cells
can have legitimate text/boolean result types; preserve the correct result
type rather than blindly removing every `t` attribute.

Read the OOXML reference when changing cell types, string indices or style
components. For template filling, change only designated inputs; keep formulas,
layout, existing conventions and the file type. Do not infer an input solely
because a cell is blank or colored. For authorized input changes, check the
[data/input contract](../common/data-and-inputs.md) without adding unrelated
restrictions or rebuilding the file.

## 3. Review structural dependencies

For row/column insertions, deletions or sheet renames, inspect all affected:

- Cell addresses, formulas on every sheet, and shared/array formula ranges.
- Defined names, print areas, merged ranges and worksheet dimensions.
- Tables, filters, conditional formats, validation and control-linked cells.
- Chart series, pivot/cache sources, external links and connections.

Prefer appending to inserting where the task allows it. Locate rows by their
actual labels before choosing a row number. `xlsx_add_column.py --help` lists
column, formula, number-format and full-row-border options; inspect the styles
it copies before applying a finance convention.

The current `xlsx_insert_row.py` invokes `xlsx_shift_rows.py` **across every
worksheet** before inserting into `--sheet`. Do not use it as a sheet-local
insert in a multi-sheet workbook, or run a separate shift first. Use it only
when that global shift matches the task; otherwise make a scoped, feature-aware
edit. The shift helper's delete mode is not a complete row-deletion operation.
Helper coverage is incomplete: review names, structured references, external
links and other features yourself. Do not delete referenced ranges without
resolving their dependents.

Keep VBA binaries, slicers, embedded objects, external-link binaries and
unrelated parts intact. Changes to coupled pivot/cache structures or live data
connections require feature-aware handling, not blind search-and-replace.
Do not recalculate/save an advanced workbook through another application
without first checking preservation on a disposable copy.

## 4. Repair formulas without hiding the problem

Use `formula_check.py` and the actual source/model intent to locate a defect.
Correct an unambiguous reference, type or name error; do not guess business
logic. A missing lookup or zero denominator is not automatically a valid zero.
Do not blanket-wrap formulas in `IFERROR(...,0)` to make checks look clean.
Use a fallback only when its meaning is appropriate and documented.

After changing a formula, clear stale cached results and recheck its entire
dependent/shared range. Preserve valid formulas elsewhere.

## 5. Package only the change, then check by impact

For a small edit, first copy the selected original XML part to a temporary file
using ZIP read APIs (the part name must come from verified relationships), edit
that copy, and replace just the coupled parts:

```bash
python3 "$SKILL_DIR/scripts/xlsx_pack.py" --base input.xlsx \
  --part xl/worksheets/sales.xml=/tmp/sales-edited.xml output.xlsx
# Repeat --part for required sharedStrings/styles/relationship changes.
# Legacy broader-directory mode:
python3 "$SKILL_DIR/scripts/xlsx_pack.py" /tmp/new-xlsx-work output-from-directory.xlsx
```

`--part` replaces existing XML/rels members only; it is not an insert/delete helper
or dependency repairer. Both pack modes refuse existing outputs, source traversal,
symlinks and duplicate/unsafe member paths. Validate replacements before publishing;
malformed XML never overwrites a target. Directory mode validates all XML but cannot
recover original ZIP metadata; scoped mode retains untouched member records.

Use the shared [VALIDATE impact matrix](validate.md#1-select-checks-by-impact), not
an automatic recalc/mutation/export sequence. Verify exact changed values/types,
related dependencies and untouched features against the source. Formula/model-input
changes need actual fresh calculation and final formula/cache readback; a verified
independent nonformula edit does not. Layout impact needs the affected actual view
**or** export; pagination needs export. Structural changes still require section 3's
full affected-dependency review. Resolve unintended changes before delivery; a
successful pack or a clean cached-error scan alone is not preservation proof.
