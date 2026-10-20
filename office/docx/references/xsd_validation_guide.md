# Document validation

Set `SKILL_DIR` to the absolute `office/docx` directory in the installed Office
package. Run setup once before using the CLI.

## Package validation

```bash
bash "$SKILL_DIR/scripts/docx.sh" validate --input output.docx --business --json
```

Every `validate` command runs the OpenXML SDK validator across the package,
including styles, headers, footers and relationships. It reports invalid element
order, missing required parts and invalid attributes without enforcing a design
recipe. Failures return a nonzero exit code.

`--business` adds the shipped business checks for margins, font-size ranges,
heading hierarchy, table widths, relationships and comments. It does not require
12 pt body text or replace the selected template's typography.

## Template comparison

```bash
bash "$SKILL_DIR/scripts/docx.sh" validate --input output.docx --gate-check template.docx
bash "$SKILL_DIR/scripts/docx.sh" diff --before source.docx --after output.docx
```

`--gate-check` takes a **template DOCX**, not an XSD. Use it after applying a
template; investigate failures before delivery. Review the diff for unintended
content or structure changes.

## Optional subset XSD

```bash
bash "$SKILL_DIR/scripts/docx.sh" validate --input output.docx \
  --xsd "$SKILL_DIR/assets/xsd/wml-subset.xsd"
```

This schema checks only `word/document.xml` against a curated subset. It includes
common paragraphs, runs, tables, section properties, hyperlinks and revision
markers. `relationships.xsd` declares `r:id`; `xml-attributes.xsd` declares
`xml:space`. Imports resolve locally within the schema directory.

It does not provide full OOXML coverage. Drawing internals, math, vendor
extensions, markup compatibility and other package parts need the SDK validator.
Do not remove valid features merely because the subset does not describe them.
The retained `business-rules.xsd` and `aesthetic-rules.xsd` are upstream design
references; they are not executable replacements for `--business` or a template
gate and their XSD 1.1 assertions are not supported by .NET's XSD 1.0 engine.

## Diagnose and review

- For element-order failures, consult `references/openxml_element_order.md` and
  repair the indicated part. Do not run mutation helpers indiscriminately.
- For missing relationships, inspect the affected part's `.rels` file and target.
- A schema compilation error is a validator/schema problem, not evidence that
  the document content is corrupt. Fix the schema or use the full SDK check.
- After fixes, rerun validation and render the completed document:

```bash
python3 "$SKILL_DIR/scripts/render_docx.py" output.docx \
  --out preview/output.pdf --pages preview/pages
```

Inspect page images for clipping, unexpected blanks and layout defects.
`docx_preview.sh` extracts text only and cannot substitute for visual review.
