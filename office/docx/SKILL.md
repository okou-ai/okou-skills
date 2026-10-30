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
  Professional DOCX document creation, editing, and formatting using OpenXML SDK (.NET).
  Three pipelines: (A) create new documents from scratch, (B) fill/edit content in existing
  documents, (C) apply template formatting with template gate-check.
  MUST use this skill whenever the user wants to produce, modify, or format a Word document —
  including when they say "write a report", "draft a proposal", "make a contract",
  "fill in this form", "reformat to match this template", or any task whose final output
  is a .docx file. Even if the user doesn't mention "docx" explicitly, if the task
  implies an editable Word document, use this skill. Use ../pdf/SKILL.md for a standalone PDF.
triggers:
  - Word
  - docx
  - document
  - 文档
  - Word文档
  - 报告
  - 合同
  - 公文
  - 排版
  - 套模板
---

# docx

Create, edit, and format DOCX documents via CLI tools or direct C# scripts built on OpenXML SDK (.NET).

## Setup

Paths below are relative to this skill directory. Set `SKILL_DIR` to the absolute
directory containing this file; do not assume the task's working directory.

**First operation in session:** `bash "$SKILL_DIR/scripts/env_check.sh"`.
This checks DOCX authoring dependencies.
If required dependencies are missing, run
`bash "$SKILL_DIR/scripts/setup.sh" --minimal` (Windows:
`powershell -File "$SKILL_DIR/scripts/setup.ps1" -Minimal`).
Reuse the installed SDK and built CLI for subsequent operations.

For PDF output, `.doc` conversion, or a user-requested rendered preview or visual
review, run `bash "$SKILL_DIR/scripts/env_check.sh" --with-rendering`. This probes
Writer by converting a minimal DOCX to PDF. If that probe fails, run the full
`setup.sh` (Windows: `setup.ps1`) without the minimal flag.

## Quick Start: Direct C# Path

When the task requires structural document manipulation (custom styles, complex tables, multi-section layouts, headers/footers, TOC, images), write C# directly instead of wrestling with CLI limitations. Use this scaffold:

Create a regular console project once, referencing the bundled SDK project:

```bash
dotnet new console --framework net8.0 --output generated/docx-task
dotnet add generated/docx-task reference "$SKILL_DIR/scripts/dotnet/Docx.Core/Docx.Core.csproj"
# Put the C# below in generated/docx-task/Program.cs.
dotnet run --project generated/docx-task
```

```csharp
using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;

using var doc = WordprocessingDocument.Create("output.docx", WordprocessingDocumentType.Document);
var mainPart = doc.AddMainDocumentPart();
mainPart.Document = new Document(new Body());

// --- Your logic here ---
// Read the relevant Samples/*.cs file FIRST for tested patterns.
// See Samples/ table in References section below.
```

**Before writing any C#, read the relevant `Samples/*.cs` file** — they contain compilable, SDK-version-verified patterns. The Samples table in the References section below maps topics to files.

## CLI entry point

The wrapper uses the built CLI without rebuilding on every call:
```bash
bash "$SKILL_DIR/scripts/docx.sh" --help
```

## Pipeline routing

Route by checking: does the user have an input .docx file?

```
User task
├─ No input file → Pipeline A: CREATE
│   signals: "write", "create", "draft", "generate", "new", "make a report/proposal/memo"
│   → Read references/scenario_a_create.md
│
└─ Has input .docx
    ├─ Replace/fill/modify content → Pipeline B: FILL-EDIT
    │   signals: "fill in", "replace", "update", "change text", "add section", "edit"
    │   → Read references/scenario_b_edit_content.md
    │
    └─ Reformat/apply style/template → Pipeline C: FORMAT-APPLY
        signals: "reformat", "apply template", "restyle", "match this format", "套模板", "排版"
        ├─ Template is pure style (no content) → C-1: OVERLAY (apply styles to source)
        └─ Template has structure (cover/TOC/example sections) → C-2: BASE-REPLACE
            (use template as base, replace example content with user content)
        → Read references/scenario_c_apply_template.md
```

If the request spans multiple pipelines, run them sequentially (e.g., Create then Format-Apply).

## Pre-processing

Convert `.doc` → `.docx` if needed: `bash "$SKILL_DIR/scripts/doc_to_docx.sh" input.doc output_dir/`

Preview before editing (avoids reading raw XML): `bash "$SKILL_DIR/scripts/docx_preview.sh" document.docx`

Analyze structure for editing scenarios: `bash "$SKILL_DIR/scripts/docx.sh" analyze --input document.docx`

## Scenario A: Create

Read `references/scenario_a_create.md`, then the selected recipe and the samples
needed for this document. Read typography/design references when making those
decisions, and `references/cjk_typography.md` for CJK. Load relevant sections,
not the entire sample library. User-supplied templates and explicit style choices
take precedence over recipe defaults; HBR's 11 pt body text must not be changed
to satisfy an unrelated 12 pt default.

**Choose your path:**
- **Simple** (plain text, minimal formatting): use CLI — `bash "$SKILL_DIR/scripts/docx.sh" create --type report --output out.docx --content-json content.json`
- **Structural** (custom styles, multi-section, TOC, images, complex tables): write C# directly. Read the relevant `Samples/*.cs` first.

CLI options: `--type` (report|letter|memo|academic), `--title`, `--author`, `--page-size` (letter|a4|legal|a3), `--margins` (standard|narrow|wide), `--header`, `--footer`, `--page-numbers`, `--toc`, `--content-json`.

Then run the **validation pipeline** (below).

## Scenario B: Edit / Fill

Read `references/scenario_b_edit_content.md` first. Preview → analyze → edit → validate.

**Choose your path:**
- **Simple** (text replacement, placeholder fill): use CLI subcommands.
- **Structural** (add/reorganize sections, modify styles, manipulate tables, insert images): write C# directly. Read `references/openxml_element_order.md` and the relevant `Samples/*.cs`.

Available CLI edit subcommands:
- `replace-text --search "X" --replace "Y"`
- `fill-placeholders --mapping values.json`
- `fill-table --csv table.csv`
- `insert-paragraph`, `update-field`, `list-placeholders`

```bash
bash "$SKILL_DIR/scripts/docx.sh" edit replace-text --input in.docx --output out.docx --search "OLD" --replace "NEW"
bash "$SKILL_DIR/scripts/docx.sh" edit fill-placeholders --input in.docx --output out.docx --mapping values.json
```

Then run the **validation pipeline**. Also run diff to verify minimal changes:
```bash
bash "$SKILL_DIR/scripts/docx.sh" diff --before in.docx --after out.docx
```

## Scenario C: Apply Template

Read `references/scenario_c_apply_template.md` first. Preview and analyze both source and template.

```bash
bash "$SKILL_DIR/scripts/docx.sh" apply-template --input source.docx --template template.docx --output out.docx
```

For complex template operations (multi-template merge, per-section headers/footers, style merging), write C# directly — see Critical Rules below for required patterns.

Run the **validation pipeline**, then the **hard gate-check**:
```bash
bash "$SKILL_DIR/scripts/docx.sh" validate --input out.docx --gate-check template.docx
```
Gate-check is a **hard requirement**. Do NOT deliver until it passes. If it fails: diagnose, fix, re-run.

Also diff to verify content preservation: `bash "$SKILL_DIR/scripts/docx.sh" diff --before source.docx --after out.docx`

## Validation pipeline

Run on the completed document, and again after changes that affect it.

```bash
bash "$SKILL_DIR/scripts/docx.sh" validate --input doc.docx --business
```

`validate` always runs the OpenXML SDK validator on all package parts. It checks
structure and relationships without forcing a particular font size or recipe.

The bundled `wml-subset.xsd` is an optional check of a curated subset, not full
OOXML coverage. Use `--xsd "$SKILL_DIR/assets/xsd/wml-subset.xsd"` only for documents
intentionally restricted to that subset. A schema limitation is not permission
to remove valid document features. Do not replace a failed package check with
a text preview. Repair the reported defect, then rerun the affected validation.

Use `fix-order` only for diagnosed ordering errors and `merge-runs` only when
consolidation is needed; do not mutate a document as a routine validation step.

### PDF export and visual review

When delivering a PDF version of a Word document, export that DOCX once:

```bash
python3 "$SKILL_DIR/scripts/render_docx.py" doc.docx --out output/doc.pdf
```

For a user-requested rendered preview or visual review, add
`--pages preview/pages` and inspect the images.

## Critical rules

These prevent file corruption — OpenXML is strict about element ordering.

**Element order** (properties always first):

| Parent | Order |
|--------|-------|
| `w:p`  | `pPr` → runs |
| `w:r`  | `rPr` → `t`/`br`/`tab` |
| `w:tbl`| `tblPr` → `tblGrid` → `tr` |
| `w:tr` | `trPr` → `tc` |
| `w:tc` | `tcPr` → `p` (min 1 `<w:p/>`) |
| `w:body` | block content → `sectPr` (LAST child) |

**Direct format contamination:** When copying content from a source document, inline `rPr` (fonts, color) and `pPr` (borders, shading, spacing) override template styles. Always strip direct formatting — keep only `pStyle` reference and `t` text. Clean tables too (including `pPr/rPr` inside cells).

**Track changes:** `<w:del>` uses `<w:delText>`, never `<w:t>`. `<w:ins>` uses `<w:t>`, never `<w:delText>`.

**Font size:** `w:sz` = points × 2 (12pt → `sz="24"`). Margins/spacing in DXA (1 inch = 1440, 1cm ≈ 567).

**Heading styles MUST have OutlineLevel:** When defining heading styles (Heading1, ThesisH1, etc.), always include `new OutlineLevel { Val = N }` in `StyleParagraphProperties` (H1→0, H2→1, H3→2). Without this, Word sees them as plain styled text — TOC and navigation pane won't work.

**Multi-template merge:** When given multiple template files (font, heading, breaks), read `references/scenario_c_apply_template.md` section "Multi-Template Merge" FIRST. Key rules:
- Merge styles from all templates into one styles.xml. Structure (sections/breaks) comes from the breaks template.
- Each content paragraph must appear exactly ONCE — never duplicate when inserting section breaks.
- NEVER insert empty/blank paragraphs as padding or section separators. Output paragraph count must equal input. Use section break properties (`w:sectPr` inside `w:pPr`) and style spacing (`w:spacing` before/after) for visual separation.
- Insert oddPage section breaks before EVERY chapter heading, not just the first. Even if a chapter has dual-column content, it MUST start with oddPage; use a second continuous break after the heading for column switching.
- Dual-column chapters need THREE section breaks: (1) oddPage in preceding para's pPr, (2) continuous+cols=2 in the chapter HEADING's pPr, (3) continuous+cols=1 in the last body para's pPr to revert.
- Copy `titlePg` settings from the breaks template for EACH section. Abstract and TOC sections typically need `titlePg=true`.

**Multi-section headers/footers:** Templates with 10+ sections (e.g., Chinese thesis) have DIFFERENT headers/footers per section (Roman vs Arabic page numbers, different header text per zone). Rules:
- Use C-2 Base-Replace: copy the TEMPLATE as output base, then replace body content. This preserves all sections, headers, footers, and titlePg settings automatically.
- NEVER recreate headers/footers from scratch — copy template header/footer XML byte-for-byte.
- NEVER add formatting (borders, alignment, font size) not present in the template header XML.
- Non-cover sections MUST have header/footer XML files (at least empty header + page number footer).
- See `references/scenario_c_apply_template.md` section "Multi-Section Header/Footer Transfer".

## References

Load as needed — don't load all at once. Pick the most relevant files for the task.

**The C# samples and design references below are the project's knowledge base ("encyclopedia").** When writing OpenXML code, ALWAYS read the relevant sample file first — it contains compilable, SDK-version-verified patterns that prevent common errors. When making aesthetic decisions, read the design principles and recipe files — they encode tested, harmonious parameter sets from authoritative sources (IEEE, ACM, APA, Nature, etc.), not guesses.

### Scenario guides (read first for each pipeline)

| File | When |
|------|------|
| `references/scenario_a_create.md` | Pipeline A: creating from scratch |
| `references/scenario_b_edit_content.md` | Pipeline B: editing existing content |
| `references/scenario_c_apply_template.md` | Pipeline C: applying template formatting |

### C# code samples (compilable, heavily commented — read when writing code)

| File | Topic |
|------|-------|
| `Samples/DocumentCreationSamples.cs` | Document lifecycle: create, open, save, streams, doc defaults, settings, properties, page setup, multi-section |
| `Samples/StyleSystemSamples.cs` | Styles: Normal/Heading chain, character/table/list styles, DocDefaults, latentStyles, CJK 公文, APA 7th, import, resolve inheritance |
| `Samples/CharacterFormattingSamples.cs` | RunProperties: fonts, size, bold/italic, all underlines, color, highlight, strike, sub/super, caps, spacing, shading, border, emphasis marks |
| `Samples/ParagraphFormattingSamples.cs` | ParagraphProperties: justification, indentation, line/paragraph spacing, keep/widow, outline level, borders, tabs, numbering, bidi, frame |
| `Samples/TableSamples.cs` | Tables: borders, grid, cell props, margins, row height, header repeat, merge (H+V), nested, floating, three-line 三线表, zebra striping |
| `Samples/HeaderFooterSamples.cs` | Headers/footers: page numbers, "Page X of Y", first/even/odd, logo image, table layout, 公文 "-X-", per-section |
| `Samples/ImageSamples.cs` | Images: inline, floating, text wrapping, border, alt text, in header/table, replace, SVG fallback, dimension calc |
| `Samples/ListAndNumberingSamples.cs` | Numbering: bullets, multi-level decimal, custom symbols, outline→headings, legal, Chinese 一/（一）/1./(1), restart/continue |
| `Samples/FieldAndTocSamples.cs` | Fields: TOC, SimpleField vs complex field, DATE/PAGE/REF/SEQ/MERGEFIELD/IF/STYLEREF, TOC styles |
| `Samples/FootnoteAndCommentSamples.cs` | Footnotes, endnotes, comments (4-file system), bookmarks, hyperlinks (internal + external) |
| `Samples/TrackChangesSamples.cs` | Revisions: insertions (w:t), deletions (w:delText!), formatting changes, accept/reject all, move tracking |
| `Samples/AestheticRecipeSamples.cs` | 13 aesthetic recipes from authoritative sources: ModernCorporate, AcademicThesis, ExecutiveBrief, ChineseGovernment (GB/T 9704), MinimalModern, IEEE Conference, ACM sigconf, APA 7th, MLA 9th, Chicago/Turabian, Springer LNCS, Nature, HBR — each with exact values from official style guides |

Note: `Samples/` path is relative to `scripts/dotnet/Docx.Core/`.

### Markdown references (read when you need specifications or design rules)

| File | When |
|------|------|
| `references/openxml_element_order.md` | XML element ordering rules (prevents corruption) |
| `references/openxml_units.md` | Unit conversion: DXA, EMU, half-points, eighth-points |
| `references/openxml_encyclopedia_part1.md` | Detailed C# encyclopedia: document creation, styles, character & paragraph formatting |
| `references/openxml_encyclopedia_part2.md` | Detailed C# encyclopedia: page setup, tables, headers/footers, sections, doc properties |
| `references/openxml_encyclopedia_part3.md` | Detailed C# encyclopedia: TOC, footnotes, fields, track changes, comments, images, math, numbering, protection |
| `references/typography_guide.md` | Font pairing, sizes, spacing, page layout, table design, color schemes |
| `references/cjk_typography.md` | CJK fonts, 字号 sizes, RunFonts mapping, GB/T 9704 公文 standard |
| `references/cjk_university_template_guide.md` | Chinese university thesis templates: numeric styleIds (1/2/3 vs Heading1), document zone structure (cover→abstract→TOC→body→references), font expectations, common mistakes |
| `references/design_principles.md` | **Aesthetic foundations**: 6 design principles (white space, contrast/scale, proximity, alignment, repetition, hierarchy) — teaches WHY, not just WHAT |
| `references/design_good_bad_examples.md` | **Good vs Bad comparisons**: 10 categories of typography mistakes with OpenXML values, ASCII mockups, and fixes |
| `references/track_changes_guide.md` | Revision marks deep dive |
| `references/troubleshooting.md` | **Symptom-driven fixes**: 13 common problems indexed by what you SEE (headings wrong, images missing, TOC broken, etc.) — search by symptom, find the fix |
