---
name: presentation-extract-template
description: Extract, extend, validate, and publish a reusable HTML presentation template after a file upload. Preserve source layouts and adapt selected built-in expressions to the source style, so later decks reuse saved editable layouts.
---

# Extract a presentation template

Turn the reference into a platform-compliant HTML template for new content. The source defines its visual language; the output remains HTML regardless of input format. Complete source analysis, layout reuse, built-in selection, style adaptation, and validation during extraction after upload, before publication. Later generation selects and edits saved local layouts; it does not repeat this extraction or rebuild their visual design. This workflow does not provide native PPTX in-place editing.

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

- Typography: preserve observed source sizes by layout/role, fonts, weights, leading, spacing, mixed runs, and supported language fallbacks. Record original units, uniform canvas conversion, source locations, and extracted versus inferred mappings; source sizes are the defaults. Do not require an unobserved metric/table/caption style just to complete a dictionary.
- Color and geometry: foreground/background roles, accents, chart colors, margins, content-safe areas, borders, radii, and image crops.
- Repeated components and chrome: cards, metrics, tables, quotes, image frames, logos, headers, footers, and page markers.
- Background fields and content-independent decorations: reusable elements, source-observed combinations, and allowed adaptations.

Read [references/layout-reuse.md](references/layout-reuse.md) for source inventory, upload-time extension, and later local editing. [references/built-in-layouts.md](references/built-in-layouts.md) identifies the pinned 52-layout Data Report catalogue in Template-artifact and the public neutral fallback. Select only needed expressions; borrow their content structure, not their theme or authoring policy. Follow the progressive token contract: a small reliable core, only needed extensions, explicit unknowns, and program binding. Preserve source-specific role/layout differences; aliases are mappings, not newly extracted styles. Read [references/typography-fit.md](references/typography-fit.md) for source-size extraction and local overflow fitting. An absent content type, such as images, is not a prohibition on future use.

## 3. Build the editable package

```text
<template-slug>/
  SKILL.md                 # usage and authoring instructions
  design-system.md         # brand rules, background elements/recipes, asset notes
  layouts/
    README.md              # local layout selection, editable regions, assembly
    source-index.json      # every original source page mapped to a preserved layout
    source/<name>.html     # distinct source compositions
    extended-index.json    # selected adaptations, capacity, provenance, validation
    extended/<name>.html   # source-styled built-in expressions, ready for reuse
    _shell.html            # shared canvas, fonts, chrome, and navigation
  styles/template.css      # shared source layout, brand, and component styles
  tokens/theme.tokens.json # small source-aware core and needed role/profile bindings
  tokens/fit-policy.json   # explicit user/inferred bounds, not extracted source facts
  scripts/fit-text.js      # shared source-size reset, measurement, and bounded fitting
  assets/                  # reusable logos, fonts, textures, and artwork
```

Preserve every distinct source composition and prefer it when new content fits. Group equivalent structures, keeping background variants separate. Follow the public core binding contract rather than copying the full optional token dictionary. Record unknown fields in extraction notes; infer only an actually needed mapping with a reason. Compile aliases and role CSS mechanically, keep source units/provenance, and use observed profiles for different source layouts.

During extraction, identify useful expression gaps and select complementary built-in structures using `references/built-in-layouts.md`. Start from the closest preserved source layout and reuse its shell, typography, components, background, and chrome. Adapt the selected expression into that visual language, validate it, and save it in `layouts/extended/` with an entry in `layouts/extended-index.json`. Do not copy all 52 layouts or vendor the upstream theme. Explain selections, skipped duplicates, and unresolved gaps; there is no mandatory extension count.

For both indexes, identify editable regions and permitted replacements/repeats separately from fixed framing. Generated decks select a fitting source layout first, then a fitting saved extension if no source layout fits; copy the chosen layout and edit only its declared regions. Keep the reusable template and original upload unchanged. A genuinely uncovered expression may use a documented deck-specific composition in the same design system; do not force incompatible content or require a GitHub fetch. Packaged layouts are references, not a whitelist.

Use a 16:9 canvas, shared CSS variables/components, and semantic regions for replaceable text, images, and data. Keep title and metric typography separate. Start each text region at its corresponding source size, converted with the layout's canvas scale. Only when rendered content overflows, automatically reduce the affected region's typography to the largest size that fits within its documented readability limit. Keep unaffected regions at their source sizes. Do not impose a universal font size or prohibit shrinking; change the layout or split content when bounded fitting cannot resolve the overflow. Prefer normal flow, Flexbox, or Grid; use absolute positioning for chrome, decoration, and intentional overlays.

Text, shapes, cards, tables, and ordinary charts must remain editable HTML/CSS/SVG. Retain isolated reusable artwork; never substitute a full-page screenshot for an editable layout or package old text/data as decoration.

Document assembly through the shared shell, with working package-relative asset paths. Wire the shared fitter into the shell so it runs after fonts and layout are ready and before the first QA capture or export; a written instruction to shrink text during QA is insufficient. Follow the readiness, reset, bounds, and reporting contract in `references/typography-fit.md`. Support all four navigation keys: `ArrowLeft`/`ArrowUp` go back; `ArrowRight`/`ArrowDown` go forward.

The generated `SKILL.md` and `layouts/README.md` must point to the local design system and both layout indexes, explain source-first selection followed by saved extensions, and document copy/edit operations, background composition, shared styles, fitter, and assembly. Include upstream commit-pinned references as provenance, not generation dependencies. Package the selected source-styled adaptations and all resources they need, not the whole catalogue, an upstream shell/theme, or synthetic fixture skins. Include source-size defaults, overflow-only shrinking, and unresolved-overflow handling locally; generation, viewing, QA, and export must work without this extraction guide or GitHub access.

## 4. Validate representative rebuilds

Rebuild representative source pages and background combinations. Render every selected extension with representative replacement content in the same source-styled shell before admitting it to `extended-index.json`. Confirm that the source inventory covers every original page and that extensions are not presented as original pages. Render the assembled examples:

```bash
npx --yes --package="${CLI_PKG_URL}" okou presentation screenshot \
  --input <rebuilt-deck.html> \
  --out <validation-dir>
```

Compare structure, typography, colors, component styling, decoration placement, and safe areas against the source. Fix shared rules where needed; verify navigation, language fallbacks, and asset loading. Rebuilt images are local validation evidence, not source-page images for publication.

Check that both local indexes resolve to packaged files, editable regions exist, and each saved extension records its upstream revision, source-style basis, capacity assumptions, and completed validation. Compare extensions with representative original pages for typography, framing, components, spacing, and background language; a zero-overflow report alone does not prove source fidelity. Validate only needed token roles, complete foreground/background pairs, source profiles, and alias provenance; do not call resolved aliases new extracted values. Keep temporary fixture decks and validation images outside the reusable package, but keep the validated reusable extensions inside it. Verify that no upstream theme/runtime dependency, fixture skin, unfinished prototype, or old business data was bundled. An unavailable catalogue may use the public fallback or leave a disclosed coverage gap; do not repeatedly fetch or claim an unvalidated extension.

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

Completion requires the editable package, complete original source layout coverage, selected source-styled extensions with local provenance and validation (or explicit unresolved gaps), reusable background elements with composition guidance, source-size typography with working automatic fitting, successful validation, and a successful publication command. Preserve the original upload and source-page image order; adapted layouts are package content, not new original pages. Report publication failures explicitly; do not claim delivery before it succeeds.
