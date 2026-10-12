# Reuse layouts and backgrounds during generation

Use the saved `design-system.md`, `layouts/source-index.json` and source fragments.
No need to inventory or extract the source again.

## Choose and adapt a layout

Prefer a source layout whose regions and capacity fit the content. Capacity is a
selection hint; actual fit depends on content, language and font.

If none fits, choose from `library/references/catalog.md`, copy selected fragments
and their needed geometry rules into the working deck, and reuse the source CSS
classes/declarations. Adapt spacing, column ratios and image crop from source
styles; scope geometry.css to the selected neutral fragments. When neither source
nor local references fit, document a new source-styled composition in the working deck.

Keep the stored template, source index and library originals unchanged. Follow the
[runtime contract](runtime-contract.md) when changing structure, navigation or charts.

## Select a background

- Select a fitting layout first, then a source-observed recipe suited to its role
  and content density. Explicit selections override defaults.
- Respect the recipe's usable content area, compatible colors, placement, scale,
  crop and repetition rules. Keep decoration out of body-copy regions unless the
  source supports it; choose quiet backgrounds for dense content.
- Keep backgrounds behind content without changing its flow or intercepting clicks.
  Preserve shared logos/footers, asset proportions and documented color variants.
- Resolve decoration conflicts through the recipe while preserving typography.
  Actual content overflow uses the [shared fitter](typography-fit.md) with its 10px
  floor; source sizes are initial styles. Document inferred combinations and new
  layouts while preserving shared brand rules.

Compatible background changes preserve content geometry and typography. Follow
[qa.md](qa.md); no extra review pass is needed solely because a layout or background
was adapted.
