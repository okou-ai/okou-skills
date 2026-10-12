---
name: office-files
description: Create or edit Word documents, Excel spreadsheets, and PDFs, including uploaded files.
---

# Office files

User requirements and supplied templates take priority. Start narrow edits from the original file and preserve its structure and design. For new Word/PDF documents without a specified design, read [style.md](style.md).

## Author natively

Prefer native authoring: create files directly with tools that support the target format and language.

- **Word**: use `python-docx` or `docx` to create editable paragraphs, headings, lists, and tables.
- **PDF**: lay out and export pages with ReportLab or Typst. Markdown conversion is optional; use DOCX-to-PDF for Word layout checks or a requested matching export.
- **Excel**: write cells and formulas with `openpyxl`. When results must already be displayed in the file, recalculate with a compatible calculation engine; do not replace formulas with static values.

## Execution constraints

1. **Check the environment once.** Check libraries, fonts, and renderers together; reuse installed dependencies and install only missing ones. For Word, verify that the renderer can load a minimal DOCX; command availability alone is insufficient. Record tool versions during this check, not again at delivery.

2. **Apply the style in the first build.** Set fonts, heading styles, sizes, spacing, and text/table widths explicitly in code. Remove conflicting theme fonts and default title/table borders. Give image paragraphs automatic or minimum line spacing and let table rows grow. Draw headers and footers in one stage only. Paired Word/PDF files must share content, calculated values, and style parameters; compute totals, ratios, and scores in code.

3. **Trial complex layouts before full generation.** Try the widest table and largest chart with real content at final sizes. Adjust columns, split tables, or add pages when needed; preserve the specified type sizes.

4. **Fix issues in batches.** Review the relevant pages, collect the issues, then edit and regenerate together. If two successive small adjustments fail to resolve the same issue, change the layout structure instead of continuing to tweak individual values.

5. **Retry only after a relevant change.** Diagnose whether a failed Word conversion comes from the file or the environment. Do not repeat the same failed command while the file, environment, and parameters remain unchanged.

6. **Verify the final artifacts.** During revisions, inspect affected pages, including downstream pages when pagination changes. For final delivery, inspect every page rendered from the actual DOCX and check independently generated PDFs separately. Check content, numbers, actual fonts and sizes, figures, clipping, overlap, overflow, pagination, and page references. Reuse unchanged renders, including a matching PDF export of the final DOCX. For Excel, check key formulas and calculated results. Resolve known defects; mark unavailable checks as unverified. A revision-count target never replaces acceptance checks.

7. **Capture records as work happens.** Record generation start/end times within generation commands and note revision reasons during edits. Leave unmeasured stages unknown. Include detailed records only for requested experiments or QA; ordinary delivery needs brief check results, not a separate report.

8. **Deliver in one batch.** After checks, upload the requested final files together; include editable DOCX with final PDFs unless the user requests otherwise. Briefly state the renderer, checks, and unverified items. Put any delivery timestamp in the reply; do not edit and re-upload a record solely to add that timestamp.
