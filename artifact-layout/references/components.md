# Components

Components take literal, already-authored content. Their placement and styling
are shared across formats; analytical review remains with its owning workflow.

| Type | Required content | Optional content | Vocabulary |
| --- | --- | --- | --- |
| `prose` | `paragraphs` | `title` | Supporting text |
| `heading` | `text` | `level` (2–4) | T01 |
| `standfirst` | `text` | — | T02 |
| `big-number` | `value`, `label` | `unit`, `period`, `note`, `source` | N01 |
| `metric-strip` | `items` with `value`, `label` | item `unit`, `period`, `delta`, `source` | N02 |
| `change-indicator` | text `value`, `label`, `comparison`, `direction` | `title`, `source` | N03 |
| `target-comparison` | `label`, numeric `actual`, `target`, `maximum` | `title`, `targetLabel`, `unit`, `period`, `source` | N04 |
| `metric-sparkline` | text `value`, `label`, `period`, numeric `values` | `unit`, `note`, `source` | N05 |
| `progress` | `label`, numeric `value`, `total` | `title`, `unit`, `period`, `source` | N06 |
| `callout` | `text` | `title`, `source` | T05, T07 |
| `takeaways` | `items` | `title` | T06 |
| `numbered-list` | string `items` | `title`, `source` | T08 |
| `pull-quote` | `text` | `attribution`, `source` | T03, T04 |
| `image-text` | `image`, `alt`, `paragraphs` | `title`, `caption`, `source` | I01 |
| `figure` | `image`, `alt` | `title`, `caption`, `source` | I02, I08 |
| `bar-chart` | `labels`, `values` | `title`, `unit`, `period`, `source` | C01 |
| `line-chart` | `labels`, `values` | `title`, `unit`, `period`, `source` | C03 |
| `grouped-bar-chart` | `labels`, named `series` | `title`, `unit`, `period`, `source` | C02 |
| `stacked-bar-chart` | `labels`, named `series` | `title`, `unit`, `period`, `source` | C05 |
| `percent-stacked-bar-chart` | `labels`, named `series` | `title`, `unit`, `period`, `source` | C06 |
| `small-multiples` | `charts` with chart type, labels, values | `title`, `source` | C27 |
| `data-table` | `headers`, `rows` | `title`, `numericColumns`, `source` | B01, B04 |
| `comparison-table` | `headers`, `rows` | `title`, `numericColumns`, `source` | B02 |
| `heatmap-table` | `headers`, `rows`, `heatColumns`, `domain` | `title`, `numericColumns`, `scaleLabel`, `source` | B03 |
| `timeline` | `items` with `label`, `text` | `title`, `source` | D01 |
| `process-steps` | `items` with `label`, `text` | `title`, `source` | D02 |
| `source-note` | `text` | `title` | R06, R07, R09 |

Block-level `span: "all"` gives wide content a full-width placement. In sidebar
sections, `placement: "aside"` gives notes an independent supporting area.

## Placement

Large numbers display values exactly as supplied, alongside their labels and
available context. Metric deltas are supplied text, not inferred calculations.
Use a small related set; repeated large-number cards flatten hierarchy.

Change arrows use the supplied `direction` (`up`, `down`, `flat`), without
interpreting whether a change is favorable. Show the supplied comparison period.
Progress uses `value / total`; targets use a supplied `maximum` for scale and a
separate marker. Both reject values outside their positive scale. Sparklines
keep the supplied metric value, period, and first/last plotted values visible;
their local min/max scale is for compact trend reading, not magnitude comparison.

Quotes preserve wording and attribution. Callouts and takeaways have quieter
backgrounds than headlines. A caption belongs to its figure, and source notes
should remain readable rather than shrink to create space.

Charts include readable labels and units at the placed size. Bars use a zero
baseline, including signed values; line charts expose their scale. Small
multiples share a scale within their group. The renderer places supplied values;
it performs no inference about their significance.

Grouped charts distinguish series by their direct labels and positions as well
as color. Stacks retain visible per-series values and totals. Percentage stacks
normalize each category's supplied positive total to 100% and show both raw
values and shares; negative values and zero-total categories are rejected.
For small multiples, use the supported single-series bar/line panels.

Tables use repeatable headers and right-aligned numeric columns. Let row text
wrap. Native output may split long tables across pages, with headers repeated.
Convert to a full-width section when columns become too narrow.

Heatmap tables color only `heatColumns` against the supplied `[min, max]`
`domain`; exact numeric cells remain editable in Word and visible in all
formats. Values outside that domain keep their numbers and clamp only the
color. Include a `scaleLabel` when the meaning is not obvious. Darker color
means higher value, without an inferred good/bad status.

Asset paths resolve relative to the input JSON. Files are copied into the output
bundle with content-derived names. Use PNG/JPEG for figures shared with Word.
HTML/PDF can also place SVG; use a compatible raster copy for Word when needed.
