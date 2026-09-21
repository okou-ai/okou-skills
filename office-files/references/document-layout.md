# General document layout

These are product defaults and review criteria, not a universal aesthetic
standard. Explicit user requirements and supplied templates take precedence.
Do not change source facts or required wording to improve page geometry.

## Establish constraints, not a genre

Determine the output format, language/direction, whether source layout must be
preserved, fixed-position elements, exact wording/fields, changing-length lists
or tables, and calculated values. These properties can coexist. They do not
require a user-facing category picker or a fixed document-type enumeration.

Choose a native Word/PDF tool when the structure or layout needs it. The optional
Pandoc prose route creates a reference from Pandoc's style set, applies the
maintained theme, and exports the final Word file to PDF. Other authoring routes
use the same page checks without adopting that theme or a Markdown intermediate.
For existing files/templates, preserve their dimensions, style and content
contract. A single theme is not a replacement for a form or a designed page.

## Default visual language

The optional Pandoc foundation uses a warm editorial-paper system: restrained ink-blue,
warm neutrals, serif display hierarchy, sans body text, hairline rules and
print-safe tables. It is intentionally brand-neutral and avoids generic UI
cards, gradients and heavy decoration. Authors still decide the opening focal
point, information grouping and page rhythm. Native authoring may define a
different coherent visual direction directly in code or a template. Read
`editorial-patterns.md` when using the maintained Markdown components.

Do not force this visual language onto a user reference, an existing Word file,
a form or a native PDF template. A theme can make consistent typography; it
cannot decide which conclusion deserves the page or repair a poor information
sequence.

## Text and hierarchy

Use the theme's body/heading/list/caption styles rather than formatting each
paragraph individually. Keep emphasis selective; a bold callout under every
heading competes with the headings. Avoid a mandatory cover, executive summary,
coloured callout, conclusion or repeated source paragraph on every page.

Set the document language explicitly when regional glyph forms matter:
`zh-CN`/`zh-Hans`, `zh-TW`/`zh-Hant`, `ja-JP`, `ko-KR`. Arabic/Hebrew need correct
direction, shaping and complex-script fonts, including mixed Latin identifiers
and numerals. The helper's language inference is only a fallback; do not infer
Traditional versus Simplified Chinese from Han characters alone.

Default sizes and spacing favour reading at ordinary page scale. Table and
caption text can be smaller than body text but must remain readable. Preserve
code/identifiers and meaningful whitespace. Long tokens, equations and wide
images need inspection; shrinking the whole document is not a repair.

## Flow, tables and figures

- Let document length follow content unless the user specifies a limit.
- Keep headings with opening text, with enough opening content to make the
  page break intelligible. Do not keep an entire long section together.
- Keep a figure, its caption and its first reference close. Keep a table caption
  and first row together; long tables may continue with repeated headers.
- Choose column widths for the content. Avoid a mostly empty label column and
  squeezed numbers. Preserve deliberate widths from the source.
- Split an overlarge table at meaningful boundaries or use a landscape section
  when needed. Do not force all its rows onto one page. Tall rows must be able
  to split rather than disappear below the page.
- Use real text, tables and editable paragraphs. Charts may be figures, but
  their labels must remain readable and their data available when needed.
- Do not impose presentation rules such as "one message per page" on flowing
  documents. Pages are a consequence of pagination; sections carry the logic.

A short lead-in needing a page relationship can use the default style:

```markdown
::: {custom-style="Keep with Next"}
The next table contains the values to compare.
:::

| Metric | Before | After |
|--------|-------:|------:|
| Value  | 12     | 18    |
```

Semantic expectations can supplement the generated heading checks:

```json
{
  "required_text": ["Terms remain unchanged"],
  "same_page": [
    {"first": "The next table contains", "second": "Metric", "reason": "Keep the lead-in with the table header"}
  ]
}
```

Use distinctive phrases. Repeated headings or cell values may be ambiguous;
inspect their actual positions rather than guessing which occurrence matched.

## Verify the final rendering

The PDF is the fixed-page evidence. A DOCX's stored page-count property is not
a layout engine, and valid XML does not establish readable pagination. The
default export produces tagged PDF where supported; that alone does not prove
logical reading order, alternative text or accessibility conformance.

For every page, check at readable scale:

1. Text is legible; density, line length and paragraph separation support reading.
2. Heading levels and emphasis create a clear hierarchy.
3. The page has an intentional focal point and balanced rhythm; repeated page
   structures are purposeful rather than mechanically identical.
4. Breaks keep related content understandable, with no isolated headings or
   accidentally empty pages.
5. Tables, charts, labels and footnotes fit without colliding or becoming tiny.

Check program findings before visual signoff. Small-text/overlap/sparse-page
heuristics may flag legitimate footnotes, superscripts or designed layouts;
record the actual reason instead of blindly treating every flag as failure.
Conversely, zero machine findings does not waive the visual review. Acceptance
is tied to the exact final PDF/DOCX and page images, not an earlier iteration.
Pass the helper's `render.json` to inspection so source/template/image edits or
a later failed render also invalidate that snapshot. For externally authored
DOCX/PDF, declare the script, data and local assets with repeated `--resource`
arguments when preparing the final file. The snapshot is not an automatic build
system: rebuild with the chosen authoring tool before refreshing the snapshot.

Retain the native source for subsequent "make it more spacious" changes. Modify
styles/layout and verify content stability rather than asking the model to
rewrite the document's facts each time.
