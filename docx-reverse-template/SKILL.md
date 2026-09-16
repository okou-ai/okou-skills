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

Note three things from the report: which required styles are missing, the
header and footer text, and the paper size and margins. Ignore the exit code
and continue.

### 2. Build the template

```bash
python3 scripts/build_reference.py <source.docx> reference.docx
```

Missing styles are filled in automatically. The output splits them into
"derived" and "using pandoc's default spacing". Only the second group may need
step 3; otherwise go straight to step 4.

### 3. Adjust styles (optional)

```bash
python3 scripts/set_style.py reference.docx --list

python3 scripts/set_style.py reference.docx "Block Text" \
        --font "Georgia" --size 10.5 --color 6C757D --before 6 --after 6

python3 scripts/set_style.py reference.docx "Source Code" --create --font "Consolas" --size 9

python3 scripts/set_header_footer.py reference.docx \
        --header "Company name" --footer "Confidential - page " --page-number
```

Pass the `w:name` of the style (`heading 2`, `Body Text`), case-insensitive.
Add `--create` for a style the template does not define.

Options: `--font --size --color --bold/--no-bold --italic/--no-italic --before
--after --line --indent --left-indent --align --keep-next`

Return to step 4 afterwards.

### 4. Verify

```bash
python3 scripts/verify_reference.py reference.docx
```

The exit code must be 0. On failure the report lists the dangling style names;
go back to step 2.

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
| A docx saved by WPS fails to parse | Ask a person to re-save it from Word, then restart at step 1 |
