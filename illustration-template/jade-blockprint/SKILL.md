---
name: jade-blockprint
description: Two-pass hand-drawn block-print spot illustration — one accent color painted as free-floating shapes on pure white, with chunky black ink line art layered on top. Imperfect screen-print feel, linocut speckle grain. Eight named palettes plus custom hex; resolves vague prompts to concrete scene metaphors automatically. Trigger when the user says /jade-blockprint, asks for a "block-print illustration", "linocut spot illustration", "two-tone screen-print", or briefs a metaphor for a blog cover or marketing card in this style.
---

# /jade-blockprint — locked two-pass block-print style

This style produces editorial spot illustrations with a hand-pressed mid-century feel. Every piece is built from exactly two ink colors — one accent + chunky black — laid down as two separate "plates" the way a screen print or linocut would print them: color blob first, ink line art on top. The accent shape floats free with no black outline tracing it; the ink layer sits on top selectively, drawing detail rather than perimeter.

The locked frame (white surface, two-tone palette, two-pass layering, wobbly linework, linocut speckle) never moves. The dials (palette hue, scene metaphor, complexity, motion marks, speckle density) vary per piece. The skill also resolves abstract/vague briefs into concrete scene metaphors before generating, so a prompt like *"growth"* or *"trust"* becomes a real object on the page.

## Prompt interpretation

The user may give:

- A concrete object — *"a vintage rotary phone"*, *"a campsite at dusk"*
- An abstract concept — *"growth"*, *"trust"*, *"freedom"*
- A topical brief — *"cover for our pricing-fairness announcement"*, *"empty state for the audit log page"*

Translate that into a full block-print brief without stopping to ask:

1. **Resolve the scene metaphor.** If the brief is abstract or topical, pick the most concrete story-bearing object or 2–3 element mini-scene that visualizes it (see the metaphor synthesizer table below). Never render abstract shapes, gradients, or word-art. The scene IS the metaphor — no generic icon catalogs of filing cabinet + megaphone.
2. **Pick a palette.** Either a named preset from the table, or honor a user-provided hex. If unspecified, choose the preset whose mood matches the brief.
3. **Pick a complexity level (L1 / L2 / L3).** L1 = single hero object. L2 = 2–3 element mini-scene. L3 = wider environmental vignette. Default L1 unless the brief calls for a scene.
4. **Decide on motion marks.** Small radiating hash lines around the subject if the metaphor implies motion / sound / energy / freshness. Skip for stillness, calm, repose.
5. **Pick speckle density.** Sparse for refined palettes (slate / rose / sage), medium otherwise. Dense only on explicit "rougher" / "hand-pressed" requests.
6. **Honor the locked frame.** White background, two-pass layering, free-floating color blobs, ink-on-top selective detail, wobbly linework, linocut grain. Those never move.

After resolving the metaphor, narrate the choice to the user in one short line ("rendered as a paper airplane mid-flight for *freedom*") so they can redirect if they had a different scene in mind.

## Locked style axes (NEVER vary)

### Surface

- Pure white background `#FFFFFF`. No cream, no off-white, no aged-paper tint. No background texture, no border, no frame.
- Canvas defaults to 1024×1024 square. Override to 1024×1536 (tall) or 1536×1024 (wide) only when the brief or use-case demands a non-square aspect.

### Two-tone palette

- Exactly two ink colors per piece: one accent + chunky black. Never a third color, never shading gradients, never multiple hues.

### Two-pass layering (CRITICAL — this is the defining rule)

- The accent color is the **first plate**: free-floating shapes laid down on white. The colored blobs have **NO black perimeter outline tracing them**. They stand alone as colored shapes.
- The black ink is the **second plate**, drawn on top: outlines of small details, hatching, motion marks, internal structure. The ink never traces around the color shapes themselves.
- Color and ink overlap imperfectly, the way a two-color screen print does when the colored plate is laid down before the key plate. Some inked elements have no color underneath. Some color blobs have no ink on top — they can stand alone.
- A common signature: a colored blob shape (a sail, a teapot body, a vinyl record body) sits free-floating while a fully-inked subject (the ship's hull, the spout, the record's grooves) is drawn on top of or beside it.

### Linework

- Hand-drawn, wobbly, confident, with **variable line weight**. Never uniform stroke width.
- Occasional **flooded solid-black masses** for heavy shadow or dense detail (the inside of a camera body, the keys of a typewriter, a dense leaf cluster).

### Texture

- Tiny black speckle dots inside the color fills for linocut grain. Sparse to medium density. Never dense enough to read as halftone or noise — these are individual ink dots, not a screen.

### Composition

- Single hero object or compact 2–3 element mini-scene, centered on the field with a slight intentional tilt. Never axis-aligned.
- No border, no frame, no headline text, no decorative inset, no caption strip.
- Mid-century block-print / linocut / hand-pressed feel. Editorial, warm, made-by-hand.

## Dials (vary per piece)

### Palette (named preset OR custom hex)

| Name | Hex | Mood |
|---|---|---|
| `jade` | `#3FD89A` | Fresh, signature — original reference color |
| `coral` | `#E94F3F` | Warm, energetic |
| `cobalt` | `#2C5BFF` | Cool, editorial |
| `plum` | `#9B3D6E` | Moody, premium |
| `sage` | `#8FAA8C` | Calm, botanical |
| `rose` | `#C58B85` | Refined, soft |
| `slate` | `#6B7F99` | Intellectual, neutral |
| `terracotta` | `#B86F4D` | Warm, earthy |

If unspecified, infer:

- Warm / energetic / launch topic → coral or terracotta
- Cool / editorial / intellectual → cobalt or slate
- Calm / botanical / refined → sage or rose
- Moody / premium → plum
- Signature / fresh / launch context → jade

Custom accent: honor any hex the user provides verbatim.

### Scene metaphor

Concrete object or mini-scene that carries the meaning. The scene IS the metaphor. Pick theme-native props. Never reuse the same metaphor across a series.

### Complexity

- **L1** — single hero object, tight crop (camera, teapot, bicycle, rotary phone, lightbulb)
- **L2** — 2–3 element mini-scene (desk + lamp + mug; pitcher + olive branch; pen + notebook + ink well; perfume bottle + bloom cluster)
- **L3** — wider environmental vignette (sailing ship on rolling waves; campsite with tent + pine + fire + moon)

### Action / motion marks

Small radiating hash lines around the subject. Use for movement / sound / energy / freshness. Skip for stillness / calm / repose.

### Speckle density

- Sparse — refined editorial mood, light hand-pressed feel (default for slate, rose, sage)
- Medium — default for everything else; visible but not noisy
- Dense — rough / heavily hand-pressed feel (only on explicit ask)

## Metaphor synthesizer (vague-prompt handling)

If the brief is an abstract concept or topical phrase rather than a concrete object, resolve it to a concrete scene **before generating**. Never render abstract shapes, gradients, or word-art for a fuzzy brief.

| Vague prompt | Concrete scene metaphor |
|---|---|
| Growth | Sprouting potted plant; vine climbing a trellis |
| Trust | Two hands clasping a sealed envelope; key + lock on a ring |
| Freedom | Paper airplane mid-flight; kite on a string; bird taking off |
| Speed | Bicycle with motion streaks; sparrow in flight |
| Calm | Teapot with rising steam; cat curled asleep in a ball |
| Discovery | Magnifying glass over an unfolded map; brass telescope; compass |
| Connection | Tin-can telephone; coiled cord between two ends |
| Balance | Stacked rock cairn; weighing scales |
| Reflection | Mirror leaning on a wall; lake with a single tree reflected |
| Beginnings | Single sprout in soil; sunrise behind a hill |
| Memory | Old photograph + open envelope; cassette tape |
| Curiosity | Cat peeking from a cardboard box; magnifying glass + butterfly |
| Focus | Lit lamp on a desk in the dark; bullseye + dart |
| Time | Hourglass; pocket watch on a chain |
| Routine | Coffee mug + croissant + folded newspaper |
| Idea | Old-fashioned lightbulb with radiating motion hashes |
| Fairness / pricing fairness | Balance scales; two equal stacks of coins |
| Privacy / safety | Closed envelope sealed with wax; lock + key on a ring |
| Productivity | Pen + open notebook + steaming coffee |
| Launch / release | Paper airplane taking off; rocket on a launchpad |

If the concept isn't listed, pick the most concrete, story-bearing object available. Default to a single L1 hero unless the brief asks for a scene.

After picking, narrate the chosen scene in one short line so the user can redirect.

## Prompt template

When generating, build a prompt of this shape:

```
Two-pass hand-drawn block-print illustration. Pure white background (#FFFFFF, no cream tint). Two-tone palette: {PALETTE_NAME} ({PALETTE_HEX}) flat color shapes AND chunky black ink line art. CRITICAL RULE: the {PALETTE_NAME} color is painted FIRST as free-floating shapes — the colored blobs have NO black perimeter outline tracing them. The black ink line art is drawn on top as a separate layer (outlines of small details, hatching, motion marks), but never traces around the color shapes. Color and ink overlap imperfectly, like a two-color screen print where the colored plate was laid down before the key plate. Subject: {SCENE_DESCRIPTION}. The {KEY_COLORED_ELEMENTS} are free-floating {PALETTE_NAME} blobs (no perimeter outline around them). Ink lines on top draw {INK_DETAILS}. {ACTION_MARKS_IF_ANY}. Tiny black speckle dots inside the {PALETTE_NAME} for linocut grain. No frame, no headline text. Centered subject, slight tilt. Mid-century linocut hand-printed feel. {SIZE_WORD} canvas.
```

Substitute every field. Be specific about which elements are colored blobs and which are ink-only — this is what the layering rule depends on.

## Model guidance

The style was developed against `gpt-image-1.5` (square 1024×1024, medium quality). The two-pass layering rule lands cleanest when:

- The CRITICAL RULE phrasing is repeated verbatim in the prompt.
- Specific colored elements are named as "free-floating blobs (no perimeter outline)" rather than letting the model decide.
- The "two-color screen print" / "color plate laid down before the key plate" metaphor is included — it nudges the model toward the right mental model.

Other image models with sufficient prompt fidelity should work, but expect drift on the perimeter-outline rule unless the prompt is explicit. Lower-fidelity models may add a thin outline to color shapes; if that happens, regenerate with stronger emphasis on the free-floating rule, or post-process to remove the residual outline.

The model does not need image-to-image references — text-only prompts using this template produce on-style results.

## Example briefs

### Brief 1 — concrete object
> *a vintage rotary telephone with a ringing handset*

Palette: default `jade`. Complexity: L1. Scene: rotary phone, receiver lifted, coil cord trailing, small motion hashes near the bell. Speckle: medium.

### Brief 2 — abstract concept
> *growth, palette=sage*

Metaphor synthesis: *growth* → small terracotta pot with a single fresh sprout breaking through the soil, two heart-shaped leaves on a tender stem. Motion hashes around the sprout for freshness. Palette: `sage` (calm/botanical). Complexity: L1. Narrate the choice.

### Brief 3 — topical brief
> *cover for our pricing-fairness announcement, palette=slate, complexity=L2*

Metaphor: pricing fairness → balance scales with two equal stacks of coins. Palette: `slate` (intellectual/neutral). Complexity: L2. No motion marks (stillness).

### Brief 4 — custom accent + tall canvas
> *a single paper airplane mid-flight, accent=#3F704D, size=1024x1536*

Custom forest-green accent. L1 paper airplane with motion-streak hashes trailing behind. Tall portrait aspect.

## Reference pieces

- `ref-coral-turntable-l1.png` — Coral L1, vinyl record on a free-floating coral body; the cleanest example of the layering rule
- `ref-cobalt-ship-l2.png` — Cobalt L2, sail and waves are free-floating blobs; hull + rigging are pure ink
- `ref-sage-teapot-l1.png` — Sage L1, refined teapot with decorative band
- `ref-rose-perfume-l2.png` — Rose L2, perfume bottle + bloom cluster
- `ref-slate-pen-notebook-l2.png` — Slate L2, fountain pen + notebook + ink well still life
- `ref-terracotta-pitcher-l2.png` — Terracotta L2, ceramic pitcher + olive branch
- `ref-mustard-monstera-l1.png` — Mustard L1, monstera leaves as free-floating blobs with ink veins on top
- `ref-sage-sprout-l1.png` — Sage L1, *growth* metaphor smoke test

## Anti-patterns

- Cream, off-white, or aged-paper backgrounds — always pure white.
- Black perimeter outlines tracing the colored shapes — the color must float free; ink draws detail, not perimeter.
- Three or more colors in a piece — strictly two-tone (one accent + black).
- Smooth uniform stroke width — linework breathes.
- Headline text, framed borders, caption strips — never.
- Returning purely abstract shapes / word-art / gradient blobs for a fuzzy brief — always resolve to a concrete scene metaphor first.
- Generic icon-catalog metaphors (filing cabinet + megaphone with relabeled tabs) — pick theme-native props.
- Reusing the same scene metaphor across a series — vary it; the scene is a per-piece dial.
- Dense halftone / noise patterns inside color fills — speckle is individual visible ink dots, not a screen.
