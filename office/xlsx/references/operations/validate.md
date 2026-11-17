# Validate a workbook — one impact-driven check plan

Use this same matrix at the end of CREATE and EDIT. Combine rows when a change
has several effects; do not run unrelated checks by default. Reuse reliable
unchanged-source/baseline evidence, and rerun affected checks after fixes. No
scanner proves business accuracy, calculation, preservation and usability at once.

## 1. Select checks by impact

| Operation / actual impact | Required checks | Not a default requirement |
| --- | --- | --- |
| READ extraction/analysis, no save | Verify requested cells/records, types, units/periods and material calculations; state cache and sampling limits | Save, mutation, style audit, recalculation or export |
| Values/text in a nonformula table, or verified independent of calculations | Reopen the exact changed cells; verify type, source coverage and unrelated-part preservation. Check actual affected display if text length/format can alter it | Calc, driver mutation or whole-workbook PDF |
| Formula, model input or value feeding calculations; new formula/model work | Static formula/dependency checks, actual candidate calculation, independently expected key results and current final formula/cache readback. For authored/changed adjustable models, test material driver propagation on copies | Reusing a previous candidate's results after any save/formula/input change; unrelated sensitivity work |
| Layout/style/chart change | Inspect the actual affected sheets/areas in an application **or** a faithful rendered export; verify chart linkage when changed | Recalculation if dependencies truly unchanged; a second PDF solely to duplicate adequate application-view QA |
| Structure: rows/columns, sheet names, names/tables/relationships/controls | Review all affected dependencies and package consistency; compare untouched records, formulas and high-risk parts against source. Add calculation/visual rows where impacted | Blind global shifts, rebuilding through an unsupported library, treating XML parsing as preservation proof |
| Printing, pagination or export is requested/changed | Produce the relevant export and inspect its actual pages, report areas, scaling and page breaks | Substituting application screen QA for pagination QA |

A new ready-to-use financial model normally combines calculation, propagation,
layout and preservation checks; it does not qualify as a simple nonformula edit.
Formatting can itself affect formulas (for example format-sensitive functions),
and a one-cell value can feed a large model. Determine impact from dependencies,
not file extension, edit size or a label such as "format-only". READ requiring
fresh results uses only an authorized disposable calculation copy, never the source.

## 2. Static and preservation checks

For affected formula work:

```bash
python3 "$SKILL_DIR/scripts/formula_check.py" output.xlsx
```

Use `--json`, `--report`, `--summary` or `--sheet` only as needed. Text mode treats
unknown-name-only findings as heuristic warnings; JSON/report modes may exit
nonzero for them. Confirm their meaning instead of equating exit codes.

The scanner detects cached errors, some broken sheet references and heuristic
unknown names; it does not evaluate formulas or validate every feature. Missing
or blank caches are unknown, not zero. Review shared-formula primaries and their
complete dependent ranges, array/spill metadata and actual workbook names.

For authored/changed parts, check sheet/relationship/content-type consistency,
style/string references and valid element order. Packing establishes XML
well-formedness only, not full schema/application compatibility. Compare the
source inventory, unchanged formulas/XML and relevant binary parts. The scoped
packer preserves untouched ZIP records; replacements still need semantic review.
Digital signatures may be invalidated by even a legitimate small edit.

## 3. Calculation environment and actual execution

Before substantial formula authoring, run one independent control in the task's
unchanged calculation environment. `--check` only discovers a binary/version.
`--preflight` actually calculates a new workbook starting with an empty cache,
then requires its live `SUM(A1:B1)` formula and nonzero numeric cache **42**.
A successful control does not validate any candidate.

Optional explicit same-task receipt (choose a task-specific new path and ID;
existing unrelated files and candidate/receipt path aliases are refused):

```bash
python3 "$SKILL_DIR/scripts/libreoffice_recalc.py" --preflight \
  --receipt /tmp/task-calc.json --task-id task-unique-id
# Later preflight calls with these exact arguments reuse a passing control only
# if the environment fingerprint still matches and the receipt is <= 2 hours old.
python3 "$SKILL_DIR/scripts/libreoffice_recalc.py" output.xlsx /tmp/recalculated.xlsx \
  --receipt /tmp/task-calc.json --task-id task-unique-id
python3 "$SKILL_DIR/scripts/formula_check.py" /tmp/recalculated.xlsx
```

Without a receipt, `--preflight` always runs a real control. In Python, pass one
explicit `CalculationSession` to reuse control/version evidence across calls.
The bounded passive fingerprint binds task ID and fixed executable/install,
Calc/main registry, bootstrap/service/type, Calc-library, package-manager/linker
and control-script metadata. It samples only allowlisted loader, locale,
PATH/home/temp and backend/runtime settings, never the full environment. It does
not recurse through installation trees or run a version command. Unknown layouts,
uninspectable identities and bootstrap overrides disable capability reuse; a
successful fresh control still passes but cannot create reusable evidence.
Ordinary no-receipt candidate conversions skip capability fingerprinting.
Receipt reuse is local task evidence, not exhaustive monitoring, a signed/portable
attestation or proof of every transitive library/configuration/font. Delete the
receipt after uncaptured dependency/configuration changes; candidate conversion
failure invalidates it. Do not share it across tasks or trust an untrusted receipt.

Version discovery may reuse this explicit session/valid receipt; **candidate
calculations never do**. Saving or changing formulas/inputs invalidates previous
candidate evidence. Rerun calculation and readback on the exact final revision.
No check installs software or retries Calc implicitly. Diagnose unavailable Calc,
timeouts or failed conversions before any authorized environment repair/new run.
Exit 2 is unavailable; exit 1 is failed, neither is passed. Never interfere with
another application's processes.

The helper uses isolated profiles, source copies and a fresh output directory.
Exit zero alone is insufficient: require a newly written output, retained live
formulas and useful calculated results. Independently compare material outputs
to source-based expected values, with correct units and periods. For an authored
or changed adjustable model, mutate relevant drivers on fresh copies, calculate,
verify detail/summary/required sensitivity outputs and current-scenario narrative,
then restore the baseline. Formula text is not propagation evidence. Check changed
[data/input contracts](../common/data-and-inputs.md); scripted values are not GUI
entry/dropdown tests.

Inspect conversion effects before selecting a recalculated file for delivery:
other applications may alter advanced formulas, controls, VBA, charts or styles.
If preservation is uncertain, retain the source-preserving authored file and say
exactly what was tested on the disposable copy. A ready-to-use calculation-driven
model must have computed required detail/summary areas, live formulas and current
critical caches in the exact final file (including ratio denominators). Recalc
flags are not results. Do not fabricate caches or disguise errors with arbitrary
zeros; uncomputed essential results mean incomplete delivery, not a finished model.

## 4. Relevant visual and scenario checks

- For layout/display impact, inspect each relevant affected worksheet/area using
  an actual application view **or** rendered export. Check clipped/wrapped text,
  `###`, overlaps, units, headers, chart boundaries and readable scaling. For new
  reader-facing models, cover all required report areas, not a convenient sample.
- If printing/pagination/export matters, inspect the actual export pages and
  inclusion of intended sheets/report areas. Use an isolated profile/fresh export
  directory; for PDF page images on Okou Harness use `okou presentation screenshot`
  (read its help). Export success alone is not visual inspection. After fixes,
  revisit affected views/pages, not unrelated whole-workbook exports.
- Review only applicable scenario requirements. Financial READ needs financial
  semantics, not theme/font/spacing changes. Authorized new/layout work also needs
  the chosen hierarchy, formats, input/formula roles and baseline-qualified notes.
- For changed charts use the [saved-chart checks](../common/charts.md#verify-the-saved-chart).
  `style_audit.py` is optional diagnosis, not proof of finance font roles, ratio
  formats, input separation or actual readability.
- Do not turn unrelated pre-existing defects into authorized edits.

## 5. Fix and deliver honestly

Correct diagnosed defects and rerun the affected matrix rows. Retain evidence
needed for material claims and disclose unavailable/failed checks; do not claim
execution, propagation or visual approval from static inspection. Tool absence
alone does not prove corruption. Deliver the requested files, not a mandatory
extra validation report or working-file bundle.
