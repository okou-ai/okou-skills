# VALIDATE a workbook

Check structure, calculations, scenario requirements and usability separately.
Set `SKILL_DIR` and `OFFICE` per [the entry point](../../SKILL.md). Never save,
recalculate or restyle the source for read-only analysis. Application and mutation
tests use disposable copies, isolated profiles, disabled macros and no external-link
updates; do not interfere with other application processes or locks.

## 1. Static checks

```bash
python3 "$OFFICE" validate --input output.xlsx --styles
```

Omit `--styles` when a style audit is not needed. JSON receipts describe only the
checks executed. Formula scanning detects cached error markers, some broken sheet
references and heuristic unknown names; it does not calculate formulas or prove
business accuracy. Inspect warnings against actual names/functions and shared
formula ranges rather than equating every exit code with the same verdict.
Empty caches are untested results, not zero. Also check required sheet/part and
relationship consistency, string/style references and preserved package features;
XML packing is not complete OOXML or application validation.

The optional style audit finds some malformed indices, formula colors and numeric
format issues, not all finance roles, cross-sheet dependencies, ratio formatting,
input separation or readable layout. `validate --help` and
`tool-help --tool xlsx-formulas` / `tool-help --tool xlsx-styles` own tool details.

## 2. Actual calculation and input behavior

Run the independent control before substantial formula authoring, then test the
candidate:

```bash
python3 "$OFFICE" preflight --format xlsx
python3 "$OFFICE" recalc --input output.xlsx --out recalculated.xlsx
python3 "$OFFICE" validate --input recalculated.xlsx --styles
```

Preflight checks a retained live formula and expected nonzero cached result in a
separate control; it is **not** a candidate pass. A binary/version probe, successful
process exit, copied file, recalculation flag or fake/synthesized cache must not
pass as recalculation. Require a newly written output, retained live formulas and
usable computed values. Diagnose failures (including missing Calc components)
before retrying; install dependencies only with permission. A timeout or unavailable
engine is not a pass or evidence that the workbook is corrupt.

Independently compare critical results with source-based expectations, including
periods and denominators. On a fresh copy, change a relevant driver, recalculate
and verify dependent results and current-scenario explanations; restore baseline
for delivery. Check [input contracts](../common/data-and-inputs.md), allowed
values/types and validation feedback. A stored input is not proof of a successful
GUI selection. Do not conceal missing data or formula errors with blanket zeros.

Before choosing the recalculated output, compare formulas, controls, formatting
and advanced features for conversion damage. If preservation is uncertain, keep
the source-preserving authored file and disclose what was tested on the copy.
Reopen the **exact final file** in formula and cached-value views without saving;
check required detail/summary outputs and current critical caches. Any later
library save requires recalculation and rechecks. Uncomputed essential results
or unloadable sheets make a ready-on-delivery model incomplete.

## 3. Actual presentation and scenario review

The wrapper does **not** implement native XLSX render/export. Use an application
to export every relevant populated sheet/report area to PDF or another faithful
preview, with the same isolation and safety settings and a fresh export directory.
Render an exported PDF through `python3 "$OFFICE" render --input exported.pdf --pages preview/pages`
or the platform presentation screenshot command, then inspect the actual images.
An export receipt or extracted text is not visual review.

Check clipping, wrapped notes, `###`, overlaps, chart boundaries, meaningful
headers, print areas and readable scaling. Apply the applicable scenario's units,
periods, role distinctions, reconciliations and baseline-qualified narrative.
For charts, use [saved-chart checks](../common/charts.md#verify-the-saved-chart)
for linkage, input-driven refresh and rendered output. For edits, compare against
the source without treating unrelated defects as authorized changes. Fix layout
or semantic defects, regenerate and repeat affected checks.

## 4. Delivery claims

Retain concise evidence of material failures, fixes and rechecks. State meaningful
checks actually performed and unavailable/failed ones; no scanner certifies
financial correctness, usability or complete presentation quality. Deliver only
requested files. A separate report is optional, not a substitute for a usable XLSX.
