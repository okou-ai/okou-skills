---
id: sport-night
name: Layered Editorial Dark
family: layered-editorial
best_for: technology launches, gaming, sport and events
size: A4 (210 x 297 mm)
pages: 12
fonts: Big Shoulders Display:800,900; Familjen Grotesk:400,500,600,700
theme: brand #2F5BEA; brand-2 #3D7BFF; accent #FF6A1A; accent-2 #FFB38A
---

# Layered Editorial — Dark · 深色叠层杂志

Near-black pages, electric-blue fields and orange accents. Layered cover,
cut-out/object slots, giant numerals, horizontal/vertical words and contrasting
light pages. A **12-page book** in the same layered family as the light variant,
not a third unrelated layout family.

| Pages | Structure |
| --- | --- |
| 1 | Layered background, glow/noise, masthead, streak, person and hero-object slots. |
| 2–3 | Contents with vertical word and studio introduction; blue cross-gutter box. |
| 4–5 | Giant word, layered image/device slots, services and flowing blue band. |
| 6–7 | Dark vertical-word opener paired with a light stack page and note box. |
| 8–9 | Design/media words, image slots, cross-fold object and flowing-edge light panel. |
| 10–11 | Statistic/price placeholders, steps band and circular portraits with note box. |
| 12 | Cut-out slot, sign-off and contacts. |

**Colours:** near-black `#070B14`, light ink `#F2F4F8`, secondary ink `#AEB8CC`,
blue `#2F5BEA` / `#3D7BFF`, orange `#FF6A1A` / `#FFB38A`, white `#FFFFFF`.
`--brand` / `--accent` preserve derived colour-role offsets; recheck contrast.

**Type:** Big Shoulders Display 800/900 for large words/numerals; Familjen Grotesk
400/500/600/700 for labels and body. Check requested weights and avoid unintended
synthesis. Chinese needs an additional licensed CJK family and reflow inspection.

Initialize with `kit.py new sport-night <fresh-project> --name brochure`.
It supplies local fonts and `pages.css`; raw `kit.html` is not standalone.
Replace/verify every `data-kit-sample` and image/mark/portrait slot. No stock photos
or real technology logos are supplied. Preserve spread continuity, then render
and inspect all pages, especially dark-page text contrast.

**Modified by Okou:** adapted from Folio's `sport-night` at
`6dd90e0019a39539d6ac6543e53c8437a3a8e13f`; logos, cut-out and undocumented noise
replaced by neutral/original assets. `scripts/generate_newsprint.py` at the skill
root reproduces the bundled noise. See [source/license](../../UPSTREAM.md).
