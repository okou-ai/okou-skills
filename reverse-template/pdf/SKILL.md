---
name: pdf-reverse-template
description: "Infer the typographic styles of a PDF and reverse-engineer it into a loadable template skill: SKILL.md, reference.docx and the source PDF. Use when asked to reverse a PDF, extract PDF styles, turn a PDF into a Word template, or analyse a PDF's layout."
---

# Reverse a PDF into a template package

Takes one `.pdf` and produces a template package directory ready to hand over.

**If the original .docx exists, use `../docx/SKILL.md` instead.** If the PDF's
pages are slides rather than a document, use `../presentation/SKILL.md`.

Run every command below from `reverse-template/pdf/`.

The router must have read the pages as an article whose body runs as one
stream. A form — a resume, a receipt, a certificate — or a body with a sidebar
beside it takes `../source-style/SKILL.md` instead.

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

Read the report before going on.

`[structure tree]` says whether this is a tagged PDF. If `/StructTreeRoot` is
present, take the heading levels in step 3 from the structure tree rather than
from font size. "No text layer" means a scan; OCR it first and come back.

`[body candidates]` marks the group it took as body text — the largest by
character count. Check that sample is running prose; if it is not, re-run with
`--body <rank>` on the one that is. Rank 1 below is a table column header:

```
rank   size   colour  chars  lines  pages  sample
1       9.4  #242121    789     65      6  Metric                       <- default
2      10.5  #242121    737     33      5  This report covers the first  <- the real body
```

### 2. Declare the column count

Read `[columns]`. The report lists the x positions lines start at, but those
bands appear for a table exactly as they do for columns, so the count settles
nothing on its own.

Render a page and look at it:

```bash
okou presentation screenshot --input <source.pdf> --out shots
```

Then pass `--columns N`.

### 3. Assign heading levels

Read the `sample` column under `[inferred styles]` and decide what each group
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

### 4. Set the bottom margin

Read `[margins]` and take the whole `suggested` row, not the `measured` row.

The bottom margin is only bounded, never measured. The report resolves it one of
two ways and says which:

- the top margin fits under the bound, so the layout is consistent with being
  symmetric and the top value is suggested
- the top margin **exceeds** the bound, so the layout is not symmetric and the
  rounded bound is suggested instead

`--bottom <cm>` overrides it; the suggestion is used by default.

The suggested row rounds to a table of common values, so check it against
`measured`. Where they disagree by more than rounding, measure it yourself and
pass `--top`, `--left` or `--right`. On a two-column document the two columns
must come out the same width — one edge comes from the gutter and the other
from the right margin, so that is a free check.

### 5. Build the template

```bash
python3 scripts/build_reference.py styles.json reference.docx \
        --map 1=Heading1,2=Title,3=Heading2
```

### 6. Verify

```bash
python3 scripts/verify_roundtrip.py reference.docx styles.json \
        --map 1=Heading1,2=Title,3=Heading2
```

Pass the same `--map`, or two groups resolving to one style read as a failure.
The exit code must be 0. A `NOT MEASURED` space-after is not a failure.

### 7. Package and deliver

```bash
python3 scripts/make_package.py <source.pdf> reference.docx styles.json <output dir> \
        --map 1=Heading1,2=Title,3=Heading2 --body 2
```

Pass `--map`, `--body` and every margin you overrode through verbatim;
`SKILL.md` is the only place they are recorded.

Append anything you hit that the scripts could not measure to "Known limits"
in the package's `SKILL.md`.

Hand over the whole directory.

### Optional: adjust styles, add a header or footer

```bash
python3 scripts/set_style.py reference.docx --list
python3 scripts/set_style.py reference.docx "Block Text" --size 10.5 --color 6C757D
python3 scripts/set_style.py reference.docx "Source Code" --create --font "Consolas" --size 9
python3 scripts/set_header_footer.py reference.docx --header "Company" --footer "Page " --page-number
python3 scripts/set_header_footer.py reference.docx --header 'Title\tv2.3'   # left / right columns
```

Re-run step 6 with `--structure-only` — the full check fails on any value you
changed on purpose — then step 7.

## Rules

- Steps 2 to 4 are values the PDF does not record. The script prints a guess
  for each; settle it against the evidence the step names — a rendered page,
  the sample text, the measured bound — instead of passing the guess through.
- Take margins from the `suggested` row, never the `measured` row.
- Reproduce the source, do not correct it. An inverted heading hierarchy or
  a style left at Word's default is the source's own value; the package
  records it as deliberate.
- The source PDF's header and footer are not carried over. Add them with
  `set_header_footer.py` if the recurring content reported in step 1 matters.
  A running head split left and right is one `--header` with a tab in it.
- Font names are restored from embedded subset names, but the font still has to
  be installed on the target machine to render.

## Troubleshooting

| Symptom | Action |
|---|---|
| Every heading level is off by one | Redo step 3 using the `sample` column |
| The right margin reads far too large | No line fills the column; round to a common value yourself |
| A single-page PDF gives bad margins | Running heads cannot be detected; measure all four off a rendered page |
| Paragraph metrics look implausible, or the default body candidate is a table or an index | Re-run step 1 with `--body <rank>` |
| Body text splits into several groups | Groups merge by size, colour and weight, so this means a real difference; keep the largest and drop the rest with `--map <n>=skip` |
| Space after reads NOT MEASURED | Every paragraph is followed by a table, list or heading, so no gap exists to measure; the template keeps pandoc's default |
| Heading before/after look off | They are derived, not recorded. The report prints the raw baseline gaps beside them; override with `set_style.py --before/--after` and re-verify using `--structure-only` |
| Verify fails after a deliberate style change | Expected; re-run it with `--structure-only` |
| Heading gaps are near zero on a multi-column source | `--columns` was not declared; redo step 2 |
