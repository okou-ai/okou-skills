---
name: reverse-template/pdf
description: "Reverse-engineer a PDF into a loadable template skill: SKILL.md, reference.docx and the source PDF. Use when asked to reverse a PDF, extract PDF styles, turn a PDF into a Word template, or analyse a PDF's layout."
---

# Reverse a PDF into a template package

Input: one `.pdf`. Output for an article: a directory holding `SKILL.md`,
`reference.docx` and `source.pdf`. Output for a fixed structure: `SKILL.md`
and the source alone.

**If the original .docx exists, use `../docx/SKILL.md` instead.** If the PDF's
pages are slides rather than a document, use `../presentation/SKILL.md`.

Run every command below from `reverse-template/pdf/`.

## Before anything — an article, or a fixed structure?

Look at the rendered pages.

An **article** is written top to bottom and could be written again at another
length on another subject — a report, a manual, a policy. A **fixed structure**
is the whole document as one arrangement of blocks, and a new one keeps that
arrangement and changes the content — a resume, an invoice, a certificate.

Judge on what the document is, not on how it looks — a plain single-column
resume is still a fixed structure. An article continues at Prerequisites below.

### A fixed structure: publish the source itself

A style sheet drops those silently. Publish the file and stop here.

Write `package/SKILL.md` and put nothing else in `package/`:

````markdown
---
name: <template-slug>
description: <what this document is, in one line>
---

Follow the source file's own styling. It is the authority for page size,
margins, typography, colour, and the position of every block.

Replace the content, keep the composition:

- <one line per entry a new document has to fill>
````

Name the entries off the rendered pages, and write nothing they do not show.

```bash
node ../scripts/cover-page.mjs --input <the original .pdf> --out cover.png
```

```bash
npx --yes --package="${CLI_PKG_URL}" okou user-template publish \
  --title "<user-visible template name>" \
  --kind document \
  --source <the original .pdf> \
  --cover cover.png \
  --page-count <pageCount from cover-page.mjs> \
  --package package
```

Publish without `--cover` and `--page-count` only when `cover-page.mjs`
failed; report what it said. Say the template exists only after the command
succeeds.

## Prerequisites

```bash
pip install pymupdf
python3 scripts/ensure_pandoc.py --dir ./vendor   # then run the export PATH line it prints
```

## Steps

### 1. Analyse

```bash
python3 scripts/analyze_pdf.py <source.pdf> --json styles.json
```

Read the report:

- `[structure tree]` present → take the heading levels in step 3 from it.
- "No text layer" → OCR the PDF first, then restart.
- `[body candidates]` → the chosen group must be running prose. If its sample
  is a table header, an index or a caption, re-run with `--body <rank>`.

### 2. Declare the column count

```bash
okou presentation screenshot --input <source.pdf> --out shots
```

Look at a page. Re-run step 1 with `--columns N`.

### 3. Map the heading levels

Under `[inferred styles]`, decide each group's role from its sample text and
write the map:

```
--map 1=Heading1,2=Title,3=Heading2
```

Right side: `Title`, `Subtitle`, `Heading1`..`Heading9` or `skip`. The
largest group is usually the document title, not `Heading1`.

### 4. Settle the margins

Use the `suggested` row. Where `measured` disagrees with it by more than
rounding, measure the page yourself and pass `--top`, `--right` or `--left`
in cm. The bottom margin is never measured. Pass `--bottom` as:

- the `measured` bound, when some page is full to the bottom;
- for a Typst source with a footer, `(page height − footer baseline − 0.73 ×
  footer size) / 0.7`, in cm;
- otherwise the mirror of the top, which `suggested` already holds.

On a two-column document the two columns must come out the same width.

### 5. Build

```bash
python3 scripts/build_reference.py styles.json reference.docx \
        --map 1=Heading1,2=Title,3=Heading2 [--bottom 2.2 ...]
```

`--map` keys are the `#` column of `[inferred styles]`. Map every group that
is a heading; leave captions and footnotes unmapped.

### 6. Verify

```bash
python3 scripts/verify_roundtrip.py reference.docx styles.json \
        --map 1=Heading1,2=Title,3=Heading2
```

Same `--map` as step 5. Exit code must be 0. `NOT MEASURED` is not a failure.

### 7. Package

```bash
python3 scripts/make_package.py <source.pdf> reference.docx styles.json <out dir> \
        --map 1=Heading1,2=Title,3=Heading2 --body 2 [--bottom 2.2 ...]
```

Pass every flag used in steps 1–5. The output directory name is the skill
name; `--name` overrides it. Add anything the scripts could not measure to the
package's `Limits`.

### Optional: adjust styles, add a header or footer

```bash
python3 scripts/set_style.py reference.docx --list
python3 scripts/set_style.py reference.docx "Block Text" --size 10.5 --color 6C757D
python3 scripts/set_style.py reference.docx "Source Code" --create --font Consolas --size 9
python3 scripts/set_header_footer.py reference.docx --header "Company" --footer "Page " --page-number
python3 scripts/set_header_footer.py reference.docx --header 'Title\tv2.3'   # left / right
```

Then step 6 with `--structure-only`, then step 7.

### 8. Publish

```bash
node ../scripts/cover-page.mjs --input <source.pdf> --out cover.png
```

```bash
npx --yes --package="${CLI_PKG_URL}" okou user-template publish \
  --title "<user-visible template name>" \
  --kind document \
  --source <source.pdf> \
  --cover cover.png \
  --page-count <pageCount from cover-page.mjs> \
  --package <out dir>
```

Publish without `--cover` and `--page-count` only when `cover-page.mjs`
failed; report what it said. Say the template exists only after the command
succeeds.

## Rules

- Reproduce the source. Do not correct an inverted hierarchy or a style left
  at a default; the package records it.
- Steps 2–4 are not recorded in the PDF. Settle each against the evidence the
  step names, never the script's default.
- The running head and foot are rebuilt from `[running head/foot]`. If that
  line lists body text, the source has no header; run
  `set_header_footer.py reference.docx --clear`.
- Change the column layout only when asked.

## Troubleshooting

| Symptom | Action |
|---|---|
| Every heading level is off by one | Redo step 3 from the `sample` column |
| Right margin far too large | No line fills the column; measure it off a page and pass `--right` |
| Single-page PDF gives bad margins | Running heads cannot be detected; measure all four and pass them |
| Paragraph metrics implausible, or the body candidate is a table | Re-run step 1 with `--body <rank>` |
| Body text splits into several groups | Real difference in size, colour or weight; keep the largest, `--map <n>=skip` the rest |
| Space after reads NOT MEASURED | No paragraph is followed by a paragraph; pandoc's default stays |
| Heading before/after look off | `set_style.py --before/--after`, then step 6 with `--structure-only` |
| Verify fails after a deliberate change | Re-run step 6 with `--structure-only` |
| Heading gaps near zero on a multi-column source | `--columns` was not passed; redo step 2 |
| A header or footer added later sits a few points off | Step 1 sets the distance from the font's hhea metrics; when it printed no `hhea` line, install the source's font and rerun, or pass `set_header_footer.py --header-distance PT --footer-distance PT` (page edge to the line box, baseline − 1.16 × size for Noto Sans CJK) |
| LibreOffice preview shows a smaller gap above a heading than the source | Expected. LibreOffice takes the larger of space-after and space-before; Word adds them, and the template is written for Word |
| Title→Subtitle or Subtitle→Heading gap doubles in Word | Both sides carry the same gap (Word adds them, LibreOffice takes the larger). Zero one side: `set_style.py reference.docx "Subtitle" --before 0` |
| A paragraph repeated on every page is listed as a running head | Body text in the header band. Pass the margins you measured; the styles are unaffected |
