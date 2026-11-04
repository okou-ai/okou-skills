---
name: xlsx
description: Create, read, edit, format, and validate Excel spreadsheets. Use for XLSX files, spreadsheet formulas, tables, and financial models, budgets, forecasts, scenarios, or management reports delivered in Excel. Select both the file operation and the business scenario; financial workbooks also load the finance reference. Read CSV/TSV data without changing the source.
license: MIT
---

# Excel workbooks

Select **both an operation and a business scenario** before authoring. Choosing
CREATE or EDIT does not finish scenario selection. User requirements and an
existing template or house style take precedence over these defaults.

Set `SKILL_DIR` to the absolute directory containing this file. Read only the
common guidance, applicable scenario, and operation needed for the task.

## Layer 1 — Common workbook rules

- Preserve the source. Read-only analysis must not save, restyle, or recalculate
  the original. Perform edits and application checks on separate copies.
- Use live Excel formulas for derived workbook outputs; keep source records and
  adjustable inputs identifiable. Do not replace formulas with cached answers.
- Preserve unrelated sheets, formulas, styles, controls, and package features.
  A narrow edit is not permission to rebuild or redesign the workbook.
- For new workbooks or requested formatting, read
  [common presentation](references/format.md). For narrow edits, apply it only
  to changed cells without overriding the supplied layout.
- For new reader-facing analytical reports/dashboards or authorized chart changes,
  read [analytical charts](references/charts.md) during planning. Choose charts for
  the question, not a fixed count; preserve data-only and narrow-edit scope.

## Layer 2 — Business scenario

| Requested work product | Read before planning the workbook |
| --- | --- |
| Financial model, revenue/cost budget, forecast, valuation, financial statements, scenario/sensitivity analysis, or financial management report | [Finance](references/finance.md), even if the request never says "finance" |
| Operational tracker, inventory, roster, ordinary data table, or other non-financial spreadsheet | Common presentation only; do not impose financial colors or extra model tabs |
| One-cell update, formula repair, or template filling in an existing financial file | Preserve the existing structure and house style; use only the finance rules relevant to the requested change |
| Read-only extraction or analysis | [Read and analyze](references/read-analyze.md); do not redesign the source |

For mixed workbooks, apply the finance layer to the financial model/report
areas, not every unrelated table. Finance guidance is bundled here: do not stop
at a generic spreadsheet route or require an external skill search to find it.

Examples:
- "Build next quarter's revenue, costs and hiring scenarios" → finance + CREATE.
- "Make a stock-count tracker" → common presentation + CREATE, not finance.
- "Change the tax-rate input in this workbook" → EDIT; keep its other tabs and
  layout, rather than adding an executive-summary sheet.

## Layer 3 — Operation and implementation

| Operation | Read | Tools |
| --- | --- | --- |
| Create a new XLSX | [Create](references/create.md) | Prefer a suitable high-level library; raw OOXML remains available |
| Edit, fill a template, or repair formulas | [Edit](references/edit.md) | Unpack → targeted XML changes → pack |
| Read or analyze XLSX/XLSM/CSV/TSV | [Read and analyze](references/read-analyze.md) | `xlsx_reader.py`, then analysis tools as needed |
| Apply or change formatting | [Common presentation](references/format.md) and [Edit](references/edit.md) for existing files | Append/reuse styles; change only intended cells |
| Check a created or edited workbook | [Validate](references/validate.md) | Static checks, application checks, and task/scenario review |

For new financial work using openpyxl, read [high-level primitives](references/authoring.md)
when choosing construction helpers. Check the calculation environment before
substantial formula authoring, then build, view and revise inside the same attempt.
Read [OOXML details](references/ooxml-cheatsheet.md) only when directly changing
package relationships, cell types, strings, or style definitions. Style indices
are workbook-local; never copy an index from an example into an unrelated file.

## Finish

Use the selected scenario's requirements while building, not as optional
polish after the workbook is complete. Run the applicable checks in VALIDATE
and fix discovered defects. A formula scanner's exit code is not a certificate
of financial accuracy, presentation quality, or usability. State unavailable
checks honestly and deliver only the files the user requested.
