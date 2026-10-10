# Source layouts and background composition

## Source inventory

Inspect every source page. Preserve distinct content regions, proportions, and hierarchy; equivalent structures may share a layout with separate background variants.

In `layouts/source-index.json`, use `sourceFilename`, positive `pageCount`, original `sourceAspectRatio` and a `layouts` array. Each entry records `id`, `file` (relative to `layouts/`, under `source/`), `sourcePages` (one-based integers), `purpose`, `regions` and `capacity`. IDs are unique; cover every input page and note material adaptations to 16:9. Capacities guide selection; actual fit depends on content, language and font. Run the packaged `tools/verify-package.mjs` before saving the Custom Template.

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

The five-step authoring path below is for later deck generation from the saved
Custom Template. It does not add outline creation, content rewriting, deck QA or
visual review of generated pages to the extraction stage.

`SKILL.md` should give a concise five-step authoring path, without breaking the work
into excessive substeps or adding standalone PPTX-export/delivery sections:

1. Determine the outline: purpose, audience, requested language, page count/range,
   and each page's main point and supporting content.
2. Choose suitable layouts: prefer fitting source-index compositions; use a selected
   neutral fragment only when the original layouts do not fit.
3. Assemble a copy in the final web directory with final asset paths. Preserve supported
   facts, source styling, editable content and the fixed 10px floor.
4. Run QA on the planned deck; diagnose geometry before changing copy, then fix and rerun
   on the same HTML. No need to repeat passing
   [interaction checks](qa.md#interaction-checks-already-included) on an unchanged deck.
5. Review only QA-designated pages unless a full pass is requested. Record the receipt
   and rerun final QA; follow [output staging](qa.md#targeted-review-and-requested-output)
   to clean the web directory before conversion and deliver the final outputs once.

Keep setup short: point to `design-system.md`, `layouts/README.md`,
`layouts/source-index.json` and the QA guide. Include only the exact QA and page-render
commands needed to follow the steps. Place source-specific caveats beside layout
selection. `layouts/README.md` should be a short path map linking back to `SKILL.md`.
Keep output handling within the five steps.

Include these source-specific rules as part of those actions:

- Select a fitting source layout first, then a source-observed background recipe suited to its role and content density.
- Respect the recipe's usable content area and documented color, placement, scale, crop and repetition rules. Keep decoration out of body-copy regions unless the source supports it.
- Prefer compatible quiet backgrounds for dense content. If decoration conflicts, change the recipe before reconsidering the layout. Do not shrink type merely to accommodate an ornament. Real content overflow uses the shared local fitter with the fixed 10px minimum; source sizes are initial styles, not runtime lower bounds.
- Document inferred combinations and new layouts while preserving shared brand rules. Do not impose a fixed background count or mechanical color rotation.

During extraction, document observed combinations from source evidence. If a
source-to-HTML reconstruction creates a specific fidelity risk, compare only one or
two unchanged source compositions; do not build a full sample deck or run generated-
deck QA by default. During later generation, validate selected adapted recipes.
Switching compatible backgrounds should preserve content geometry and typography;
verify actual text contrast rather than relying on low texture opacity. Follow `qa.md`
for generated-deck automatic gates and separate source-style review.
