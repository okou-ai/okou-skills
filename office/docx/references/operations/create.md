# CREATE a DOCX

Use for new documents without a structured supplied template. Existing content
edits use [EDIT](edit.md); new content in a structured template uses
[BASE-REPLACE](template.md). Follow the [entry routing order](../../SKILL.md#routing-order-common--applicable-profile--operation):
user requirements and templates take precedence over profiles and generic presets.
Set `SKILL_DIR` and `OFFICE` as in [setup](../../SKILL.md#setup).

## Decide content and presentation

Establish the intended reader, title, attribution, source-backed sections and any
tables, images or special elements. Separate supplied facts from assumptions and
missing information; do not copy sample findings, citations or agency identities.
The author—not the executable—decides substantive adequacy and usability.

Use [presentation](../common/presentation.md) and the selected profile for layout.
Generic CLI presets are `report|letter|memo|academic`; `academic` is not APA/IEEE,
and `memo` alone does not construct To/From fields. Do not infer named-standard
compliance from a preset. Exact style values belong to the implementation/help,
not a second default table here.

## Simple content contract

`create --format docx --content content.json` reads a JSON **array** of blocks.
Each requires case-sensitive `type` and `text`:

```json
[
  {"type": "heading", "text": "Overview", "level": 1},
  {"type": "paragraph", "text": "Replace with verified task content."},
  {"type": "pagebreak", "text": ""}
]
```

Supported types: `heading` with optional `level` 1–6 (default 1), `paragraph`,
and `pagebreak` with empty text. Tables, images and lists are not part of this
simple block contract.

```bash
python3 "$OFFICE" preflight --format docx
python3 "$OFFICE" create --format docx --content content.json \
  --title "Report" --type report --out output.docx
python3 "$OFFICE" validate --input output.docx --business
```

Use `create --help` and `tool-help --tool docx-create` for parameters rather than
inventing flags. For custom styles, sections, tables, images, TOC, fields or
watermarks, use [direct C# authoring and actual samples](../implementation/authoring.md).
[OpenXML part 2](../implementation/openxml-part-2.md) owns page setup, tables and
headers/footers; [part 3](../implementation/openxml-part-3.md) owns TOC, fields and
images. Adapt only required elements, preserving package invariants.

## Finish

Follow [VALIDATE](validate.md), repair diagnosed defects and repeat affected
checks. For a requested Word/PDF pair, render this DOCX instead of redesigning
its PDF companion. Preserve the source and deliver only requested formats;
preflight or a successful create receipt is not candidate or visual acceptance.
