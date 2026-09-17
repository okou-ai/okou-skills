---
name: docx-reverse-template
description: "Reverse-engineer an existing Word document into a loadable template skill: SKILL.md, reference.docx and the source document. Use when asked to reverse a docx, build a reference.docx, extract a Word template, apply a company template to Markdown, or set up --reference-doc."
---

# Reverse a docx into a template package

Takes one `.docx` and produces a template package directory ready to hand over.

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

```bash
sudo apt-get update -qq && sudo apt-get install -y -qq libreoffice-writer
soffice --headless -env:UserInstallation=file:///tmp/lo \
        --convert-to pdf --outdir . <source.docx>
okou presentation screenshot --input <source.pdf> --out package/pages
```

`package/` holds three things and nothing else. `SKILL.md` and
`design-system.md` are both required and neither may be empty — publish rejects
the archive otherwise.

`package/SKILL.md`, how a later run uses the template:

````markdown
---
name: <template-slug>
description: <what this document is, in one line>
---

Follow the source file's own styling. It is the authority for page size,
margins, typography, colour, and the position of every block.

Replace the content, keep the composition:

- <one line per entry a new document has to fill>

`pages/` holds the source's rendered pages in order.
````

`package/design-system.md`, what the pages show: the regions and where they sit,
the type hierarchy, the colour roles, the repeated blocks.

Read both off the rendered pages, and write nothing they do not show.

```bash
npx --yes --package="${CLI_PKG_URL}" okou user-template publish \
  --title "<user-visible template name>" \
  --kind document \
  --source <the original .docx> \
  --package package
```

`--kind document` takes no `--pages`; they ride inside `--package`. Say the
template exists only after the command succeeds.

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
