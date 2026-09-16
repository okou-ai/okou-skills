---
name: office-files
description: Produce and edit real Office deliverables — docx, xlsx and PDF — with one verified toolchain instead of hand-rolled code.
---

## Setup — run once per run, before authoring

```bash
pip install --break-system-packages --quiet pypandoc_binary typst openpyxl python-docx
```

About 6 seconds. Nothing is preinstalled. `--break-system-packages` is required: the system Python is PEP 668 externally managed and the install fails without it.

## Pick the contract before you write anything

| Deliverable | Content contract | Style / structure contract |
| --- | --- | --- |
| Prose (docx, PDF) | **Markdown** you author | **a `.docx`** passed as `--reference-doc`, or pandoc's default when there is none |
| Data (xlsx) | **structured data** you build | **openpyxl** — formulas, sheets, validation |

Never author a spreadsheet as a Markdown table, and never hand-build docx XML.

## docx

```bash
pandoc report.md --reference-doc=theme.docx -o report.docx
pandoc report.md --reference-doc=theme.docx --toc --toc-depth=2 -o report.docx   # with a table of contents
```

`--reference-doc` is where headers, footers, page numbers, margins, paper size, fonts and numbering come from — the output inherits `word/header1.xml` and `word/footer1.xml`, including a live `PAGE` field. **Do not write headers, footers or page numbers into the Markdown.** When the user uploaded their own Word file, use that file as the reference doc: their branding comes across for free.

**When there is no reference doc**, omit the flag — `pandoc report.md -o report.docx` uses pandoc's built-in default and produces a clean but unbranded file with no header, no footer and no page number. Say that in one line when you deliver it, and offer to match their house style if they send you a Word file.

The exception is a request that explicitly needs a header, footer or page numbers. None of those can be expressed in Markdown, so build a minimal reference doc first with python-docx — set `section.header`, and add a `PAGE` field to `section.footer` — then pass that file with `--reference-doc`.

Two traps:

- **Missing styles fail silently.** Pandoc writes `<w:pStyle w:val="Heading1">` but does not add the style definition, so Word quietly falls back to Normal and the document still opens fine. If you supply a user's docx as the reference, verify the styles it defines. Commonly missing and therefore dangling: `heading 1`–`heading 9`, `Body Text`, `First Paragraph`, `Compact`, `Title`, `Subtitle`, `Author`, `Date`, `Block Text`, `Table Caption`, `Hyperlink`, `Table`.
- Styles match on `<w:name>`, not `<w:styleId>`. A Chinese-locale Word file with `styleId="1"` still works as long as `w:name` is `heading 1`. Never rewrite styleIds.

## PDF

```bash
pandoc report.md -t typst -o report.typ
python3 -c "import typst; typst.compile('report.typ', output='report.pdf')"
```

**`--reference-doc` does not apply to PDF** — only docx, pptx and ODT support it. This path gives a clean but unbranded PDF. When the user needs their branding on a PDF, produce the docx with their reference doc and say that the PDF export has to happen on their side; the sandbox cannot convert docx to PDF.

## xlsx

Use openpyxl. Write formulas as strings (`ws["D2"] = "=C2-B2"`) — Excel evaluates them on open, so if the file must already contain computed values, compute them yourself and write both. Use `wb.create_sheet("Notes")` for multiple sheets.

## Reading files back in

```bash
pandoc input.docx -t markdown --wrap=none    # edit a document the user sent
```

For xlsx, read with openpyxl. Pandoc lists xlsx as an input format but fails on many real files — do not rely on it.

## Delivery

`okou web upload-file`. When prose is final and being sent onward, attach both the PDF and the docx source: the recipient gets something fixed and something they can still edit.

## Do not use

- `soffice` / LibreOffice conversion — the sandbox installs only `libreoffice-impress` and `libreoffice-draw`, so the Writer and Calc filters do not exist and every convert fails with `Error: source file could not be loaded`.
- `chromium --headless --print-to-pdf` — produces no file.
- `weasyprint` as a pandoc `--pdf-engine` — exits non-zero.
- `pandoc -o out.xlsx` — pandoc has no xlsx writer.

## If the install fails

Deliver Markdown or a hosted HTML view instead and tell the user the toolchain was unavailable. Do not fall back to LibreOffice, and do not silently ship a worse format without saying so.
