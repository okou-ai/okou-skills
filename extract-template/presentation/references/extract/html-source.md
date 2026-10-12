# Batch an HTML source

Use during extraction, including HTML prepared from a PDF by [pdf-source.md](pdf-source.md).
That helper already creates the inventory below; continue with its outputs.
Keep the original HTML in the work directory; for a URL,
download its entry HTML once. A dynamic site may need the browser-serialized DOM.
This stdlib-only helper inventories all pages and exports their original
fragments without rewriting their markup:

```bash
python3 scripts/inventory-html.py --input <work-dir>/source.html \
  --base-url <original-url> --out <work-dir>/html
```

Omit `--base-url` for local files. For other class names, use `--slide-class`,
`--stage-class` and, where needed, `--text-class`. The latter summarizes fragmented
text runs per page, without treating them as editable slots. For a directory of
independent pages, reuse the files directly; this helper is for multiple slides
in one document.

Read `html/inventory.json` and the shared CSS together. The report lists page roles,
text regions, source character counts, HTML resource references, scripts and missing
runtime hooks. Character counts are source observations, not measured capacity.
The tool preserves distinct pages even when their layout names repeat.

Copy/adapt the exported `html/source/` fragments into `layouts/source/` in one batch.
Create `source-index.json` from the inventory, adding the original aspect ratio,
purpose and source-grounded capacity guidance. Preserve shared CSS and download/copy
referenced assets in a batch, including dependencies in CSS imports, `url()`, inline
styles and SVG. Resolve each from its source file, then use package-relative paths.

Add `.fit` to the existing content container when it already defines the intended
area; creating another wrapper may change grid/flex layout or direct-child CSS.
Check its bounds against the source. `data-text-role` labels may identify individual
titles; `data-fit-region` belongs on a meaningful containing area, not automatically
on every text element. Keep the source geometry and replace only competing navigation
handlers with the supplied runtime.

Use contact sheets for full page coverage and inspect an individual page/computed
style only to resolve missing details or a distinct layout. No per-page reconstruction,
interaction pass or generated-deck QA is needed to inventory an HTML source.
Finish with the package check in [SKILL.md](../../SKILL.md).
