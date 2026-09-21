# Preserve source layouts and adapt the shared library

Use this reference while extracting a presentation package and writing its authoring instructions. The shared library provides 44 reusable content structures. Their provenance is `generic`; the user's original layouts remain a separate collection with source-page evidence.

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
2. Otherwise consult `layouts/common/catalog.json`. Select by purpose, region types, and `capacity.items`/`capacity.note`, then read only the relevant fragments.
3. If neither collection supports the required relationship, add a documented layout using the same design system.

Do not choose a generic layout merely because it is familiar when a suitable source layout exists. Do not force a source layout to hold incompatible content. Shorten or split dense content before reducing the brand's text hierarchy or margins.

## CSS and framing boundary

The package has three cooperating parts:

| File | Responsibility |
| --- | --- |
| `styles/layout.css` | Namespaced `.pl-*` structures and component geometry for the shared fragments; preserve the installed library copy. |
| `styles/theme.css` | Shared brand palette, typography, spacing, reusable background fields/decorations, borders, and component treatments, using the documented `--pl-*` tokens. |
| `layouts/chrome.html` | Repeated brand framing such as logos, footers, and page markers; style it in the shared theme. |

Read the starter `theme.css` for the supported token names. Map these tokens to the source design system, directly or with `var(--source-token)` aliases. Load `layout.css` first and `theme.css` second. The starter theme is a neutral fallback, not evidence of the user's brand; replace its defaults where the source establishes a rule and label any remaining fallback choices in `design-system.md`.

Use the semantic classes consistently: `.pl-title` identifies a slide title, while `.pl-metric` identifies a prominent value. A title selector must not resize a metric. Shared component overrides belong in `theme.css`, not copied inline into each fragment. Avoid broad element selectors that accidentally change original source layouts; scope common-library adaptations to `.pl-*` classes or the common stage.

The library separates reusable relationships from brand treatment, but it does not claim that every composition is style-independent. Distinctive source geometry remains in source layouts. Brand-specific card, table, or quote treatments can be expressed once in the theme. A structure needing different semantic regions warrants a documented layout, rather than a collection of page-specific CSS exceptions.

Keep source-specific structural styles in an optional `styles/template.css`. Link them from the shell if used, while retaining the same brand typography and color roles. Do not use full-page screenshots as backgrounds to imitate a missing editable layout.

## Background elements and combinations

Extract reusable ingredients from the user's source, then preserve how the source combines them. Record three linked inventories in `design-system.md`:

| Inventory | Record |
| --- | --- |
| Background fields | IDs, source pages, canvas fill and background blocks/bands/splits, their colors, shapes, proportions, edge anchors, and paired foreground/logo treatment. |
| Content-independent decorations | IDs, source pages, editable geometry or asset paths, native colors/aspect ratio, and observed scale, rotation, cropping, opacity, repetition, and placement. Reuse one asset across placements instead of baking a new full-page image for each. |
| Combination recipes | IDs referencing the fields and decorations, source pages, layer order, placements, usable content regions, intended page roles/density, and allowed variations. Mark source-observed combinations separately from inferred adaptations. |

A content-independent decoration can be removed or reused without changing the slide's factual message. Charts, value-encoding shapes, process arrows, product screenshots, and case-specific illustrations belong to content. Card fills or title underlines that move with their content belong to components. A branded edge shape or texture can belong to the background. Judge the element's role rather than its file format or whether it looks decorative.

Implement simple fields and shapes as editable CSS/SVG. Retain isolated original artwork and textures under `assets/` when useful, preserving transparency and aspect ratio. Never crop source text or data into a reusable decoration; when an element is obscured, label any reconstructed geometry as inferred. Preserve original colors and documented alternatives rather than assuming arbitrary recoloring, stretching, or rotation is faithful.

Keep field styles and decoration styles independently reusable in `styles/theme.css`, for example through `data-surface` and `data-decoration` on the outer stage. Names are package-defined, not a universal palette. A recipe selects a compatible pair and its placement; it need not duplicate content HTML or become a flattened image. For example, a package that actually defines these two elements could assemble:

```html
<div class="stage pl-stage" data-layout="two-column"
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

The shared stage has a base `--pl-bg` color and two optional layers behind content:

| Layer | Shared tokens | Use |
| --- | --- | --- |
| Background field/image (`::before`) | `--pl-bg-image`, `--pl-bg-size`, `--pl-bg-position`, `--pl-bg-repeat`, `--pl-bg-opacity` | Source-derived photography, texture, or color-field composition. |
| Decorative motif (`::after`) | `--pl-motif-image`, `--pl-motif-size`, `--pl-motif-position`, `--pl-motif-repeat`, `--pl-motif-opacity` | Source-derived ornaments, cropped edge shapes, or repeated marks. |

Both image tokens default to `none`. Values accept normal CSS background syntax, including multiple images; asset URLs resolve relative to `styles/theme.css`. These layers neither occupy layout space nor intercept clicks. Keep meaningful images in content regions, and logos/footers in chrome; do not repeat the same ornament in both chrome and a background layer.

Each surface must specify its compatible ink, muted text, accent, panel, border, chart-series and table-header colors, plus the appropriate logo. Changing the base color alone is insufficient. Place visible motifs in the source's permitted areas—typically empty edges, display-title areas, or behind opaque panels. Do not use low-opacity texture as a substitute for checking actual text contrast.

Check the source-observed recipes and representative documented adaptations on compatible layouts. Also confirm that one unchanged layout can switch between compatible recipes without moving its content or altering its typography. Source layout, element, and combination evidence remain separate from the generic layout catalog.

## Installing and assembling

From the extraction skill directory:

```bash
node scripts/install-layout-library.mjs --package <template-slug>
```

The installer copies the shared fragments and catalog to `layouts/common/`, the structural CSS to `styles/layout.css`, and starter theme/shell/chrome files only when absent. It never replaces existing source files or customized theme/shell/chrome. Repeated installation with identical library files is safe. A differing shared fragment, catalog, or structural stylesheet stops installation before writes; install the newer library into a fresh directory for an explicit comparison. Symlinked package destinations are rejected.

The default `_shell.html` links `../styles/layout.css` and `../styles/theme.css`. It has exactly one `<!-- BEGIN SLIDES -->` / `<!-- END SLIDES -->` pair and supports all four arrow keys. Keep those links and markers when customizing the shell if using the preview helper.

Common fragments contain only their editable content structure. Assemble each as:

```html
<section class="slide">
  <div class="stage pl-stage" data-layout="chosen-layout-id">
    <!-- Insert the shared layouts/chrome.html here. -->
    <!-- Insert the selected layouts/common/<id>.html here. -->
  </div>
</section>
```

Keep package-relative asset links valid at the assembled HTML's location. The preview helper writes to `layouts/preview.html`, beside `_shell.html`; paths such as `../assets/logo.svg` resolve from there. If the final deck is assembled elsewhere, adjust all resource paths together. Source layouts may use their own composition inside the shared canvas; document their assembly and content regions in the package's README.

Generate the common-layout preview after adapting the theme:

```bash
node scripts/preview-layouts.mjs --package <template-slug>
npx --yes --package="${CLI_PKG_URL}" okou presentation screenshot \
  --input <template-slug>/layouts/preview.html \
  --out <validation-dir>
```

Check every common layout with the brand theme, including dense metrics/tables and the languages the template must support. Use representative source-page content for comparison examples. The package's production `SKILL.md` must name the source index, common catalog, both shared stylesheets, and chrome path explicitly; a layout collection that later authors do not read will not improve their output.

Keep preview renders separate from the ordered original source-page images. Only the original source screenshots go to the publication command's `--pages` directory.
