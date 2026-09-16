---
name: crowd-ink
description: Hand-drawn editorial crowd illustration — confident sketchy black ink contours over flat 3-color spot fills on a pure-white background, scene-as-metaphor composition, fine-line backdrop drawn lighter than the foreground, and scattered atmospheric marks in negative space. Trigger when the user says /crowd-ink, asks for a "crowd-ink illustration", an "editorial crowd scene", a "hand-drawn ink-and-spot-color illustration", a "New-Yorker-style crowd vignette", or briefs with a palette + scene metaphor + complexity level.
---

# crowd-ink — locked editorial crowd illustration

This style produces a hand-drawn editorial crowd vignette. The locked frame is strict: confident sketchy black ink lines, flat 3-color spot fills on pure white, fine-line backdrop, scattered atmospheric specks, scene-as-metaphor composition. Only the dials change per piece — palette, scene metaphor, complexity, cast, backdrop, atmospheric motif.

The anchor reference (`anchor.png`) is a packed city bus stop in mustard + coral + dusty slate. Always use it as the visual i2i seed when the generation pipeline supports image-to-image — the line weight and palette discipline transfer much more reliably with the seed than with text-only prompting.

## Prompt interpretation

The user typically gives a short brief — usually a scene + a palette. Expand it confidently:

1. Pick complexity from the brief or default to **L3** (8–10 figures) for energetic scenes and **L2** (3–5 figures) for intimate scenes. Avoid L1 (single figure) unless the user explicitly asks — solo figures lose the crowd energy that defines the style.
2. Cast a varied set of people for the scene — mix age, posture, profession-appropriate dress. Never reuse the same recurring character across pieces.
3. Pick a backdrop and atmospheric motif that match the scene metaphor (birds for urban, leaves for nature, steam for food, confetti for festival, dots/specks as a safe default, music notes for parties).
4. Render the prompt and run.

Bias toward concrete moments: a woman with shopping bags, a man checking his watch, a teenager with headphones, an elderly couple leaning together. The scene should feel observed, not staged.

## Locked frame (NEVER vary)

### Background
- **Pure white.** Not cream, not off-white, not paper texture. This is a hard constraint — if the model drifts toward a warm/cream paper background, the result is wrong and must be regenerated.

### Line treatment
- Confident sketchy black ink contour lines.
- Slightly irregular weight — visible pressure variation, a hand-drawn wobble. Never vector-clean, never marker-uniform.
- Foreground figures get the heaviest, most confident strokes. Backdrop elements are drawn with thinner, lighter ink so the foreground reads first.

### Color treatment
- Flat spot-color fills sitting **under or beside** the ink lines.
- Edges allowed to misregister slightly — colors don't need to live inside the contour perfectly. Slight offset is part of the charm.
- **No shading. No gradients. No lighting effects. No texture inside fills.**
- Black ink does not count as a fill color — it's always available as the line layer.

### Palette discipline
- **Strict 3-color spot palette** plus black ink. Never exceed 3 fill colors.
- The palette is one of the explicit dials. See "Tested palette families" below for proven options.

### Backdrop
- Fine-line environmental setting (cityscape, office, transit interior, market, park, café, etc.).
- Drawn in **lighter / thinner ink** than the foreground figures so the eye reads the people first.
- Should match the scene metaphor — a coffee shop has an espresso machine and a menu board, an airport has departure screens and rolling luggage, a park has trees and a bench.

### Atmospheric marks
- Scattered marks float in the negative space above the figures: tiny dots, specks, birds, leaves, steam, paper, music notes, confetti.
- Choose to match the scene mood: urban → birds, nature → leaves, food/drink → steam, party → confetti + music notes, default → small dots.

### Composition
- **Scene-as-metaphor.** The scene IS the message — no generic "office metaphor" props (filing cabinets, megaphones) glued on top. Pick theme-native props.
- Figures or objects mid-action, never posed or symmetrical.
- Cast varies per piece — there is no locked recurring mascot.

### Anti-marks
- No text. No logo. No watermark. No captions inside the image.

## Dials (vary per piece)

1. **Palette** — 3 spot colors + black ink. Tested families:
   - **Urban editorial (anchor):** mustard yellow + coral red + dusty slate blue
   - **Cool transit:** teal blue + tangerine orange + dusty slate
   - **Warm natural:** sage green + dusty rose + butter yellow
   - **Cozy interior:** burgundy red + mustard yellow + sage green

   New palettes are welcome as long as they stay in the same 3-color editorial-spot register — saturated but slightly desaturated, mid-tone, not neon, not pastel-mushy.

2. **Scene metaphor** — the per-piece concept. Tested examples: bus stop, open-plan office, park picnic, subway interior, café conversation, market, airport departure, street festival, library, team standup.

3. **Complexity**
   - **L2** — small group, 3–5 figures (intimate scenes — café, picnic, conversation, standup)
   - **L3** — full crowd vignette, 8–10+ figures (energetic scenes — bus stop, subway, market, office, festival; this is the anchor density)
   - L1 (single figure) is allowed but generally discouraged; the style is defined by the crowd.

4. **Cast** — who's in the scene; varies per piece. Mix age, demographics, posture. Give each figure a small individual gesture (checking phone, holding bags, leaning, gesturing, sleeping).

5. **Backdrop** — fine-line environment matching the scene (cityscape, office, transit interior, café, market, park).

6. **Atmospheric motif** — what floats in negative space.

## Prompt template

When asking the model to render a piece, structure the prompt as:

```
Match the exact style of the reference image (anchor.png in this resource): editorial hand-drawn illustration on a PURE WHITE background (no cream, no off-white, no paper texture). Confident sketchy black ink contour lines with slightly irregular weight. Flat spot-color fills sitting under or beside the ink lines (edges allowed to misregister slightly, no shading, no gradient). Strict 3-color palette: {COLOR_1}, {COLOR_2}, {COLOR_3}, plus black ink.

SCENE: {SCENE_METAPHOR} — {COMPLEXITY: L2 small group of 3–5 / L3 full crowd of 8–10}, {CAST_DESCRIPTION_WITH_INDIVIDUAL_GESTURES}. {DETAILS_AND_PROPS}.

Fine-line backdrop of {BACKDROP_ELEMENTS} drawn in lighter thinner ink.

Scattered atmospheric marks: {ATMOSPHERIC_MOTIF} in the negative space above.

NO CREAM, BACKGROUND MUST BE WHITE. No text. No logo.
```

## Model guidance

- Use a high-fidelity instruction-following image model with image-to-image input (the anchor reference is the seed). Strong matches in practice: `gpt-image-1.5` at landscape (1536×1024) with high input fidelity.
- If text-to-image is the only option, expect the model to drift toward cream / off-white backgrounds. Re-emphasize "pure white" in the prompt and accept that the line weight may feel cleaner than the anchor.
- Default canvas is **landscape 1536×1024** for blog covers and marketing. Portrait 1024×1536 is acceptable when explicitly briefed.
- Per-piece variation comes from the dials, not from sampling parameters — keep the dials explicit in the prompt rather than relying on temperature/seed variance.

## Example briefs

**Brief 1 — anchor: bus stop crowd (L3, urban editorial)**
> A packed bus stop on a city street — L3 full crowd of 8–10. Standing passengers including a woman with shopping bags, a man checking his watch, teenagers with backpacks, an elderly couple. Palette: mustard yellow, coral red, dusty slate blue. Backdrop: bus, city buildings, BUS STOP sign. Atmospheric: birds and small dots.

**Brief 2 — interior B2B: open-plan office (L3, urban editorial)**
> A crowded open-plan office floor — L3 full crowd of 8–10. Presenter at whiteboard, colleagues at desks with laptops, two people in conversation, someone walking with coffee. Palette: mustard, coral, dusty slate blue. Backdrop: office furniture, glass partitions, ceiling lights. Atmospheric: floating papers and dust specks.

**Brief 3 — intimate: café conversation (L2, cozy interior)**
> 3 friends mid-conversation at a small round café table — L2 small group. One laughing, one gesturing with hands, one leaning forward with a coffee cup. Pastries and cups on the table. Palette: burgundy, mustard yellow, sage green. Backdrop: espresso machine, hanging menu board, large window with city silhouette. Atmospheric: tiny dots and steam wisps.

**Brief 4 — natural: park picnic (L2, warm natural)**
> 4 friends having a park picnic on a blanket — L2 small group. One pouring lemonade, one lying back on elbows, one with a guitar, one offering a sandwich. Palette: sage green, dusty rose, butter yellow. Backdrop: park trees, bench, distant joggers. Atmospheric: small floating leaves.

**Brief 5 — transit interior: packed subway (L3, cool transit)**
> Inside a crowded subway car — L3 full crowd of 8–10. Some standing holding hand straps, some seated; a man reading a folded newspaper, a teen with headphones, a tired commuter dozing. Palette: teal blue, tangerine orange, dusty slate. Backdrop: train car interior, windows, ads above seats, ceiling lights. Atmospheric: dots between heads.

## Reference assets

- `anchor.png` — packed city bus stop, urban editorial palette. Use as the i2i seed.
- `sample-office.png` — open-plan office, urban editorial palette (B2B-friendly).
- `sample-picnic.png` — park picnic L2, warm natural palette.
- `sample-subway.png` — subway interior L3, cool transit palette.
- `sample-cafe.png` — café conversation L2, cozy interior palette.

## Anti-patterns (do not regress)

- ❌ Cream / off-white / paper-texture backgrounds. Pure white only.
- ❌ More than 3 spot colors plus black ink.
- ❌ Shading, gradients, or modeled volume inside fills.
- ❌ A locked recurring character across pieces.
- ❌ Generic office-metaphor props (filing cabinets, megaphones) glued onto unrelated scenes.
- ❌ Vector-clean line weight or marker-uniform thickness.
- ❌ Captions, labels, or any text inside the image.
- ❌ Skipping the i2i seed — text-to-image alone tends to drift toward cream backgrounds and tidy line weight.
