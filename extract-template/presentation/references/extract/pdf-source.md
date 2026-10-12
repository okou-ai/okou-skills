# Route a PDF deck through HTML extraction

Use **PDF → pdf2htmlEX → the HTML extraction flow**. Keep the original PDF as the
capture and upload source. Conversion supplies positioned HTML, CSS and assets;
full-deck manual reconstruction from screenshots is no longer needed.

From this guide's directory:

```bash
python3 scripts/prepare-pdf.py --input <source.pdf> --work-dir <work-dir>
```

The helper reuses an installed `pdf2htmlEX`, or caches the pinned official Linux
x86_64 AppImage without root/FUSE. `--converter <executable>` selects an existing
installation. It uses the converter's visual defaults, writes resources as separate
files, then runs the shared HTML inventory with `.pf` pages, `.pc` content and `.t`
text lines. Other platforms need an installed converter.

| Output | Use |
| --- | --- |
| `pdf-html/source.html` and sibling resources | Converted source for HTML extraction |
| `pdf-html/conversion.json`, `conversion.log` | Source hash, converter version, timings and diagnostics |
| `html/inventory.json`, `html/source/` | Existing HTML inventory and unchanged page fragments |

Continue [html-source.md](html-source.md) at **reading the inventory and shared
CSS**; no second inventory pass is needed. Render the original PDF once into
`source-pages/` as described in [SKILL.md](../../SKILL.md). Match its page count and
order to the inventory, and review the original contact sheets for layout roles.
Keep the original PDF filename/page mapping in `source-index.json`; record the
conversion in `design-system.md`.

When adapting the converted fragments:

- Preserve page geometry, generated CSS, fonts, background assets and text spans.
  Wrap each `.pf` in `.slide`, make `.pf` the `.stage`, and preserve `.pc` geometry
  while adding `.fit` for editable content. Keep page backgrounds and fixed
  footer/logo chrome outside `.fit`.
- Replace the converter's viewer/sidebar/zoom scripts with the installed shared
  runtime. Keep `.pc` visible without the converter's lazy-rendering script. The
  template runtime provides the black surround, scaling, centering and navigation.
- Check visible text against the PDF before naming editable slots. Type 3 fonts
  and scanned pages may leave hidden text or lettering painted into background
  images; editable slots require visible, replaceable text. Record flattened regions
  and encoding differences. Adapt only regions needed for reusable content, clearing
  original lettering before replacement; keep any unresolved regions as reference-only.

Use the existing package check and original PDF upload. No second PDF export,
converter-parameter sweep or generated-deck QA pass is needed for extraction.
