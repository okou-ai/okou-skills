---
name: office-files
description: Generate or edit docx, xlsx and PDF deliverables — Word documents, spreadsheets, reports — including editing a file the user uploaded.
---

# Office files

Create or edit the requested document or spreadsheet. This skill provides
business guidance, applicable style defaults, and final-result checks. Choose
suitable tools to produce the requested formats directly; no authoring library,
intermediate format, installation sequence, or conversion chain is required.

## Find business guidance

For a new business document or analysis that needs a task-specific structure,
use `business-skill-index` when available: route by the requested work product,
read the selected source and matching template, and follow its application and
final-content checks. The index is optional; its absence does not block work.
Skip discovery for conversion, styling, or narrow edits to an established
document.

## Apply the relevant style

For a new English report without a user-specified design, read and apply
[the report style](style.md). It defines typography, spacing, tables, charts,
and pagination independently of the production tools. Apply it to an existing
English report when the user requests this style. Explicit user requirements
and supplied templates take priority.

For other languages and document types, choose a suitable style for the task,
script, and audience. Preserve an existing file's design during narrow edits or
conversion unless the user requests a redesign. Business references guide the
content; their production recipes do not bind the implementation.

## Deliver a usable result

- Honor the requested file format, supplied facts, and any explicit template or
  branding requirements. For edits, preserve the user's document and unrelated
  content and formatting.
- Verify the final file against the task and the applicable skill, including
  content, numbers, readability, and whether the file can be opened. Record
  relevant checks that could not be performed as unverified.
- Inspect every final document page, or the relevant worksheet and print views,
  at a readable scale. Correct clipping, overlapping text, font substitution,
  isolated headings, broken table continuations, and separated figures/captions.
- Keep Word text and tables editable. When delivering multiple formats, check
  that their content, data, and visual hierarchy agree; generating a PDF does
  not require converting it from Word.
- Keep spreadsheet inputs editable and calculations recalculable when the task
  requires them; check the delivered file's results and narrative agree.
- Share the requested files. For final prose delivered as PDF, also provide an
  editable Word source unless the user requests otherwise.
