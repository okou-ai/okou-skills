# Source layouts and background composition

## Source inventory

Inspect every source page. Preserve distinct content regions, proportions, and hierarchy; equivalent structures may share a layout with separate background variants.

In `layouts/source-index.json`, use `sourceFilename`, positive `pageCount`, original `sourceAspectRatio` and a `layouts` array. Each entry records `id`, `file` (relative to `layouts/`, under `source/`), `sourcePages` (one-based integers), `purpose`, `regions` and `capacity`. IDs are unique; cover every input page and note material adaptations to 16:9. Capacities guide selection; actual fit depends on content, language and font. Run the packaged `tools/verify-package.mjs` before publication.

During generation, prefer a source layout whose regions and capacity fit. If none fits, choose from the local Markdown table `library/references/catalog.md`, copy only selected fragments and their needed geometry rules into the working deck, and reuse the user's CSS classes/declarations. Adapt spacing, column ratios and image crop from observed source styles; do not apply geometry.css to preserved source layouts. Only when neither source nor local references fits should a documented source-styled composition be created. Do not force incompatible content into an existing composition.

Keep the source upload and library originals immutable. Upload analysis preserves source compositions and copies the neutral library; it does not pre-style the full library. Library adaptations belong to the generated working deck, not the original-source inventory.

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

`SKILL.md` must be a runnable, numbered authoring procedure, not only a set of style principles. `layouts/README.md` is its short path map and quick start. For every step, state which files to read, what to do, what artifact/checkpoint results, and what to do if the gate fails. Cover this sequence:

1. Confirm audience, objective, requested language, page count/range and output format; verify the package and read `design-system.md`, `layouts/README.md`, `layouts/source-index.json`, source-specific QA findings and `references/qa.md`.
2. Create a slide-by-slide content outline with evidence and one takeaway per page; do not invent missing facts.
3. Map planned pages to source-index IDs/pages, regions and capacity. Prefer original source compositions; explain available language-specific variants. Use the neutral table only when no source composition fits.
4. Create an isolated working copy, distinguish it from the archived shell/source fragments, assemble only planned pages and preserve package-relative assets. Never edit the original upload or stored package.
5. Replace all sample content; reuse actual source classes, typography, background recipes, geometry, crops and chrome. Adapt only the working copy and mark inferences.
6. Run the bundled fitter with disjoint regions and the fixed 10px logical-canvas floor; recompose or split unresolved content.
7. Run `tools/qa.mjs` with the planned page count and distinct report/prepared paths. Fix all hard blockers before continuing.
8. Render and compare the prepared HTML with source evidence. If PPTX is requested, convert that exact copy, render the actual PPTX and review the roundtrip. Follow the requested format; if none is stated, deliver both a hosted HTML deck and a PPTX. Explain how to create a minimal host directory with `index.html` plus only required styles/assets, preserving relative paths; never publish the archived source package as the finished deck. Deliver the requested files with a concise QA summary.

The generated runbook must show executable commands using paths that exist in that
package: copy to a fresh working directory, verify the package, run QA with its
planned page count/report/prepared outputs, render the prepared HTML, optionally
convert and render PPTX, and host the minimal HTML site. State success statuses and
what to fix/retry on failure. Explain placeholders; do not name absent tools/configs.

Include these source-specific rules as part of those actions:

- Select a fitting source layout first, then a source-observed background recipe suited to its role and content density.
- Respect the recipe's usable content area and documented color, placement, scale, crop and repetition rules. Keep decoration out of body-copy regions unless the source supports it.
- Prefer compatible quiet backgrounds for dense content. If decoration conflicts, change the recipe before reconsidering the layout. Do not shrink type merely to accommodate an ornament. Real content overflow uses the shared local fitter with the fixed 10px minimum; source sizes are initial styles, not runtime lower bounds.
- Document inferred combinations and new layouts while preserving shared brand rules. Do not impose a fixed background count or mechanical color rotation.

Check representative observed recipes during extraction and newly adapted recipes during generation. Switching compatible backgrounds should preserve content geometry and typography; verify actual text contrast rather than relying on low texture opacity. Follow `qa.md` for automatic gates and a separate source-style comparison.
