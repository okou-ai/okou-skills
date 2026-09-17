---
name: docx-reverse-template
description: "Reverse-engineer an existing Word document into a loadable template skill: SKILL.md, reference.docx and the source document. Use when asked to reverse a docx, build a reference.docx, extract a Word template, apply a company template to Markdown, or set up --reference-doc."
---

# Reverse a docx into a template package

Takes one `.docx` and produces a template package directory ready to hand over.

Run every command below from `reverse-template/docx/`.

## Before anything — an article, or a form?

This branch builds a style sheet: paper size, margins, columns, per-style type,
a header and a footer. Pandoc pours one stream of paragraphs into it. Look at
the rendered pages before going further.

An **article** is written top to bottom and could be written again at another
length on another subject — a report, a paper, a white paper, a manual, a
policy, a memo. A **form** is one object with a fixed set of entries, and a new
one fills the same entries — a resume, a receipt, an invoice, a certificate, an
offer letter, a spec sheet.

Stay here only for an article whose body runs as one stream. One column is one
stream, and so are columns of equal width.

Take `../source-style/SKILL.md` instead when the file is a form, when a sidebar
or a margin note sits beside the body, or when the call is close. A style sheet
holds none of those, and it drops them silently; that branch keeps everything.

Judge on what the document is, not on how it looks. A plain single-column
resume with no colour is still a form.

## Prerequisites

```bash
python3 scripts/ensure_pandoc.py --dir ./vendor
```

Requires pandoc 3.x. The script checks for it or installs it; run the
`export PATH` line it prints.

## Steps

### 1. Inspect the source

```bash
python3 scripts/inspect_docx.py <source.docx>
```

Note from the report: which required styles are missing, the paper size, margins
and column count, and — if a `REVIEW` block appears — the literal header and
footer text.

Literal header and footer text is copied verbatim into every document made
from the template, so replace the source's own numbers, versions, owners and
dates in step 3. `[fields: ...]` are computed by Word and need no action.

Ignore the exit code and continue.

### 2. Build the template

```bash
python3 scripts/build_reference.py <source.docx> reference.docx
```

Missing styles are filled in automatically. Only the ones listed as "using
pandoc's default spacing" may need step 3; otherwise go to step 4.

### 3. Set the paper size, and adjust styles

Set the paper size whenever step 2 printed `ACTION REQUIRED`. Everything else in
this step is optional.

```bash
# Paper size, and the header/footer values step 1 flagged. The left side of
# each --replace is text the source's own header literally says; the right
# side is what every document built from the template should say instead.
python3 scripts/set_header_footer.py reference.docx --paper A4 \
        --replace "DOC-2026-001=[DOC ID]" --replace "Jane Doe=[OWNER]"

# Change the column layout. Not needed to keep the one the source already has.
python3 scripts/set_header_footer.py reference.docx --columns 2 --column-gap 20
python3 scripts/set_header_footer.py reference.docx --columns 1

# Read the current style values back out
python3 scripts/set_style.py reference.docx --list

python3 scripts/set_style.py reference.docx "Block Text" \
        --font "Georgia" --size 10.5 --color 6C757D --before 6 --after 6

python3 scripts/set_style.py reference.docx "Source Code" --create --font "Consolas" --size 9
```

`--replace` edits the text in place, so tab columns, border rules, a
first-page variant and any table in the footer survive. It exits non-zero when
a value is not found, and composes with the other flags in one invocation.

`--columns` **changes** the layout and is not needed to preserve one: a
multi-column source is already multi-column in the template. Changing the count
on an unequal-width layout drops the per-column widths, which the output says.

`--header` / `--footer` rebuild the part and flatten all of that. Use them only
on a plain-text header or footer, or to add one that does not exist:

```bash
python3 scripts/set_header_footer.py reference.docx \
        --footer "Confidential - page " --page-number
```

Only the kind being set is touched, so a logo in the header survives a footer
change.

Pass the `w:name` of the style (`heading 2`, `Body Text`), case-insensitive.
Add `--create` for a style the template does not define.

Options: `--font --size --color --bold/--no-bold --italic/--no-italic --before
--after --line --indent --left-indent --align --keep-next`

Return to step 4 afterwards.

### 4. Verify

```bash
python3 scripts/verify_reference.py reference.docx
```

The exit code must be 0. Two things fail it:

- **dangling style names** — go back to step 2
- **no paper size** — the source document never set one, so output would follow
  the reader's locale default (A4 in most of the world, Letter in the US) and
  the page count would differ per machine. Fix it in step 3 with
  `set_header_footer.py reference.docx --paper A4`

**Do not skip this step**: a missing style raises no error, Word simply renders
the text as Normal.

### 5. Package and deliver

```bash
python3 scripts/make_package.py <source.docx> reference.docx <output dir>
```

Append anything you hit that the scripts could not read to "Known limits" in
the package's `SKILL.md`.

Hand over the whole directory.

## Rules

- Reproduce the source, do not correct it. An inverted heading hierarchy or
  a style left at Word's default is the source's own value; the package
  records it as deliberate.
- Do not edit `w:styleId`. Pandoc matches on `w:name`, so the numeric styleIds
  produced by localised Word builds work as they are.
- Do not invent style names outside Pandoc's set; they are never referenced.
  Modify the existing ones.
- Step 4 is mandatory.

## Troubleshooting

| Symptom | Action |
|---|---|
| Headings render like body text | Run step 4; it names the dangling styles |
| CJK text falls back to a serif font | Use `set_style.py --font`, which also writes `w:eastAsia` |
| Code block appearance will not change | `set_style.py reference.docx "Source Code" --create` |
| Output carries the source document's number or owner | Literal header/footer text; replace it with `set_header_footer.py` |
| A docx saved by WPS fails to parse | Ask a person to re-save it from Word, then restart at step 1 |
