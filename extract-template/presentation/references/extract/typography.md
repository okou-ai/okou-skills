# Extract source typography

Record font families, sizes, weights, leading, tracking and mixed-run relationships
as initial styles. For HTML, read computed CSS, including inherited styles and
transforms. Resolve effective PPTX styles through runs, paragraphs,
placeholders, layouts, masters, themes and existing source autofit, then compare
with rendered source pages. For PDF, reuse the converted HTML's CSS/fonts and
transforms, checking against the original PDF; label missing-font fallbacks and
visual estimates as inferred. See [pdf-source.md](pdf-source.md) for flattened text.
Label image-based estimates as inferred.

Map typography and geometry with the same uniform source-to-canvas transform.
A 24pt font on a 960pt-wide slide becomes 40px on a 1600px-wide canvas. Record
original units, aspect adaptation and scale independently of viewport zoom.

Retain source runs below 11px as evidence; generation QA flags them against the
fixed **11px logical-canvas minimum** for deliberate adaptation. Record any approved
fallback families in the design notes and [QA configuration](qa-config.md).

Use `.fit` for the content area and `data-text-role` for text roles. Extra disjoint
`data-fit-region` hooks are only for genuinely constrained subareas; self-sized
titles/body need no additional fit boundary.
The installer supplies the shared fitter once in the shell; its generation usage
is documented in [typography-fit.md](../generate/typography-fit.md).
No routine reconstruction or export pass is needed to save an extracted template.
