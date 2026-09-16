---
name: op-ed-cover
description: Editorial magazine op-ed cover illustration — flat-vector + paper-grain scene with elongated ink-line characters, a muted retro palette, and a serif headline overlay block in the lower-right corner. Trigger when the user says /op-ed-cover, asks for an "editorial magazine illustration", an "op-ed cover", a "magazine essay illustration", or a scene with a headline overlay in this style.
---

# /op-ed-cover — locked editorial magazine cover style

This skill produces a single editorial illustration laid out like a page from a print magazine essay: a flat-vector scene with paper-grain texture, expressive elongated ink-line characters, a muted retro palette, and a **serif headline block in the lower-right corner** that frames the scene as a witty opinion piece.

The whole point is the **editorial tension** between the picture and the headline — the picture sets a moment, the headline gives it a contrarian or knowing voice. Headlines should sound like they came from the back pages of a New Yorker / Monocle / Time-Out essay column.

## Prompt interpretation

The user will give a short brief, usually some combination of:
- a **scene metaphor** (e.g. "Tokyo ramen master", "London tube commute", "Italian barista")
- a **palette direction** (e.g. "mustard + forest green", "dusty rose + ink navy")
- a **complexity level** (L1 single hero / L2 small ensemble / L3 busy crowd)
- optionally, a **headline** or a **headline voice** ("declarative", "punning", "appreciative")

For each invocation:

1. **Brainstorm the scene vividly.** Picture the time of day, the weather, the specific gesture the main character is mid-doing, the props that signal place. Avoid generic "person in venue" — go for a moment that has tension or charm.
2. **Pick a sharp, original headline.** Use one of the headline voices below. Do **not** default to "In Defense of the [Adjective] [Archetype]" — that formula is the most identifiable cliché of the style. Mix declaratives, puns, sensory metaphors, and quiet appreciations.
3. **Compose the page** with the scene filling the canvas and a solid or translucent color block in the lower-right corner carrying the serif headline + two short lines of small italic body copy (faux lorem ipsum is fine).
4. **Lock the style.** Every invocation keeps the flat-vector + grain treatment, the elongated ink-line figures, the retro editorial mood, and the headline-block placement.

## Locked style axes (NEVER vary)

### Rendering
- **Flat-vector with subtle paper-grain texture overlay** — like a Riso print or a high-quality magazine page reproduction.
- **Gentle painterly shading** — soft modeling on faces, fabric folds, ceramic, steam. Never airbrushed gradients, never 3D rendering.
- **Subtle film grain throughout** the canvas, not just on the figures.
- No drop shadows, no glow effects, no digital cleanness.

### Character drawing
- **Elongated expressive forms.** Slightly stretched proportions — long necks, long limbs, slightly tilted heads. Characters lean.
- **Confident ink-line outlines** with subtle weight variation; lines feel hand-drawn, not vector-uniform.
- **Period-appropriate clothing** — 1950s–60s editorial-illustration silhouettes (slim suits, structured coats, aprons, hats).
- **Expressions are restrained.** Characters wear knowing, calm, slightly skeptical looks. Almost never wide-eyed or shouting.

### Composition
- **Portrait orientation** (roughly 7:9 / 4:5), magazine-page aspect ratio.
- Scene fills the canvas edge-to-edge — no white or paper border framing.
- **Headline overlay block sits in the lower-right corner**, occupying roughly the bottom-right quarter of the canvas.
- The headline block is a **solid or translucent rectangle** in an accent color from the scene's palette.
- Inside the block: large serif headline (2 lines), then two short lines of small italic body copy beneath.

### Mood
- **1950s–60s editorial illustration** — think *Saul Steinberg*, *Charley Harper*, mid-century *Esquire* / *Punch* / *Vogue* spot illustrations, with a contemporary editorial revival sensibility.
- Wry, observational, gently contrarian. The picture is never angry, never sentimental.

## Variable axes (the 5 dials)

### 1. Palette
Pick three roles: **background hue** (dominates the canvas), **accent** (used in the headline block and 1–2 props), **figure ink** (outlines and key fills). Avoid more than three colors.

Battle-tested palettes:
- Dusty slate-blue · cream · brick-red (original)
- Mustard ochre · cream · forest green
- Dusty rose · warm cream · ink navy
- Sage olive · cream · burnt orange
- Mocha brown · cream · oxblood
- Pale teal · cream · charcoal

When you write the palette into the prompt, be explicit about **what each color is for** and **what colors are off-limits** — image-to-image models otherwise drift back to the most-seen palette (dusty blue + brick red).

### 2. Complexity
- **L1 — Single hero.** Tight close-up, one character mid-action, 1–3 supporting props. The figure carries the whole frame.
- **L2 — Small ensemble.** 2–4 characters in a clear shared setting (a train carriage, a counter, a stoop). Spatial relationship between them is part of the story.
- **L3 — Busy crowd.** 6+ characters, layered vignettes, dense background detail. Reads like a Where's-Waldo of editorial archetypes — but each character still has a specific, observed beat.

L3 is the hardest to keep editorially soft — character softness erodes as count rises. Pull back on character count if the result starts looking like a cluttered children's-book scene.

### 3. Scene
The scene IS the metaphor. Pick a **specific cultural microcosm** — a small ritual or social space where a recognizable archetype lives. Examples:
- A Tokyo ramen-ya at closing time
- A London tube carriage at 8am
- A New York Jewish deli at lunch rush
- An Italian café where the barista refuses to be rushed
- A Parisian bakery at dawn
- A Hong Kong dai pai dong after midnight
- A Buenos Aires tango bar mid-set

Avoid "person standing in generic place." The scene must have **temporal specificity** (rush hour, last call, opening) and **textural detail** (handrails, salamis on hooks, lacquered chopsticks, brass espresso lever).

### 4. Headline voice
Pick one — do **not** default to "In Defense of…".

- **Noun-led declarative** — `The Slowest Bowl in Tokyo`, `Pastrami at Full Volume`, `Last Call at the Counter`
- **Pun / local idiom** — `Mind the Eye Contact` (riff on "Mind the Gap"), `Tokyo, by Ladle`, `Brisket and Brevity`
- **Quiet appreciation** — `An Hour at the Ramen-ya`, `On Patience, By the Bowl`, `Notes from the Counter`
- **Contrarian** (the original formula — use sparingly) — `In Defense of the [Adjective] [Archetype]`, `A Quiet Defense of [Behavior]`

Keep headlines to **5–8 words**, two visual lines. Use a small italic faux-body line (1–2 short sentences of lorem ipsum is fine) under the title.

### 5. Headline block style
- **Solid opaque rectangle** — strongest contrast, reads as a poster block. Use when the scene is busy (L3) or low-contrast.
- **Translucent rectangle** — softer, lets the scene bleed through. Use for L1/L2 when the figure work should breathe.
- The rectangle's fill color must be the palette's **accent**, not the background.
- Type is always serif, weight bold-to-medium, color is the palette's lightest tone (cream / ivory).

## How to brief an image-to-image model

This style is most reliably reproduced via an **image-to-image model that accepts multiple reference images** — both reference images in this folder plus a strong textual override of palette, scene, and headline.

Key briefing principles:
- Lead with `"in the EXACT style of the reference images"` and explicitly call out **flat-vector + paper grain, expressive elongated ink-line characters, 1950s–60s editorial mood, portrait magazine composition**.
- Write the palette with **role tags** (`background dominates the canvas`, `accent for the headline block`, `ink for figure outlines`) and explicit **negatives** (`NO blue, NO red`).
- Specify **complexity level** in plain language (`Level 1 — single hero close-up`).
- Describe the scene with concrete props and gestures — the model will fill in generic decor otherwise.
- For the headline: give the **exact text in quotes**, specify **lower-right corner**, name the **block fill color**, and require **serif type**.
- Add `no logos, no other text outside the headline block` to suppress stray watermarks and signage.

Model notes (semantic, not endpoint-specific):
- Multi-reference image-to-image models in the nano-banana / SDXL-IP-Adapter family handle this style well.
- For palette discipline, use **explicit negative color callouts** in the prompt — these models otherwise regress to the most-seen palette of the reference set.
- For headline legibility, prefer a **solid opaque block** over a translucent one when text rendering is weak; the model can lose translucent serif text.

## Reference outputs

Three reference outputs are committed alongside this skill to anchor the style. Each demonstrates a different point on the palette × complexity × scene matrix:

- `ref-slowest-bowl.png` — **L1 single hero**, mustard ochre + forest green, Tokyo ramen master, declarative headline (*"The Slowest Bowl in Tokyo"*).
- `ref-mind-eye-contact.png` — **L2 ensemble**, dusty rose + ink navy, London tube carriage, pun headline (*"Mind the Eye Contact"*).
- `ref-pastrami-full-volume.png` — **L3 crowd**, sage olive + burnt orange, NYC Jewish deli, sensory headline (*"Pastrami at Full Volume"*).

When briefing a new piece, treat these three as the style anchor and override only the variable axes.

## Anti-patterns

- ❌ Defaulting every headline to "In Defense of [Adjective] [Archetype]". One per series, max.
- ❌ Generic "person standing in venue" — always anchor to a **specific cultural microcosm** with temporal and textural detail.
- ❌ Bright pure white background. The background should be a saturated muted hue from the palette.
- ❌ Photographic shading, lens-blur depth-of-field, or 3D lighting. Keep shading flat and painterly.
- ❌ Centered headline blocks. The block always sits in the lower-right.
- ❌ Modern sans-serif headlines. Always serif.
- ❌ Logos, brand marks, URLs, or stray decorative text outside the headline block.
- ❌ Cluttering L3 scenes past ~10 characters — the editorial softness collapses.
