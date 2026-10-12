# Document style

Use this baseline for new Word/PDF documents across languages and topics. User requirements and templates take priority; preserve existing designs during narrow edits. The blank assets provide typography and page settings, with no sample content, report outline, palette, decoration, or automatic page numbers. Choose any additional design for the task.

## Baseline

Measurements are in points unless stated otherwise. `12/16` means 12 pt type with a target text line spacing of 16 pt. Increase line spacing when a script or equation needs it; never use it to constrain image height.

| Element | Style |
| --- | --- |
| Paper and text area | US Letter, single column; 5.5-inch text width; margins: left/right 108, top 65, bottom 64 |
| Body | 12/16; aligned to the reading start; 8 after paragraphs; no first-line indent |
| Document title | 18/22, bold; 14 after |
| Section heading | 13/17, bold; 16 before, 9 after; use real heading levels |
| Tables | 11/14; bold header row; table title above, at the same size |
| Chart labels | 10–11 at the final placed size, including after image scaling |
| Captions and sources | 10/13, below the figure |
| Footer, when used | 9/12; clear of the body |

These type sizes are acceptance criteria for this style. Unless the user or template specifies otherwise, do not reduce them to fit content or cut page count. Adjust column widths, wrap text, split tables, or add pages first; use landscape pages for wide tables when needed.

## Fonts and languages

- The Word asset sets Latin `ascii`/`hAnsi` to Times New Roman, `eastAsia` to Noto Serif CJK SC, and complex-script `cs` to Noto Naskh Arabic. The PDF source uses Liberation Serif with Noto Serif CJK SC fallback. Adapt the East Asian regional font and complex-script font to the actual language; provide the required weights.
- Keep Word's script-specific font slots separate in defaults, styles, and direct run formatting, including tables and headers/footers. Remove conflicting theme-font attributes when setting explicit fonts; do not map Latin text to an embedded CJK font merely to cover all scripts. This addresses a known Microsoft preview compatibility risk, not a ban on CJK fonts or embedding.
- If a font is unavailable, choose an available substitute with full script coverage and a similar style, and briefly disclose it. Respect font usage and embedding licenses; embed fonts in PDFs. Setting a font name does not prove it rendered correctly.
- Adapt line spacing, line breaks, shaping, reading direction, and mixed-script text to the language. For RTL content, check punctuation, numbers, and table direction. Preserve the type hierarchy.
- Microsoft preview compatibility requires checking the final DOCX in the actual Okou/Microsoft viewer, including mixed-script text and selection/copy. Local Word/PDF renders alone do not establish that result; mark unavailable preview checks as unverified. Use a compatibility copy when repairing an existing file.

## Tables and charts

- Choose table rules, backgrounds, and padding to suit the content; the assets prescribe no decorative treatment.
- Align text labels to the reading start and numbers to the right. Keep units, precision, and number formats consistent within a column. Repeat headers on continuation pages; keep ordinary rows together and restructure oversized rows. Keep table titles with the header and first row.
- Fit charts within the available text area, preserve their aspect ratio, and leave room for labels and legends. Use the document fonts. Distinguish series with labels, markers, or line styles as well as color.
- State chart units and sources; use the same data definitions as the prose and tables. Bar-chart value axes start at zero. Keep figures, captions, and sources on the same page where possible; label illustrative data.

## Pagination and variants

- Let content determine page count. Keep headings with the following paragraph and avoid isolated first or last paragraph lines. Different language versions may have different page counts.
- When A4 or two columns are requested, adapt margins and column widths; wide tables and charts may span both columns. Check reading order, line length, and actual pagination. Do not shrink body text to preserve the original page count.
