# Render and integrate

`render.py` composes the same literal content model through HTML and native
adapters. The maintained themes, recipes, and CSS are owned by this package.
There is no runtime fetch from Open Design.

## HTML

```bash
python3 <layout-dir>/scripts/render.py report.json --format html --out ./output
```

This writes `index.html` and any content-addressed local images. Styles and
SVG charts are embedded. Text, image alternatives, and supplied metadata are
escaped. Two-column prose has sequential DOM order; narrower screens use a
single column. Print styles remove the browser canvas and preserve margins.
Print/PDF exporters still need actual pagination inspection.

Use the current `okou generate report` packet for output paths and delivery.
For a new report without an explicitly selected layout, this package supplies
the layout resources. A user's selected template or visual system takes
priority; apply only compatible components instead of replacing that choice.
Other artifact categories may reuse the components when appropriate, but this
package does not redefine their generation pipelines.

## Editable Word and native PDF

Read the installed `office-files` skill and prepare only the needed formats:

```bash
python3 <office-files-dir>/scripts/office_env.py --formats docx pdf --install-missing
```

Use the Python executable returned by that command:

```bash
<office-python> <layout-dir>/scripts/render.py report.json --format docx pdf \
  --office-dir <office-files-dir> --out ./output
```

Native adapters inherit the Office blank assets. Word uses actual paragraphs,
editable table cells, and section columns. PDF compiles independently with
Typst. The adapters preserve the 12 pt body, 11 pt data-table text, and 10 pt
captions; display-number emphasis has its own role. Font slots and script
fallbacks stay separate. Word/PDF may have different page counts and line wraps.

Charts use the same coordinates and supplied values across formats. Word draws
the shared geometry as a high-resolution PNG through Pillow (`--charts` during
Office setup); PDF and HTML use SVG. PNG/JPEG figures need no chart dependency. Figure sizes must
fit the current column or span both columns.

Native metric, quotation, figure and chart units retain their associated
labels, attributions, captions and supplied source notes at page/column breaks.
PDF units taller than a full text area remain breakable; long prose and tables
continue in normal document flow. Line-chart gutters and wrapped label spacing
adapt to the placed label size rather than clipping labels in narrow grids.

Word's sidebar, metric-strip, and modular layouts use editable layout tables.
Their prose keeps 12 pt body text; actual data tables use 11 pt text. A checker
that assumes every Word table is a data table needs this distinction when
reviewing these deliberate layouts.

The renderer handles layout and known input-shape errors. Use Office's actual
file rendering and the owning quality workflow for broader acceptance. The
library does not score analysis or facts.

## Preview library

```bash
python3 <layout-dir>/scripts/preview.py --out ./layout-preview
```

The preview contains all three recipes in all four themes. Each report uses
the production renderer and an explicitly labeled illustrative fixture. Theme
and recipe choices link to full report pages, not imagined thumbnails. Publish
the preview with `okou host` when a browsable review is requested.

## Maintenance

Edit semantic tokens in `themes.json`, layout defaults in `recipes.json`, and
components in the renderer/CSS. `catalog.json` owns the full vocabulary and
its provenance. Regenerate the preview from those sources after changes.
The package lives at the repository root as `artifact-layout/`. It is synced
as its own skill, independently of `gen`. A companion application change adds
it to the default skill set. Merge and sync this package before enabling that
default. Office report creation can read the same installed skill; preserve
existing Office authoring and quality procedures.
