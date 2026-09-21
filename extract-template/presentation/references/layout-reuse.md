# Preserve source layouts and compose extracted backgrounds

Use this reference while extracting a presentation package and writing its authoring instructions. Preserve the user's source layouts and separately reusable background elements, with source-page evidence and guidance for composing new slides.

## Source inventory and selection

Inspect every source page before grouping layouts. Two pages can share a layout when they have equivalent content regions, proportions, and hierarchy; preserve different background treatments as separate theme variants. A split cover and centered cover are distinct even though both are covers. Record intentional layout variants rather than flattening them into a few representative pages.

Write `layouts/source-index.json` and summarize it in `layouts/README.md`. A useful entry is:

```json
{
  "source": { "name": "reference.pptx", "pageCount": 12, "aspectRatio": "16:9" },
  "layouts": [
    {
      "id": "source-split-cover",
      "file": "source/split-cover.html",
      "sourcePages": [1],
      "purpose": "Opening with a title region and a separate image region",
      "regions": [
        { "name": "title", "type": "text" },
        { "name": "visual", "type": "image" }
      ],
      "capacity": { "items": [1, 1], "note": "One short title and one image; preserve the observed title hierarchy." }
    }
  ]
}
```

This example shows one entry; a completed index accounts for every input page. Preserve the original ratio in the record when adapting its proportions to the required 16:9 output. Record any material adaptation. Capacities describe intended content roles and approximate limits, not measured guarantees across languages or fonts.

For each new slide, use this order:

1. Read the source index and choose an original layout if its regions and capacity fit.
2. If no source layout supports the required content relationship, add a documented layout using the same design system.

Do not replace a suitable source layout merely because another composition is familiar. Do not force a source layout to hold incompatible content. Shorten or split dense content before reducing the brand's text hierarchy or margins.

## CSS and framing boundary

The package has three cooperating parts:

| File | Responsibility |
| --- | --- |
| `layouts/source/` | Editable compositions preserved from the source, with semantic content regions and usage guidance in the source index. |
| `styles/template.css` | Shared brand palette, typography, spacing, background fields/decorations, component treatments, and layout rules extracted from the source. |
| `layouts/_shell.html` | Shared canvas, stylesheet/font links, navigation, and repeated framing such as logos, footers, and page markers. |

Define shared CSS variables and semantic classes from the source design system. Keep title and metric roles distinct so title styling does not accidentally resize prominent values. Shared component rules belong in the stylesheet rather than being copied inline into individual pages. Label fallback choices for elements the source does not establish in `design-system.md`.

Preserve distinctive source geometry. Keep brand-specific card, table, quote and framing treatments shared across layouts. A structure needing different semantic regions warrants a documented layout rather than page-specific CSS exceptions. Do not use full-page screenshots as backgrounds to imitate a missing editable layout.

## Background elements and combinations

Extract reusable ingredients from the user's source, then preserve how the source combines them. Record three linked inventories in `design-system.md`:

| Inventory | Record |
| --- | --- |
| Background fields | IDs, source pages, canvas fill and background blocks/bands/splits, their colors, shapes, proportions, edge anchors, and paired foreground/logo treatment. |
| Content-independent decorations | IDs, source pages, editable geometry or asset paths, native colors/aspect ratio, and observed scale, rotation, cropping, opacity, repetition, and placement. Reuse one asset across placements instead of baking a new full-page image for each. |
| Combination recipes | IDs referencing the fields and decorations, source pages, layer order, placements, usable content regions, intended page roles/density, and allowed variations. Mark source-observed combinations separately from inferred adaptations. |

A content-independent decoration can be removed or reused without changing the slide's factual message. Charts, value-encoding shapes, process arrows, product screenshots, and case-specific illustrations belong to content. Card fills or title underlines that move with their content belong to components. A branded edge shape or texture can belong to the background. Judge the element's role rather than its file format or whether it looks decorative.

Implement simple fields and shapes as editable CSS/SVG. Retain isolated original artwork and textures under `assets/` when useful, preserving transparency and aspect ratio. Never crop source text or data into a reusable decoration; when an element is obscured, label any reconstructed geometry as inferred. Preserve original colors and documented alternatives rather than assuming arbitrary recoloring, stretching, or rotation is faithful.

Keep field styles and decoration styles independently reusable in the shared stylesheet, for example through `data-surface` and `data-decoration` on the outer stage. Names are package-defined, not a universal palette. A recipe selects a compatible pair and its placement; it need not duplicate content HTML or become a flattened image. For example, a package that actually defines these two elements could assemble:

```html
<div class="stage" data-layout="source-two-column"
     data-surface="paper" data-decoration="arc-upper-right">
  <!-- Shared chrome and the chosen editable content fragment. -->
</div>
```

Use the surface selector for the base fill, color fields, and foreground palette, and the decoration selector for motif geometry/assets and placement. Scope compatible motif color/asset variants to their surface when required by the source. Document which pairs are valid; extracting two fields and three decorations does not establish six usable combinations. A theme may supply defaults, but explicit choices must override them.

The generated package's authoring instructions must describe how to choose and combine these elements:

1. Prefer an observed recipe that suits the page's role and content density. Preserve its paired text, logo, component, and chart colors.
2. Check that the selected layout's content regions respect the recipe's usable area. Keep the source-first selection order above. Layout and background remain separately reusable, but a large background block can constrain the space available to content.
3. If adaptation is needed, stay within the documented placement, scale, crop, color, and repetition rules; record an inferred combination as such. Keep decorations out of body-copy regions unless the source explicitly supports that treatment.
4. For dense content, prefer a compatible quiet recipe, including no decoration when appropriate. If a combination cannot fit, prefer changing the recipe before revisiting the layout. Do not displace a fitting source layout or shrink the brand's typography solely to accommodate decoration.

Quiet source pages are intentional recipes too. Do not impose a fixed number of backgrounds, rotate colors mechanically, or invent decorations to fill an inventory. Preserve visual rhythm through the source's page-role guidance rather than binding one background permanently to each layout ID.

Implement background fields and decorative motifs as separate layers behind content, using CSS backgrounds, pseudo-elements, or editable positioned shapes as appropriate to the source. Decorative layers must not intercept clicks or change content flow. Keep meaningful images in content regions and logos/footers in shared framing; do not repeat the same ornament in both framing and a background layer.

Each surface must specify its compatible ink, muted text, accent, panel, border, chart-series and table-header colors, plus the appropriate logo. Changing the base color alone is insufficient. Place visible motifs in the source's permitted areas—typically empty edges, display-title areas, or behind opaque panels. Do not use low-opacity texture as a substitute for checking actual text contrast.

Check the source-observed recipes and representative documented adaptations on compatible layouts. Also confirm that one unchanged layout can switch between compatible recipes without moving its content or altering its typography. Keep source layout, element, and combination provenance explicit.

## Package authoring guidance

Document in the generated `SKILL.md` and `layouts/README.md` how to read the source index, select layouts and background recipes, and assemble editable content with the package's shell and shared styles. Keep asset paths relative to the assembled HTML's location; if it moves, update its resource paths together. A layout or recipe inventory that later authors do not read will not improve their output.

Keep preview renders separate from the ordered original source-page images. Only the original source screenshots go to the publication command's `--pages` directory.
