---
name: office
description: Create, read, edit, and validate Word documents, PDF files, and Excel spreadsheets. Includes Chinese government-style documents, named academic papers, thesis templates and business/editorial formatting in Word; research and technical PDF features; and financial models, budgets, forecasts and scenarios in Excel. Use for DOCX, PDF, XLSX, spreadsheet formulas, PDF forms, document formatting or conversion.
license: MIT
---

# Office files

Use the format-specific skill below. Read only the selected route and the
references needed for the task.

## Choose the content route

- **Direct drafting:** For a straightforward brief, summary or memo that condenses
  supplied material or established conclusions, use the format route directly.
  Also skip deep research for translation, extraction, conversion, styling and
  narrow edits that require no new analysis.
- **Deep research:** When the user requests in-depth research, or the task needs
  substantial investigation or analysis to establish new conclusions, read
  [deep-research/SKILL.md](deep-research/SKILL.md) before researching or drafting.

Choose by the work required, not the document's label, length or file format.
A short brief can require research, but creating a brief does not itself trigger
this route. Research must preserve the requested output scope and length; it
must not add an unrequested research report. Both routes retain the selected
format's production and validation requirements.

## Choose the file format

Set `OFFICE_DIR` to the absolute directory containing this file. Set `SKILL_DIR`
to the selected subdirectory before running its examples; it is a shell variable,
not a literal directory named `SKILL_DIR`. Do not assume the current working
directory is the skill directory.

| Output or task | Read | Set |
| --- | --- | --- |
| Word creation, editing, formatting, or DOCX-to-PDF, including government-style, named academic, thesis-template and business/editorial documents | [docx/SKILL.md](docx/SKILL.md) — select the applicable presentation profile as well as the operation | `SKILL_DIR="$OFFICE_DIR/docx"` |
| Standalone PDF creation, form inspection/filling, or reformatting, including research/technical content | [pdf/SKILL.md](pdf/SKILL.md) — distinguish named manuscript requirements from visual presets | `SKILL_DIR="$OFFICE_DIR/pdf"` |
| Excel creation, reading, editing, formulas, or validation, including financial budgets and forecasts | [xlsx/SKILL.md](xlsx/SKILL.md) — select its common and business-scenario layers before authoring | `SKILL_DIR="$OFFICE_DIR/xlsx"` |

Honor the user's format and supplied template. The selected template's styles
take precedence over generic typography defaults. For a DOCX and its PDF
companion, author once and render the DOCX so content and layout remain aligned.
Use each route's setup and validation commands; reuse a working environment
within the session. Presentation profiles are formatting guidance, not substantive
research, policy, medical or legal expertise. Package checks do not certify
compliance with a publication or government standard.

## Package map

The top-level `office` package is the single discovery entry. The optional
`deep-research/` content route is loaded only under the conditions above; it is
not a separate default skill or a fourth file format. Each format's `SKILL.md`
routes to references grouped by responsibility:

- `common/`: reusable data/presentation conventions.
- `domains/`: applicable business or named-format requirements.
- `operations/`: the authorized create/read/edit/fill/validate workflow.
- `implementation/`: library, package, schema and environment details.

Format-specific reference guides are linked directly from the relevant format
entry; load only those needed. Scripts, templates and assets retain their
existing paths. A format route does not authorize unrelated edits, redesign or
extra deliverables.

The implementations are adapted from MiniMax's MIT-licensed skills. Original
licenses and pinned-source attribution are preserved in each subdirectory's
`LICENSE` and `UPSTREAM.md`.
