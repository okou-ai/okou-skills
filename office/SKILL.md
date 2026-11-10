---
name: office
description: Create, read, edit, and validate Word documents, PDF files, and Excel spreadsheets, including research and substantive analysis for reports, assessments and plans delivered in these formats. Includes Chinese government-style documents, named academic papers, thesis templates and business/editorial formatting in Word; research and technical PDF features; and financial models, budgets, forecasts and scenarios in Excel. Use for DOCX, PDF, XLSX, spreadsheet formulas, PDF forms, document formatting or conversion.
license: MIT
---

# Office files

Read the guide for the requested file format and the references relevant to the
task. Apply the research guidance below when the document requires it.

## Determine the analytical work

Read [deep-research/SKILL.md](deep-research/SKILL.md) when the user requests an
in-depth investigation or substantial analysis. Also read it when answering the
question requires evaluating evidence, explaining results, comparing alternatives
or establishing feasibility beyond reporting supplied facts. Read it before
developing the analysis, regardless of the file format or requested length.

For briefs, summaries and memos that only consolidate supplied material or
established findings, follow the DOCX, PDF or XLSX instructions below to prepare
and validate the file. Do not load the research guide for these tasks or for
translation, extraction, formatting, conversion and limited edits that require
no additional analysis.

Decide from the work needed to answer the question, not the document's title or
whether sources were supplied. If reading the material reveals a need for
substantial analysis to answer that question, read the guide before continuing.
A short brief may require investigation; apply the research guidance while
retaining the requested brief's scope and length. Do not expand a consolidation
or editing task into an investigation the user did not request.

## Prepare the requested file

Set `OFFICE_DIR` to the absolute directory containing this file. Set `SKILL_DIR`
to the selected subdirectory before running its examples; it is a shell variable,
not a literal directory named `SKILL_DIR`. Do not assume the current working
directory is the skill directory.

| Output or task | Read | Set |
| --- | --- | --- |
| Word creation, editing, formatting, or DOCX-to-PDF, including government-style, named academic, thesis-template and business/editorial documents | [docx/SKILL.md](docx/SKILL.md) — select the applicable presentation profile as well as the operation | `SKILL_DIR="$OFFICE_DIR/docx"` |
| Standalone PDF creation, form inspection/filling, or reformatting, including research/technical content | [pdf/SKILL.md](pdf/SKILL.md) — distinguish named manuscript requirements from visual presets | `SKILL_DIR="$OFFICE_DIR/pdf"` |
| Excel creation, reading, editing, formulas, or validation, including financial budgets and forecasts | [xlsx/SKILL.md](xlsx/SKILL.md) — read its general instructions and applicable business-scenario guidance before authoring | `SKILL_DIR="$OFFICE_DIR/xlsx"` |

Honor the user's format and supplied template. The selected template's styles
take precedence over generic typography defaults. For a DOCX and its PDF
companion, author once and render the DOCX so content and layout remain aligned.
Complete the setup and validation steps in the selected format guide; reuse a
working environment within the session. Presentation profiles describe document
formatting; they do not provide research, policy, medical or legal expertise.
Package checks do not certify compliance with a publication or government
standard.

## Package map

Start with `office/SKILL.md`. The `deep-research/` guide covers research and
analytical methods. The `docx/`, `pdf/` and `xlsx/` guides cover file preparation
and validation. Their references are organized by responsibility:

- `common/`: reusable data/presentation conventions.
- `domains/`: applicable business or named-format requirements.
- `operations/`: the authorized create/read/edit/fill/validate workflow.
- `implementation/`: library, package, schema and environment details.

Each format guide links to its supporting references; read only the relevant
ones. Scripts, templates and assets retain their existing paths. Using a format
guide does not authorize unrelated edits, redesign or extra deliverables.

The implementations are adapted from MiniMax's MIT-licensed skills. Original
licenses and pinned-source attribution are preserved in each subdirectory's
`LICENSE` and `UPSTREAM.md`.
