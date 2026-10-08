---
name: presentation-extract-template
description: Extract and publish a reusable HTML presentation template from PPTX, PPT, PDF, image decks, or page screenshots. Preserve the source's typography, layouts, backgrounds, decoration, and brand framing as editable structures and reusable assets.
---

# Extract a presentation template

Turn the reference into a platform-compliant HTML template for new content. The source defines its visual language; the output remains HTML regardless of input format.

## 1. Inspect the source

Preserve the original and inspect every page in order, noting canvas ratio, page count, content types, page roles, and recurring structures. For PPT, PPTX, or PDF, run from this guide's directory:

```bash
node scripts/render-pages.mjs \
  --input <deck.ppt|deck.pptx|deck.pdf> \
  --out <source-pages-dir>
```

This writes ordered source images (`page-001.png`, `page-002.png`, …). Determine design rules from the rendered pages, not file structure alone.

## 2. Extract the design system

Record in `design-system.md`:

- Typography: source sizes by layout and text role, display/body fonts, weights, line heights, spacing, and CJK fallbacks. Record source units, canvas conversion, and whether a value was extracted or inferred; the source sizes are the defaults for new content.
- Color and geometry: foreground/background roles, accents, chart colors, margins, content-safe areas, borders, radii, and image crops.
- Repeated components and chrome: cards, metrics, tables, quotes, image frames, logos, headers, footers, and page markers.
- Background fields and content-independent decorations: reusable elements, source-observed combinations, and allowed adaptations.

Read [references/layout-reuse.md](references/layout-reuse.md) for source inventory, compatible built-in layouts, and background composition. Read [references/typography-fit.md](references/typography-fit.md) for source-size extraction and automatic overflow fitting. Distinguish observed rules from inferred or fallback choices. An absent content type, such as images, is not a prohibition on future use.

## 3. Build the editable package

```text
<template-slug>/
  SKILL.md                 # usage and authoring instructions
  design-system.md         # brand rules, background elements/recipes, asset notes
  layouts/
    README.md              # layout selection and assembly instructions
    source-index.json      # every source page mapped to a preserved layout
    source/<name>.html     # distinct source compositions
    _shell.html            # shared canvas, fonts, chrome, and navigation
  styles/template.css      # shared layout, brand, and component styles
  scripts/fit-text.js       # shared source-size reset, measurement, and bounded fitting
  assets/                  # reusable logos, fonts, textures, and artwork
```

Preserve every distinct source composition and prefer it when new content fits. Group equivalent structures, keeping background variants separate. When no source layout fits, adapt a compatible built-in layout if one is available, or add a documented layout in the same design system. Reuse its structure while applying the source typography, components, and brand rules; packaged layouts are references, not a whitelist.

Use a 16:9 canvas, shared CSS variables/components, and semantic regions for replaceable text, images, and data. Keep title and metric typography separate. Start each text region at its corresponding source size, converted with the layout's canvas scale. Only when rendered content overflows, automatically reduce the affected region's typography to the largest size that fits within its documented readability limit. Keep unaffected regions at their source sizes. Do not impose a universal font size or prohibit shrinking; change the layout or split content when bounded fitting cannot resolve the overflow. Prefer normal flow, Flexbox, or Grid; use absolute positioning for chrome, decoration, and intentional overlays.

Text, shapes, cards, tables, and ordinary charts must remain editable HTML/CSS/SVG. Retain isolated reusable artwork; never substitute a full-page screenshot for an editable layout or package old text/data as decoration.

Document assembly through the shared shell, with working package-relative asset paths. Wire the shared fitter into the shell so it runs after fonts and layout are ready and before the first QA capture or export; a written instruction to shrink text during QA is insufficient. Follow the readiness, reset, bounds, and reporting contract in `references/typography-fit.md`. Support all four navigation keys: `ArrowLeft`/`ArrowUp` go back; `ArrowRight`/`ArrowDown` go forward.

The generated `SKILL.md` and `layouts/README.md` must direct authors to the design system and source index, explain source-first selection, built-in layout adaptation, and background composition, and identify the shared styles, fitter, and assembly steps. Include the source-size defaults, overflow-only shrinking, and unresolved-overflow handling in the generated instructions; do not depend on access to this extraction guide at generation time.

## 4. Validate representative rebuilds

Rebuild representative source pages and background combinations, including documented adaptations. Confirm that the source inventory covers every page. Render the assembled examples:

```bash
npx --yes --package="${CLI_PKG_URL}" okou presentation screenshot \
  --input <rebuilt-deck.html> \
  --out <validation-dir>
```

Compare structure, typography, colors, component styling, decoration placement, and safe areas against the source. Fix shared rules where needed; verify navigation, language fallbacks, and asset loading. Rebuilt images are local validation evidence, not source-page images for publication.

Also validate the fitter with unchanged source content, longer replacement content, CJK/mixed-language text where supported, and content too dense to fit within the documented limit. Confirm that fitting content keeps its source size, actual overflow shrinks automatically before capture, unresolved overflow remains reported, and replacing long content with short content restores source sizes. Inspect affected pages visually for clipping, overlaps, and readability; overflow measurements alone are not visual QA.

## 5. Publish

Publish the source file, ordered original page images, and complete template package together:

```bash
npx --yes --package="${CLI_PKG_URL}" okou presentation-template publish \
  --title "<user-visible template name>" \
  --source <deck.pptx|normalized-source.pdf> \
  --pages <source-pages-dir> \
  --package <template-slug>
```

`--source` accepts PPTX or PDF. Convert legacy PPT to PPTX; for images/screenshots, create a PDF preserving page order and retain input provenance. `--pages` must contain only original source screenshots in filename order, never reconstructed validation images.

Completion requires the editable package, source layout coverage, reusable background elements with composition guidance, source-size typography with working automatic fitting, successful validation, and a successful publication command. Report publication failures explicitly; do not claim delivery before it succeeds.
