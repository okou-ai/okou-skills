# Finance workbooks

Use for financial models, budgets, forecasts, valuations, statements and
financial management reports in Excel, together with common workbook rules.
Preserve supplied templates/house styles; narrow edits do not authorize redesign.

- [Plan](#plan-the-reading-and-calculation-paths)
- [Theme](#apply-the-fixed-green-theme)
- [Font roles](#apply-financial-font-roles)
- [Spacing](#space-new-report-and-model-sheets)
- [Readability](#make-the-report-readable)
- [Review](#review-the-financial-work-not-only-the-file)

## Plan the reading and calculation paths

1. Fix the audience, decision, reporting periods, currency, scale, and model
   scope from the request and sources. Distinguish actuals, assumptions and
   estimates; retain source locations for material inputs. Do not invent missing
   data, explanations, or accounting policies.
2. Start the reader with the answer: key results, period/scenario comparisons,
   main drivers, and material limitations. Keep detailed workings available
   behind that overview rather than making raw inputs the entry point.
3. For new budgets, forecasts or multi-scenario models, normally put the
   overview, editable assumptions and calculation schedules on distinct sheets.
   Keep source history and required sensitivity work clearly identifiable.
   For example, use Overview / Drivers / Model, with linked History or
   Sensitivity sheets where the task needs them. Adapt names and coverage to
   the request; this is a functional example, not a required tab count.
4. Use a single-sheet model for a straightforward task only when its results,
   inputs, workings and explanations remain distinct and readable. If they
   compete for space or make review difficult, separate their purposes into
   sheets instead of shrinking text, crowding blocks or omitting context.
5. Link summary values to the model with formulas; reference assumptions
   rather than duplicating them in calculation areas. Keep details and source
   evidence traceable. Include the scenarios, sensitivities and explanations
   needed to answer the request, without adding unrelated analyses or an
   unrequested full model.

## Apply the fixed green theme

Unless the supplied style overrides it, use this palette across financial
report/model sheets; do not choose a different accent for each workbook.

Reuse `report_band` and `table_header` from the existing
[authoring primitives](../implementation/authoring.md) for green title/section
bands and gray label headers; their code owns exact colors, font sizes and row
heights. For chart accents reuse `BANDS["title"][0]`; period/baseline dividers may
use light gray `#E7E5E4`. Direct library calls are normally shortest. The optional
`python3 "$OFFICE" style --help` discovers the equivalent explicit-plan CLI;
a JSON plan is **not required** for every workbook or authoring task.

Use green bands to introduce sections and gray rows to identify table columns;
keep these levels visually distinct. Neutral header text applies to labels,
not editable inputs or formula outputs that happen to sit in a header row.
Use white (`#FFFFFF`) for data grids. Theme fills and chart accents must not
override the font roles below or imply positive/negative performance.

## Apply financial font roles

Use this precedence for data cells when no supplied convention overrides it:

Assign `style_value(cell, role=..., kind=...)` after populating each affected
cell; it applies existing font colors and display formats together. Select roles
semantically: `input` for editable hardcodes (numeric, text, date or selectors),
`external` for formulas depending on other files, `cross_sheet` for same-workbook
sheet dependencies, `same_sheet` for local formulas, and `source`/`label` for
retained records/text. External dependencies take precedence and must be disclosed.
Resolve named ranges and indirect dependencies before choosing the role; the
helper checks formula-versus-literal state, not dependency correctness. Identify
editable cells in a legend; do not classify every number as an editable assumption.
Use fills for sections, periods or review flags, not instead of font roles.

These are modeling defaults, not accounting standards, edit permissions, or
proof of correctness. Inspect fonts/number formats, not copied style indices.

## Space new report and model sheets

Apply these defaults to new reader-facing layouts, not raw-data-only exports:

- Leave two blank rows above the main title. Leave one blank row after the
  title band and one before the first content block; keep any subtitle and
  unit notation together between them. Share a spacer when boundaries coincide.
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
  Inspect both the worksheet and exported pages for crowded or excessive gaps.

## Make the report readable

- State currency and scale near the numbers. Use the supplied currency rather
  than inheriting the starter template's dollar symbol. Keep comparable values
  at consistent precision; use parentheses for negative amounts by default.
- Display rates as percentages, storing `0.05` for 5%. Distinguish percentage
  change from percentage-point change. Keep years ungrouped (`2026`, not
  `2,026`). Do not disguise missing evidence as a zero; use a dash for zero
  amounts only where the legend makes that meaning clear.
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
- Make printing/export usable when relevant: call the existing `report_page`
  primitive with the actual report area/direction for one-page-wide fit and
  unrestricted height, then inspect the export. It cannot choose readable column
  widths or page breaks. Do not impose print layout on a raw-data-only export.

## Review the financial work, not only the file

Check the applicable items before delivery and correct any discrepancy:

- Summary and scenario results reconcile to detail and supplied inputs. Sum
  period flows, but do not sum stock balances. Operating margin is operating
  income divided by revenue; for a quarter, divide the quarter's total operating
  income by its total revenue, not the simple average of monthly percentages.
- Period, currency, tax basis, sign, and unit assumptions are consistent.
  Distinguish operating income, net income and cash flow as the model requires.
- Adjustable drivers actually propagate. On disposable copies, change a
  material input, recalculate, verify the expected dependencies, then restore
  the baseline. Trace the effect through detail, summary and sensitivity outputs,
  not just the headline total. Do not claim propagation from formula text alone.
- Editable inputs, same-sheet calculations, cross-sheet links, and any external
  dependencies follow the selected legend throughout the affected model.
- Every relevant populated sheet is readable: headings, units, amounts,
  explanations and charts are not clipped, overlapping or illegibly scaled.
- Key conclusions, scope and limitations are easy to locate. Do not report a
  blanket pass when application or visual checks could not be performed.

Use the shared VALIDATE workflow for execution and evidence boundaries. The
bundled style audit is a diagnostic aid, not a replacement for this review.
