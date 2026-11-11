---
name: office
description: Create, edit, format, convert, or validate DOCX, PDF and XLSX files. Use when the task requires producing or changing an Office file, applying a template, repairing formulas or file structure, or inspecting layout, editability, recalculation, form fields or saved-file usability. Reading, summarizing, translating or analyzing document contents alone does not require this skill.
license: MIT
---

# Office files

## Scope

Use this skill for file production, modification and format-specific inspection.
An Office file supplied as source material is not by itself a reason to load it.
For ordinary reading, extraction, summaries, translation or content analysis,
use the available reading tools directly. If the requested result is an Office
file, or the task concerns its layout, structure, formulas or usability, use the
relevant file route below.

Choose the workflow by the requested operation. Formatting, conversion, template
filling and limited edits do not authorize new analysis or a rewrite. Apply the
analysis section only when developing explanations, comparisons, recommendations
or feasibility judgments for the deliverable. Apply the writing section to new
or substantially rewritten prose, including workbook narratives. For limited
edits, review the affected content and necessary context.

Honor the user's audience, genre, language, sources, scope, length and template.
Use only authorized factual sources. When a material input is missing, ask if
clarification is permitted; otherwise complete the supported work and qualify
the affected conclusion. Preserve required headings and source field names.

## Develop the analysis

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
and established causes. A cost saving during falling sales does not by itself
show greater efficiency; an accounting residual does not identify its cause.
Missing causal evidence does not prevent completing supported calculations or
comparisons.

For a changed scenario, state what changes and what stays constant, then update
all dependent results and resource constraints. A fixed setup fee remains fixed
when channel spend scales unless an additional cost is justified. Scaling all-in
cost per result also scales that fee. Unknown capacity or unit economics makes
such a calculation conditional, not a guaranteed outcome or a proven minimum
budget. Check the revised proposal as a whole: a budget solution may create a
staffing or timing conflict.

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

Order content around the recipient's task. The opening should establish the
subject, scope and main finding or recommendation, including a condition
essential to interpreting it. Keep the reasoning needed to assess that conclusion
in the main narrative; place useful but interrupting detail in notes or an
appendix when appropriate. Combine sections that serve the same reader need.

The document title identifies its subject and purpose. In formal reports, use
concise, descriptive section headings with established domain terminology.
Headings at the same level should have comparable scope and grammatical form;
subheadings should divide the parent topic meaningfully. A finding-led heading
must retain material qualifications. Internal analysis prompts, coaching language,
slogans and metaphors should not become report headings. Question-based headings
remain appropriate when the requested genre calls for them.

Develop each paragraph around a substantive point. Connect evidence to its
interpretation and consequence; explain how a comparison supports the proposed
choice. Use tables for comparable values, options or schedules, and prose for
relationships the table leaves implicit. Distinguish reported facts, analytical
judgments and proposed actions through wording. Put assumptions and limitations
beside the conclusions they affect and explain their practical consequence;
consolidate recurring qualifications instead of repeating general disclaimers.

Use concrete subjects, precise verbs and familiar terms at the reader's level
of technical detail. Formality comes from accuracy and disciplined organization,
not inflated vocabulary, abstract noun phrases or narration of the agent's work.

## File workflow

Set `OFFICE_DIR` to the absolute directory containing this file. Set `SKILL_DIR`
to the selected subdirectory before running its examples; it is a shell variable,
not a literal directory named `SKILL_DIR`. Do not assume the current working
directory is the skill directory.

| Output or task | Read | Set |
| --- | --- | --- |
| Word creation, editing, formatting, or DOCX-to-PDF, including government-style, named academic, thesis-template and business/editorial documents | [docx/SKILL.md](docx/SKILL.md) — select the applicable presentation profile as well as the operation | `SKILL_DIR="$OFFICE_DIR/docx"` |
| Standalone PDF creation, form inspection/filling, or reformatting, including research/technical content | [pdf/SKILL.md](pdf/SKILL.md) — distinguish named manuscript requirements from visual presets | `SKILL_DIR="$OFFICE_DIR/pdf"` |
| Excel creation, editing, formulas, validation or format-specific inspection, including financial budgets and forecasts | [xlsx/SKILL.md](xlsx/SKILL.md) — select its common and business-scenario layers before authoring | `SKILL_DIR="$OFFICE_DIR/xlsx"` |

The selected template's styles take precedence over generic typography defaults.
For a DOCX and its PDF companion, author once and render the DOCX so content and
layout remain aligned.
Use each route's setup and validation commands; reuse a working environment
within the session. Presentation profiles are formatting guidance, not substantive
research, policy, medical or legal expertise. Package checks do not certify
compliance with a publication or government standard.

## Review and deliver

Check the exact saved output, not only the authoring code or intermediate data:

- Reconcile the main figures, source interpretations, assumptions and
  recommendations to the checked workings. Read surrounding prose as well as
  tables and charts; update dependent statements when a result changes.
- Read the title, heading outline, opening and each section's main point together.
  Repair missing reasoning, unsupported emphasis, inconsistent terms and
  repetition. Confirm that headings, prose, tables and cross-references agree.
- Run the selected format's package, rendering and application checks. Record
  important executed or unavailable checks in existing notes or logs; structural
  validation or a successful render does not establish content quality.

Keep internal skill paths, review instructions and execution details out of the
document unless needed to use it or requested. Deliver only requested files and
state material limitations or unexecuted checks honestly.

## Package map

This entry owns shared scope, analysis, writing and content review. Each format's
`SKILL.md` owns setup, presentation profiles and file operations, with references
grouped by responsibility:

- `common/`: reusable data/presentation conventions.
- `domains/`: applicable business or named-format requirements.
- `operations/`: the authorized create/read/edit/fill/validate workflow.
- `implementation/`: library, package, schema and environment details.

Load only the format-specific guides needed for the task. Scripts, templates
and assets retain their existing paths.

The implementations are adapted from MiniMax's MIT-licensed skills. Original
licenses and pinned-source attribution are preserved in each subdirectory's
`LICENSE` and `UPSTREAM.md`.
