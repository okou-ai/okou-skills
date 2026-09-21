---
name: docx-reverse-template
description: "Reverse-engineer a Word document into a loadable template skill: SKILL.md, reference.docx and the source document. Use when asked to reverse a docx, build a reference.docx, extract a Word template, apply a company template to Markdown, or set up --reference-doc."
---

# Reverse a docx into a template package

Input: one `.docx`. Output for an article: a directory holding `SKILL.md`,
`reference.docx` and `source.docx`. Output for a fixed structure: `SKILL.md`
and a copy of the source beside it.

Run every command below from `reverse-template/docx/`.

## Before anything — an article, or a fixed structure?

Look at the rendered pages.

An **article** is written top to bottom and could be written again at another
length on another subject — a report, a manual, a policy. A **fixed structure**
is the whole document as one arrangement of blocks, and a new one keeps that
arrangement and changes the content — a resume, an invoice, a certificate.

Judge on what the document is, not on how it looks — a plain single-column
resume is still a fixed structure. An article continues at Prerequisites below.

### A fixed structure: package the file and fill it in

A style sheet drops those silently, and no description reproduces a background
image. Ship the file itself, and have each new document edit a copy of it.

List the runs a new document replaces:

```bash
python3 scripts/inspect_docx.py <source.docx> --slots
```

Copy the source into `package/`, then write `package/SKILL.md` beside it:

````markdown
---
name: <template-slug>
description: <what this document is, in one line>
---

Make the new document by editing a copy of `<source filename>`.

Change only the text inside `<w:t>`. Everything else stays exactly as the file
has it: the rest of `word/document.xml`, and every other entry in the archive,
byte for byte.

The wording sits here, in reading order:

| Current text | Holds |
|---|---|
| `<one run's text>` | <what a new document says there> |

To add or drop a <line/row/section>, copy or delete a whole `<w:p>` of the same
kind and edit its text. Never build a paragraph from scratch and never let one
fall back to a style default; that is how the formatting slips.

Rewrite the entry in the zip. Opening and saving the file through python-docx or
LibreOffice rewrites parts that must stay byte-identical.

Render the result and look — if the text has outgrown <the page, the card, its
box>, shorten the wording, never the type or the spacing.

Re-author the design only when the user asks for a new document in this style,
rather than for this document with new wording.
````

One row per run, named off `--slots` and the rendered pages; write nothing they
do not show. A label and its value are usually separate runs — give the value a
row and leave the label out. Leave a field's run out too; Word recomputes it.
Word the table as where the wording sits, never as the set of edits allowed — a
new document may need one line more, or one fewer.

```bash
node ../scripts/cover-page.mjs --input <the original .docx> --out cover.png
```

```bash
npx --yes --package="${CLI_PKG_URL}" okou user-template publish \
  --title "<user-visible template name>" \
  --kind document \
  --source <the original .docx> \
  --cover cover.png \
  --page-count <pageCount from cover-page.mjs> \
  --package package
```

`--source` and the copy in `package/` are both needed: the first is what a
reader opens, the second is the only one a later run can open. Publish without
`--cover` and `--page-count` only when `cover-page.mjs` failed; report what it
said.

Say the template exists only after the command succeeds.

## Prerequisites

```bash
python3 scripts/ensure_pandoc.py --dir ./vendor   # then run the export PATH line it prints
```

## Steps

### 1. Inspect

```bash
python3 scripts/inspect_docx.py <source.docx>
```

Note the missing required styles, the paper size, and every `REVIEW` line.
`[styles in use]` decides the route:

- the document uses its own style names: run step 2 with the `--map` it
  prints, after checking which pandoc style each name plays the part of;
- the document is formatted by hand (`Normal` with direct formatting): its
  styles carry nothing. Render it as the inspector says and follow
  `../pdf/SKILL.md` on the render instead of continuing here.
Ignore the exit code.

### 2. Build

```bash
python3 scripts/build_reference.py <source.docx> reference.docx \
        [--map 'Memo Title=Title,Section Head=Heading1,Body Copy=BodyText']
```

Missing styles are filled in. If it prints `ACTION REQUIRED`, set the paper
size in step 3.

### 3. Adjust

Required when step 1 or 2 asked for it; otherwise optional.

```bash
# paper size, and the header values step 1 flagged (left = literal text in the source)
python3 scripts/set_header_footer.py reference.docx --paper A4 \
        --replace "DOC-2026-001=[DOC ID]" --replace "Jane Doe=[OWNER]"

# style values
python3 scripts/set_style.py reference.docx --list
python3 scripts/set_style.py reference.docx "Block Text" --font Georgia --size 10.5 --color 6C757D
python3 scripts/set_style.py reference.docx "Source Code" --create --font Consolas --size 9

# only to change the layout; a multi-column source is already multi-column
python3 scripts/set_header_footer.py reference.docx --columns 2 --column-gap 20

# only for a plain-text header/footer, or to add one; rebuilds the part
python3 scripts/set_header_footer.py reference.docx --footer "Confidential - page " --page-number
```

Style names are the `w:name`, case-insensitive. `set_style.py` options:
`--font --east-asia-font --size --color --bold/--no-bold --italic/--no-italic
--before --after --line --indent --left-indent --align --keep-next`.

### 4. Verify

```bash
python3 scripts/verify_reference.py reference.docx
```

Exit code must be 0. Dangling style → step 2. No paper size → step 3 with
`--paper`.

### 5. Package

```bash
python3 scripts/make_package.py <source.docx> reference.docx <out dir>
```

The output directory name is the skill name; `--name` overrides it. Add
anything the scripts could not read to the package's `Limits`.

### 6. Publish

```bash
node ../scripts/cover-page.mjs --input <source.docx> --out cover.png
```

```bash
npx --yes --package="${CLI_PKG_URL}" okou user-template publish \
  --title "<user-visible template name>" \
  --kind document \
  --source <source.docx> \
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
- Replace the source's own title, document number, version, owner and date in
  the header and footer with `--replace`; they are copied into every output.
- Change the column layout only when asked.
- Do not edit `w:styleId`. Do not add style names outside pandoc's set.
- Step 4 is mandatory.

## Troubleshooting

| Symptom | Action |
|---|---|
| Headings render like body text | Step 4 names the missing style |
| CJK text falls back to a serif font | The source names no East Asian font. `set_style.py Normal --east-asia-font NAME` fills that slot and leaves the Latin font alone |
| Code blocks will not restyle | `set_style.py reference.docx "Source Code" --create` |
| Output carries the source's number or owner | `set_header_footer.py --replace` |
| Header text sits outside the text area | Step 1 reports the tab stop; rebuild the header with `--header 'left\tright'`, which places it from the margins |
| A docx saved by WPS fails to parse | Re-save it from Word, restart at step 1 |
| A fixed structure comes back redrawn in a similar style | Its package carries no copy of the source, so there was nothing to edit. Add the file and republish |
| A rendered page drops the text held in content controls | LibreOffice exports those as form fields, whose appearance font carries no CJK. Render with `--convert-to png`, or export the PDF with `ExportFormFields` false |
