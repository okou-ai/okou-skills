# Word/PDF layout and verification

## Rendering setup

Set `OFFICE_FILES_DIR` to this skill's absolute directory in each shell invocation.
Install the shared page inspector:

```bash
python3 -m pip install --break-system-packages --quiet PyMuPDF==1.28.2
```

For DOCX or Markdown export, also install LibreOffice Writer if absent:

```bash
sudo apt-get update -qq
sudo apt-get install -y -qq libreoffice-writer
```

Check the chosen font with `fc-match` on the rendering host. Set the document's
language and direction, and use fonts that cover its script and regional glyphs.
Pass `--lang zh-CN` (or the actual BCP 47 language) when preparing the output if
the source does not declare it. `render.json` records the language and whether it
came from an override, document metadata or a script-based fallback. This record
does not change the language/font settings inside a supplied native file.

## Layout

- Follow the supplied design. For a new document, choose a consistent hierarchy,
  opening focal point and page rhythm suited to the content.
- Use semantic headings, lists, tables and captions. Keep text editable.
- Keep headings with opening text and figures with their captions; allow long
  sections and tables to flow across pages.
- Size table columns for their contents and repeat headers on continued tables.
  Split oversized tables or use a landscape section when needed.
- Repair crowding through grouping, widths and page breaks. Do not shrink text
  or compress spacing merely to reduce the page count.
- Preserve facts and required wording when changing the layout.

## Verification

### Prepare the output

Pass the finished `.docx`, `.pdf` or Pandoc `.md` to the shared renderer, using a
separate output directory. Use actual filenames and resources; for example:

```bash
python3 "$OFFICE_FILES_DIR/scripts/render_document.py" document.docx \
  --out generated/document --resource build_docx.py
```

Repeat `--resource` for the external authoring script, original/template, data
and assets used. DOCX/Markdown produces a DOCX and a PDF preview; native PDF
stays PDF.

### Content expectations

Before authoring or editing, identify required titles, key wording/numbers and
content that must stay together from the request and source. Before inspection,
put those checks in the generated `expectations.json`. Retain applicable existing
entries and use distinctive phrases. Markdown may seed headings and opening
paragraphs; **native Word/PDF starts with empty lists that you must populate**:

```json
{
  "required_text": ["Terms remain unchanged"],
  "same_page": [
    {"first": "The next table contains", "second": "Metric", "reason": "Keep the lead-in with the table header"}
  ]
}
```

Check repeated text, exact page counts and other constraints not represented by
this format directly against the rendered pages.

Each empty category blocks acceptance unless it has a concrete reason under
`not_applicable`. For example, a single-page form with no heading/body groups may
use `"not_applicable": {"same_page": "One-page form without heading/body groups"}`.
For an image-only page, explain why text checks do not apply and verify the
required content visually. Do not use a reason to skip applicable checks or
derive expected wording/numbers solely from the candidate you are testing.

### Inspect the pages

```bash
python3 "$OFFICE_FILES_DIR/scripts/check_document.py" inspect \
  generated/document/document.pdf --docx generated/document/document.docx \
  --render generated/document/render.json \
  --expectations generated/document/expectations.json --out generated/document/qa
```

For native PDF, omit `--docx`. Adapt the filenames to the actual outputs.
For edits to an existing Word document, also pass `--docx-comparison` with the
passed comparison report from the [Word workflow](word-authoring.md#compare-before-and-after).
The inspector verifies the compared document is the same DOCX being reviewed and
binds the original, edited file and change policy to acceptance.

### Page review

Inspection writes every `page-NNN.png` plus `gallery/index.html` and numbered
`gallery/overview-NNN.png` contact sheets. Open the gallery to scroll through all
pages, click to enlarge, use arrow keys for adjacent pages, and toggle original
pixels for small text. Contact sheets show page numbers and batch ranges so
missing or badly paginated pages are easy to find. Everything works offline.

To regenerate the gallery from the existing, hash-checked PNGs with a different
batch size (without re-rendering the document):

```bash
python3 "$OFFICE_FILES_DIR/scripts/page_gallery.py" generated/document/qa \
  --columns 2 --pages-per-sheet 6
```

An agent can open full page PNGs in small batches, for example 4–6 images per
tool call, in page-number order. Use contact sheets to check overall layout,
then examine every page at readable size. Enlarge dense tables, small notes,
Chinese punctuation and symbols as needed. Extractable text can still have
invisible glyphs; text matching does not establish visible ink.

Generating or opening a gallery never marks pages as passed. In `review.json`, record
observations for all five criteria and mark each `pass` only after checking it:

| Criterion | Check |
| --- | --- |
| Legibility and density | Readable type, line length, paragraph separation and text density |
| Hierarchy | Clear heading levels, emphasis and reading order |
| Composition and rhythm | A deliberate focal point, balanced whitespace and purposeful page variation |
| Pagination and grouping | Related content stays together; no isolated headings or accidental blank pages |
| Tables and figures | Readable labels and notes; suitable widths and placement; no clipping or collisions |

If a page has no tables or figures, record that observation. Explain every
warning using what is visible on the page. Repair blockers and visual defects
in the source; change grouping, emphasis or page transitions to fix a flat
composition. Regenerate and prepare the document, reapply request-specific
expectations, then inspect again.

When relevant, verify interactive features and accessibility separately. For
Word, report material pagination differences between the verified LibreOffice
export and the user's target application.

### Accept before delivery

Run acceptance immediately before upload:

```bash
python3 "$OFFICE_FILES_DIR/scripts/check_document.py" accept generated/document/qa
```

Deliver after `READY_TO_DELIVER`. If an input or output changes, regenerate the
document, then repeat preparation, request-specific expectations and inspection.
Older review records must be regenerated with the current inspector.
If a tool or source limitation blocks completion, state the issue and label any
delivered file as a draft or unverified source.
