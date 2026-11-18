# Scenario A: Creating a New DOCX from Scratch

Use for a new document without a structured supplied template. For edits or
content inside an existing template, follow the [entry routing](../../SKILL.md#pipeline-routing).

## Standard CLI creation

Use `create --content-json` for headings, paragraphs, tables, lists and inline
figures. Complete the [session setup](../../SKILL.md#setup), prepare the content
blocks below, then create and validate the document:

```bash
bash "$SKILL_DIR/scripts/docx.sh" create \
  --type report --title "Quarterly Revenue Analysis" --page-numbers \
  --content-json content.json --output report.docx &&
bash "$SKILL_DIR/scripts/docx.sh" validate --input report.docx --business
```

Choose the title, section structure and content from the task. Omit optional
title or author text the user has not supplied. Apply any requested named format
or template from the entry's profile routing before choosing generic defaults.

The CLI supplies styles, numbering, tables and package structure. Set the
supported options and content blocks; use [direct C# authoring](#custom-layouts-and-complex-elements)
only when required features are outside them.

## CLI options and defaults

- `--type`: `report` (default), `letter`, `memo` or `academic`. These are generic
  presets, not named profiles such as APA or HBR.
- `--title`: optional visible title paragraph inserted before the JSON content.
  Omit when the body supplies the title; the CLI does not deduplicate titles.
- `--author`: optional visible author subtitle.
- `--page-size`: `letter` (default), `a4`, `legal` or `a3`. Pass the chosen size
  explicitly when the task requires it.
- `--margins`: `standard` (default), `narrow` or `wide`.
- `--header`, `--footer`: optional text; `--page-numbers` adds a footer PAGE field.
- `--toc`: adds a TOC placeholder that must be updated in Word to populate entries.
- `--content-json`: path to the content array. `--output` is required.

The effective presets are defined by [FontDefaults.cs](../../scripts/dotnet/Docx.Core/Typography/FontDefaults.cs)
and [PageSizes.cs](../../scripts/dotnet/Docx.Core/Typography/PageSizes.cs), applied
by [CreateCommand.cs](../../scripts/dotnet/Docx.Core/Commands/CreateCommand.cs).
Consult these when exact preset values matter. The CLI does not load the style
XML assets, and custom-layout design examples are not its defaults.

## Content Configuration JSON Format

Save an array of blocks as `content.json`. Include only the block types needed
for the task; replace the example text and image path with the task's content:

```json
[
  { "type": "heading", "text": "Executive Summary", "level": 1 },
  { "type": "paragraph", "text": "Revenue grew 12% year-over-year." },
  { "type": "heading", "text": "Detailed Analysis", "level": 1 },
  { "type": "table", "headers": ["Region", "Revenue"], "rows": [["North America", "$4.2M"]] },
  { "type": "image", "path": "figures/revenue.png", "widthPx": 480, "heightPx": 300,
    "caption": "Revenue by region", "alt": "Bar chart of revenue by region" },
  { "type": "list", "ordered": true, "items": ["Confirm the period", "Review the regional totals"] }
]
```

Each block requires a case-sensitive `type`:

- `heading`: `text`; optional `level` from 1 to 6 (default: 1).
- `paragraph`: `text`.
- `pagebreak`: inserts a page break.
- `table`: `headers` is a non-empty array of column names; `rows` is an array
  of rows with the same number of cells as `headers`. All cells are strings.
  Headers repeat across pages; keep each row short enough to fit on one page.
- `list`: `items` is a non-empty array of strings. Set `ordered` to `true` for
  a numbered list starting at 1; the default is bullets.
- `image`: `path` is absolute or relative to `content.json`. Supply positive
  integer `widthPx` and `heightPx` in the desired aspect ratio. Large figures
  scale down to the body area. Optional `caption` and `alt` are strings.
  PNG and JPEG embed directly; WebP converts through `dwebp` or Python/Pillow.

The CLI reports invalid blocks by position and preserves an existing output file
on creation failure.

## Custom layouts and complex elements

Use [direct C# authoring](../implementation/authoring.md#project-scaffold) for
required features such as merged cells, nested lists, floating figures or custom
styles/sections not exposed by the CLI. Read the selected named-profile sample
when applicable and only the implementation guide for the needed element:

| Needed feature | Reference |
|---|---|
| Custom styles, runs and paragraphs | [OpenXML part 1](../implementation/openxml-part-1.md) |
| Page geometry, sections, tables and headers/footers | [OpenXML part 2](../implementation/openxml-part-2.md) |
| TOC, fields, images, math and numbering | [OpenXML part 3](../implementation/openxml-part-3.md) |
| Watermarks and other behind-text figures | [Image anchoring samples](../../scripts/dotnet/Docx.Core/Samples/ImageSamples.cs) |

For reports built directly in C#, enable `WidowControl` on `Normal` and use the
bundled table/image helpers for standard pagination and WebP conversion.

## Validation and delivery

Validate the final DOCX:

```bash
bash "$SKILL_DIR/scripts/docx.sh" validate --input doc.docx --business
```

For DOCX-only delivery with no images or tables, skip rendering and visual
review unless the task requires visual verification. Follow
[rendering and delivery](validate.md#rendering-and-delivery) when applicable.
Confirm that the resulting content, citations and required structure match
the task.
