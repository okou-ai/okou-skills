# Public shared structure catalogue · pilot v1

Canonical public index: https://github.com/okou-ai/okou-skills/blob/main/presentation-layouts/references/catalog.md

Resolve the guide/library revision to a full commit SHA once per authoring run, then read this index and selected files at that same SHA. During PR validation, use the PR's exact head, not `main`. Relative links below retain that revision when the index is opened at a commit-pinned GitHub URL. A deployed extracted template should record its tested absolute commit-pinned index URL; the canonical URL is discovery, not a render dependency.

| Purpose | Fragment | Roles | Structural capacity hint |
| --- | --- | --- | --- |
| KPI | [kpi-grid.html](../layouts/kpi-grid.html) | title, metric-value, metric-label, caption | 2-8 concise metrics; choose 2/3/4 columns via `--okp-layout-kpi-grid-columns` |
| Table | [table.html](../layouts/table.html) | title, table-header, table-cell, caption | 3-6 columns and 3-8 short rows; split dense data |
| Two narratives | [two-column.html](../layouts/two-column.html) | title, heading, body | Paired 1:1 columns, separate text-fit regions |
| Comparison | [comparison.html](../layouts/comparison.html) | title, heading, body | Two comparable options; user-defined card skin |
| Process | [process.html](../layouts/process.html) | title, label, body | Four horizontal steps and meaningful connectors |
| Image + narrative | [image-text.html](../layouts/image-text.html) | title, heading, body, caption | Local meaningful image, contain crop, independent text |

Read only selected fragments plus [shared geometry](../styles/geometry.css) and the relevant [token contract](token-contract.md). [catalog.json](catalog.json) exposes the same IDs, roles, repeated slots and hints for programs. Hints are estimates, not fit guarantees or source-observed capacities.

These fragments were authored as neutral structures. They contain no source data, fonts, palette, brand decoration, theme CSS, shell or private-reference imports. Two-column and comparison deliberately share geometry but differ in semantics and component hooks. No attempt is made to market themed variants as dozens of independent structures.

Prefer the user's existing source layouts. Bind source role sizes, safe areas, surface pairs and components. Materialize repeated slots; put adapted HTML and its provenance in the generated deck, **not** in the reusable template package. Final HTML/CSS/assets/runtime must be self-contained. Never fetch this catalogue or a fragment when viewing/exporting the delivered deck.

The first pilot does not include charts, timelines or every table variant. Keep chart series mappings in the user's skin if needed; use a source layout or a documented deck-specific structure rather than importing an unlisted private theme.
