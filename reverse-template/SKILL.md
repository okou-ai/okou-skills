---
name: reverse-template
description: "Decide what an uploaded file is — a deck, a Word document, a PDF document, or artwork — and hand it to the reverse-engineering guide that matches. Use when asked to reverse a deck or a document, extract a template from a file, turn a PDF into a Word template, save an image style as a reusable template, apply a company template to Markdown, or save a file's visual language as a reusable template."
---

# Reverse a file into a reusable template

Look at what the file holds, decide what it is, follow that guide to the end.

Render a `.pptx`, `.ppt` or `.pdf` first. An image is already viewable.

```bash
okou presentation screenshot --input <source.pptx|source.pdf> --out shots
```

| The file is | Go to |
|---|---|
| a deck — `.pptx`, `.ppt`, an image deck, or a `.pdf` whose pages are slides | `presentation/SKILL.md` |
| a Word document — `.docx` | `docx/SKILL.md` |
| a PDF document — pages of prose, not slides | `pdf/SKILL.md` |
| artwork — `.png`, `.jpg`, or several images of one drawing style | `illustration/SKILL.md` |

A page carrying one idea in display type is a slide. A page carrying running
prose under a repeated header, footer, or page number is a document. A picture with no
reading order is artwork.

Re-save a `.doc`, or a `.docx` written by WPS, as `.docx` from Word first. To
render a `.docx`, export a PDF from it and keep the original as the source.

Four rules override the table:

- A deliverable the user names beats the table. "Turn these slides into a Word
  template" is `docx/`; "save this report's look as a presentation template" is
  `presentation/`.
- Reverse the authoring file when it sits beside an export of itself: `.docx`
  over its PDF, `.pptx` over its PDF.
- One or two pages at a paper size is never slides, however sparse. A resume and
  an invoice carry as little text as a slide and are still documents.
- Several images at once are one style to `illustration/`, not several
  templates. A single image of a page — a scanned document, a screenshot of
  slides — is that page's kind, not artwork.

`cd` into the branch directory; every path inside a branch guide is relative to
it. The two document guides open by checking whether a style sheet can hold this
particular file, and publish the source itself when it cannot.
