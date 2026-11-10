---
id: sport-night
name: Sport Layers Night
family: sport & action
best_for: technology, gaming, sport, launches, events
size: A4 (210 x 297 mm)
pages: 12
render: --bleed 3
fonts: Big Shoulders Display:800,900; Familjen Grotesk:400,500,600,700
theme: brand #2F5BEA; brand-2 #3D7BFF; accent #FF6A1A; accent-2 #FFB38A
---

> **MODIFIED BY OKOU: sanitized adaptation of Folio at 6dd90e0019a39539d6ac6543e53c8437a3a8e13f; not a statement of legal clearance.**

# Sport Layers Night

**Style:** Dark, high-contrast layered magazine for technology, gaming, sport, launches or events. Near-black grounds with shared low-opacity photo slots, electric-blue gutter-spanning note boxes and bands, orange numerals and vertical words, and one light stack page. Cover stack: background slot, glow, original monochrome noise, masthead, streak, person slot, hero-object slot and spark. Horizontal and top-to-bottom vertical headline roles are retained.

**Page roles (12):** 1 layered cover; 2–3 contents with vertical word and studio introduction, gutter box; 4–5 large word, layered photo/device slots, services with neutral marks, flowing spread band; 6–7 dark vertical-word opener and light stack page with neutral marks, gutter box; 8–9 large design/media words, layered photo slots, fold-crossing object slot and flowing-edge light panel; 10–11 statistic, generic stars, pricing, flowing steps band and directors with circular portrait slots, gutter box; 12 cut-out slot, sign-off and contact back cover.

**Palette:** Theme recommendations: brand `#2F5BEA`, secondary brand `#3D7BFF`, accent `#FF6A1A`, secondary accent `#FFB38A`. CSS roles: night/paper `#070B14`, light ink/support `#F2F4F8`, secondary ink `#AEB8CC`, brand `#2F5BEA`, on-brand `#FFFFFF`, accent `#FF6A1A`, dark ink `#070B14`, secondary dark ink `#4A5368`. A background-slot duotone recommendation is near-black `#05070D` with the selected blue and light tones.

**Typography:** Big Shoulders Display 800/900 for large words and numerals; Familjen Grotesk 400/500/600/700 for labels and body text. These are the named free alternatives retained from the source kit recommendations. CSS can request intermediate/heavier weights; assembled font supply must account for them or document synthesis.

**Imagery roles:** Context background slots, one cut-out-person slot (recommended eventual source resolution at least 4000 px), hero device/object slot, additional photo/cut-out slots (roughly eight or more for a filled design), neutral service marks, streak, spark, glow and flowing bands. No stock imagery or real technology-logo files are included. `assets/newsprint.png` is original 512×512 binary black/white noise generated from a fixed seed using the included stdlib-only `../../scripts/generate_newsprint.py --out <new-path-outside-skill>`, not the excluded upstream PNG.

## Assembly and use

- A4 portrait, 210 × 297 mm; recommended bleed: 3 mm. Preserve the listed page roles and cross-fold continuity.
- Run `kit.py new sport-night <fresh-project> --name brochure`: it supplies `fonts/fonts.css`, licensed local Latin fonts and `folio.css`. Raw kit.html is a source template, not the assembled output.
- HTML text and image slots marked `data-kit-sample` are demonstration content, not verified claims. Replace sample company identity, contacts, project counts, prices, timelines and capability labels with verified project content before use.
- Replace neutral mark/photo/portrait slots only with appropriately sourced project assets; do not infer a real brand affiliation from sample technology names.
- Original photo-credit sentences were removed because those photographs are not in this bundle. Generic vector assets retain their source bytes and the upstream Apache-2.0 license accompanies this curated bundle.
- After every adaptation, render and inspect all pages; check contrast, font loading, overflow, bleed and preflight. Template validation does not certify final copy, print production or legal clearance.
