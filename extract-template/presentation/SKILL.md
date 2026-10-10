---
name: presentation-extract-template
description: Extract source style and editable HTML layouts from PPTX, PPT, PDF or slide images, then save a reusable Custom Template.
---

# Extract a presentation template

Preserve the original source and save its style, layouts and assets as a reusable
HTML package. **Extraction uses package checks; deck QA and page-by-page review are
for later generation.** Rebuild samples only when requested, within that scope.
Write package instructions in English; preserve source content and the requested
presentation language.

## 1. Inspect the source

Render the source once, or reuse existing ordered source captures:

```bash
okou presentation screenshot --input <source.ppt|source.pptx|source.pdf> --out <source-pages-dir>
```

Inspect every page. Record the filename, aspect ratio, page count, page roles and
recurring structures. Check typography against source metadata and label visual
estimates as inferred. Archive original-source captures, never reconstruction images.

## 2. Record the design system

In `design-system.md`, record typography, foreground/background colours, spacing,
safe areas, borders, image crops, required chrome and reusable backgrounds/decorations.
Distinguish source observations from inferred adaptations, including unit conversion
and aspect-ratio mapping to 16:9.

Use [typography-fit.md](references/typography-fit.md) for font mapping and the fixed
**10px runtime minimum**; use [layout-reuse.md](references/layout-reuse.md) for source
inventory, background recipes and layout selection.

## 3. Build the editable package

```text
<template-slug>/
  SKILL.md
  design-system.md
  layouts/README.md
  layouts/source-index.json
  layouts/source/<name>.html
  layouts/_shell.html
  styles/template.css
  assets/
  library/                  # supplied neutral layouts and Markdown catalogue
  scripts/                  # supplied fitter and navigation
  tools/                    # package verifier and future-generation QA
  references/               # supplied usage guidance
```

Cover every source page in the index; preserve distinct compositions and background
variants. Keep text, shapes, tables and ordinary charts editable in HTML/CSS/SVG.
Use package-relative assets and `.deck > .slide`, one `.stage` and a `.fit` root per
slide, with disjoint `data-fit-region` areas for independently fitted content.

Write `tools/qa-config.json` with source-derived safe areas, required chrome and
approved font fallbacks; see the [QA source contract](references/qa.md#source-specific-contract).
Then run from this guide's directory:

```bash
node scripts/install-qa.mjs --package <template-slug>
```

The installer supplies the library, tools, references and shared runtime, including
four-arrow navigation. Keep neutral library layouts separate from the source index;
adapt only selected layouts during later generation.

Write these **five steps for future generation** into the package's `SKILL.md`:

1. **Outline:** establish purpose, audience, language, page count and each page's message.
2. **Choose layouts:** prefer `layouts/source-index.json`; use `library/references/catalog.md`
   when source layouts do not fit. Note source-specific and language caveats here.
3. **Replace/adapt or rewrite:** work on a copy, use supported facts and source styling,
   and change layouts or rewrite pages as needed. Retain editable content and the 10px floor.
4. **Run QA:** use the planned page count; fix blockers and rerun.
5. **Review every page:** render the QA-prepared HTML, check against the outline and
   source style, fix problems, then rerun QA and review affected pages.

Link the design system, source index and QA guide; include exact QA and screenshot
commands from [qa.md](references/qa.md). Keep `layouts/README.md` a short path map
linking back to `SKILL.md`. Do not add export, hosting or delivery steps.

## 4. Check the package

Check required files, source coverage, library links, capture count and local paths:

```bash
node <template-slug>/tools/verify-package.mjs \
  --package <template-slug> --source-pages <source-pages-dir>
```

Only for a specific reconstruction risk, compare one or two unchanged compositions
with their source captures. Keep these check outputs outside the package.

## 5. Save the Custom Template

After the package check passes:

```bash
okou presentation-template publish --title "<template name>" \
  --source <source.pptx|normalized-source.pdf> --pages <source-pages-dir> \
  --package <template-slug>
```

Convert legacy PPT to PPTX or image decks to an ordered PDF with provenance only
when needed for upload. Confirm successful saving and retain any returned template
reference; if publishing fails, report that the template was not saved.
