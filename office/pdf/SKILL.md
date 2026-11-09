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

Set `SKILL_DIR` to the absolute directory containing this file, not the task's
working directory. Identify output format(s), source, content features and
formatting requirements first. Deliver only the requested format(s); an internal
DOCX authoring file is not automatically an extra deliverable.

Use the [unified executable](../scripts/office.py) for supported mechanics:

```bash
OFFICE="$SKILL_DIR/../scripts/office.py"
python3 "$OFFICE" list
python3 "$OFFICE" preflight --format pdf
python3 "$OFFICE" create --format pdf --content content.json --title "Report" --out output.pdf
python3 "$OFFICE" validate --input output.pdf
```

Actions return JSON receipts and never invoke recursive AI. The author owns
fact boundaries, content semantics, professional judgments and final usability.
Use `--help` for wrapper parameters; `tool-help --tool pdf-create|pdf-env|pdf-palette`
accepts one underlying tool ID at a time. Never overwrite the source; keep
application checks isolated with macros disabled and external links not updated.

Honor explicit requirements and supplied templates, including typography, colors,
cover/no-cover layout, spacing, and numbering. Do not silently substitute a
preset. Verify actual capabilities and disclose unavailable fonts or unsupported
requirements. Presets do not supply research, finance, legal or medical expertise
or standards certification.

## 2. Named manuscript requirement or visual preset

- **Named manuscript:** for strict APA, IEEE or a journal/institution template,
  select capable authoring per [requirement profiles](references/domains/profiles.md).
  `--type academic` does **not** implement APA/IEEE. Consider
  [DOCX](../docx/SKILL.md) and PDF export when appropriate; verify its actual fonts
  and layout too, rather than claiming unsupported compliance.
- **Visual-only:** for a generic, nonstandard academic-looking PDF or another
  designed report, read [presentation](references/common/presentation.md) before
  CREATE/REFORMAT. It owns supported preset names, tokens and overrides.
- **DOCX companion control:** render the authored DOCX through its own route;
  do not independently redesign the PDF with this pipeline.

## 3. Select the operation

| Authorized task | Direct workflow | Existing implementation |
|---|---|---|
| New cover/body PDF | [Route A: CREATE](references/operations/create.md) | `palette.py` → `cover.py` → `render_cover.js` → `render_body.py` → `merge.py` |
| Form inspection or filling | [Route B: FILL](references/operations/fill.md) | `fill_inspect.py` → `fill_write.py` |
| Requested redesign of an existing document | [Route C: REFORMAT](references/operations/reformat.md) | `reformat_parse.py` → CREATE |
| Completed output | [VALIDATE](references/operations/validate.md) | Reopen, source comparison and applicable actual-page QA |

For a creation/redesign request, clarify whether a source exists if needed:
existing source → REFORMAT, no source → CREATE. FILL stays separate; an input
alone does not authorize redesign. These remain the three implemented operations,
with no new general READ, OCR, scans, signature or exact-layout editing workflow.
PDF text parsing is best-effort, not lossless layout or source reconstruction.

Read [environment](references/implementation/environment.md) only for the selected
route. Run `preflight --format pdf` before cover/body CREATE/REFORMAT; this is an
environment probe, not validation of the output. Other authoring routes use their
own setup: DOCX export does not require Chromium, and FILL/read-only inspection
need Python/`pypdf`, not the cover browser. Install dependencies only as permitted.

## Load content features directly

For every CREATE/REFORMAT using this pipeline, read the
[block contract](references/implementation/content.md#block-contract), then only
applicable sections. This is the single block-schema authority; presentation
owns appearance, not duplicated fields. Follow the operation's workflow and
[actual output validation](references/operations/validate.md) before delivery.

| Required feature | Direct reference |
|---|---|
| Headings, prose, lists, tables, breaks and spacing | [Common blocks and tables](references/implementation/content.md#common-blocks-and-tables) |
| Equations, labels and mathtext limits | [Mathematics](references/implementation/content.md#mathematics) |
| Charts, datasets and defaults | [Charts](references/implementation/content.md#charts) |
| Images, figures, captions and shared numbering | [Figures and captions](references/implementation/content.md#figures-and-captions) |
| Citations and references | [Bibliography](references/implementation/content.md#bibliography) |
| Code whitespace and language labels | [Code](references/implementation/content.md#code) |
| Process nodes, arrows and back-edges | [Flowcharts](references/implementation/content.md#flowcharts) |
| Delivered content features | [Feature-specific rendering QA](references/implementation/content.md#feature-specific-rendering-qa) |

## Package organization

`references/common/`, `domains/`, `operations/` and `implementation/` separate
appearance, applicable requirements, workflows and technical detail. All guides
are linked directly above; load only relevant files. `scripts/` entry points and
licenses remain in their existing locations. A successful check, merge or parser
call is not a substitute for inspecting content and actual pages; disclose
unexecuted checks.
