# Source layouts and background composition

## Source inventory

Inspect every source page. Preserve distinct content regions, proportions, and hierarchy; equivalent structures may share a layout with separate background variants.

In `layouts/source-index.json`, use `sourceFilename`, positive `pageCount`, original `sourceAspectRatio` and a `layouts` array. Each entry records `id`, `file` (relative to `layouts/`, under `source/`), `sourcePages` (one-based integers), `purpose`, `regions` and `capacity`. IDs are unique; cover every input page and note material adaptations to 16:9. Capacities guide selection; actual fit depends on content, language and font. Run the packaged `tools/verify-package.mjs` before saving the Custom Template.

During generation, prefer a source layout whose regions and capacity fit. If none fits, choose from `library/references/catalog.md`, copy selected fragments and their needed geometry rules into the working deck, and reuse the user's CSS classes/declarations. Adapt spacing, column ratios and image crop from source styles; keep geometry.css scoped to the selected neutral fragments. When neither source nor local references fit, document a new source-styled composition.

Keep the source upload and library originals immutable. Upload analysis preserves source compositions and copies the neutral library; it does not pre-style the full library. Library adaptations belong to the generated working deck, not the original-source inventory.

When changing slide structure, navigation or charts, follow the
[runtime contract](runtime-contract.md) for the required HTML hooks.

## Background elements and recipes

Extract reusable elements and preserve their source combinations in `design-system.md`:

| Inventory | Record |
| --- | --- |
| Background fields | ID, source pages, fills/blocks/bands/splits, colors, shape, proportions, anchors, and paired foreground/logo treatment. |
| Content-independent decoration | ID, source pages, editable geometry or asset path, colors, aspect ratio, and observed placement, scale, rotation, crop, opacity, and repetition. |
| Combination recipes | ID, field/decoration IDs, source pages, layering/placement, usable content area, page role/density, and permitted variations. Distinguish observed combinations from inferred adaptations. |

Decoration can be removed or reused without changing a slide's factual message. Charts, process arrows, and product screenshots remain content; card fills and title underlines that follow content remain components.

Use editable CSS/SVG for simple geometry and retain isolated artwork/textures in `assets/`. Reuse assets across placements. Preserve their proportions and documented color variants; label reconstructions of obscured elements as inferred.

Keep field and decoration styles separately reusable in `styles/template.css`, for example through package-defined `data-surface` and `data-decoration` attributes. Recipes select compatible combinations; not every extracted field and ornament necessarily works together. Explicit selections override defaults.

Place background layers behind content without changing its flow or intercepting clicks. Keep logos/footers in shared chrome and meaningful imagery in content regions. Pair each background with compatible text, component, chart, and logo colors.

## Selecting backgrounds during generation

- Select a fitting source layout first, then a source-observed background recipe suited to its role and content density.
- Respect the recipe's usable content area and documented color, placement, scale, crop and repetition rules. Keep decoration out of body-copy regions unless the source supports it.
- Prefer compatible quiet backgrounds for dense content. Resolve decoration conflicts through the recipe while preserving typography. Real content overflow uses the shared local fitter with the fixed 10px minimum; source sizes are initial styles, not runtime lower bounds.
- Document inferred combinations and new layouts while preserving shared brand rules. Choose background variety to suit the content.

Compatible background changes preserve content geometry and typography. Use
[qa.md](qa.md) for contrast checks and the scope of visual review; no additional
review pass is needed solely because a layout or background was adapted.
