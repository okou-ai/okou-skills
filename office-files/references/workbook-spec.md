# Workbook JSON specification

Use this reference with [the Excel workflow](excel-authoring.md). The author
accepts `version: 1`; existing sheet-level `start_cell`, `columns`, `rows` and
`table` specs continue to work. New features below also work in that original
single-block form, except `title`, which belongs to `blocks` entries.

## Workbook and sheet fields

Only the fields below and the block/column extensions in this reference are
supported. Use the Excel workflow's existing-file/native-feature route for
other authoring needs.

| Field | Input |
| --- | --- |
| `version`, `sheets` | `version` is `1`; `sheets` is a nonempty ordered array. |
| `theme` | Optional `font`, `font_size`, `accent`, `stripe`, `currency`, `chart_colors`. Colors are six-digit RGB hex strings without `#`. |
| `styles` | Named style objects; built-ins are `normal`, `header`, `title`, `total`, `note`. Named overrides extend those built-ins. |
| Sheet `name` | Unique Excel sheet name, at most 31 characters, without `\\ / * ? : [ ]`. Names are case insensitive. |
| `start_cell`, `columns`, `rows` | Original single-block form: starts at `A1` by default. Nonempty columns create a header row. Rows are arrays; strings starting `=` are formulas unless typed as text. Omit columns for headerless rows. Column and row rules are below. |
| `blocks` | Array of reusable sections; replaces sheet-level `start_cell`, `columns`, `rows`, `table`. See below. |
| `cells` | A1-address-to-value/object mapping. In the original single-block form, applied after rows and allowed to override them. With `blocks`, must be outside their reserved rectangles. Objects take `value` **or** `formula`, optional `style`, style fields, and `type`. |
| `column_widths`, `row_heights` | Overrides such as `{"A": 18}` and `{"1": 32}`. Column widths must be positive and at most 255; row heights positive and at most 409. |
| `merges` | A1 ranges, e.g. `["A1:F1"]`; other cells in each range must be empty. Ranges cannot overlap each other or intersect blocks. |
| `freeze`, `filter`, `table` | Freeze cell (e.g. `B2`), sheet filter range (e.g. `A1:E20`), optional structured-table name for the original single block. Each reusable block instead supplies its own `table`. |
| `charts` | Array of chart objects, described below. |
| `print` | Optional `orientation` (`portrait`/`landscape`), `area`, `title_rows` (e.g. `1:1`), `break_rows` (break after these row numbers). |

Style objects and inline style fields accept `font`, `font_size`, `bold`,
`italic`, `color`, `fill`, `format`, `horizontal`, `vertical`, `wrap`, `indent` and
`border` (bottom-border color). `format` may be `money`, `integer`, `decimal`,
`percent`, `date`, `text`, or an Excel number-format string. The `money` format
uses `theme.currency`, defaulting to `¥`. A column's style fields apply to its
data cells; headers use the named `header` style.
Use `horizontal: "left", indent: 1` on text columns when a right-aligned
number/date in the preceding column touches its label. Indentation changes
alignment, not the underlying value; the default remains zero.

All cell/range strings use uppercase A1 coordinates without a sheet qualifier;
`$` anchors are allowed. Formulas may contain normal sheet-qualified references.

## Reusable sheet blocks

For a sheet with several sections, use `blocks` instead of the sheet-level
`start_cell`, `columns`, `rows` and `table` fields. Each block accepts only:

| Field | Meaning |
| --- | --- |
| `start_cell` | One uppercase A1 cell without a sheet qualifier; defaults to `A1`. This is the title row when `title` exists, otherwise the header row (or first data row without columns). |
| `title` | Optional nonempty literal string, or an object with `value`, optional named `style`, and the usual style fields. It occupies one row merged across the block's actual width, using the `title` style by default. It never becomes a formula. |
| `columns` | Optional array of column objects. Each object accepts `header`, `width`, `type`, `formula`, and the usual style fields. A nonempty array creates one header row. |
| `rows` | Array of data arrays; defaults to `[]`. The first data row immediately follows the optional title and header rows. Rules for formula columns are below. |
| `table` | Optional structured-table name, unique across the whole workbook (case insensitive). Requires nonempty, unique string column headers and at least one data row. The table includes the header and data, excluding the title. |

Blocks reserve their entire rectangle, including null values and unused cells
in shorter headerless rows. Overlapping blocks are rejected. Sheet `cells` and
explicit `merges` must be outside every block. Put per-cell styling in row cell
objects; use `title` for an automatically merged section heading. Each block
must have a title, columns, or nonempty row content. Blocks that extend beyond
Excel's `XFD` column or row `1048576` are rejected before saving.

`rows: []` intentionally creates just a title/header section; omit `table`
until data exists. No placeholder data row is invented. A title-only block is
one cell wide. Without columns, the widest row defines the block width and
shorter rows are allowed. `blocks: []` is also allowed for a sheet using only
ordinary `cells`/charts or an intentionally blank sheet.

Column widths belong to the sheet, even when multiple blocks use a column.
Prefer one sheet-level `column_widths` map for sections sharing columns. An
explicit width in one block applies to all blocks using that absolute column;
conflicting explicit widths are rejected unless `column_widths` supplies the
shared override. Unspecified widths default to 16 for declared columns.
Freeze panes, filters, charts, row heights and print settings remain sheet
fields. Chart references and print areas use final worksheet coordinates.

## Column types and row cell objects

`type: "date"` converts ISO date strings to actual Excel date values; null
stays blank. It defaults to `yyyy-mm-dd` unless a cell or column format is
provided. `format: "date"` alone only sets the number format: it does **not**
convert string values. `type: "text"` stores literal text, including strings
starting `=`; numeric/boolean inputs become their JSON text spelling and null
stays blank.

A data cell may be a scalar or an object with `value` **or** `formula`, optional
`type`, named `style`, and the usual style fields. Objects work in both `rows`
and the sheet's `cells` mapping. Column types apply to scalar values and cell
objects alike. An explicit cell `type` overrides the column type; `type: null`
clears the inherited conversion, for example for a formula in a date column.
Cell style fields override column style fields. A formula uses a string
starting `=`. To keep such a string literal, use `type: "text"`.

## Formula columns

Set a column's `formula` once, written for that column's **first data cell**.
The author uses openpyxl's `Translator` to fill it down, preserving absolute
references (`$B$2`), mixed references (`B$2`, `$B3`), ranges and sheet-qualified
references. The source formula is not moved automatically when you change a
block's `start_cell` or add/remove its title: update the source formula to the
new first data row. Named/structured references retain their original tokens.
Use `format` for formula results; a formula column cannot also have `type`.
Put a range's worksheet qualifier once before the range, e.g.
`'Data'!A2:B3`. Column formula fill rejects repeated endpoint qualifiers such
as `'Data'!A2:'Data'!B3` and 3-D sheet ranges such as `Sheet1:Sheet3!A2`;
openpyxl cannot translate all of those endpoints safely. This restriction
applies only to column formula fill, not ordinary per-cell formulas.

Each row with columns must use one of these two unambiguous forms:

- **Compact:** provide only the non-formula columns, in their original order.
  Formula columns are omitted, including those between input columns.
- **Full:** provide one entry per column. Every formula-column entry must be
  null or a style-only object (named `style` and/or style fields, with no
  `value`, `formula` or `type`). An attempted value override is rejected.

Both forms can be used in one block. With no formula columns they are the
same form. With only formula columns, each compact data row is `[]`.

## Example

This has a four-column title band at `B2:E2`, a structured table at `B3:E5`,
real dates, literal customer IDs and a formula filled from `E4` to `E5`.
The second block shows an intentional empty section sharing the same widths.

```json
{
  "version": 1,
  "sheets": [{
    "name": "Sales",
    "column_widths": {"B": 16, "C": 22, "D": 18, "E": 18},
    "cells": {"G1": {"value": 0.1, "format": "percent"}},
    "blocks": [
      {
        "start_cell": "B2",
        "title": "九月销售 · 示例数据",
        "columns": [
          {"header": "日期", "type": "date"},
          {"header": "客户编号", "type": "text"},
          {"header": "收入", "format": "money"},
          {"header": "含税金额", "format": "money", "formula": "=D4*(1+$G$1)"}
        ],
        "rows": [
          ["2026-09-01", "00123", 100],
          [{"value": "2026-09-02", "format": "yyyy/m/d"}, "=literal", 200, {"style": "total"}]
        ],
        "table": "SeptemberSales"
      },
      {
        "start_cell": "B8",
        "title": "待录入十月数据",
        "columns": [{"header": "日期", "type": "date"}, {"header": "客户编号", "type": "text"}],
        "rows": []
      }
    ]
  }]
}
```

## Charts and print layout

Chart objects accept `type` (`column`, `bar`, `line`), `title`, `data_sheet`
(defaults to the current sheet), required `data`, `categories` and `anchor`,
optional `titles_from_data` (default true), `number_format`, `labels` (default
false), `legend` (`b`, `t`, `l`, `r`, null) and `colors` (nonempty RGB array).
`data` is a rectangular range with one series per column. `categories` is one
column with the same number of data rows, excluding the optional title row.
The default chart type is `column`; default number format is `decimal`. Legends
default to bottom for multiple series and are omitted for a single series.
Colors use `theme.chart_colors` or the built-in palette when omitted.
Horizontal bars keep category labels at the chart edge, including when
negative values move the zero axis into the plot.

`anchor: "A7:D21"` occupies those cells, inclusive. Set column widths and leave
a row/column gutter between charts; overlapping chart rectangles are rejected.
Chart defaults use explicit grid anchors, cell fills and per-series label flags
that survive Calc. When enabling labels, make the source-cell number format
readable; Calc may ignore a label-specific format. Chart sources and anchors
remain explicit sheet coordinates, including when source data uses blocks.

The default print area includes cells and charts, uses A4 paper, fits one page
wide and has unlimited height. Orientation defaults to landscape when the
rightmost used column is beyond `F`, otherwise portrait. Keep all content in
the reviewed print area; use page breaks between logical blocks when a preview
splits a chart or table. Literal wrapped text gets an estimated row height;
check long text in the preview. Do not wrap formulas inside merged cells: Calc
can drop the wrapping. Use an unmerged cell, or put a short formula result
beside a separate literal label.

Authoring alone does not verify formula results. Follow the independent
expectations, Calc verification and preview review steps in the
[Excel workflow](excel-authoring.md) before delivery.
