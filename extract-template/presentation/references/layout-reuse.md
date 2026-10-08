# Source layouts and background composition

## Source inventory

Inspect every source page. Preserve distinct content regions, proportions, and hierarchy; equivalent structures may share a layout with separate background variants.

In `layouts/source-index.json`, record the source filename, page count, and original aspect ratio. Each layout entry needs an ID, file path, source pages, purpose, content regions, their typography roles, and approximate capacity at the source font sizes. Cover every input page and note material adaptations to 16:9. Capacities guide selection; actual fit depends on content, language, and font.

Prefer a source layout whose regions and capacity fit. If none fits, adapt an available compatible built-in layout or create a documented layout using the same design system. Do not force incompatible content into an existing composition.

## Generation-time built-in references

The public neutral pilot supplies missing KPI, table, two-column, comparison, four-step process and image/text structures. It does not supply a theme or a complete chart/timeline catalogue. Keep them in the shared library, not in every extracted template package. The generated `SKILL.md` and `layouts/README.md` must include the absolute reference-index URL from [built-in-layouts.md](built-in-layouts.md) and these selection/adaptation rules; do not copy the catalogue or pre-adapt its layouts during extraction.

When generating a deck:

1. Prefer a fitting source layout. Only if the source compositions do not cover the new content or density, use the shared index to choose compatible structures by slide purpose and content volume.
2. Read only the selected fragment links, once per distinct layout in the run. Keep the catalogue and fragments at the same commit-pinned library revision; do not download the whole library or read unselected layouts, example decks, shared shells, or QA implementations. If a link is unavailable or unsuitable, use a source layout or create a documented custom composition instead of repeatedly retrying.
3. Borrow region ordering, proportions, bounded fit rectangles and repeat prototypes. Materialize all placeholders/repeated slots, then mechanically bind the needed roles to the custom template's type, surface pairs, spacing and components using the public core contract. Label any new role alias inferred rather than pretending it was observed. Use the user's shell/chrome; shared geometry and binding/fitting runtime are allowed, but no synthetic skin, private theme, decoration, font default or minimum size may be imported.
4. Start at the corresponding source font sizes, preserve observed layout profiles and mixed runs, and use the custom shared overflow fitter. Pair every selected background with its primary/secondary text and border roles; never assume white text on a brand-colored field. The built-in layout's capacity is only an estimate; measure again with the custom fonts, language, and real content before the first QA capture.
5. Inline the adapted structure in the generated deck using the custom shared styles and shell. Record the chosen layout ID, commit-pinned source URL, and adaptations in that deck's generation notes, not `layouts/source-index.json`. Keep all required styles and assets in the delivered artifact; it must render without fetching reference HTML or CSS. Do not write the adapted layout back into the reusable template package.

Reuse compatible structures instead of rebuilding common layouts for every deck. Built-in layouts supplement the source compositions; they do not replace the source design system.

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

1. Select a fitting source layout first. If none fits, use the shared external layout links on demand and the adaptation rules above; do not require packaged built-in layouts. Then select a source-observed background recipe suited to the slide's role and content density.
2. Respect the recipe's usable content area and documented color, placement, scale, crop, and repetition rules. Keep decoration out of body-copy regions unless the source supports it.
3. Prefer compatible quiet backgrounds for dense content. If decoration conflicts, change the recipe before reconsidering the layout; do not displace a fitting source layout or shrink typography just to fit an ornament.
4. Document inferred combinations and new layouts while preserving shared brand rules. Do not impose a fixed background count or mechanical color rotation.
5. Start at source font sizes and automatically fit real content overflow according to [typography-fit.md](typography-fit.md). Background changes must not trigger smaller text when the content already fits.

Check representative observed and adapted recipes on compatible layouts. Switching a compatible background should preserve content geometry and typography; verify actual text contrast rather than relying on low texture opacity.
