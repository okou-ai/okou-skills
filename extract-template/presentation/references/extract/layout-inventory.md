# Extract source layouts and backgrounds

Inspect every source page. Preserve distinct content regions, proportions and
hierarchy; equivalent structures may share a layout with separate background variants.

## Source inventory

In `layouts/source-index.json`, record `sourceFilename`, positive `pageCount`, original
`sourceAspectRatio` and a `layouts` array. Each entry has a unique `id`, `file`
(relative to `layouts/`, under `source/`), one-based `sourcePages`, `purpose`,
`regions` and `capacity`. Cover every input page and note material adaptations to
16:9. Capacity guides future selection; actual fit depends on content, language and font.

Preserve the source upload and copy the neutral library unchanged. Style the source
layouts now; selected library fragments are adapted later in the generated working
deck. Source-index entries describe original compositions only.

## Background inventory

Record reusable elements and observed combinations in `design-system.md`:

| Inventory | Record |
| --- | --- |
| Background fields | ID, source pages, fills/blocks/bands/splits, colors, shape, proportions, anchors, and paired foreground/logo treatment. |
| Content-independent decoration | ID, source pages, editable geometry or asset path, colors, aspect ratio, and observed placement, scale, rotation, crop, opacity, and repetition. |
| Combination recipes | ID, field/decoration IDs, source pages, layering/placement, usable content area, page role/density, and permitted variations. Distinguish observed combinations from inferred adaptations. |

Decoration can be removed or reused without changing the factual message. Charts,
process arrows and product screenshots remain content; card fills and title
underlines that follow content remain components.

Use editable CSS/SVG for simple geometry and retain isolated artwork/textures in
`assets/`. Preserve proportions and documented color variants, reuse assets across
placements, and label reconstructions of obscured elements as inferred.

Keep fields and decorations separately reusable in `styles/template.css`, for
example with `data-surface` and `data-decoration`. Record compatible recipes;
explicit selections override defaults. Place backgrounds behind content without
changing its flow or intercepting clicks. Keep logos/footers in shared chrome and
meaningful imagery in content regions. Pair backgrounds with compatible text,
component, chart and logo colors.

Return to [SKILL.md](../../SKILL.md) to build and check the package.
