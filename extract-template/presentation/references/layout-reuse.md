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
| `styles/theme.css` | Shared brand palette, typography, spacing, background variants, borders, and component treatments, using the documented `--pl-*` tokens. |
| `layouts/chrome.html` | Repeated brand framing such as logos, footers, page markers, and motifs; style it in the shared theme. |

Read the starter `theme.css` for the supported token names. Map these tokens to the source design system, directly or with `var(--source-token)` aliases. Load `layout.css` first and `theme.css` second. The starter theme is a neutral fallback, not evidence of the user's brand; replace its defaults where the source establishes a rule and label any remaining fallback choices in `design-system.md`.

Use the semantic classes consistently: `.pl-title` identifies a slide title, while `.pl-metric` identifies a prominent value. A title selector must not resize a metric. Shared component overrides belong in `theme.css`, not copied inline into each fragment. Avoid broad element selectors that accidentally change original source layouts; scope common-library adaptations to `.pl-*` classes or the common stage.

The library separates reusable relationships from brand treatment, but it does not claim that every composition is style-independent. Distinctive source geometry remains in source layouts. Brand-specific card, table, or quote treatments can be expressed once in the theme. A structure needing different semantic regions warrants a documented layout, rather than a collection of page-specific CSS exceptions.

Keep source-specific structural styles in an optional `styles/template.css`. Link them from the shell if used, while retaining the same brand typography and color roles. Do not use full-page screenshots as backgrounds to imitate a missing editable layout.

## Background variants

Preserve observed background treatments as theme variants rather than flattening the deck to one solid color. In `design-system.md`, record each variant's source pages, base color, image/texture assets, placement/crop/scale, paired text/logo colors, and suitable page roles or content density. Quiet pages are an intentional variant too. Do not prescribe a number of variants, a color rotation, or decorations absent from the source.

Select the layout for its content relationships and capacity, then select a compatible background for the slide's role, readability, and the deck's visual rhythm. Use a separate stage attribute such as `data-surface="accent"`; names are package-defined, not a universal palette. The same layout can use several surfaces without copying its fragment. A theme may provide layout-based defaults, but an explicit surface must override those defaults.

The shared stage has a base `--pl-bg` color and two optional layers behind content:

| Layer | Shared tokens | Use |
| --- | --- | --- |
| Background field/image (`::before`) | `--pl-bg-image`, `--pl-bg-size`, `--pl-bg-position`, `--pl-bg-repeat`, `--pl-bg-opacity` | Source-derived photography, texture, or color-field composition. |
| Decorative motif (`::after`) | `--pl-motif-image`, `--pl-motif-size`, `--pl-motif-position`, `--pl-motif-repeat`, `--pl-motif-opacity` | Source-derived ornaments, cropped edge shapes, or repeated marks. |

Both image tokens default to `none`. Values accept normal CSS background syntax, including multiple images; asset URLs resolve relative to `styles/theme.css`. These layers neither occupy layout space nor intercept clicks. Keep meaningful images in content regions, and logos/footers in chrome; do not repeat the same ornament in both chrome and a background layer.

Define surface selectors in `theme.css`, for example `.pl-stage[data-surface="accent"]`. Each variant must specify its compatible ink, muted text, accent, panel, border, chart-series and table-header colors, plus the appropriate logo. Changing the base color alone is insufficient. Place visible motifs in the source's permitted areas—typically empty edges, display-title areas, or behind opaque panels—and retain quiet backgrounds for dense content when that matches the source. Do not use low-opacity texture as a substitute for checking actual text contrast.

Check each defined background variant on representative compatible layouts. Also confirm that one unchanged layout can switch between compatible surfaces without moving its content or altering its typography. Source layout and background evidence remain separate from the generic layout catalog.

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
