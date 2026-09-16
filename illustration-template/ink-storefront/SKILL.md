---
name: ink-storefront
description: Single-color hand-drawn ink line illustration of a small storefront on warm cream paper — locked house style with confident fineliner contours, a hand-lettered shop sign, foliage, and small street props (bike, A-frame, planters, lanterns, cat). Boutique poster aesthetic. Trigger when the user says /ink-storefront, asks for a "shopfront illustration", "storefront poster", "boutique fineliner illustration", "café line drawing", or briefs with a shop name + ink color + archetype in this house style.
---

# /ink-storefront — locked boutique storefront illustration

Forge a portrait boutique-poster illustration of a small storefront in the **ink-storefront** house style: single-color hand-drawn ink line drawing on warm cream paper, with a hand-lettered shop sign baked into the building, foliage and small street props softening the facade. Mood: airy, charming, hand-illustrated by a fineliner pen — a poster you'd hang in a café or send as a postcard.

Every invocation flexes the dials below against a locked frame. The frame never changes; the dials describe the per-piece shop.

## Locked frame (never change)

- **Canvas** — portrait aspect ratio, 1024×1536.
- **Background** — warm cream / off-white paper `#f4ecd8`, fully flat. No vignette, no border ring, no paper-grain texture overlay.
- **Line treatment** — single-color ink, monochromatic. **Every stroke in the same hue, no accent color, no second hue, no shadow color.** Confident fineliner contour drawing with occasional **double-stroke shadow** under awnings, signs, ledges, wheels, and other prominent edges. The double-stroke is the only shading device in the style.
- **Subject** — always a small **storefront / shopfront** seen from street level. Architectural focus, never an interior, never a portrait. The building, its sign, and its sidewalk are the entire piece.
- **Signage** — a hand-lettered shop name is baked into the building (over the door, on an awning, on a wall sign). Optional smaller subtitle or street-address line beneath. The lettering must look hand-drawn — decorative serif or script, not vector-perfect.
- **Foliage + props** — plants/foliage **and** at least one small street prop are always present. A bare facade is wrong for the style.
- **Ground line** — a faint horizontal sidewalk line runs across the bottom of the canvas.
- **Rendering** — pure linework. **No solid color fills. No shading beyond the double-stroke trick. No gradients. No dense hatching.** Plenty of cream paper showing through.

## Dials (vary per piece)

| Dial | Options |
|---|---|
| **Ink color** | Single hex — every stroke in this hue. Tested anchors: cobalt blue `#1f4ec9`, forest green `#2f5b3a`, terracotta rust `#b94e2c`, charcoal indigo `#1f2547`, burgundy `#7a1f2b`, olive `#5a6e2b`. |
| **Shop name + subtitle** | The lettering on the building. Subtitle is optional but common (e.g., "PETIT PAIN" / "BOULANGERIE", "FLEUR & FERN" / "FLOWERS · PLANTS · GIFTS", "AKIRA RAMEN" / "アキラ ラーメン"). |
| **Shop archetype** | café, boulangerie, florist, bookshop, ramen, barber, wine bar, record store, gelato, butcher, cheese shop, perfumery, tea house, etc. |
| **Perspective** | Flat facade-on OR 3/4 corner view. |
| **Foreground props** | Bike leaning on the wall, A-frame chalkboard, café tables + chairs, parasol, planter cluster, lanterns strung above the door, scooter at the curb, dog/cat at the doorstep, vintage car parked outside, hanging baskets. |
| **Foliage density** | Sparse vine ↔ moderate (a few climbers around windows) ↔ overgrown (ivy across the brickwork, hanging baskets, planters spilling). |
| **Complexity level** | **L1** — single facade, one or two props, lots of cream paper showing. <br>**L2** — denser foreground OR 3/4 corner view with extra props + a single walking figure. <br>**L3** — full vignette: alley/corner scene, multiple figures or vehicles, overhead lanterns or wires, steam wisps. Use sparingly. |

## Prompt template

```
Single-color hand-drawn ink line illustration of a {ARCHETYPE} storefront viewed
from the street, {PERSPECTIVE}, on a warm cream off-white paper background (#f4ecd8).

Ink color: {INK_HEX}, monochromatic — every line in this single hue, no other
colors.

Hand-lettered serif shop sign reads '{NAME}' with smaller subtitle '{SUBTITLE}'
below.

Foreground props: {PROPS}. Foliage: {FOLIAGE_DENSITY}.

Confident fineliner contour drawing with occasional double-stroke shadow under
awnings, signs, ledges, and wheels. No solid color fills, no shading, no
gradients — pure linework only. Faint horizontal sidewalk line across the bottom.

Portrait orientation. Boutique poster aesthetic, hand-illustrated by a fineliner
pen. {COMPLEXITY_NOTE}.
```

Where `{COMPLEXITY_NOTE}` is:
- **L1** — "Single facade, one or two foreground props, plenty of paper showing"
- **L2** — "Small scene, dense foreground with planters and a walking figure"
- **L3** — "Full vignette with multiple figures, vehicles, and overhead detail"

## How to interpret a brief

The user will usually hand over a short seed (e.g. "boulangerie called Petit Pain in cobalt", "Japanese ramen counter in charcoal", "wine bar named Lupo in burgundy"). Expand it into the locked frame:

1. **Resolve the ink color.** If the user names a hue without a hex, pick from the tested anchors above or a nearby boutique shade. Avoid neons, pastels, and pure black — they break the boutique-poster mood.
2. **Lock the shop name + subtitle.** The sign is the focal type. If the user gives only a name, invent a tasteful subtitle that matches the archetype (e.g. boulangerie → "BOULANGERIE", florist → "FLOWERS · PLANTS · GIFTS", ramen → katakana transliteration).
3. **Choose the perspective.** Default to flat facade for L1; switch to 3/4 corner when the archetype benefits from depth (florist with spilling pots, ramen in an alley, wine bar with sidewalk seating).
4. **Pick foreground props that fit the archetype.** Bike/A-frame for café/bakery. Planters/sandwich-board for florist. Lanterns/scooter/noren for ramen. Bistro tables/lemon tree for wine bar. Never reach for the same prop set every time.
5. **Calibrate foliage.** Sparse for tight L1 facades. Overgrown for romantic L2 floristry. None for urban L3 ramen alleys.
6. **Set complexity.** Default to L1 unless the brief explicitly asks for a fuller scene. L3 is a rare treat — don't reach for it by default.

## Reference pieces

Reference assets are under this resource directory:

- `ref-l1-petit-pain.png` — anchor (L1, cobalt blue, boulangerie, flat facade)
- `ref-l2-fleur-fern.png` — secondary anchor (L2, forest green, florist, 3/4 corner)
- `ref-l1-lupo.png` — smoke-test piece (L1, burgundy, Italian wine bar, flat facade)

## Example briefs

**Brief 1 — L1 / cobalt blue / boulangerie / flat facade**
> Shop: "PETIT PAIN" with subtitle "BOULANGERIE". Ink: `#1f4ec9`. Perspective: flat facade. Props: a vintage bicycle leaning on the wall, an A-frame chalkboard, two terracotta planters with trailing ivy on either side of the door. Foliage: sparse. L1.

**Brief 2 — L2 / forest green / florist / 3/4 corner**
> Shop: "FLEUR & FERN" with subtitle "FLOWERS · PLANTS · GIFTS". Ink: `#2f5b3a`. Perspective: 3/4 corner showing front and side. Props: overflowing planters and pots spilling onto the sidewalk, hanging baskets above the door, a sandwich-board easel, a woman with a tote walking past in profile. Foliage: overgrown. L2.

**Brief 3 — L1 / burgundy / Italian wine bar / flat facade**
> Shop: "LUPO" with subtitle "VINI · APERITIVI". Ink: `#7a1f2b`. Perspective: flat facade. Props: two small bistro tables with curved iron chairs, a chalkboard menu on an A-frame, a cat under one of the tables, a small planter with a lemon tree on the sidewalk. Foliage: climbing vines around the upper windows. L1.

**Brief 4 — L3 / charcoal indigo / ramen counter / 3/4 alley**
> Shop: "AKIRA RAMEN" with katakana subtitle "アキラ ラーメン". Ink: `#1f2547`. Perspective: 3/4 corner looking down a narrow alley. Props: paper lanterns strung across the entrance, a noren curtain partly open, a vintage Vespa at the curb, a man in a flat cap walking past with an umbrella, a hand-painted standing sign with a bowl-of-ramen icon, overhead wires criss-crossing between buildings, faint steam wisps from a vent. Foliage: none. L3.

## Anti-patterns

- **Engraving / etching drift** — if linework gets too tight, hatched, or Victorian-engraving-like, the piece stops feeling like a boutique poster. Push for airy, sparse, confident strokes with paper showing through.
- **Vector-perfect signage** — the shop sign must look hand-lettered, not Illustrator-clean. Slight wobble and personality.
- **Multiple ink hues** — every stroke must be the same single color. No accent, no second hue, no separate shadow color.
- **Empty facade** — always include foliage AND at least one street prop. A bare building reads as a technical drawing.
- **Missing sidewalk line** — the faint ground line at the bottom is part of the locked frame. Skip it and the piece floats.
- **Generic relabeled shop** — the props must fit the archetype. A bicycle + A-frame in front of a ramen counter is wrong; lanterns + scooter + noren is right.

## Output expectations

A portrait 1024×1536 PNG, register-only style. The output should pass these quick checks:

- One ink hue across the entire piece, sitting on cream paper.
- Hand-lettered shop sign readable as the focal type element.
- Foliage and at least one street prop visible in the foreground.
- Faint horizontal sidewalk line across the bottom.
- Paper showing through generously — not packed with hatching.
