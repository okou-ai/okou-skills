---
name: reverse-template
description: "Route a deck or document to the reverse-engineering branch that matches it and produce a reusable template. Covers .pptx, .ppt, .pdf, .docx, image decks, and page screenshots, including composed documents such as resumes that a style-only template cannot hold. Use when asked to reverse a deck or a document, extract a template from a file, turn a PDF into a Word template, apply a company template to Markdown, or save a file's visual language as a reusable template."
---

# Reverse a file into a reusable template

Two checks pick the branch. Run both, then follow that branch's `SKILL.md` to
the end. The branches produce different deliverables, so do not carry steps
between them.

## Check 1 — which kind of template

| Source | Branch | Guide |
|---|---|---|
| `.pptx`, `.ppt`, `.key`, `.odp` | presentation | `presentation/SKILL.md` |
| image deck, or a directory of page screenshots | presentation | `presentation/SKILL.md` |
| `.pdf` whose pages are slides | presentation | `presentation/SKILL.md` |
| `.pdf` whose pages are a document | pdf | `pdf/SKILL.md` |
| `.docx` | docx | `docx/SKILL.md` |
| `.doc`, `.rtf`, `.odt`, or a `.docx` saved by WPS | — | re-save it as `.docx` from Word, then start again |

`.pdf` is the only extension the table cannot settle on its own:

```bash
python3 scripts/classify_source.py <source.pdf>
```

It votes on page geometry and on the characters of the median page, then names
the branch. Requires `pdfinfo` and `pdftotext`.

One or two pages at a paper size is a document whatever the density says. A
resume or an invoice carries as little text as a slide and is still not a deck;
what makes it sparse is composition, which check 2 answers.

When the two signals disagree it prints `ambiguous` and exits 1 — an A4
landscape deck reads as paper by geometry and as slides by density. Render the
first page and decide by looking at it:

```bash
okou presentation screenshot --input <source.pdf> --out shots
```

A page carrying one idea in display type is a slide. A page carrying running
prose under a repeated header, footer, or page number is a document.

## Check 2 — an article, or a form

Only for the pdf and docx branches. The presentation branch rebuilds pages in
HTML, so this is not a question it has.

Look at the pages. Render them first if the source is a PDF:

```bash
okou presentation screenshot --input <source.pdf> --out shots
```

Two questions, both answered by looking:

1. **Is it an article, or a form?** An article is written top to bottom and
   could be written again at another length on another subject — a report, a
   paper, a white paper, a manual, a policy, a memo. A form is one object with
   a fixed set of entries, and a new one fills the same entries — a resume, a
   receipt, an invoice, a certificate, an offer letter, a spec sheet.
2. **If it is an article, does the body run as one stream?** One column is one
   stream, and so are columns of equal width. A sidebar, a margin note beside
   the text, or blocks tiled across the page is not.

An article that runs as one stream stays on the branch check 1 named: a
`reference.docx` reproduces it. Everything else goes to
`source-style/SKILL.md`, which uploads the source file itself.

Answer question 1 on what the document is, not on how it looks. A plain
single-column resume with no colour is still a form.

When it is not obvious either way, take `source-style`. That branch keeps
everything; the other one silently drops whatever a style sheet cannot hold.

## Deliverables

| Branch | Deliverable | Ends with |
|---|---|---|
| presentation | HTML presentation template package | `okou presentation-template publish` |
| pdf, docx | package directory holding `SKILL.md`, `reference.docx`, and the source | handing the directory over |
| source-style | the source file plus one line of instruction | `okou user-template publish --kind document` |

Three rules override both checks:

- A deliverable the user names wins over the source's extension. "Turn these
  slides into a Word template" is the docx branch; "save this report's look as a
  presentation template" is the presentation branch.
- When an authoring file sits beside an export of itself, reverse the authoring
  file: `.docx` over its PDF, `.pptx` over its PDF.
- A PDF with no text layer is a scan or an image export. Settle it on a rendered
  page, not on a measurement.

## Then

`cd` into the branch directory. Every path inside a branch guide is relative to
that directory.
