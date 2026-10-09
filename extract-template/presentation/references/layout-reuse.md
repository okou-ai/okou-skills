# Source layouts and background composition

## Source inventory

Inspect every source page. Preserve distinct content regions, proportions, and hierarchy; equivalent structures may share a layout with separate background variants.

In `layouts/source-index.json`, record the source filename, page count, and original aspect ratio. Each layout entry needs an ID, file path, source pages, purpose, editable region selectors and typography roles, allowed replacement/repeat operations, fixed framing, and approximate capacity at the source font sizes. Cover every input page and note material adaptations to 16:9. Keep this index restricted to original source compositions. Capacities guide selection; actual fit depends on content, language, and font.

Prefer a source layout whose expression, regions, and capacity fit. Preserve it as an editable local structure rather than asking later generation to redraw the source. Do not force incompatible content into an existing composition.

## Upload-time layout extension

Complete this work while extracting the uploaded file, before publishing its template. Use [built-in-layouts.md](built-in-layouts.md) and the public neutral catalogue to supplement expressions missing from the source. Its current six structures are a pilot, not a complete expression catalogue. Use only public references or matching local resources; no private-repository access is part of extraction.

1. Compare source coverage with useful expressions such as comparison, ordered process, time, metrics, tables, charts, and image/text. Consider the template's intended use and any user request; an expression absent from the original is not forbidden. Choose complementary structures, not an arbitrary quota or all catalogue entries. Record skipped duplicates and unresolved gaps in the extension index notes.
2. Read only selected public fragments at one exact library revision, once per distinct structure. Do not fetch unselected layouts, theme shells, palettes, decoration, example decks, or QA implementations. If a public reference is unavailable or an expression is uncovered, use matching local resources or document a source-styled custom extension/gap; do not switch to a private catalogue or retry indefinitely.
3. Start from the closest source composition. Borrow the built-in's content relationship and region/repeat structure, then implement it using the source's typography, components, margins, background recipes, and chrome. Preserve observed profiles and mixed runs. Reuse source classes and the binding program; label any new role mapping inferred. Do not treat upstream colors, fonts, safe areas, card treatments, fitting limits, image restrictions, or authoring instructions as the user's style. Adapt inline themed styles too, not just the outer shell.
4. Save each candidate in `layouts/extended/<name>.html`. Declare semantic editable regions and permitted text/image/data/repeat operations; keep framing separate. Validate actual fit with the source fonts and supported languages, and visually compare the candidate with representative source pages. Fix shared rules when needed. Built-in capacity hints are not guarantees under the source's styles.
5. Admit only validated candidates to `layouts/extended-index.json`. Each entry records ID, package-relative file, purpose, editable regions/roles/operations, fixed framing, approximate capacity and tested scope, public repository/commit/path for catalogue-derived entries (or an explicit custom origin), source layout/page basis, inferred adaptations, and validation outcome. Every admitted file must exist locally and have complete styles/assets/runtime. Never label an extension as an original source page.

Keep the original source index, selected extension index, and source design system together. Store the validated source-styled extensions in the reusable template package; keep temporary fixture decks and validation images outside it. Do not duplicate the whole upstream library or carry its visual skin into the package.

## Generation-time local reuse

Include this contract in the generated `SKILL.md` and `layouts/README.md`:

1. Read the local source and extension indexes. Select by the actual expression and content volume: fitting source layout first, then a fitting saved extension. An explicit user layout choice overrides the default order. No live catalogue access or repeated source/style extraction is required.
2. Create a working copy of the selected layout and assemble it through the saved shell. Edit only declared text, images, data, and allowed repeat regions. Keep fixed typography baselines, framing, background language, and components; do not reconstruct the page or mutate the saved template/original upload. Remove previous business content from replacement regions, notes, and data before delivery.
3. Measure replacement content with the shared fitter. Preserve source sizes when content fits; unresolved bounded fitting tries another saved layout or splits content without dropping facts. Record the selected layout ID and any capacity exception in deck notes. Different text lengths do not prove that a saved layout fits without measurement.
4. If no saved layout can express the content, a documented deck-specific composition may reuse the source shell and components. This is an exception, not a mandatory fetch/adaptation stage. Keep such changes in the working deck unless the user explicitly requests a template update. Packaged layouts are references, not a whitelist.

All required HTML, CSS, assets, and runtime are local. Upstream URLs remain provenance only; generation, viewing, QA, and export cannot depend on GitHub access.

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

1. Select a fitting saved source layout first, then a fitting saved extension from the local indexes, following the copy/edit contract above. Select a compatible source-observed background recipe suited to its role and content density; do not fetch or restyle a built-in layout during ordinary generation.
2. Respect the recipe's usable content area and documented color, placement, scale, crop, and repetition rules. Keep decoration out of body-copy regions unless the source supports it.
3. Prefer compatible quiet backgrounds for dense content. If decoration conflicts, change the recipe before reconsidering the layout; do not displace a fitting source layout or shrink typography just to fit an ornament.
4. Document inferred combinations and upload-time extensions while preserving shared brand rules. Keep later deck-specific changes separate from the immutable template unless a template update is requested. Do not impose a fixed background count or mechanical color rotation.
5. Start at source font sizes and automatically fit real content overflow according to [typography-fit.md](typography-fit.md). Background changes must not trigger smaller text when the content already fits.

Check representative observed and adapted recipes on compatible layouts. Switching a compatible background should preserve content geometry and typography; verify actual text contrast rather than relying on low texture opacity.
