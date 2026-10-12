---
name: office-files
description: Create or edit Word documents, Excel spreadsheets, and PDFs, including uploaded files.
---

# Office files

## Before starting

- User requirements and supplied templates take priority. Start narrow edits from the original file and preserve its structure and design. For new Word/PDF documents without a specified design, read [style.md](style.md) and apply its parameters in the generation code.
- Check the required libraries, fonts, and renderers together. Reuse installed dependencies and install only missing ones. For a complex new layout, first try the widest table and largest chart.

## Generate

Prefer native authoring: create files directly with tools that support the target format and language.

- **Word**: use `python-docx` or `docx` to create editable paragraphs, headings, lists, and tables.
- **PDF**: lay out and export pages with ReportLab or Typst. Markdown conversion is optional; use DOCX-to-PDF for Word layout checks or a requested matching export.
- **Excel**: write cells and formulas with `openpyxl`. When results must already be displayed in the file, recalculate with a compatible calculation engine; do not replace formulas with static values.

For paired Word/PDF files, share content, calculated values, and style parameters. Compute totals, ratios, and scores in code instead of entering them separately in each file.

## Avoid known problems

- Use automatic or minimum line spacing for Word paragraphs containing charts; do not inherit fixed body line spacing. Let table row heights grow with their content.
- Set fonts and heading styles explicitly; remove conflicting theme fonts, default title borders, and table borders.
- Draw headers and footers in one stage only. Do not overlay existing headers or page numbers again during PDF post-processing.

## Check and deliver

- Check final content, numbers, actual fonts and sizes, and every page for overflow, clipping, overlap, and pagination. For Word, inspect pages rendered from the actual DOCX. Check independently generated PDFs separately. If the PDF is a direct export of the final DOCX, reuse those pages without repeating the export and rasterization.
- For Excel, check key formulas and calculated results. Combine fixes from each review before regenerating, and resolve known defects before delivery. Mark missing recalculation, rendering, or other checks as unverified, not passed.
- Deliver the requested files; include editable DOCX with final PDFs unless the user requests otherwise. Briefly state the renderer used, checks performed, and unverified items. Provide detailed QA files only when needed.
