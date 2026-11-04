# PDF content contract and conventions

Use for CREATE/REFORMAT content features, independently of visual preset. This is
the single block-contract reference; [design](../common/presentation.md) owns appearance.
Fields marked `?` are optional in the renderer, even where authoring guidance
requests them (notably captions). Existing rendering behavior is documented below;
the final QA section adds agent checks, not script-enforced validation.

## Contents

- [Block contract](#block-contract)
- [Common blocks and tables](#common-blocks-and-tables)
- [Mathematics](#mathematics)
- [Charts](#charts)
- [Figures and captions](#figures-and-captions)
- [Bibliography](#bibliography)
- [Code](#code)
- [Flowcharts](#flowcharts)
- [Feature-specific rendering QA](#feature-specific-rendering-qa)

## Block contract

Supply `content.json` as a JSON array of block objects with a `type`. Escape
backslashes in JSON math strings. Use the supported kinds below; do not assume
unknown kinds are rejected by a schema validator. Body styling consumes
`tokens.json`; nominal sizes below are defaults, not manuscript requirements.

| Block | Fields | Rendering / convention |
|---|---|---|
| `h1` | `text` | Section heading, nominal 22pt + full-width accent rule; heading and rule kept together (not a guarantee about following prose) |
| `h2` | `text` | Subsection heading, nominal 15pt dark text; no rule/accent |
| `h3` | `text` | Sub-subsection, nominal 11.5pt bold dark text; no accent |
| `body` | `text` | Nominal 10.5pt justified, 17pt leading; supports `<b>` `<i>` `<font>` ReportLab markup |
| `bullet` | `text` | Body size, `•` prefix, 14pt indent |
| `numbered` | `text` | Body size, automatic `N.` prefix, hanging indent; reset on non-numbered blocks |
| `callout` | `text` | Accent left border + light tint; authoring guidance: max one per section |
| `table` | `headers`, `rows`, `col_widths`?, `caption`? | Accent header, alternating tint, outer box rather than cell grid |
| `image` | `path` or `src`, `caption`? | Local image, column-width constrained; no auto-number |
| `figure` | `path` or `src`, `caption`? | Image with automatic `Figure N:` caption (or `Figure N` without text) |
| `code` | `text`, `language`? | Courier 8.5pt, accent left border, light tint; optional language label |
| `math` | `text`, `label`?, `caption`? | Centered display formula via matplotlib mathtext; optional right-aligned equation label |
| `chart` | `chart_type`, `labels`, `datasets`, `title`?, `x_label`?, `y_label`?, `caption`?, `figure`? | Bar / line / pie via matplotlib; `chart_type` defaults to `bar`, `figure` to `true` |
| `flowchart` | `nodes`, `edges`, `caption`?, `figure`? | Matplotlib process diagram; `figure` defaults to `true` |
| `bibliography` | `items` (`id`, `text` per item), `title`? | Hanging-indent `[id] text`; title defaults to `References`, empty title suppresses heading/rule |
| `divider` | — | Accent-colored full-width 1.2pt rule with padding; use sparingly for thematic breaks |
| `caption` | `text` | Nominal 8.5pt muted centered label, e.g. below image/table |
| `pagebreak` | — | Force a new page |
| `spacer` | `pt`? | Vertical whitespace, default 12pt |

## Common blocks and tables

- Do not manually prefix `numbered` text: its counter auto-resets on intervening
  supported non-numbered blocks, including spacers and page breaks.
- Supply table `headers` and `rows`. `col_widths` are fractions summing to 1.0,
  e.g. `[0.3, 0.5, 0.2]`, one per column; without matching widths the renderer
  uses equal columns. This is an authoring constraint, not sum validation.
- Use the `caption` field below tables/images or a standalone `caption` block.
  Do not duplicate the same caption with both mechanisms.
- Match document hierarchy and preserve supplied values. These blocks do not
  validate evidence, research quality, arithmetic, or professional conclusions.

## Mathematics

**Existing engine:** matplotlib mathtext, pure Python; no LaTeX compiler or browser
is needed for the formula itself (the full CREATE cover still needs Chromium).
Supply `text` without enclosing `$`; JSON-escape LaTeX backslashes.

| Expression | Meaning |
|---|---|
| `E = mc^2` | Simple expression (display block, not inline-math support) |
| `\frac{\sqrt{\pi}}{2}` | Fraction |
| `\int_0^\infty e^{-x^2} dx` | Integral |
| `\sum_{i=1}^{n} x_i` | Summation |
| `\alpha + \beta = \gamma` | Greek letters |

Mathtext covers common notation (`\frac{}{}`, `\int`, `\sum`, `\alpha`, `^`, `_`),
not advanced LaTeX environments: `align`, `cases`, `matrix` are unsupported.
Split complex multi-line proofs into multiple `math` blocks; this does not add
those environments. Set `"label": "(1)"` for a right-aligned equation number;
labels are supplied, not auto-generated. Optional `caption` is below the formula.

**Fallback caution:** missing matplotlib or a math rendering failure yields the
expression in code style, not typeset mathematics. This fallback returns before
rendering label/caption. `make.sh fix` can install missing dependencies; it cannot
make unsupported syntax valid. Do not accept fallback as successful math output.

```json
{"type":"math","text":"\\bar{x}=\\frac{10+12+15}{3}=12.33","label":"(1)"}
```

## Charts

**Existing engine:** entirely Python/matplotlib, no external chart service,
pre-existing image file, or internet required for chart generation.

| `chart_type` | Use | Required content |
|---|---|---|
| `bar` (default) | Discrete-category comparisons | `labels`, `datasets` |
| `line` | Time / ordered-category trends | `labels`, `datasets` |
| `pie` | Part-to-whole composition | `labels`, `datasets[0].values` |

Each dataset contains `values` (numbers) and an optional `label`; supply a label
for meaningful multi-series legends. Add multiple dataset objects for multi-series
bar/line charts. `title` is optional; `x_label`/`y_label` label bar/line axes.
Colors derive from the document accent for consistency; do not set per-chart
custom colors (no documented block override). Explicit color requirements that
cannot be represented must be disclosed rather than silently ignored.
Set `"figure": true` (default) for figure prefixes or `false` to suppress them.
An unsuccessful chart render can produce an install-matplotlib placeholder even
when the cause is not a missing package; inspect output before diagnosing.

```json
{"type":"chart","chart_type":"bar","labels":["Q1","Q2","Q3","Q4"],
 "datasets":[{"label":"Revenue","values":[120,145,132,178]}],"caption":"Q results"}
```

## Figures and captions

- Prefer PNG or JPEG. Use `path` or `src` to a local file; images wider than the
  text column scale down preserving aspect ratio, never up.
- Authoring guidance: always provide an image/figure caption, although the field
  is optional to the renderer. `image` does not number; use `figure` for numbering.
- `figure`, `chart`, and `flowchart` share one figure counter, not separate series.
  Charts/flowcharts default `figure` to `true`. Existing nuance: a chart/flowchart
  with `figure: false` but a nonempty caption still advances the shared counter,
  without a visible prefix. If both are absent/false it does not advance. Verify
  resulting visible numbering; no renumbering repair is implemented here.
- A missing image becomes an `[Image not found: ...]` placeholder; image errors
  may also become text placeholders. Neither is acceptable evidence of a figure.

## Bibliography

- Supply `items` as objects with `id` and `text`. IDs may be numeric (`"1"`, `"2"`)
  or alphanumeric (`"Smith23"`); the renderer prints `[id] text`, with hanging indent.
- Use a consistent citation style in supplied text (APA, Chicago, etc.). The
  renderer does **not** enforce citation style, verify sources, or connect inline
  citations to references. A bracketed bibliography is not strict APA compliance.
- `title` defaults to `"References"`; `"title": ""` suppresses the heading and
  accent rule. Otherwise it creates a section heading styled as h2 plus rule;
  it does not imply an automatic new page.

```json
{"type":"bibliography","items":[
  {"id":"1","text":"Author (Year). Title. Publisher."}]}
```

## Code

- Preserve whitespace exactly; do not add JSON-value indentation to code.
- Optional `language` renders a small language label above the block, e.g.
  `"language": "python"`. There is no syntax highlighting (restraint by design).
- Keep lines under ~90 characters for A4 column width. This is authoring guidance,
  not a promise of automatic wrapping or overflow prevention.

## Flowcharts

Supply `nodes` as `{id, label, shape?}` and `edges` as `{from, to, label?}`.

| `shape` | Meaning |
|---|---|
| `rect` (default) | Process step |
| `diamond` | Decision / condition |
| `oval` or `terminal` | Start / End |
| `parallelogram` | Input / Output |

Nodes are placed in input order, top to bottom. Forward edges use straight
arrows; back-edges to earlier nodes use curved arcs. Keep labels short, 3–5 words
max: diagrams render at A4-column width with 78% maximum-width scale. Figure
numbering follows the chart behavior above (`figure: true` by default); `caption`
is optional. Failure can become an install-matplotlib placeholder, not a diagram.

```json
{"type":"flowchart",
 "nodes":[{"id":"s","label":"Start","shape":"oval"},
          {"id":"p","label":"Process","shape":"rect"},
          {"id":"d","label":"Valid?","shape":"diamond"},
          {"id":"e","label":"End","shape":"oval"}],
 "edges":[{"from":"s","to":"p"},{"from":"p","to":"d"},
          {"from":"d","to":"e","label":"Yes"},
          {"from":"d","to":"p","label":"No"}]}
```

## Feature-specific rendering QA

**Required agent acceptance checks, not existing renderer guarantees.** Render and
inspect actual PDF page images for each used feature, alongside content/source
comparison. Record which checks ran; proposed checks or static doc tests are not
an executed native rendering pass. PDF text extraction alone cannot validate
rasterized equations/charts/flowcharts. Merge success does not prove compliance.

| Feature | Check in actual rendered output |
|---|---|
| Headings / lists / tables | Hierarchy, list resets, all rows/cells, supplied values, column widths, legibility, no clipping or stranded headings |
| Math | Symbols and glyphs, formula correctness against supplied expression, equation label/caption visibility, no code-style fallback |
| Charts | Categories and values match table/source, units/axes/legend, correct chart type, readable labels; no placeholder |
| Figures / captions | Correct asset, aspect ratio, no missing-image/error text; shared numbering and caption sequence match in-text references |
| Bibliography | All cited IDs resolve to supplied references, consistent intended style, no invented sources; inspect hanging indents and heading suppression |
| Code | Whitespace/indentation, language label, complete visible lines, no overflow; syntax highlighting is not expected |
| Flowcharts | All nodes/edges/labels, arrow direction and decision branches, legible back-edges, no clipping or placeholder |

For strict manuscripts additionally verify the actual requested font, sizes,
spacing, margins, title/cover treatment, pagination, and citation standard in the
selected capable authoring route. Disclose unsupported or unverified constraints;
do not fabricate output compliance or infer substantive expertise from a preset.
