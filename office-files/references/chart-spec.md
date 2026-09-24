# Document chart JSON specification

Use this reference for `scripts/render_chart.py --spec <json> --output <png>`.
Choose a preset whose data model fits the relationship. Use the shared
[custom chart helper](document-charts.md#custom-chart-types) for other Matplotlib
charts; the preset list does not limit the document's chart types.

## Shared fields

| Field | Meaning |
| --- | --- |
| `type` | `bar` (default), `line`, `scatter`, `pie`, `donut`, `histogram` or `waterfall`. |
| `series` | Nonempty array of series objects. Each has a nonempty string `name`; its data fields depend on `type` below. |
| `title` | Optional internal chart title. Use only if distinct from the Markdown caption. |
| `x_label`, `y_label` | Optional axis labels for Cartesian charts; include units where relevant. Not accepted for pie/donut. |
| `width_inches`, `height_inches` | Optional physical size, each from 1 to 30 inches; defaults to 6 × 3.6 inches. Keep labels readable when the document fits the image to its text column. |
| `accent`, `palette` | Optional RGB hex colour or nonempty array of colours, with or without `#`. `accent` changes the default first colour; `palette` replaces the full cycle and takes precedence if both are supplied. |
| `font` | Optional installed font family or font file path. The shared exporter checks coverage of actual figure text, including ticks, legends and annotations. |

Numeric arrays must be nonempty and contain finite numbers, not strings, booleans
or nulls. Category arrays must be nonempty and contain strings; individual labels
may be empty. Use only fields
accepted for the chosen type. All values must come from the task's sources or
verified calculations; examples below illustrate structure, not reusable data.

## Preset data models

| Type | Required data | Additional fields and interpretation |
| --- | --- | --- |
| `bar` | Exactly one of `categories` or numeric `x`; `series: [{"name": ..., "values": [...]}]`. Each series has one value per category/coordinate. | `orientation`: `vertical` (default) or `horizontal`; `stacked`: boolean (default `false`). Signed stacks accumulate positive and negative values separately. Axis labels name the displayed axes; horizontal bars put values on the x axis. |
| `line` | Same coordinate and series shape as bar. | Values are connected in the supplied category/coordinate order. |
| `scatter` | `series: [{"name": ..., "x": [...], "y": [...]}]`; each series has equal-length x/y arrays. | Coordinates belong to each series and may be unordered or repeated. Do not supply top-level `categories` or `x`. |
| `pie`, `donut` | `categories` and exactly one `series: [{"name": ..., "values": [...]}]`; one value per category. | Values must be nonnegative with a positive total. Shares appear in the legend. No top-level `x`, `x_label` or `y_label`. |
| `histogram` | `series: [{"name": ..., "values": [...]}]`, where values are raw samples. | Optional `bins`: positive integer (default `10`) or at least two strictly increasing numeric edges covering all samples. No top-level `categories` or `x`. |
| `waterfall` | `categories` and exactly one `series: [{"name": ..., "values": [...]}]`; one value per category. | Optional `totals`: distinct zero-based category indices marking absolute levels; other values are signed changes. No top-level `x`. |

For bar/line, numeric `x` coordinates must be distinct and strictly ascending.
Do not replace uneven numeric intervals with equally spaced category labels
when spacing carries meaning. A histogram takes observations, not precomputed
bin counts; use bars for existing counts.

A waterfall starts at zero unless index `0` is marked as an opening total. A
marked total after index `0` must equal the accumulated preceding level; it does
not add to that level. Inconsistent totals are rejected. With no `totals`, every
value is a change.

## Examples

Each example is a separate specification. Replace its labels and illustrative
values with source-derived data and run the same renderer command.

A horizontal stacked comparison:

```json
{
  "type": "bar",
  "orientation": "horizontal",
  "stacked": true,
  "categories": ["North", "South"],
  "x_label": "Orders",
  "series": [
    {"name": "New customers", "values": [24, 18]},
    {"name": "Returning customers", "values": [16, 22]}
  ]
}
```

Paired observations with repeated x coordinates:

```json
{
  "type": "scatter",
  "x_label": "Response time (hours)",
  "y_label": "Satisfaction score",
  "series": [{"name": "Responses", "x": [3, 1, 3, 2], "y": [4, 5, 3, 4]}]
}
```

A distribution of raw samples using explicit bin edges:

```json
{
  "type": "histogram",
  "x_label": "Handling time (minutes)",
  "y_label": "Cases",
  "bins": [0, 5, 10, 15],
  "series": [{"name": "Cases", "values": [2, 3, 4, 7, 8, 12, 15]}]
}
```

A reconciliation with opening and closing totals:

```json
{
  "type": "waterfall",
  "categories": ["Opening", "Added", "Removed", "Closing"],
  "y_label": "Accounts",
  "totals": [0, 3],
  "series": [{"name": "Accounts", "values": [100, 30, -20, 110]}]
}
```

Use `![Caption](chart.png)` to insert the image once. See
[insertion and review](document-charts.md#insert-and-review) for resource binding
and final page checks; a successful render is not document acceptance.
