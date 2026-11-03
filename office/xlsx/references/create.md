# Create a new XLSX

Use for a new workbook, not for filling or changing an existing file. Select
the business scenario and common presentation before writing. Keep calculated
outputs as live formulas rather than pasting externally computed answers.

## 1. Plan

Choose the smallest useful sheet/block structure, the intended reading order,
source/input locations, formula dependencies and styles. Use the finance layer
for budgets, forecasts and financial reports. Do not add unrelated analyses.

## 2. Copy the starter

```bash
cp -R "$SKILL_DIR/templates/minimal_xlsx" /tmp/xlsx_work
```

Use a fresh working directory. The starter is a package skeleton with one
worksheet, shared strings and styles; it does not assign styles to your model.
Edit XML and pack with the bundled tools. Read OOXML details when adding package
parts or implementing cell/string/style definitions.

When adding a sheet, keep these four points consistent:

| Location | Required change |
| --- | --- |
| `xl/workbook.xml` | Add a unique sheet name, stable `sheetId`, and relationship ID |
| `xl/_rels/workbook.xml.rels` | Map that ID to the new worksheet part |
| `[Content_Types].xml` | Declare the worksheet part's content type |
| `xl/worksheets/` | Create the referenced XML file |

Read existing IDs before assigning new ones. In the starter, `rId1` is the
initial sheet, `rId2` styles, and `rId3` shared strings; additional sheets start
at an unused ID such as `rId4`. Keep names within Excel's length/character
limits and quote names with spaces in formulas.

## 3. Populate data and formulas

- Store raw numeric inputs as numbers, rates as decimals, and dates with
  appropriate date formats. Write text as shared strings or inline strings;
  XML-escape text and preserve significant whitespace.
- For shared strings, use zero-based indices and accurate counts: `uniqueCount`
  is the number of entries, while `count` is total shared-string cell usage.
  `shared_strings_builder.py --help` describes the bundled construction helper;
  review counts after repeated strings or later edits.
- Write formulas in `<f>` without the UI's leading `=`. Keep source inputs,
  derived results, labels and their styles distinct. Resolve named ranges and
  cross-sheet references instead of inventing indices or sheet paths.

```xml
<!-- Numeric input; choose s for its actual role and display format. -->
<c r="B2"><v>1000</v></c>
<!-- Formula with an empty cache until an application recalculates it. -->
<c r="B4"><f>SUM(B2:B3)</f><v/></c>
<!-- Text may be inline; shared strings use t="s" and an index in v. -->
<c r="A1" t="inlineStr"><is><t>Amount</t></is></c>
```

An empty cache is not a successful calculation. Apply final styles, useful
widths/heights and any requested print settings before checking the result.
Use ordinary formulas unless shared/array formulas are actually needed; if
used, preserve their primary range and consumer relationships.

## 4. Pack and check

```bash
python3 "$SKILL_DIR/scripts/xlsx_pack.py" /tmp/xlsx_work output.xlsx
python3 "$SKILL_DIR/scripts/formula_check.py" output.xlsx
```

Packing checks XML well-formedness, not complete spreadsheet correctness.
Continue with VALIDATE for recalculation, task/scenario checks and actual
presentation review. Deliver the requested file only; do not append an
unrequested validation report or alternate workbook.
