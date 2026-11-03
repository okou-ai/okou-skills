# Design System

The appearance, tokens, and visual QA layer for CREATE/REFORMAT. Read this after
common requirements and manuscript/preset selection in [SKILL.md](../SKILL.md).
For block fields, mathematics, charts, figures/captions, bibliography, code, and
flowcharts, read [the content reference directly](../references/content.md).

## Contents

- [Appearance priority](#appearance-priority)
- [Palette logic](#palette-logic)
- [Visual presets and overrides](#visual-presets-and-overrides)
- [Typography system](#typography-system)
- [Cover design](#cover-design)
- [Inner page rules](#inner-page-rules)
- [Design targets](#design-targets)
- [Content conventions](#content-conventions)

## Appearance priority

Explicit user instructions and supplied template typography, colors, cover/no-cover
layout, spacing, and numbering supersede every visual default below, including
"always", "never", font-pair limits, and aesthetic anti-patterns. A strict APA/IEEE
manuscript is not implemented by `--type academic`. Do not impose the default cover
or 10.5pt business-body scale on a named manuscript; select a capable authoring
route per SKILL.md and disclose unavailable actual fonts or standard capabilities.
A preset is not academic research, finance, legal, or medical expertise.

These are design targets, not proof of automatic enforcement or output compliance.

---

## The one rule

Every design decision must be **rooted in the document's content and purpose**.
Dark teal + cream is not "professional". Serif + beige is not "elegant".
A color chosen because it fits the content will always outperform a color chosen
because it seems safe.

---

## Palette logic

`palette.py` selects a named `--type` preset and caller overrides to output
`tokens.json`; it does not infer an industry from prose. The agent makes the
content-sensitive selection. The following mood table is design inspiration,
not an exact listing of current script defaults; retain the script's preset
values unless an explicit override is selected.

### Mood → base palette

| Content signal | Mood | Background | Accent | Text |
|---|---|---|---|---|
| Research, science, analysis | Authoritative | `#0F1F2E` deep ink | `#00B4A6` teal | `#F0EDE6` warm white |
| Business, strategy, finance | Confident | `#1C1C2B` near-black | `#E8A020` amber | `#F5F2EC` cream |
| Creative, portfolio, design | Expressive | `#1A0A2E` deep violet | `#FF6B6B` coral | `#FAF5FF` lavender white |
| Education, academic paper | Scholarly | `#FAFAF7` warm white | `#2C4A7C` navy | `#1A1A2E` dark |
| Healthcare, wellness | Calm | `#F5F9F8` pale mint | `#2D8B72` forest | `#1E3830` deep green |
| Resume / personal | Clean | `#FFFFFF` white | pick from content | `#111111` near-black |
| General / unknown | Neutral | `#F8F6F1` warm off-white | `#3D3D3D` dark gray | `#1A1A1A` black |
| Formal publications, annual reports | Magazine | `#F2F0EC` warm linen | `#1C3557` deep navy | `#0D1A2B` near-black |
| Premium/dark reports, tech reviews | Darkroom | `#151C27` deep navy | `#4A6FA5` steel blue | `#F0EDE6` warm white |
| Technical docs, developer reports | Terminal | `#0D1117` near-black | `#39D353` neon green | `#E6EDF3` cool white |
| Portfolios, creative, photography | Poster | `#FFFFFF` white | `#0A0A0A` near-black | `#0A0A0A` near-black |

### Accent selection rules

- **One accent color only.** Using two accents splits visual energy.
- Accent appears on: cover geometric elements, section rules, callout left borders,
  table header background, page header rule. Nowhere else.
- Accent must contrast with the cover background by at least 4.5:1 (WCAG AA).
- Do not default to blue. Blue is the most overused accent in AI-generated documents.

### Color pairing anti-patterns (never use these)

| ❌ Avoid | Why |
|---|---|
| Purple gradient on white | The default AI aesthetic — immediately signals "generated" |
| Navy + gold | Overused corporate cliché |
| All-black background | Prints badly, feels aggressive |
| More than 3 colors in the system | Visual noise |
| Accent on body text | Destroys readability |

---

## Visual presets and overrides

Retain these existing CLI names; all are appearance choices, not domain workflows.

| Type | Cover pattern | Visual identity |
|---|---|---|
| `report` | `fullbleed` | Dark bg, dot grid, Playfair Display |
| `proposal` | `split` | Left panel + right geometric, Syne |
| `resume` | `typographic` | Oversized first-word, DM Serif Display |
| `portfolio` | `atmospheric` | Near-black, radial glow, Fraunces |
| `academic` | `typographic` | Light bg, classical serif, EB Garamond |
| `general` | `fullbleed` | Dark slate, Outfit |
| `minimal` | `minimal` | White + single 8px accent bar, Cormorant Garamond |
| `stripe` | `stripe` | 3 bold horizontal color bands, Barlow Condensed |
| `diagonal` | `diagonal` | SVG angled cut, dark/light halves, Montserrat |
| `frame` | `frame` | Inset border, corner ornaments, Cormorant |
| `editorial` | `editorial` | Ghost letter, all-caps title, Bebas Neue |
| `magazine` | `magazine` | Warm cream bg, centered stack, hero image, Playfair Display |
| `darkroom` | `darkroom` | Navy bg, centered stack, grayscale image, Playfair Display |
| `terminal` | `terminal` | Near-black, grid lines, monospace, neon green |
| `poster` | `poster` | White bg, thick sidebar, oversized title, Barlow Condensed |

Existing `make.sh run` overrides:
- `--accent "#HEX"` sets accent; `accent_lt` is auto-derived toward white.
- `--cover-bg "#HEX"` sets cover background.
- `--abstract "text"` adds cover abstract text (magazine/darkroom).
- `--cover-image "url"` supplies a hero image URL/path (magazine/darkroom/poster).

Absent explicit user/template colors, choose accent from title, purpose, audience,
and context rather than blindly using the preset. It appears on section rules,
callout bars, table headers, and cover. Suggested ranges (not domain expertise):

| Context | Suggested accent range |
|---|---|
| Legal / compliance / finance | Deep navy `#1C3A5E`, charcoal `#2E3440`, slate `#3D4C5E` |
| Healthcare / medical | Teal-green `#2A6B5A`, cool green `#3A7D6A` |
| Technology / engineering | Steel blue `#2D5F8A`, indigo `#3D4F8A` |
| Environmental / sustainability | Forest `#2E5E3A`, olive `#4A5E2A` |
| Creative / arts / culture | Burgundy `#6B2A35`, plum `#5A2A6B`, terracotta `#8A3A2A` |
| Academic / research | Deep teal `#2A5A6B`, library blue `#2A4A6B` |
| Corporate / neutral | Slate `#3D4A5A`, graphite `#444C56` |
| Luxury / premium | Warm black `#1A1208`, deep bronze `#4A3820` |

Prefer muted, desaturated tones to vivid primaries when free to choose; when in
doubt choose darker and neutral. This preference never overrides requested colors.

---

## Typography system

### Font pairing logic

Two typefaces maximum. Always.

| Role | Criteria | Good choices (system-safe) |
|---|---|---|
| Display (cover title, H1) | Distinctive, strong contrast, high weight | Times New Roman, Georgia (serif) |
| Text (body, captions, UI) | Highly readable at 10–11pt | Helvetica, Arial (sans) |

Cover fonts are loaded live via `@import url(...)` in the cover HTML — Playwright
fetches them at render time, no local caching. Fetch availability is not proof of
actual font use: inspect the rendered PDF and disclose fallbacks. Body defaults
use ReportLab system fonts (Times-Bold / Helvetica), not the cover web fonts.
Token font paths can register available local fonts, but `--type academic` does
not supply a requested manuscript font and there is no new font-selection CLI.

Pairs by mood (cover HTML only — body defaults use system fonts):
- Authoritative: `Playfair Display` / `IBM Plex Sans`
- Confident: `Syne` / `Nunito Sans`
- Expressive: `Fraunces` / `Inter`
- Scholarly: `EB Garamond` / `Source Sans 3`
- Clean: `DM Serif Display` / `DM Sans`
- Restrained: `Cormorant Garamond` / `Jost`
- Bold: `Barlow Condensed` / `Barlow`
- Dynamic: `Montserrat` / `Montserrat`
- Classical: `Cormorant` / `Crimson Pro`
- Editorial: `Bebas Neue` / `Libre Franklin`
- Body fallback (always): `Times-Bold` / `Helvetica` (ReportLab system fonts)

### Type scale

All sizes in points. This scale is used by `palette.py` to populate `tokens.json`.

| Token | Size | Leading | Usage |
|---|---|---|---|
| `display` | 54pt | 1.0 | Cover title |
| `h1` | 22pt | 1.3 | Section headings |
| `h2` | 15pt | 1.4 | Subsection headings |
| `h3` | 11.5pt | 1.5 | Sub-subsection |
| `body` | 10.5pt | 1.6 | Main prose |
| `caption` | 8.5pt | 1.4 | Figure/table captions |
| `meta` | 8pt | 1.3 | Header/footer text |

### Spacing system

Margins and rhythm are what separate "looks designed" from "looks printed".

| Token | Value | Notes |
|---|---|---|
| `margin_outer` | 2.8cm | Left/right page margin |
| `margin_top` | 2.8cm | Top page margin |
| `margin_bottom` | 2.5cm | Bottom page margin |
| `section_gap` | 26pt | Space before H1 |
| `para_gap` | 8pt | Space after paragraph |
| `line_gap` | 17pt | Leading for body text |

Never use ReportLab's default margins (too tight). Always set explicitly.

---

## Cover design

The cover is the most important page. It determines whether a reader trusts the document.

### Thirteen cover patterns

`cover.py` selects one based on `tokens.json["cover_pattern"]`.

**1. `fullbleed`** — used for: `report`, `general`
- Deep background fills 100% of page
- Title: large, left-aligned, upper 60% of page
- Accent: thin horizontal rule + top-right corner strip
- Dot-grid background texture (subtle, 8–10% opacity)
- Footer band: author + date metadata
- Fonts: Playfair Display / IBM Plex Sans

**2. `split`** — used for: `proposal`
- Left 42% panel: solid cover color, title + author
- Right 58%: off-white, dot-grid decoration
- Hard vertical dividing line in accent color
- No gradients — pure flat geometry
- Fonts: Syne / Nunito Sans

**3. `typographic`** — used for: `resume`, `academic`
- White/off-white background
- Name or title as oversized display type (60–80pt), left-aligned
- First word in accent color, remainder in dark
- Thin rule below title block
- Fonts: DM Serif Display / DM Sans (resume) · EB Garamond / Source Sans 3 (academic)

**4. `atmospheric`** — used for: `portfolio`
- Near-black background
- Soft radial glow in accent color (upper-right quadrant)
- Title centered-left, 2 lines max
- Short rule in accent below title
- Dot-grid texture at low opacity
- Fonts: Fraunces / Inter

**5. `minimal`** — used for: `minimal`
- Near-white background, 8px left accent bar is the only color
- Title in very large, light-weight display type (300 weight)
- Hairline rule, author + date as single muted line
- Nothing else — the bar does all the visual work
- Fonts: Cormorant Garamond / Jost

**6. `stripe`** — used for: `stripe`
- Page cut into three horizontal bands: accent / dark / light
- Top band: category label; middle: oversized title in white; bottom: metadata
- Hard edges, no gradients, no textures — newspaper / brand poster aesthetic
- Fonts: Barlow Condensed / Barlow

**7. `diagonal`** — used for: `diagonal`
- SVG polygon cuts page diagonally: dark upper-left, light lower-right
- Accent-colored edge line traces the diagonal cut
- Title on dark area, metadata on light area
- Fonts: Montserrat / Montserrat

**8. `frame`** — used for: `frame`
- White/cream background with an inset rectangular border (1.2px, 28px from edges)
- Accent strips inside top + bottom of frame; small accent corner squares
- Title centered in the frame space, centered alignment, classical weight
- Formal, timeless — annual reports, legal documents, academic papers
- Fonts: Cormorant / Crimson Pro

**9. `editorial`** — used for: `editorial`
- Ghost first-letter of title fills upper-right at 5% opacity — visual texture
- 5px accent top bar; full-width uppercase title in condensed weight
- Title all-caps, very large (80px), flush-left
- Footer rule + author/date metadata
- Fonts: Bebas Neue / Libre Franklin

**10. `magazine`** — used for: `magazine`
- Warm cream/linen background; fully centered, vertical stack layout
- Org/company name in small spaced caps + 2px accent rule beneath (top anchor)
- Large bold serif title (52px) centered; short accent rule under title
- Italic subtitle; optional `cover_image` URL renders as centered hero thumbnail
- Optional `abstract` field: justified text block with bold "Abstract:" label
- Author name in accent color (large, bold); date beneath
- Fonts: Playfair Display / EB Garamond

**11. `darkroom`** — used for: `darkroom`
- Same centered stack layout as `magazine` but deep navy background, white text
- Org name + rules in semi-transparent white; accent rules desaturated
- Hero image (if provided) gets `grayscale(20%) brightness(0.9)` filter
- Fonts: Playfair Display / EB Garamond

**12. `terminal`** — used for: `terminal`
- Near-black background; neon green accent; Space Mono monospace throughout
- Grid overlay: faint horizontal + vertical lines at 48px intervals (7% opacity)
- Status label top-left: green dot + `SYSTEM_REPORT // <date>`
- Title inside a bracket frame (border-left + border-top + pseudo-element corner)
- Subtitle prefixed with `>` in accent color
- Abstract text left; author block right; status bar at bottom (UTF-8 / Ln 1)
- Fonts: Space Mono / Space Mono

**13. `poster`** — used for: `poster`
- White background; thick 52px left sidebar in accent (typically near-black)
- Title: 96px, 900-weight, all-caps, condensed — the dominant visual element
- Subtitle in typewriter font below title; thin 2px rule as separator
- Author + meta in Courier Prime monospace beneath rule
- Optional `cover_image` rendered as 260×340 grayscale thumbnail, right-aligned
- Accent square icon block (lower-right) with white horizontal lines
- Fonts: Barlow Condensed / Courier Prime

### Optional token: `cover_image`

Patterns `magazine`, `darkroom`, and `poster` accept an optional `cover_image`
token containing an absolute URL or `file://` path to an image.
The image renders via `<img src="...">` — Playwright fetches it at render time.
If omitted, the image area is simply skipped (layout adjusts gracefully).

### Cover CSS requirements (critical for Playwright rendering)

These three rules must appear in every cover HTML file or the output will have
white borders / incorrect dimensions:

```css
body { margin: 0; padding: 0; }
html, body { width: 794px; height: 1123px; overflow: hidden; }
```

No `@page` rules needed — Playwright handles page size via the `pdf()` call.
Do NOT use CSS `background-image` for textures — use inline SVG or `<canvas>`.
Always use `position: absolute` + `z-index` for layered elements.

### What always kills a cover

- Centered title on white background with a thin horizontal line underneath
- Gradient from one color to another (reads as PowerPoint, not print design)
- Drop shadows on text
- More than one accent color
- Emoji or icon fonts (fail silently on headless Chromium)

---

## Inner page rules

### What "restraint" means in practice

Every design decision should remove something, not add something.
The page is done when there is nothing left to remove.

- Accent color appears on section rules only — not on headings, not on bullets
- No card components (bordered boxes with colored headers)
- No rounded corners on anything except callout boxes (4px max)
- No shadows anywhere
- Tables: header row in accent, alternating row tint, no grid lines except outer box
- Callout boxes: left border in accent (4px), very light tint background, no icon

### Page header / footer

Header: document title (left, 7.5pt, muted) + accent rule (1.5pt, full width below)
Footer: author name (left, 7.5pt, muted) + page number (right, 7.5pt, muted) + light rule above

---

## Design targets

Agent acceptance checks: inspect actual rendered pages, not only tokens or a
successful merge receipt. Record checks not executed as unverified. Verify actual
fonts/glyphs (including web-font fallbacks), colors/contrast, page dimensions,
margins, cover treatment, readable type, and page sequence against requirements.
These are QA instructions, not new renderer checks or accessibility certification.
For feature-specific output QA use [content QA](../references/content.md#feature-specific-rendering-qa).

- Cover, when requested, has a clear visual identity that is not "generic AI output"
- Body text is readable at arm's length without squinting
- Every page looks like it belongs to the same document
- No element bleeds off the edge or overlaps another
- Page numbers are present and correct
- The accent color appears fewer than 8 times per page on average

---

## Content conventions

Read [the single content contract](../references/content.md) for all block fields,
defaults, numbering, mathtext limits/fallbacks, and chart, caption, bibliography,
code, and flowchart conventions. Do not infer content requirements from a cover
pattern or a palette mood.
