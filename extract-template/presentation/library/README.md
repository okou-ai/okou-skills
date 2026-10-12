# Local neutral presentation layouts

These **54 editable reference fragments** complement the user's source layouts.
The library is bundled unchanged with the extracted template. Read the
[catalogue](references/catalog.md), then only the selected fragments; catalogue
paths are relative to that file. Purpose and capacity are selection hints.

## Adapt selected fragments during generation

1. Prefer a fitting source layout from `layouts/source-index.json`. Otherwise copy
   a selected reference into the working deck's `.stage > .fit`, together with its
   needed geometry.css rules. Keep the stored template and library originals unchanged.
2. Apply `design-system.md`, the source CSS and a compatible source profile. Reuse
   matching classes or tags, including the actual title selector. Adapt spacing,
   column ratios, crops, borders and decorations from source evidence; label inferred
   components. Set `--layout-gap` and `--layout-image-fit` from those observations.
3. Expand the required `data-repeat` groups and replace every `{{slot}}` with supplied
   content. Derive chart geometry, units, baselines, segment sums and bubble areas from
   real data. Keep `data-plot-mark` hooks and fill bar/area `data-value` with the actual
   quantity, including zero or negative values. Use point/line hooks for other marks.
4. Retain disjoint `data-fit-region` hooks only where the adapted layout has genuinely
   constrained subareas; ordinary flow text uses the enclosing `.fit`. Keep one shared
   page scale and the **11px logical-canvas minimum**. SVG sizes use viewBox units; `PresentationMetrics.fontFactor(element)`
   maps them to logical pixels. Diagnose unresolved fitting through the geometry
   guidance in [typography-fit.md](../references/generate/typography-fit.md).

geometry.css supplies structure, not PPT parsing or the user's visual style.
Its selectors use `.builtin-layout` and zero-specificity `:where()`. Apply only
selected rules to adapted fragments; preserved source layouts keep their own CSS.
Equal columns, `1em` gaps and `contain` are reference starting points.

Source evidence guides adaptation; [qa.md](../references/generate/qa.md) defines final QA and
visual review. Review only QA-designated pages unless a full pass is requested;
no extra review pass is needed solely because a fragment was adapted.

HTML/CSS/SVG remain editable in the HTML template. SVG may rasterise during PPTX
conversion. Use HTML labels when native PPTX text editing is required, and follow
the QA guide's checks for the requested export.
