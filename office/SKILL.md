---
name: office
description: Analyze source material and create, read, edit, and validate Word documents, PDF files, and Excel spreadsheets. Use for reports, research comparisons, operating reviews, proposals and plans delivered in DOCX, PDF or XLSX. Includes Chinese government-style documents, named academic papers, thesis templates and business/editorial formatting in Word; research and technical PDF features; and financial models, budgets, forecasts and scenarios in Excel. Also use for spreadsheet formulas, PDF forms, document formatting or conversion.
license: MIT
---

# Office files

## Content guidance

Route by the user's requested operation, not analytical statements in the source
being edited. For extraction, translation, consolidation of established findings,
formatting, conversion or a limited edit, use the format route directly and skip
the analysis guide. Existing recommendations or numbers do not authorize a new
investigation.

When asked to explain results, evaluate evidence, recommend an option or establish
a plan's feasibility, read [Analysis](references/analysis.md) before drafting the
findings. Use it even for a short memo or a task with supplied sources. It covers
the analytical work; the format routes below cover the file. Read only the
references needed for the actual work.

When creating or substantially rewriting reader-facing prose, read
[Writing](references/writing.md) for structure, headings and explanatory prose.
This includes workbook narratives and applies independently of whether new
analysis is needed. Preserve the scope of limited edits and supplied templates.

## File workflow

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

## Content review

Check the exact saved deliverable against the applicable content guidance:
[analytical review](references/analysis.md#accept-the-findings-then-check-the-saved-document)
for conclusions and supporting work, and
[editorial review](references/writing.md#review-the-completed-text) for newly
authored or substantially rewritten prose. For limited edits, check the affected
content and necessary context. Use the selected format's validation for file
structure, rendering and application behavior; it does not establish content quality.

## Package map

The top-level `office` entry owns shared content routing and review, with its
guides in `references/`. Each format's `SKILL.md` owns setup, presentation profiles
and file operations, with references grouped by responsibility:

- `common/`: reusable data/presentation conventions.
- `domains/`: applicable business or named-format requirements.
- `operations/`: the authorized create/read/edit/fill/validate workflow.
- `implementation/`: library, package, schema and environment details.

Shared guides are linked above; format-specific guides are linked from their
format entry. Load only those needed. Scripts, templates and assets retain their
existing paths.
A format route does not authorize unrelated edits, redesign or extra deliverables.

The implementations are adapted from MiniMax's MIT-licensed skills. Original
licenses and pinned-source attribution are preserved in each subdirectory's
`LICENSE` and `UPSTREAM.md`.
