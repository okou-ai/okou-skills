---
name: office-files
description: Create or edit Word documents, Excel spreadsheets, and PDFs, including uploaded files.
---

# Office files

User requirements and supplied templates take priority. Start narrow edits from the original file and preserve its structure and design. For new Word/PDF documents without a specified design, read [style.md](style.md).

## Author natively

Prefer native authoring: create files directly with tools that support the target format and language.

Use the reusable tools in [references/native-authoring.md](references/native-authoring.md) for on-demand setup, ordinary paired reports, and cached checks. They add no report outline or palette. [scripts/office_env.py](scripts/office_env.py) reuses available dependencies and installs only those missing for the current task.

- **Word**: for a new document, open [assets/blank.docx](assets/blank.docx) with `python-docx.Document(...)` and save a new file. Use its named styles: `Title`, `Heading 1`–`Heading 3`, `Normal`, `List Bullet`, `List Number`, `Table Text`, `Table Header`, `Table Title`, `Figure`, `Caption`, and `Source`. Keep paragraphs and tables editable.
- **PDF**: copy [assets/blank.typ](assets/blank.typ), append content, and compile with `typst compile report.typ report.pdf` or Python's `typst.compile('report.typ', output='report.pdf')`. Use `#doc-title[...]`, headings, tables, and figure captions to inherit typography. Other native engines may use the same baseline. Markdown conversion is optional; DOCX-to-PDF serves Word layout checks or a requested matching export.
- **Excel**: write cells and formulas with `openpyxl`. When results must already be displayed in the file, recalculate with a compatible calculation engine; do not replace formulas with static values.

## Execution constraints

1. **Check the environment once.** From your working directory, run `python3 <skill-dir>/scripts/office_env.py --formats docx pdf --install-missing`, selecting only needed formats and adding `--charts` when used. Reuse its returned Python path and capability result. It checks libraries/fonts together and verifies actual Writer import; command availability alone is insufficient. Do not repeat installations, font searches, or failed probes without a relevant change.

2. **Reuse content and style from the first build.** Use shared content/data and the blank assets; compute totals, ratios, and scores once. For ordinary paired reports, `scripts/office.py` supplies native Word/PDF methods without rewriting two generators. Apply table/figure styles explicitly when authoring directly. Adapt script fonts as in `style.md`, remove conflicting overrides, let image paragraphs and rows grow, and draw headers/footers once. Run the baseline structural check during generation so size, alignment, header, and image-spacing defects are caught before visual review.

3. **Trial complex layouts before full generation.** Try the widest table and largest chart with real content at final sizes. Adjust columns, split tables, or add pages when needed; preserve the specified type sizes.

4. **Batch work and corrections.** Combine independent reads, calculations, and checks into as few tool calls as practical. Use `scripts/review.py` to render requested formats together and reuse unchanged results. Collect page issues, then edit and regenerate together. If two successive small adjustments fail to resolve the same issue, change the layout structure.

5. **Retry only after a relevant change.** Diagnose whether a failed Word conversion comes from the file or the environment. Do not repeat the same failed command while the file, environment, and parameters remain unchanged.

6. **Verify the final artifacts.** During revisions, inspect affected pages, including downstream pages when pagination changes. For final delivery, inspect every page rendered from the actual DOCX and check independently generated PDFs separately. Check content, numbers, actual fonts and sizes, figures, clipping, overlap, overflow, pagination, and page references. Reuse unchanged renders, including a matching PDF export of the final DOCX. For Excel, check key formulas and calculated results. Resolve known defects; mark unavailable checks as unverified. A revision-count target never replaces acceptance checks.

7. **Keep diagnostics internal.** For requested experiments or QA, record generation start/end times within commands and revision reasons during edits. Leave unmeasured stages unknown. Keep detailed records locally and summarize useful results in the reply; an experiment does not require a separate QA or timing deliverable.

8. **Deliver only what the user needs.** Honor requested formats; otherwise choose the minimum set for reading, editing, or importing. Upload final files once after checks. Keep preview images, QA notes, logs, and build sources internal unless explicitly requested or needed to use the result. Briefly state checks and unverified items in the reply. Put any delivery timestamp there, without creating or re-uploading a record for it.
