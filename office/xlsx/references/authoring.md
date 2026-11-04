# High-level financial authoring primitives

Read when creating a new financial report with openpyxl and the finance defaults.
Do not use this to redesign an existing workbook or impose finance styling on an
ordinary table. A supplied template/house style takes precedence.

Add the bundled scripts directory to the chosen interpreter's import path:

```python
import os
import sys
sys.path.insert(0, os.path.join(os.environ["SKILL_DIR"], "scripts"))
from xlsx_authoring import style_value, report_band, table_header, report_page
```

These helpers operate on worksheets/cells already planned by the author. They
do not create sheets, decide sheet count, insert formulas or supply business
facts. Read `scripts/xlsx_authoring.py` for signatures and supported kinds.

## Cell roles and formats together

Populate a cell, then call `style_value(cell, role=..., kind=...)`.

| `role` | Use |
| --- | --- |
| `input` | An editable hardcoded assumption; not every source number |
| `same_sheet` | A live formula using only this sheet |
| `cross_sheet` | A live formula depending on another sheet in this workbook |
| `external` | A live formula depending on another file |
| `source` / `label` | Retained source value / ordinary text |

Resolve named-range targets and indirect dependencies yourself before selecting a
role. The helper checks formula vs literal state, not every dependency. It keeps
other font attributes while selecting the finance font color. Supported `kind`:
`amount`, `percent`, `integer`, `year`, `date`, `text`. Choose appropriate precision
or a supplied format directly when these defaults do not match the task.

```python
# Illustrative cell objects; compute these locations from the workbook plan.
rate_cell.value = 0.05
style_value(rate_cell, role="input", kind="percent")
margin_cell.value = f"={profit_cell.coordinate}/{revenue_cell.coordinate}"
style_value(margin_cell, role="same_sheet", kind="percent")
```

Do not blanket-wrap errors in `IFERROR(...,0)`. Preserve a genuine missing or
invalid denominator as a diagnosed model issue, not a fabricated zero result.

## Layout as explicit geometry

- `report_band(ws, planned_range, text, level="title" or "section")` spans one
  planned empty row, fills its full width, and sets a usable band height. It
  refuses to merge over existing content or merged ranges; call before populating
  that range. There are no fixed starting cell addresses.
- `table_header(ws, label_range)` styles one gray column-label row. It refuses
  formula outputs. Do not apply it over editable inputs; those retain input roles.
- `report_page(ws, report_range, orientation="landscape", paper_size=...)` sets
  the print area and one-page-wide fit with unrestricted height. Pass the selected
  paper size explicitly. It does not choose readable widths or page breaks.

Set widths for each content column and heights for wrapped explanation rows;
allocate chart space outside the tables and notes. Apply the finance spacing
reference rather than shrinking content into fewer sheets. Keep grid values and
formula roles legible; adjust geometry after looking at actual exports.

## Save, calculate and inspect

The helpers neither evaluate formulas nor write their caches. After library
save, use the control-tested application path in [VALIDATE](validate.md). Read
the final file using `load_workbook(..., data_only=False)` to check formulas and
`data_only=True` to inspect current cached results; these reads alone do not
prove native calculation. Do not save either readback just to inspect it.

After Calc conversion, compare relevant formulas, features and formatting before
selecting that file for delivery. Recalculate again after any later library save.
Export and inspect relevant sheets, revise defects, then check the exact final
file again. A helper call or static PASS is not a finished-workbook guarantee.
