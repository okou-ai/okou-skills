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
