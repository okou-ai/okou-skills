# PDF presets and supported appearance controls

For this cover/body CREATE/REFORMAT pipeline only. User instructions and supplied
styles/templates override defaults, including colors, typography, spacing,
numbering and cover/no-cover requirements. If the pipeline cannot represent a
requirement, select a capable route rather than silently applying a preset.

## Visual presets and overrides

Choose a suitable existing `--type` once (default: `general`); keep its script
tokens unchanged unless a user requirement needs an override. No new mood-board,
accent research or open-ended aesthetic planning is required for a default PDF.
Custom styling is only for requested/necessary departures. The optional
[design reference](design-reference.md) retains pattern descriptions and design
ideas; it is not a prerequisite or a new operation branch.

| Type | Cover pattern | Identity |
|---|---|---|
| `report` | `fullbleed` | Dark, dot grid, Playfair Display |
| `proposal` | `split` | Split panel, Syne |
| `resume` | `typographic` | Oversized first word, DM Serif Display |
| `portfolio` | `atmospheric` | Dark, radial glow, Fraunces |
| `academic` | `typographic` | Light, EB Garamond |
| `general` | `fullbleed` | Dark slate, Outfit |
| `minimal` | `minimal` | White, single accent bar, Cormorant Garamond |
| `stripe` | `stripe` | Three color bands, Barlow Condensed |
| `diagonal` | `diagonal` | Angled cut, Montserrat |
| `frame` | `frame` | Inset border, Cormorant |
| `editorial` | `editorial` | Ghost initial, all-caps, Bebas Neue |
| `magazine` | `magazine` | Cream, centered stack, optional hero image |
| `darkroom` | `darkroom` | Navy, centered stack, optional filtered image |
| `terminal` | `terminal` | Near-black, grid, monospace |
| `poster` | `poster` | White, thick sidebar, oversized title |

`make.sh run` supports:
- `--accent "#HEX"` (also derives `accent_lt`) and `--cover-bg "#HEX"`.
- `--subtitle "text"`.
- `--abstract "text"` for magazine/darkroom covers.
- `--cover-image "URL-or-path"` for magazine/darkroom/poster. Cover HTML loads the
  asset at render time; prefer an absolute URL or `file://` path.

`make.sh reformat` accepts its documented title/type/author/date/subtitle flags,
not all `run` overrides. For those overrides, parse to JSON and call `run`.
Do not invent font, no-cover, manuscript, OCR or renderer CLI modes.

## Actual capability restrictions

- This pipeline produces one A4 cover plus A4 body pages. A no-cover requirement
  or strict manuscript layout needs a route that actually implements it; use
  [named-format selection](../domains/profiles.md) only when applicable.
- `palette.py` supplies sizes, margins and tokens; it does not infer an industry.
  Body defaults are Times-Bold/Helvetica (10.5pt prose, 17pt leading), not the
  Google cover typefaces. A preset name is not proof of actual font use.
- Cover fonts are fetched via Google Fonts CSS at render time, without local
  caching. Network availability and fallback fonts can change appearance; check
  the output and disclose missing requested faces. No font-selection CLI is added.
- Local token font paths may register usable TTFs. CJK/mixed-script body text
  needs an embeddable TrueType font covering the actual glyphs; see
  [environment](../implementation/environment.md). Do not hide font failures.
- Charts/math/flowcharts use matplotlib, not a browser or full LaTeX engine;
  limits and schemas live in the [content contract](../implementation/content.md).
- A Word/PDF pair must use the authored DOCX as the PDF source, not this separate
  design pipeline.

[VALIDATE](../operations/validate.md) owns all operation- and feature-specific
acceptance checks; there is no separate design checklist here.
