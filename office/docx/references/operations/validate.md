# Validate a DOCX and its requested PDF companion

Use for authored/edited output, not content-only reads. Validate the candidate
package and authorized changes; repeat affected checks after edits. Existing
files remain untouched unless their modification is authorized. Set `SKILL_DIR`
as described in [the entry point](../../SKILL.md#setup).

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

Render for requested PDF output or when affected pagination/layout needs visual
QA, not for reading or package-only inspection. For a requested Word/PDF pair,
export the authored DOCX instead of redesigning it.

Before authoring, create a private directory unique to this task/session and
prepare once. Keep these variables for the actual render; do not reuse this
receipt across tasks or share it with parallel work:

```bash
DOCX_RENDER_SESSION=$(mktemp -d)
python3 "$SKILL_DIR/scripts/render_docx.py" --prepare \
  --probe-cache "$DOCX_RENDER_SESSION/writer.json" --probe-session "$DOCX_RENDER_SESSION"
# Later, same task/session and unchanged converter environment:
python3 "$SKILL_DIR/scripts/render_docx.py" doc.docx --out output/doc.pdf --no-install \
  --probe-cache "$DOCX_RENDER_SESSION/writer.json" --probe-session "$DOCX_RENDER_SESSION"
# Remove this directory when all same-task renders are done.
```

Use `--no-install` on prepare too when installation is not permitted. If page
images are needed, include `--pages preview/pages` in both calls (Poppler only
then). Only a **successful Writer capability** is cached, for at most two hours,
using a bounded set of executable/runtime, Writer-registry and package-database
metadata plus allowlisted non-secret loader/locale/backend/temp-path settings.
There is no tree/font scan or full-environment collection. **Discard the receipt
after any installation/configuration change (including fonts)**; these fixed
samples are not exhaustive change monitoring. Changed identity, unknown layouts
or bootstrap overrides, uninspectable fingerprints, failed controls, installation
and candidate errors invalidate reuse. Font appearance remains candidate QA.
Every candidate still converts
once and must produce a fresh PDF; no document result is cached and failed or
unknown conversions are never automatically replayed.

Without receipt flags the command safely performs a fresh control; `--check` is
always a fresh no-install/read-only probe and cannot use receipt flags. Do not
combine an early prepare with another standalone `--check`/`--with-rendering`.
A capability pass is not candidate content/layout validation.

For a user-requested rendered preview or visual review, add `--pages preview/pages`
to the rendering command and inspect the actual images. Render the validated
candidate first. Check page breaks, font substitutions, tables, headings, fields,
headers/footers and content completeness against the chosen requirements.

Deliver only requested formats and state any unexecuted application/visual or
standards checks. Do not label a structural validator or sample recipe as a
complete publication/government compliance certificate.
