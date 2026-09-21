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
- Preserve every meaningfully distinct source layout. Consolidate pages only when their structure, proportions, and visual treatment are equivalent, and keep the source-page mapping.
- Never use full-page screenshots in place of editable HTML layouts.
- Reusable source logos, fonts, and textures may be retained as template assets.
- Scripts prepare page images, copy the shared layout scaffold, and assemble previews. The AI determines typography, color roles, components, motifs, chrome, and source layout meaning by inspecting the rendered pages.
- Prefer a preserved source layout when the new content fits. Otherwise use the shared generic library with the extracted brand theme; create a new layout only for a structure neither collection supports. Packaged layouts are not a whitelist.
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
2. **Color roles:** primary and alternate backgrounds, body text, muted text, accents, borders, states, and data-series colors. Record what each color does, not only its value.
3. **Repeated components:** recurring content structures such as cards, labels, metrics, charts, tables, quotes, steps, and image frames, including their fixed and variable parts.
4. **Motifs:** recurring decorative shapes, textures, lines, geometry, illustration treatments, or compositional gestures that carry the presentation's identity.
5. **Chrome:** page numbers, headers, footers, logos, edge markers, persistent navigation, and other framing elements repeated across pages.

Also capture the rules required to implement reusable layouts:

- page margins and the content safe area;
- page roles and reusable reference layout types;
- corner radii, borders, shadows, and image-cropping behavior;
- chart, table, label, and metric styling;
- which rules stay fixed and which may vary with the content.

Implement these rules as shared HTML/CSS variables, base styles, and components instead of scattering them across individual sample pages. Distinguish observed source rules from neutral fallback choices for components the source does not establish; do not describe those choices as extracted facts.

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

Read [references/layout-reuse.md](references/layout-reuse.md) when building the package. It defines source provenance, shared layout selection, and the brand CSS boundary. Install the bundled 44 generic layouts from the directory containing this guide:

```bash
node scripts/install-layout-library.mjs --package <template-slug>
```

The installer preserves existing source files and customized theme, shell, and chrome. It refuses a conflicting shared library file without overwriting it. These generic layouts supplement the source layouts; they are not 44 layouts extracted from the user's deck.

Use this package shape:

```text
<template-slug>/
  SKILL.md                 # template metadata and usage instructions
  design-system.md         # visual rules, component rules, and asset notes
  layouts/
    README.md              # selection order and assembly instructions
    source-index.json      # every source page mapped to its preserved layout
    source/                # every meaningfully distinct original layout
      <layout-name>.html
    common/
      catalog.json         # generic purposes, regions, and capacity guidance
      <layout-name>.html   # 44 shared generic content fragments
    _shell.html            # canvas, stylesheet links, navigation, slide markers
    chrome.html            # shared brand logo, footer, motifs, and edge elements
  styles/
    layout.css             # generic layout structures; keep the shared copy intact
    theme.css              # one shared brand theme, including component treatment
    template.css           # optional source-layout-specific structure
  assets/                  # only the logos, fonts, textures, and other assets in use
```

Name source layouts by content purpose, such as `cover`, `section-divider`, `two-column`, `kpi-grid`, `image-left`, `table`, and `closing`. Record every input page in `layouts/source-index.json`; equivalent pages may share a layout. Retain distinct compositions even if they have the same broad purpose. A few representative samples are not a substitute for this complete layout inventory.

Map the extracted brand into `styles/theme.css`, using the scaffold's `--pl-*` tokens and `.pl-*` semantic classes. Keep `.pl-title` separate from `.pl-metric`. Put shared brand framing in `layouts/chrome.html`; generic fragments carry content relationships rather than logos or brand ornaments. Source-specific compositions can retain their own editable structures and use the same brand rules.

The generated package's `SKILL.md` and `layouts/README.md` must explicitly instruct later authors to:

1. Read `design-system.md` and `layouts/source-index.json` first, and prefer a source layout whose regions and capacity fit the content.
2. Read `layouts/common/catalog.json` when no source layout fits, then use the selected fragment with `styles/layout.css`, the same `styles/theme.css`, and `layouts/chrome.html` in `_shell.html`.
3. Adapt or split content to keep the brand's typography and spacing; do not shrink text with page-specific inline styles. Catalog capacities are selection guidance and require checking the actual content and language.
4. Create a new structure only for a genuine gap, preserving the shared brand rules and documenting the addition.

Neither source layouts nor the generic catalog require forcing unsuitable new content into an existing file.

Original logos, fonts, and textures may be extracted and retained. Do not crop a full-page screenshot containing old text, old data, or one-off content and present it as a template asset.

If the reference presentation contains no images, record only that image usage was not observed in the reference. Do not turn that observation into "no images," "text-only layouts," or another authoring restriction. When new content needs imagery, an image layout may be introduced with cropping, borders, corner radii, and composition that fit the design system.

### 4. Rebuild representative pages and validate the extraction

Use representative source pages to compare the extracted rules against the reference, while checking that the full source layout inventory remains represented. Also assemble every common layout with the shared brand theme and chrome:

```bash
node scripts/preview-layouts.mjs --package <template-slug>
```

This writes `<template-slug>/layouts/preview.html`. Existing customized shells must retain the documented slide markers and stylesheet links (see the layout-reuse reference). These rebuilds validate the package; they do not generate the source-page images that will be uploaded.

Check whether the rebuilt pages reproduce:

- the reference page structure;
- the typography and color system;
- the structure and styling of repeated components;
- the position, proportion, and use of motifs and chrome;
- the page margins, content safe area, and layout relationships;
- the required behavior of `ArrowLeft`, `ArrowUp`, `ArrowRight`, and `ArrowDown`.

Render the common-layout preview to ordered local page images:

```bash
npx --yes --package="${CLI_PKG_URL}" okou presentation screenshot \
  --input <template-slug>/layouts/preview.html \
  --out <validation-dir>
```

Use the same screenshot command on assembled source-layout examples for reference comparisons. Correct mismatches in shared theme/components, check dense tables and metrics as well as simple columns, and confirm CJK fallbacks and asset paths. If a composition cannot express the brand through these shared rules, use its preserved source layout or document the missing structure; do not silently replace the brand with the neutral starter theme. `<validation-dir>` is temporary local evidence: never pass it to `--pages` and do not upload its reconstructed screenshots.

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
- the 44 shared generic layouts supplement those originals and use one source-adapted brand theme and shared chrome;
- later authoring instructions explicitly prefer fitting source layouts, consult the common catalog as needed, and preserve typography through content selection or splitting;
- packaged layouts are explicitly identified as references and do not limit later generation tasks to those layouts;
- text, shapes, cards, tables, and ordinary charts remain editable HTML, CSS, or SVG;
- no full-page screenshot substitutes for an editable layout;
- the HTML presentation supports navigation with all four arrow keys;
- typography, color roles, repeated components, motifs, and chrome are represented in the shared design system;
- no unobserved content type has been turned into a prohibition, including images when the source contains none;
- every reusable asset is packaged and every logo, font, texture, and stylesheet path resolves;
- representative source-page rebuilds and all generic layouts have been rendered to verify the extracted design information and brand adaptation;
- template metadata, layout documentation, and content-region definitions are complete;
- the normal template publication flow succeeds.
