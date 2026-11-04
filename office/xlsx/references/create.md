# Create a new XLSX

Use for a new workbook, not for filling or changing an existing file. Select
business scenario and common presentation first. Keep derived outputs as live
formulas. Follow this order: [plan](#1-plan), [prepare](#2-choose-and-check-the-tools),
[build](#3-build-in-business-objects), [check](#4-calculate-view-and-revise),
[raw package fallback](#raw-ooxml-path).

## 1. Plan

Plan around the user's reading and editing tasks. Define each worksheet or
section's purpose and order, the source and input locations, and how calculations
feed the reported results. Prioritize completeness and readability over reducing
the sheet count; give data and explanations enough space to be inspected. Use
the finance layer for the structure of budgets, forecasts and financial reports.
Keep the work within the requested scope.

## 2. Choose and check the tools

Prefer a maintained high-level workbook library, such as openpyxl, when it can
express the planned new file. Use workbook/cell/range/style/chart objects instead
of manually maintaining package relationships and numeric style indices. Reuse
an installed suitable tool; another library or the raw OOXML path is valid when
needed. Do not rebuild existing files through a library that may drop features.

For the optional Python path, check imports in the chosen interpreter. Reuse a
working virtual environment; install only missing dependencies when setup is
allowed. If no suitable environment exists, an isolated example is:

```bash
AUTHOR_ENV=$(mktemp -d /tmp/xlsx-authoring.XXXXXX)
python3 -m venv "$AUTHOR_ENV"
. "$AUTHOR_ENV/bin/activate"
python -m pip install -r "$SKILL_DIR/requirements-authoring.txt"
```

Before substantial formula authoring, read VALIDATE's application section and run:

```bash
python3 "$SKILL_DIR/scripts/libreoffice_recalc.py" --preflight
```

This tests an independent formula control, not the candidate. A working binary
or version string is insufficient. Diagnose a failed control before blaming a
workbook; repair permitted missing components, then rerun the control. If setup
or application use is forbidden/unavailable, record that limitation and do not
present uncalculated output as a ready-to-use model.

## 3. Build in business objects

- Populate values/formulas, then assign both semantic role and display format:
  amount, percentage, date or integer. A ratio formula needs a percentage format;
  a valid formula alone does not determine its appearance.
- Store numeric inputs as numbers, rates as decimals and actual dates with date
  formats. Use library string APIs and named-range/worksheet references; do not
  invent string, style or relationship indices.
- Make headings span the planned content width, not just a narrow label column.
  Set column widths and sufficient row heights for explanations; `wrap_text`
  alone does not provide a fitted layout. Keep gaps outside data tables.
- Set a report area and usable page width, leaving long reports free to continue
  vertically. Keep source tables separate from reader-facing print layouts.

For new financial layouts using the selected defaults, read
[high-level primitives](authoring.md). Its optional `xlsx_authoring.py` functions
assign explicit cell roles/formats, full-width bands, gray label headers and
report-page settings. They are building blocks, not a financial model template,
formula evaluator or automatic layout/quality checker. Supplied styles override
them; do not call financial styling helpers for ordinary non-financial tables.

## 4. Calculate, view and revise

Save a first complete draft early. Use VALIDATE to recalculate a copy, compare
source-based expected results and change relevant inputs. Export the relevant
sheets and inspect the actual pages; fix clipped headings, cramped notes, split
columns or chart overlaps, then repeat affected checks. Resolve defects inside
this authoring attempt rather than returning an unchecked first draft.

Select the final delivery file only after checking conversion effects and live
formulas. Reopen that exact file with formula and cached-value views. Saving an
openpyxl workbook again after Calc recalculation can clear its caches: recalculate
and recheck after any later save. Never synthesize cached answers to bypass this.
Deliver only the requested file; working scripts, images and checks are not
mandatory extra user attachments.

## Raw OOXML path

Use when package-level control is needed or a suitable library is unavailable.
Read [OOXML details](ooxml-cheatsheet.md), then use a fresh working directory:

```bash
cp -R "$SKILL_DIR/templates/minimal_xlsx" /tmp/xlsx_work
python3 "$SKILL_DIR/scripts/xlsx_pack.py" /tmp/xlsx_work output.xlsx
```

Edit the copied package before packing. Its initial sheet count is not a layout
recommendation; expand it to match the plan. Adding a sheet requires consistent
entries in `workbook.xml`, its relationships, `[Content_Types].xml`, and the
worksheet part. In the starter `rId1` is the sheet, `rId2` styles and `rId3` shared
strings; select an unused relationship ID. Quote sheet names with spaces.

Use `<f>` without a leading `=`, numeric `<v>` for numbers, and inline/shared
strings for text. Use `shared_strings_builder.py --help` for shared-string counts.
Keep valid worksheet element order and workbook-local style references. Empty
or placeholder formula caches are not successful calculation. Packing checks XML
well-formedness, not full schema, application behavior or presentation; continue
with the same VALIDATE workflow, not a weaker raw-package acceptance path.
