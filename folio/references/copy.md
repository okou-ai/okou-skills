# Copy integrity

Use the supplied source and current user corrections as the source of truth.
Separate exact required wording, approved paraphrase and unresolved gaps. Do not
silently improve quotations, legal wording, prices, dates, names or contacts.
Fictional demonstrations must say they are demonstrations; never present their
statistics, people or affiliations as client facts.

## Required-copy file

Create approved-copy.txt as plain UTF-8: **one complete required string per logical
line**, including short names, numbers, URLs and contacts. Do not add Markdown
headings or checklist syntax unless those characters should appear in the document.
Keep a paragraph on one logical line. Preflight normalizes whitespace, case and
curly quotes, then checks the **entire** string across the laid-out page text.

Example:

    青禾设计工作室（虚构示例）
    本页用于版式与中文排版验证，不构成客户项目或业绩声明。
    hello@example.invalid

A full-string presence check catches omissions/alterations, including long-sentence
suffixes, but it is not semantic fact-checking, proof of visual readability or a
whole-document diff. It does not validate text hidden inside images, SVG image
files, PDF glyph extraction or HTML metadata. Inspect those separately.

## Authoring rules

- Replace each marked sample element individually; verify nested text, footer
  numbers, captions and portrait/mark slots. Changing company names alone is not enough.
- Preserve facts while adjusting sentence length to the layout. If copy is too long,
  change the composition or obtain approval to edit; never silently omit it.
- Treat copy-style warnings as editorial suggestions. Do not rewrite approved client
  wording just because it contains a flagged phrase, dash or common font name.
- Verify the PDF's extracted text and page order against important source facts;
  DOM checks cannot prove that the exported PDF contains the intended text.
- Keep client data in the task project. Do not save it into shared kits, histories,
  personal preference stores or a reusable style without separate authorization.
