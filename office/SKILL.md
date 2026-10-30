---
name: office
description: Create, read, edit, and validate Word documents, PDF files, and Excel spreadsheets. Use for DOCX, PDF, XLSX, spreadsheet formulas, PDF forms, and document formatting or conversion.
license: MIT
---

# Office files

Use the format-specific skill below. Read only the selected route and the
references needed for the task.

Set `OFFICE_DIR` to the absolute directory containing this file. Set `SKILL_DIR`
to the selected subdirectory before running its examples; it is a shell variable,
not a literal directory named `SKILL_DIR`. Do not assume the current working
directory is the skill directory.

| Output or task | Read | Set |
| --- | --- | --- |
| Word creation, editing, formatting, or DOCX-to-PDF | [docx/SKILL.md](docx/SKILL.md) | `SKILL_DIR="$OFFICE_DIR/docx"` |
| Standalone PDF creation, reading, forms, or reformatting | [pdf/SKILL.md](pdf/SKILL.md) | `SKILL_DIR="$OFFICE_DIR/pdf"` |
| Excel creation, reading, editing, formulas, or validation | [xlsx/SKILL.md](xlsx/SKILL.md) | `SKILL_DIR="$OFFICE_DIR/xlsx"` |

Honor the user's format and supplied template. The selected template's styles
take precedence over generic typography defaults. For a DOCX and its PDF
companion, author once and render the DOCX so content and layout remain aligned.
Use each route's setup and validation commands; reuse a working environment
within the session.

For DOCX and PDF, deliver after content and structural checks.

The implementations are adapted from MiniMax's MIT-licensed skills. Original
licenses and pinned-source attribution are preserved in each subdirectory's
`LICENSE` and `UPSTREAM.md`.
