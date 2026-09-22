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
| New prose report in Word, PDF, or both | [Runnable document starter](references/new-document.md) |
| Edit Word, fill a Word template, or use native Word features | [Word workflow](references/word-authoring.md) |
| Edit PDF or author a PDF with a specified native engine | [PDF workflow](references/pdf-authoring.md) |
| Create or edit Excel (`.xlsx`) | [Excel workflow](references/excel-authoring.md) |

For multiple independent deliverables, follow each relevant page. If the user
supplies a template package, follow that package's entry point.

Use the starter's working defaults before writing custom authoring code. Adapt
content to the requested sections, decisions and evidence. Do not expand a short
report into extra scenarios, appendices or financial models without a task need.
Do not add quantitative forecasts, counterfactual decompositions, payback models
or numerical operating thresholds unless the user asks for them. If an essential
decision lacks evidence, state the missing input and how to validate it instead
of inventing a diagnostic rule or expanding the analysis. A next-steps section
can give concrete actions and owners without a speculative financial model.
Let complete content paginate naturally unless the user specifies a page limit.
For a time target, keep that scope and use the one-command setup/preparation
routes below; never meet a deadline by dropping requested content or checks.
When simulated data is requested, generate it once and describe its actual results.

Resolve quick-check findings while drafting. Once content is stable, verify the
final candidate, review its page gallery, and run acceptance before delivery.
Repair observed defects together where possible; do not explore alternative
styling after the candidate passes. Keep sources and check records for revisions.
Immediately after uploading the accepted file, send a short assistant message
containing the returned download URL. Then prepare any requested retrospective
using existing logs and timestamps.
