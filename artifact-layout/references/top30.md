# Top 30 report expressions

This selection prioritizes breadth of use, communicative value and composition
for business reports, research and analysis. It is a curated maintenance
priority, not measured frequency or a requirement to place all 30 in a report.
Research conclusions, factual checks and quality scoring remain with the
existing analytical workflow.

The canonical ranking and Chinese selection reasons are in
[top30.json](../assets/top30.json). Query them with `catalog.py --top30`.
Every ID has an executable model in the
[specimen collection](../assets/examples/top30.json), and renders to HTML,
editable Word and independently compiled PDF using the same content.

| Rank | ID | Expression | Renderer |
| --- | --- | --- | --- |
| 1 | T01 | Display headline / typographic hierarchy | `heading` |
| 2 | T02 | Standfirst / deck | `standfirst` |
| 3 | N01 | Big Numbers / standalone numbers / stat callout | `big-number` |
| 4 | N02 | Metric strip / KPI row | `metric-strip` |
| 5 | T06 | Key takeaways / summary box | `takeaways` |
| 6 | C01 | Bar / column chart | `bar-chart` |
| 7 | C03 | Line chart | `line-chart` |
| 8 | B01 | Data table | `data-table` |
| 9 | B02 | Comparison table / comparison matrix | `comparison-table` |
| 10 | L02 | Two-column grid | `two-column` |
| 11 | L03 | Asymmetric two-column / main-content-and-sidebar layout | `sidebar` |
| 12 | L05 | Modular grid | `modular` |
| 13 | T05 | Callout / callout box | `callout` |
| 14 | I01 | Image–text split / side-by-side image and text | `image-text` |
| 15 | I02 | Figure with caption | `figure` |
| 16 | N03 | Delta / change indicator | `change-indicator` |
| 17 | N04 | Target / benchmark comparison | `target-comparison` |
| 18 | N05 | Metric with sparkline | `metric-sparkline` |
| 19 | N06 | Progress / completion indicator | `progress` |
| 20 | C02 | Grouped / clustered bar or column chart | `grouped-bar-chart` |
| 21 | C05 | Stacked bar / column chart | `stacked-bar-chart` |
| 22 | C06 | 100% stacked bar / column chart | `percent-stacked-bar-chart` |
| 23 | C27 | Small multiples / trellis / faceted charts | `small-multiples` |
| 24 | B03 | Heatmap table / conditionally formatted table | `heatmap-table` |
| 25 | D01 | Timeline | `timeline` |
| 26 | D02 | Process diagram / process list | `process-steps` |
| 27 | T08 | Numbered list / icon list | `numbered-list` |
| 28 | T03 | Pull quote | `pull-quote` |
| 29 | L07 | Full-width / column-spanning block | `span-all` |
| 30 | R06 | Footnote / endnote / source line | `source-note` |

Grid IDs configure `section.layout`; L07 configures `block.span: "all"`.
Other IDs identify block types. A layout specimen contains several supplied
blocks to demonstrate actual reading order and placement.

Use [components.md](components.md) for fields and selection considerations,
and [model.md](model.md) for value/scale contracts. `preview.py` generates
all 30 expressions in all four themes, with searchable examples and portable
self-contained model/image ZIP downloads. The images are original and the example data is illustrative.
