---
name: pdf-reverse-template
description: Infer the typographic styles of a PDF and reverse-engineer it into a Pandoc template package, delivering reference.docx plus the source PDF and usage notes. Use when asked to reverse a PDF, extract PDF styles, turn a PDF into a Word template, or analyse a PDF's layout.
---

# Reverse a PDF into a template package

Takes one `.pdf` and produces a template package directory ready to hand over.

**If the original .docx exists, use `docx-reverse-template` instead.**

## Prerequisites

```bash
pip install pymupdf
python3 scripts/ensure_pandoc.py --dir ./vendor
```

Requires pandoc 3.x. The script checks for it or installs it; run the
`export PATH` line it prints.

## Steps

### 1. Analyse

```bash
python3 scripts/analyze_pdf.py <source.pdf> --json styles.json
```

The `[structure tree]` line says whether this is a tagged PDF. If
`/StructTreeRoot` is present, take the step 2 mapping from the structure tree
rather than guessing from font size.

"No text layer" means a scan; OCR it first and come back.

### 2. Assign heading levels — human decision

Read the `sample` column under `[inferred styles]` and decide what each cluster
actually is:

```
role  size    colour    sample
H1   20.0  #1B4F72  Chapter 1        ->  Heading1
H2   16.5  #000000  Technical Guide  ->  Title      <- the document title, not an H2
H3   15.0  #2E86C1  1.1 Overview     ->  Heading2
```

Write it as an argument; the right side takes `Title`, `Subtitle`,
`Heading1`..`Heading9`, or `skip`:

```
--map 1=Heading1,2=Title,3=Heading2
```

Skipping this shifts every level by one.

### 3. Set the bottom margin — human decision

Read `[margins]`. Take the left, right and top values from the `suggested` row,
not the `measured` row.

The bottom margin is only bounded, never measured. Use the top margin value and
confirm it sits below the bound, or override it with `--bottom <cm>`.

### 4. Build the template

```bash
python3 scripts/build_reference.py styles.json reference.docx \
        --map 1=Heading1,2=Title,3=Heading2
```

### 5. Verify

```bash
python3 scripts/verify_roundtrip.py reference.docx styles.json
```

The exit code must be 0. It catches dangling style references and reconciles
the output's size, colour, spacing, indent and alignment against the inferred
values.

### 6. Package and deliver

```bash
python3 scripts/make_package.py <source.pdf> reference.docx styles.json <output dir> \
        --map 1=Heading1,2=Title,3=Heading2
```

Pass `--map` and `--bottom` through verbatim; they are recorded in the "Human
decisions" section of the README.

Hand over the whole directory.

### Optional: adjust styles, add a header or footer

```bash
python3 scripts/set_style.py reference.docx --list
python3 scripts/set_style.py reference.docx "Block Text" --size 10.5 --color 6C757D
python3 scripts/set_style.py reference.docx "Source Code" --create --font "Consolas" --size 9
python3 scripts/set_header_footer.py reference.docx --header "Company" --footer "Page " --page-number
```

Re-run step 5, then step 6.

## Rules

- Steps 2 and 3 are human decisions; do not let a script stand in for them.
- Take margins from the `suggested` row, never the `measured` row.
- The source PDF's header and footer are not carried over. Add them with
  `set_header_footer.py` if the recurring content reported in step 1 matters.
- Font names are restored from embedded subset names, but the font still has to
  be installed on the target machine to render.

## Troubleshooting

| Symptom | Action |
|---|---|
| Every heading level is off by one | Redo step 2 using the `sample` column |
| The right margin reads far too large | No line fills the column; round to a common value by hand |
| A single-page PDF gives bad margins | Running heads cannot be detected; measure all four by hand |
| Body text splits into several clusters | Mixed fonts in the source; keep the largest cluster and drop the rest with `--map <n>=skip` |
