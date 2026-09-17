---
name: reverse-template
description: "Route a deck or document to the reverse-engineering branch that matches it and produce a reusable template. Covers .pptx, .ppt, .pdf, .docx, image decks, and page screenshots, including forms such as resumes and invoices that a style-only template cannot hold. Use when asked to reverse a deck or a document, extract a template from a file, turn a PDF into a Word template, apply a company template to Markdown, or save a file's visual language as a reusable template."
---

# Reverse a file into a reusable template

Two questions name the branch. Only the first one can end it. Then follow that
branch's `SKILL.md` to the end — the branches produce different deliverables,
so do not carry steps between them.

## 1. A deck, or a document?

| Source | It is |
|---|---|
| `.pptx`, `.ppt` | a deck |
| an image deck, or a directory of page screenshots | a deck |
| `.docx` | a document |
| `.doc`, or a `.docx` saved by WPS | re-save it as `.docx` from Word, then start again |
| `.pdf` | look at the pages |

```bash
okou presentation screenshot --input <source.pdf> --out shots
```

A page carrying one idea in display type is a slide. A page carrying running
prose under a repeated header, footer, or page number is a document. One or two
pages at a paper size is a document whatever else it looks like — a resume and
an invoice carry as little text as a slide and are still not decks.

**A deck goes to `presentation/SKILL.md`. That is the whole answer; stop here.**

A document goes to question 2.

## 2. An article, or a form?

Look at the same pages and answer two things:

1. **Is it an article, or a form?** An article is written top to bottom and
   could be written again at another length on another subject — a report, a
   paper, a white paper, a manual, a policy, a memo. A form is one object with
   a fixed set of entries, and a new one fills the same entries — a resume, a
   receipt, an invoice, a certificate, an offer letter, a spec sheet.
2. **If it is an article, does the body run as one stream?** One column is one
   stream, and so are columns of equal width. A sidebar, a margin note beside
   the text, or blocks tiled across the page is not.

| Answer | Branch |
|---|---|
| an article, and one stream | `docx/SKILL.md` for a `.docx`, `pdf/SKILL.md` for a `.pdf` |
| a form, or a body that is not one stream | `source-style/SKILL.md` |

Answer the first one on what the document is, not on how it looks. A plain
single-column resume with no colour is still a form.

When it is not obvious either way, take `source-style`. That branch keeps
everything; the other one silently drops whatever a style sheet cannot hold.

## The four branches

| Branch | Deliverable | Ends with |
|---|---|---|
| `presentation` | HTML presentation template package | `okou presentation-template publish` |
| `docx`, `pdf` | package directory holding `SKILL.md`, `reference.docx`, and the source | handing the directory over |
| `source-style` | the source file plus one line of instruction | `okou user-template publish --kind document` |

Three rules override both questions:

- A deliverable the user names wins over the source's extension. "Turn these
  slides into a Word template" is question 2's answer for a deck; "save this
  report's look as a presentation template" is the presentation branch.
- When an authoring file sits beside an export of itself, reverse the authoring
  file: `.docx` over its PDF, `.pptx` over its PDF.
- A PDF with no text layer is a scan or an image export. Settle both questions
  on a rendered page.

## Then

`cd` into the branch directory. Every path inside a branch guide is relative to
that directory.

`python3 scripts/classify_source.py <source.pdf>` answers question 1 from page
geometry and text density if a second opinion is useful. It needs `pdfinfo` and
`pdftotext`, and it prints `ambiguous` rather than guessing when its two signals
disagree.
