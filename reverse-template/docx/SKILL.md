---
name: docx-reverse-template
description: "Reverse-engineer a Word document into a loadable template skill: SKILL.md, reference.docx and the source document. Use when asked to reverse a docx, build a reference.docx, extract a Word template, apply a company template to Markdown, or set up --reference-doc."
---

# Reverse a docx into a template package

Input: one `.docx`. Output: a directory holding `SKILL.md`, `reference.docx`
and `source.docx`.

Run every command below from `reverse-template/docx/`.

## Before anything — an article, or a form?

Look at the rendered pages.

An **article** is written top to bottom and could be written again at another
length on another subject — a report, a manual, a policy. A **form** is one
object with a fixed set of entries, and a new one fills the same entries — a
resume, an invoice, a certificate.

Stay here only for an article whose body runs as one stream; one column, or
columns of equal width, is one stream. Judge on what the document is, not on
how it looks — a plain single-column resume is still a form.

### Otherwise: publish the source itself

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
npx --yes --package="${CLI_PKG_URL}" okou user-template publish \
  --title "<user-visible template name>" \
  --kind document \
  --source <the original .docx> \
  --package package
```

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
anything the scripts could not read to the package's `Limits`. Hand over the
whole directory.

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
