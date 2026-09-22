# PDF authoring and editing

## Start

Use this page to author or edit PDF directly. For matching Word/PDF deliverables,
follow the [Word workflow](word-authoring.md) and export its finished DOCX to PDF.

Follow a supplied template's instructions. Keep an existing original unchanged:
open it as the input and save edits to a distinct output path. Preserve content
and formatting outside the requested changes. When layout must be preserved,
inspect the original pages before editing.

Read the [rendering setup](document-layout.md#rendering-setup), then use the
applicable method below. For new simple text-led documents or an existing
publishing workflow, optionally use [Pandoc](pandoc-authoring.md).

## ReportLab

Use Platypus for flowing paragraphs, tables and pagination. Use Canvas for
fixed-position pages or measured overlays; wrap and paginate its text explicitly.

```bash
python3 -m pip install --break-system-packages reportlab
```

This example takes a TrueType font with glyph coverage for the content:

```python
import sys
from html import escape
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate

if len(sys.argv) != 3:
    raise SystemExit("Usage: python3 author_pdf.py FONT.ttf OUTPUT.pdf")
pdfmetrics.registerFont(TTFont("Body", sys.argv[1]))
body = ParagraphStyle("Body", fontName="Body", fontSize=11, leading=16,
                      spaceAfter=8)
heading = ParagraphStyle("Heading", parent=body, fontSize=20, leading=25,
                         spaceAfter=14, keepWithNext=True)
document = SimpleDocTemplate(sys.argv[2], pagesize=A4, leftMargin=54,
                             rightMargin=54, topMargin=54, bottomMargin=54)
story = [
    Paragraph(escape("Quarterly review"), heading),
    Paragraph(escape("Replace this example with the approved source content."), body),
]
document.build(story)
```

- Set page dimensions, margins, hierarchy and spacing for the document.
- Escape text passed to paragraph markup; add only intended formatting tags.
- Use paragraph cells and explicit column widths for wrapping tables. Repeat
  headers across pages, allow row splitting where needed, and keep captions with
  figures. Avoid unbreakable containers taller than a page.
- Register regular, bold and italic faces with their family mapping. This example
  requires TrueType outlines; CFF-based fonts are not supported. A `.ttc` extension
  identifies a collection, not its outline format: TrueType collections work with
  `TTFont(..., subfontIndex=0)`, but CFF collections such as Noto Sans CJK do not.
- For CJK, use the appropriate regional glyphs and configure CJK line breaking.
  For Arabic/Hebrew or mixed-direction text, verify shaping and bidirectional
  support in the installed engine; switch to a verified engine if necessary.
  Do not reverse Unicode strings manually.

### Runnable Simplified Chinese example

For this ReportLab route on Debian/Ubuntu, install an embeddable Chinese
TrueType font and a separate bullet font:

```bash
sudo apt-get update -qq
sudo apt-get install -y -qq fonts-wqy-zenhei fonts-dejavu-core
python3 -m pip install --break-system-packages reportlab
python3 "$OFFICE_FILES_DIR/scripts/author_pdf_cjk.py" generated/chinese.pdf
```

Read and adapt [the example source](../scripts/author_pdf_cjk.py) to the approved
content. It embeds WenQuanYi Zen Hei face 0, sets `lang="zh-CN"` and
`wordWrap="CJK"`, and demonstrates Chinese punctuation, Latin text, numerals,
`·` and wrapped paragraphs. WenQuanYi Zen Hei lacks `•` (U+2022), so the example
embeds DejaVu Sans for `bulletText="•"` with `bulletFontName="Symbols"`.
For an inline bullet, use an explicit `<font name="Symbols">•</font>` run inside
otherwise escaped paragraph text; do not use a font that lacks the glyph.
On other systems, pass
`--font /path/to/chinese.ttf --symbols-font /path/to/symbols.ttf`, using fonts
whose glyph coverage and regional forms match the content. The example uses
regular faces only; add actual faces before requesting bold or italic.

Do not use `UnicodeCIDFont("STSong-Light")` as an automatic substitute for an
embedded font. It relies on the viewer's CJK resources, has no registered bold
or italic variants, and `·` or `•` can extract as text while rendering blank.
After authoring, use the shared [page review](document-layout.md#page-review)
to inspect every page, including punctuation and symbols at readable scale.
Successful text extraction or character matching does not prove visible glyphs.

## Typst and HTML/CSS

For native Typst, use the project's compiler or install the official build for
the environment. Check available fonts with `typst fonts`, set language,
direction, fonts and page settings, then run `typst compile report.typ report.pdf`.
Inspect mathematics, long tables and multilingual text.

Use WeasyPrint for static HTML/CSS; it does not execute JavaScript:

```bash
python3 -m pip install --break-system-packages weasyprint
weasyprint report.html report.pdf
```

Resolve native dependencies using the platform's installation instructions.
Use Chromium when the design depends on browser behavior or JavaScript. Wait
for fonts, images and charts to load before printing. Set page size, margins,
background printing and headers/footers explicitly. Adapt print CSS to the design:

```css
@page { size: A4; margin: 20mm; }
@media print {
  h1, h2, h3 { break-after: avoid; }
  thead { display: table-header-group; }
  figure { break-inside: avoid; }
}
```

Avoid unbreakable containers taller than a page. Check the engine's support for
any running headers, counters, footnotes, grids and page breaks used by the design.

## Existing PDFs and forms

Inspect page sizes, rotation, media/crop boxes, text, annotations and fields
before editing. Use `pypdf` or PyMuPDF for supported edits and `pdfplumber` for
text/table extraction. For scans, use OCR and verify names, numbers and
low-confidence text against the page images.

```bash
python3 -m pip install --break-system-packages pypdf pdfplumber
```

For PyMuPDF, open the original and save the modified document under a new name:

```python
from pathlib import Path
import pymupdf

source = Path("original.pdf")
output = Path("revised.pdf")
if source.resolve() == output.resolve():
    raise ValueError("The edited PDF must use a distinct output path")
with pymupdf.open(source) as document:
    # Apply the requested page, annotation or redaction edits here.
    document.save(output, garbage=4, deflate=True)
```

Do not copy the input, open that copy and call `save()` on the same path:
PyMuPDF rejects non-incremental in-place saves. For content removal, use real
redaction and a full save to a new path as above; an incremental save can retain
earlier versions of removed content. Reopen and verify the new file.

For AcroForms, inspect `PdfReader("form.pdf").get_fields()` and use actual field
names and types. Clone the document to retain its form structure. This example
requires an existing text field named `client_name`:

```python
from pypdf import PdfReader, PdfWriter

source = "form.pdf"
fields = PdfReader(source).get_fields() or {}
if "client_name" not in fields:
    raise ValueError("Expected form field is absent")
writer = PdfWriter(clone_from=source)
for page in writer.pages:
    if page.get("/Annots"):
        writer.update_page_form_field_values(
            page, {"client_name": "Example Company"}, auto_regenerate=False
        )
writer.write("filled.pdf")
```

- Match checkbox/radio values to their actual appearance states. Check tool
  support for XFA and unusual font/appearance structures before editing.
- Reopen the PDF to verify stored values and render it to check visible field
  appearances. Test fields, links and annotations in a compatible viewer.
- Retain editable fields unless flattening was requested. Revalidate digital
  signatures after editing signed content.
- For a non-fillable form, add an overlay in measured blank regions. Match page
  size, rotation, coordinate origins and crop boxes before merging. Check
  clipping and line breaks with the actual values.
- To remove content, use actual redaction and save a cleaned copy. Overlays,
  cropping and flattening do not ensure removal. Check text, images, annotations,
  attachments and metadata for remaining content.

## Verify and deliver

Run [document verification](document-layout.md#verification) on the finished PDF.

Upload the PDF with `okou web upload-file` and include its editable source when
appropriate. Keep authoring sources, data, assets and QA files for revisions.
