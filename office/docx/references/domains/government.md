# Chinese government document presentation (公文)

Use for authorized creation or reformatting toward GB/T 9704-2012 layout, not
for policy drafting expertise. Apply the entry's scope and precedence rules first.

## Read and adapt

- Read [CJK typography](../common/cjk-typography.md), especially `GB/T 9704`.
- Read [AestheticRecipeSamples.cs](../../scripts/dotnet/Docx.Core/Samples/AestheticRecipeSamples.cs),
  method `CreateChineseGovernmentDocument` in `AestheticRecipeSamples`.
- Adapt that method's layout in task-specific C#; it creates demonstration content,
  not a production document from user input. No government CLI selector exists.

## Resolve the letterhead conflict

The CJK reference describes red agency elements; the sample is an all-black,
undecorated layout. Scope red agency name/separator/seal elements to the **actual
supplied formal letterhead**. Preserve those supplied elements when applying it;
do not invent an official seal, issuance number (发文字号), agency identity or
approval. If formal letterhead is required but unavailable, request it rather
than manufacture it. An all-black simulation is permitted when appropriate to
the request, with explicit disclosure that it is a simulation without formal
letterhead, not an officially certified document. This scope governs the older
reference's blanket color language; retain its underlying typography guidance.

## Check the selected layout separately

For the bundled no-template layout, check A4 `11906 × 16838` DXA; margins
T/B/L/R `2098/1984/1588/1474`; 仿宋_GB2312 body 16 pt; centered title 22 pt;
exact 28 pt lines (`line=560`); distinct 黑体/楷体/仿宋 heading levels;
Chinese outline numbering and dash-surrounded page numbers. Record unavailable
fonts/substitutions. With a supplied template, check its actual requirements
instead. Review text and supplied metadata for accidental sample leakage.
Package/business validation is not proof of full GB/T compliance or authority.
