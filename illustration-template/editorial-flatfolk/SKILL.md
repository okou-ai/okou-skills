---
name: editorial-flatfolk
description: Editorial hand-drawn naive book-illustration style — flat saturated color blocks, loose hand-drawn ink line overlay on top of the color, subtle paper grain, simple ink sun-ray hatching, and a strong sense of place built from tall narrow architecture and one-point perspective. Five creative dials (palette, scene metaphor, perspective, cast, light/weather) over a locked style core. Trigger when the user says /editorial-flatfolk, asks for an "editorial flat-folk illustration", a "saturated naive book-illustration scene", a "tall narrow row-house illustration", or briefs a palette + scene metaphor + season.
---

# /editorial-flatfolk — locked editorial flat-folk illustration

This skill produces one square editorial illustration in a locked hand-drawn naive book-illustration style. The line work, color medium, surface texture, and overall feel are constants. The caller only dials five creative knobs (palette, scene metaphor, perspective, cast, light / weather).

The aesthetic sits in the contemporary editorial / picture-book / pop-folk space — flat saturated color blocks with loose hand-drawn ink line work sitting ON TOP of the color, subtle paper grain across the canvas, and a charming slightly imperfect hand. Adjacent to Pol Mara, Klaus Haapaniemi, and Carson Ellis editorial work. Not anime, not vector, not photoreal, not soft watercolor wash, not flat-vector poster.

## Required model

This style is locked to **`gpt-image-1.5`** (OpenAI image generation through whichever provider the executing tool routes to). The combination of flat saturated color, loose hand-drawn ink overlay, paper grain, and naive architectural depth requires this specific model; it does not survive on harder-line vector models or softer painterly models.

Required generation parameters:

- **Model:** `gpt-image-1.5`
- **Size:** `1024x1024` (square)
- **Quality:** `high` — the paper grain and ink hatching need resolution to read
- **Mode:** **image-to-image** with `ref-harbor.png` (the locked style anchor that lives next to this SKILL.md) passed as the style reference
- **Style:** caller must opt out of stacked style injection (the executing tool should pass `--skip-style` or its equivalent — the SKILL itself is the style)

These are semantic parameters. The executing tool decides the invocation mechanics (CLI command, REST call, gateway, local runtime).

## Reference anchors

Three reference images live alongside this SKILL.md:

- `ref-harbor.png` — **the canonical style anchor** (coastal-peach palette, harbor metaphor, golden-hour light, solo wanderer cast, one-point dock perspective). This is the locked anchor every generation must use for image-to-image style hold.
- `ref-alpine.png` — clean output from the validation batch: winter-cool palette, alpine-village metaphor, snow-midday light, solo child cast, one-point sloped lane perspective.
- `ref-park.png` — clean output from the validation batch: autumn-rust palette, park metaphor, midday light, seated character cast, low-angle hero perspective.

`ref-harbor.png` is the **required** style reference. The other two are exemplars showing how the dials move within the locked style.

## Locked style axes (NEVER vary)

### Color medium
- Flat, saturated color blocks. Each shape is one solid color.
- No airbrush gradients, no soft pastel haze, no internal form modeling, no 3D rendering inside shapes.
- A faint vertical sky gradient is acceptable (warm-to-cool low horizon); everywhere else stays flat.

### Line work
- Loose hand-drawn black ink lines that sit ON TOP of the color blocks — not as outlines that perfectly trace the shape's perimeter.
- Lines wobble slightly, occasionally cross or fall short of a color edge, never look ruler-straight.
- Line weight is fairly uniform; this is not a brush-pen calligraphic style.

### Surface texture
- Subtle paper grain across the entire canvas. Visible but quiet.
- The grain is the ONLY texture allowed; nothing inside any shape should be brushy, impressionistic, or gouache-thick.

### Sky treatment
- Simple ink sun-ray hatching radiating from the sun, OR ink rain ticks for wet scenes, OR ink-tick snowflakes for cold scenes.
- Cloud forms are drawn as simple soft humps with a single optional outline.

### Composition
- A clear depth axis. Default is one-point perspective with two flanking walls of color receding to a vanishing point.
- Tall narrow architecture lines the receding walls when the scene metaphor allows (row houses, harbor-front shops, alpine chalets, market stalls).
- The scene metaphor IS the composition; do not retrofit a generic urban template with relabeled props (see Pitfalls).

### Mood
- Editorial, picture-book, naive, observational. Calm and warm by default; pivots cleanly into rainy, snowy, or twilight tones via the Light dial without changing the underlying flatness.

## Dialable knobs (vary per illustration)

### 1. Palette
Pick one. Always name 4–6 specific anchor colors in the prompt.

- **warm-primary** (default) — mustard yellow / tomato red / cobalt blue / leaf green / terracotta / cream sky.
- **coastal-peach** — soft peach / coral / cobalt / mustard / terracotta / rose-gold sky.
- **jewel-night** — deep indigo / magenta / jade green / lantern yellow / plum / charcoal.
- **winter-cool** — cream snow / pale icy blue / evergreen / plum / terracotta-red roofs / mustard window frames.
- **autumn-rust** — burnt orange / ochre / plum / sage green / deep brick red / cream sky.
- **monsoon-twilight** — slate blue / teal / dusty rose / mustard / cream / charcoal.

### 2. Scene metaphor
The scene IS the metaphor — pick a place that itself embodies the idea. Examples that respect the style:

- **street** — tall narrow row houses lining a cobblestone lane.
- **harbor** — wooden dock between two rows of fishing boats with colored hulls, harbor-front shops behind (the canonical anchor).
- **market** — covered stalls lining a market street, awnings, hanging lanterns.
- **transit** — a small train platform, a tram stop, a ferry terminal.
- **park** — a clearing with a bench, fountain, or stone bridge; tall trees as the flanking depth elements.
- **square** — a town plaza with a clock tower or fountain centered, shopfronts framing the edges.
- **interior** — a small café, library reading room, or shop interior with tall narrow windows.
- **alpine-village** — chalet houses with steep snow-capped roofs along a sloped lane, evergreens flanking.

If the scene metaphor is a pure-nature scene with no buildings, FORCE one architectural anchor element (a bench, a stone bridge, a wooden bandstand, a fountain). Otherwise the style softens — see Pitfalls.

### 3. Perspective
- **one-point street** (default) — straight depth axis with two flanking walls of architecture receding to a vanishing point.
- **frontal facade** — flat parallel composition, one wall of buildings filling the frame.
- **low-angle hero** — looking slightly up at a central figure or structure framed by trees / buildings.
- **isometric** — for top-down map-like scenes; the style still holds but loses the receding-rhythm feel.
- **top-down** — bird's eye map view; use sparingly, only for explicit "map" scenes.

Default to **one-point street** unless the brief explicitly requests another. Composition without a clear depth axis reads flat — see Pitfalls.

### 4. Cast
- **solo wanderer** (default) — a single figure walking, cycling, or standing in the scene, typically rear- or three-quarter-view.
- **paired** — two figures, often sharing an umbrella, walking together, or facing each other.
- **small crowd** — 4–8 background figures plus one foreground anchor figure.
- **none** — no figures, only architecture and atmospheric elements.

Figures are drawn small-to-medium relative to the frame; they anchor the scale of the architecture, they are not portraits.

### 5. Light / weather
- **midday sun** (default) — warm cream sky with simple ink sun-ray hatching.
- **golden hour** — warm peach / rose sky, low sun, longer ink sun rays.
- **rain** — wet cobblestone reflections, ink rain ticks, NO atmospheric haze — see Pitfalls.
- **snow** — pale icy sky, ink-tick snowflakes, snow caps on architecture.
- **blue hour** — deep blue sky with one or two ink-line clouds, lit windows glowing.

## Pitfalls (lock these in the prompt)

These are validated failure modes from the calibration batch:

1. **Dark + wet drift.** At the dark-and-rainy extreme, the model drifts toward impressionist atmospheric texture (Van Gogh nightscape territory). The prompt must explicitly include `flat color blocks, no atmospheric texture, no impressionist brushwork, no soft shading` whenever Light is `rain` or `blue hour`.
2. **Nature scenes soften.** Pure forest / pure park / pure field scenes lose the style. If the scene metaphor has no architecture, FORCE one architectural anchor element into the prompt (bench, fountain, stone bridge, bandstand).
3. **Flat composition.** Without a clear depth axis the result reads vector-flat. Default to one-point perspective; if the brief asks for low-angle or frontal, explicitly call out a strong vertical-line rhythm to keep the depth feel.

## Prompt template

Given a brief, assemble this prompt and pass it to the model together with `ref-harbor.png` as the image-to-image style reference:

```
Editorial flat-vector illustration in EXACTLY the same hand-drawn naive book-illustration style as the reference image: flat saturated color blocks, loose imperfect hand-drawn ink line overlay, subtle paper grain texture, organic edges, no rendering, no soft shading, no atmospheric texture, no impressionist brushwork.

SCENE: {SCENE_DESCRIPTION_WITH_ARCHITECTURAL_ANCHOR}.

PALETTE: {4–6 anchor colors from the chosen palette dial}.

PERSPECTIVE: {one-point street / frontal facade / low-angle hero / etc.} — emphasize a clear depth axis.

CAST: {solo wanderer / paired / small crowd / none}; figures small-to-medium, no portrait close-ups.

LIGHT: {midday sun / golden hour / rain / snow / blue hour} — render sky with simple ink hatching (sun rays / rain ticks / snowflakes).

No text, no logo, no watermark.
```

## How to evaluate the output

A clean render satisfies all of:

- Color reads as flat solid blocks, not airbrushed or painted.
- Black ink lines sit on top of the color and occasionally cross or fall short of a color edge.
- Paper grain is visible across the whole canvas; nothing inside any shape is brushy.
- The scene has a clear depth axis.
- Architecture (or the forced architectural anchor) is present and reads as the scale of the place.
- Sky uses simple ink hatching (sun rays / rain / snow) — no soft cloud rendering.

If the result drifts toward soft watercolor, oil-paint impasto, anime, or clean vector, the style failed and the prompt should be re-run with the Pitfall-lock language reinforced.
