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

## Check 2 — whether a style sheet can hold it

Only for the pdf and docx branches. The presentation branch rebuilds pages in
HTML, so composition is not a problem it has.

Those two branches produce a `reference.docx`: paper size, margins, columns,
per-style fonts and spacing, a header and a footer. No composition — no
sidebar, no panel behind a block of text, no floating photo, no grid of cards.
A resume, a certificate, an invoice, or a brochure usually keeps its identity
in exactly those things.

```bash
pip install pymupdf        # PDF only
python3 scripts/assess_layout.py <source.pdf|source.docx>
```

| Verdict | Go to |
|---|---|
| `flow` | the branch check 1 named |
| `composed` | `source-style/SKILL.md` |
| `check` | render a page and decide; blocks placed side by side at different widths, or text over a fill, mean `source-style` |

On a PDF it splits each page at its vertical corridors and keeps the regions
that run down the page. One region is a flow. Two of equal width are columns,
which `w:cols` reproduces. Two of unequal width are a sidebar, which nothing in
a style sheet holds. A narrow strip of right-aligned dates is a tab stop rather
than a region — a region has to carry its share of the page's text.

It then measures fill and image coverage, after subtracting whatever repeats in
the same place on most pages, because a header band and a logo are chrome the
branch already reproduces.

Colour is the weaker of the two signals and only the second is about it: a
sidebar drawn in plain text with a hairline rule covers no area at all.

On a `.docx` it reads the markup instead: floating shapes, text boxes,
positioned frames, and short wide tables whose cells hold prose.

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
