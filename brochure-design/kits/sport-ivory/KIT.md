---
id: sport-ivory
name: Layered Editorial Light
family: layered-editorial
best_for: studios, agencies, creative portfolios and service brochures
size: A4 (210 x 297 mm)
pages: 12
fonts: Big Shoulders Display:800,900; Bodoni Moda:400,400i,500; Familjen Grotesk:400,600; Source Serif 4:400,400i
theme: brand #7D8B6A; accent #C9A96E
---

# Layered Editorial — Light · 浅色叠层杂志

Warm-paper magazine with oversized condensed headings, an espresso cover,
cut-out/layered image slots, large numerals, sage bands and champagne cross-gutter
note boxes. A **12-page book**; shares the layered family with the dark variant.

| Pages | Structure |
| --- | --- |
| 1 | Oversized masthead, cut-out-person slot, sage panel and offset image slot. |
| 2–3 | Contents and studio introduction with a cross-gutter note box. |
| 4–5 | Giant word, layered imagery, service lists and a flowing timeline band. |
| 6–7 | Dark systems opener paired with a light stack/industries page and note box. |
| 8–9 | Large design/media words, sage field, image/sketch slots and print list. |
| 10–11 | Statistic/price placeholders, steps band and circular portraits with note box. |
| 12 | Contact back cover. |

**Colours:** paper `#F6F1E7`, ink `#2B1D16`, secondary ink `#5E4E43`, espresso
`#3B2A20`, tint `#EFE7DA`, sage `#7D8B6A`, champagne `#C9A96E`.
`--brand` changes sage/support, not the espresso field.

**Type:** Big Shoulders Display for oversized words/numerals, Bodoni Moda editorial
heads, Familjen Grotesk labels, Source Serif 4 body. Chinese needs licensed local CJK
fonts and reflow review; the condensed Latin masthead is not a Chinese font.

Initialize with `kit.py new sport-ivory <fresh-project> --name brochure`.
It supplies local fonts and `pages.css`; raw `kit.html` is not standalone.
Replace/verify every `data-kit-sample`, including people, service marks, prices and
contact details. Image slots are generic vectors, not licensed stock photographs.
Preserve gutter continuity, then render and inspect every page.

**Modified by Okou:** adapted from Folio's `sport-ivory` at
`6dd90e0019a39539d6ac6543e53c8437a3a8e13f`; real logos and undocumented textures
replaced by neutral/original assets, transparent cover cut-out supplied, commercial
font aliases removed. See [source/license](../../UPSTREAM.md).
