# Excel authoring

Choose the authoring route once; read its interface, then run the scripts.
Inspect implementation only for a concrete failure or an unsupported feature.

| Task | Route |
| --- | --- |
| Tabular inputs → monthly/category totals, ratios, changes and charts | [Tabular summary builder](tabular-summary.md): raw CSV/JSON + a small report spec; emits formulas, ranges and independent expectations together |
| Custom workbook layout or formulas outside that builder | [Workbook JSON spec](workbook-spec.md): reusable blocks, typed columns, formula fill and chart anchors |
| Edit an existing file or use native Excel features | Preserve the source as described below; use Python/native Excel for the required edit |

## Prepare

Set the package path on its own line. Install missing dependencies once:

```bash
export OFFICE_FILES_DIR="/absolute/path/to/office-files"
python3 -m pip install --break-system-packages --quiet openpyxl==3.1.5 lxml==6.1.3 PyMuPDF==1.28.2
sudo apt-get update -qq
sudo apt-get install -y -qq libreoffice-calc
```

Calc provides formula recalculation and print previews; Writer alone cannot
load XLSX. Choose the final filename before QA. Keep raw input data separate
from presentation. For simulated data, generate inputs once, inspect the
aggregates, then write conclusions supported by those aggregates.

## Author

For supported tabular summaries, follow the linked builder page and use
`--prepare-review` to run authoring, quick checks, fresh calculation and preview
in one command. Reuse its generated expectations and source bindings; no custom
`build_spec.py` or `build_expectations.py` is needed for supported calculations.

For a custom layout, copy [the workbook example](../assets/workbook.json), adapt
it using the JSON reference, and run:

```bash
python3 "$OFFICE_FILES_DIR/scripts/author_workbook.py" \
  --spec generated/workbook.json --output generated/operating-summary.xlsx
```

Use column `type: "date"` for real dates; `format: "date"` alone does not parse
text. Reuse `blocks` and column `formula` templates instead of spelling out
every cell address. Let content paginate naturally. Review actual clipping,
misleading labels, broken references or unreadable text; passing checks do not
call for another candidate solely to explore alternate styling.

### Existing files and advanced features

Work on a copy with `load_workbook(..., data_only=False)` and save to a new
output. Preserve unrelated content. After structural edits, explicitly update
all affected totals, formulas, table/chart ranges and defined names; openpyxl
does not maintain them all. Inventory pivots, macros, links and embedded objects
first. Use a compatible native workflow for features openpyxl/Calc cannot
preserve, with preservation checks before delivery.

## Verify custom workbooks

The summary builder's `--prepare-review` performs this section automatically.
For other routes, derive expected results from raw inputs, not workbook caches
or copies of Excel formulas. Cover every requested or affected total, subtotal,
ratio, cross-sheet indicator and plotted result. Check representative repeated
row calculations and boundary rows; listing every repeated formula is not a
substitute for covering all key outputs.

```json
{
  "calculation_basis": "Raw revenues 3000 + 48 + 380 sum to 3428; calculated independently of workbook formulas.",
  "range_review": "Data rows 2:4 contain all three months. MonthlyData and chart ranges cover these rows. Summary B3 is the revenue total.",
  "cells": [{"sheet": "Summary", "cell": "B3", "value": 3428}],
  "tables": [{"sheet": "Data", "name": "MonthlyData", "ref": "A1:E4"}]
}
```

Expand the example for the actual requested outputs. `cells` must be nonempty,
even without formulas; values may be strings, numbers, booleans or null. Set
appropriate numeric `abs_tol`/`rel_tol` (defaults zero). Bind raw data with
`--data` and authoring/expectation code with repeatable `--resource`; for edits,
also bind the original workbook. A spec with literal simulated inputs can be
the raw data. Use real files in these commands:

```bash
python3 "$OFFICE_FILES_DIR/scripts/check_workbook.py" quick \
  --input generated/operating-summary.xlsx \
  --expectations generated/workbook-expectations.json \
  --data generated/workbook.json \
  --resource "$OFFICE_FILES_DIR/scripts/author_workbook.py" \
  --resource generated/build_expectations.py

python3 "$OFFICE_FILES_DIR/scripts/check_workbook.py" verify \
  --input generated/operating-summary.xlsx \
  --expectations generated/workbook-expectations.json \
  --data generated/workbook.json \
  --resource "$OFFICE_FILES_DIR/scripts/author_workbook.py" \
  --resource generated/build_expectations.py --out generated/workbook-qa
```

Fix quick-check errors before `verify`; quick does not compare fresh values.
Verification clears stale caches, recalculates in a private Calc profile and
checks values plus formula/sheet/table/chart-range/name preservation. Equivalent
case and redundant sheet quotes are already normalized; use valid Excel quoting
for names containing spaces or apostrophes. Do not change sound formulas to
avoid that supported normalization.

Read `failures` and `formula_coverage`: omitted sheets or key results need
attention. Counts do not prove complete semantic coverage. A failed or missing
verification is `UNVERIFIED`; do not remove checks to obtain a pass. Use a new
QA directory for each changed candidate.

## Review and deliver

For custom workbooks, generate the preview after verification:

```bash
python3 "$OFFICE_FILES_DIR/scripts/render_workbook.py" --qa generated/workbook-qa
```

Open the gallery for the overview, then every page at readable size in batches.
Review the recalculated candidate: number/date formats, displayed formulas,
merged text, tables, labels, chart placement and print coverage. Record a short,
specific observation and `status: "pass"` for each reviewed page in
`preview/review.json`. Fix actual defects and repeat QA after changes. Calc print
previews do not establish native Excel appearance or cover hidden/nonprinting
content; verify that the visible scope includes the intended deliverable.

```bash
python3 "$OFFICE_FILES_DIR/scripts/check_workbook.py" accept --qa generated/workbook-qa
```

Only `READY_TO_DELIVER` permits verified delivery. Upload the exact
`candidate.path` returned by `accept`, then provide its link promptly. Changes
to bound files invalidate acceptance. Keep the source, raw data and QA records
for revisions. Any requested retrospective follows delivery using existing
logs; it does not require regenerating the files.
