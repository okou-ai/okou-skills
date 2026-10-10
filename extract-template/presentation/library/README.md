# Local neutral presentation layouts

This package contains **54 editable reference fragments**, not 54 pre-styled slides. It is bundled with extraction and copied unmodified into each reusable user package. No private repository, catalogue download, GitHub credentials, or another template's branded shell, stock photos, fonts, palette or decorations are required.

Read the [layout catalogue table](references/catalog.md), then only the selected `layouts/fragments/*.html` files. Inspect content slots and repeated groups directly in the HTML; no separate JSON metadata is needed. Catalogue paths are relative to the catalogue file. Purpose and capacity are selection hints, not a fixed slide count or a guarantee that content will fit.

## How geometry.css works with the user's uploaded PPT

**It does not parse PPT files, automatically convert the user's design into CSS, or apply to preserved source layouts.** Source layouts continue to use the extracted user styles. This file provides structural references for complementary layouts: Flex/Grid, columns, charts and media containers. It does not define the user's typography, palette or component skin.

Adaptation happens during generation:

1. Read the user's `design-system.md`, `styles/template.css`, original layouts and reference pages. Identify the actual styles used for titles, body copy, cards, tables and images.
2. If an original layout can express the content, reuse that layout and the user's styles without introducing geometry.css.
3. Only when a complementary layout is needed, copy the selected HTML and its required geometry.css rules into the **working deck**. Do not attach the entire stylesheet globally to the original layouts.
4. Reuse the user's existing CSS classes or declarations on selected title/body nodes. Change tags when needed to match the source selectors: if the source defines its title on `h1`, do not expect a new `div` to inherit that styling automatically. If the source has no corresponding component, infer it only from documented source styles and label that inference.
5. Adapt spacing, column ratios, image crop, borders and radii from measured source evidence. Set `--layout-gap` from the user's spacing and `--layout-image-fit` from the source crop mode, such as `cover` or `contain`. Equal columns, `1em` and `contain` in this file are reference starting points, not extracted user styles or mandatory constraints.
6. Fonts, initial sizes, weights, leading, foreground/background pairs, chart colours, fixed page elements and decorations must follow the user's PPT. Preserve the user's shell and source styling; do not import another template's skin.

Every geometry selector is scoped to `.builtin-layout` and uses zero-specificity `:where()` to avoid affecting original layouts or overriding existing user style classes. Selector isolation is not style adaptation: actually modify the selected layouts using the steps above.

## Generation-time adaptation

1. Prefer a fitting preserved source layout from the user's `layouts/source-index.json`.
2. Otherwise select a local reference fragment by its communicative purpose from the catalogue table. Copy it into the working deck's `.stage > .fit`. Do not modify the source upload, stored user template or library originals.
3. Apply the user's design system and matching source profile as described above. SVG CSS pixels are viewBox units: convert label sizes through `PresentationMetrics.fontFactor(element)` so their effective logical size matches the source, rather than blindly reusing HTML px values.
4. Expand only the required `data-repeat` prototypes and replace every `{{slot}}`. These markers are authoring hints, not a requirement for a template compiler. Use real supplied text, images and data. Do not retain example claims or invent facts to fill slots. Numeric SVG geometry must derive from real data; chart units, baselines, segment sums and bubble areas must remain correct.
   Keep the supplied `data-plot-mark` hooks on the actual geometry. Fill `data-value` slots from the real quantity for bars/areas, including negative or zero values; do not use an arbitrary positive number to satisfy QA. Point/line markers validate visible geometry without treating a zero coordinate or a flat series as missing data. The packaged QA guide defines these checks and intentional label overlaps.
5. Preserve the disjoint title/body `data-fit-region` hooks. Run the packaged text fitter and final QA. Every visible editable text run, including SVG labels, must meet the **10px logical-canvas minimum**. If content still cannot fit, change composition or split it; never hide or clip text.
6. Compare newly adapted compositions with the user's original file and style references. A green mechanical QA result is not a source-fidelity review.

Style only selected fragments during generation. Upload analysis preserves the user's style and original compositions; it does not pre-adapt the entire reference library.

HTML, CSS and SVG remain editable in the HTML template. SVG may become a picture during PPTX conversion; this package does not claim a native PowerPoint chart renderer. Keep labels as HTML text when native PPTX text editing is required, and validate the exported file.
