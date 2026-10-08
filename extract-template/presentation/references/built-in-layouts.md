# Shared built-in layout references

Built-in layouts are optional structural references for generating new decks in a custom template's design system. Maintain this index centrally; do not bundle the library, this catalogue, or pre-adapted built-in layouts into each custom template package.

## Link from generated package instructions

Include this absolute URL in the generated `SKILL.md` and `layouts/README.md`, together with the source-first, on-demand adaptation rules in [layout-reuse.md](layout-reuse.md):

https://github.com/okou-ai/okou-skills/blob/main/extract-template/presentation/references/built-in-layouts.md

The index is consulted only when a source layout does not fit. Read the selected fragments once per generation run; transfer their structure into the generated deck using the custom styles, shell, and fitter. No reference URL is a render-time dependency. If the index or a fragment is unavailable, continue with source layouts or a documented custom composition.

## Library and catalogues

These links are pinned to `okou-ai/Template-artifact` commit `efbf5f4e6f17728468921c2e9bbe73a8aef760f5`. When updating this index, update and verify catalogue and fragment links together; record the selected commit-pinned URLs in the generated deck's notes.

- [All built-in templates](https://github.com/okou-ai/Template-artifact/tree/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation).
- [Data Report catalogue — 52 layouts](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/data-report/authoring-core.md).
- [Business Data catalogue — 42 layouts](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/business-data/authoring-core.md).

The catalogues help select IDs; their full-theme assembly and identity rules do not replace the custom template's rules when borrowing only a structure. Do not read a full catalogue when a direct link below already covers the slide's purpose.

## Direct references by slide purpose

| Purpose | Fragment links |
| --- | --- |
| KPI and metric grids | [kpi-grid](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/data-report/layouts/fragments/kpi-grid.html), [overview-kpis](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/data-report/layouts/fragments/overview-kpis.html) |
| Tables and scorecards | [table](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/data-report/layouts/fragments/table.html), [scorecard](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/data-report/layouts/fragments/scorecard.html) |
| Parallel columns | [two-column](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/data-report/layouts/fragments/two-column.html), [three-column](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/data-report/layouts/fragments/three-column.html) |
| Comparisons and trade-offs | [comparison](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/data-report/layouts/fragments/comparison.html), [pros-cons](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/business-data/layouts/fragments/pros-cons.html) |
| Process and architecture | [process-steps](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/data-report/layouts/fragments/process-steps.html), [architecture](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/business-data/layouts/fragments/architecture.html) |
| Timelines and roadmaps | [timeline](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/data-report/layouts/fragments/timeline.html), [roadmap](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/data-report/layouts/fragments/roadmap.html) |
| Funnels | [funnel](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/data-report/layouts/fragments/funnel.html) |
| Magnitude and ranking | [chart-bar](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/data-report/layouts/fragments/chart-bar.html), [bar-ranking](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/data-report/layouts/fragments/bar-ranking.html) |
| Time-series trends | [line-chart](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/data-report/layouts/fragments/line-chart.html), [area-chart](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/data-report/layouts/fragments/area-chart.html) |
| Shares and contributions | [stacked-bar](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/data-report/layouts/fragments/stacked-bar.html), [waterfall](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/data-report/layouts/fragments/waterfall.html) |
| Images and evidence | [image-grid](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/data-report/layouts/fragments/image-grid.html), [image-evidence](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/data-report/layouts/fragments/image-evidence.html) |
| Summaries and longer prose | [executive-summary](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/data-report/layouts/fragments/executive-summary.html), [longform](https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/business-data/layouts/fragments/longform.html) |

Choose by content and density, not by the number of available layouts. Preserve the source template's fonts, source-size defaults, colors, components, chrome, and backgrounds. Measure capacity with those fonts and use the custom fitter before QA; the referenced theme's capacity and minimum font sizes are not transferable.
