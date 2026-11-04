# Named academic paper presentation

Use for requested paper formatting, not research, citation verification or
publisher acceptance. Apply the entry's scope/precedence rules; a narrow edit
of an APA/IEEE document stays B and does not rebuild its presentation.

## Select the actual bundled method

All methods belong to the partial class `AestheticRecipeSamples`. Read only the
selected method and relevant helpers; adapt layout to supplied content. These
methods write complete sample documents, including invented example text and
references. Do not deliver their sample content or call them as content-fill APIs.

| Requested format | Actual source | Method |
|---|---|---|
| IEEE conference | [Batch1](../../scripts/dotnet/Docx.Core/Samples/AestheticRecipeSamples_Batch1.cs) | `CreateIEEEConferenceDocument` |
| ACM conference / sigconf | [Batch1](../../scripts/dotnet/Docx.Core/Samples/AestheticRecipeSamples_Batch1.cs) | `CreateACMConferenceDocument` |
| APA 7 professional paper | [Batch2](../../scripts/dotnet/Docx.Core/Samples/AestheticRecipeSamples_Batch2.cs) | `CreateAPA7Document` |
| MLA 9 | [Batch2](../../scripts/dotnet/Docx.Core/Samples/AestheticRecipeSamples_Batch2.cs) | `CreateMLA9Document` |
| Chicago / Turabian | [Batch3](../../scripts/dotnet/Docx.Core/Samples/AestheticRecipeSamples_Batch3.cs) | `CreateChicagoTurabianDocument` |
| Springer LNCS | [Batch3](../../scripts/dotnet/Docx.Core/Samples/AestheticRecipeSamples_Batch3.cs) | `CreateSpringerLNCSDocument` |
| Nature journal | [Batch4](../../scripts/dotnet/Docx.Core/Samples/AestheticRecipeSamples_Batch4.cs) | `CreateNatureJournalDocument` |

`create --type academic` is a generic font-default choice, **not** APA/IEEE
selection and not a loader for `assets/styles/academic_styles.xml`. There is no
named-format CLI flag; use the direct C# path. Generic heading-size defaults
must not overwrite a selected named recipe. For a thesis/university template,
use the entry's thesis/template route instead of assuming a publication format.

## Review against the requested publication instructions

Bundled recipe comments are starting points, not independently verified current
submission rules. Distinguish a published-page approximation (notably Nature)
from a manuscript/submission template. Ask for the target venue's instructions
when material requirements are unspecified; supplied instructions govern.

- IEEE/ACM: check column count, gutter, body/caption sizes, heading hierarchy,
  numbering and reference layout against the selected method and target format.
- APA 7 professional: the bundled TNR choice is 12 pt with double spacing,
  0.5-inch body indent, unindented abstract, all-12-pt headings distinguished by
  alignment/bold/italic, no numbered headings, top-right page numbers and an
  uppercase left running head. Check title-page fields: adapt professional
  author/affiliation/author-note content; remove student course/instructor/date
  placeholders from the sample. Do not treat professional and student papers
  as interchangeable.
- MLA: check first-page identification, surname/page header and Works Cited
  hanging indents; Chicago/Turabian: check notes and heading distinctions;
  LNCS/Nature: check title/abstract/body section transitions and captions.

Use only supplied or verified reference metadata; report missing sources instead
of fabricating citations, findings or authors. Compare effective styles/section
properties separately from package validation. Package validation and
`--business` do not certify APA, IEEE or another publication standard.
