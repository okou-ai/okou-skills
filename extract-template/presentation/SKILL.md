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
| Source helpers in `scripts/` and `tools/verify-package.mjs` | Prepare source files, assemble and check the package | No |

The installer copies the generation guides and runtime by an explicit file list.
The package's own `SKILL.md` is its generation entrypoint.

## 1. Inspect the source

| Input | Extraction route |
| --- | --- |
| HTML file, directory or URL | [Inventory the HTML](references/extract/html-source.md) and reuse its fragments, CSS and assets. |
| PDF deck | [Prepare, inspect and assemble](references/extract/pdf-source.md) through the HTML extraction contract; after `PACKAGE_VALID`, continue at step 5. |
| PPTX / PPT | Read available structure/style metadata together with the rendered pages. |
| Slide images | Infer layouts and styling from the supplied pages. |

Keep the original as evidence. Source parsing/conversion and the independent page
capture can run together.

Use a new `<work-dir>` beside the template package. All commands below use fixed
subdirectories: `source-pages/` for original pages, `previews/` for contact sheets
and review images, and `upload/` for the upload PDF.

Reuse existing ordered captures or supplied slide images at
`<work-dir>/source-pages/page-001.png`, etc. Otherwise, render once:

```bash
okou presentation screenshot --input <source.ppt|source.pptx|source.pdf|source.html|html-dir|url> --out <work-dir>/source-pages
```

Review every page through contact sheets; open individual captures only for details
that are unclear at that size. The helper installs Pillow if needed and writes previews
to their own directory. For HTML/images without an original PDF, create the upload
PDF in the same pass:

```bash
python3 scripts/source-derivatives.py --work-dir <work-dir> --contact-sheet --pdf
```

For PPT/PPTX/PDF, omit `--pdf`: the original already supplies the upload source.
For HTML, use `--slides "<slide-selector>"` when the source uses a different slide
selector from `.deck > .slide`; use `--slides none` for one page per HTML file.
Read computed CSS once per distinct style, including inherited styles and SVG.
Record the original entry file or URL in `design-system.md`.

Record the filename, aspect ratio, page count, page roles and
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

Create the source index and fragments in one batch; preserve every distinct composition
and background variant. Equivalent structures may share a layout with explicit source-page
coverage. Keep text, shapes, tables and ordinary charts editable in HTML/CSS/SVG.
Use package-relative assets and `.deck > .slide > .stage`, with a `.fit` root per
slide. Extra `data-fit-region` hooks are only for genuinely constrained subareas;
ordinary flow text needs no extra measurement boundary. All content shares one scale.

`layouts/_shell.html` is the shared HTML document with one `.deck` insertion point.
The installer supplies a pure-black viewer surround with centered, proportional
canvas scaling. Keep source dimensions, backgrounds and styling on `.stage` and
inside it; no separate viewport or resize script is needed.
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
the viewport frame and four-arrow navigation. Keep neutral library layouts separate
from the source index; adapt only selected layouts during later generation.

Write the package's `SKILL.md` with its template identity, source/language caveats,
links to `design-system.md` and `layouts/source-index.json`, and a Markdown link to
`references/generate/workflow.md`. That supplied [workflow](references/generate/workflow.md)
contains the generation steps and routes to the other guides; no need to duplicate
them. Keep `layouts/README.md` a short path map linking back to the package's `SKILL.md`.
When refreshing an older package, update its entrypoint links to `references/generate/`.
Keep content QA separate from platform publication: do not tell future runs to stop
at `READY_TO_PUBLISH` or prohibit the platform-required cover capture and inspection.

## 4. Check the package

From this guide's directory, run the package verifier. It checks slide/stage/fit
structure, generation links, source coverage/configuration, library resources and
capture inventory, and rejects extraction files mixed into the saved package:

```bash
node tools/verify-package.mjs \
  --package <template-slug> --source-pages <work-dir>/source-pages
```

No generation QA, interaction pass or runtime test-suite run is needed during extraction.
Only for a specific reconstruction risk, compare one or two unchanged compositions
with their source captures, using `--out <work-dir>/previews/reconstruction` for
any check screenshots.

## 5. Save the Custom Template

After the package check passes, prepare the upload source.

Use the original `.ppt`, `.pptx` or `.pdf` as `--source`. For HTML/images, reuse
`<work-dir>/upload/source.pdf` from step 1. Record this conversion in `design-system.md`;
the package retains editable layouts and assets. No reconstructed export is needed.

```bash
okou user-template publish --kind presentation --title "<template name>" \
  --source <original.ppt|original.pptx|original.pdf|work-dir/upload/source.pdf> \
  --pages <work-dir>/source-pages \
  --package <template-slug>
```

Confirm successful saving and retain any returned template reference; if publishing
fails, report that the template was not saved.
