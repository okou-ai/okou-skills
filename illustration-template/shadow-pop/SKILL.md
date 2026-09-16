---
name: shadow-pop
description: Bright flat-vector editorial illustration style — every colored shape sits in front of an offset black silhouette of itself (the signature depth trick, no outlines on the fills), with white hand-drawn dashed stitching, scattered palette-colored sparkle confetti, and a fully transparent PNG background so the piece drops cleanly onto any surface. Five dials per brief — palette (default / berry-pop / tropical / citrus-cobalt), scene metaphor, complexity (L1 / L2 / L3), confetti density, and subject domain. Trigger when user says /shadow-pop, asks for a "shadow-pop illustration", a "bright flat-vector illustration with offset shadow", an "in-app illustration with offset shadow trick", or briefs in the style of the included reference images.
---

# /shadow-pop — locked bright flat-vector editorial style

This skill produces bright flat-vector editorial illustrations in the shadow-pop house style: each colored shape carries an offset black silhouette behind it (the signature depth trick that replaces outlines), with white hand-drawn dashed stitching, palette-colored sparkle confetti scattered around, and a fully transparent PNG background so the piece drops cleanly into any surface — blog covers, marketing cards, in-app spot illustrations, empty states, dashboard tiles.

Each invocation swaps only a handful of dials — every other style axis stays locked.

## Prompt interpretation

The user will usually give a short brief — sometimes just a subject ("piggy bank"), sometimes subject + palette ("coffee cup, citrus-cobalt"), sometimes a use case ("empty state for no messages"). Your job is to turn that into a full illustration brief without stopping to ask:

1. **Pick a hero subject** that embodies the metaphor — never paste a generic label on a non-thematic object. Theme-native props win (mailbox + envelope for messaging, vinyl + sleeve for music, parcel + ink stamp for shipping, watering can + plant for growth).
2. **Choose a palette** from the four locked presets. If the user gave a vibe, pick the palette whose mood fits (warm/upbeat → default or berry-pop; fresh/optimistic → tropical; energetic/marketing → citrus-cobalt).
3. **Choose a complexity level** (L1 / L2 / L3) — match it to the use case. In-app spot illustrations and empty states tend toward L1; blog covers and marketing cards toward L2; campaign visuals toward L3.
4. **Choose confetti density** — minimal for quiet/empty-state energy, medium for editorial default, lively for celebration/marketing.
5. **Hold the locked frame** — transparent background, per-shape offset black shadow, no outlines on fills, dashed white stitching, sparkle confetti, bright saturated palette only.

Bias toward warm, friendly, slightly hand-drawn subjects. Avoid muted / pastel / dusty / earth-toned palettes — they are off-spec for this style. Avoid letterforms inside the canvas; no slogans or labels.

## Locked style axes (NEVER vary)

### Composition

- **Single hero subject or compact mini-scene**, centered on a square or near-square canvas (default 1024×1024; portrait 1024×1536 or landscape 1536×1024 only when the layout demands it).
- **Generous breathing room** around the subject — never bleed off the edges.
- **No backgrounds, no scenery, no horizon, no ground line** — the subject sits on a fully transparent canvas.

### Depth treatment — the signature

- Every colored shape sits in front of an **offset black silhouette of itself**, shifted **down-right ~6–10 px**.
- The offset shadow **replaces outlines entirely**. Never trace a black perimeter around a fill — the offset shadow does ALL the depth work.
- Shadows are flat, hard-edged, solid black — never soft, never grayscale, never gradient.

### Line + surface

- **Flat saturated color fills** with no gradient, no airbrush, no internal texture.
- **Slight hand-drawn wobble on edges** — curves aren't perfectly geometric, mimicking a vector illustration traced from a hand sketch.
- **White hand-drawn dashed stitching** on at least one prop seam.
- **A small dashed-rectangle "label panel"** detail on at least one prop (mimics a sewn-on tag — appears in nearly every piece).
- **Brushy white flicks** for shine or highlight, sparingly.

### Background

- **Fully transparent PNG (alpha channel).** No fill color. No polka dots. No ground.
- The piece must drop cleanly onto a white modal, a colored card, a marketing hero, or a dark dashboard surface without recomposing.

### Sparkle confetti

- **Tiny 4-point stars + small filled circles + small open dots** scattered around the subject.
- Confetti colors come from the chosen palette only — never gray, never desaturated.
- Confetti density follows the dial (minimal / medium / lively).

## Variable axes (the five dials)

These are the only things that should change between pieces.

| # | Axis | What it controls | Values |
|---|---|---|---|
| 1 | **Palette** | The hue family | `default` (coral / butter / royal blue / teal) · `berry-pop` (hot pink / tangerine / cobalt / lime) · `tropical` (turquoise / lime / tangerine / hot pink) · `citrus-cobalt` (tangerine / golden butter / lime / cobalt) |
| 2 | **Scene metaphor** | What the centerpiece IS | shipping (parcel + ink stamp) · music (vinyl + sleeve) · finance (piggy bank + coins) · messaging (mailbox + envelope) · growth (watering can + plant) · lifestyle (coffee + croissant + newspaper) · e-commerce (shopping bag + gift) · productivity (laptop + paper airplane) · travel (suitcase + passport) — any theme-native pairing |
| 3 | **Complexity** | How many elements compose the piece | **L1** single hero subject · **L2** object + interacting prop · **L3** small scene with 3+ elements arranged on a base |
| 4 | **Confetti density** | How many sparkle marks float around | `minimal` (3–4 marks — empty-state energy) · `medium` (6–10 marks — editorial default) · `lively` (12+ marks — marketing / celebration) |
| 5 | **Subject domain** | Optional thematic tilt | finance · e-commerce · productivity · lifestyle · music · communication · plant care · travel · etc. Not locked to commerce; coins / price tags / barcodes are optional flavor only. |

### Palette hex values

- `default` — coral red `#FF4D5A` · butter yellow `#FFD24D` · royal blue `#2E5BFF` · teal green `#1FB58F`
- `berry-pop` — hot pink `#FF3D8A` · tangerine `#FF8533` · cobalt `#2E5BFF` · lime `#9BE54A`
- `tropical` — turquoise `#1ED4C7` · lime `#A8E55A` · tangerine `#FF8533` · hot pink `#FF4D8A`
- `citrus-cobalt` — tangerine `#FF8533` · golden butter `#FFC83D` · lime `#9BE54A` · cobalt `#2E5BFF`

Black + white are universal across all palettes (offset shadow + dashed stitching).

## Brief template

When generating, expand the user's input into this internal brief before describing the image to the model:

```
Hero subject / scene: <one specific named subject or compact scene>
Complexity: <L1 / L2 / L3 — with one-line description of how many elements and how they're arranged>
Palette: <one of the four named presets, with hex list>
Confetti density: <minimal / medium / lively>
Subject domain: <optional thematic tilt>
```

## Full prompt template

Substitute the bracketed values and feed this to the image model:

```
Flat-vector editorial illustration on a TRANSPARENT background (PNG alpha — no fill, no polka dots, no ground color whatsoever).
Scene metaphor: {SCENE_DESCRIPTION} — {COMPLEXITY_DESCRIPTION}.
Palette: {PALETTE_NAME} — {PALETTE_HEX_LIST}.
Every colored shape sits in front of an offset black silhouette of itself (offset down-right ~8px), creating the signature shadow-pop depth effect.
NO black outlines on the colored fills — the offset shadow does ALL the depth work, never trace a black perimeter.
White hand-drawn dashed stitching on at least one prop seam and a small dashed-rectangle label panel detail.
Bright sparkle confetti of tiny 4-point stars and small dots in palette colors scattered around the subject — {CONFETTI_DENSITY} density.
Colors must be BRIGHT, CLEAN, SATURATED — never muted, never pastel, never dusty.
Slight hand-drawn wobble on edges. Square 1:1 canvas. No text. Background MUST be fully transparent.
```

## Output requirements

- **Format:** PNG with alpha channel — the background must be transparent, not white, not cream, not gray.
- **Canvas:** 1024×1024 by default; 1024×1536 (portrait) or 1536×1024 (landscape) only when the layout requires.
- **Color depth:** RGBA, 8-bit per channel.
- **Compression:** lossless PNG; no JPEG for this style (alpha needed).

If the chosen execution environment does not support transparent PNG output natively, document the constraint in the output and have the operator post-process the result to remove the background — do not silently substitute a white or colored ground.

## Worked examples

Five reference pieces below — each holds the locked frame and varies the five dials. The image files live alongside this SKILL.md.

### Example 1 — default · L2 · lively (canonical anchor)

Brief: *"A cardboard parcel being postmarked, default palette."*

Filled prompt:
```
Flat-vector editorial illustration on a TRANSPARENT background (PNG alpha — no fill, no polka dots, no ground color whatsoever).
Scene metaphor: a cardboard parcel tied with twine being postmarked by a wooden ink stamp hovering above, with a couple of red postmark imprints already on the box — L2 (object + interacting prop).
Palette: default — coral red #FF4D5A · butter yellow #FFD24D · royal blue #2E5BFF · teal green #1FB58F.
Every colored shape sits in front of an offset black silhouette of itself (offset down-right ~8px), creating the signature shadow-pop depth effect.
NO black outlines on the colored fills — the offset shadow does ALL the depth work, never trace a black perimeter.
White hand-drawn dashed stitching on at least one prop seam and a small dashed-rectangle label panel detail.
Bright sparkle confetti of tiny 4-point stars and small dots in palette colors scattered around the subject — lively density.
Colors must be BRIGHT, CLEAN, SATURATED — never muted, never pastel, never dusty.
Slight hand-drawn wobble on edges. Square 1:1 canvas. No text. Background MUST be fully transparent.
```

Reference: `ref-default-mail-l2.png`

### Example 2 — citrus-cobalt · L3 · medium

Brief: *"A morning brew scene — coffee cup, croissant, newspaper — on a tray, citrus-cobalt palette."*

Filled prompt:
```
Flat-vector editorial illustration on a TRANSPARENT background (PNG alpha — no fill, no polka dots, no ground color whatsoever).
Scene metaphor: a takeaway coffee cup with a steam swirl, a buttery croissant, and a rolled-up newspaper all sitting on a flat butter-yellow serving tray — L3 (small scene with 3+ elements arranged on a base).
Palette: citrus-cobalt — tangerine #FF8533 · golden butter #FFC83D · lime #9BE54A · cobalt #2E5BFF.
Every colored shape sits in front of an offset black silhouette of itself (offset down-right ~8px), creating the signature shadow-pop depth effect.
NO black outlines on the colored fills — the offset shadow does ALL the depth work, never trace a black perimeter.
White hand-drawn dashed stitching on at least one prop seam and a small dashed-rectangle label panel detail.
Bright sparkle confetti of tiny 4-point stars and small dots in palette colors scattered around the subject — medium density.
Colors must be BRIGHT, CLEAN, SATURATED — never muted, never pastel, never dusty.
Slight hand-drawn wobble on edges. Square 1:1 canvas. No text. Background MUST be fully transparent.
```

Reference: `ref-citrus-coffee-l3.png`

### Example 3 — tropical · L2 · lively

Brief: *"A watering can pouring water onto a leafy potted plant, tropical palette."*

Filled prompt:
```
Flat-vector editorial illustration on a TRANSPARENT background (PNG alpha — no fill, no polka dots, no ground color whatsoever).
Scene metaphor: a turquoise watering can tipped over a leafy potted plant, water droplets in mid-air, sparkles on the leaves — L2 (object + interacting prop).
Palette: tropical — turquoise #1ED4C7 · lime #A8E55A · tangerine #FF8533 · hot pink #FF4D8A.
Every colored shape sits in front of an offset black silhouette of itself (offset down-right ~8px), creating the signature shadow-pop depth effect.
NO black outlines on the colored fills — the offset shadow does ALL the depth work, never trace a black perimeter.
White hand-drawn dashed stitching on at least one prop seam and a small dashed-rectangle label panel detail.
Bright sparkle confetti of tiny 4-point stars and small dots in palette colors scattered around the subject — lively density.
Colors must be BRIGHT, CLEAN, SATURATED — never muted, never pastel, never dusty.
Slight hand-drawn wobble on edges. Square 1:1 canvas. No text. Background MUST be fully transparent.
```

Reference: `ref-tropical-plant-l2.png`

### Example 4 — berry-pop · L1 · medium

Brief: *"A vinyl record sliding out of a hot-pink sleeve with a music note, berry-pop palette."*

Filled prompt:
```
Flat-vector editorial illustration on a TRANSPARENT background (PNG alpha — no fill, no polka dots, no ground color whatsoever).
Scene metaphor: a single vinyl record (black disc with a center label) sliding halfway out of a square album sleeve, with one playful music note floating to the side — L1 (single hero subject).
Palette: berry-pop — hot pink #FF3D8A · tangerine #FF8533 · cobalt #2E5BFF · lime #9BE54A.
Every colored shape sits in front of an offset black silhouette of itself (offset down-right ~8px), creating the signature shadow-pop depth effect.
NO black outlines on the colored fills — the offset shadow does ALL the depth work, never trace a black perimeter.
White hand-drawn dashed stitching on at least one prop seam and a small dashed-rectangle label panel detail.
Bright sparkle confetti of tiny 4-point stars and small dots in palette colors scattered around the subject — medium density.
Colors must be BRIGHT, CLEAN, SATURATED — never muted, never pastel, never dusty.
Slight hand-drawn wobble on edges. Square 1:1 canvas. No text. Background MUST be fully transparent.
```

Reference: `ref-berry-record-l1.png`

### Example 5 — citrus-cobalt · L3 · medium (proof of transparent PNG)

Brief: *"A travel scene — open suitcase with folded shirt, sunglasses, passport, and luggage tag — citrus-cobalt palette."*

Filled prompt:
```
Flat-vector editorial illustration on a TRANSPARENT background (PNG alpha — no fill, no polka dots, no ground color whatsoever).
Scene metaphor: an open suitcase laid flat with a folded blue shirt, a pair of sunglasses, a passport, and a small lime-green luggage tag on a strap — L3 (small scene with 3+ elements).
Palette: citrus-cobalt — tangerine #FF8533 · golden butter #FFC83D · lime #9BE54A · cobalt #2E5BFF.
Every colored shape sits in front of an offset black silhouette of itself (offset down-right ~8px), creating the signature shadow-pop depth effect.
NO black outlines on the colored fills — the offset shadow does ALL the depth work, never trace a black perimeter.
White hand-drawn dashed stitching on at least one prop seam and a small dashed-rectangle label panel detail.
Bright sparkle confetti of tiny 4-point stars and small dots in palette colors scattered around the subject — medium density.
Colors must be BRIGHT, CLEAN, SATURATED — never muted, never pastel, never dusty.
Slight hand-drawn wobble on edges. Square 1:1 canvas. No text. Background MUST be fully transparent.
```

Reference: `ref-citrus-suitcase-l3-transparent.png` — RGBA-transparent PNG; the verified anchor for the transparent-background contract.

## Common drifts to fight in prompts

These are the failure modes that consistently appear with this style. Reinforce them in every prompt:

1. **Black perimeter outlines on fills** — the most common drift. The model wants to outline each shape. Always include "NO black outlines on the colored fills" and "the offset shadow does ALL the depth work." If the output still has outlines, regenerate with the constraint stated twice.
2. **Background fill leakage** — even with transparent set, the model may paint a polka-dot grid, cream wash, or pale gray onto the canvas. Always include "TRANSPARENT background (PNG alpha — no fill, no polka dots, no ground color)" in the prompt text, and request alpha output from the model. Visually inspect output for unintended background fill.
3. **Muted / pastel drift** — words like "soft," "subtle," "calm," or "gentle" pull saturation down. Always end the prompt with "Colors must be BRIGHT, CLEAN, SATURATED — never muted, never pastel, never dusty."
4. **Over-literal floating text** — the model sometimes paints out the metaphor in floating words. Always include "No text."
5. **Cartoon faces on objects** — when asked for an "empty" or "sad" state, the model may add an emotive face to the hero. If you don't want one, state explicitly: "no eyes, no face on the object."

## Portability notes

- The locked frame depends only on prompt-level controls and a transparent-PNG output. It does not require a specific provider, model family, or CLI.
- The most reliable results to date come from frontier image models that accept structured prompts and support transparent PNG output natively. If a chosen model does not support transparent backgrounds, generate on a pure white ground and have the operator key out the white before delivery.
- The reference assets in this directory are PNG with alpha. If a downstream renderer rejects PNG alpha (e.g. flattens to JPEG or requires opaque), document the limitation rather than substituting a fill color.
