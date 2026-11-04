# Analytical charts in workbooks

Read while planning a new reader-facing analytical report/dashboard, or when
adding or changing charts is within scope. Preserve supplied templates and
house styles. Do not rebuild an existing file merely to add a chart; use the
preservation boundaries in [EDIT](../operations/edit.md).

## Plan the question, not a chart quota

For a new analytical report, consider one or two charts alongside the tables
when they clarify the main comparison or trend. This is a planning heuristic,
not a chart quota. Omit redundant charts when a small table is clearer.
Do not decorate data-only exports, expand narrow edits, or redesign a source
during read-only analysis just to satisfy this heuristic.

Before building, identify the reader's question, the supporting output ranges,
and space for each useful chart. Do not add dashboard tabs solely to meet a
chart count. Verify the source calculation first; for scenario/sensitivity views,
reconcile the baseline with the main model before charting it.

## Choose the form for the message

| Question | Useful starting point | Check |
| --- | --- | --- |
| Compare categories or scenarios | Bar/column chart | Use a zero value-axis baseline; keep units and periods comparable |
| Show change over time | Line chart | Keep chronological order and make irregular time gaps explicit; disclose a restricted axis |
| Explain a change from one total to another | Waterfall | Reconcile the components to the start/end totals |
| Show sensitivity across two drivers | Labeled matrix/heatmap | Keep both driver axes explicit; do not imply probabilities |
| Show composition of a whole | Stacked bar; pie only for a few clear shares | Require a meaningful common total and compatible, nonnegative parts |

Avoid 3-D decoration, unnecessary dual axes and exotic types without an
analytical reason. Label units, periods, scenario and any scale conversion.
Use consistent series colors and ordering across related charts, following the
selected house/scenario style; financial charts use [Finance](../domains/finance.md), not
a separate palette invented for each figure.

## Build from model outputs

Prefer native editable charts for ordinary Excel chart types. Use an image only
when requested or the needed representation is unsuitable for native charts;
keep the supporting data traceable and disclose the editability limitation.

Bind series and categories to worksheet ranges, not pasted results or manually
copied arrays that become stale. Keep headers, periods and series lengths
aligned; exclude totals from a monthly trend unless they are deliberately
separate. Review chart references after row/column insertion or range changes.

For a compatible new workbook using openpyxl, this pattern uses variables from
the worksheet plan; it does not supply data, formulas or fixed cell locations:

```python
from openpyxl.chart import LineChart, Reference

chart = LineChart()
chart.title = question_title
chart.y_axis.title = units
chart.add_data(
    Reference(ws, min_col=first_metric_col, max_col=last_metric_col,
              min_row=header_row, max_row=last_data_row),
    titles_from_data=True,
)
chart.set_categories(Reference(ws, min_col=period_col,
                               min_row=header_row + 1, max_row=last_data_row))
chart.width, chart.height = chart_width_cm, chart_height_cm
ws.add_chart(chart, planned_anchor)
```

Allocate readable chart geometry outside the tables and notes; include it in
the report area and appropriate page setup. Do not shrink labels or split a
chart across pages just to force it into remaining space.

## Verify the saved chart

Use [VALIDATE](../operations/validate.md) for calculation and final-file checks. Recalculate
source formulas before checking plotted values; never invent chart data caches
or substitute zeros for missing results to make a preview look complete.

- Reopen the saved file and check each chart's ranges, category order, series
  names and plotted values against the intended worksheet outputs. A current
  cell cache alone does not prove the chart data cache or rendered plot is current.
- On a disposable copy of an adjustable model, change a relevant driver,
  recalculate, and verify both dependent cells and the plotted series refresh.
  Restore and recheck the baseline selected for delivery.
- Inspect actual previews of every relevant chart-containing sheet. Check axes,
  legends, units, label clipping, overlaps, blank plots and print/export boundaries.
  Revise and rerender within the same authoring attempt, then check the exact
  final file after later saves. If calculation, refresh or rendering is unavailable,
  identify that check as unverified rather than treating a chart object as a pass.

A chart illustrates an analysis; it is not evidence that the model is correct.
Deliver only the requested files, not extra chart images or a dashboard by default.
