---
name: office-files
description: Create or edit Word documents, Excel spreadsheets, and PDFs, including uploaded files.
---

# Office files

User requirements and supplied templates take priority. Start narrow edits from the original file and preserve its structure and design. For new Word/PDF documents without a specified design, read [style.md](style.md).

## Author natively

Prefer native authoring: create files directly with tools that support the target format and language.

- **Word**: for a new document, open [assets/blank.docx](assets/blank.docx) with `python-docx.Document(...)` and save a new file. Use its named styles: `Title`, `Heading 1`–`Heading 3`, `Normal`, `List Bullet`, `List Number`, `Table Text`, `Table Header`, `Table Title`, `Figure`, `Caption`, and `Source`. Keep paragraphs and tables editable.
- **PDF**: copy [assets/blank.typ](assets/blank.typ), append content, and compile with `typst compile report.typ report.pdf` or Python's `typst.compile('report.typ', output='report.pdf')`. Use `#doc-title[...]`, headings, tables, and figure captions to inherit typography. Other native engines may use the same baseline. Markdown conversion is optional; DOCX-to-PDF serves Word layout checks or a requested matching export.
- **Excel**: write cells and formulas with `openpyxl`. When results must already be displayed in the file, recalculate with a compatible calculation engine; do not replace formulas with static values.

## Execution constraints

1. **Check the environment once.** Check libraries, fonts, and renderers together; reuse installed dependencies and install only missing ones. For Word, verify that the renderer can load a minimal DOCX; command availability alone is insufficient. Record tool versions during this check, not again at delivery.

2. **Reuse the style from the first build.** Inherit the blank assets' typography and page settings; apply the table and figure styles explicitly. They contain no report outline, palette, or decoration. Adapt fonts to the language as described in `style.md`; avoid conflicting theme or run overrides. Keep image paragraphs at automatic or minimum line spacing and let rows grow. Draw any headers/footers once. Paired Word/PDF files share content, calculations, and the baseline; compute totals, ratios, and scores in code.

3. **Trial complex layouts before full generation.** Try the widest table and largest chart with real content at final sizes. Adjust columns, split tables, or add pages when needed; preserve the specified type sizes.

4. **Fix issues in batches.** Review the relevant pages, collect the issues, then edit and regenerate together. If two successive small adjustments fail to resolve the same issue, change the layout structure instead of continuing to tweak individual values.

5. **Retry only after a relevant change.** Diagnose whether a failed Word conversion comes from the file or the environment. Do not repeat the same failed command while the file, environment, and parameters remain unchanged.

6. **Verify the final artifacts.** During revisions, inspect affected pages, including downstream pages when pagination changes. For final delivery, inspect every page rendered from the actual DOCX and check independently generated PDFs separately. Check content, numbers, actual fonts and sizes, figures, clipping, overlap, overflow, pagination, and page references. Reuse unchanged renders, including a matching PDF export of the final DOCX. For Excel, check key formulas and calculated results. Resolve known defects; mark unavailable checks as unverified. A revision-count target never replaces acceptance checks.

7. **Keep diagnostics internal.** For requested experiments or QA, record generation start/end times within commands and revision reasons during edits. Leave unmeasured stages unknown. Keep detailed records locally and summarize useful results in the reply; an experiment does not require a separate QA or timing deliverable.

8. **Deliver only what the user needs.** Honor requested formats; otherwise choose the minimum set for reading, editing, or importing. Upload final files once after checks. Keep preview images, QA notes, logs, and build sources internal unless explicitly requested or needed to use the result. Briefly state checks and unverified items in the reply. Put any delivery timestamp there, without creating or re-uploading a record for it.
