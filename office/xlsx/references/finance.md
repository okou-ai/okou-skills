# Finance workbooks

Read for financial models, budgets, forecasts, valuations, statements, and
financial scenario or management reports in Excel. Apply this layer together
with common workbook rules. A template or explicit house style overrides the
default layout and colors; a narrow edit does not authorize a redesign.

## Plan the reading and calculation paths

1. Fix the audience, decision, reporting periods, currency, scale, and model
   scope from the request and sources. Distinguish actuals, assumptions and
   estimates; retain source locations for material inputs. Do not invent missing
   data, explanations, or accounting policies.
2. Give the reader a clear first reading area: key results, comparison/scenario,
   main drivers, and material limitations. Use a compact block or a summary
   sheet as the task warrants, not a mandatory extra tab or page count.
3. Separate source history, editable assumptions, and calculations in labeled
   blocks or sheets. Link summary values to the model with formulas; link
   assumptions rather than copying them into calculation areas.
4. Keep detail and source evidence traceable without making the reader search
   through raw data to find the requested answer. Include only relevant
   scenarios, sensitivities, and charts; do not build an unrequested full model.

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

These are modeling defaults, not universal accounting standards. Colors do not
prove correctness or provide edit permissions. Do not copy template style
numbers without inspecting their actual font and number-format definitions.

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
  results and subtotals with bold text and appropriate rules; keep explanation
  text distinct from dense numeric rows. Use whitespace and one restrained
  accent rather than arbitrary full-sheet fills or fixed row numbers.
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
