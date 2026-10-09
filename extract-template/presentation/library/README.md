# Local neutral presentation layouts

This package contains **54 editable reference fragments**, not 54 pre-styled slides.
It is bundled with extraction and copied unmodified into each reusable user package.
No private repository, catalogue download, GitHub credentials, branded shell,
stock photo, font, colour system or decoration resource is required.

Read `references/catalog.json` first, then only the selected `layouts/fragments/*.html`
files and `styles/geometry.css`. Paths in the catalogue are relative to the catalogue.
The catalogue describes purpose, content slots, repeated groups and approximate
capacity; these are selection hints, not a fixed slide count or a guarantee of fit.

## Generation-time adaptation

1. Prefer a fitting preserved source layout from the user's `layouts/source-index.json`.
2. Otherwise choose a local fragment by its communicative purpose. Copy it into the
   working deck's `.stage > .fit`; do not edit the source upload or library originals.
3. Apply the user's design system and a matching source profile: fonts, initial sizes,
   weights, leading, foreground/background pairs, component skin, spacing, crop,
   chart colours, chrome and decoration. SVG CSS pixels are viewBox units: convert
   source label sizes through `PresentationMetrics.fontFactor(element)` so their
   effective logical size matches the source, rather than blindly reusing HTML px.
   Keep unfamiliar roles explicitly inferred
   or alias them to a documented source role. Do not introduce another template skin.
4. Expand only the required `data-repeat` prototypes and replace every `{{slot}}`.
   These markers are authoring hints, not a required template compiler. Use real
   supplied text, image assets and data. Never keep example claims or fill a slot
   with an invented fact. Numeric SVG geometry must be derived from the real data;
   chart units, baselines, segment sums and bubble areas must remain correct.
5. Preserve the disjoint title/body `data-fit-region` hooks. Run the packaged
   fitter and final QA. Every visible editable text run has a **10px logical-canvas
   minimum**, including SVG labels. Change composition or split if it still cannot fit.
6. Compare newly adapted compositions with the user's source/style references.
   A green mechanical QA result is not a source-fidelity audit.

Only selected fragments are styled during generation. Upload analysis does not
pre-adapt the complete library. Shared geometry is a reference: `--layout-gap` and
`--layout-image-fit` must be adapted to observed source spacing and crop. The
contain fallback prevents distortion, but does not override a source `cover` recipe.
Do not copy temporary fixture skins, QA data or screenshots into a user package.

HTML/CSS/SVG remain editable in the HTML template. SVG can become a picture during
PPTX conversion; this package does not claim a native PowerPoint chart renderer.
Keep labels in HTML when native PPTX text editing is required and validate export.
