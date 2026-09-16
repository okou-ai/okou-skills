---
name: postcard-illustration
description: Hand-drawn editorial postcard illustration style. Fine black marker/pen ink linework over flat saturated gouache color fills with sharp edges, dense small repeated ink patterns on surfaces (rows of windows, shingle curves, hatching, stippling), subtle paper-grain background texture, tiny scattered white speckles (snow / petals / sparkle), and a tall portrait composition with a layered foreground-midground-background. Travel-journal / urban-sketcher aesthetic. Trigger when the user says /postcard-illustration, asks for a "postcard illustration", "travel illustration", "urban sketcher style", or briefs a palette + scene archetype + complexity.
---

# /postcard-illustration — locked postcard / travel-journal illustration

This skill produces one tall portrait illustration in a locked hand-drawn editorial postcard style. The line work, color medium, surface texture, and overall composition are constants. The caller only dials seven creative knobs (palette, scene archetype, subject, complexity, atmosphere, sky treatment, surface-pattern density, cast).

The aesthetic sits in the urban-sketcher / travel-postcard / picture-book editorial space. Think dense layered architectural and botanical scenes, confident ink line work, flat saturated gouache color, and a charming slightly imperfect hand. Not anime, not manga, not 3D, not vector, not photoreal, not soft watercolor wash.

## Required model

This style is locked to **`gpt-image-2`** (OpenAI GPT image generation, served through whichever provider the executing tool routes to). The dense small ink patterns, flat-but-textured color medium, and consistent line weight do NOT survive on weaker or differently-tuned image models — they collapse into either soft-watercolor wash or clean vector. Do not substitute with another model unless you have validated that the two locked reference anchors regenerate faithfully.

Required generation parameters:

- **Model:** `gpt-image-2`
- **Size:** `1024x1536` (tall portrait)
- **Quality:** `high` — the dense ink patterns and small speckles need resolution to read
- **Mode:** image-to-image with BOTH locked reference anchors (`ref-sensoji.png` and `ref-shibuya.png`) passed as style references
- **Input fidelity:** `high` — the model must hold line-work weight, color flatness, and pattern density from the references

These are semantic parameters. The executing tool decides the invocation mechanics (CLI command, REST call, gateway, local runtime).

## Reference anchors

Two locked reference images live alongside this SKILL.md and define the look:

- `ref-sensoji.png` — Tokyo Senso-ji temple at golden hour: Kaminarimon gate with the giant red lantern, five-story pagoda, Mt. Fuji silhouette, drifting sakura petals, ink-outlined clouds, paper lanterns strung overhead, silhouette pedestrians. Anchors the **Tokyo warm palette**, **L3 architectural complexity**, **drifting-petals atmosphere**, **ink-cloud sky**, and **high pattern density** (roof tile shingle curves, woodgrain on pagoda beams, repeated lantern marks).
- `ref-shibuya.png` — Shibuya scramble crossing at twilight in the rain: indigo→magenta gradient sky, towering buildings packed with vertical neon kanji signs and lit windows, a sea of black-umbrella silhouettes with three focal sakura-pink / cyan / yellow umbrellas, a yellow taxi, wet asphalt with neon reflections. Anchors the **neon dusk palette**, **L3 modern urban complexity**, **rainy-streaks atmosphere**, **gradient-sky treatment**, and **very high pattern density** (endless tiny windows, vertical kanji marks, umbrella spokes, crosswalk stripes).

When generating, the executing agent should pass both references to the model as style anchors (image-to-image with high input fidelity). The prompt then names the new scene and dials the knobs.

## Locked style axes (NEVER vary)

### Orientation
- Tall portrait, approximately 2:3 — generate at 1024×1536.

### Line tool
- Fine BLACK MARKER or technical pen.
- Thin, fairly uniform weight. Confident, deliberate strokes.
- NOT a wet watercolor brush. NOT a wobbly sketch line. NOT variable calligraphic taper.
- Architectural straight lines are drawn straight, but with a hand-made feel — slight imperfections are welcome, geometric perfection is not.

### Color medium
- FLAT, SATURATED gouache or marker fills.
- Sharp, hard edges between color zones — colors do not bleed or blur into each other.
- NO wet-on-wet watercolor bloom.
- NO soft pastel haze or airbrush gradient (sky may have a gentle vertical gradient — see Sky knob below — but everywhere else is flat).
- Each color zone stays roughly within its ink contour, but small imperfections (a tiny patch of color crossing a line, a tiny patch of white inside a fill) read as hand-painted.

### Surface texture
- Subtle paper-grain texture layered across the whole canvas. Visible but quiet — never the dominant element.

### Speckles
- Small sparse scattered white (or white-pink) dot specks distributed across the canvas. They read as snow, drifting petals, or sparkle depending on the scene. Stay light and airy — never blizzard density.

### Mood
- Editorial, travel-journal, picture-book postcard. Charming, layered, slightly imperfect.

## Dial-able knobs (vary per illustration)

### 1. Palette
A saturated, warm-leaning postcard palette anchored in charcoal-black ink. Pick or compose one — examples:

- **Tokyo warm** — ivory / vermillion-red / slate-grey roof / sakura-pink / Fuji-blue (matches `ref-sensoji.png`).
- **Neon dusk** — deep indigo / magenta-pink / cyan-neon / window-gold / wet-asphalt charcoal (matches `ref-shibuya.png`).
- **Postcard warm** — cream / tan / ochre / sky-blue / red accents.
- **Botanical bright** — magenta-pink / lime-yellow / leaf-green / sky-blue / golden bee-yellow.
- **Jiangnan garden** — ivory / slate-grey roof / koi-orange / peony-pink / bamboo-green.
- **Nordic muted** — sage / sand / dusty-rose / charcoal.
- **Monsoon cool** — slate / teal / cream / mustard.

Always state 4–6 specific palette anchors in the prompt.

### 2. Scene archetype
- **Architectural landmark** — a building or street scene (temple, plaza, old town, monument).
- **Botanical close-up** — flowers, insects, a single small creature.
- **Interior** — a room, café, library, shop, bathhouse.
- **Vehicle / object** — boat, train, market stall, taxi.
- **Travel landscape** — mountains, harbor, garden, coastline.
- **Modern urban** — crossing, neon street, skyline.

### 3. Complexity
- **L1** — single subject + simple background. Sparse and graphic.
- **L2** — one main scene + light secondary layer.
- **L3** — dense layered scene with clear foreground, midground, and background (matches both `ref-sensoji.png` and `ref-shibuya.png`).

### 4. Atmosphere
- Snowfall (white speckles dominate).
- Drifting petals (sakura, jacaranda — speckles take on petal color).
- Bright clear daylight.
- Cloud-cover with ink-outlined fluffy cumulus clouds.
- Foggy or overcast.
- Golden hour or dusk.
- Rainy (speckles become diagonal rain streaks).
- Night with neon glow.

### 5. Sky treatment
- Solid color band.
- Vertical gradient (light blue → cream, or indigo → magenta-pink at dusk).
- Ink-outlined cumulus clouds against a gradient.
- No sky (the subject fills the canvas top to bottom).
- A distant mountain or landmark silhouette layered into the sky (Fuji, an alpine ridge).

### 6. Surface-pattern density
How busy the ink hatching / stippling / repeated marks are on surfaces.

- **Low** — clean fills with minimal marks.
- **Medium** — windows-as-rectangles on buildings, occasional hatching, simple shingle indication.
- **High** — every surface packed with stippling, shingle curves, micro-marks, woodgrain hatching, repeated kanji or signage marks (matches both `ref-sensoji.png` and `ref-shibuya.png`).

### 7. Cast
- None.
- 1–3 tiny silhouette pedestrians for scale.
- A featured creature (bee, cat, bird, koi).
- A dense crowd (umbrellas in rain, market shoppers).
- Bird silhouettes flying in the sky.

## Brief template the caller fills in

```
Palette: {palette name + 4–6 color anchors}
Scene archetype: {architectural | botanical | interior | landscape | urban | …}
Subject: {one or two sentences describing what the scene IS}
Complexity: {L1 | L2 | L3}
Atmosphere: {snowfall | drifting petals | clear | cloudy | dusk | rainy | …}
Sky: {solid | gradient | ink-clouds | mountain silhouette | none}
Pattern density: {low | medium | high}
Cast: {none | silhouette figures | featured creature | crowd | birds}
```

## Prompt assembly

When generating, compose a single prompt that:

1. Begins with: "Create a new illustration in EXACTLY the same hand-drawn editorial postcard style as the reference images."
2. Restates the LOCKED STYLE block in plain language: tall portrait, fine confident black marker/pen ink, flat saturated gouache fills, sharp edges, paper-grain texture, sparse white speckles, dense small repeated ink patterns, urban-sketcher mood.
3. Names the scene in concrete detail — foreground / midground / background elements, lighting, key props.
4. States the palette with 4–6 named color anchors.
5. Explicitly forbids: anime, manga, 3D rendering, photoreal, clean vector, soft watercolor wash, pastel haze.

Pass both locked reference images as style anchors (image-to-image / multi-image edit, high input fidelity) so the model holds the line-work weight, color flatness, and pattern density steady.

## Model guidance

See the **Required model** section near the top of this file for the locked model and required generation parameters. Additional notes:

- Do not request `--style` chaining with another registered image style — this style is self-contained and the resource is selected as the primary style.
- Do not silently fall back to a different image model if `gpt-image-2` is unavailable. Surface the unavailability and ask the caller before substituting — the locked look will not survive on a weaker model.

## Evaluation cues

A correct output should show:

- Tall portrait composition with clear foreground, midground, and background layering (L2 or L3) or a single subject on a simple flat background (L1).
- Black marker / pen ink line work that is thin, confident, and deliberate — visible across every shape.
- Flat saturated color fills with sharp edges between zones. No watercolor bleed.
- Dense small repeated ink marks on appropriate surfaces (windows, shingles, hatching, stippling) when pattern density is medium or high.
- Subtle paper-grain texture across the whole canvas.
- Small sparse white dot or streak speckles (snow, petals, sparkle, rain) distributed across the canvas.
- A palette that matches the brief's named anchors.

A wrong output usually shows one of:

- Soft watercolor wash with bleeding edges (treat as a regeneration trigger).
- Anime / manga character styling.
- Clean vector flat-design illustration with no ink hand.
- Photoreal or 3D rendering.
- Empty surfaces lacking the small repeated ink marks.
