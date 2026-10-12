---
name: office-files
description: Create or edit Word documents, Excel spreadsheets, and PDFs, including uploaded files.
---

# Office files

For reports requiring research, data interpretation, or calculations, use the
`analysis-methods` skill when available before authoring. Reuse completed
analysis; formatting-only edits do not need a new analysis.

Honor user requirements and supplied templates. Start edits from the original file and preserve unrelated content and formatting.

## Generate

For new Word/PDF documents without a specified design, read [style.md](style.md) and inherit the blank assets from the first build. They define typography, not a report outline or palette.

| Format | Native starting point |
| --- | --- |
| Word | Open [blank.docx](assets/blank.docx) with `python-docx`; use named styles and editable paragraphs/tables. |
| PDF | Copy [blank.typ](assets/blank.typ), append content, and compile directly with Typst. |
| Excel | Use `openpyxl`; preserve formulas and recalculate with a compatible engine when displayed results are needed. |

Use the [native tools guide](references/native-authoring.md) for setup, shared Word/PDF authoring, and cached review. Check capabilities once, reuse available dependencies, and install only missing ones. Share content and calculations across formats. Trial complex tables/charts at final sizes before full generation; preserve the style's type sizes.

Other native engines may follow the same style. Markdown conversion is optional; DOCX-to-PDF serves actual Word inspection or a requested matching export.

## Check

- Run structural style checks during generation. Inspect every final page rendered from the actual DOCX and independently authored PDF separately: facts, numbers, rendered fonts/sizes, tables, figures, clipping, overlap, pagination, and page references. Check Excel formulas and calculated results.
- Batch independent operations and corrections; reuse unchanged renders. Recheck affected pages and downstream reflow. After two ineffective small adjustments, change the layout structure. Retry failed commands only after a relevant file, environment, or parameter change.
- Resolve known defects and label unavailable checks as unverified. Claim Okou/Microsoft preview compatibility only after inspecting that viewer, including mixed-script text and selection/copy.

## Deliver

Upload the final files once after checks, choosing only the formats needed by the user. Keep previews, sources, logs, and QA notes local unless requested or needed to use the result. Briefly report checks and limitations.

For experiments, record command timings and revision reasons locally; leave unmeasured stages unknown. Summarize useful measurements in the reply without adding a separate deliverable.
