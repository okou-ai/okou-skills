---
name: office-files
description: Create and edit Word, PDF and Excel files using task-appropriate authoring tools, preserved source layouts, and rendered-page verification.
---

# Office files

Keep content, layout and output format separate. Choose tools from the task and
preservation requirements, not a mandatory intermediate format. Keep the actual
authoring source, data and assets for revisions. Do not classify requests into a
fixed list of document types or impose one writing structure.

## Choose from the actual constraints

| Task or constraint | Authoring route |
| --- | --- |
| New editable Word with deliberate sections, tables or page layout | Native `docx` (Node.js) or `python-docx`; read [Word authoring](references/word-authoring.md) |
| Edit existing Word, fill slots, retain revisions/comments/fields | Work on a copy of the supplied DOCX; choose focused library edits or OOXML patches from the Word guide |
| New flowing prose naturally expressed as Markdown | Use the optional Pandoc prose route below, or Pandoc's appropriate reader, filters and writer |
| PDF-only with designed typography, multi-column or fixed-position layout | ReportLab, native Typst, or a working HTML/CSS renderer; read [PDF authoring](references/pdf-authoring.md) |
| Modify an existing PDF or fill its fields | Preserve the PDF and use native field editing or targeted overlays; see the PDF guide |
| Matching Word and PDF deliverables | Author Word with the chosen tool, then export the actual DOCX to PDF |
| Selected template/package | Follow its native recipe and preserve its content/layout contract |
| Spreadsheet calculations or tabular data | Use openpyxl; see xlsx below |

Render supplied documents before editing when their layout matters. A Pandoc
`reference.docx` supplies styles, not a preserved body, form, fixed geometry or
content skeleton. Do not round-trip existing Word through Markdown and claim
preservation. Keep untouched content native and editable; do not flatten pages
to images. New documents may define styles directly in code or native templates.

Read [document-layout.md](references/document-layout.md) for page design and
verification. Read only the authoring guide needed for the selected route.
Infer ordinary details; ask only when missing information changes the result.

## Shared verification setup

Resolve this skill's directory as `OFFICE_FILES_DIR` in each shell invocation.
Install only the selected route's dependencies. The shared PDF inspector needs:

```bash
python3 -m pip install --break-system-packages --quiet PyMuPDF==1.28.2
```

Word preview/export also needs LibreOffice **Writer**; a native PDF does not.
If conversion reports a missing Writer/filter, install it and retry:

```bash
sudo apt-get update -qq
sudo apt-get install -y -qq libreoffice-writer
```

Fonts must exist on the authoring/rendering host. Check the selected family with
`fc-match`, including the correct CJK region or complex-script family. Do not
turn an old environment failure into a ban on an engine: verify the actual
dependency and output. Install the dependencies listed for the selected route;
use `requirements.txt` when the complete bundled toolchain is needed.

If the toolchain is unavailable, explain the blocked export/preview. Return a
usable source when possible, clearly marked as not visually verified. Do not
claim a successful PDF or verified Word file, or silently change the format.

## Native authoring: create or edit, then prepare for inspection

Use the selected library or template to produce a finished `edited.docx` or
`report.pdf`. Retain the script and input data separately from formatting code
when that makes revisions reusable. Then prepare the actual output:

```bash
python3 "$OFFICE_FILES_DIR/scripts/render_document.py" edited.docx \
  --out generated/document --format both --resource build_docx.py

python3 "$OFFICE_FILES_DIR/scripts/render_document.py" report.pdf \
  --out generated/document --resource build_pdf.py --resource data.json
```

These are alternative examples; list resources that actually exist. Repeat
`--resource` for the authoring source, original/template, data, filters and assets
used by an external authoring pipeline. The helper records hashes; it does not
execute those files or discover their dependencies. Rebuild the output after
source changes, then prepare and inspect it again. This records the current
files, not proof that an external generator used them.

The helper preserves supplied DOCX/PDF bytes. DOCX gets a LibreOffice PDF export
for preview and optional delivery. PDF stays PDF, without Pandoc, Word libraries
or LibreOffice; it cannot be turned into editable Word by changing `--format`.
For matching Word/PDF output, supply the finished DOCX. The original files are
never overwritten or house-styled. LibreOffice pagination is verified, not
identical rendering in every Microsoft Word version.

## Optional Pandoc prose route

Use this convenience route when its flowing-prose structure fits. It is not a
restriction on Pandoc's readers, extensions, Lua filters, citations, templates
or output engines. For those workflows, run Pandoc with the required options,
then pass the finished DOCX/PDF and its authoring resources to the shared helper.
Do not squeeze native layout into Markdown merely to use this wrapper.

```bash
python3 -m pip install --break-system-packages --quiet pypandoc_binary==1.17 python-docx==1.2.0
```

The wrapper finds the bundled Pandoc itself. Before writing new untemplated
Markdown, read [editorial-patterns.md](references/editorial-patterns.md). Its
optional editorial foundation supplies typography, tables and page numbers;
it does not invent a logo, cover, section order or page-count target.

Before writing, state a one-sentence visual direction based on the audience,
language and information shape (for example, “quiet editorial paper with one
ink-blue accent; the KPI strip is the opening focal point”). This is a design
constraint, not a document-type label. Decide the opening focal point and page
rhythm before choosing components. Do not expect the renderer, a model name or
a colour palette to create composition on its own.

Write `doc.md` with semantic headings, paragraphs, lists, tables, captions,
footnotes and images. Set language in YAML (`lang: zh-CN`, `en-US`, `ja-JP`, `ar`,
etc.) or pass `--lang`. Metadata is optional; do not invent title/author/date.
Use only the few editorial components that serve the content:

```markdown
::: {custom-style="Deck"}
A concise opening statement that frames the document.
:::

| 88.3% | 20.2× | 121× |
|------:|------:|-----:|
| usage share | multiplier gap | cost gap |

: {#opening-metrics .metric-grid}

::: {custom-style="Key Takeaway"}
One decision-relevant conclusion, not a decorative summary after every heading.
:::

# 01 First chapter {.chapter}

::: {custom-style="Source Note"}
Source: concise provenance and period.
:::
```

`.metric-grid` creates an editable KPI strip rather than a screenshot.
`.chapter` starts that heading on a new page; use it only for a deliberate
chapter/cover transition, never to chase a page count. Other available styles
are `Eyebrow`, `Pull Quote`, `Section Lead` and `Source Note`. See the patterns
reference for selection rules and examples.

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

Use an output directory separate from the source. All routes produce `render.json`
(inputs, hashes, helper engine versions and delivery choices) and
`expectations.json`. Markdown supplies heading/opening-text relationships;
native files start with empty expectations. Add important exact wording and
figure/reference pairs from the request/source when relevant. Compilation or
copying alone leaves a candidate in `needs-inspection`. The house theme is only
applied to new untemplated Markdown, never to supplied files or templates.

## Inspect, repair, then deliver

```bash
python3 "$OFFICE_FILES_DIR/scripts/check_document.py" inspect \
  generated/document/doc.pdf --docx generated/document/doc.docx \
  --render generated/document/render.json \
  --expectations generated/document/expectations.json --out generated/document/qa
```

The command above uses a Word export named `doc`; use the actual filenames.
For native PDF, omit `--docx` and retain `--render` and `--expectations`. Pass
`--render` for every output prepared by the helper: it binds the source,
reference, declared resources and completed preparation to the inspected files.
A failed new render cannot reuse an old export's acceptance. Read
`inspection.json`, open the generated page images, and review
**every page** for legibility/density, hierarchy, composition/rhythm,
pagination/grouping and figures/tables. Inspect Word's actual exported pages,
not its XML alone. For composition/rhythm, record the page's focal point,
balance of occupied and open space, and whether repeated page structures feel
intentional rather than mechanically identical.

- Fix machine blockers and visual defects in the source/style and rerender.
- Do not reduce font size or squeeze spacing merely to fit fewer pages.
- Repair a flat or monotonous page by changing grouping, emphasis, component
  choice or page transition—not by adding arbitrary decoration.
- Complete each page's `review.json` observations only after inspecting it;
  acknowledge heuristic warnings with a concrete reason. A generated review
  form or a contact sheet alone is not visual acceptance.
- Repair and repeat the affected inspection until the result meets the request.
  If a concrete tool/source limitation prevents completion, explain the defect
  and provide a clearly identified draft or usable source, not a claimed final.

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
