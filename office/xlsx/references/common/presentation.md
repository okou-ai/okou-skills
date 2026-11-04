# Common workbook presentation

Read when creating or formatting a workbook. Keep financial-specific decisions
in the finance layer; ordinary rosters, trackers and data exports need not look
like investment-banking models. Preserve supplied templates and house styles.

## Plan before assigning styles

- Match the requested audience and workflow. Put the requested result in an
  obvious place; organize source records, editable fields, calculations and
  explanations so their roles are clear.
- Use a small hierarchy of title, section, header and body styles. Align text
  left and numeric comparisons right; use consistent widths, row heights and
  precision. Freeze useful headers for long tables and enable filters where
  they aid the task.
- Keep labels, units and time periods visible. Use real numeric/date values
  with display formats; retain identifiers with leading zeros as text.
  Missing data is not zero. Follow the requested locale and decimal places.
- Wrap explanation text and allow enough row height. Do not merge ordinary
  data cells needed for filtering/sorting. Use spacing, restrained fills and
  borders to show structure rather than decorating every cell.
- Distinguish user-editable fields using the chosen convention and explain it.
  Do not rely on color alone or imply that color is worksheet protection.
- Use charts only when they improve the requested comparison. Include units,
  periods and labels; keep comparable scales consistent and do not conceal
  differences with arbitrary axis changes.

## Apply styles without collateral changes

For an existing file, follow EDIT before formatting. Do not change values or
formulas in a formatting-only task.

1. Resolve each target cell's actual style: `s` → `cellXfs` → font, fill,
   border, alignment and number format. Account for inherited row/column
   defaults, theme colors and conditional formatting when relevant.
2. Reuse a matching style. Otherwise append the required definitions and a new
   `xf`, then assign the new index only to the intended cells. Changing an
   existing shared style changes every cell that uses it.
3. Keep style counts and references valid. Preserve the required `none` and
   `gray125` fill entries and existing style order. Declare new custom number
   formats with unused IDs of at least 164; built-in formats need no duplicate
   declaration. See the OOXML reference for package details.
4. For a requested border or fill across a row, cover the full requested range,
   not merely the cell a helper added. Check that labels and formulas retain
   their own number format and alignment.

The starter template contains reusable style slots, not a complete report or
an automatically applied financial design. Inspect its actual definitions;
style indices are not meaningful across different workbooks.

## Review the result

Check the affected sheets against the chosen hierarchy and field roles, not
just XML validity. Inspect actual display/export for truncation, `###`,
overlap, misleading formats, chart cuts and unreadable page scaling. Use the
shared VALIDATE workflow; do not claim visual approval from a successful pack
command or a formula-error scan.
