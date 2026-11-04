# Finance workbooks

Use for financial models, budgets, forecasts, valuations, statements and
financial management reports in Excel, together with common workbook rules.
Preserve supplied templates/house styles; narrow edits do not authorize redesign.

- [Plan](#plan-the-reading-and-calculation-paths)
- [Theme](#apply-the-fixed-green-theme)
- [Font roles](#apply-financial-font-roles)
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

Use this precedence for data cells when no supplied convention overrides it:

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
- Make printing/export usable when relevant: set the actual report area, page
  direction and one-page-wide fit without shrinking an entire long model onto
  one unreadable page. Do not impose a print layout on a raw-data-only export.

## Review the financial work, not only the file

Check the applicable items before delivery and correct any discrepancy:

- Summary and scenario results reconcile to detail and supplied inputs. Sum
  period flows, but do not sum stock balances or average ratios blindly.
- Period, currency, tax basis, sign, and unit assumptions are consistent.
  Distinguish operating income, net income and cash flow as the model requires.
- Adjustable drivers actually propagate. On disposable copies, change a
  material input, recalculate, verify the expected dependencies, then restore
  the baseline. Do not claim propagation from formula text alone.
- Editable inputs, same-sheet calculations, cross-sheet links, and any external
  dependencies follow the selected legend throughout the affected model.
- Every relevant populated sheet is readable: headings, units, amounts,
  explanations and charts are not clipped, overlapping or illegibly scaled.
- Key conclusions, scope and limitations are easy to locate. Do not report a
  blanket pass when application or visual checks could not be performed.

Use the shared VALIDATE workflow for execution and evidence boundaries. The
bundled style audit is a diagnostic aid, not a replacement for this review.
