# Native authoring

Use these helpers for new documents with the blank baseline. For existing files or layouts the helpers cannot express, use the native libraries directly.

## Prepare once

From your working directory, replace `<skill-dir>` with this skill's absolute path:

```bash
python3 <skill-dir>/scripts/office_env.py --formats docx pdf --install-missing
```

Select needed formats (`docx`, `pdf`, `xlsx`); add `--charts` only for charts. Use the returned `python` path in subsequent commands. The [helper](../scripts/office_env.py) reuses available packages, installs missing ones into `.office-cache/venv`, and leaves system Python unchanged. For DOCX, it installs missing Writer components where supported and caches a real import probe. Font mappings still need language-coverage checks; unavailable rendering remains unverified.

## Write shared content once

Add `<skill-dir>/scripts` to your Python import path. Pass content and computed values once:

```python
from office import OfficeDocument

report = OfficeDocument()
report.title(title)
report.paragraph(summary)
report.heading(section_title)
report.paragraph(section_text)
report.table(headers, rows, numeric_columns=(1, 2), widths=(2, 1, 1))
report.list(next_actions, numbered=True)
report.figure(chart_path, caption=chart_caption, source=source_note)
report.save("output", name="report", formats=("docx", "pdf"))
```

Variables illustrate methods, not required report fields. `OfficeDocument` inherits both blank assets, escapes text, repeats bold table headers, right-aligns numeric cells, and preserves image proportions. Draw charts at their placed size. `save()` checks the Word baseline before writing editable DOCX and/or independently compiling Typst PDF.

`report.word` and `report.preamble` allow native layout/language changes. `baseline_check=False` is for deliberately different user/template designs, not unresolved baseline defects.

When authoring directly:

- **Word:** open `assets/blank.docx` with `python-docx.Document`. Apply `Title`, `Heading 1`–`Heading 3`, `Normal`, `List Bullet`/`List Number`, `Table Text`/`Table Header`/`Table Title`, `Figure`, `Caption`, and `Source` styles.
- **PDF:** copy `assets/blank.typ`, append content using `#doc-title[...]`, headings, tables, and figure captions, then run `typst compile report.typ report.pdf` or `typst.compile('report.typ', output='report.pdf')` in Python. Copying preserves the top-level style rules.

## Check and render together

Use the selected Python path. Run the checker separately only when authoring outside `OfficeDocument`:

```bash
python <skill-dir>/scripts/check_docx.py output/report.docx
python <skill-dir>/scripts/review.py output/report.docx output/report.pdf
```

The checker detects known DOCX size, alignment, header, image-spacing, and font-theme defects. `review.py` renders actual DOCX/PDF files together and reuses results only while file bytes, renderers, and fonts remain unchanged; identical failed conversions are cached too. Neither structural checks nor cached page images replace visual inspection. Write/compile/render timings cover those commands only.
