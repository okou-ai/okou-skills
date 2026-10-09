# Built-in expressions for upload-time extension

Select and adapt built-in expressions **during extraction after upload**, before the custom template is published. Later generation uses the saved local adaptations; it must not fetch a catalogue and restyle layouts on each run.

## Reviewed catalogue: 52 Data Report layouts

[artifact-layout-catalog.json](artifact-layout-catalog.json) records the immutable repository revision, index path, fragment root, and all 52 IDs. It is selection metadata only, not a copy of upstream HTML, assets, or styles.

Reviewed index:

https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/data-report/authoring-core.md

Selected fragments are at:

`https://github.com/okou-ai/Template-artifact/blob/efbf5f4e6f17728468921c2e9bbe73a8aef760f5/Template-Presentation/data-report/layouts/fragments/<id>.html`

Choose by the expression, not the built-in theme:

| Expression | Example IDs |
| --- | --- |
| Comparison and peer prose | `comparison-ruled`, `comparison`, `two-column`, `three-column` |
| Process and chronology | `process-steps`, `timeline`, `roadmap` |
| Indicators and decisions | `kpi-grid`, `stat-highlight`, `scorecard`, `executive-summary`, `risk-recommendations` |
| Records and detail | `table`, `detail-summary`, `methods-definitions`, `appendix-index` |
| Trends and relationships | `line-chart`, `area-chart`, `stacked-bar`, `scatter-plot`, `waterfall`, `funnel`, `heatmap-matrix` |
| Images and supporting material | `image-evidence`, `image-grid`, `team`, `quote-cards` |

Read the selectable-ID section of the index and only chosen fragments. The catalogue's own identity, fonts, colors, safe areas, motifs, image restrictions, minimum sizes, authoring flow, and QA shortcuts do **not** become custom-template rules. Keep the source design authoritative. A layout's existence is an expression option, not a requirement to invent data, images, people, or quotes.

Template-artifact is private. Use the extraction run's authorised GitHub connector/access; do not claim these URLs are public or ask later generation to authenticate. With an available authenticated `gh`, a selected fragment can be inspected using the exact revision:

```bash
gh api 'repos/okou-ai/Template-artifact/contents/Template-Presentation/data-report/layouts/fragments/process-steps.html?ref=efbf5f4e6f17728468921c2e9bbe73a8aef760f5' \
  --jq '.content' | base64 --decode
```

Use one revision for all chosen fragments and keep it in each adaptation's provenance. Updating the catalogue requires checking the new ID/path set and selected structures, not replacing the pin with `main`. Do not vendor private themed implementation files into this public skill repository.

## Public neutral fallback

When the authorised catalogue is unavailable or a neutral structure is sufficient, the six-layout pilot is available at:

https://github.com/okou-ai/okou-skills/blob/1004a653cdfcef8881a28f8735f93ab01e26d37c/presentation-layouts/references/catalog.md

It offers KPI grid, table, two-column narrative, comparison, four-step process, and image/text. Fetch selected fragments, geometry, [token contract](../../../presentation-layouts/references/token-contract.md), and any needed binding/fitting tools from that same revision, or use their matching local copies. The pilot is not a 40+ layout catalogue or a theme. Failed access leaves a disclosed gap or a source-styled custom composition; do not retry repeatedly or silently claim broader coverage.

## Adapt once, save, reuse

Follow [layout-reuse.md](layout-reuse.md): identify useful gaps, select complementary IDs, reuse the closest source layout/components, and adapt the expression to its typography and framing. Inspect inline styles as well as the outer structure. Validate each adaptation with source fonts and representative replacement content, compare it visually with source pages, then save it in `layouts/extended/` and `layouts/extended-index.json`.

Save only selected, validated, source-styled adaptations and their necessary local resources. Do not copy the entire 52-layout catalogue into a custom package or import upstream shells, palettes, decoration, default type scales, example facts, or QA policies. Temporary test decks stay outside the package; reusable adapted layouts stay inside it.

The generated package instructions point to the local source/extension indexes. Preserve selected upstream repository, exact commit, fragment path, source-style basis, inferred changes, capacity/test scope, and validation outcome as provenance. External links are provenance only; ordinary generation, viewing, QA, and export must work without GitHub access.

## PRs reviewed for this contract

- [Template-artifact #76](https://github.com/okou-ai/Template-artifact/pull/76) demonstrates source-first selection and source-styled adaptation of Data Report structures. It is a draft reference, not a production dependency; no 9px floor or Okou Brand skin is inherited.
- [Template-artifact #74](https://github.com/okou-ai/Template-artifact/pull/74) contains a separate native PPTX Data Report experiment. Do not mix its engine with this HTML package or claim that HTML layout reuse implements native source-PPTX editing.
