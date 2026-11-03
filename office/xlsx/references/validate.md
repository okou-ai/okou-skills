# Validate a workbook

Check file structure, calculations, scenario requirements and actual usability
separately. No single scanner proves business accuracy or presentation quality.
For read-only work, never save or recalculate the original without permission.
For creation/editing, use disposable copies for application and mutation tests.

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
application when available. `--check` locates LibreOffice and its version; it
does not prove Calc works. First verify a minimal independent formula workbook
and its expected calculated value, then test the candidate copy:

```bash
python3 "$SKILL_DIR/scripts/libreoffice_recalc.py" --check
python3 "$SKILL_DIR/scripts/libreoffice_recalc.py" output.xlsx /tmp/recalculated.xlsx
python3 "$SKILL_DIR/scripts/formula_check.py" /tmp/recalculated.xlsx
```

The helper preserves its input and uses an isolated profile. A newly written
output and usable recalculated values are required; process exit alone is not
enough. Exit 2 means unavailable; exit 1 means a failed check, not a pass. Do
not repeatedly retry a timeout or interfere with another application's process.

Independently verify key results against the actual source and intended
calculation. For an adjustable model, change a relevant driver on a fresh
copy, force recalculation, and verify dependent results; restore the baseline
for delivery. A no-error result can still use the wrong formula or period.

Check conversion effects before selecting a recalculated file for delivery.
Other applications can change formulas, controls, formatting or advanced
features. If preservation is uncertain, keep the authored/source-preserving
file and disclose exactly what was checked on the disposable copy.

## 3. Presentation and scenario review

- Review the selected scenario's requirements. Financial outputs must satisfy
  the finance layer's reading order, font roles, units, period distinction,
  formula/input separation, reconciliation and baseline-qualified narrative.
- Inspect each relevant populated worksheet in an application or rendered
  export. Check clipped/wrapped text, `###`, overlaps, chart boundaries,
  meaningful headers and readable print/export scaling. Rerender after fixes
  that affect layout; a successful export is not itself visual inspection.
- `style_audit.py output.xlsx` can help diagnose malformed style indices,
  blue formulas and some numeric-format issues. It does **not** enforce all
  finance font roles, cross-sheet green, input separation, summary hierarchy
  or print readability. Check those requirements directly; its success message
  is not a financial-format compliance certificate.
- For edits, compare the changed file with the source and verify the requested
  operation without treating unrelated existing defects as authorized changes.

## 4. Fix and report honestly

Correct diagnosed defects, then rerun the affected checks. Do not mask missing
inputs, lookup failures or numeric errors with arbitrary zeros/blanks. Review
warnings against real names, functions and intended business behavior.

Keep only the working evidence needed to support your statements. In the final
response, identify meaningful checks performed and any unavailable/failed
checks; do not label unperformed work as passed. For example: "Static scan
completed; Calc unavailable, so recalculation and input propagation remain
unverified." Tool absence alone is not evidence that the workbook is corrupt.

Deliver the user's requested files. A separate validation report is appropriate
when requested, not a mandatory extra attachment or a substitute for the XLSX.
