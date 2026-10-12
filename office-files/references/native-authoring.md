# Reuse the native tools

These helpers serve new documents using the blank baseline. They supply typography and mechanical checks, not a business outline, fixed page count, or palette. For existing files, user templates, complex layouts, or language-specific typesetting, use the native libraries directly and preserve the requested design.

## Prepare once

From your working directory, replace `<skill-dir>` with this skill's absolute directory and run:

```bash
python3 <skill-dir>/scripts/office_env.py --formats docx pdf --charts --install-missing
```

Select only the formats needed; omit `--charts` without charts. Use the returned `python` path for subsequent commands, without shell activation. The helper prefers a working `/opt/office/bin/python`, reuses installed libraries, or creates `.office-cache/venv` on older hosts. It installs missing Writer components before one real DOCX probe. Failed probes are cached until the renderer changes. Font mappings are reported, not silently accepted as language coverage. On hosts without apt/sudo, use an available compatible renderer or report Word rendering as unverified.

New Okou images can preinstall the packages and fonts at image-build time. The helper also supports old images and other hosts; a PR alone is not evidence that a runtime has the new image.

## Write shared content once

Add `scripts/` to your generator's Python import path, then use the small `OfficeDocument` helper for ordinary prose, lists, tables, and images:

```python
from office import OfficeDocument

report = OfficeDocument()
report.title(title)
report.paragraph(summary)
for section in sections:
    report.heading(section["heading"])
    report.paragraph(section["text"])
report.table(headers, rows, numeric_columns=(1, 2), widths=(2, 1, 1))
report.list(next_actions, numbered=True)
report.figure(chart_path, caption=chart_caption, source=source_note)
result = report.save("output", name="report", formats=("docx", "pdf"))
print(result)
```

The variable names above are illustrative, not required report fields. Compute the underlying values once in Python and reuse them in prose, table rows, and chart data. Plain strings are escaped as literal Typst text. Both formats inherit the blank assets; tables get bold repeated headers, 11 pt text, and right-aligned numbers. Images preserve their aspect ratio and use automatic Word line spacing. Draw charts at their intended placed width so labels keep their specified size.

`report.word` exposes the python-docx document; `report.preamble` is the copied Typst baseline. Adapt both when changing page settings, fonts, or language direction. Use native authoring directly when the helper does not cover the task; do not build a second copy of the content. `save(..., baseline_check=False)` is for a deliberately different user/template design, not a way to bypass a baseline defect.

## Check and render together

`save()` runs a structural Word style check before writing. For a document created directly with python-docx, use:

```bash
python <skill-dir>/scripts/check_docx.py output/report.docx
python <skill-dir>/scripts/review.py output/report.docx output/report.pdf
```

Use the selected Python executable in place of `python`. The checker catches common baseline regressions: type sizes, table headers, numeric alignment, exact-height image paragraphs/rows, and theme-font overrides. It does not prove full multilingual rendering or inspect PDF typography.

The review command batches independent formats and caches conversions/page images against file bytes, renderer versions, and installed fonts. It preserves differing Word/PDF page counts. Reuse cached images for unchanged pages; inspect every final page, including downstream reflow, and verify content and numbers. A cache hit is not a new visual review. Mixed portrait/landscape PDFs use Poppler directly to preserve each page's dimensions.

Keep `.typ` sources, page PNGs, caches, and timing output local. Only upload the files needed by the user. Measured write/compile/render durations exclude content authoring, reasoning, visual review, and delivery.
