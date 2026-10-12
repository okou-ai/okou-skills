---
name: extract-template
description: "Extract a reusable presentation, document, or illustration template from source files or an HTML deck URL. Use when asked to extract a deck or Word template, turn a PDF into a Word template, apply a company template to Markdown, or save an image style for reuse."
---

# Extract a reusable template from a file

Choose the intended template, select its extraction guide, then follow that guide
through inspection, extraction, validation and saving.

## 1. Choose the template type

Use the user's requested template type. For example, a report can supply the
visual style for a presentation template. When the user leaves the type open,
identify what the source contains:

| Template type | Source content |
| --- | --- |
| Presentation | Slides organized around individual ideas, with display text and visual compositions |
| Document | A report, letter, resume, invoice or other document with reading order and document structure |
| Illustration | Artwork whose drawing style will be reused |

Classify PDFs and page images by their content. A slide screenshot belongs to
presentation; a scanned document belongs to document. Sparse text or a short page
count alone does not make a document a slide deck. Several artwork references in
one drawing style form one illustration template.

## 2. Select the source and guide

Keep the original file. When both an authoring file and its export are available,
prefer the authoring file: `.pptx` over its PDF, `.docx` over its PDF.

| Chosen template | Available source | Guide |
| --- | --- | --- |
| Presentation | HTML file, HTML directory or deck URL; `.pptx`, `.ppt`, PDF or ordered slide images | [Presentation extraction](presentation/SKILL.md) |
| Document | Word file | [Word extraction](docx/SKILL.md) |
| Document | PDF | [PDF extraction](pdf/SKILL.md) |
| Illustration | One or more artwork images | [Illustration extraction](illustration/SKILL.md) |

Prepare another format only when the selected guide requires it:

- PDF slide decks: convert with pdf2htmlEX, then use the presentation guide's HTML
  extraction flow; keep the original PDF for captures and upload.
- Scanned document images: assemble an ordered PDF for the PDF guide.
- Cross-format reuse: export slides to PDF for a Word-style template, or a Word
  report to PDF for a presentation template. The requested template type stays
  the same.

Keep conversions alongside the original source.

## 3. Follow the selected guide

`cd` into the selected guide's directory; its commands and paths are relative to
that directory.

The guide handles source rendering when needed. Rendering produces page images
for inspecting layout, typography, colours and image crops; those captures become
the visual reference for extraction. Keep the original for structure and style
metadata. Reuse existing source captures; no need to render them again.

Document guides use [document-reuse.md](document-reuse.md) to choose between slot
filling, structure and expression reuse, and style extraction. The presentation
guide separately identifies extraction files and the generation files bundled
into the saved template.
