---
id: old-money-book
name: Classic Serif
family: classic-serif
best_for: company profiles, professional services, heritage and premium brands
size: A4 (210 x 297 mm)
pages: 8
fonts: Bodoni Moda:400,400i,500; Familjen Grotesk:400,600; Source Serif 4:400,400i
theme: brand #7D8B6A; accent #C9A96E
---

# Classic Serif · 经典衬线

Ivory paper, espresso type, sage fields and champagne details. Restrained serif
hierarchy, generous whitespace, sketch/image slots and flowing bands connect the
reader spreads. This is an **8-page company book**, not a folded leaflet.

| Pages | Structure |
| --- | --- |
| 1 | Serif masthead, italic subtitle, seal and large sketch slot. |
| 2–3 | Contents; studio introduction, quote, statistic and sage heading field. |
| 4–5 | Services spread, fold-crossing sketch slot and flowing sage timeline band. |
| 6–7 | Print/services page with champagne field; people page with two portrait slots. |
| 8 | Sign-off, sketch slot and espresso contact field with flowing edge. |

**Colours:** paper `#F6F1E7`, ink `#2B1D16`, secondary ink `#5E4E43`, espresso
`#3B2A20`, tint `#EFE7DA`, sage `#7D8B6A`, champagne `#C9A96E`.
`--brand` changes sage/support, not the espresso field.

**Type:** Bodoni Moda display, Familjen Grotesk labels, Source Serif 4 body.
Chinese requires a licensed local CJK font and new line-break inspection.

Initialize with `kit.py new old-money-book <fresh-project> --name brochure`.
It supplies local fonts and `pages.css`; raw `kit.html` is not standalone.
Replace/verify every `data-kit-sample` text and image slot, preserving spread
continuity. Included vectors are generic placeholders, not stock photography or
verified client assets. Render and inspect every page after content changes.

**Modified by Okou:** adapted from Folio's `old-money-book` at
`6dd90e0019a39539d6ac6543e53c8437a3a8e13f`; commercial aliases replaced by free fonts,
paper overlay replaced by an original procedural SVG. See [source/license](../../UPSTREAM.md).
