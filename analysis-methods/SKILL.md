---
name: analysis-methods
description: Apply analytical methods to business research, data analysis, comparisons, and evidence-backed reports, including answers delivered in chat.
---

# Analysis methods

Use the integrated DeerFlow and Scientific Agent Skills resources below for the
parts of the task that need analysis. Preserve the user's question, sources,
language, template and output format. Formatting-only work can reuse completed
analysis. Do not load every reference for a simple question.

## Choose the relevant material

| Need | Read |
| --- | --- |
| Select business frameworks, plan chapters and specify data needs | [DeerFlow framework selection and planning](references/methods.md) |
| Inspect tables, calculate metrics, compare groups or write SQL | [Data analysis and DeerFlow SQL patterns](references/data-analysis.md) |
| Size a market, forecast scenarios, normalize units or compare shares | [Scientific Agent Skills market-analysis patterns](references/market-analysis.md) |
| Choose a statistical test for the outcome and study design | [Scientific Agent Skills test-selection guide](references/statistics.md) |
| Track claim/source evidence, reconcile conflicts and examine explanations | [Evidence model and appraisal workflow](references/evidence.md) |
| Organize substantive findings into a report | [Modular report structure](references/reporting.md) |

Select methods for the question and the evidence that can actually be obtained.
The DeerFlow chapter, data and visualization tables are useful working formats
for substantive reports, not required paperwork for every answer. If data is
missing, carry out the supported analysis and state the conditions or next
observation needed. An unexecuted method is a proposed analysis.

## Execute and check

Use currently available Okou search, file and connector tools within the task's
scope. Keep attachment-only work within the attachments. Inspect actual inputs,
execute calculations and retain the source locations, formulas or queries needed
to reproduce important conclusions. Distinguish observations, calculations,
estimates, forecasts and recommendations; keep unsupported causes conditional.

The bundled `scripts/` and matching `assets/` come directly from the pinned
Scientific Agent Skills market-research package. Use them when their ledger or
scenario format fits the task. They use Python's standard library and operate on
local files; run a tool's `--help` before use. Replace synthetic template data.
A passing structural/arithmetic check does not establish source truth or that
assumptions fit the business question. No framework or document-length quota
applies.

## Deliver

Keep concise answers in chat. For requested files or generated artifacts, pass
the checked content to available `office-files` or `gen` capabilities, preserving
the requested template and format. Analysis does not require either output skill.
Reuse the findings rather than repeating analysis when only the format changes.

[sources.md](sources.md) maps the retained upstream files and the small Okou
adaptations; [upstream-manifest.json](upstream-manifest.json) records exact source
commits and hashes. Keep the accompanying MIT notices.
