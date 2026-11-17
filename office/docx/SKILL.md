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
  with stdlib read/inspection and OpenXML SDK (.NET) authoring. Use for reports/报告, proposals, memos, forms, contract
  formatting/合同, Chinese government documents/公文 (GB/T 9704), academic papers
  (IEEE, ACM, APA 7 professional, MLA 9, Chicago/Turabian, Springer LNCS, Nature),
  theses/学位论文 and supplied university templates, business/editorial formats
  (Modern Corporate, Executive Brief, HBR), 排版 and 套模板. Route creation,
  narrow content edits, or template application without assuming a restyle.
  Named profiles guide presentation, not official standards certification. Use
  ../pdf/SKILL.md for a standalone PDF.
---

# Word documents

## Pipeline routing

| Task | Workflow |
|---|---|
| New document without a structured supplied template | Pipeline A: [CREATE](references/operations/create.md), using the CLI for supported blocks/options |
| Fill placeholders, replace text or edit authorized content | Pipeline B: [EDIT/FILL](references/operations/edit.md) |
| Read content / answer text questions | Stdlib preview below; no setup, .NET, structural scan or render |
| Inspect styles, sections or template/edit targets | Stdlib inventory once per input; reuse it |
| Authorized restyling with a pure style template | Pipeline C-1: [OVERLAY](references/operations/template.md) |
| New content within a structured cover/TOC/section template | Pipeline C-2: [BASE-REPLACE](references/operations/template.md) |
| Completed output or an affected change | [VALIDATE](references/operations/validate.md) |

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

Check only the selected operation's dependencies:

- **Read text / inspect:** Python 3 standard library only; skip `env_check`, setup,
  SDK and rendering. The commands below never modify the source.
- **Execute CLI create/edit/template/validate:** once per session, run
  `bash "$SKILL_DIR/scripts/env_check.sh"`. A prebuilt CLI needs only .NET 8 runtime;
  entrypoints rediscover it in fresh shells without editing shell profiles.
- **Build missing CLI / custom C# authoring:** SDK is required here only. With an
  installed SDK, use `env_check.sh --build`; for permitted missing dependencies,
  use `scripts/setup.sh --minimal` (Windows: `scripts/setup.ps1 -Minimal`).
- **Requested PDF or rendered QA:** use the task-local prepare/receipt commands in
  [VALIDATE](references/operations/validate.md#rendering-and-delivery) before
  authoring. Reuse that successful capability check for the candidate; do not also
  run `env_check.sh --with-rendering` or another standalone probe. No render for reads.

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

When a named profile or custom layout exceeds the CLI's supported blocks and
options, use the relevant [C# authoring pattern](references/implementation/authoring.md).
Adapt samples to the task; never copy their findings, citations or identities.

## Existing documents

Read only what the task needs; preserve the source:

```bash
# Content-only: complete stored body text, not rendered pagination/lossless extraction.
bash "$SKILL_DIR/scripts/docx_preview.sh" document.docx
# Optional: non-body text, explicitly separated from the body (or --part footnotes).
bash "$SKILL_DIR/scripts/docx_preview.sh" document.docx --part all
# Only when structure/styles/edit targets are needed: one reusable JSON inventory.
python3 "$SKILL_DIR/scripts/docx_inspect.py" inventory document.docx > document.inventory.json
```

Inventory defaults to bounded body previews, complete style/section/relationship
metadata and cheap part names/sizes; it does not read media/binary parts. Observe
its `body_coverage` and truncation markers. Choose range/full text, XML or member
hashes only when needed, using the [inspection contract](references/implementation/inspection.md)
or `inventory --help`; reuse the saved input inventory across stages. Presence
checks/hashes do not replace package or actual-output QA; printed XML is for
inspection, not byte-preserving repacking.
Convert legacy `.doc` only when necessary via
`bash "$SKILL_DIR/scripts/doc_to_docx.sh" input.doc output_dir/` (needs Writer).

Read-only work stops after answering the question. For authored/edited output,
validate the candidate package, check authorized content/preservation, and repeat
only affected checks. Render when pagination/layout changed or requested output
needs visual QA; text-only edits can also reflow, so assess their impact first.

## References by responsibility

Load only the operation and relevant named profile/element/symptom; optional design
references below are not prerequisites for a standard CLI document or narrow edit.

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
