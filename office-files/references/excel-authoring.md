# Excel authoring

Use this page to create or edit `.xlsx` workbooks.

## 1. Install

```bash
python3 -m pip install --break-system-packages --quiet openpyxl==3.1.5
```

## 2. Create or edit

Create the workbook with openpyxl. For an existing workbook, work on a copy,
load it with `load_workbook(..., data_only=False)` to keep formulas, and save
to a new output file. Preserve unrelated sheets, formulas and formatting.

## 3. Check

Reopen the saved workbook and verify the requested data, formulas and formatting.

openpyxl does not calculate formulas. When calculated values are required,
recalculate with a spreadsheet engine, then reopen with `data_only=True` and
verify the results. If recalculation is unavailable, state that calculated
results remain unverified; do not present cached values as current results.

## 4. Deliver

Upload the requested `.xlsx` using the actual output filename:

```bash
okou web upload-file -f generated/workbook.xlsx
```

Keep input workbooks, authoring code and data for revisions.
