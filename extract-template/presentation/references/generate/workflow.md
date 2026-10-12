# Generate a deck from this template

Follow the template's `SKILL.md` for its identity and language rules.
The package is ready to use; no need to extract, install or save the template again.

## 1. Decide the story and layouts

- Read the prompt and supplied material once. Identify the audience, intended outcome,
  throughline and one takeaway per slide internally. No separate planning artifact
  or approval pause is needed.
- Ground every claim in the supplied material. Label forecasts, targets and assumptions.
- Choose slide roles and layouts from `layouts/source-index.json`; use
  `library/references/catalog.md` when source layouts do not fit. Let the content
  determine the count within any user-requested count or range.

## 2. Batch-read the build set

Read `tools/qa-config.json`, `design-system.md`, the selected layout fragments and
their required styles together with [layout reuse](layout-reuse.md) and
[runtime hooks](runtime-contract.md). No need to read unselected fragments,
extraction guides or QA/runtime implementation files, or reread unchanged files.

## 3. Assemble and author once

Copy `layouts/_shell.html` into the final web directory, resolve final asset paths
and adapt the selected fragments to the supplied material. Preserve the source
styling, required chrome and [10px floor](typography-fit.md), with shared CSS and
runtime included once. Keep the stored template and library originals unchanged.
Make content and layout decisions autonomously while authoring.

## 4. Final QA and delivery

Follow [qa.md](qa.md) with the chosen page count. Checks covered by the supplied QA
need no separate manual preflight. Use its JSON result: fix reported causes together
and rerun after edits; review only QA-designated pages unless a full review was
requested. Record any required receipt and pass final QA. Follow the same guide
for capture staging, requested PPTX checks and one final publication/upload.
