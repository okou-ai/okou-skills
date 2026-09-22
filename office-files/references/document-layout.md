# Document layout and verification

## Rendering setup

Install the shared page inspector:

```bash
python3 -m pip install --break-system-packages --quiet PyMuPDF==1.28.2
```

For DOCX or Markdown export, also install LibreOffice Writer if absent:

```bash
sudo apt-get update -qq
sudo apt-get install -y -qq libreoffice-writer
```

Check the chosen font with `fc-match` on the rendering host. Set the document's
language and direction, and use fonts that cover its script and regional glyphs.

## Layout

- Follow the supplied design. For a new document, choose a consistent hierarchy,
  opening focal point and page rhythm suited to the content.
- Use semantic headings, lists, tables and captions. Keep text editable.
- Keep headings with opening text and figures with their captions; allow long
  sections and tables to flow across pages.
- Size table columns for their contents and repeat headers on continued tables.
  Split oversized tables or use a landscape section when needed.
- Repair crowding through grouping, widths and page breaks. Do not shrink text
  or compress spacing merely to reduce the page count.
- Preserve facts and required wording when changing the layout.

## Content expectations

Before inspection, add request-specific constraints to the generated
`expectations.json`. Retain its existing entries; use distinctive phrases:

```json
{
  "required_text": ["Terms remain unchanged"],
  "same_page": [
    {"first": "The next table contains", "second": "Metric", "reason": "Keep the lead-in with the table header"}
  ]
}
```

Check repeated text, exact page counts and other constraints not represented by
this format directly against the rendered pages.

## Page review

Open every page at a readable scale and record these five checks in `review.json`:

| Criterion | Check |
| --- | --- |
| Legibility and density | Readable type, line length, paragraph separation and text density |
| Hierarchy | Clear heading levels, emphasis and reading order |
| Composition and rhythm | A deliberate focal point, balanced whitespace and purposeful page variation |
| Pagination and grouping | Related content stays together; no isolated headings or accidental blank pages |
| Tables and figures | Readable labels and notes; suitable widths and placement; no clipping or collisions |

If a page has no tables or figures, record that observation. Acknowledge warnings
with what is visible on the page; repair blockers and visual defects before
marking criteria `pass`. Change grouping, emphasis or page transitions to fix a
flat composition. Do not replace page inspection with a contact sheet or XML check.

When relevant, verify interactive features and accessibility separately. For
Word, report material pagination differences between the verified LibreOffice
export and the user's target application.
