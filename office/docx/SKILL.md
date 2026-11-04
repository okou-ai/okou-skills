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

## Setup

Set `SKILL_DIR` to the absolute directory containing this file. All command paths
are relative to this directory, not the task's working directory.

First DOCX operation in the session:
`bash "$SKILL_DIR/scripts/env_check.sh"`. Reuse the working SDK and CLI afterward.
For permitted missing dependencies, use `scripts/setup.sh --minimal` (Windows:
`scripts/setup.ps1 -Minimal`). For PDF output, `.doc` conversion or requested
rendering, run `bash "$SKILL_DIR/scripts/env_check.sh" --with-rendering`; it probes
Writer with a real DOCX-to-PDF conversion. If needed and setup is allowed, run the
full setup script without the minimal flag. Do not equate a binary/version probe
with successful candidate rendering.

## Routing order: common → applicable profile → operation

1. For a **narrow EDIT** or **read-only** task, preserve existing presentation:
   use B for edits and preview/analyze for reading; never recreate or restyle
   merely because text mentions APA, 公文 or HBR.
2. Treat explicit user requirements and the supplied template as authoritative.
   If they conflict, clarify rather than silently replacing either with a recipe.
3. For **new creation or explicitly requested restyling**, select an applicable
   profile. Named-format rules override generic academic/business defaults, not
   the user's requirements or template.
4. Select A/B/C below. New content in a supplied structured template uses C-2
   Base-Replace; a simple fill remains B.

| Condition (within the authorized scope) | Read directly |
|---|---|
| Chinese government / 公文 / GB/T 9704 layout | [Government](references/domains/government.md) |
| Named paper: IEEE, ACM, APA, MLA, Chicago/Turabian, LNCS, Nature | [Academic](references/domains/academic.md) |
| Thesis/dissertation or supplied university template | [Thesis/template](references/domains/thesis-template.md) |
| Corporate report, executive brief, HBR or editorial presentation | [Business/editorial](references/domains/business-editorial.md) |
| Generic memo, letter or unspecified layout; narrow edit/read | No domain recipe required |

Profiles address structure/presentation, not research, government, legal or
business expertise or official certification. Adapt examples to the supplied
content; never copy sample findings, citations, agency identities or business
data. Samples are not CLI recipe selectors or publisher acceptance guarantees.

## Pipeline routing

| Task | Workflow |
|---|---|
| New document without a structured template | Pipeline A: [CREATE](references/operations/create.md) |
| Fill placeholders, replace text or edit authorized content | Pipeline B: [EDIT/FILL](references/operations/edit.md) |
| Authorized restyling with a pure style template | Pipeline C-1: [OVERLAY](references/operations/template.md) |
| New content within a structured cover/TOC/section template | Pipeline C-2: [BASE-REPLACE](references/operations/template.md) |
| Completed output or an affected change | [VALIDATE](references/operations/validate.md), including template gate-check when applicable |

For existing documents, preview and analyze before editing. Convert legacy `.doc`
only when needed; these entry points remain unchanged:

```bash
bash "$SKILL_DIR/scripts/doc_to_docx.sh" input.doc output_dir/
bash "$SKILL_DIR/scripts/docx_preview.sh" document.docx
bash "$SKILL_DIR/scripts/docx.sh" analyze --input document.docx
bash "$SKILL_DIR/scripts/docx.sh" --help
```

Simple CLI creation supports `report|letter|memo|academic`; `--type academic` is
not APA/IEEE selection. For custom styles, sections, TOC, images or complex
tables, read [authoring and sample patterns](references/implementation/authoring.md)
and the relevant actual C# sample before implementing. Compose operations only
as requested, then validate the completed file. For Word plus PDF, render that
DOCX rather than independently redesigning its companion.

## References by responsibility

Each format uses `references/common/`, `domains/`, `operations/` and
`implementation/`. Select only applicable guides; do not load the whole library.
For long guides, use their headings/contents or search for the needed element or
symptom. The operation owns the workflow, profiles own named requirements, and
implementation guides own SDK/package details. Executable and asset paths stay
under `scripts/` and `assets/`.

| Need | Direct reference |
|---|---|
| Fonts, sizes, page/table design | [Presentation](references/common/presentation.md) |
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
