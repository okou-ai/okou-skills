# Finance workbooks

Use for financial models, budgets, forecasts, valuations, statements and
financial management reports in Excel, together with common workbook rules.
For **READ**, use financial semantics only: no theme/font/spacing or model mutation.
Apply authoring, theme, font, spacing and print defaults only to authorized new
reader-facing work or relevant layout changes. Preserve supplied templates/house
styles; narrow edits do not authorize redesign.

- [Financial semantics](#financial-semantics-read-and-authoring)
- [Plan](#plan-the-reading-and-calculation-paths)
- [Theme](#apply-the-fixed-green-theme)
- [Font roles](#apply-financial-font-roles)
- [Spacing](#space-new-report-and-model-sheets)
- [Readability](#make-the-report-readable)
- [Review](#review-the-financial-work-not-only-the-file)

## Financial semantics (READ and authoring)

- Use consistent reporting periods, currency, scale, tax basis and signs.
  Distinguish actual/budget/forecast, assumptions and estimates; do not invent
  missing data, causes or accounting policies. Distinguish operating income,
  net income and cash flow rather than treating them as interchangeable.
- Sum period flows, not stock balances. Quarterly operating margin is total
  quarterly operating income divided by total quarterly revenue, **not** the
  simple average of monthly percentages. Reconcile material summaries to detail.
- Store 5% as `0.05`; distinguish percentage change from percentage-point change.
  Keep years ungrouped. Missing/invalid/unavailable is not zero; a zero-amount
  dash is appropriate only with an explicit legend. Preserve source dates/IDs
  and formula/cache distinctions from READ; do not round intermediate arithmetic.
- Independently verify calculations material to the requested findings. READ
  does not require scenarios, sensitivity work, driver mutation or restyling.

## Plan the reading and calculation paths

For authorized authored models, keep outputs, editable assumptions, retained
history and workings identifiable and traceable. Separate sheets only when useful
for complete, readable review; no fixed tab count or names. Link summaries with
live formulas and reference assumptions rather than duplicating constants. Scope
scenario/sensitivity work to the request. Use the shared data/input contract for
input ownership and dynamic or explicitly baseline-qualified explanations.

## Apply the fixed green theme

For authorized new/layout work only, unless the supplied style overrides it,
use this palette across financial report/model areas. It is not a READ check or
permission to recolor unchanged sheets.

| Use | Fill/accent | Text |
| --- | --- | --- |
| Main title bands and primary chart accents | Deep green `#135B44` | White `#FFFFFF` on title bands |
| Section divider bands | Pale green `#CFE9E0` | Dark green `#0B3D2C` |
| Table column-header labels | Light gray `#F2F2F2` | Dark gray `#404040`, bold |
| Period dividers and sensitivity baseline | Light gray `#E7E5E4` | Neutral text |

Use green bands to introduce sections and gray rows to identify table columns;
keep these levels visually distinct. Neutral header text applies to labels,
not editable inputs or formula outputs that happen to sit in a header row.
Use white (`#FFFFFF`) for data grids. Theme fills and chart accents must not
override the font roles below or imply positive/negative performance.

## Apply financial font roles

For authorized new/layout work, use this precedence for affected data cells
when no supplied convention overrides it:

| Cell role | Default font | Rule |
| --- | --- | --- |
| Editable hard-coded assumption/input | Blue `#0000FF` | Include numeric, text, date and scenario-selector inputs; identify editable cells in a legend |
| Formula depending on another file | Red `#FF0000` | Takes priority over same-workbook links; disclose the external dependency |
| Formula depending on another sheet in this workbook | Green `#008000` | Includes arithmetic, aggregations, and defined names resolving to another sheet |
| Formula using only this sheet | Black `#000000` | Keep formulas distinct from editable hardcodes |
| Labels and retained source records | Neutral text | Do not mark every number or heading as an editable assumption |

Examples: an editable `Inputs!B4 = 0.05` is blue;
`Model!C6 = Inputs!B4` and `C5*(1+Inputs!$B$4)` are green;
`Model!C9 = C7-C8` is black. Resolve named-range targets before assigning a role.
Never color a formula as an editable input. Use fills for sections, periods, or
explicit review flags, not as a substitute for the font-role convention.

These are modeling defaults, not accounting standards, edit permissions, or
proof of correctness. Inspect fonts/number formats, not copied style indices.

## Space new report and model sheets

For new reader-facing layouts (not READ/raw-data-only exports), keep hierarchy
and whitespace readable; narrow edits retain the existing geometry. Optional
starting presets, not fixed acceptance requirements:

- Two blank rows above the title, one after the title band and one before the
  first content block; keep subtitle/unit notation together. Share coinciding
  spacers and adapt the gaps to the actual content.
- Separate completed sections or standalone tables with one blank row. Keep a
  section band next to its table's column-header row, and headers next to data;
  do not scatter blank rows between every label or record.
- After a margin/ratio line or a completed subtotal block, use a short spacer
  (about 6 pt high) where needed to distinguish the next group. A full section
  gap replaces this smaller gap; do not stack both.
- Keep spacer rows empty and unshaded, outside structured tables, filter ranges
  and raw-data blocks. Do not fake spacing with hidden rows or blank formulas.
- Plan the gaps before writing formulas and ranges. Preserve existing layouts
  during narrow edits; check dependencies if authorized row insertion is needed.
  Inspect the affected application view or rendered export for crowded/excessive
  gaps; actual export is necessary when printing/pagination matters.

## Make the report readable

- State currency and scale near the numbers. Use the supplied currency rather
  than inheriting the starter template's dollar symbol. Keep comparable values
  at consistent precision; use parentheses for negative amounts by default.
- Use percentage formats for rates and ungrouped year formats. Preserve the
  financial semantics above; formats are not permission to change source values.
- Label actual/budget/forecast periods explicitly. Where they are adjacent, use
  a consistent separator or light neutral fill as a second cue; labels must
  work without color. Do not imply that forecast values are observed actuals.
- Establish title → section → table header → detail hierarchy. Emphasize key
  results/subtotals with bold type and appropriate rules; distinguish explanation
  text from numeric rows. Use whitespace and the fixed green theme rather than
  full-sheet fills or fixed row numbers.
- Keep explanations consistent with formulas. Make input-dependent narrative
  dynamic or label it as applying to the stated baseline. Do not infer causes
  or motives merely because two numbers move together.
- Make printing/export usable when relevant: set the actual report area, page
  direction and one-page-wide fit without shrinking an entire long model onto
  one unreadable page. Do not impose a print layout on a raw-data-only export.

## Review the financial work, not only the file

Use the shared VALIDATE impact matrix; for READ independently verify only the
financial semantics/calculations material to the requested findings. For authored
or changed financial work, also check the applicable items:

- Summary/scenario results reconcile to detail and source inputs on the semantic
  basis above, with current final live formulas/caches when calculation-driven.
- For adjustable models being authored or changed, verify material driver effects
  through detail, summary and required sensitivity outputs using the shared
  propagation procedure; do not claim execution from formula text alone.
- Editable inputs, same-sheet calculations, cross-sheet links, and any external
  dependencies follow the selected legend throughout the affected model.
- For new/layout work, relevant reader-facing areas are actually readable:
  headings, units, amounts, explanations and charts are not clipped, overlapping
  or illegibly scaled. Inspect affected areas, not an unrelated blanket export.
- Key conclusions, scope and limitations are easy to locate. Do not report a
  blanket pass when application or visual checks could not be performed.

Use the shared VALIDATE workflow for execution and evidence boundaries. The
bundled style audit is a diagnostic aid, not a replacement for this review.
