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
- Consolidate similar pages into reusable layouts instead of creating one-off templates for individual pages.
- Never use full-page screenshots in place of editable HTML layouts.
- Reusable source logos, fonts, and textures may be retained as template assets.
- Scripts prepare viewable page images and delivery files only. The AI determines typography, color roles, components, motifs, chrome, and layout meaning by inspecting the rendered pages.
- Packaged layouts are references, not a layout whitelist. A later generation task may use another layout when the new content calls for it, provided it retains the same design system.
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

For PPT, PPTX, and PDF inputs, run this command from `extract-template/presentation/`:

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

Implement these rules as shared HTML/CSS variables, base styles, and components instead of scattering them across individual sample pages. Leave anything the source does not establish undefined rather than inventing it.

### 3. Implement the HTML template

Follow the platform's HTML Presentation specification:

- use the platform's required 16:9 slide canvas;
- use shared design variables, base styles, and font declarations;
- implement recurring structures as reusable layouts and components;
- give variable content clear semantic regions;
- allow later generation tasks to replace text, images, and data;
- make every layout render independently and reliably;
- use package-relative resource paths and verify that every resource loads;
- make the assembled HTML presentation support four-direction keyboard navigation: `ArrowLeft` and `ArrowUp` go to the previous slide, while `ArrowRight` and `ArrowDown` go to the next slide;
- prefer normal document flow, Flexbox, and CSS Grid; reserve absolute positioning for fixed chrome, decoration layers, and intentional overlays;
- implement text, shapes, cards, tables, and ordinary charts as editable HTML, CSS, or SVG.

Use this package shape as a guide and omit unused files or directories:

```text
<template-slug>/
  SKILL.md                 # template metadata and usage instructions
  design-system.md         # visual rules, component rules, and asset notes
  layouts/
    README.md              # layout index, purposes, and content-region definitions
    _shell.html            # shared canvas, fonts, chrome, and base structure
    <layout-name>.html     # reusable example layout
  styles/
    template.css           # shared CSS; may be inlined in _shell.html if required
  assets/                  # only the logos, fonts, textures, and other assets in use
```

Name layouts by content purpose, such as `cover`, `section-divider`, `two-column`, `kpi-grid`, `image-left`, `table`, and `closing`. Add a layout only when it represents a meaningfully different, reusable structure.

State clearly in `layouts/README.md` that the packaged files demonstrate page structures and visual language observed in the reference presentation. Later generation tasks should consult them but must not force new content into an existing layout or require every slide to match a packaged file. When needed, create a new layout while preserving the typography system, color roles, repeated components, motifs, and chrome.

Original logos, fonts, and textures may be extracted and retained. Do not crop a full-page screenshot containing old text, old data, or one-off content and present it as a template asset.

If the reference presentation contains no images, record only that image usage was not observed in the reference. Do not turn that observation into "no images," "text-only layouts," or another authoring restriction. When new content needs imagery, an image layout may be introduced with cropping, borders, corner radii, and composition that fit the design system.

### 4. Rebuild representative pages and validate the extraction

Use the extracted design rules to rebuild a small number of representative pages. This reconstruction exists only to verify that the extracted information is correct. It is not a page-by-page rebuild of the source and does not generate the source-page images that will be uploaded.

Check whether the rebuilt pages reproduce:

- the reference page structure;
- the typography and color system;
- the structure and styling of repeated components;
- the position, proportion, and use of motifs and chrome;
- the page margins, content safe area, and layout relationships;
- the required behavior of `ArrowLeft`, `ArrowUp`, `ArrowRight`, and `ArrowDown`.

Render a rebuilt HTML page to a local 1600×900 image when a visual comparison is useful:

```bash
agent-browser --allow-file-access set viewport 1600 900
agent-browser --allow-file-access open \
  file:///ABSOLUTE_PATH/<template-slug>/layouts/<layout-name>.html
agent-browser screenshot \
  <validation-dir>/<layout-name>.png
agent-browser errors
```

Compare the rebuild with the user's source-page images. If it reveals a mismatch, correct the extracted design rules and template implementation, then rebuild and check again. `<validation-dir>` is temporary local evidence: never pass it to `--pages` and do not upload its reconstructed screenshots.

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
- similar pages have been consolidated into reusable layouts rather than page-specific templates;
- packaged layouts are explicitly identified as references and do not limit later generation tasks to those layouts;
- text, shapes, cards, tables, and ordinary charts remain editable HTML, CSS, or SVG;
- no full-page screenshot substitutes for an editable layout;
- the HTML presentation supports navigation with all four arrow keys;
- typography, color roles, repeated components, motifs, and chrome are represented in the shared design system;
- no unobserved content type has been turned into a prohibition, including images when the source contains none;
- every reusable asset is packaged and every logo, font, texture, and stylesheet path resolves;
- representative page rebuilds have verified the extracted design information;
- template metadata, layout documentation, and content-region definitions are complete;
- the normal template publication flow succeeds.
