# Optional document charts

Use a chart when requested or when it explains a relationship needed by the
document. Add `--charts` to `setup_office.py document` for chart dependencies.
Reuse verified source/calculated values from the document's data.

For a bar, line, scatter, pie/donut, histogram or waterfall, use the
[preset schema](chart-spec.md) when it covers the requested features. Write a
task-specific specification. The renderer shares
the same style and export helper as custom charts. Its default size is 6 × 3.6
inches; set dimensions, colours or font only when the document needs them.

```bash
python3 "$OFFICE_FILES_DIR/scripts/render_chart.py" \
  --spec generated/document/chart.json --output generated/document/chart.png
```

## Custom chart types

Use Matplotlib directly for another chart type, such as a box plot or heatmap,
or features outside the preset schema, such as point annotations, extra axes or
custom scales. Choose this route before rendering when those features are needed.
Import the shared `chart_style` helper; do not copy its
implementation or force data into an unrelated preset. Create any needed
figures, axes, annotations and colour bars inside `chart_theme(...)`, then call
`save_chart(fig, output, font=None)`. The helper applies a covering font to actual
figure text, exports a PNG with warnings, and closes the figure.

For example, a custom box plot can read source-derived samples with a `unit`
and `groups` containing `name` and raw numeric `values`. Adapt the input reader
to the actual source; this is not an additional document configuration format.
Save the authoring code as `generated/document/build_chart.py`:

```python
import json
from pathlib import Path
from chart_style import chart_theme, save_chart
import matplotlib.pyplot as plt

data = json.loads(Path("generated/document/samples.json").read_text(encoding="utf-8"))
with chart_theme(width_inches=6, height_inches=3.6):
    fig, ax = plt.subplots()
    ax.boxplot(
        [group["values"] for group in data["groups"]],
        tick_labels=[group["name"] for group in data["groups"]],
    )
    ax.set_ylabel(data["unit"])
    print(json.dumps(save_chart(fig, "generated/document/chart.png")))
```

```bash
PYTHONPATH="$OFFICE_FILES_DIR/scripts${PYTHONPATH:+:$PYTHONPATH}" \
  python3 generated/document/build_chart.py
```

The context also accepts `palette=None` and `accent=None`; `save_chart` accepts
an installed font family or font file path through `font`. Custom plot geometry,
scales and statistical choices remain part of the authoring code.

## Insert and review

Insert `![Caption](chart.png)` into Markdown. Pandoc renders the image's alt text
as the visible caption, so do not repeat it in a separate paragraph. Add an
internal chart `title` only when it conveys different information.

Add repeated `--resource` arguments to the existing `prepare_document.py`
command for each used chart input: raw data, calculation/custom authoring source,
preset specification and final PNG. Keep these inputs outside `--out`.
Check export warnings, then verify values, units, legends, visible labels and
placement at the chart's final size during the normal document page review.
An exported image still needs that review before document acceptance.
