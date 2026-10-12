---
name: presentation-extract-template
description: Extract source style and editable HTML layouts from HTML decks (files, directories or URLs), PPTX, PPT, PDF or slide images, then save a reusable Custom Template.
---

# Extract a presentation template

Preserve the original source and save its style, layouts and assets as a reusable
HTML package. **Extraction uses package checks; deck QA and targeted visual review are
for later generation.** Rebuild samples only when requested, within that scope.
Write package instructions in English; preserve source content and the requested
presentation language.

| Files in this guide | Stage | Included in the saved template |
| --- | --- | --- |
| This `SKILL.md`, `references/extract/` | Extract and record the source | No |
| `references/generate/` | Generate, check and deliver new decks | Yes, at the same paths |
| `scripts/source-derivatives.py`, `scripts/install-qa.mjs`, `tools/verify-package.mjs` | Prepare source files, assemble and check the package | No |

The installer copies the generation guides and runtime by an explicit file list.
The package's own `SKILL.md` is its generation entrypoint.

## 1. Inspect the source

Create ordered page images to inspect the original layouts, typography, colours
and image crops. These captures are the visual reference for extraction and the
saved template's source preview. Keep the original for structure and style metadata.

Use a new `<work-dir>` beside the template package. All commands below use fixed
subdirectories: `source-pages/` for original pages, `previews/` for contact sheets
and review images, and `upload/` for the upload PDF.

Reuse existing ordered captures or supplied slide images at
`<work-dir>/source-pages/page-001.png`, etc. Otherwise, render once:

```bash
okou presentation screenshot --input <source.ppt|source.pptx|source.pdf|source.html|html-dir|url> --out <work-dir>/source-pages
```

When a contact sheet helps inspection, the supplied helper writes it directly to
`<work-dir>/previews/` and returns its paths. It installs Pillow only if needed:

```bash
python3 scripts/source-derivatives.py --work-dir <work-dir> --contact-sheet
```

For HTML, use `--slides "<slide-selector>"` when the source uses a different slide
selector from `.deck > .slide`; use `--slides none` for one page per HTML file.
Inspect the DOM, computed CSS, SVG and assets directly. Reuse editable source
elements and copy their required resources into the package with local paths.
Record the original entry file or URL in `design-system.md`.

Inspect every page. Record the filename, aspect ratio, page count, page roles and
recurring structures. Check typography against source metadata and label visual
estimates as inferred. Archive original-source captures, never reconstruction images.

## 2. Record the design system

In `design-system.md`, record typography, foreground/background colours, spacing,
safe areas, borders, image crops, required chrome and reusable backgrounds/decorations.
Distinguish source observations from inferred adaptations, including unit conversion
and aspect-ratio mapping to 16:9.

Use [typography.md](references/extract/typography.md) for source font mapping and
[layout-inventory.md](references/extract/layout-inventory.md) for source coverage
and reusable background recipes.

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
  tools/                    # source configuration and generation QA
  references/generate/      # generation-only guidance
```

Cover every source page in the index; preserve distinct compositions and background
variants. Keep text, shapes, tables and ordinary charts editable in HTML/CSS/SVG.
Use package-relative assets and `.deck > .slide`, one `.stage` and a `.fit` root per
slide, with disjoint `data-fit-region` measurement areas that share one page-wide scale.

`layouts/_shell.html` is the shared HTML document with one `.deck` insertion point.
Its `.deck` can be empty or retain source examples; no need to assemble every source
page in it. Complete source-page coverage belongs in `source-index.json`. Source fragments
use paths relative to `layouts/`, where they are inserted into the shell.

Write `tools/qa-config.json` with source-derived safe areas, required chrome and
approved font fallbacks; follow [qa-config.md](references/extract/qa-config.md).
Use the [runtime hooks](references/generate/runtime-contract.md) when creating
the source HTML, so later generation can reuse it directly.
Then run from this guide's directory:

```bash
node scripts/install-qa.mjs --package <template-slug>
```

The installer supplies the library, tools, references and shared runtime, including
four-arrow navigation. Keep neutral library layouts separate from the source index;
adapt only selected layouts during later generation.

Write the package's `SKILL.md` with its template identity, source/language caveats,
links to `design-system.md` and `layouts/source-index.json`, and a Markdown link to
`references/generate/workflow.md`. That supplied [workflow](references/generate/workflow.md)
contains the generation steps and routes to the other guides; no need to duplicate
them. Keep `layouts/README.md` a short path map linking back to the package's `SKILL.md`.
When refreshing an older package, update its entrypoint links to `references/generate/`.

## 4. Check the package

From this guide's directory, check generation guidance and links, source coverage,
source QA configuration, library links, capture count and local paths. The verifier
also rejects extra entries in the capture directory and extraction references or
helpers included in the saved package:

```bash
node tools/verify-package.mjs \
  --package <template-slug> --source-pages <work-dir>/source-pages
```

Only for a specific reconstruction risk, compare one or two unchanged compositions
with their source captures, using `--out <work-dir>/previews/reconstruction` for
any check screenshots.

## 5. Save the Custom Template

After the package check passes, prepare the upload source.

The upload accepts `.ppt`, `.pptx` or `.pdf` as `--source`. Use the original when
it is one of these formats. For HTML or image decks, create the upload PDF directly
at `<work-dir>/upload/source.pdf`:

```bash
python3 scripts/source-derivatives.py --work-dir <work-dir> --pdf
```

The helper reads only original page images. Its `--contact-sheet` and `--pdf` flags
can be combined when both outputs are needed. Record this conversion
and the original file or URL in `design-system.md`; the package retains the
editable layouts and assets. No need to export or render the reconstructed package
for this upload.

```bash
okou user-template publish --kind presentation --title "<template name>" \
  --source <original.ppt|original.pptx|original.pdf|work-dir/upload/source.pdf> \
  --pages <work-dir>/source-pages \
  --package <template-slug>
```

Confirm successful saving and retain any returned template reference; if publishing
fails, report that the template was not saved.
