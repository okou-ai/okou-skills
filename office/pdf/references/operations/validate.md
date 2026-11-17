# Validate and deliver by operation

This is the single PDF acceptance checklist. Select only the applicable operation
and used features; do not repeat it in design/content guides. Record the exact
output checked, checks executed and unavailable/unexecuted checks. Script success
alone is not content, font, visual or standards validation.

## Read-only form inspection

Check that the input opened and the reported field names/types/options answer
the request. Stop with findings. Do not generate a copy, run authoring/Chromium
checks, or require page-image review for a field-inventory-only request.

## FILL

- Confirm every requested field exists and its supplied value is valid for the
  observed type/choices; resolve validation errors, unknown names or omissions.
- Reopen the exact output and compare each requested stored value against the
  request. Preserve the source and check unchanged page count/order.
- Render/open the affected field widgets/pages and inspect their actual visible
  values, checkbox/radio states, clipping and font/glyph appearance. Inspect
  related widgets of the same field, not every unrelated authoring feature.
  Expand review if changes show broader effects.
- State which viewer/renderer was checked: `/NeedAppearances` and correct stored
  values do not prove that every PDF reader paints widgets correctly. A storage-
  only check is not a viewer pass. No cover/body browser setup is required.

## CREATE / REFORMAT

Reopen the exact completed PDF; verify a new, readable, nonempty output, page
count/order and requested content/values. For REFORMAT compare against the source
for omissions, changed structure and lost assets; PDF text parsing cannot prove
layout fidelity. For Word/PDF pairs verify that PDF came from the authored DOCX.

Render and inspect actual output pages, not just extracted text or token values.
Use the platform page renderer for presentations; for ordinary PDFs, one option is:

```bash
mkdir -p preview
pdftoppm -png -r 120 output.pdf preview/page
```

Review page sequence, dimensions, margins, readable type, overlaps/clipping,
headings, page numbers and requested cover treatment. Verify actual fonts/glyphs
(including CJK and web-font fallback), colors/contrast and explicit user styles.
For a named manuscript additionally check its exact required typography, spacing,
pagination and citation rules in the selected capable route; disclose unsupported
or unverified constraints. Do not claim unsupported APA/IEEE compliance.

### Feature-specific rendering QA

Apply only rows for delivered features, reusing the same page review and source
comparison. Text extraction cannot verify rasterized math/charts/diagrams.

| Feature | Check in actual rendered output |
|---|---|
| Headings / lists / tables | Hierarchy, list resets, all rows/cells, source values, widths, legibility, no clipping/stranded headings |
| Math | Symbols/glyphs and formula against source, label/caption visibility, no code-style fallback |
| Charts | Source categories/values, units/axes/legend, chart type, readable labels; no placeholder |
| Figures / captions | Correct asset/aspect ratio, no missing-image text, shared numbering and in-text reference sequence |
| Bibliography | Cited IDs resolve to supplied references, intended consistent style, no invented sources, hanging indents/heading suppression |
| Code | Exact whitespace/indentation, language label, all lines visible, no overflow; no syntax highlighting expected |
| Flowcharts | All nodes/edges/labels, arrow direction/branches/back-edges, legibility, no clipping/placeholder |

After a repair, recheck affected content/pages and any changed pagination or
numbering; reuse unaffected evidence only when it still describes the exact
output. Deliver only requested formats and report material limitations.
