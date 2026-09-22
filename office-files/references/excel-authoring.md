# Excel authoring

Use this page to create or edit `.xlsx` workbooks.

## 1. Install

```bash
python3 -m pip install --break-system-packages --quiet openpyxl==3.1.5 lxml==6.1.3
sudo apt-get update
sudo apt-get install -y libreoffice-calc
```

Calc is required for formula workbooks. `libreoffice-writer` alone cannot load
and recalculate XLSX; its `source file could not be loaded` message does not prove
the workbook is corrupt. Set `OFFICE_FILES_DIR` to this `office-files` directory.

## 2. Create or edit

Create the workbook with openpyxl. For an existing workbook, work on a copy,
load it with `load_workbook(..., data_only=False)` to keep formulas, and save
to a new output file. Preserve unrelated sheets, formulas and formatting.

`insert_rows()` / `delete_rows()` do **not** maintain all dependent references.
After changing rows, columns or sheets, explicitly update affected totals,
cross-sheet formulas, table boundaries, chart source ranges and defined names.
For example, inserting a month before `Data!B4` moves the total to `B5`, but a
summary formula `=Data!B4` can remain pointed at the new month's 380 instead of
the total 3428. A valid formula string is not proof of a correct calculation.

Before editing advanced workbooks, inventory features such as pivots, macros,
external links and embedded objects. openpyxl and Calc may discard or rewrite
unsupported features. Use a compatible native workflow when preservation is
required; do not deliver a recalculated replacement without checking it.

## 3. Check

### Independent expectations

For both creation and editing, derive expected key values independently from
the raw data, such as a Python sum of the input CSV/JSON. Do not copy workbook
caches or repeat its formulas to manufacture the expected results. Cover every
requested or affected key total, subtotal, ratio and cross-sheet indicator;
one unrelated passing cell does not cover the rest of the workbook.

Save `generated/workbook-expectations.json`, for example:

```json
{
  "calculation_basis": "Sum quantities from raw-data.json in Python: 3000 + 48 + 380 = 3428; independent of workbook formulas.",
  "range_review": "Added month 3 in Data row 4. Checked total B5 sums B2:B4; Summary B2 targets Data!B5; Sales table extends through row 4. Reviewed chart series and defined names against those data rows.",
  "cells": [
    {"sheet": "Data", "cell": "B5", "value": 3428},
    {"sheet": "Summary", "cell": "B2", "value": 3428, "abs_tol": 0}
  ],
  "tables": [
    {"sheet": "Data", "name": "Sales", "ref": "A1:B4"}
  ]
}
```

Replace the example with the actual data and checks. `cells` must be nonempty,
including for a workbook without formulas. Values may be strings, numbers,
booleans or null; numeric comparisons use `abs_tol` / `rel_tol`, both zero by
default. State tolerances appropriate to the calculation. `tables` is optional;
include affected structured tables with their intended ranges. `range_review`
must record the actual changed ranges and dependent references reviewed. For a
new workbook, review its initial references; if no references exist, say so.

### Fresh recalculation and checks

```bash
python3 "$OFFICE_FILES_DIR/scripts/check_workbook.py" verify \
  --input generated/workbook.xlsx \
  --expectations generated/workbook-expectations.json \
  --data generated/raw-data.json \
  --resource generated/author_workbook.py \
  --resource generated/build_expectations.py \
  --out generated/workbook-qa
```

Use real existing file paths; repeat `--data` for the raw inputs and `--resource`
for authoring/expectation scripts or other dependencies. For edits, also bind
the original workbook with `--resource`. Formula workbooks require declared raw
data and at least one expected formula result. This minimum prevents empty
checks; the author remains responsible for covering all key results.

The QA directory must not exist. The checker creates a separate calculation
copy, removes old formula caches, requests automatic full recalculation, and
runs Calc with a private profile and a fresh output directory. The underlying
command, with actual absolute paths recorded in `verification.json`, is:

```bash
soffice -env:UserInstallation=file:///absolute/new-qa/libreoffice-profile \
  --headless --convert-to 'xlsx:Calc MS Excel 2007 XML' \
  --outdir /absolute/new-qa/recalculated \
  /absolute/new-qa/recalculation-input/workbook.xlsx
```

Use the checker for the complete cache-clearing and verification sequence;
running `soffice` against arbitrary old output is insufficient. It never
overwrites the input. It rejects error cells, missing fresh formula results,
independent value mismatches, broken sheet references, unexpected table ranges,
and recalculation changes to formulas, sheet order, table ranges, chart source
references or defined names. It refuses advanced parts that this Calc route
cannot safely preserve. Inspect `verification.json` when a check fails.

These checks cannot infer whether every plausible reference is the intended
one, prove expectations independent, or verify visual formatting. Review the
actual delivered workbook's changed sheets, number/date formats, tables and
chart appearance. Do not rely solely on a formula count or on text extraction.
If Calc rewrites a formula or range, inspect the change and use a compatible
engine where needed; do not simply remove the check to get a pass.

Formula-free workbooks use the same expected-value checks without Calc and are
recorded as `values_only_no_formulas`. If recalculation is missing or any check
fails, the status is `UNVERIFIED`, never a successful delivery gate. State that
limitation if sharing an unfinished file; do not label its cached results
verified.

## 4. Deliver

Immediately before upload, recheck the source, raw data, expectations, scripts
and candidate bindings:

```bash
python3 "$OFFICE_FILES_DIR/scripts/check_workbook.py" accept --qa generated/workbook-qa
```

Only `READY_TO_DELIVER` permits normal verified delivery. Changing a bound file
invalidates the old acceptance; rerun `verify` into a new QA directory. Upload
the exact `candidate.path` returned by `accept`. For the formula example it is:

```bash
okou web upload-file -f generated/workbook-qa/recalculated/workbook.xlsx
```

For a workbook without formulas the candidate is the original checked output.
Keep input workbooks, authoring code, raw data and QA records for revisions.
