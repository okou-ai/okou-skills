# Validate a DOCX and its requested PDF companion

Run on the completed document and repeat affected checks after edits. Existing
files remain untouched unless their modification is authorized. Set `SKILL_DIR`
as described in [the entry point](../../SKILL.md#setup).

## Package and business checks

```bash
bash "$SKILL_DIR/scripts/docx.sh" validate --input doc.docx --document-rules
```

`validate` always runs the OpenXML SDK validator on all package parts, including
structure and relationships. `--document-rules` adds general document checks; it is not
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

For DOCX-only delivery, check the completed document for images and tables,
including those inherited from a template. When it contains neither and the
task does not require visual verification, run the package and business
validation script above and skip rendering and visual review. Skip renderer
setup on this path.

When images or tables introduce a layout risk, render the affected content
and inspect the relevant pages. Follow any explicit visual review or layout
verification requirements regardless of document contents.

For a requested Word/PDF pair, export the authored DOCX instead of redesigning it:

```bash
python3 "$SKILL_DIR/scripts/render_docx.py" doc.docx --out output/doc.pdf
```

Where package installation is permitted, rendering attempts one automatic
dependency installation during preflight when needed (Writer, plus Poppler for
`--pages`). Add `--no-install` when installation is not permitted.

For a user-requested rendered preview or visual review, add `--pages preview/pages`
to the rendering command and inspect the actual images. Render the validated
candidate first. Check page breaks, font substitutions, tables, headings, fields,
headers/footers and content completeness against the chosen requirements.

Deliver only requested formats and state any required application, visual or
standards checks that could not be completed. Do not label a structural
validator or sample recipe as a complete publication/government compliance
certificate.
