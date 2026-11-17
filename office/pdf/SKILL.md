---
name: pdf
description: >
  Create, fill, or reformat PDF files, including reports with tables, charts,
  equations, citations, figures, code and flowcharts. Use for "make a PDF",
  "fill in this PDF form", "what fields does this PDF have", "reformat this
  document", or "convert this Markdown/text to PDF". For Word plus PDF, render
  the authored DOCX through ../docx/SKILL.md to retain the same source and layout.
license: MIT
metadata:
  version: "1.0"
  category: document-generation
---

# PDF

Set `SKILL_DIR` to the absolute directory containing this file. Identify the
authorized operation, input/source, requested output(s), required features and
user styles first. Deliver only requested formats, not internal authoring files.
Honor supplied templates, fonts, colors, cover/no-cover, spacing and numbering;
disclose unsupported requirements rather than silently replacing them.

## Select the operation first

| Authorized task | Direct workflow | Implementation |
|---|---|---|
| New PDF | [CREATE](references/operations/create.md) | Tokens → cover/body render → merge |
| Form inspection or filling | [FILL](references/operations/fill.md) | `fill_inspect.py` → authorized `fill_write.py` |
| Redesign of an existing document | [REFORMAT](references/operations/reformat.md) | `reformat_parse.py` → CREATE |
| Output acceptance/delivery | [VALIDATE](references/operations/validate.md) | Checks selected by operation/features |

An input alone does not authorize redesign. Read-only form inspection stops
with findings: no authoring check, Chromium, output generation or visual-design
reading. FILL also stays outside the cover/body browser pipeline.
These are the three implemented operations, not a new READ, OCR, scans, signature
or exact-layout editing workflow. PDF text parsing is best-effort, not lossless
layout preservation or source reconstruction.

## Select an authoring route only for CREATE/REFORMAT

- **Word/PDF pair:** render the authored DOCX through [DOCX](../docx/SKILL.md),
  not an independently designed PDF. Use that route's setup/validation.
- **Named manuscript:** only for strict APA, IEEE or a journal/institution
  template, read [requirement profiles](references/domains/profiles.md) and
  choose an actually capable route. `--type academic` is a visual preset, not
  APA/IEEE compliance, certification or substantive domain expertise.
- **This visual pipeline:** use the concise [preset/override catalog](references/common/presentation.md).
  Choose one supported preset (default `general`) and keep its script tokens;
  custom design work is only for a user-requested/necessary departure. Detailed
  aesthetic advice is optional, not another mandatory branch.

Use [environment](references/implementation/environment.md) for selected features
only, after checking input existence/type. All runtime helpers are install-free;
missing dependencies give a nonzero error. Only an explicitly authorized setup
such as `make.sh fix` may install packages. Non-PDF text/JSON parsing needs only
the Python standard library; inspecting/filling PDF forms needs `pypdf`, never
Chromium. The cover/body route checks its actual renderer once per unchanged
session, not once per parser or field operation.

## Load only used content features

For this pipeline's CREATE/REFORMAT, read the
[block contract](references/implementation/content.md#block-contract), then only
sections for used features. It is the single schema/renderer-limit authority.
[VALIDATE](references/operations/validate.md) is the single acceptance checklist;
no second presentation/content checklist is required.

| Required feature | Direct reference |
|---|---|
| Prose, headings, lists, tables, breaks, spacing | [Common blocks and tables](references/implementation/content.md#common-blocks-and-tables) |
| Equations, labels, mathtext limits | [Mathematics](references/implementation/content.md#mathematics) |
| Charts and datasets | [Charts](references/implementation/content.md#charts) |
| Images, figures, captions, shared numbering | [Figures and captions](references/implementation/content.md#figures-and-captions) |
| Citations/references | [Bibliography](references/implementation/content.md#bibliography) |
| Code whitespace/language labels | [Code](references/implementation/content.md#code) |
| Nodes, arrows, back-edges | [Flowcharts](references/implementation/content.md#flowcharts) |

A successful parser, check or merge is not a source comparison or actual-page QA.
Disclose checks that were unavailable or not run.
