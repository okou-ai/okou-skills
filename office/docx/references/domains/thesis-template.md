# Thesis and supplied-template presentation

Use for thesis/dissertation structure or an authorized template application.
Follow the entry's scope and precedence rules; ordinary placeholder filling
remains B, and narrow edits do not trigger template reconstruction.

## Supplied template first

For a Chinese university template, read the
[Chinese university guide](../implementation/university-template.md) and
[Scenario C](../operations/template.md). Inspect actual style IDs rather
than assuming `Heading1`: numeric `1/2/3/a` and custom names are common.

When creating body content within a template with cover/abstract/SDT-wrapped
TOC/chapters/back matter, choose **C-2 Base-Replace**, even for new user content.
Keep the template package as base. Identify replacement zones and update all
sample personal data, abstracts and references that are not the user's content;
preserving front-matter structure does not mean retaining sample prose. Preserve
section breaks, distinct zone headers/footers, Roman/Arabic page numbering,
TOC fields/SDTs, numbering and relationships. Map source styles to existing
template IDs. Keep necessary `w:eastAsia` and semantic emphasis during selective
cleanup; do not flatten paragraphs to text. Do not impose 公文's 28 pt spacing
on a thesis (templates often use 20/22 pt, but inspect the supplied file).

## No template supplied

Read [AestheticRecipeSamples.cs](../../scripts/dotnet/Docx.Core/Samples/AestheticRecipeSamples.cs),
method `CreateAcademicThesisDocument` in `AestheticRecipeSamples`, only as a
fallback long-form layout example. It is APA-style with a binding margin, not
a university compliance template or a substitute for the named APA professional
paper route. Adapt it in task-specific C#; do not copy its sample content.
Request university requirements if an institutional submission format is needed.

## Check

Compare template style IDs and effective EastAsia fonts, zone boundaries,
headers/footers, section geometry, page-number restarts and TOC preservation.
Run package validation and `--gate-check template.docx` for application, then
review the content diff. The gate compares only selected properties; it does
not certify university compliance or inspect every section/header/SDT.
