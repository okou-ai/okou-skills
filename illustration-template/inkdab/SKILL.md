---
name: inkdab
description: Brush-pen editorial illustration with a single free-floating accent color "dab" sitting underneath loose ink linework. Black hand-wobbled ink on pure white background, ONE flat accent-color shape per prop (painted-first, never outlined in black), scribbled hatched hair, open-outline bodies with zero fill, and one small solid-accent triangle floating freely as a recurring motif. Trigger when user says /inkdab, asks for an "inkdab illustration", a "brush-pen illustration with a single accent color", a "free-floating color block illustration", or briefs in the style of the included reference images.
---

# /inkdab — locked brush-pen + single-accent-color editorial illustration

The name comes from the style's two-layer construction: a flat color **dab** painted first, then loose **ink** drawn freely on top. The dab is never outlined; the ink never frames it. They overlap imperfectly.

This skill produces editorial spot illustrations in a hand-drawn brush-pen style with exactly ONE flat accent color and a strict free-floating color rule. Each invocation swaps the **palette, cast, scene, and density**; every other style axis stays locked.

The style is friendly, business-appropriate, and reads instantly as a small captured moment — never busy, never decorative for its own sake.

## Prompt interpretation

The user usually provides a short brief — palette + scene archetype + maybe a cast hint. Expand it into a specific vignette using the framework below. Do not ask the user to fill in every dial; pick reasonable defaults from the modifier axes.

For each invocation:

1. **Resolve the 4 primary axes** — palette, cast, scene (archetype : action), and density. These are required decisions. If the user omitted any, choose a default that fits the context.
2. **Derive the modifier axes** — pick 1–4 props from the prop vocabulary, the ink decorations that go on each, and per-character traits (hair, glasses). The number of props is governed by density.
3. **Compose the moment** — single character or pair, slightly off-center if it helps the gesture read; props arranged to support the action; always include the one floating solid-accent triangle accent.
4. **Restate every locked rule in the generation prompt** — the underlying model does not retain style constraints between calls. The free-floating-color rule and pure-white-background rule must be spelled out explicitly each time.

## Locked style axes (NEVER vary)

### Background
- Pure white `#FFFFFF`, completely flat, edge to edge.
- **No vignette, no edge shading, no gradient darkening, no gray corners, no paper texture, no border, no off-white tone.**
- This rule is the most commonly violated by the underlying model under busy prompts — always restate it explicitly and include an explicit negative list (no vignette, no gray corners, no sepia, no beige).

### Linework
- Black brush-pen ink, hand-wobbled, single medium weight.
- Confident, slightly imperfect — visible pressure variation, organic micro-wobbles.
- NOT digital-clean, NOT vector, NOT marker-uniform-thickness.

### Palette
- Black ink + exactly ONE flat accent color.
- No second hue, no gradient, no shading inside the accent shape.
- The accent color is allowed to have very subtle marker-like streak texture inside the shape — this is fine and expected.

### Accent-color shapes (critical — the defining rule)
- Each accent-color shape is a **free-floating** painted-first shape.
- Edges are rough, slightly fuzzy, uneven, often visibly hand-painted.
- **Black ink NEVER traces the perimeter of any accent-color shape.** Not the outer edge of the apron, not the bag silhouette, not the laptop body, not the package box, not the screen frame. Every accent shape must have edges where the color sits on white directly, with no black outline.
- Black ink details that appear *on* the color (a chart icon, wavy text squiggles, a checkmark, a `$` mark) sit directly **on top of** the color as loose squiggles. They are NEVER framed by a black border, NEVER drawn inside a black container.
- Treat the two as independent layers: the color is painted down first as a flat shape, the ink linework is then drawn freely on top of and beside it. They overlap imperfectly — the color often extends past the ink by a few pixels at one or two edges.

### Furniture rule
- Desks, tables, counters, floors, ground lines, whiteboard stands, and similar **structural surfaces** are drawn as plain black ink lines only.
- Accent color is reserved for **handheld, worn, or focal props** (papers, bags, devices, aprons, packages, signs, mugs, books).
- Coloring furniture makes the composition visually heavy and breaks the style.

### Hair
- Scribbled separate ink strokes that overlap to suggest curls or volume.
- **White paper visible between strokes** — never a solid black mass, never a filled silhouette.
- Strokes are countable; the texture reads as a tangle of loose curls.

### Face
- One small dot for the eye, one short upward smile curve.
- Optional simple oval glasses laid on top of the face (round or square frames).
- No nose, no eyebrows, no nostrils — minimal.
- For a more peaceful or focused expression, the eye can be a small closed-crescent arc instead of a dot.

### Body / clothing
- Pure open ink outline only.
- **Zero fill, zero shading, zero hatching.** Shirts, sweaters, pants, shoes are all just contour lines on white.
- Sleeves, collars, and cuffs can have small visible breaks where the brush lifted — this is welcome but not required.

### Triangle accent (recurring motif)
- One small solid-accent-color equilateral triangle floats freely on the white space of every illustration.
- Position varies — lower-right is default; lower-left, upper-right, and upper-left are all valid.
- The triangle has no outline and no ink details on it.

### Composition
- Single primary character (or a small pair when the action requires it).
- Square-ish vignette, generous white margins.
- No environment, no horizon, no background scenery, no shadow.
- A single thin black ink ground line under the feet is allowed but not required.

### Mood
- Friendly, business-appropriate, candid. A small captured moment with energy.

## Variable axes — 4 primary + 3 modifiers

### Primary axes (must specify)

**① Palette** — one accent color. Defaults to soft cornflower blue `#8BB8E5`. Other palettes that have been tested and read well in this style:
- `blue` `#8BB8E5` (default — work / business / tech vignettes)
- `dusty-pink` `#E5A5B5` (service / care / logistics vignettes)
- `lavender` `#B8A8D8` (personal / cozy / reflective vignettes)
- `butter-cream` `#F2D67A` (collaboration / brainstorming / warm-work vignettes)
- `coral` `#F08E7E` (reading / energy / playful vignettes)
- `mustard` `#E0B040` (coworking / cafés)
- `sage` `#9BB89A` (focus / craft / design)
- `terracotta` `#C97A5A` (service / café / retail)

**② Cast**
- `solo` — single character
- `pair-equal` — two peers in conversation or collaboration, equally engaged
- `pair-asymmetric` — one foreground / lead character + one observer / peeker behind them
- `pair-transactional` — one giver + one receiver (delivery, sale, handoff)

**③ Scene** — written as `archetype : action`
- `work : presenting` / `focusing` / `collaborating` / `brainstorming` / `debugging`
- `service : serving customer` / `handing off package` / `taking order`
- `comms : calling` / `messaging` / `video meeting`
- `motion : commuting` / `delivering` / `walking`
- `personal : reading` / `sketching` / `drinking coffee`
- `transaction : paying` / `receiving`

**④ Density**
- `light` — exactly 1 prop, 0–1 ambient mark; intentionally spare composition with strong negative space
- `medium` — 2 props, 1–2 ambient marks, one clear gesture
- `rich` — 3–4 props, 2–3 ambient marks, layered gesture + multiple ink-on-color details

### Modifier axes (optional — defaults derived from the scene)

**⑤ Prop vocabulary** (pick 1–4 depending on density)
paper · clipboard · open book · briefcase · tote bag · apron · uniform · phone · card terminal · screen / laptop · package box · large sign / chart-poster · badge · mug · ticket · envelope · sketchbook · whiteboard · sticky note · marker · plant pot · tip jar

**⑥ Ink decoration vocabulary** (what gets scribbled on each prop)
3 wavy text lines · small bar chart · upward arrow · checkmark · dotted grid · small icon · single squiggle · small face · `$` or `%` · `!` · short word in caps (e.g., `OPEN`, `TIP`, `WIFI`)

**⑦ Character traits** (per character)
- Hair: `short crop` · `messy curls` · `long curls` · `bun` · `short bob`
- Glasses: `none` · `round oval` · `square oval`
- Other: clean-shaven by default; facial hair sparingly

## Brief template

```
Palette:    {accent color}
Cast:       {solo | pair-equal | pair-asymmetric | pair-transactional}
Scene:      {archetype}: {action}
Density:    {light | medium | rich}
Props:      {optional — overrides scene defaults; 1–4 accent-color props}
Ink:        {optional — overrides density defaults; squiggle marks on each prop}
Character:  {optional — hair, glasses per character}
```

### Worked examples

**Pitch moment (rich pair):**
```
Palette:    blue
Cast:       pair-asymmetric
Scene:      work: presenting
Density:    rich
Props:      large chart-poster, small clipboard
Ink:        rising bar chart + upward arrow on poster, 2 short lines on clipboard
Character:  presenter — short curls + round glasses; peeker — messy curls
```
→ Foreground presenter holds the chart-poster, peeker leans in from behind their shoulder. Reference: `ref-pitch-blue.png`.

**Light phone call (intentionally spare):**
```
Palette:    blue
Cast:       solo
Scene:      comms: calling
Density:    light
Props:      phone
Ink:        single signal squiggle
Character:  short crop, no glasses
```
→ One character holding a phone to the ear, free hand gesturing. Strong negative space. Reference: `ref-calling-blue-light.png`.

**Package handoff (medium transactional):**
```
Palette:    dusty-pink
Cast:       pair-transactional
Scene:      service: handing off package
Density:    medium
Props:      package box, clipboard
Ink:        checkmark + squiggle on box, 2 short lines on clipboard
Character:  delivery — messy curls, no glasses; recipient — long curls + round glasses
```
→ Reference: `ref-handoff-dusty-pink.png`.

**Cozy reading (rich personal):**
```
Palette:    lavender
Cast:       solo
Scene:      personal: reading + coffee
Density:    rich
Props:      open book, mug, plant pot
Ink:        wavy text on book pages, steam wisp from mug, ink plant leaves on top of the pot
Character:  long curls + round glasses, closed-crescent eye
```
→ Reference: `ref-reading-lavender-rich.png`.

**Brainstorming pair (rich work):**
```
Palette:    butter-cream
Cast:       pair-equal
Scene:      work: brainstorming at whiteboard
Density:    rich
Props:      whiteboard, sticky note, marker
Ink:        flow arrow + wavy text + tiny diagram on whiteboard; word on sticky
Character:  left — short crop + square glasses; right — bun, no glasses
```
→ Reference: `ref-brainstorm-butter-cream-rich.png`.

## Reference images

The five PNGs in this directory are the canonical look-and-feel for this style. Any image-to-image generation backend should be passed one or more of these as style anchors. They cover the four primary axes (palette × cast × scene × density) so the generator can interpolate any combination.

| File | Palette | Cast | Scene | Density |
|---|---|---|---|---|
| `ref-pitch-blue.png` | blue | pair-asymmetric | work : presenting | rich |
| `ref-calling-blue-light.png` | blue | solo | comms : calling | light |
| `ref-handoff-dusty-pink.png` | dusty-pink | pair-transactional | service : handing off package | medium |
| `ref-reading-lavender-rich.png` | lavender | solo | personal : reading + coffee | rich |
| `ref-brainstorm-butter-cream-rich.png` | butter-cream | pair-equal | work : brainstorming at whiteboard | rich |

## Style brief structure

Use this template when asking a generative-image model to render a new piece. Replace `{{ACCENT}}`, `{{HEX}}`, and `{{SUBJECT}}` with the resolved values; keep every other rule verbatim.

```
Hand-drawn editorial spot illustration in the brush-pen + single-accent-color style shown in the reference images.

LOCKED STYLE RULES (absolute):
- BACKGROUND: pure white #FFFFFF only, completely flat. NO vignette, NO edge shading, NO gradient darkening, NO gray corners, NO paper texture, NO border, NO off-white tone. Pure white edge to edge.
- Black brush-pen ink, hand-wobbled, single medium weight.
- ONE accent color only: {{ACCENT}} (~{{HEX}}).
- Accent-color blocks are FREE-FLOATING shapes painted first with rough edges, NEVER outlined in black, NEVER framed by ink.
- Ink details on accent-color shapes = loose squiggles ON TOP, never a containing frame.
- Hair = scribbled separate strokes with white visible between curls. NEVER a solid black mass.
- Face = one dot eye (or closed-crescent arc) + short smile curve. Optional simple oval glasses. No nose, no eyebrows.
- Body / clothing = pure open ink outline. ZERO fill, ZERO shading, ZERO hatching.
- Furniture (desks, tables, counters, floors, stands) = plain black ink lines only. NEVER colored.
- One small solid-{{ACCENT}} equilateral triangle floats freely on white.
- Produce ONE single scene (do NOT tile or grid).

ABSOLUTELY DO NOT add: gray edge vignette, gray corners, drop shadows, paper grain, sepia tint, beige background, off-white background, or any non-white background tone.

SUBJECT — {{SUBJECT}}
```

The `{{SUBJECT}}` block should spell out cast, action, props (with each accent-color shape called out as free-floating with explicit "no outline"), ink-on-color details for each prop, ambient marks, triangle position, and per-character traits.

## Anti-patterns to avoid

The following are common failure modes the underlying image model produces under busy prompts. Restate the corresponding rule whenever you spot the risk:

- **Gray edge vignette / dark corners.** The model defaults to a soft vignette unless told otherwise. Always include the explicit negative list.
- **Black outline around the accent-color shape.** This is the most subtle and the most damaging failure — it makes the style look like flat-vector clip art instead of hand-drawn brush. Whenever you describe a prop, append "(rough free-floating shape, no black outline)".
- **Solid-black hair.** The model often fills hair as a black blob. Always specify "scribbled separate strokes with white visible between curls".
- **Coloring furniture.** If you let the model decide, it will paint desks and counters in the accent color. Always specify "desk / counter / table is plain black ink lines, NOT the accent color".
- **Multi-cell grid output.** The phrase "match the reference grid" makes the model tile multiple small scenes. Use "match the reference style" instead.
- **Adding a second color.** Even when the prompt says "one accent color only", a second hue can creep in (a yellow detail on a blue scene). Restate "exactly one accent color, no second hue, no gradient".

## Portability note

This style was developed against the `fal-ai/nano-banana/edit` image-to-image model and is now generated on `fal-ai/nano-banana-2/edit` (Gemini 3.1 Flash Image — supports up to 14 reference images and natural-language edit instructions). The reference images in this directory should be passed as style anchors. If a different image generation product, gateway, or runtime is used, the style guidance is portable as long as that runtime supports a reference-image (or i2i) style transfer mode and accepts a long, rule-heavy system prompt. With a text-to-image-only model, expect weaker style fidelity — the free-floating-color rule is especially hard for the model to honor without a visual anchor.
