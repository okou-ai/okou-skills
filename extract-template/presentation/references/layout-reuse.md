# Source layouts and background composition

## Source inventory

Inspect every source page. Preserve distinct content regions, proportions, and hierarchy; equivalent structures may share a layout with separate background variants.

In `layouts/source-index.json`, record the source filename, page count, and original aspect ratio. Each layout entry needs an ID, file path, source pages, purpose, content regions, and approximate capacity. Cover every input page and note material adaptations to 16:9. Capacities guide selection; actual fit depends on content, language, and font.

Prefer a source layout whose regions and capacity fit. If none fits, create a documented layout using the same design system. Do not force incompatible content into an existing composition.

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

## Authoring guidance

Include these rules in the generated package's `SKILL.md` and `layouts/README.md`:

1. Select a fitting source layout first, then a source-observed background recipe suited to its role and content density.
2. Respect the recipe's usable content area and documented color, placement, scale, crop, and repetition rules. Keep decoration out of body-copy regions unless the source supports it.
3. Prefer compatible quiet backgrounds for dense content. If decoration conflicts, change the recipe before reconsidering the layout; do not displace a fitting source layout or shrink typography just to fit an ornament.
4. Document inferred combinations and new layouts while preserving shared brand rules. Do not impose a fixed background count or mechanical color rotation.

Check representative observed and adapted recipes on compatible layouts. Switching a compatible background should preserve content geometry and typography; verify actual text contrast rather than relying on low texture opacity.
