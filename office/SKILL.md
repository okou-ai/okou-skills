---
name: office
description: Create, edit, format, convert, or validate DOCX, PDF and XLSX files. Use when the task requires producing or changing an Office file, applying a template, repairing formulas or file structure, or inspecting layout, editability, recalculation, form fields or saved-file usability. Reading, summarizing, translating or analyzing document contents alone does not require this skill.
license: MIT
---

# Office files

## Choose the operation

An Office file supplied as source material does not by itself require this skill.
Choose by the requested work, not the file extension or the presence of analytical
statements in the input. The sections below are conditional guidance, not a
sequence to execute for every Office task.

| Requested work | Applicable workflow |
| --- | --- |
| Read, extract, summarize, translate or analyze contents without producing or changing an Office file | Use suitable reading tools directly. A bundled reader may be used when useful without adopting the authoring workflow. |
| Inspect layout, structure, formulas, form fields or editability | Use the relevant format's read-only inspection tools and check the requested properties. |
| Edit, fill, format, convert or assemble supplied content into a file | Use the selected file operation. Preserve content and presentation outside the authorized change; do not add new analysis or rewrite supplied text merely because a file is being produced. |
| Write or substantially rewrite content for an Office deliverable | Use the selected file operation and the writing guidance. Use the analysis guidance only when the task requires developing explanations, comparisons, recommendations or feasibility judgments. |

Honor the user's audience, genre, language, sources, scope, length and template.
Use only authorized factual sources. When a material input is missing, ask if
clarification is permitted; otherwise complete the supported work and qualify
the affected conclusion. Preserve required headings and source field names.

## File routes

Set `OFFICE_DIR` to the absolute directory containing this file, and `SKILL_DIR`
to the selected format directory below. Command paths are relative to that
directory, not the task's working directory.

| Format | Read | Set |
| --- | --- | --- |
| Word documents and DOCX-to-PDF | [docx/SKILL.md](docx/SKILL.md) | `SKILL_DIR="$OFFICE_DIR/docx"` |
| Standalone PDFs and PDF forms | [pdf/SKILL.md](pdf/SKILL.md) | `SKILL_DIR="$OFFICE_DIR/pdf"` |
| Excel workbooks | [xlsx/SKILL.md](xlsx/SKILL.md) | `SKILL_DIR="$OFFICE_DIR/xlsx"` |

Use only the selected operation's setup and references; reuse a working
environment within the session. Template requirements take precedence over
generic presentation defaults. For a requested Word/PDF pair, author the DOCX
once and render it so content and layout remain aligned.

## Develop the analysis

Use when authoring analytical content, not for routine file operations or inspection.

Identify what the reader needs to understand or decide. Read the relevant source
content and calculate the requested results before organizing findings around a
template. Source extraction and environment checks can start immediately. Keep
useful source locations, executed calculations and unresolved material questions
in existing task notes or scripts; these are working materials, not additional
deliverables.

After the initial results, pursue the unresolved issue most likely to change
the explanation, recommendation or feasibility judgment. Perform the relevant
operation, use its result in the judgment, then reassess. Select operations as
needed rather than running a fixed checklist on every task.

| Unresolved issue | Work to perform |
| --- | --- |
| A change is described but not explained | Reconcile it to meaningful components, segments or offsets. Separate scale, rate and mix only where the data support the stated baseline. |
| A cause is proposed | Check its mechanism and supporting evidence, a credible competing explanation and the observation that would distinguish them. |
| A plan appears to meet its target | Rebuild resource use from its activities, fixed and variable costs, capacity, dependencies and deadlines. Check the binding constraint. |
| An option is recommended | Compare the credible alternative using consistent assumptions; explain the benefit or coverage forgone, cost, risk and conditions of the choice. |
| An uncertain input could reverse the conclusion | Calculate a relevant threshold or sensitivity and state when the judgment changes. |
| Source results appear inconsistent | Check result identity, configuration, population, period, units, metric and data split in the original context, including table headings and notes. |

Check the claims whose failure would change the answer. Execute material
arithmetic with suitable tools and reconcile it independently to actual source
inputs or controls. Check signs, denominators, types, missing values and range
coverage. A citation's existence does not establish that its source supports
the claim; preserve source-specific values when an apparent conflict remains
unresolved.

Distinguish arithmetic contributions, associations, source-reported explanations
and established causes. Missing causal evidence does not prevent completing
supported calculations or comparisons; an arithmetic residual does not identify
its business cause.

For a changed scenario, state what changes and what stays constant. Recompute
dependent results from their components, including fixed and variable costs, and
check the revised resource constraints together. Unknown capacity or unit
economics makes the result conditional, not a guarantee or a proven minimum.

Use available specialist guidance when needed: `flux-analysis` for financial
decomposition, `analysis-qa` for numerical checks, or `business-skill-index` for
a task-matched method. Scientific-paper comparison and interview synthesis need
different methods. These resources do not authorize new sources or extra scope.

Finish when the reader can use the answer without completing essential analysis
left implicit. Resolve material questions that the permitted evidence can answer;
otherwise revise the recommendation, confidence or conditions. Do not substitute
a list of gaps or future studies for work possible now, or add sections solely
to make the report longer.

## Write the document

Use for newly authored or rewritten passages. For a local wording change, preserve
the surrounding voice and structure rather than applying a document-wide style.

Choose language for the situation, purpose and recipient: their subject knowledge,
relationship to the author, and what they need to understand or do. Professional
expression may be conversational, explanatory, technical or formal. Accuracy,
clarity and suitability matter; ornate wording, jargon and uniform formality
are not quality goals.

Choose a structure that serves the genre. A report may lead with its conclusion;
instructions may follow an action sequence; correspondence may lead with its
purpose or request. Do not impose a report structure on every document. Titles
and headings should help the intended reader understand the subject, coverage or
main point. Topic labels, findings, questions and metaphors can each be suitable;
judge whether they communicate the content clearly in context. Do not copy
internal drafting prompts into the output merely because they guided the work.

In analytical reports and plans, connect evidence to interpretations and proposed
actions, retaining material assumptions beside the conclusions they affect.
Use tables for comparable values, options or schedules, and prose for their
meaning. Consolidate repetition and keep supporting detail proportionate to the
reader's needs. These requirements do not authorize rewriting supplied content
during a formatting or conversion task.

## Check the requested result

- For read-only work, verify the requested content or file properties and
  preserve the source. Reading an Office file does not add requirements to
  review new prose or validate a newly produced deliverable.
- For created or modified files, check the exact saved output with the selected
  operation's applicable package, rendering and application checks. Limit review
  to the change and its relevant effects; a local edit does not require a new
  investigation of the entire document.
- When analytical content was authored or changed, reconcile affected figures,
  interpretations and recommendations to the checked workings, including prose
  surrounding tables and charts. Update dependent statements when results change.
- When prose was authored or rewritten, review its organization, wording,
  headings and cross-references for the intended audience and purpose.

Retain important check results or limitations in existing notes or logs. A package
pass or successful render does not establish content quality. Return only the
requested findings or files, and state material unexecuted checks honestly.
Keep internal skill paths and execution details out of the document unless needed
to use it or requested.

## Package map

This entry owns shared task routing and conditional content guidance. Format
entries own setup, presentation profiles and file operations, with task-specific
references. Load only those needed. Scripts, templates and assets retain their
existing paths.

The implementations are adapted from MiniMax's MIT-licensed skills. Original
licenses and pinned-source attribution are preserved in each subdirectory's
`LICENSE` and `UPSTREAM.md`.
