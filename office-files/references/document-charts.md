# Optional document charts

Use a chart when requested or when it explains a relationship needed by the
document. Add `--charts` to `setup_office.py document` for chart dependencies.

Copy [the chart specification](../assets/chart.json) into the authoring directory.
Use `type: "bar"` or `"line"`, `categories` or numeric `x`, and `series` entries
with `name` and `values`. Reuse verified source/calculated values. Set meaningful
`x_label` and `y_label`; optional appearance keys are `font`, `accent` or `palette`.
The default is 6 × 3.6 inches. Override `width_inches` and `height_inches` only
when needed. Put the caption in Markdown; add an internal `title` only if distinct.

```bash
python3 "$OFFICE_FILES_DIR/scripts/render_chart.py" \
  --spec generated/document/chart.json --output generated/document/chart.png
```

Insert `![Caption](chart.png)` into Markdown and bind the specification using
`prepare_document.py --resource generated/document/chart.json`. Check visible
labels, units and placement during the normal page review. Reuse this renderer
before writing custom drawing code.
