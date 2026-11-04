# Validate a workbook

Check file structure, calculations, scenario requirements and actual usability
separately. No single scanner proves business accuracy or presentation quality.
For read-only work, never save or recalculate the original without permission.
For creation/editing, use disposable copies for application and mutation tests.

- [Static checks](#1-static-package-and-formula-checks)
- [Application and calculation](#2-application-and-calculation-checks)
- [Presentation](#3-presentation-and-scenario-review)
- [Fix and report](#4-fix-and-report-honestly)

## 1. Static package and formula checks

```bash
python3 "$SKILL_DIR/scripts/formula_check.py" output.xlsx
```

Use `--json`, `--report`, `--summary`, or `--sheet` only when needed. The normal
text mode treats unknown-name-only findings as heuristic warnings; JSON/report
modes may exit nonzero for those findings too. Inspect their meaning rather
than treating every mode's exit code as the same verdict.

The scanner detects cached error markers, some broken sheet references, and
heuristic unknown names. It does not evaluate formulas, find every hardcoded
derived output, validate all package features, or check styling. Empty formula
caches are untested results, not zero or proof that a formula works. Shared
formula consumers need their primary range reviewed; a regex warning about
sheet/name syntax can require manual confirmation.

Check sheet/relationship/part consistency, valid style/string references, and
preservation of relevant features. The packer checks XML well-formedness, not
full OOXML or application compatibility. Inspect all required output areas,
not only a convenient sample or a scanner's formula count.

## 2. Application and calculation checks

For a created/edited formula workbook, test it in a functioning spreadsheet
application when available. Run the independent control before substantial
formula authoring, not only after writing the candidate. `--check` locates
LibreOffice and its version; it does not prove Calc works. `--preflight` creates
a separate formula control, recalculates it, and checks a retained live formula
and its expected nonzero cache. A successful control does not validate a candidate.

```bash
python3 "$SKILL_DIR/scripts/libreoffice_recalc.py" --preflight
python3 "$SKILL_DIR/scripts/libreoffice_recalc.py" output.xlsx /tmp/recalculated.xlsx
python3 "$SKILL_DIR/scripts/formula_check.py" /tmp/recalculated.xlsx
```

If the control cannot load, inspect the application components: a Linux
LibreOffice core install without Calc is not a working spreadsheet engine.
When dependency setup is permitted, install the missing spreadsheet component
and rerun the control. On an apt-based host this may require refreshing the
package index before installing `libreoffice-calc`; an initial "no installation
candidate" is not proof that Calc is unsupported. Respect explicit restrictions
on installing or invoking applications. Do not install software automatically
from a check, or repeatedly invoke a known failing conversion without diagnosis.

The helper preserves its input and uses an isolated profile. A newly written
output and usable recalculated values are required; process exit alone is not
enough. Exit 2 means unavailable; exit 1 means a failed check, not a pass. Do
not repeatedly retry a timeout or interfere with another application's process.

Independently verify key results against the actual source and intended
calculation. For an adjustable model, change a relevant driver on a fresh
copy, force recalculation, and verify dependent results; restore the baseline
for delivery. A no-error result can still use the wrong formula or period.
For editable inputs, also check the saved [data/input contract](../common/data-and-inputs.md):
allowed types/values, enabled validation feedback and source-defined boundaries.
Review current-scenario explanations after mutation, not just the numbers. A
programmatically stored value is not evidence of a successful GUI selection.

Check conversion effects before selecting a recalculated file for delivery.
Other applications can change formulas, controls, formatting or advanced
features. If preservation is uncertain, keep the authored/source-preserving
file and disclose exactly what was checked on the disposable copy.

For a new calculation-driven workbook intended to be ready on delivery, reopen
the exact final file after saving. Confirm that required detail and summary
areas display computed values, retain live formulas, and have current cached
results for critical cells, including ratio denominators. Recalculation flags
alone do not establish this. If required results remain uncomputed or essential
sheets fail to load, report the delivery as incomplete, not a ready-to-use model.
Do not fabricate caches or conceal these defects with blanket error-to-zero fixes.

## 3. Presentation and scenario review

- Review the selected scenario's requirements. Financial outputs must satisfy
  the finance layer's reading order, font roles, units, period distinction,
  formula/input separation, reconciliation and baseline-qualified narrative.
- When charts are included or changed, apply the
  [saved-chart checks](../common/charts.md#verify-the-saved-chart) for data linkage,
  input-driven refresh and actual rendered output.
- Inspect each relevant populated worksheet in an application or rendered
  export. Check clipped/wrapped text, `###`, overlaps, chart boundaries,
  meaningful headers and readable print/export scaling. Rerender after fixes
  that affect layout; a successful export is not itself visual inspection.
- Export each relevant populated sheet to PDF or another faithful preview and
  inspect the rendered pages, not only extracted text. Use an isolated application
  profile and fresh export directory; do not disturb another user's locks/processes.
  On Okou Harness, read `okou presentation screenshot --help` and use it to render
  an exported PDF to page images. Verify that the intended sheets and report areas
  are included. Revise the authoring code/geometry, regenerate and rerender affected
  pages when you find defects; do not merely describe the defect and stop.
- `style_audit.py output.xlsx` can help diagnose malformed style indices,
  blue formulas and some numeric-format issues. It does **not** enforce all
  finance font roles, cross-sheet green, input separation, summary hierarchy
  or print readability. In particular, a percentage check on a percent-formatted
  cell cannot detect every ratio accidentally assigned an amount format. Check
  those requirements directly; success is not a financial-format certificate.
- For edits, compare the changed file with the source and verify the requested
  operation without treating unrelated existing defects as authorized changes.

## 4. Fix and report honestly

Correct diagnosed defects, then rerun the affected checks. Do not mask missing
inputs, lookup failures or numeric errors with arbitrary zeros/blanks. Review
warnings against real names, functions and intended business behavior.

Keep concise working notes of observed defects, changes and rechecks; retain
material failures alongside later successes. Do not create a mandatory receipt
format or extra attachment. Keep only evidence needed to support your statements.
In the final response, identify meaningful checks performed and any unavailable/failed
checks; do not label unperformed work as passed. For example: "Static scan
completed; Calc unavailable, so recalculation and input propagation remain
unverified." Tool absence alone is not evidence that the workbook is corrupt.

Deliver the user's requested files. A separate validation report is appropriate
when requested, not a mandatory extra attachment or a substitute for the XLSX.
