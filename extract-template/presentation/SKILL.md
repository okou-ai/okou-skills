---
name: presentation-extract-template
description: Extract a reusable, editable, renderable, and publishable HTML Presentation Template from a reference PPTX, PPT, PDF, image deck, or set of page screenshots. Use when a reference presentation's typography system, color roles, repeated components, motifs, chrome, and layouts should become a reusable template, with ordered source-page images and a complete package prepared for publication.
---

# Extract an HTML template from a reference presentation

## Goal

Convert the user's reference presentation into a reusable HTML Presentation Template.

The input may be a PPTX, PPT, PDF, image deck, or set of page screenshots. Regardless of the input format, the final deliverable must be an HTML presentation template package that conforms to the platform specification.

The source provides visual and layout reference only. It does not determine the technical format of the final template.

## Principles

- Reimplement the template in HTML and CSS.
- Reproduce the presentation's visual language and layout system, not the source file's internal object structure.
- The template must support new content instead of merely reproducing the original presentation.
- Preserve every meaningfully distinct source layout. Pages with equivalent content structure and proportions may share a layout; preserve their background and decoration differences separately, with source-page mappings.
- Never use full-page screenshots in place of editable HTML layouts.
- Reusable source logos, fonts, and textures may be retained as template assets.
- Scripts prepare viewable page images and delivery files only. The AI determines typography, color roles, components, motifs, chrome, and source layout meaning by inspecting the rendered pages.
- Prefer a preserved source layout when the new content fits. When no preserved layout supports the content, create a documented layout using the same design system. Packaged layouts are not a whitelist.
- The absence of a content type in the source is not a prohibition. In particular, a source presentation with no images must not cause the template to forbid images in future presentations.

## Workflow

### 1. Inspect the complete input

Preserve the original source and inspect every page in its original order. Establish:

- page ratio, canvas size, and page count;
- primary content types;
- recurring page structures;
- typography, colors, and graphic material;
- visual consistency across pages;
- page roles such as cover, section divider, content, data, and closing pages.

For PPT, PPTX, and PDF inputs, run this command from the directory containing this guide:

```bash
node scripts/render-pages.mjs \
  --input <deck.ppt|deck.pptx|deck.pdf> \
  --out <source-pages-dir>
```

The command writes ordered source-page images named `page-001.png`, `page-002.png`, and so on.

### 2. Extract the design system

Inspect the complete rendered presentation and prioritize five kinds of information:

1. **Typography system:** font families, display and body faces, size hierarchy, weights, line heights, letter spacing, and CJK fallbacks.
2. **Color roles and background fields:** primary fills, background blocks/bands/splits, body text, muted text, accents, borders, states, and data-series colors. Preserve field geometry and compatible foreground colors as well as color values.
3. **Repeated components:** recurring content structures such as cards, labels, metrics, charts, tables, quotes, steps, and image frames, including their fixed and variable parts.
4. **Content-independent decoration:** reusable shapes, textures, lines, geometry, or illustration treatments that carry identity without encoding the slide's message or data. Preserve these as separate elements with source-page evidence and placement rules; meaningful imagery and diagrams remain content.
5. **Chrome:** page numbers, headers, footers, logos, edge markers, persistent navigation, and other framing elements repeated across pages.

Also capture the rules required to implement reusable layouts:

- page margins and the content safe area;
- page roles and reusable reference layout types;
- corner radii, borders, shadows, and image-cropping behavior;
- chart, table, label, and metric styling;
- which rules stay fixed and which may vary with the content.

Implement these rules as shared HTML/CSS variables, base styles, and components instead of scattering them across individual sample pages. Distinguish observed source rules from neutral fallback choices for components the source does not establish; do not describe those choices as extracted facts.

Extract background fields and decorative elements separately, then record the source's combinations and their permitted adaptations. The package must retain both reusable elements and guidance for combining them, including layering, cropping, text-safe regions, and suitable page roles. Follow the background section in [references/layout-reuse.md](references/layout-reuse.md).

### 3. Implement the HTML template

Follow the platform's HTML Presentation specification:

- use the platform's required 16:9 slide canvas;
- use shared design variables, base styles, and font declarations;
- implement recurring structures as reusable layouts and components;
- give variable content clear semantic regions;
- allow later generation tasks to replace text, images, and data;
- make every layout render reliably through the documented shared shell;
- use package-relative resource paths and verify that every resource loads;
- make the assembled HTML presentation support four-direction keyboard navigation: `ArrowLeft` and `ArrowUp` go to the previous slide, while `ArrowRight` and `ArrowDown` go to the next slide;
- prefer normal document flow, Flexbox, and CSS Grid; reserve absolute positioning for fixed chrome, decoration layers, and intentional overlays;
- implement text, shapes, cards, tables, and ordinary charts as editable HTML, CSS, or SVG.

Read [references/layout-reuse.md](references/layout-reuse.md) when building the package. It defines the source layout inventory, reuse priority, and background element/composition guidance.

Use this package shape:

```text
<template-slug>/
  SKILL.md                 # template metadata and usage instructions
  design-system.md         # visual rules, background elements/recipes, and asset notes
  layouts/
    README.md              # selection order and assembly instructions
    source-index.json      # every source page mapped to its preserved layout
    source/                # every meaningfully distinct original layout
      <layout-name>.html
    _shell.html            # shared canvas, fonts, chrome, navigation, and base structure
  styles/
    template.css           # extracted layout, brand, background, and component styles
  assets/                  # only the logos, fonts, textures, and other assets in use
```

Name source layouts by content purpose, such as `cover`, `section-divider`, `two-column`, `kpi-grid`, `image-left`, `table`, and `closing`. Record every input page in `layouts/source-index.json`; equivalent pages may share a layout. Retain distinct compositions even if they have the same broad purpose. A few representative samples are not a substitute for this complete layout inventory.

Implement the extracted brand and reusable components in shared `styles/template.css`. Keep slide-title and metric typography separate. Preserve source compositions as editable structures, with shared brand framing in the shell or reusable components.

Implement reusable background-field and decoration styles in the same shared CSS, with source-backed combinations documented in `design-system.md`. Select these independently from content layout, subject to the combination's usable content area.

The generated package's `SKILL.md` and `layouts/README.md` must explicitly instruct later authors to:

1. Read `design-system.md` and `layouts/source-index.json` first, and prefer a source layout whose regions and capacity fit the content.
2. Read the background element and recipe inventories in `design-system.md`. Prefer a source-observed combination of background fields and decoration, then adapt within its documented color, placement, crop, and content-area rules. Use a compatible quiet recipe for dense content when available.
3. Adapt or split content to keep the brand's typography and spacing; do not shrink text with page-specific inline styles. Recorded layout capacities are selection guidance and require checking the actual content and language.
4. Create a new structure only when the source layouts do not support the content, preserving the shared brand rules and documenting the addition.

Do not force unsuitable new content into a preserved source layout.

Original logos, fonts, and textures may be extracted and retained. Do not crop a full-page screenshot containing old text, old data, or one-off content and present it as a template asset.

If the reference presentation contains no images, record only that image usage was not observed in the reference. Do not turn that observation into "no images," "text-only layouts," or another authoring restriction. When new content needs imagery, an image layout may be introduced with cropping, borders, corner radii, and composition that fit the design system.

### 4. Rebuild representative pages and validate the extraction

Use representative source pages to compare the extracted rules against the reference, while checking that the full source layout inventory remains represented. Include the observed background combinations and representative documented adaptations. These rebuilds validate the package; they do not generate the source-page images that will be uploaded.

Check whether the rebuilt pages reproduce:

- the reference page structure;
- the typography and color system;
- the structure and styling of repeated components;
- the position, proportion, and use of motifs and chrome;
- the page margins, content safe area, and layout relationships;
- the required behavior of `ArrowLeft`, `ArrowUp`, `ArrowRight`, and `ArrowDown`.

Render assembled HTML examples to ordered local page images:

```bash
npx --yes --package="${CLI_PKG_URL}" okou presentation screenshot \
  --input <rebuilt-deck.html> \
  --out <validation-dir>
```

Compare the rebuilds with the user's source-page images. Correct mismatches in shared styles/components and confirm the supported language fallbacks and asset paths. `<validation-dir>` is temporary local evidence: never pass it to `--pages` and do not upload its reconstructed screenshots.

### 5. Upload and publish the template

The completed template package must contain the platform-required:

- template metadata and usage instructions;
- reusable HTML layouts;
- shared CSS;
- logos, fonts, textures, and other reusable static assets;
- layout and content-region definitions.

Use the normal template publication flow for final delivery. The command uploads and commits the source file, ordered source-page images, and HTML template package together:

```bash
npx --yes --package="${CLI_PKG_URL}" okou presentation-template publish \
  --title "<user-visible template name>" \
  --source <deck.pptx|normalized-source.pdf> \
  --pages <source-pages-dir> \
  --package <template-slug>
```

The current `--source` option accepts PPTX or PDF. Convert and preserve a legacy PPT as PPTX before publishing. For an image deck or page screenshots, first create a PDF that preserves the original page order and retain the provenance of the original inputs.

`<source-pages-dir>` must contain only screenshots of the user's source pages. Their filename order determines upload order. Never mix reconstructed validation images into this directory. Claim that the template was created or published only after the publication command succeeds; report the specific blocker if it fails.

## Completion criteria

The task is complete only when all of the following are true:

- the final deliverable is a platform-compliant HTML Presentation Template;
- the source presentation's primary visual characteristics and layout language are retained;
- the template supports new content instead of only reproducing the original pages;
- every meaningfully distinct source layout is retained, with every source page mapped in `layouts/source-index.json`;
- later authoring instructions explicitly prefer fitting source layouts and preserve typography through content selection or splitting;
- packaged layouts are explicitly identified as references and do not limit later generation tasks to those layouts;
- text, shapes, cards, tables, and ordinary charts remain editable HTML, CSS, or SVG;
- no full-page screenshot substitutes for an editable layout;
- the HTML presentation supports navigation with all four arrow keys;
- typography, color roles, repeated components, motifs, and chrome are represented in the shared design system;
- background fields and content-independent decorations are reusable separately, with source-observed recipes and explicit combination guidance in the generated package;
- no unobserved content type has been turned into a prohibition, including images when the source contains none;
- every reusable asset is packaged and every logo, font, texture, and stylesheet path resolves;
- representative source-page rebuilds and background combinations have been rendered to verify the extracted design information;
- template metadata, layout documentation, and content-region definitions are complete;
- the normal template publication flow succeeds.
