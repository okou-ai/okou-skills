---
name: docx
license: MIT
metadata:
  version: "1.0.0"
  category: document-processing
  upstream: UPSTREAM.md
  sources:
    - "ECMA-376 Office Open XML File Formats"
    - "GB/T 9704-2012 Layout Standard for Official Documents"
    - "IEEE / ACM / APA / MLA / Chicago / Turabian Style Guides"
    - "Springer LNCS / Nature / HBR Document Templates"
description: >
  Create, read, edit, fill, and format editable Word documents (.docx / Word文档 / 文档)
  using OpenXML SDK (.NET). Use for reports/报告, proposals, memos, forms, contract
  formatting/合同, Chinese government documents/公文 (GB/T 9704), academic papers
  (IEEE, ACM, APA 7 professional, MLA 9, Chicago/Turabian, Springer LNCS, Nature),
  theses/学位论文 and supplied university templates, business/editorial formats
  (Modern Corporate, Executive Brief, HBR), 排版 and 套模板. Route creation,
  narrow content edits, or template application without assuming a restyle.
  Provides document structure and presentation guidance, not government-policy,
  research, or legal expertise or official certification. Use ../pdf/SKILL.md
  for a standalone PDF.
---

# Word documents

## Pipeline routing

| Task | Workflow |
|---|---|
| New document without a structured supplied template | Pipeline A: [CREATE](references/operations/create.md), using the CLI for supported blocks/options |
| Fill placeholders, replace text or edit authorized content | Pipeline B: [EDIT/FILL](references/operations/edit.md) |
| Read or analyze an existing document | Use preview/analyze below; preserve the file |
| Authorized restyling with a pure style template | Pipeline C-1: [OVERLAY](references/operations/template.md) |
| New content within a structured cover/TOC/section template | Pipeline C-2: [BASE-REPLACE](references/operations/template.md) |
| Completed output or an affected change | [VALIDATE](references/operations/validate.md) |

For DOCX-only delivery, validate the final file with the script and skip
rendering and visual review when it contains no images or tables and the
task does not require visual verification. Set `SKILL_DIR` as described
in [Setup](#setup) and run:

```bash
bash "$SKILL_DIR/scripts/docx.sh" validate --input doc.docx --document-rules
```

Follow the user's requirements and supplied template. Preserve existing
presentation for narrow edits and read-only work; a mention of APA, 公文 or HBR
does not by itself authorize restyling. Clarify conflicting requirements.

For a new report, letter, memo or generic academic document without a named
presentation, use the standard CLI route in CREATE and its validation guide.
A request for a report or proposal does not select a named business recipe.
Load additional presentation or SDK references only for requirements outside
that route.

## Setup

Set `SKILL_DIR` to the absolute directory containing this file. All command paths
are relative to this directory, not the task's working directory.

First DOCX operation in the session:
`bash "$SKILL_DIR/scripts/env_check.sh"`. Bash entrypoints reuse installed .NET;
a built CLI needs only the .NET 8 runtime.
For permitted missing authoring dependencies, use `scripts/setup.sh --minimal`
(Windows: `scripts/setup.ps1 -Minimal`).

When the [validation workflow](references/operations/validate.md#rendering-and-delivery)
calls for a PDF export or visual review, the rendering command
automatically provisions unavailable converters where installation is permitted.
To prepare them before authoring, optionally run
`python3 "$SKILL_DIR/scripts/render_docx.py" --prepare`.
Add `--pages qa/pages` when page images are needed. Render the validated DOCX
using the [rendering instructions](references/operations/validate.md#rendering-and-delivery).

## Named presentation profiles

Read a profile when the user requests its named format or supplies a template
that requires it. Apply those requirements before generic defaults; use the
operation selected above to preserve or create the required structure.

| Requested format | Read directly |
|---|---|
| Chinese government / 公文 / GB/T 9704 layout | [Government](references/domains/government.md) |
| IEEE, ACM, APA, MLA, Chicago/Turabian, LNCS, Nature | [Academic](references/domains/academic.md) |
| Thesis/dissertation or supplied university template | [Thesis/template](references/domains/thesis-template.md) |
| Modern Corporate, Executive Brief, Minimal Modern or HBR presentation | [Business/editorial](references/domains/business-editorial.md) |

Profiles address structure/presentation, not domain expertise or certification.
When a named profile or custom layout exceeds the CLI's supported blocks and
options, use the relevant [C# authoring pattern](references/implementation/authoring.md).
Adapt samples to the task; never copy their findings, citations or identities.

## Existing documents

Preview and analyze before editing. Convert legacy `.doc` only when needed:

```bash
bash "$SKILL_DIR/scripts/doc_to_docx.sh" input.doc output_dir/
bash "$SKILL_DIR/scripts/docx_preview.sh" document.docx
bash "$SKILL_DIR/scripts/docx.sh" analyze --input document.docx
```

## References by responsibility

Select only applicable guides; do not load the whole library. For long guides,
search for the needed element or symptom. Operations own the workflow, profiles
own named requirements, and implementation guides own SDK/package details.
Executable and asset paths stay under `scripts/` and `assets/`.

| Need | Direct reference |
|---|---|
| Custom fonts, sizes, page/table design | [Presentation](references/common/presentation.md) |
| CJK fonts, 字号, RunFonts and scoped GB/T layout | [CJK typography](references/common/cjk-typography.md) |
| Hierarchy, spacing, contrast and alignment | [Design principles](references/common/design-principles.md) |
| Visual mistakes and corrections | [Design examples](references/common/design-examples.md) |
| C# project scaffold, sample index and corruption-prevention rules | [Authoring](references/implementation/authoring.md) |
| Element ordering | [Element order](references/implementation/element-order.md) |
| DXA, EMU and half-point conversion | [Units](references/implementation/units.md) |
| XML namespace details | [Namespaces](references/implementation/namespaces.md) |
| Document creation, styles, runs and paragraphs | [OpenXML part 1](references/implementation/openxml-part-1.md) |
| Pages, tables, headers/footers and sections | [OpenXML part 2](references/implementation/openxml-part-2.md) |
| TOC, fields, revisions, comments, images, math and numbering | [OpenXML part 3](references/implementation/openxml-part-3.md) |
| Numeric thesis style IDs, zones and template preservation | [University templates](references/implementation/university-template.md) |
| Revision markup | [Track changes](references/implementation/track-changes.md) |
| Comment package parts | [Comments](references/implementation/comments.md) |
| Package/business/subset validation boundaries | [Validation details](references/implementation/validation.md) |
| Visible symptoms and targeted fixes | [Troubleshooting](references/implementation/troubleshooting.md) |
