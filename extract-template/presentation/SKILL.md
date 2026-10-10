---
name: presentation-extract-template
description: Extract and save an editable HTML presentation template from PPTX, PPT, PDF or slide images. Preserve source style and compositions, bundle local layouts and future-generation QA, and use lightweight package checks during extraction.
---

# Extract a presentation template

The uploaded source defines style; the reusable output remains HTML. Preserve the
original file unchanged. Upload analysis saves source style and source layouts;
**generation** selectively adapts local reference layouts when originals do not fit.
No private repository, external layout catalogue or GitHub credential is required.

This guide separates extraction from later deck generation. Extraction saves the
source, style, layouts, assets, index and authoring guidance. Its five-step authoring
workflow is written into the package for future PPT creation; do not run that workflow
or build a finished sample deck as part of extraction.

Write all authoring/generation prompts and guidance in English, including the
user package's SKILL.md, READMEs, design-system instructions and references.
Preserve original quoted content, font-family names and the user's requested
presentation language; English guidance does not mean translating the source deck.

## 1. Inspect every source page

Render PPT/PPTX/PDF in order:

```bash
okou presentation screenshot --input <source.ppt|source.pptx|source.pdf> --out <source-pages-dir>
```

Record filename, original canvas ratio, page count, page roles and recurring
structures. Corroborate rendered typography with authoring-file metadata; keep
aspect adaptation and source-to-HTML units explicit. Label unavailable evidence
and visual estimates as inferred. Never package reconstructed images as originals.
Render the source once for extraction and the ordered source-page archive; do not
rebuild a full deck or compare every rebuilt page during this step.

## 2. Extract the source design system

Record in `design-system.md`:

- Source fonts, effective initial sizes, weights, leading, tracking, mixed runs and
  approved CJK fallbacks. Read [typography-fit.md](references/typography-fit.md):
  the runtime minimum is always **10px**, never the source's minimum font size.
- Foreground/background pairs, chart colours, source content-safe areas, spacing,
  borders, radii, crop rules and source-observed component variants.
- Source-required chrome and reusable background fields/decorations with compatible
  recipes. Read [layout-reuse.md](references/layout-reuse.md).

Keep observed values separate from inferred adaptations and runtime policy. Missing
images or another content type is not a prohibition on adding it during generation.

## 3. Build a self-contained, editable package

```text
<template-slug>/
  SKILL.md                  # source-first generation and final QA instructions
  design-system.md          # source rules, profiles and provenance
  layouts/
    README.md
    source-index.json       # original pages/compositions only
    source/<name>.html
    _shell.html             # canvas, fonts, source chrome, four-arrow navigation
  styles/template.css
  assets/                   # only reusable source assets in use
  library/                  # local Markdown layout table and 54 neutral fragments
  scripts/                  # common measurements and 10px text fitter
  tools/                    # package verifier plus QA for later generated decks
  references/               # portable QA, fitting and reuse instructions
```

Cover every source page in the source index and preserve every distinct source
composition. Consolidate equivalent structures with separate background/profile
variants. Do not adapt all library fragments during upload or include them in the
source index as original compositions.

Use `.deck > .slide` with one `.stage` per slide and a `.fit` content root. Preserve
source geometry on the 16:9 target, and use disjoint `data-fit-region` areas for
independent title/body fitting. Prefer normal flow, Flexbox or Grid; source chrome,
decoration and intentional overlays may use absolute geometry. Text, shapes,
tables and ordinary charts stay editable HTML/CSS/SVG, not full-page screenshots.

Write `tools/qa-config.json` from the actual source: safe areas per layout/profile,
required chrome counts and approved fallbacks. Then run from this guide's directory:

```bash
node scripts/install-qa.mjs --package <template-slug>
```

The installer copies the local library and QA, and inlines the shared runtime once.
It does not import another template's fonts, palette, motifs or picture crop policy.
Use working package-relative asset paths and preserve all four navigation keys.

The generated `SKILL.md` must give a concise five-step authoring path, without
splitting routine work into many substeps or adding separate PPTX-export/delivery
sections:

1. **Determine the outline:** identify the purpose, audience, requested language and
   page count/range; write the main point and supporting content for each page.
2. **Choose a suitable layout:** prefer fitting compositions in `layouts/source-index.json`;
   use a selected fragment from `library/references/catalog.md` only when the source
   layouts do not fit. Mention any language-specific source variants.
3. **Replace content and adapt styling, or rewrite:** work in a separate copy, never
   changing the archived source/package. Replace sample content with supported facts;
   reuse source style. If the selected composition cannot express the outline, choose
   another layout or rewrite that page. Preserve editable content and the 10px floor.
4. **Run QA:** give the package's concise final-QA command with the planned page count.
   Fix hard blockers and rerun before visual review.
5. **Review every page:** render the QA-prepared HTML and check each page against the
   outline and source style. Fix visual problems in the working copy, then rerun QA
   and review the affected deck again.

Keep the author's setup brief: point to `design-system.md`, `layouts/README.md`,
`layouts/source-index.json` and the package's QA guide. Include only the exact QA and
page-render commands needed to follow the five steps. Place source-specific caveats
next to layout selection. Do not add separate steps for PPTX conversion, hosting or
file delivery; those are outside this template-authoring runbook.

The generated `layouts/README.md` should be a short path map linking to `SKILL.md`;
briefly distinguish the original-page archive from the working output. Avoid repeating
the entire workflow there.

The five authoring steps above are future-generation instructions inside the package.
They are not extraction steps. Do not create an outline, rewrite source content, assemble
a finished deck, or run final-deck QA/page-by-page review during extraction. If a user
separately requests a sample rebuild, keep it to the requested sample; do not infer a
full-deck scope or an all-pages comparison.

## 4. Verify the extracted package

Run the lightweight package check after creating the source index, local assets and
package. It verifies required files, source-page coverage, local library links, source
page capture count and package-local resource paths. It does not render or QA a newly
authored deck:

```bash
node <template-slug>/tools/verify-package.mjs \
  --package <template-slug> --source-pages <source-pages-dir>
```

Do not run `<template-slug>/tools/qa.mjs` on the source shell during extraction. That
final QA is for a deck created later by following the package's five-step workflow.
Only when source-to-HTML reconstruction creates a specific fidelity risk, compare one
or two unchanged representative compositions against their original page images. Do
not rebuild the entire presentation or compare every page by default. Keep any small
smoke-check output outside the reusable package.

## 5. Save and verify the Custom Template

After the package check passes, save the original source, ordered source-page images
and complete package together:

```bash
okou presentation-template publish --title "<template name>" \
  --source <source.pptx|normalized-source.pdf> --pages <source-pages-dir> \
  --package <template-slug>
```

Confirm the command exits successfully and record its save confirmation; if it
returns a template reference, retain it. If the command fails, report the template was
not saved.
This save step does not require generating a presentation, running final-deck QA,
merging the repository PR or claiming a production deployment. Convert legacy PPT to
PPTX and normalize image decks to an ordered PDF with provenance only as needed for
the source upload. Never publish reconstruction images as original source pages.
