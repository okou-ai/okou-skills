---
name: iberian-vignette
description: Hand-drawn editorial vignette illustration in a locked Iberian-Mediterranean style — loose wobble ink linework, flat muted color fills with a cream ground and burgundy/wine as the anchor color, exactly one secondary accent (sage / mustard / dusty blue / terracotta), minimal abstract faces (tiny dot eyes, soft nose hint, almost no mouth), casually-observed body language, and a short Spanish serif lowercase wordmark anchored at the bottom of the canvas. Always grounded by an architectural / scenic prop (doorway, archway, balcony, courtyard, counter). Trigger when the user says /iberian-vignette, asks for an "Iberian vignette illustration", a "Spanish editorial illustration", a "Mediterranean observed-moment scene", or briefs with a scene metaphor + cast + complexity in this hand-drawn editorial style.
---

# /iberian-vignette — locked Iberian editorial vignette style

This skill produces quietly cinematic, observed-moment vignettes in a hand-drawn Iberian-Mediterranean editorial aesthetic. Every piece reads as the same illustrator's hand — same loose wobble ink, same muted cream-and-burgundy palette, same minimal abstract faces, same intimate observed posture, same short Spanish serif wordmark anchored at the bottom.

The style was trained from a Spanish "equipo" editorial cover and refined across both trade-shop scenes (cafe, bookshop, bakery, tailor, flower market, kitchen, bodega, ceramics, bicycle repair) and domestic / leisure moments (morning coffee on a balcony, a couple slow-dancing, three generations on a courtyard bench). See `ref-l1-manana.png`, `ref-l2-ritmo.png`, `ref-l3-familia.png`, and `ref-l2-cafe.png` for the visual target.

## How to use this skill

The user gives a short brief — sometimes just a scene ("two friends at a market"), sometimes a fuller brief with palette + cast + wordmark. Your job:

1. Map the brief to the six dials below. Fill in any missing dial with a tasteful, period-coherent default.
2. Pick the matching complexity-tier reference anchor (L1 → `ref-l1-manana.png`, L2 → `ref-l2-ritmo.png` or `ref-l2-cafe.png`, L3 → `ref-l3-familia.png`) and feed it to the image model as a reference / source image.
3. Compose a prompt from the **Style brief structure** below, preserving the locked axes verbatim and filling in the dial fields.
4. Generate at portrait 2:3 (1024×1536 recommended) with the host style overlay bypassed so the model honors the locked brief.
5. Inspect the output against the **Quality checks** list before returning it.

If the brief is empty, default to: solo woman in a soft cream linen outfit on a small Mediterranean balcony with a steaming mug, sage green herb pot on the railing, terracotta rooftops below, wordmark `mañana`.

## Locked style axes (NEVER vary)

### Medium and surface

- **Hand-drawn editorial ink + flat color** — loose ink linework with visible wobble and varied weight (medium-fine pen feel; confident but imperfect, never digitally clean).
- **Flat opaque color fills** — no gradients, no airbrush, no rendered shading inside shapes, no halftone, no paper texture.
- **Background**: a single warm cream / off-white solid ground filling the entire canvas.
- **Floor (when shown)**: soft brown wood or stone.
- **Skin tones**: warm sand / beige.

### Anchor color

- **Burgundy / wine must be present in every piece** — somewhere visible in the scene (a sweater, a dress, a hanging sign, a chair, a clay pitcher, an apron, a pot). Without it, the piece drifts away from the locked family.

### Secondary accent (exactly one per piece)

- Sage green · mustard yellow · dusty muted blue · terracotta-rust. Used sparingly on a single prop, plant, sign, tile, or one piece of clothing. **Never two accents in the same piece** — that breaks the calibrated mood.

### Faces

- **Minimal abstract faces** — tiny dot or short-mark eyes, soft nose hint (a single short curve), barely any mouth (a faint short line at most). Never detailed facial features. Never cartoon dot pupils or big anime eyes.
- Pink blush is **not** used here (that belongs to other styles).

### Hair

- Flat solid color masses; the silhouette is one color block.
- A few simple texture marks (a curl, a wave) are okay; never rendered strands or airbrushed highlights.

### Posture and body language

- **Casually-observed** — leaning, holding, gently propped, mid-action without performance. People stand, lean, sit, pour, wipe, kneel, dance, look out — never stiffly posed and never freeze-framed dramatically.
- Energy goes in posture, never the face.

### Composition

- **Portrait orientation**, 2:3 (recommended 1024×1536).
- Centered, cinematic, intimate — figures clustered, never sparse.
- **Always grounded by an architectural / scenic prop**: a doorway, stone archway, window, balcony, courtyard, stone bench, counter, stoop, interior corner. Without the architectural anchor, the piece feels untethered.

### Wordmark

- A short **lowercase serif noun** anchored at the bottom center of the canvas. Bold serif. Always present.
- Typically Spanish or another Iberian language: `mañana`, `ritmo`, `familia`, `cafe`, `vino`, `pescado`, `sastre`, `libros`, `flores`, `cocina`, `bicis`, `panadería`, `ceramica`, `cena`, `tarde`.

### Mood

- Calm, intimate, observed; quietly cinematic. Mediterranean afternoon light. Never frantic, never glamorous, never melancholic. This is the warmth of an everyday moment held still.

### No edge artifacts

- The original training reference was a magazine spread cropped to leave fragments of body copy (`site`, `Sear`) at the canvas edges. **Do NOT include any cropped magazine text** at the edges of the canvas — that was a training artifact, not part of the style.

## Six creative dials (user-controlled)

| # | Axis | What it controls | Example values |
|---|---|---|---|
| 1 | **Scene metaphor** | The observed moment | morning coffee · evening dance · family courtyard · cafe conversation · flower market · tailor's workshop · bakery prep · bodega tasting · ceramics studio · bicycle repair · reading on a stoop · sharing a meal on a terrace |
| 2 | **Cast** | Who is in the scene | solo (L1), pair (L2), 3–4 figures (L3). Mix genders. Vary ages — child, young adult, mature, elder all welcome |
| 3 | **Architectural prop** | The scenic anchor | stone arched doorway · tall arched window · stone balcony · sunlit courtyard · wooden counter · interior corner with archway · stoop with cast-iron railing · open terrace with arbor |
| 4 | **Secondary accent (one only)** | The single non-burgundy color note | sage green (plants, ceramics, signage) · mustard yellow (lamp, awning, sign, skirt) · dusty muted blue (tile work, pottery glaze, clothing) · terracotta-rust (bottles, amphora, pots, brick) |
| 5 | **Wordmark** | The short Spanish noun anchored at the bottom | `mañana` · `ritmo` · `familia` · `cafe` · `vino` · `pescado` · `flores` · `sastre` · `libros` · `cocina` · `cena` · `tarde` · `bicis` |
| 6 | **Complexity** | Scene density | **L1** — 1 figure + 1–2 props, single architectural framing element · **L2** — 2 figures + small scene with arch prop · **L3** — 3–4 figures + full vignette interior, courtyard, or storefront |

## Style brief structure (fill the bracketed fields, keep everything else verbatim)

```
Hand-drawn editorial vignette illustration in a loose-ink Iberian-Mediterranean style. Loose hand-drawn ink linework with visible wobble and varied weight. Flat muted color fills only — NO gradients, NO shading, NO texture. Warm cream off-white background filling the canvas, soft brown floor where applicable. Casually-observed body language — leaning, holding, gently propped, mid-action without performance.

[CAST: number + genders + ages + clothing notes; warm sand skin tones; one or more figures show BURGUNDY / WINE as the anchor color (sweater, dress, sign, prop, apron — pick one)]. Minimal abstract faces: tiny dot or short-mark eyes, soft nose hint, almost no mouth. Hair as flat color masses. [POSE: how the figures sit, lean, stand, hold, work, dance — must read as observed mid-moment, never stiffly posed].

The scene is grounded by [ARCHITECTURAL PROP: stone arched doorway / tall arched window / stone balcony / sunlit courtyard / wooden counter / archway / stoop / open terrace] framing the figures.

Secondary accent color: [SAGE GREEN / MUSTARD YELLOW / DUSTY MUTED BLUE / TERRACOTTA-RUST], used sparingly on [WHERE IT APPEARS — one prop or one piece of clothing]. NO second accent color anywhere.

Wordmark at the bottom center of the canvas: the word "[WORDMARK]" in bold serif lowercase.

DO NOT add any cropped magazine text at the edges of the canvas — keep the canvas clean. No additional text, no logos, no watermarks.

Portrait orientation 2:3, recommended 1024×1536.
```

## Recommended model and reference handling

This style was trained on **nano-banana-2 (ByteDance)** in image-to-image mode, using one of the locked anchor references in this directory as the source image. The model is well-suited to the loose wobble ink + flat fill register and reliably preserves minimal-face anatomy across re-prompts when seeded from a reference.

When invoking the model:

- Generate at portrait 2:3 (1024×1536 recommended). The wordmark needs the vertical room.
- Bypass any host or app style overlay so the locked style brief above is what the model actually receives.
- Pass the **complexity-matched anchor** as the source / reference image:
  - L1 (solo) → `ref-l1-manana.png`
  - L2 (pair) → `ref-l2-ritmo.png` (warm interior) or `ref-l2-cafe.png` (window seating)
  - L3 (3–4 figures) → `ref-l3-familia.png`
- If the executor cannot fetch the reference attachment, document the limitation and proceed with a text-only prompt at higher creativity — outputs will be looser but still on-style.

Other models worth trying at lower fidelity: Seedream 5 (slightly cleaner edges, may over-tighten the wobble). Avoid Flux for this style — it tends to render the faces too photorealistically.

## Quality checks (review before returning the image)

- ✅ Line quality is loose and slightly wobbled, NOT crisp digital vector
- ✅ Color fills are flat — no gradients, no shading inside shapes
- ✅ Background is warm cream / off-white filling the canvas
- ✅ Burgundy / wine appears somewhere on a figure or prop (anchor color present)
- ✅ Exactly ONE secondary accent color (sage / mustard / dusty blue / terracotta) appears, used sparingly
- ✅ Faces are minimal — tiny dot eyes, soft nose hint, almost no mouth; NOT detailed
- ✅ Hair is a flat color mass, NOT rendered strands
- ✅ Posture reads as observed and casual — leaning, holding, mid-action
- ✅ The scene is grounded by an architectural / scenic prop (doorway, archway, balcony, courtyard, counter, etc.)
- ✅ A short Spanish serif lowercase wordmark sits at the bottom center
- ✅ NO cropped magazine text fragments at any canvas edge
- ✅ Portrait 2:3 orientation; nothing crucial clipped at top or bottom

If any of these fail, re-prompt with stronger emphasis on the failed axis — move it earlier in the prompt and add an explicit anti-pattern instruction — rather than regenerating with the same prompt.

## Anti-patterns to actively avoid

- Crisp digital vector linework — wobble is the style; clean lines break it
- Two or more accent colors — exactly one accent besides cream + burgundy + sand
- Detailed facial features — minimal abstract faces only
- Centered formal poses or symmetrical compositions — keep posture casual and observed
- Empty / floating composition with no architectural anchor
- Wordmark at the top, in a sans-serif, or in uppercase — bottom + lowercase + serif always
- Cropped magazine text at the canvas edges (training artifact)
- Adding aprons just because the original training image had aprons — aprons are scene-specific, not part of the locked frame

## Example briefs

### Example A — `mañana` (locked anchor, L1)

**Brief:** solo woman with morning coffee on a Mediterranean balcony, sage accent
**Filled:**
- Cast: 1 woman in a burgundy cardigan over cream linen, barefoot
- Pose: standing at the balcony railing holding a steaming mug with both hands, gazing out at terracotta rooftops
- Architectural prop: small stone balcony with curtain-draped balcony door behind her
- Accent: sage green (potted herb on the railing)
- Wordmark: `mañana`
- Anchor: `ref-l1-manana.png`

### Example B — `ritmo` (locked anchor, L2)

**Brief:** couple slow-dancing in a warm-lit living room, mustard accent
**Filled:**
- Cast: 1 man in burgundy crew-neck sweater + 1 woman in cream blouse and mustard skirt
- Pose: slow-dancing close, his hand at her waist, her arm draped over his shoulder
- Architectural prop: interior living-room corner with a vintage record player on a side table
- Accent: mustard yellow (her skirt + the warm table-lamp glow)
- Wordmark: `ritmo`
- Anchor: `ref-l2-ritmo.png`

### Example C — `cafe` (locked anchor, L2 alternate)

**Brief:** two friends sharing late-afternoon coffee near a tall arched window
**Filled:**
- Cast: 1 man in burgundy crew-neck sweater + 1 woman in cream blouse with mustard skirt
- Pose: leaning gently toward each other over small espresso cups at a small wooden cafe table
- Architectural prop: tall arched window beside the table
- Accent: mustard yellow (small mustard table lamp on the cafe table)
- Wordmark: `cafe`
- Anchor: `ref-l2-cafe.png`

### Example D — `familia` (locked anchor, L3)

**Brief:** three generations in a sunlit Mediterranean courtyard, dusty blue accent
**Filled:**
- Cast: grandmother with silver hair in a burgundy linen dress + mother in cream blouse and dark trousers + young child in a cream sundress holding an orange
- Pose: all three on a stone courtyard bench, grandmother turned toward the child, mother leaning gently back
- Architectural prop: arched stone courtyard wall with a small dusty-blue-tiled fountain and a potted lemon tree
- Accent: dusty muted blue (fountain tile)
- Wordmark: `familia`
- Anchor: `ref-l3-familia.png`

### Example E — `vino` (new brief, L3, terracotta accent)

**Brief:** three vintners around a tasting bar in a small wine bodega
**Filled:**
- Cast: older bearded man pouring + younger woman across the bar swirling a glass + younger man wiping a glass behind the bar
- Pose: mid-pour, mid-swirl, mid-wipe — observed working moment
- Architectural prop: wooden bar inside a small bodega with wooden shelves behind
- Accent: terracotta-rust (rows of terracotta-colored bottles + a clay amphora at the end of the bar)
- Wordmark: `vino`
- Anchor: `ref-l3-familia.png`

### Example F — `flores` (new brief, L2, mustard accent)

**Brief:** two flower-market vendors under a striped awning
**Filled:**
- Cast: 1 woman in burgundy apron arranging bouquets + 1 man in burgundy apron leaning on the side of the stall holding a stem
- Pose: working the morning stall, mid-conversation
- Architectural prop: wooden flower stall under a mustard-and-cream striped awning
- Accent: mustard yellow (awning stripes)
- Wordmark: `flores`
- Anchor: `ref-l2-ritmo.png`
