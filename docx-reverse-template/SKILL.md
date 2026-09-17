---
name: docx-reverse-template
description: Reverse-engineer an existing Word document into a reusable Pandoc template package, delivering reference.docx plus the source document and usage notes. Use when asked to reverse a docx, build a reference.docx, extract a Word template, apply a company template to Markdown, or set up --reference-doc.
---

# Reverse a docx into a template package

Takes one `.docx` and produces a template package directory ready to hand over.

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

That literal text is copied verbatim into every document made from the template.
Document numbers, versions, owners and dates belonging to the source have to be
replaced in step 3. Page numbers and section names shown as `[fields: ...]` are
computed by Word and need no action.

Ignore the exit code and continue.

### 2. Build the template

```bash
python3 scripts/build_reference.py <source.docx> reference.docx
```

Missing styles are filled in automatically. The output splits them into
"derived" and "using pandoc's default spacing". Only the second group may need
step 3; otherwise go straight to step 4.

### 3. Set the paper size, and adjust styles

Set the paper size whenever step 2 printed `ACTION REQUIRED`. Everything else in
this step is optional.

```bash
python3 scripts/set_header_footer.py reference.docx --paper A4 \
        --replace "DOC-2026-001=[DOC ID]" --replace "Jane Doe=[OWNER]"

python3 scripts/set_header_footer.py reference.docx --columns 2 --column-gap 20
python3 scripts/set_header_footer.py reference.docx --columns 1

python3 scripts/set_style.py reference.docx --list

python3 scripts/set_style.py reference.docx "Block Text" \
        --font "Georgia" --size 10.5 --color 6C757D --before 6 --after 6

python3 scripts/set_style.py reference.docx "Source Code" --create --font "Consolas" --size 9

```

When step 1 flagged literal header or footer text, swap the values with
`--replace`. It edits the text in place, so tab columns, border rules, a
first-page variant and any table in the footer survive. It exits non-zero when a
value is not found, and composes with the other flags in one invocation.

`--columns` **changes** the layout; it is not needed to preserve one. A
multi-column source is already multi-column in the template, because `w:cols`
rides along in `sectPr` with the paper size and margins. Step 1 reports the
count so the inheritance is visible.

`--header` / `--footer` rebuild the part from scratch and flatten all of that.
Use them only for a template whose header and footer are plain text, or when
adding one that does not exist:

```bash
python3 scripts/set_header_footer.py reference.docx \
        --footer "Confidential - page " --page-number
```

Either way only the kind being set is touched, so a logo in the header survives
a footer change.

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

Hand over the whole directory, not just `reference.docx`.

## Rules

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
