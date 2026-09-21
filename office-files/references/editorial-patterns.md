# Editorial page patterns

Use this only for **new, untemplated flowing prose**. A supplied template,
existing Word file, form or fixed-position source remains the visual authority.
These are compositional options, not a mandatory report outline and not document
categories.

## Default visual direction

The maintained default is editorial paper rather than generic office software:

- warm paper (`#F5F4ED`) with near-black text;
- one ink-blue accent (`#1B365D`), used sparingly;
- serif display hierarchy with a neutral sans body;
- warm rules and alternating table rows instead of boxed grids;
- no gradients, heavy shadows, ornamental icons or repeated callout cards.

The palette and print rhythm adapt the open-source kami paper aesthetic documented
in `nexu-io/open-design` at commit
`3fb620af423534643677c7c6fae76be088fa770a` (which attributes its inspiration to
`tw93/kami`, MIT). The Office implementation here is original OOXML styling and
keeps user templates untouched.

A visual system only supplies constraints. The author must still choose a focal
point, group related material and create page-to-page rhythm.

## Choose an opening

Use one primary opening pattern. Do not stack all of them merely because they are
available.

### Narrative opening

Suitable when the main value is an argument or explanation.

```markdown
---
title: A clear, specific title
subtitle: One line that adds meaning rather than repeating the title
lang: en-US
---

::: {custom-style="Deck"}
Two or three sentences that establish the question and the main answer.
:::
```

### Evidence-led opening

Suitable when three or four numbers orient the reader faster than prose.

```markdown
| 88.3% | 20.2× | 121× |
|------:|------:|-----:|
| internal usage share | multiplier gap | model-cost gap |

: {#opening-metrics .metric-grid}
```

A metric grid should contain **two rows**: values, then short labels. Use two to
four columns. Put interpretation immediately before or after it. It is editable
Word content, not a chart image.

### Decision-led opening

Suitable when the reader needs the conclusion before the evidence.

```markdown
::: {custom-style="Key Takeaway"}
The one conclusion that changes a decision, with enough context to stand alone.
:::
```

Use one opening takeaway and occasional later takeaways. A callout after every
heading destroys hierarchy.

## Establish reading rhythm

### Section lead

Use a short lead to state why the next section matters. It should be more
specific than the heading.

```markdown
# 03 Trigger sources

::: {custom-style="Section Lead"}
Internal usage is machine-amplified; external usage is still conversation-led.
:::
```

### Deliberate chapter transition

```markdown
# 04 Economics {.chapter}
```

`.chapter` inserts a real page break before the heading. Use it for a major
transition, after a designed opening, or before a landscape/appendix-like
section. Do not use it to force every top-level section onto a new page.

### Pull quote

```markdown
::: {custom-style="Pull Quote"}
The workflow, not the chat box, is the product boundary that matters here.
:::
```

A pull quote is a pacing device. Keep it brief and do not duplicate a nearby
heading or callout.

### Eyebrow

```markdown
::: {custom-style="Eyebrow"}
PRODUCT INTELLIGENCE · 30-DAY WINDOW
:::
```

Use for a small series label, confidentiality marker or edition. Do not invent
one solely to decorate the page.

## Tables and figures

- Let the standard renderer balance ordinary table columns from their contents.
- Prefer a few meaningful columns over a wide spreadsheet squeezed onto a page.
- Keep a metric grid to two rows; use a normal table for records or comparisons.
- Use the same paper, ink and warm-neutral palette in charts. Labels and values
  must carry meaning without colour.
- A chart page needs an interpretation sentence, the figure, a caption when
  useful, and a concise source note—not multiple repeated source paragraphs.

```markdown
![Trigger-source comparison. Values are labelled directly.](trigger-source.svg){width=16cm}

::: {custom-style="Source Note"}
Source: full population, 2026-08-22 to 2026-09-20 UTC.
:::
```

## Page-level review

For each rendered page, answer all five questions with concrete observations:

1. **Legibility and density:** Is body text readable at ordinary page scale?
2. **Hierarchy:** Is the entry point and reading order obvious?
3. **Composition and rhythm:** What is the focal point? Are open and occupied
   areas balanced? Does this page differ from adjacent pages for a reason?
4. **Pagination and grouping:** Do headings, leads, figures, captions and opening
   rows stay with the material they introduce?
5. **Tables and figures:** Are widths, labels, notes and visual weight balanced?

If a page is technically valid but visually flat, the review has not passed.
Change the source composition or selected components and render again. Limit the
process to two repair rounds, then deliver a clearly marked draft if the defect
cannot be resolved.
