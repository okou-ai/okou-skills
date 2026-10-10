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

The generated `SKILL.md` is the executable authoring runbook, not a short style
summary. It must give a numbered, end-to-end sequence that a new author can follow
without guessing. For every stage, name the input files, the action, the output or
checkpoint, and what to do when the check fails. Include these stages in this order:

1. **Preflight:** confirm the requested audience, goal, language, page-count/range
   and delivery format; preserve the user's requested language. Run
   `node tools/verify-package.mjs --package <template-dir>`. Read `design-system.md`,
   `layouts/README.md`, `layouts/source-index.json`, source-specific QA findings,
   and `references/qa.md` before building.
2. **Plan content:** make a page-by-page outline with one takeaway, its supporting
   user-provided evidence/data, and a proposed source layout for each slide. Resolve
   missing material facts or flag them; do not invent claims or create slides solely
   to fill an arbitrary count.
3. **Map layouts:** match each planned page to the source index's `id`, source page,
   regions and capacity. Prefer an original composition. Explain how to use any
   language-specific derivatives when present. Treat capacities as guidance, not
   guarantees; route unsupported relationships to a selected neutral fragment.
4. **Create a working deck:** explicitly distinguish the archived `layouts/_shell.html`
   and `layouts/source/` from the new deliverable. Copy the package to a separate
   working directory (or preserve the equivalent relative asset tree), then assemble
   only planned pages there. Never edit the stored package, source fragments, original
   upload or library files. Preserve CSS, fonts, assets, runtime and navigation.
5. **Populate and adapt:** specify how to copy the mapped HTML fragments, replace all
   sample content, retain editable HTML/CSS/SVG and source classes, keep source chrome
   and image crops, and modify only the working copy. If no source composition fits,
   select from `library/references/catalog.md`; inspect only selected fragments and
   copy only their needed geometry rules. Reuse source CSS classes/declarations and
   measured spacing, column ratios and crop. Do not apply `geometry.css` globally or
   to preserved source layouts. Record inferred adaptations.
6. **Fit text:** retain disjoint title/body `data-fit-region` hooks and run the bundled
   fitter. Enforce the fixed 10px logical-canvas floor. If content still does not fit,
   change composition or split the page; never hide/crop text or scale the canvas.
7. **Run mechanical QA:** give the exact `tools/qa.mjs` command with the planned page
   count and separate report/prepared output paths. Fix every hard failure and rerun;
   state which statuses permit visual review versus delivery. QA must examine the
   completed deck, not only the archived source shell.
8. **Review, export and deliver:** render the exact prepared HTML, compare all output
   pages with source evidence, and separately review typography, colour pairs,
   components, chrome, safe areas, crops, assets and navigation. If PPTX is requested,
   convert that prepared HTML with `okou presentation convert --verify`, render the
   actual PPTX and inspect the roundtrip; text coverage alone is not visual QA. Follow
   the delivery format requested by the user; if none is specified, deliver both a
   hosted HTML deck and a PPTX. Explain how to create a minimal host directory with
   `index.html` and only the required styles/assets while preserving relative paths;
   never publish the archived source shell/package as the finished deck. Give the
   requested deliverables and a short QA/result summary.

The generated runbook must include executable examples with the package's actual
paths: copy to a fresh working directory; verify the package; run final QA with
`--expected-pages`, `--report` and `--prepared`; render the prepared HTML; optionally
convert and render PPTX; and host a minimal HTML site. Show how the hosted `index.html`,
HTML deck, stylesheet and required assets are arranged so relative URLs still resolve.
For each command, state its expected success result and the fix/retry path when it fails.
Do not leave angle-bracket placeholders unexplained or refer to tools/config files that
the package does not contain.

The generated `layouts/README.md` must be a quick start that links to this runbook,
explains the package paths and distinguishes the original-page archive from the
working output. Both documents must list source-specific known exceptions and tell
the author to fix them in the working copy, not silently copy them unchanged. Avoid
vague directions such as “preserve the style” unless the package names the source
files/classes/rules to inspect.

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
