---
name: office-files
description: Generate or edit docx, xlsx and PDF deliverables with reusable document styling, preserved source layouts, and rendered-page verification.
---

# Office files

Keep content, layout and output format separate. Use the same document foundation
for PDF and Word; do not classify requests into a fixed list of document types.
A filename extension selects a renderer, not a writing structure.

## Choose from the actual constraints

- **New prose, no supplied template:** author Markdown, then use the default
  renderer below. It provides readable body text, heading hierarchy, lists,
  tables, captions, page numbers and pagination without inventing branding,
  a cover, sections, or a page-count target.
- **A selected template/package:** follow its own authoring instructions and
  preserve its style. Run the rendered-page check below on the final PDF too.
  A `reference.docx` carries styles; it does not carry the source's body,
  fixed positions, forms, signatures, fields or reusable content skeleton.
- **Editing an existing document:** start from that file. Preserve required
  wording, fields, relationships and layout. Make focused edits in its native
  source. Do not round-trip an existing Word file through Markdown and claim
  that its structure is preserved. The renderer accepts a finished DOCX
  without rewriting its bytes and produces its PDF preview/export.
- **Fixed-position layout or a native PDF template:** use the template's native
  renderer/source. Apply the shared checks to the resulting PDF. Do not force
  it into the flowing-prose default, rasterise whole pages, or rebuild untouched
  content merely to change the delivery format.
- **Spreadsheet calculations or tabular data:** use openpyxl; see xlsx below.

Read [references/document-layout.md](references/document-layout.md) when
selecting language, arranging figures/tables, preserving templates, or resolving
an inspection finding. Infer constraints from the request and source; ask only
when missing information changes the intended result.

## Setup for PDF / Word

Resolve this skill's directory as `OFFICE_FILES_DIR` in each shell invocation.
The scripts find the bundled Pandoc binary themselves, so PATH setup is unnecessary.

```bash
pip install --break-system-packages --quiet -r "$OFFICE_FILES_DIR/requirements.txt"
```

The default route requires LibreOffice **Writer** for both PDF export and Word
preview. If the renderer reports it missing, install it and retry:

```bash
sudo apt-get update -qq
sudo apt-get install -y -qq libreoffice-writer
```

Fonts must be installed on the rendering host. The Okou image carries Noto Sans,
Noto Sans CJK and Noto complex-script families. Check `fc-match` if a font warning
or wrong glyph shape appears. Dependencies are pinned in `requirements.txt`;
`render.json` records the actual Pandoc and LibreOffice versions used.

If the toolchain is unavailable, explain the blocked export/preview. Return a
usable source when possible, clearly marked as not visually verified. Do not
claim a successful PDF or verified Word file, or silently change the format.

## New prose: render one source

Write `doc.md` with semantic headings, paragraphs, lists, tables, captions,
footnotes and images. Set language in YAML (`lang: zh-CN`, `en-US`, `ja-JP`, `ar`,
etc.) or pass `--lang`. Metadata is optional; do not invent title/author/date.

```bash
python3 "$OFFICE_FILES_DIR/scripts/render_document.py" doc.md \
  --out generated/document --format both --lang zh-CN
```

`--format pdf|docx|both` chooses delivery files. Both formats are rendered so the
PDF also serves as Word's visual preview. Deliver only the requested format;
attach the editable source alongside a final PDF when appropriate.

The default theme is applied only to new, untemplated Markdown. For a style-only
reference supplied for new prose:

```bash
python3 "$OFFICE_FILES_DIR/scripts/render_document.py" doc.md \
  --out generated/document --format both --reference theme.docx
```

For a finished or edited Word source:

```bash
python3 "$OFFICE_FILES_DIR/scripts/render_document.py" edited.docx \
  --out generated/document --format both
```

The input and output directories must differ when their filenames would collide.
Original documents/references are never overwritten or house-styled. The default
flow exports PDF from the actual delivered DOCX, rather than generating the two
formats independently. LibreOffice's rendering is verified; fidelity in every
Word version is not implied.

Outputs include `render.json` (inputs, hashes, engine versions, delivery choices)
and `expectations.json` (heading/opening-text relationships). Add important exact
wording and figure/reference pairs to the expectations when relevant. Compilation
alone leaves the candidate in `needs-inspection` state.

## Inspect, repair, then deliver

```bash
python3 "$OFFICE_FILES_DIR/scripts/check_document.py" inspect \
  generated/document/doc.pdf --docx generated/document/doc.docx \
  --render generated/document/render.json \
  --expectations generated/document/expectations.json --out generated/document/qa
```

Pass `--render` for this helper's output: it binds the source, reference, local
image resources and completed render to the inspected files. A failed new
render cannot reuse an old export's acceptance. For native PDF output omit
`--docx` and `--render`; provide expectations when source relationships are
known. Read `inspection.json`, open the generated page images, and review
**every page** for legibility/density, hierarchy, pagination/grouping and
figures/tables. Inspect Word's actual exported pages, not its XML alone.

- Fix machine blockers and visual defects in the source/style and rerender.
- Do not reduce font size or squeeze spacing merely to fit fewer pages.
- Complete each page's `review.json` observations only after inspecting it;
  acknowledge heuristic warnings with a concrete reason. A generated review
  form or a contact sheet alone is not visual acceptance.
- Use at most two repair rounds. If still blocked, explain the specific defect
  and provide the source or a clearly identified draft; do not label it final.

```bash
python3 "$OFFICE_FILES_DIR/scripts/check_document.py" accept generated/document/qa
```

`READY_TO_DELIVER` requires completed page reviews, no unresolved blockers and
unchanged input/page hashes. Changes to the PDF, paired DOCX, expectations,
render manifest or its bound source/reference/resources invalidate inspection.
Rerun `accept` immediately before upload; reinspect and review changed files.
The checks cover geometry, text extraction and declared relationships; they are
not PDF/UA certification or a guarantee of aesthetic quality.

Deliver with `okou web upload-file`. Keep source, `render.json` and QA evidence
for revisions. State material verification limits without burdening users with
internal tool details.

## xlsx

For spreadsheets alone, install only the spreadsheet dependency:

```bash
pip install --break-system-packages --quiet openpyxl==3.1.5
```

Build/read the workbook with openpyxl, not a Markdown table or Pandoc. Start from
the user's workbook for edits and preserve unrelated sheets/formulas.

```python
import openpyxl

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Q3"
ws.append(["Region", "Q2", "Q3", "Delta"])
ws.append(["APAC", 120, 148, "=C2-B2"])
wb.save("out.xlsx")
```

Excel calculates formulas when opened. If values must already be available,
verify them separately and explain any uncached formula results. Never claim
that writing a formula recalculates it. Deliver with `okou web upload-file`.
