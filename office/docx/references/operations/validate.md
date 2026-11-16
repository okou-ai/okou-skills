# Validate a DOCX and its requested PDF companion

Run on the completed document and repeat affected checks after edits. Existing
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

DOCX-only delivery does not require PDF conversion. For a requested Word/PDF
pair, export the authored DOCX instead of redesigning it:

```bash
python3 "$SKILL_DIR/scripts/render_docx.py" doc.docx --out output/doc.pdf
```

The rendering entry point tests Writer with a known-good DOCX before touching the
user document. If unavailable, it attempts to install Writer once. Only
`--pages preview/pages` requires Poppler (`pdftoppm`); an installed Writer alone
is sufficient for PDF output. It never installs .NET, Pandoc or a general font
bundle. Python 3 must be available before invoking the script.

Automatic installation requires an authorized environment: supported Linux
package managers are apt-get, dnf, pacman, zypper and apk, using root or
noninteractive `sudo -n`; macOS uses an existing Homebrew installation. Windows
and other environments require manual dependency provisioning. An installation,
permission, network or post-install probe failure exits nonzero without retrying
the user document. The installer wait limit is 600 seconds per command;
`--timeout` controls conversions instead. A timed-out package transaction may
leave running child processes or partial changes: inspect it before retrying;
the script does not claim rollback or automatically repeat package operations. Use `--no-install` to prohibit package
installation entirely. A failure converting the actual document is reported as
such, not treated as a reason to reinstall or retry.

For diagnostics without package installation:

```bash
python3 "$SKILL_DIR/scripts/render_docx.py" --check
# Include Poppler in the check; this does not create the pages directory:
python3 "$SKILL_DIR/scripts/render_docx.py" --check --pages preview/pages
```

For a user-requested rendered preview or visual review, add `--pages preview/pages`
to the rendering command and inspect the actual images. Check page breaks, font
substitutions, tables, headings, fields, headers/footers and content completeness
against the chosen requirements. Preview PDF/PNG files are review intermediates,
not additional delivery formats unless requested.

Deliver only requested formats and state any unexecuted application/visual or
standards checks. Do not label a structural validator or sample recipe as a
complete publication/government compliance certificate.
