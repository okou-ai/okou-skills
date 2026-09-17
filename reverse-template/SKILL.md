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

Those two branches produce a `reference.docx`, and pandoc pours one stream of
paragraphs into it. The gates below are the list of what that reproduces. A
source passes to the branch only when every gate passes; anything else goes to
`source-style/SKILL.md`, which keeps the source file itself.

```bash
pip install pymupdf        # PDF only
python3 scripts/assess_layout.py <source.pdf|source.docx>
```

| Gate | Passes when |
|---|---|
| columns | one column, or columns of equal width |
| blocks side by side | no fill or image has text beside it at the same height |
| page art | fills and images cover under a quarter of the page, page chrome excluded |
| dividing rules | no vertical rule runs 40% of the page height or more |
| paragraph rules | no horizontal rule sits against a line of text |

A `.docx` is gated on its markup instead: floating shapes, text boxes,
positioned frames, short wide tables whose cells hold prose, and unequal
`w:cols` widths. It has no paragraph-rule gate — `build_reference.py` copies
`styles.xml` across whole, so a rule carried on a style survives.

The exit code is 0 for `flow` and 1 for `composed`; the report names the gates
that failed and, where the gap is the branch's own tooling rather than the
format, says so.

Widen the list by widening the branch, not by overriding a gate here. A wrong
`flow` is silent — the template comes out looking plausible with the sidebar
gone — and a wrong `composed` only costs editability.

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
