---
name: pdf
description: >
  Create, fill, or reformat PDF files, including research and technical reports with
  tables, charts, equations, citations, figures, code, and flowcharts. Use for
  "make a PDF", "write a proposal", "professional document", "cover page",
  "fill in this PDF form", "what fields does this PDF have", "reformat this
  document", or "convert this Markdown/text to PDF". Distinguish named manuscript
  requirements (APA, IEEE, journal/institution templates) from visual presets:
  --type academic is appearance, not standards compliance or research expertise.
  For a PDF companion to Word, render the DOCX through ../docx/SKILL.md so both
  requested deliverables retain the same content and layout.
license: MIT
metadata:
  version: "1.0"
  category: document-generation
---

# PDF

## 1. Common requirements

Set `SKILL_DIR` to the absolute directory containing this file (the `pdf/`
subdirectory of the Office package). Resolve reference paths relative to it.
Identify the requested output format(s), source, content features, and formatting
requirements before choosing an operation. Deliver only the requested format(s);
a DOCX used internally to author a PDF is not an additional deliverable.

Honor explicit user instructions and supplied templates before visual defaults,
including typography, colors, cover/no-cover layout, spacing, and numbering.
Do not silently replace a requirement with a preset. Verify actual capabilities;
disclose unavailable fonts or unsupported standard/layout requirements rather
than claiming compliance. Presets do not provide complete academic research or
finance, legal, or medical expertise.

## 2. Named manuscript requirement or visual preset

- **Named manuscript requirements:** for strict APA, IEEE, or journal/institution
  formatting, read the supplied requirements and select a capable authoring
  route that can actually implement them. `--type academic` does **not** implement APA/IEEE.
  The default cover and 10.5pt business-body scale must not override an explicit
  manuscript. When suitable, author via [DOCX](../docx/SKILL.md) and export to PDF;
  verify that route's actual fonts and layout capabilities too. If no available
  route can meet a constraint, disclose it and agree an alternative, not a false
  standards-compliant PDF. This is authoring selection, not a new PDF engine mode.
- **Visual-only request:** for a generic, nonstandard academic-looking PDF or
  business/technical report, select a `--type` visual preset and relevant content
  features independently. Read [design/design.md](design/design.md) for preset
  names, cover patterns, tokens, override flags, and appearance QA before CREATE
  or REFORMAT. Agent reasoning selects the preset; `palette.py` does not analyze
  the document's domain or validate its substance.
- **DOCX companion control:** if Word and PDF are requested together, render the
  authored DOCX through [the DOCX route](../docx/SKILL.md); do not independently
  redesign the PDF with this cover/body pipeline.

## 3. Select the operation

| User intent | Route | Scripts used |
|---|---|---|
| Generate a new PDF with this cover/body pipeline | **CREATE** | `palette.py` → `cover.py` → `render_cover.js` → `render_body.py` → `merge.py` |
| Fill / complete form fields in an existing PDF | **FILL** | `fill_inspect.py` → `fill_write.py` |
| Reformat / re-style an existing document | **REFORMAT** | `reformat_parse.py` → then full CREATE pipeline |

For a creation/redesign request, ask whether there is an existing document if
unclear: yes → REFORMAT, no → CREATE. FILL stays separate; an existing input alone
does not authorize redesign. These remain the three implemented operations.
Read-only field inspection is covered by FILL; no new general READ, OCR, scans,
signature, or exact-layout editing workflow is provided here. PDF text parsing is
best-effort, not a claim of lossless layout preservation or source reconstruction.

### Load content features directly

Read the [block contract](references/content.md#block-contract) for every CREATE
or REFORMAT using this pipeline, then only the relevant feature sections below.
The content reference is the single authority for block fields and conventions;
the design guide owns appearance, not duplicate schemas.

| Required feature | Read directly |
|---|---|
| Headings, prose, lists, tables, breaks, spacing | [Common blocks and tables](references/content.md#common-blocks-and-tables) |
| Equations, labels, mathtext limits | [Mathematics](references/content.md#mathematics) |
| Bar / line / pie, datasets, chart defaults | [Charts](references/content.md#charts) |
| Images, figures, captions, shared numbering | [Figures and captions](references/content.md#figures-and-captions) |
| Citations and references | [Bibliography](references/content.md#bibliography) |
| Code whitespace and language labels | [Code](references/content.md#code) |
| Process nodes, arrows, back-edges | [Flowcharts](references/content.md#flowcharts) |
| Any of these features in delivered PDF | [Feature-specific rendering QA](references/content.md#feature-specific-rendering-qa) |

### Environment and delivery

For this cover/body pipeline, run `bash "$SKILL_DIR/scripts/make.sh" check`
once per session before this pipeline's CREATE/REFORMAT. It verifies an actual
Chromium launch. A named manuscript using another authoring route follows that
route's setup and validation instead; DOCX-to-PDF does not require Chromium
unless it also invokes this pipeline. If needed, install dependencies with
`bash "$SKILL_DIR/scripts/make.sh" fix` in an activated Python virtual environment;
on Linux, Chromium may also need `npx playwright install-deps chromium`.
FILL and read-only inspection need Python and `pypdf`, not the browser pipeline;
do not make them install Chromium. Read only the guide and scripts for the route.

For a user-requested rendered preview or visual review, create `preview/`, run
`pdftoppm -png -r 120 output.pdf preview/page`, and inspect the images. Apply the
linked appearance and feature QA to actual output; a merge success alone is not
proof of correct rendering or compliance. Report unexecuted checks as unverified.

## Route A: CREATE

Full pipeline — content → design tokens → cover → body → merged PDF.

```bash
bash "$SKILL_DIR/scripts/make.sh" run \
  --title "Q3 Strategy Review" --type proposal \
  --author "Strategy Team" --date "October 2025" \
  --accent "#2D5F8A" \
  --content content.json --out report.pdf
```

Prepare `content.json` using the linked contract and feature guidance. Preset and
color options are in [Visual presets and overrides](design/design.md#visual-presets-and-overrides).
Do not treat sample/default content as a finished user document.

## Route B: FILL

Fill form fields in an existing PDF without altering layout or design.
Always run `fill_inspect.py` first to get exact field names.

```bash
# Step 1: inspect
python3 "$SKILL_DIR/scripts/fill_inspect.py" --input form.pdf

# Step 2: fill
python3 "$SKILL_DIR/scripts/fill_write.py" --input form.pdf --out filled.pdf \
  --values '{"FirstName": "Jane", "Agree": "true", "Country": "US"}'
```

| Field type | Value format |
|---|---|
| `text` | Any string |
| `checkbox` | `"true"` or `"false"` |
| `dropdown` | Must match a choice value from inspect output |
| `radio` | Must match a radio value (often starts with `/`) |

## Route C: REFORMAT

Parse an existing document → content.json → CREATE pipeline.

```bash
bash "$SKILL_DIR/scripts/make.sh" reformat \
  --input source.md --title "My Report" --type report --out output.pdf
```

**Supported input formats:** `.md` `.txt` `.pdf` `.json`
For structured Markdown, select content guidance by the actual features, not by
filename or preset. The wrapper parses then renders; it does not enforce the
feature QA or guarantee preservation of every source structure. No new parser,
PDF-source reconstruction safeguards, or engine semantics are introduced here.

## Environment reference

```bash
bash "$SKILL_DIR/scripts/make.sh" check   # verify all deps, including browser launch
bash "$SKILL_DIR/scripts/make.sh" fix     # auto-install missing deps
bash "$SKILL_DIR/scripts/make.sh" demo    # build a sample PDF
```

| Tool | Used by | Install |
|---|---|---|
| Python 3.9+ | all `.py` scripts | system |
| `reportlab` | `render_body.py` | `pip install reportlab` |
| `pypdf` | fill, merge, reformat | `pip install pypdf` |
| Node.js 18+ | `render_cover.js` | system |
| `playwright` + Chromium | `render_cover.js` | `npm install -g playwright && npx playwright install chromium` |
| `matplotlib` | math, charts, flowcharts | `pip install matplotlib` |
