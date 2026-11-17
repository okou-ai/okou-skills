# Stored text and scoped package inspection

These stdlib tools are read-only and require no .NET, setup or renderer.
`docx_preview.sh FILE` returns complete stored body text; `--part` can select
headers, footers, footnotes, endnotes, comments, `all`, or an exact XML part.
Non-body text is labeled separately, not reconstructed into page order.

## Inventory detail is opt-in

```bash
python3 "$SKILL_DIR/scripts/docx_inspect.py" inventory document.docx > document.inventory.json
```

The default contains the first 50 direct body elements with 160-character text
previews, all styleId/name/type/basedOn/default records and used styles, section
properties, relationships/references and cheap ZIP part names/sizes. It does not
read media/binary parts. `body_coverage` reports total/range/completeness;
`text_truncated` identifies shortened text. Counts describe stored XML, not pages.

- `--start 50 --end 100`: another zero-based, end-exclusive body range.
- `--full`: all body elements and complete text; incompatible with a range.
- `--xml`: serialized XML for selected body elements, styles and sections.
- `--hash-parts`: byte-preservation hashes; explicitly reads every ZIP member once.

Flags are independent: full text does not imply XML or hashes. Choose needed
coverage/evidence once and reuse the saved source inventory. For example, whole
template-zone selection may need `--full`, a targeted style fix may need `--xml`,
and a preserved base/output comparison may need `--hash-parts`. Do not scan all
binary parts just to inspect styles.

`text FILE --start 3 --end 8` selects a body range without an inventory.
`part FILE word/numbering.xml` prints a specific serialized XML part. Printed XML
is inspection data, not original byte-preserving input for repacking.

## Limits

Text is not OCR, lossless extraction, field recalculation, rendered pagination or
full revision acceptance. Drawings, equations, automatic numbering and alternate
content need specialized inspection. Reference scanning covers `r:id/embed/link`
in body/header/footer/note/comment XML, not every feature's semantics. Inventory,
part hashes and reference presence do not replace package or actual-output QA.
Conventional Word part paths are assumed; legacy `.doc` needs conversion first.
