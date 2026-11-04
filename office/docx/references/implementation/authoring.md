# DOCX authoring and package invariants

Use for direct C# structural work after selecting the requested
[operation](../../SKILL.md#pipeline-routing). Read the relevant actual sample
method first, adapt it to the supplied content and compile the adaptation.
Examples and recipes do not certify a document or implement new CLI flags.

## Contents

- [Project scaffold](#project-scaffold)
- [Sample index](#sample-index)
- [Package invariants](#package-invariants)
- [Structured template boundaries](#structured-template-boundaries)

## Project scaffold

Reference the bundled SDK project from a regular console project:

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
// Add task-specific content using the selected sample's current SDK patterns.
```

For simple operations, use the existing `scripts/docx.sh --help`; do not rebuild
the CLI on every call or invent named-recipe selectors.

## Sample index

Paths below point to the actual bundled C# sources under
`scripts/dotnet/Docx.Core/Samples/`. Read only relevant methods. Recipe source
comments describe assumptions; verify named requirements independently. HBR is
an analysis-derived published-format approximation, not an official HBR template.

| Source | Topics |
|---|---|
| [DocumentCreationSamples.cs](../../scripts/dotnet/Docx.Core/Samples/DocumentCreationSamples.cs) | Create/open/save, streams, defaults, settings, properties, pages, sections |
| [StyleSystemSamples.cs](../../scripts/dotnet/Docx.Core/Samples/StyleSystemSamples.cs) | Style inheritance, character/table/list styles, DocDefaults, CJK, APA, import |
| [CharacterFormattingSamples.cs](../../scripts/dotnet/Docx.Core/Samples/CharacterFormattingSamples.cs) | Fonts, size, emphasis, underline, color, shading, borders, scripts |
| [ParagraphFormattingSamples.cs](../../scripts/dotnet/Docx.Core/Samples/ParagraphFormattingSamples.cs) | Alignment, indentation, spacing, keep/widow, outline, tabs, bidi, frames |
| [TableSamples.cs](../../scripts/dotnet/Docx.Core/Samples/TableSamples.cs) | Grids, borders, margins, row heights, repeat headers, merges, nested/floating tables |
| [HeaderFooterSamples.cs](../../scripts/dotnet/Docx.Core/Samples/HeaderFooterSamples.cs) | First/even/odd and per-section headers, logos, page fields, 公文 numbering |
| [ImageSamples.cs](../../scripts/dotnet/Docx.Core/Samples/ImageSamples.cs) | Inline/floating images, wrapping, dimensions, alt text, replacement, SVG fallback |
| [ListAndNumberingSamples.cs](../../scripts/dotnet/Docx.Core/Samples/ListAndNumberingSamples.cs) | Bullets, outline/legal/Chinese numbering, restart and continuation |
| [FieldAndTocSamples.cs](../../scripts/dotnet/Docx.Core/Samples/FieldAndTocSamples.cs) | TOC, field types, DATE/PAGE/REF/SEQ/MERGEFIELD/IF/STYLEREF |
| [FootnoteAndCommentSamples.cs](../../scripts/dotnet/Docx.Core/Samples/FootnoteAndCommentSamples.cs) | Notes, four-part comments, bookmarks and hyperlinks |
| [TrackChangesSamples.cs](../../scripts/dotnet/Docx.Core/Samples/TrackChangesSamples.cs) | Insertions, deletions, formatting revisions, moves, accept/reject |
| [AestheticRecipeSamples.cs](../../scripts/dotnet/Docx.Core/Samples/AestheticRecipeSamples.cs) | Modern Corporate, Academic Thesis, Executive Brief, Chinese Government, Minimal Modern |
| [AestheticRecipeSamples_Batch1.cs](../../scripts/dotnet/Docx.Core/Samples/AestheticRecipeSamples_Batch1.cs) | IEEE and ACM conference recipes |
| [AestheticRecipeSamples_Batch2.cs](../../scripts/dotnet/Docx.Core/Samples/AestheticRecipeSamples_Batch2.cs) | APA 7 professional and MLA 9 recipes |
| [AestheticRecipeSamples_Batch3.cs](../../scripts/dotnet/Docx.Core/Samples/AestheticRecipeSamples_Batch3.cs) | Chicago/Turabian and Springer LNCS recipes |
| [AestheticRecipeSamples_Batch4.cs](../../scripts/dotnet/Docx.Core/Samples/AestheticRecipeSamples_Batch4.cs) | Nature and analysis-derived HBR recipes |

## Package invariants

OpenXML ordering is significant; properties precede their content:

| Parent | Order |
|---|---|
| `w:p` | `pPr` → runs |
| `w:r` | `rPr` → `t`/`br`/`tab` |
| `w:tbl` | `tblPr` → `tblGrid` → `tr` |
| `w:tr` | `trPr` → `tc` |
| `w:tc` | `tcPr` → `p`, including at least one paragraph |
| `w:body` | Block content → final `sectPr` |

Read [element order](element-order.md) for details. Font sizes use half-points:
`w:sz` is points × 2. DXA uses 1440 per inch (about 567 per cm); see
[units](units.md). A heading style needs `OutlineLevel` in
`StyleParagraphProperties` (H1→0, H2→1, H3→2), not merely larger/bold text, for
Word navigation and TOC. In revisions, `<w:del>` requires `<w:delText>` and
`<w:ins>` requires `<w:t>`; see [track changes](track-changes.md).

When applying a template, remove only unwanted source overrides. Retain necessary
`w:eastAsia` declarations or transfer them into mapped styles; preserve semantic
emphasis, numbering, fields, relationships and intentional section structure.
Use [selective cleanup](../operations/template.md#direct-formatting-cleanup-rules-detailed),
not blanket removal or conversion to plain text.

## Structured template boundaries

Begin with [TEMPLATE's workflow](../operations/template.md#workflow) and
[structure analysis](../operations/template.md#template-structure-analysis-required).
For multi-template composition, retain these safeguards. They are not a bundled
end-to-end multi-template merge procedure; adapt the relevant SDK samples and
verify each section and relationship explicitly:

- Merge styles from all supplied templates; take sections/breaks from the selected
  structure template. Retain each content paragraph exactly once.
- Do not add blank paragraphs as section padding. Preserve input paragraph count
  and use section properties plus paragraph/style spacing.
- For the documented chapter layout, place oddPage breaks before each chapter.
  Two-column chapters need the preceding oddPage break, a continuous two-column
  switch in the heading and a continuous one-column reset after the body.
- Copy the template's `titlePg` setting for each section, including abstract/TOC.

For a structured thesis with different section headers, footers or page-number
schemes, use C-2 Base-Replace rather than rebuilding the document. Preserve the
template header/footer XML byte-for-byte and do not invent borders, alignment or
sizes. Retain the section-specific parts, including the documented non-cover
header and page-number footer, and their relationship targets. Review
[relationship remapping](../operations/template.md#relationship-id-remapping),
[section-property conflicts](../operations/template.md#3-section-property-conflicts)
and [university-template details](university-template.md). No dedicated automatic
header/footer-transfer procedure or all-section template gate is supplied here;
compare each section and its linked header/footer parts against the template.
Validate and diff after structural changes; these invariants are not an
alternative acceptance check.
