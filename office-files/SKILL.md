---
name: office-files
description: Create or edit Word, PDF and Excel files by following the workflow for the requested format.
---

# Office files

Read only the route needed for this task. Run the documented scripts without
reading their implementation; inspect source when diagnosing an actual failure
or implementing a feature outside the documented interface.

| Requested task | Page |
| --- | --- |
| New prose in Word, PDF, or both | [Runnable document starter](references/new-document.md) |
| Edit Word, fill a Word template, or use native Word features | [Word workflow](references/word-authoring.md) |
| Edit PDF or author a PDF with a specified native engine | [PDF workflow](references/pdf-authoring.md) |
| Create or edit Excel (`.xlsx`) | [Excel workflow](references/excel-authoring.md) |

For multiple independent deliverables, follow each relevant page. If the user
supplies a template package, follow that package's entry point.

Use the starter's working defaults before custom authoring code. Write for the
requested purpose, reader and scope. Choose headings from the task; the file
format does not require a report, calculations, charts or a separate planning
document. Add tools and deeper checks only for work the content actually needs.
Preserve supplied facts and distinguish assumptions from evidence. For a
decision that lacks evidence, state what to verify next. Let complete content
paginate naturally unless the user specifies a page limit. A time target never
permits dropping requested content or applicable checks.

Resolve quick-check findings while drafting. Once content is stable, verify the
final candidate, review its page gallery, and run acceptance before delivery.
Repair observed defects together where possible; do not explore alternative
styling after the candidate passes. Keep sources and check records for revisions.
Immediately after uploading the accepted file, send a short assistant message
containing the returned download URL. Then prepare any requested retrospective
using existing logs and timestamps.
