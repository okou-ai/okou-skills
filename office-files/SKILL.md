---
name: office-files
description: Create and edit Word, PDF and Excel files, verify the results, and deliver them.
---

# Office files

## 1. Choose a tool

Read the guide for the selected route:

| Task | Tool and guide |
| --- | --- |
| Create or edit Word | `docx`, `python-docx`, `docxtpl` or targeted OOXML edits — [Word](references/word-authoring.md) |
| Create or edit PDF | ReportLab, Typst, HTML/CSS or native PDF tools — [PDF](references/pdf-authoring.md) |
| Simple text-led Word/PDF | Optional [Pandoc](references/pandoc-authoring.md); existing Pandoc publishing workflows can continue using their filters and templates |
| Create or edit Excel | openpyxl |

Follow a supplied template's instructions. For matching Word/PDF deliverables,
export the finished DOCX to PDF.

## 2. Create or edit

Install only the selected tool's dependencies from its guide. For Excel:

```bash
python3 -m pip install --break-system-packages --quiet openpyxl==3.1.5
```

Work on a copy of an existing file; preserve content and formatting outside the
requested changes. When layout must be preserved, inspect the original pages
before editing.

For Word/PDF, read [layout and rendering setup](references/document-layout.md),
then create or edit the document with the selected tool. Set `OFFICE_FILES_DIR` to this
skill's absolute directory in each shell invocation.

For Excel, create or edit the workbook with openpyxl and preserve unrelated
sheets and formulas.

## 3. Check the result

**Word/PDF:** prepare the `.docx`, `.pdf` or Pandoc `.md` in a separate output
directory. Use the actual source filename and resources; for example:

```bash
python3 "$OFFICE_FILES_DIR/scripts/render_document.py" document.docx \
  --out generated/document --resource build_docx.py
```

Repeat `--resource` for the external authoring script, original/template, data
and assets used. For Pandoc Markdown, set `lang` in YAML or pass `--lang`;
use `--reference` only for a style reference for new prose.

DOCX/Markdown produces a DOCX and a PDF preview; native PDF stays PDF. Add any
required exact wording or same-page relationships to `expectations.json` using
[the expectations format](references/document-layout.md#content-expectations).
Then inspect the prepared files:

```bash
python3 "$OFFICE_FILES_DIR/scripts/check_document.py" inspect \
  generated/document/document.pdf --docx generated/document/document.docx \
  --render generated/document/render.json \
  --expectations generated/document/expectations.json --out generated/document/qa
```

For native PDF, omit `--docx`. Adapt the filenames to the actual outputs.

Open every generated page image. Review legibility, hierarchy, composition,
pagination and tables/figures against [the review criteria](references/document-layout.md#page-review).
In `review.json`, record observations for all five criteria, mark each `pass`
only after checking it, and explain every warning. Fix defects in the source,
regenerate and prepare the document, reapply request-specific expectations,
then inspect again.

**Excel:** reopen the workbook and verify its data and formulas. When calculated
values are required, recalculate with a spreadsheet engine and verify the
results; openpyxl does not evaluate formulas.

## 4. Deliver

For Word/PDF, run acceptance immediately before upload:

```bash
python3 "$OFFICE_FILES_DIR/scripts/check_document.py" accept generated/document/qa
```

Deliver Word/PDF after `READY_TO_DELIVER`. If an input or output changes, regenerate
and inspect it again. If a tool or source limitation blocks completion, state
the issue and label any delivered file as a draft or unverified source.

Upload with `okou web upload-file`. Deliver the requested format; attach the
editable source alongside a final PDF when appropriate. Keep authoring sources,
data, assets and QA files for revisions.
