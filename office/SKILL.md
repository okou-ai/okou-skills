---
name: office
description: >
  Create, edit, format, convert, or validate Word documents, PDFs, and Excel
  workbooks. Content-only reading, extraction, summaries, and analysis use a
  reader directly, without authoring setup or presentation workflows.
license: MIT
---

# Office files

Select the operation before the format; load only the references it needs.

**Content-only reading/analysis:** read only the needed parts, sheets or ranges.
Skip authoring setup, style profiles and output validation. Inspect structure or
recalculate an authorized copy only when needed for the result; never modify the
source. Bundled lightweight readers are `docx/scripts/docx_preview.sh` and
`xlsx/scripts/xlsx_reader.py`, relative to this directory. Use an available PDF
reader for content, not the cover/browser pipeline.

**Create, edit, convert or inspect file features:** select one route:

- [Word](docx/SKILL.md): DOCX, templates and DOCX-to-PDF.
- [PDF](pdf/SKILL.md): standalone PDF creation, redesign and form fields.
- [Excel](xlsx/SKILL.md): XLSX authoring, formulas and formatting.

## Analytical results

- Answer within the requested scope; clarify only material ambiguities.
- Trace material conclusions to permitted sources and locations. Distinguish
  observations, estimates, inferences and proposals; retain units, populations, periods
  and metric definitions.
- Verify calculations or assumptions that could change the conclusion; state
  affected limitations beside the result.
- Add domain guidance only for a concrete method, structure or correctness gap.
  Reuse verified inputs/checks; do not restart discovery, full-data profiling,
  staged research or a separate report merely because a file is involved.

## File delivery

Honor the supplied template and requested scope/formats. Use conventional
headings and domain terminology; remove drafting labels and unsupported promotional phrasing
in the final content review, not a separate prose pass. For Word and PDF together,
render PDF from the authored DOCX. Check affected features; setup or static
validation alone does not prove correct content, calculation or rendering.

The format implementations are adapted from MiniMax's MIT-licensed skills.
Each format directory retains its `LICENSE` and `UPSTREAM.md`.
