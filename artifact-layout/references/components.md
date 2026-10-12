# Components

Components take literal, already-authored content. Their placement and styling
are shared across formats; analytical review remains with its owning workflow.

| Type | Required content | Optional content | Vocabulary |
| --- | --- | --- | --- |
| `prose` | `paragraphs` | `title` | T01, P02 |
| `big-number` | `value`, `label` | `unit`, `period`, `note`, `source` | N01 |
| `metric-strip` | `items` with `value`, `label` | item `unit`, `period`, `delta`, `source` | N02, N03 |
| `callout` | `text` | `title`, `source` | T05, T07 |
| `takeaways` | `items` | `title` | T06 |
| `pull-quote` | `text` | `attribution`, `source` | T03, T04 |
| `image-text` | `image`, `alt`, `paragraphs` | `title`, `caption`, `source` | I01 |
| `figure` | `image`, `alt` | `title`, `caption`, `source` | I02, I08 |
| `bar-chart` | `labels`, `values` | `title`, `unit`, `period`, `source` | C01 |
| `line-chart` | `labels`, `values` | `title`, `unit`, `period`, `source` | C03 |
| `small-multiples` | `charts` with chart type, labels, values | `title`, `source` | C27 |
| `data-table` | `headers`, `rows` | `title`, `numericColumns`, `source` | B01, B04 |
| `comparison-table` | `headers`, `rows` | `title`, `numericColumns`, `source` | B02 |
| `timeline` | `items` with `label`, `text` | `title`, `source` | D01, D02 |
| `source-note` | `text` | `title` | R06, R07, R09 |

Block-level `span: "all"` gives wide content a full-width placement. In sidebar
sections, `placement: "aside"` gives notes an independent supporting area.

## Placement

Large numbers display values exactly as supplied, alongside their labels and
available context. Metric deltas are supplied text, not inferred calculations.
Use a small related set; repeated large-number cards flatten hierarchy.

Quotes preserve wording and attribution. Callouts and takeaways have quieter
backgrounds than headlines. A caption belongs to its figure, and source notes
should remain readable rather than shrink to create space.

Charts include readable labels and units at the placed size. Bars use a zero
baseline, including signed values; line charts expose their scale. Small
multiples share a scale within their group. The renderer places supplied values;
it performs no inference about their significance.

Tables use repeatable headers and right-aligned numeric columns. Let row text
wrap. Native output may split long tables across pages, with headers repeated.
Convert to a full-width section when columns become too narrow.

Asset paths resolve relative to the input JSON. Files are copied into the output
bundle with content-derived names. Use PNG/JPEG for figures shared with Word.
HTML/PDF can also place SVG; use a compatible raster copy for Word when needed.
