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

### 2. Pick the body cluster — human decision

Read `[body candidates]` and decide which cluster is the running prose. The
default is just the largest one by character count, which loses whenever a table,
an index or a caption block holds more characters than the text around it.

This choice drives every paragraph metric — line advance, space after, first-line
indent, and the size threshold that decides what counts as a heading. A wrong
pick corrupts all of them and nothing downstream complains.

```
rank   size   colour  chars  lines  pages  sample
1       9.4  #242121    789     65      6  指标                      <- default
2      10.5  #242121    737     33      5  本报告覆盖试点项目第一阶段的交付范围…   <- the real body
```

Rank 1 there is a table column header; rank 2 is prose. Judge it from the sample
text, not the character count, and re-run with `--body 2`.

### 3. Assign heading levels — human decision

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

### 4. Set the bottom margin — human decision

Read `[margins]` and take the whole `suggested` row, not the `measured` row.

The bottom margin is only bounded, never measured. The report resolves it one of
two ways and says which:

- the top margin fits under the bound, so the layout is consistent with being
  symmetric and the top value is suggested
- the top margin **exceeds** the bound, so the layout is not symmetric and the
  rounded bound is suggested instead

Override either with `--bottom <cm>`. `build_reference.py` uses this suggestion
by default, so a non-symmetric layout no longer needs the flag — pass it only to
disagree with the report.

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

Pass the same `--map`. Without it the cluster-to-style match is guessed from
size and colour, which reports a false failure when two clusters resolve to one
style.

The exit code must be 0. It catches dangling style references and reconciles
the output's size, colour, spacing, indent and alignment against the inferred
values.

Fields the analysis could not measure are skipped rather than compared, so a
`NOT MEASURED` space-after is not a failure.

### 7. Package and deliver

```bash
python3 scripts/make_package.py <source.pdf> reference.docx styles.json <output dir> \
        --map 1=Heading1,2=Title,3=Heading2 --body 2
```

Pass `--map`, `--bottom` and `--body` through verbatim. They are recorded in the
"Human decisions" section of the README, and `--body` is replayed when the
report is regenerated — omitting it makes `report.txt` re-analyse with the
default cluster and contradict the template shipped beside it.

Hand over the whole directory.

### Optional: adjust styles, add a header or footer

```bash
python3 scripts/set_style.py reference.docx --list
python3 scripts/set_style.py reference.docx "Block Text" --size 10.5 --color 6C757D
python3 scripts/set_style.py reference.docx "Source Code" --create --font "Consolas" --size 9
python3 scripts/set_header_footer.py reference.docx --header "Company" --footer "Page " --page-number
```

Re-run step 6 with `--structure-only`, then step 7.

The full reconciliation compares the template against `styles.json`, so it fails
on any value you deliberately changed. `--structure-only` keeps the dangling
reference check and drops that comparison.

## Rules

- Steps 2, 3 and 4 are human decisions; do not let a script stand in for them.
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
| Paragraph metrics look implausible | The wrong body cluster was picked; re-run step 2 with `--body <rank>` |
| The default body candidate is a table or an index | Expected; that is what step 2 exists to catch |
| Body text splits into several clusters | Clusters merge by size, colour and weight, so this means a real difference; keep the largest and drop the rest with `--map <n>=skip` |
| Space after reads NOT MEASURED | Every paragraph is followed by a table, list or heading, so no gap exists to measure; the template keeps pandoc's default |
| Heading before/after look off | They are derived, not recorded. The report prints the raw baseline gaps beside them; override with `set_style.py --before/--after` and re-verify using `--structure-only` |
| Verify fails after editing a style by hand | Expected; re-run it with `--structure-only` |
