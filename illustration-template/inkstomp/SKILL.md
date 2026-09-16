---
name: inkstomp
description: Inkstomp — a loud, hand-screened indie-packaging poster style. Full-bleed saturated flat color filling the entire canvas, a two-line hand-lettered headline (thin arched caps over chunky drop-shadowed display), and one weird-cute character drawn in thick uniform black brush ink. Trigger when the user says /inkstomp, asks for an "inkstomp poster", a "Ray Fenwick / Hattie Stewart packaging poster", an "indie brush-ink flavor card", or briefs in a "palette + headline + character" shape.
---

# /inkstomp — locked indie-packaging brush-ink poster style

Inkstomp produces a single tall portrait poster with the energy of a hand-screened indie packaging design: one saturated flat color filling the canvas edge to edge, a confident two-line hand-lettered headline at the top, and one weird-cute character drawn in thick uniform black brush ink occupying the lower two-thirds. The character is the *concept* — it always visibly matches the headline.

Each invocation swaps the **palette, headline, character, and a handful of dialable creative axes**. Everything else is locked.

## Prompt interpretation

The user will brief in some loose combination of:
- a color or mood,
- a two-word headline (or just a noun for the second line),
- a character idea (object, food, creature, hybrid).

It is your job to expand the brief — fill in any missing axes with sensible defaults, write an alliterative two-line headline if only the noun was given, and pick a character archetype + anthropomorphism level + action that *reads* as the headline at first glance. Do not stall asking the user to flesh it out. Make confident choices and run.

If the user briefs a **series** (e.g. "make me 4 inkstomp flavors"), choose 4–6 visibly distinct palettes from across the palette categories, write alliterative headlines, and vary the anthropomorphism level and action across the set so they don't all read as the same silhouette.

## Locked style axes (NEVER vary)

### Canvas and fill
- Tall portrait orientation, intended for a 2:3-ish aspect ratio (well-suited to 1024×1536).
- **The entire canvas is edge-to-edge filled with one saturated flat color.** No border, no white margin, no paper backdrop, no drop shadow on the canvas itself, no gradient, no texture. Solid uniform color from corner to corner.
- The character and lettering sit directly on this color — there is never a secondary background panel.

### Ink and line quality
- All artwork in **thick uniform black brush ink only.** No other colors anywhere. No fills inside the line work — the colored canvas shows through every shape interior.
- Hand-drawn, slightly uneven, confident. Each line feels brush-painted, not vector-traced.
- No shading, no hatching, no cross-hatching, no halftone, no gradients. Flat black ink on flat color.

### Headline (always present)
- Two-line headline anchored in the **top third** of the canvas.
- **Line 1:** thin all-caps brushed letters, gently arched. This is the *modifier* — adjective, onomatopoeia, mood word.
- **Line 2:** much bigger, blockier, chunky display caps, with a heavy **black drop shadow offset down-right.** This is the *noun*.
- Both lines are clearly hand-lettered with a brush pen — uneven baselines, organic spacing, NOT a font. Slight wobble in the strokes.
- The headline must be readable at a glance and tightly bound to the character below it.

### Character (always present)
- Exactly **one** character, occupying the center and lower two-thirds of the canvas.
- Drawn in the same thick uniform black brush ink as the headline. Interiors are the canvas color showing through.
- Has at least two simple dot eyes and a visible mouth (smile, smirk, open laugh, grimace, etc.).
- Slightly absurd, weird-cute, indie hand-screened poster vibe. Cousin to Ray Fenwick / Hattie Stewart / "Mr Men" personified-object aesthetics.

### Signature
- A tiny "R.H." monogram in the **lower right corner** in black brush ink. This is the locked signature; if the user explicitly asks for a different monogram, use theirs, otherwise default to "R.H.".

### Things to avoid
- Photographic mockups, paperboard box renders, shelf scenes, or any 3D framing — inkstomp posters are flat 2D, not product photos.
- Drop shadows on the character or canvas (only the headline display word has a shadow).
- Color anywhere other than the canvas fill — no orange peel highlight, no green leaf, no red accent. Color goes in the background only; everything else is black ink.
- Gradients, halftone shading, painterly brush textures inside shapes.
- Off-style faces — no realistic eyes, no detailed pupils with glints, no anime mouth.
- Generic stock characters with no relation to the headline. The character must **visibly be the noun**.

## Dialable axes (vary per invocation)

Brief along whichever the user cares about; fill in the rest with the defaults listed.

### Axis 1 — Palette
A single saturated flat color filling the entire canvas. Pick the **energy** first, then the hue.

| Category | Sample hues |
|---|---|
| **Punchy / hot** | coral red, hot pink, neon yellow, sunset orange, lime, vermillion |
| **Saturated cool** | cobalt blue, deep purple, jade teal, electric blue, ultramarine |
| **Dusty / muted** | mauve gray, terracotta, mustard ochre, sage, oat, dusty rose |

For a series, pick 4–6 visibly distinct hues that read well as a shelf. Avoid muddy mid-tones and pastels — the style needs saturation to land.

**Default if unspecified:** a hue that *contrasts* with the character's natural color (e.g. warm food → cool background, cool drink → warm background).

### Axis 2 — Headline pair
Two words, hand-lettered in the locked format above.

- The pair almost always benefits from **alliteration** ("MOODY MUSHROOM", "TURBO TOFU", "CRUNCHY CRICKET").
- Sub-pattern: **repetition or rhythm doubles** ("CLIMB / CLIMB", "GO GO GOJI BERRY", "ESPRESSO SO-SO") create a stronger gestalt than a modifier+noun pair when you want extra punch.
- Line 1 should be short (4–8 letters); line 2 should be the visually dominant noun.

**Default if only a noun is given:** invent an alliterative modifier on line 1 that matches the character's vibe ("WILD / WAFFLE", "JOLLY / JALAPEÑO").

### Axis 3 — Character archetype
What the figure fundamentally **is**.

- **A1** Anthropomorphic food / drink (waffle stack, coffee bean, jalapeño, plum)
- **A2** Personified object / tool (stapler, telephone, lava lamp, suitcase)
- **A3** Creature / bug / small animal (cricket, snail, frog, slug, moth)
- **A4** Hybrid chimera — an object replaces a body part (frying-pan-as-head, espresso-mug-as-head)
- **A5** Pure abstract shape with a face (blob, lump, melting puddle)

**Default:** A1 for food/flavor briefs, A2 for office/everyday briefs, A3 for nature/weird briefs.

### Axis 4 — Anthropomorphism level
How human the figure has become.

- **L1** Face on the object + tiny stubs (smiling fruit with two little legs)
- **L2** Full body — object grows full arms + legs
- **L3** Object-as-head — human body in clothing with the object literally replacing the head
- **L4** Object operating other objects (banana driving a car, plum holding a cannon)
- **L5** Object as machine / contraption (cockroach strapped to a rocket, blackcurrant as cannon ammunition)

**Default:** L2 for food/creature, L3 for office/everyday objects when the brief calls for "weirder", L5 only when the brief leans absurd.

### Axis 5 — Action energy
What the figure is *doing*.

- **E1** Static portrait — standing, arms crossed, posed
- **E2** Interacting with a small prop — holding, eating, pointing, catching
- **E3** Mid-motion — running, falling, leaping, climbing
- **E4** Reacting — winking, wincing, shouting, laughing, blushing
- **E5** Operating — driving, firing, throwing, riding

**Default:** E2 — gives the character a clear concept-hook and tends to read fastest.

### Axis 6 — Weirdness dial
How far from "cute" toward "absurd".

- **W1** Friendly cute (smiling fruit with simple face) — feels closer to a kids' brand
- **W2** Quirky (one weird detail — oversized tongue, mismatched limbs, eye on the wrong side)
- **W3** Weird (hybrid bodies, object-as-head, slight surrealism) — **the inkstomp sweet spot**
- **W4** Absurd (impossible scenarios, contraptions, machine-creature hybrids)

**Default:** W3. The locked reference set leans W3–W4; anything below W2 starts to feel off-style.

### Axis 7 — Ink motifs
Small black-ink extras around the figure that add life. Keep them subtle and asymmetric — they support the action, they never crowd the character.

- ✦ sparkles, four-point stars, tiny dots
- motion lines, speed swooshes, drip lines, slime trails
- dust puffs, sweat drops, exclamation marks, question marks
- micro-props the character is interacting with (cracker, sugar cube, helmet, briefcase, paper note)
- a hand-lettered callout in a little balloon ("POP!", "WHOO!", "BYE")

**Default:** 2–3 motifs picked to support the chosen action.

### Axis 8 — Composition
Where the headline and figure sit relative to each other.

- **C1** Headline top third, figure centered in the lower two-thirds — **the default**
- **C2** Headline arched over the figure's head — circus-poster feel
- **C3** Figure climbs, sits on, or breaks the letters of the headline itself
- **C4** Headline and figure side by side (figure stretches tall on one side)
- **C5** Oversized figure breaks above or around the headline (figure dominates the canvas)

**Default:** C1. Reach for C3 or C5 when you want the figure to feel kinetic or when the headline is a verb like "CLIMB" or "STOMP".

## Worked examples

### Example 1 — Single poster, default axes
**User brief:** "an inkstomp poster for crunchy cricket, coral red background"

**Axis fill:**
- Palette: coral red (given)
- Headline: "CRUNCHY / CRICKET" (alliteration, line 1 thin arched, line 2 chunky shadowed)
- Archetype: A3 cricket
- Anthropomorphism: L2 full body
- Action: E2 holding a small cracker, nibbling it
- Weirdness: W3
- Motifs: a crumb mark, a tiny grin line, one wing detail
- Composition: C1

**See** `ref-crunchy-cricket.png` for the reference output.

### Example 2 — Object-as-head (L3) absurd lean
**User brief:** "make it weirder — orange background, GREASY GRIDDLE"

**Axis fill:**
- Palette: sunset orange
- Headline: "GREASY / GRIDDLE" (alliteration; line 1 thin arched, line 2 chunky shadowed)
- Archetype: A4 hybrid chimera
- Anthropomorphism: L3 — human body in apron, head replaced by an actual cast-iron frying pan
- Action: E2 flipping a tiny egg in a spatula
- Weirdness: W3
- Motifs: three steam squiggles, two grease drops, a "POP!" starburst near the egg
- Composition: C1

**See** `ref-greasy-griddle.png` for the reference output.

### Example 3 — Composition test (C3 — figure on the letters)
**User brief:** "hot pink, headline CLIMB CLIMB, snail, the snail should climb on the letters"

**Axis fill:**
- Palette: hot pink
- Headline: "CLIMB / CLIMB" (repetition doubles — stronger gestalt for a verb headline)
- Archetype: A3 snail
- Anthropomorphism: L1 (face + stalk eyes + small foot, no full human body)
- Action: E3 climbing
- Weirdness: W3
- Motifs: slime trail looping across the upper letters, a sweat drop, two tiny ink dots
- Composition: **C3** — the snail's body is perched between the two CLIMB lines, one foot on the "M"

**See** `ref-climb-climb.png` for the reference output.

### Example 4 — Series of four
**User brief:** "do me a 4-flavor inkstomp series"

**Axis fill (vary across the set):**
- 4 contrasting palettes (e.g. coral red / golden yellow / deep purple / mint teal)
- 4 alliterative headlines
- Vary archetype across A1, A1, A1, A1 (food series stays cohesive) — but vary action and anthropomorphism level
- Hold weirdness at W3 across the set so they read as one family

**See** `ref-crunchy-cricket.png`, `ref-jolly-jalapeno.png`, `ref-pocket-plum.png`, `ref-turbo-tofu.png` for a reference 4-set with consistent style.

## Reference outputs (in this folder)

The eight reference posters in this directory are the canonical look. When in doubt, match these.

| File | Palette | Headline | Archetype + Anthropomorphism | Action | Weirdness | Composition |
|---|---|---|---|---|---|---|
| `ref-crunchy-cricket.png` | coral red | CRUNCHY / CRICKET | A3 cricket, L2 full body | E2 holding cracker | W3 | C1 |
| `ref-jolly-jalapeno.png` | golden yellow | JOLLY / JALAPEÑO | A1 jalapeño, L2 full body | E4 winking laugh, waving arm | W3 | C1 |
| `ref-pocket-plum.png` | deep purple | POCKET / PLUM | A1 plum, L2 full body | E2 catching sugar cube | W3 | C1 |
| `ref-turbo-tofu.png` | mint teal | TURBO / TOFU | A1 tofu cube, L2 full body | E5 race-driver thumbs-up | W3 | C1 |
| `ref-greasy-griddle.png` | sunset orange | GREASY / GRIDDLE | A4 chimera, L3 pan-as-head | E2 flipping egg | W3 | C1 |
| `ref-quiet-quitter.png` | sage green | QUIET / QUITTER | A2 stapler, L2 full body | E3 sneaking off | W3 | C1 |
| `ref-rocket-roach.png` | cobalt blue | ROCKET / ROACH | A3 roach, L5 strapped to rocket | E5 blasting off | W4 | C1 |
| `ref-climb-climb.png` | hot pink | CLIMB / CLIMB | A3 snail, L1 | E3 climbing letters | W3 | **C3** |

## Output expectations

A single invocation should return one PNG file with:
- ~2:3 portrait aspect (1024×1536 is the canonical size)
- Edge-to-edge saturated flat color background
- Two-line hand-lettered black-ink headline in the top third
- One single weird-cute character in black brush ink in the lower two-thirds, clearly matching the headline
- Tiny "R.H." monogram in the lower right corner

When generated through a model that can render hand-lettering text accurately (the OpenAI GPT Image family is the proven path for inkstomp), the result should be visually indistinguishable in style from the reference set above, varying only on the chosen axes.

## Portability notes

- This resource is provider-agnostic at the semantic level. The locked style and the 8 axes describe **what to produce**, not which endpoint to call.
- The reference set in this folder was produced with a GPT Image-family model at 1024×1536 high quality. Models with weaker text rendering will tend to garble the hand-lettered headline; if you see broken lettering, switch to a model that handles in-image text well.
- The "R.H." monogram is a stylistic anchor, not a brand mark. Treat it as part of the locked composition.
