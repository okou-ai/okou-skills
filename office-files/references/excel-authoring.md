# Excel authoring

For ordinary new workbooks, use the JSON author below. Read script source only
to investigate a specific failure or implement an unsupported feature. Set the
package path in a separate shell command:

```bash
export OFFICE_FILES_DIR="/absolute/path/to/office-files"
```

## 1. Prepare

Install missing dependencies once:

```bash
python3 -m pip install --break-system-packages --quiet openpyxl==3.1.5 lxml==6.1.3 PyMuPDF==1.28.2
sudo apt-get update
sudo apt-get install -y libreoffice-calc
```

Use a meaningful final filename before starting QA. Calc is required for
formula recalculation and PDF preview; Writer alone cannot load XLSX.

## 2. Author

Copy [the working JSON spec](../assets/workbook.json) to
`generated/workbook.json`, replace its content/data, then run:

```bash
python3 "$OFFICE_FILES_DIR/scripts/author_workbook.py" \
  --spec generated/workbook.json --output generated/operating-summary.xlsx
```

Keep analysis and charts relevant to the requested decisions. Let content
paginate naturally unless the user specifies a page limit.

### JSON fields

`version` is `1`; `sheets` is an ordered array. Only the fields below are
supported; use Python for other features.

| Field | Input |
| --- | --- |
| `theme` | Optional `font`, `font_size`, `accent`, `stripe`, `currency`, `chart_colors` (RGB hex strings without `#`) |
| `styles` | Named style objects; built-ins are `normal`, `header`, `title`, `total`, `note` |
| Sheet `name` | Unique Excel sheet name |
| `start_cell`, `columns`, `rows` | Table starts at `A1` by default. Column objects take `header`, `width` and style fields. Rows are arrays matching the columns; strings starting `=` are formulas. Omit columns for rows without a header. |
| `cells` | A1-address-to-value/object mapping, applied after rows. Cell objects take `value` **or** `formula`, optional `style`, style fields and `type: "date"` (ISO date) or `"text"` (literal text even if it begins `=`). |
| Style fields | `font`, `font_size`, `bold`, `italic`, `color`, `fill`, `format`, `horizontal`, `vertical`, `wrap`, `border` (bottom-border color). `format`: `money`, `integer`, `decimal`, `percent`, `date`, `text`, or an Excel number-format string. |
| `column_widths`, `row_heights` | Overrides such as `{"A": 18}` and `{"1": 32}` |
| `merges` | A1 ranges, e.g. `["A1:F1"]`; other cells in each range must be empty |
| `freeze`, `filter`, `table` | Freeze cell (e.g. `B2`), filter range (e.g. `A1:E20`), optional structured-table name for the columns/rows block |
| `charts` | Chart objects described below |
| `print` | Optional `orientation` (`portrait`/`landscape`), `area`, `title_rows` (e.g. `1:1`), `break_rows` (break after these row numbers) |

Chart objects take `type` (`column`, `bar`, `line`), `title`, `data_sheet`,
`data`, `categories`, `anchor`, optional `titles_from_data` (default true),
`number_format`, `labels` (default false), `legend` (`b`, `t`, `l`, `r`, null),
and `colors`. Data is a rectangular range with one series per column;
categories is one column with the same number of data rows. `anchor: "A7:D21"`
occupies those cells, inclusive. Set column widths and leave a row/column gutter
between charts. Defaults use explicit grid anchors, cell fills and per-series
label flags that survive Calc. When enabling labels, make the source-cell
number format readable; Calc may ignore a label-specific format.

The default print area includes cells and charts, fits one page wide and has
unlimited height. Keep all content in the reviewed print area; use page breaks
between logical blocks when a preview splits a chart or table. Literal wrapped
text gets an estimated row height; check long text in the preview. Do not wrap
formulas inside merged cells: Calc can drop the wrapping. Use an unmerged cell,
or put a short formula result beside a separate literal label.

### Existing files or advanced features

Work on a copy with `load_workbook(..., data_only=False)` and save to a new
output. Preserve unrelated sheets, formulas and formatting. After inserting or
deleting rows/columns/sheets, update affected totals, cross-sheet formulas,
table boundaries, chart ranges and defined names explicitly; openpyxl does not
maintain them all. A valid formula can still reference the wrong row.

Inventory pivots, macros, external links and embedded objects first. Use a
compatible native workflow when openpyxl/Calc cannot preserve required features;
do not deliver a rewritten replacement without preservation checks.

## 3. Check data, then recalculate once

Derive key results independently from raw inputs (for example, Python sums),
never from workbook caches or a copy of its formulas. Cover every requested or
affected total, subtotal, ratio and cross-sheet indicator. Save expectations:

```json
{
  "calculation_basis": "Independently sum raw revenue inputs: 3000 + 48 + 380 = 3428.",
  "range_review": "Data rows 2:4 are the three input months. Summary B3 sums Data B2:B4. MonthlyData and both chart source ranges cover these rows; no other data rows exist.",
  "cells": [{"sheet": "Summary", "cell": "B3", "value": 3428}],
  "tables": [{"sheet": "Data", "name": "MonthlyData", "ref": "A1:E4"}]
}
```

Expand this example to cover the actual key results. `cells` must be nonempty,
even without formulas; values can be strings, numbers, booleans or null.
Numeric `abs_tol`/`rel_tol` default to zero; set appropriate tolerances for
ratios. Include affected tables and describe the actual reference review in
`range_review`; for new workbooks review initial ranges too.

Use real files in these commands. Bind original raw inputs as `--data`; a spec
containing literal simulated inputs may itself be that raw data. Bind authoring
code and independent expectation code with repeatable `--resource`; for edits,
also bind the original workbook. Formula workbooks need raw data and at least
one independently expected formula result; this minimum is not full coverage.

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
  --resource generated/build_expectations.py \
  --out generated/workbook-qa
```

Fix quick-check errors before `verify`. Quick checks do not verify fresh formula
results. Use a new QA directory for each changed candidate. `verify` clears old
caches, recalculates in a private Calc profile, compares independent values and
checks formula/sheet/table/chart-range/name preservation. Inspect
`verification.json` for failures; do not remove a check to make it pass. Use a
compatible engine if Calc changes a required formula, range or advanced feature.

Formula-free files still require expected-value checks. Failed or missing
verification is `UNVERIFIED`; do not describe its caches as verified.

## 4. Batch preview and deliver

```bash
python3 "$OFFICE_FILES_DIR/scripts/render_workbook.py" --qa generated/workbook-qa
```

Open `workbook-qa/preview/gallery/index.html` for the batch overview and inspect
each page at readable size. Check the **recalculated candidate**, including
number/date formats, formulas displayed as text, merged text, table pagination,
labels, chart placement and print-area coverage. Record each reviewed page's
`status: "pass"` and observations in `preview/review.json`; fix failures and
repeat QA only after an actual change. Calc PDF preview does not establish
native Excel rendering, nor does it review hidden/out-of-print-area content.

Immediately before upload:

```bash
python3 "$OFFICE_FILES_DIR/scripts/check_workbook.py" accept --qa generated/workbook-qa
```

Only `READY_TO_DELIVER` permits verified delivery. Upload the exact
`candidate.path` returned by `accept`; for formula workbooks it is the
recalculated file. Changes to bound files invalidate acceptance. Keep source
workbooks, spec/code, raw data and QA records for revisions.
