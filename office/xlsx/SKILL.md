---
name: xlsx
description: Create, read, edit, format, and validate Excel spreadsheets. Choose the requested operation first; read XLSX/XLSM/CSV/TSV directly without changing the source. For financial work apply finance semantics; layout defaults apply only to authorized new or layout work.
license: MIT
---

# Excel workbooks

Set `SKILL_DIR` to this directory's absolute path. Start with the operation;
load only the relevant references. User requirements, supplied templates and
house styles take precedence over authoring defaults.

## Choose the operation

| Request | Read | Tool path |
| --- | --- | --- |
| Extract/read/analyze XLSX/XLSM/CSV/TSV | [READ](references/operations/read-analyze.md) | Stdlib inventory/preview/range first; explicit `--analyze`/`--quality` only for full pandas work |
| New workbook | [CREATE](references/operations/create.md) | Suitable installed high-level library, or raw OOXML |
| Edit/fill/repair existing workbook | [EDIT](references/operations/edit.md) | Inspect relevant parts; scoped `xlsx_pack.py --base/--part` for small edits; directory unpack/pack remains available |
| Authorized formatting | [Presentation](references/common/presentation.md) + EDIT for existing files | Reuse/append styles; change only intended ranges |
| Check created/edited work | [VALIDATE](references/operations/validate.md) | One shared impact matrix: calculation, layout, structure and export only as affected |

- Preserve sources and unrelated sheets, formulas, styles, controls and binary
  parts. READ never saves, restyles, recalculates or executes macros. Application
  and mutation tests use disposable copies; a narrow edit is not redesign permission.
- Keep derived workbook outputs as live formulas, not substituted cached answers.
  Missing/blank caches are unknown, not zero; values-only reads never overwrite
  formula sources. Recheck candidate calculation after later saves/input changes.
- New/authorized layout work uses [common presentation](references/common/presentation.md).
  Data-only extraction does not require a theme or reader-facing report layout.
- Imports or authored/changed editable inputs use the
  [data/input contract](references/common/data-and-inputs.md); reuse confirmed
  schema evidence and check affected transformations/records.
- New reader-facing analytical reports or authorized chart changes use
  [charts](references/common/charts.md); no fixed chart count or extra model tabs.

## Add the applicable business rules

- Financial models, budgets, forecasts, valuation, statements, sensitivities and
  financial management reports use [finance](references/domains/finance.md).
  For READ load its **financial semantics only**, not theme/fonts/spacing. New
  reader-facing or authorized layout work also uses the relevant authoring defaults.
- Ordinary trackers, inventories, rosters and tables do not inherit finance colors,
  font roles, model tabs or sensitivity work. Mixed workbooks apply finance only
  to the relevant financial areas.
- A one-cell financial input/formula edit retains the existing structure/style;
  apply only relevant semantics and dependency checks, not a new overview sheet.

For new financial work using openpyxl, consult
[authoring primitives](references/implementation/authoring.md) when needed. Check
actual calculation capability once before substantial formula authoring, reuse
explicit same-task environment evidence, and still execute each affected candidate.
Read [OOXML details](references/implementation/ooxml.md) when directly changing
relationships, types, strings or styles; indices are workbook-local.

## Finish

Use the same [impact-driven checks](references/operations/validate.md#1-select-checks-by-impact)
at the end of CREATE/EDIT. Real calculation and affected visual checks remain
necessary for new financial models; unrelated simple edits do not trigger driver
mutation, Calc or whole-workbook PDF export. Report meaningful checks and limits
honestly. A scanner exit code is not a business, preservation or visual certificate.
Deliver only the requested files.
