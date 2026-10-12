---
name: artifact-layout
description: Compose report and document artifact layouts with reusable grids, large-number callouts, figures, charts, tables, and coordinated visual themes. Use for new report layouts or a requested redesign, including HTML, Word, and PDF.
---

# Artifact layout

This package is the Okou-maintained layout source for report and document
artifacts. It composes supplied content; research methods, factual review, and
analytical quality belong to their existing workflows.

Honor the user's template, branding, format, language, and requested structure.
For edits, preserve the existing layout unless a redesign is requested. A
visual recipe proposes grids and emphasis, not mandatory business sections.

## Choose and compose

1. Read [selection.md](references/selection.md). Choose a recipe and theme from
   [recipes.json](assets/recipes.json) and [themes.json](assets/themes.json).
   Explicit user choices take priority. These themes are maintained here;
   general Open Design examples are optional references, not this package's
   runtime dependency.
2. Select a few components appropriate to the supplied content. Read
   [components.md](references/components.md) for their fields and placement.
   Search the full bilingual vocabulary only when needed:

   ```bash
   python3 <layout-dir>/scripts/catalog.py --query "big numbers"
   python3 <layout-dir>/scripts/catalog.py --group L
   python3 <layout-dir>/scripts/catalog.py --ids N01 L02 I01
   ```

   The catalog contains 109 core entries and 12 extensions. Rendering coverage
   is explicit: reference-only terms are guidance, not implemented components.
3. Arrange blocks in single-column, flowing two-column, main/sidebar, or modular
   sections. Use full-width blocks for wide figures/tables. Keep related prose,
   figures, captions, and supplied source notes together; let content reflow.
4. Render the requested format using [rendering.md](references/rendering.md).
   The same content model, recipes, and theme tokens drive HTML, editable Word,
   and native Typst PDF. Their pagination may differ. Keep native body/table
   sizes from `office-files`; adjust layout instead of shrinking text.

## Practical commands

Replace `<layout-dir>` with this package's absolute path. Author literal content
using [model.md](references/model.md), or start with one matching file in
[examples](assets/examples).

```bash
python3 <layout-dir>/scripts/render.py report.json --format html --out ./output
python3 <layout-dir>/scripts/render.py report.json --format docx pdf --out ./output \
  --office-dir <office-files-dir>
```

For native formats, use the existing `office-files` setup to install only the
required libraries. The renderer requires no network and performs no research
or scoring. It retains supplied units, periods, citations, and literal text.

Inspect the rendered layout at its actual viewing/print size: column reading
order, figure labels, clipping, wide tables, and downstream pagination. Use the
existing artifact/Office delivery and quality workflows for final delivery.

To review the maintained recipes and themes together:

```bash
python3 <layout-dir>/scripts/preview.py --out ./layout-preview
```

The preview is generated from the same assets and renderer as real artifacts.
Its content is explicitly illustrative. Keep sources and diagnostics outside
the published artifact bundle.
