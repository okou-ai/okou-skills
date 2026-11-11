# Validate a DOCX and its requested PDF companion

Run on the completed document and repeat affected checks after edits. Existing
files remain untouched unless their modification is authorized. Set `SKILL_DIR`
as described in [the entry point](../../SKILL.md#setup).

For analytical content, reconcile the saved document's main figures, source
interpretations, assumptions and recommendations to the checked workings under
[Analysis](../../../references/analysis.md#accept-the-findings-then-check-the-saved-document).
Check accompanying prose and qualifications as well as tables. A structural or
business-rule validation result does not perform this review.

For created or rewritten prose, review the saved title and heading outline under
[Writing](../../../references/writing.md#review-the-saved-wording-as-well-as-its-appearance).
Check that headings describe their sections in the reader's register and retain
the evidence's qualifications; package checks do not assess wording.

## Package and business checks

```bash
bash "$SKILL_DIR/scripts/docx.sh" validate --input doc.docx --business
```

`validate` always runs the OpenXML SDK validator on all package parts, including
structure and relationships. `--business` adds general document checks; it is not
domain certification. Neither a package pass nor a business pass certifies
GB/T, APA or publisher compliance.
Read [validation details](../implementation/validation.md) for actual coverage.

The optional `--xsd "$SKILL_DIR/assets/xsd/wml-subset.xsd"` checks a curated
subset, not full OOXML. Use it only for documents intentionally restricted to
that subset; do not remove valid features merely to satisfy that schema.
Diagnose a package failure and rerun after repair; text preview is no substitute.
Use `fix-order` only for diagnosed ordering errors and `merge-runs` only when
needed, not as routine validation mutations.

## Review authorized content changes

For EDIT, compare the original and completed document:

```bash
bash "$SKILL_DIR/scripts/docx.sh" diff --before in.docx --after out.docx
```

## Rendering and delivery

For a requested Word/PDF pair, export the authored DOCX instead of redesigning it:

```bash
python3 "$SKILL_DIR/scripts/render_docx.py" doc.docx --out output/doc.pdf
```

For a user-requested rendered preview or visual review, add `--pages preview/pages`
and inspect the actual images. Run the rendering environment probe first per
[setup](../../SKILL.md#setup). Check page breaks, font substitutions, tables,
headings, fields, headers/footers and content completeness against the chosen
requirements. Rendering success alone does not verify those properties.

Deliver only requested formats and state any unexecuted application/visual or
standards checks. Do not label a structural validator or sample recipe as a
complete publication/government compliance certificate.
