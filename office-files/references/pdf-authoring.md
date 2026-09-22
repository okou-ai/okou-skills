# PDF authoring and editing

A PDF-only task can use a native PDF workflow. Select the engine from the page
layout, language, supplied source and edit requirements. A matching DOCX/PDF
pair should instead export the actual final DOCX, as described in
[Word authoring](word-authoring.md). Do not invent a Word intermediate for a
PDF template, form or designed page.

| Situation | Route |
| --- | --- |
| New flowing PDF with programmable paragraphs and tables | ReportLab Platypus. |
| Fixed-position page or measured overlay | ReportLab Canvas, preserving the source's page geometry. |
| Native typesetting, mathematics or a Typst template | Typst, authored in its own source format. |
| Existing HTML/CSS design or print template | Its verified print renderer, such as Chromium or WeasyPrint. |
| Existing PDF pages, fields or annotations | `pypdf` or PyMuPDF for supported edits; `pdfplumber` for text/table extraction. |
| Simple text-led PDF or an established Pandoc publishing workflow | Optionally use Pandoc with the suitable PDF engine and full required options. |

Keep the selected native source and assets. A visual revision should change
layout/styles while preserving the approved content, without rebuilding the
document through an unrelated format.

## ReportLab

```bash
python3 -m pip install --break-system-packages reportlab
```

Use Platypus flowables for paragraphs, tables, wrapping and pagination. Use
Canvas when coordinates are part of the task; it does not automatically flow
long text across lines or pages. This minimal script accepts a real font file
instead of assuming a particular installed family. Run it with a compatible
TrueType font whose glyphs cover the content.

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

Change page dimensions, hierarchy and spacing for the task or template. Escape
content before passing it to ReportLab's paragraph markup; add only intentional
formatting markup. Register the actual regular/bold/italic faces and their
family mapping before relying on inline emphasis. Use paragraph cells and
deliberate column widths for wrapping tables; repeat headers on continued
tables and allow appropriate row splitting. Keep a short caption with its
figure, but do not put an entire long section/table in an unbreakable container.

For CJK, use a supported font with the required regional glyphs and configure
CJK line breaking where needed. Font registration alone does not establish
correct Arabic/Hebrew shaping or bidirectional layout. Confirm the installed
ReportLab version and shaping support with representative mixed-script text;
choose a verified shaping-capable route when needed. Do not reverse Unicode
strings manually. A `.ttf` suffix is not proof of coverage, and CFF-based fonts
are not interchangeable with the TrueType fonts supported by this example.

## Typst and HTML/CSS

For Typst, retain the `.typ` source, fonts, assets and package versions. Use the
project's existing toolchain, or install the official compiler appropriate to
the environment. `typst fonts` lists available families; `typst compile
report.typ report.pdf` creates the PDF. Native Typst is available independently
of Pandoc. Choose language/direction, font, paper and page numbering explicitly
where relevant, and inspect mathematics, long tables and multilingual text.

For HTML/CSS, preserve the source's intended print design. WeasyPrint works for
static HTML/CSS and does not execute page JavaScript:

```bash
python3 -m pip install --break-system-packages weasyprint
weasyprint report.html report.pdf
```

Its native dependencies and supported CSS vary with the environment; resolve
reported dependencies using the installation instructions for that platform.
Use Chromium when the layout depends on browser behavior or JavaScript. Wait
for fonts and images to finish loading before printing. Set the intended page
size, margins, background printing and header/footer behavior rather than
accepting browser defaults. Use print CSS deliberately, for example:

```css
@page { size: A4; margin: 20mm; }
@media print {
  h1, h2, h3 { break-after: avoid; }
  thead { display: table-header-group; }
  figure { break-inside: avoid; }
}
```

This is an example, not a stylesheet to apply over every template. Avoid
unbreakable containers taller than a page. Verify the chosen engine's actual
support for running headers, counters, footnotes, grids and fragmentation.
Wait for asset load completion explicitly; a successful print call with blank
charts or fallback fonts is not a finished document.

For a simple text-led PDF, Pandoc is an optional route through an appropriate
installed PDF engine. Retain an established Pandoc publishing toolchain when it
serves the source correctly, using its templates, citations, filters and
extensions. Apply the same final-page checks.

## Existing PDFs and forms

Start with the supplied PDF and inspect its pages, rotation, media/crop boxes,
text layer, annotations and fields. Use text extraction or `pdfplumber` tables
as analysis inputs, not as evidence that the original layout can be recreated
losslessly. OCR adds/searches a text layer for scanned pages; verify names,
numbers and low-confidence text against the images.

```bash
python3 -m pip install --break-system-packages pypdf pdfplumber
```

For an AcroForm, inspect `PdfReader("form.pdf").get_fields()` and fill actual
field names/types. Clone the document so its form structure survives. The
following example assumes an existing text field named `client_name`:

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

Checkbox/radio values must match the field's actual appearance states. XFA,
signed forms and unusual appearance/font structures may need a different
implementation. Reopen to verify stored values and render to verify the visible
appearance; either check alone is insufficient. Preserve editability unless
the task calls for flattening. Editing signed content can invalidate its
signature; do not claim that an edited copy remains signed.

For a non-fillable form, place text in the measured blank regions with a PDF
overlay. Match page sizes, rotation, coordinate origins and crop boxes before
merging; do not cover or rebuild unrelated content. `pypdf` can merge overlay
pages, while ReportLab can create the added text/graphics. Check text clipping,
font size and line breaks for the actual values, not just short placeholders.

**An overlay is not redaction.** White boxes, image overlays, cropping and hidden
layers can leave the underlying content extractable. When removal is requested,
use a tool's actual redaction operation, save an appropriately cleaned copy,
and verify relevant text, images, annotations, attachments and metadata. Do not
label a visual cover-up as secure removal or assume flattening removes all
hidden information.

## Final verification

Follow [the shared verification and delivery flow](../SKILL.md) on the exact
final PDF, using its native-PDF route and recording the source/engine needed to
reproduce it. Inspect every rendered page for pagination, clipping, missing
glyphs, table/figure placement and font substitution. Check extracted text and
declared content expectations as well as the page images. For forms or other
interactive PDFs, also test the functionality in a compatible viewer; page
images cannot establish that fields, links or annotations work.

Use the common layout guidance as applicable, while preserving a supplied
design. Do not rasterize whole pages merely to hide layout or font problems.
Keep a usable native source for future revisions; neither successful PDF
creation nor tagged output alone proves accessibility conformance.
