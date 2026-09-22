# PDF authoring and editing

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
  requires TrueType outlines; CFF-based fonts are not supported.
- For CJK, use the appropriate regional glyphs and configure CJK line breaking.
  For Arabic/Hebrew or mixed-direction text, verify shaping and bidirectional
  support in the installed engine; switch to a verified engine if necessary.
  Do not reverse Unicode strings manually.

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

Follow the [shared page verification and delivery steps](../SKILL.md) on the
final PDF.
