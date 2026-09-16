---
name: ink-mascot
description: Generate a vintage editorial marketing card in a locked style — hand-drawn ink line illustration of an anthropomorphic object (with stick arms, legs, and chunky white sneakers) standing on a single solid saturated color background, topped with a bold serif headline and short serif descriptor. Trigger when the user says /ink-mascot, asks for a "marketing card illustration", "retro editorial mascot poster", "ink mascot card", or briefs with a marketing concept + palette + character.
---

# ink-mascot

Generates a portrait 3:5 editorial marketing card in a locked vintage-textbook style: bold serif headline, optional short serif descriptor, and a hand-drawn black-ink anthropomorphic mascot floating on a single solid saturated color background.

The output looks like a page lifted from a 1970s marketing primer — playful, didactic, slightly absurd. Each invocation swaps the **concept, palette, hero object, action, doodle density, and type layout**. Everything else is locked.

## Prompt interpretation

The user briefs in some loose combination of:
- a **concept** (a marketing word — "Branding", "SEO", "Loyalty", "Launch"...),
- a **color or mood**,
- a **character idea** (object, prop, tool that fits the concept).

Expand the brief — fill in any missing dials with sensible defaults, write a one-sentence descriptor if not provided, and pick a hero object that *visibly is* the concept at first glance. Do not stall asking the user to flesh it out; make confident choices and run.

If the user briefs a **series** (e.g. "make me a 6-card marketing curriculum"), pick visibly distinct palettes across the set, vary the hero object and action so every card silhouette reads differently, and hold the type layout consistent across the set unless explicitly asked to vary it.

## Locked style (NEVER vary)

### Canvas and fill
- Tall portrait orientation, 3:5 aspect — well-suited to 1024×1536.
- **One single saturated, slightly-muted flat color fills the canvas edge to edge.** No gradient, no texture, no border frame, no horizontal divider line, no ground line under the character, no separator panel. Text and illustration share the exact same flat color field.

### Ink and line quality
- All artwork in **black ink line work only.** Thin to medium confident outlines.
- **Clean white interior fills** inside every shape so the colored background does not bleed through the character.
- Crosshatch and stipple shading on rounded surfaces — restrained, supporting form, not decorative.
- No color anywhere inside the line art (only black ink + white fill on the colored background). No airbrush gradients, no 3D modeling shading, no photo realism, no drop shadow on the character.

### Type
- Bold black serif (Playfair-style display serif) headline.
- Optional short serif descriptor in the same family, lighter weight, 1–2 lines.
- The headline must be tightly bound to the concept and feel like a chapter heading from an editorial textbook.

### Character anatomy (the locked through-line)
The hero is an anthropomorphic **object**, not a creature. The object IS the body. It always has:
- Two thin black stick arms emerging from the sides.
- Two thin black stick legs.
- **Chunky white sneakers with black laces, toe caps, and visible outsole.** This is the signature detail — never skip it.
- Optional simple face: two dot eyes + tiny smile. Omit the face if the object's silhouette already feels alive.

### Floating ink doodles
Small black-ink props orbit the character on the colored field — sparkles, arrows, hearts, percentage/dollar/at signs, paper drops, motion lines, tiny duplicates of the hero, hashtags, ticks, question marks, lightning bolts, light bulbs, clouds, stars. **Never** contain them in a frame; they float freely.

### Forbidden
- Photographic mockups, 3D shading, airbrush gradients.
- Ground lines, baselines, horizontal dividers, frame borders.
- Drop shadows under the character or under the text.
- Colored fills inside the line art (only black ink + white fill).
- Generic stock mascots with no relation to the concept. The hero must visibly be the concept.

## Dialable axes (vary per invocation)

### 1. CONCEPT — headline word(s)
The chapter heading. Marketing concepts work best. Examples:
`Branding` · `SEO` · `Email marketing` · `Conversion` · `Loyalty` · `Retention` · `Pricing` · `Positioning` · `Storytelling` · `Community` · `Referrals` · `Launch` · `Growth` · `Attribution` · `Personalization` · `A/B testing` · `Targeting` · `Online advertising` · `Multichannel marketing` · `Analytics`.

The concept drives *everything else*: hero object, doodle vocabulary, even the palette's emotional register.

### 2. PALETTE — single solid background hex
One saturated, slightly-muted hue. Avoid pure pastels and avoid black/white/gray.

| name | hex |
| --- | --- |
| orange | `#F08C4A` |
| cream sage | `#D9DEC2` |
| sunshine yellow | `#FFD93D` |
| sky blue | `#7FB6E6` |
| mint teal | `#9FD9C2` |
| coral peach | `#F4A896` |
| lavender | `#C7B8E8` |
| dusty terracotta | `#D88880` |
| sage olive | `#B5C088` |
| mustard | `#E8C547` |
| cobalt | `#4A6FB5` |
| rose | `#E8A2B0` |
| plum | `#8C6BA8` |
| rust | `#C26B4B` |
| forest | `#5C8A6E` |
| slate | `#7A8B9C` |
| butter cream | `#F2E0A8` |
| tangerine | `#E89A4F` |
| pistachio | `#C5D89B` |

**Default:** pick a hue that fits the concept's emotional register (growth → green family, urgency → red/orange, trust → blue, premium → plum/cobalt). For a series, pick distinct hues so the set reads cohesively on a shelf.

### 3. HERO — anthropomorphic object
Pick a **theme-native** prop, not a generic mascot. Examples paired with concepts:

| concept | hero |
| --- | --- |
| Branding | paint bucket, stamp, brush |
| SEO | magnifying glass |
| Email marketing | envelope, mailbox |
| Content marketing | notebook, fountain pen, quill |
| Conversion | funnel |
| Online advertising | megaphone |
| Multichannel marketing | browser window |
| Targeting | bullseye, dartboard |
| Analytics | chart, dashboard panel |
| Positioning | compass, lighthouse |
| Loyalty | gift box, badge |
| Pricing | price tag, coin stack |
| Launch | rocket, flag |
| Growth | seedling, watering can |
| Referrals | gift box passing a duplicate |
| Community | speech-bubble cluster |
| A/B testing | scales, split tube |

**Default:** if the concept is unfamiliar, pick the most iconic theme-native prop — what would appear next to this concept in a marketing textbook glossary.

### 4. ACTION — what the character is doing (pose verb)
Drives the energy. Both hands should be doing *something*.

- `holding` — static, calm
- `pressing/stamping` — concentrated, decisive
- `launching` — paper airplane, rocket, projectile
- `painting/writing/drawing` — making something
- `catching/receiving` — incoming object
- `pointing/presenting` — gesturing at a prop
- `running/skating` — motion, hustle
- `peering/inspecting` — magnifying, investigating
- `juggling` — multi-tasking
- `building/stacking` — incremental progress
- `planting/watering` — growth, nurture

**Default:** the action most tightly bound to the concept's verb (Branding → stamping, SEO → peering, Launch → launching).

### 5. DOODLE DENSITY — floating ink props
- **L1 — minimal**: 0–2 props. Calm, lots of negative space.
- **L2 — balanced** (default): 3–5 props.
- **L3 — packed**: 6–8 props. Busy, energetic.

Props should be theme-relevant doodles drawn in the same ink language as the character: sparkles, arrows, hearts, currency/at signs, paper drops, motion lines, tiny duplicates of the hero, hashtags, ticks, question marks, lightning bolts, light bulbs, clouds, stars.

### 6. TYPE LAYOUT — where the words sit
- **A** — Title top, descriptor below, illustration fills bottom *(default)*.
- **B** — Illustration top, headline anchored at bottom. No descriptor.
- **C** — Headline only, no descriptor (cleanest, poster-like).
- **D** — Big single-word headline + tiny one-line descriptor (max contrast).

## Worked examples

### Example 1 — Default (Layout A, L2 balanced)
**Brief:** "Loyalty, plum, gift box"

**Dial fill:**
- Concept: Loyalty
- Palette: plum #8C6BA8
- Hero: gift box (square wrapped present with a tied ribbon and bow)
- Action: holding the ribbon up like a banner
- Doodle density: L2 (4 props — sparkle, heart, confetti streamer, tiny duplicate mini gift box)
- Type layout: A (headline "Loyalty" top, two-line descriptor below)

**See** `ref-loyalty-plum.png`.

### Example 2 — Bottom-anchored headline (Layout B, L3 packed)
**Brief:** "Launch, tangerine, rocket, energetic"

**Dial fill:**
- Concept: Launch
- Palette: tangerine #E89A4F
- Hero: capsule-shaped rocket with porthole window, fins, pointed nose cone
- Action: launching upward with motion lines streaming behind; right hand raises a small flag, left hand holds a tiny clipboard
- Doodle density: L3 (7 props — three cloud puffs trailing below, two sparkles, upward arrow, tiny duplicate mini rocket, star, checklist tick, lightning bolt)
- Type layout: B (illustration fills upper canvas, "Launch" anchored at the bottom)

**See** `ref-launch-tangerine.png`.

### Example 3 — Headline only, minimal density (Layout C, L1)
**Brief:** "Growth, forest green, seedling, calm"

**Dial fill:**
- Concept: Growth
- Palette: forest #5C8A6E
- Hero: small pot with a young sprouting plant (central stem + two curving leaves); pot is the torso
- Action: gently cupping one of its own leaves, looking down at it tenderly
- Doodle density: L1 (just 2 props — one water droplet falling from above + one sparkle near the top leaf)
- Type layout: C (headline "Growth" top, no descriptor, generous negative space)

**See** `ref-growth-forest.png`.

## Reference outputs (in this folder)

| File | Concept | Palette | Hero | Action | Density | Layout |
|---|---|---|---|---|---|---|
| `ref-branding-mint.png` | Branding | mint teal `#9FD9C2` | paint bucket | painting star + brush | L2 | A |
| `ref-seo-coral.png` | SEO | coral peach `#F4A896` | magnifying glass | peering at browser window | L2 | A |
| `ref-email-lavender.png` | Email marketing | lavender `#C7B8E8` | envelope | launching paper plane + holding letters | L2 | A |
| `ref-content-terracotta.png` | Content marketing | dusty terracotta `#D88880` | open notebook | writing with fountain pen, "STORY" banner | L3 | A |
| `ref-conversion-sage.png` | Conversion | sage olive `#B5C088` | funnel | catching falling figures, star emerging | L3 | A |
| `ref-loyalty-plum.png` | Loyalty | plum `#8C6BA8` | gift box | holding ribbon like a banner | L2 | A |
| `ref-launch-tangerine.png` | Launch | tangerine `#E89A4F` | rocket | launching, motion lines, flag + clipboard | L3 | B |
| `ref-growth-forest.png` | Growth | forest `#5C8A6E` | potted seedling | cupping own leaf | L1 | C |

When in doubt, match these eight.

## Output expectations

A single invocation should return one PNG file with:
- 3:5 portrait aspect (1024×1536 canonical)
- Edge-to-edge solid saturated flat color background, no gradient or divider
- Bold black serif headline (and optional descriptor, depending on layout)
- One anthropomorphic hero object in black ink line work with white interior fills, stick arms/legs, **chunky white sneakers with black laces**, optional simple face
- Crosshatch/stipple shading restrained to rounded surfaces
- 0–8 floating ink doodles (matching the requested density level)
- No drop shadow, no frame, no ground line

## Self-check before delivering

- ☐ Background is one flat saturated color, no gradient or divider.
- ☐ Character has chunky white sneakers with black laces (locked signature).
- ☐ Line work is black ink only — no fills colored other than white inside shapes.
- ☐ Headline is a bold serif; descriptor (if present) is the same family lighter.
- ☐ Floating doodles match the requested density level.
- ☐ Hero object is theme-native to the concept, not a generic mascot.
- ☐ Layout follows the requested A/B/C/D pattern.

If any check fails, regenerate with a tightened prompt before sharing.

## Portability notes

- The locked style and 6 dials describe **what to produce**, not which endpoint to call. The resource is provider-agnostic at the semantic level.
- The reference set in this folder was produced with a GPT Image-family model at 1024×1536, high quality. Models with weak in-image text rendering will tend to garble the serif headline; if you see broken lettering, switch to a model that handles in-image text well (e.g., GPT Image 1 / 1.5).
- The chunky white sneakers are the most under-prompted detail. If a model is dropping them, lean harder in the prompt ("two thin black stick legs ending in chunky white sneakers with visible black laces, toe caps, and outsole").
- Series consistency: keep the sneakers + serif type + flat color as the through-line; vary palette, hero, action, density, and layout. Never repeat a palette across a single series.
