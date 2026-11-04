# Business and editorial presentation

Use for requested visual/structural business formats, not business analysis
expertise. Apply the entry's scope and precedence rules before selecting a recipe.
A generic memo needs no named recipe; use A and explicit CLI geometry/options
or task-specific C# rather than loading an editorial profile unnecessarily.

| Requested presentation | Actual source | Method in `AestheticRecipeSamples` |
|---|---|---|
| Modern Corporate report/proposal | [Base](../../scripts/dotnet/Docx.Core/Samples/AestheticRecipeSamples.cs) | `CreateModernCorporateDocument` |
| Executive Brief / board summary | [Base](../../scripts/dotnet/Docx.Core/Samples/AestheticRecipeSamples.cs) | `CreateExecutiveBriefDocument` |
| Minimal Modern / creative brief | [Base](../../scripts/dotnet/Docx.Core/Samples/AestheticRecipeSamples.cs) | `CreateMinimalModernDocument` |
| HBR-style article/brief | [Batch4](../../scripts/dotnet/Docx.Core/Samples/AestheticRecipeSamples_Batch4.cs) | `CreateHBRStyleDocument` |

Read the selected method, then adapt its layout in task-specific C#. Methods
create sample documents, not content-fill APIs; replace every sample claim,
quote, table, source and author with supplied/verified content. Do not invent
CLI recipe flags. Generic CLI report/memo defaults do not implement these recipes.

For HBR, retain the chosen 11 pt Georgia body, block paragraphs (no first-line
indent), 1.3 spacing, “Exhibit” labels, pull-quote treatment and minimal numbering
unless the user's instructions/template say otherwise. Never change it to an
unrelated 12 pt academic default. HBR here is **analysis-derived from published
formatting**, not an official HBR template or a promise of publication acceptance.
Use pull quotes only from actual supplied text; do not manufacture evidence.

Check the selected type scale, paragraph spacing, table labels, headers/footers
and section geometry. Keep content/metadata intact. Package/business validation
is separate from visual/profile review and is not domain certification.
