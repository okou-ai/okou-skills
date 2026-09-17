---
name: reverse-template
description: "Route a deck or document to the reverse-engineering branch that matches it and produce a reusable template. Covers .pptx, .ppt, .pdf, .docx, image decks, and page screenshots, including forms such as resumes and invoices that a style-only template cannot hold. Use when asked to reverse a deck or a document, extract a template from a file, turn a PDF into a Word template, apply a company template to Markdown, or save a file's visual language as a reusable template."
---

# Reverse a file into a reusable template

Render the pages, read one row off the table, follow that guide to the end.

```bash
okou presentation screenshot --input <source.pptx|source.pdf> --out shots
```

Re-save a `.doc`, or a `.docx` written by WPS, as `.docx` from Word first. For a
`.docx`, export a PDF to render from and keep the original as the source.

| The pages show | Go to |
|---|---|
| slides — one idea a page, display type | `presentation/SKILL.md` |
| an article, body running as one stream — report, paper, manual, policy | `docx/SKILL.md` for a `.docx`, `pdf/SKILL.md` for a `.pdf` |
| an article whose body does not run as one stream — a sidebar or margin note beside it | `source-style/SKILL.md` |
| a form — resume, receipt, invoice, certificate, offer letter, spec sheet | `source-style/SKILL.md` |
| a scan, or anything you are unsure of | `source-style/SKILL.md` |

One column is one stream, and so are columns of equal width. Read row 4 off what
the document is, not off how it looks: a plain single-column resume is a form.

Three rules override the table:

- A deliverable the user names beats the table. "Turn these slides into a Word
  template" is `docx/`; "save this report's look as a presentation template" is
  `presentation/`.
- Reverse the authoring file when it sits beside an export of itself: `.docx`
  over its PDF, `.pptx` over its PDF.
- One or two pages at a paper size is never slides, however sparse.

| Branch | Deliverable | Ends with |
|---|---|---|
| `presentation` | HTML presentation template package | `okou presentation-template publish` |
| `docx`, `pdf` | directory holding `SKILL.md`, `reference.docx`, and the source | handing the directory over |
| `source-style` | the source file plus one line of instruction | `okou user-template publish --kind document` |

`cd` into the branch directory; every path inside a branch guide is relative to
it. `python3 scripts/classify_source.py <source.pdf>` reads slides-or-document
off page geometry and text density, for a second opinion on row 1.
