# Validate a DOCX and its requested PDF companion

Check the exact final file and repeat affected checks after edits. Set `SKILL_DIR`
and `OFFICE` per [setup](../../SKILL.md#setup). Never overwrite the source.

```bash
python3 "$OFFICE" validate --input output.docx --business
```

This runs OpenXML SDK package validation; `--business` adds general document
checks, not business judgment or GB/T, APA or publisher certification. See
[actual coverage and subset limits](../implementation/validation.md).
`tool-help --tool docx-validate` owns detailed options. The underlying optional
subset XSD is not full OOXML: use it only for intentionally restricted documents,
never by stripping valid features to force a pass. Diagnose before repair;
`fix-order` and `merge-runs` are targeted mutations, not routine checks.

For an edit, compare authorized changes against the original:

```bash
bash "$SKILL_DIR/scripts/docx.sh" diff --before input.docx --after output.docx
```

For requested PDF output or actual-page review:

```bash
python3 "$OFFICE" preflight --format docx --rendering
python3 "$OFFICE" render --input output.docx --out output.pdf --pages preview/pages
```

Omit `--pages` if only PDF export is needed. Render the authored DOCX for a
Word/PDF pair. Preflight tests the environment, not this candidate; a successful
render is not visual inspection. Use disposable copies, an isolated application
profile, macros disabled and no external-link updates.

Inspect actual pages when visual QA applies: content completeness, page breaks,
font substitutions, tables, hierarchy, fields and headers/footers against the
chosen requirements. Recheck after fixes. Report structural, business and visual
coverage separately, including unavailable checks; deliver only requested formats.
