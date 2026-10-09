---
name: presentation-extract-template
description: Extract and publish an editable HTML presentation template from PPTX, PPT, PDF or slide images. Preserve source style and original compositions, bundle a local neutral layout library, and validate with automatic 10px-bounded text fitting and source-configured rendered QA.
---

# Extract a presentation template

The uploaded source defines style; the reusable output remains HTML. Preserve the
original file unchanged. Upload analysis saves source style and source layouts;
**generation** selectively adapts local reference layouts when originals do not fit.
No private repository, external layout catalogue or GitHub credential is required.

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
  tools/                    # source QA config, package verifier and final audit
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

The generated `SKILL.md` and `layouts/README.md` must direct later authors to:

1. Read source design rules and `layouts/source-index.json`; copy a fitting source
   composition first without modifying the stored package or original upload.
2. Otherwise choose from the Markdown table `library/references/catalog.md`, then
   read only selected HTML fragments and their needed geometry rules. Copy them
   into the working deck; reuse the user's existing CSS classes/declarations for
   fonts, initial sizes, palette, components, backgrounds, spacing, crop and chrome.
   Adapt column ratios and gaps to observed source geometry, rather than treating
   equal columns, 1em or contain as user defaults. Do not attach geometry.css to
   preserved source layouts or the stored source shell. Read `library/README.md`.
3. Fill real content/data, expand needed repeated groups, and keep text-fitting hooks.
   Do not refetch a catalogue or recreate source analysis for each generation.
4. Automatically fit only overflowing regions, never below 10px. Still-unfit content
   needs a different composition or splitting, not hiding/cropping or canvas scaling.
5. Run final QA with the planned page count, compare new adaptations to source style,
   and capture/export the exact measured working copy. Read [qa.md](references/qa.md).

## 4. Validate representative source rebuilds

Rebuild representative distinct compositions, profiles and background recipes.
Check the source index covers every original page. Run the packaged final commands:

```bash
node <template-slug>/tools/verify-package.mjs --package <template-slug> --source-pages <source-pages-dir>
node <template-slug>/tools/qa.mjs --final <rebuilt.html> \
  --expected-pages <representative-count> --report <qa-report.json> \
  --prepared <rebuilt.ready.html>
okou presentation screenshot --input <rebuilt.ready.html> --out <validation-dir>
```

The prepared file must be a separate working copy beside the assembled HTML.
Compare structure, type, source colour pairs, component styling, decoration,
image crops and safe areas with original page images. A mechanical green status
is not a source-fidelity pass. Keep temporary fixtures/review images outside the
package and outside `source-pages-dir`. Fix shared rules rather than page-by-page
ad hoc CSS. Fonts, images, clipping, the 10px floor, page count and live four-key
navigation must pass; unknown image/gradient contrast needs recorded visual review.

If PPTX is delivered, use `okou presentation convert --verify` on the prepared HTML
and render that actual PPTX for roundtrip review. Text coverage alone does not prove
font, crop or layout fidelity; SVG may rasterise. This is not a native PPTX editor.

## 5. Publish only after both validations pass

```bash
okou presentation-template publish --title "<template name>" \
  --source <source.pptx|normalized-source.pdf> --pages <source-pages-dir> \
  --package <template-slug>
```

Publish the original source, ordered original page images and complete package
including local library/runtime/QA together. Convert legacy PPT to PPTX; normalise
image decks to an ordered PDF with provenance. Never publish reconstruction images
as originals. Completion requires source coverage, source-style review, passing QA,
and a successful publication command. A repository PR is not production registry
publication; report publication or entrypoint-sync blockers without claiming rollout.
