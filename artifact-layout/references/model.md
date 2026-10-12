# Shared content model

Use one UTF-8 JSON file for all requested formats. Text is literal, not HTML,
Typst code, or Markdown. No block is required merely to make the layout full.

```json
{
  "version": 1,
  "title": "A report title from the task",
  "language": "en",
  "theme": "editorial",
  "recipe": "editorial-research",
  "subtitle": "Optional supplied standfirst",
  "meta": "Optional period, author, or document label",
  "sections": [
    {
      "title": "An existing section title",
      "layout": "two-column",
      "blocks": [
        {"type": "prose", "paragraphs": ["The supplied analysis."]},
        {
          "type": "big-number",
          "value": "42%",
          "label": "The supplied metric name",
          "period": "The supplied period",
          "source": "The supplied source note"
        },
        {
          "type": "data-table",
          "span": "all",
          "headers": ["Item", "Value"],
          "rows": [["A", "42"]],
          "numericColumns": [1]
        }
      ]
    }
  ]
}
```

`theme` and `recipe` must identify maintained assets. A section without `layout`
uses its recipe's default grid. Allowed layouts are `single`, `two-column`,
`sidebar`, and `modular`. `placement: "aside"` is meaningful only in a sidebar.

Chart `values` are finite JSON numbers, and match `labels` in length. All charts
within a small-multiples block share the same domain/scale; include each panel's
labels and title. Table rows match header lengths; `numericColumns` are zero-
based indexes. Metric items retain each item's context. Image paths are local
files relative to this JSON; outputs contain their own bundled copies.

The schema enforces renderable structure, not whether supplied facts are true.
See the three [examples](../assets/examples) for the actual component fields.

The [Top 30 specimen collection](../assets/examples/top30.json) maps each
vocabulary ID to a complete, runnable report model. Extract one ID's object,
save it next to `field-study.png` when it uses that image, and pass it to the
renderer. The preview's downloaded ZIP examples include `report.json` and their images
with relative paths. Extract an example and render its `report.json` directly.

Additional contracts:

- `heading.level` is an HTML heading level from 2 to 4, below the report's H1;
  native output maps these to document heading levels 1 to 3.
- `change-indicator` takes literal string `value` and `comparison`; supply
  `direction: "up"`, `"down"`, or `"flat"`. Arrows do not imply good/bad status.
- `target-comparison` takes finite `actual`, `target`, and positive `maximum`;
  both values lie between zero and maximum.
- `progress` takes finite `value` and positive `total`, with `0 <= value <= total`.
- `metric-sparkline` takes at least two finite `values`, a literal displayed
  `value`, and a supplied `period`. No derived significance or change is added.
- Grouped/stacked charts use `series: [{"name": "A", "values": [1, 2]}]` with
  distinct names and the same number of values as `labels`. Stacks require
  nonnegative values; percentage stacks require a positive total per category.
- `heatmap-table.heatColumns` contains zero-based numeric cell indexes;
  `domain` contains two increasing finite numbers. No row/column color
  normalization is inferred.
- `numbered-list.items` is an ordered string list; `process-steps.items` uses
  objects with supplied `label` and `text`. `timeline` preserves supplied dates
  or phases without inventing an order or date.
