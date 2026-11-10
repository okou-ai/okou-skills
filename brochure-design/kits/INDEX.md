# Included brochure styles

**Two layout families, three variants.** These are actual HTML/CSS A4 portrait
books, not prompts, author-preview images or 32 separate style templates.

| Family | Variant / ID | Pages | Appearance | Typical use |
| --- | --- | --- | --- | --- |
| Classic Serif | [Classic Serif](old-money-book/KIT.md) · `old-money-book` | 8 | Ivory, espresso, sage, champagne; serif display, generous whitespace, sketch slots, flowing bands. | Company profiles, professional services, heritage or premium brands. |
| Layered Editorial | [Light](sport-ivory/KIT.md) · `sport-ivory` | 12 | Warm-paper magazine; oversized condensed titles, cut-out/layered image slots, large numbers, cross-gutter notes. | Studio/agency introductions, services and creative portfolios. |
| Layered Editorial | [Dark](sport-night/KIT.md) · `sport-night` | 12 | Near-black with electric blue and orange; layered cover, vertical words, giant numbers and contrasting light pages. | Technology launches, sports, gaming and events. |

All trim to **210 × 297 mm**. Photo/portrait/mark slots and fictional copy must be
replaced. `kit.py new` supplies the page CSS and local licensed fonts; raw
`kit.html` files are not standalone assembled projects. The technical IDs preserve
upstream mapping; the skill name is `brochure-design`.

The light/dark variants share a layout family and page-role sequence; colour and
image treatment do not make them wholly unrelated designs. No two-sided six-panel
trifold is included. Adapt individual page structures for an original flyer.

Adapted from stanesjenson11-lgtm's Folio at
`6dd90e0019a39539d6ac6543e53c8437a3a8e13f` under Apache-2.0; see
[provenance and excluded kits](../UPSTREAM.md).
