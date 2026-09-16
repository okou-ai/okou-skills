---
name: tiny-wanderer
description: Contemplative bande-dessinée landscape illustration in a locked house style — a tiny human (or 2–3 figures) dwarfed by a vast natural panorama, hand-drawn black ink contour + parallel hatching for clouds/rock/grass texture, flat color fills sitting beneath the ink, restrained 3–5 color palette, vertical portrait canvas. Mood is quiet wonder, Moebius / Christophe Chabouté travel-sketchbook lineage. Trigger when the user says /tiny-wanderer, asks for a "tiny wanderer illustration", a "bande-dessinée landscape", a "Moebius-style travel illustration", an "ink-hatched vertical landscape", or briefs with a palette + landscape archetype + complexity in this house style.
---

# /tiny-wanderer — locked contemplative landscape illustration

Forge a vertical-portrait landscape illustration in the **tiny-wanderer** house style: a tiny human figure (or 2–3 figures) dwarfed by a vast natural panorama, drawn in confident hand-drawn black ink with parallel/cross-hatching for sky/rock/grass texture, sitting on top of restrained flat color blocks. Mood: quiet wonder. Lineage: Moebius, Christophe Chabouté, French BD landscape comics.

Every invocation flexes the dials below against a locked frame. The frame never changes; the dials describe the per-piece scene.

## Locked frame (never change)

- **Canvas** — Vertical portrait, 1024×1536 (~2:3 aspect, reads as ~3:5). Always portrait, never landscape.
- **Line treatment** — Hand-drawn black ink contour lines with confident parallel hatching and cross-hatching for ALL texture: clouds, rock walls, foliage masses, grass tufts, water ripples, distant haze. Variable line weight, slight wobble — never mechanical. Hatching is the only shading method.
- **Color rule** — Flat color fills sit *underneath* the ink linework. No gradients, no airbrush modeling, no shading inside fills. All texture comes from ink hatching on top.
- **Figure rule** — Human figure(s) are always tiny relative to the landscape. The landscape dominates; the figure is the eye's entry point but never the subject — the *scale relationship* is the subject.
- **Palette discipline** — 3–5 colors per piece, including black ink. No more than 5 hues including neutrals.
- **Subject** — Always outdoors. Wilderness, mountains, plains, coast, valley, ridge, river. Never urban, never interior.
- **No frame elements** — No text, no borders, no logos, no signature.

## Dials (vary per piece)

| Dial | Options |
|---|---|
| **Palette family** | `sage-plains` (sage + olive + cream + white + ink) · `sunset-warm` (dusty rose + terracotta + sage + denim + cream + ink) · `coastal-teal` (teal + chalky white + sage + sand + pale blue + ink) · `cool-mist` (slate blue + sage + cream + ochre + dusty blue + ink) · `autumn-rust` (burnt orange + ochre + sage + cream + ink) · `winter-pale` (pale blue + cool grey + cream + sage + ink) · or custom 3–5 hex set |
| **Landscape archetype** | plains+clouds · mountain valley · river vista · rocky ridge · coastal cliffs · misty gorge · forest clearing · alpine pass · desert mesa · lakeshore |
| **Activity** | walking · hiking with backpack · cycling · standing-and-gazing · sitting-on-rock · paused-mid-step |
| **Solitude count** | 1 (lone) · 2 (paired) · 3 (small group). Never more than 3. |
| **Complexity** | **L1** — single plane: sky + foreground only, one figure (e.g. walker on plain under huge clouds). <br>**L2** — foreground + middle ground + distant horizon (e.g. hikers on ridge looking at distant peaks). <br>**L3** — full multi-plane vista: foreground rock/path + mid river/valley + distant cliff walls or peaks, often framed by foreground masses on both sides. |
| **Weather / time** | bright midday · golden hour · sunset (banded hatched sky) · overcast · misty/foggy · blue hour · early morning haze |

## Prompt template

Fill the bracketed slots, drop everything else verbatim. Bake the locked frame in every time — don't trust the model to remember.

```
Vertical portrait illustration (3:5) in a contemplative bande-dessinee travel-sketchbook
style. Hand-drawn black ink contour lines with confident parallel hatching and cross-hatching
for {TEXTURE_TARGETS}. Flat color fills sit UNDERNEATH the ink linework, never modeled or
gradient. {FIGURE_COUNT} {ACTIVITY} {SCENE}, dwarfed by the landscape. {ATMOSPHERE}.
Restrained limited palette: {PALETTE_DESCRIPTION}. Quiet wonder mood, Moebius and Christophe
Chaboute lineage. No text, no logos, no borders, no signature.
```

### Slot fills

- **TEXTURE_TARGETS** — name the surfaces the ink is hatching, e.g. "clouds and grass", "rock walls and mist", "cliffs and ocean waves", "snow peaks and foreground rocks", "tree foliage and distant hills"
- **FIGURE_COUNT** — "A single tiny figure" / "Two small figures" / "Three small figures"
- **ACTIVITY** — "walking" / "cycling" / "standing in profile gazing" / "hiking with a small backpack" / "paused on a rocky outcrop"
- **SCENE** — concrete landscape sentence, e.g. "across rolling open meadows", "on a foreground rocky ridge above a desert valley", "along the edge of dramatic chalky sea cliffs", "on a winding path beside a meandering river deep in a tall misty mountain valley"
- **ATMOSPHERE** — sky/light treatment, e.g. "towering puffy cumulus clouds drawn with dense curving ink hatching dominate the upper two-thirds", "sky striped with hand-hatched horizontal bands of dusky pink and pale blue at sunset", "low mist drifting through the middle distance with hatched cliff walls flanking both sides", "hatched cloud-streaked sky with tiny v-mark gulls"
- **PALETTE_DESCRIPTION** — name 3–5 colors explicitly plus black ink, e.g. "sage green grass, white clouds with fine black hatching, warm cream sky, black ink" or "dusty rose, terracotta rocks, sage green scrub, denim blue distant peaks, warm cream highlights, black ink"

## How to interpret a brief

The user will usually give a short scene seed (e.g. "morning hike", "solo bike trip", "vast emptiness"). Expand it into the locked frame:

1. **Pick the palette family.** Default to `sage-plains` for openness, `sunset-warm` for warmth, `cool-mist` for solitude, `coastal-teal` for clarity. Custom hex sets are allowed but must stay within 5 colors total.
2. **Pick the landscape archetype.** Match the mood — open `plains+clouds` reads serene; `misty gorge` reads cinematic; `coastal cliffs` reads bracing.
3. **Pick the figure count and activity.** Default to a single walker. Add a second figure only when companionship is part of the brief. Cycling reads as journey; standing-and-gazing reads as arrival.
4. **Choose complexity.** Default to L2 unless the brief is explicitly minimal (L1) or scenic (L3).
5. **Design the atmosphere line.** This is the one most-skipped slot — without explicit sky/light treatment instructions, the model defaults to bland midday. Always specify what the sky is doing and how its texture is rendered.

## Example briefs

**Brief 1 — L1 / sage-plains / lone walker**
> A single tiny walker with a backpack crosses rolling open meadows at midday, dwarfed by towering puffy cumulus clouds drawn with dense curving ink hatching that fills the upper two-thirds. Palette: sage green grass with olive shadow patches, white clouds with fine black hatching, warm cream sky, black ink.

**Brief 2 — L2 / sunset-warm / two hikers gazing**
> Two small hiking figures stand on a foreground rocky ridge in profile, gazing across a layered desert valley toward distant snow-capped peaks, dwarfed by the landscape. Sky striped with hand-hatched horizontal bands of dusky pink, peach, and pale blue at sunset. Palette: dusty rose, terracotta rocks, sage green scrub, denim blue distant peaks, warm cream highlights, black ink.

**Brief 3 — L2 / coastal-teal / three hikers on cliffs**
> Three tiny figures walk single-file along the edge of dramatic chalky white sea cliffs above a vast turquoise ocean horizon, dwarfed by the landscape, tiny v-mark gulls scattered in a hatched cloud-streaked sky. Palette: chalky off-white cliffs with fine black hatching, sage green clifftop grass, teal-blue ocean, warm sandy beach below, pale blue sky, black ink.

**Brief 4 — L3 / cool-mist / lone cyclist in gorge** (the anchor variation)
> A single tiny lone cyclist rides along a winding path beside a meandering river deep inside a tall misty mountain valley, dwarfed by the landscape, towering hatched rock walls flanking both sides of the frame, low mist drifting through the middle distance. Full multi-plane vista: foreground path with grass tufts, mid-distance river, far cliff walls. Palette: cool slate blue rock walls, sage green grass, soft cream mist, pale ochre dirt path, dusty blue river, black ink.

## Anti-patterns

- ❌ Modeled / gradient color fills. Texture is ink hatching only.
- ❌ Figure large enough to be the subject — the landscape must always dominate.
- ❌ Interior or urban scenes.
- ❌ More than 3 figures.
- ❌ More than 5 colors (including black ink).
- ❌ Landscape orientation. Always portrait.
- ❌ Text, logos, watermarks, signatures, or border frames.
- ❌ Locking a recurring character across pieces — cast is per-scene, not a mascot.
- ❌ Painterly soft brushwork or watercolor bleeds — every texture is line-based hatching.

## Output evaluation checklist

Before delivering, confirm:

- [ ] Canvas is vertical portrait (~3:5).
- [ ] The human figure(s) read as tiny — the landscape clearly dominates the frame.
- [ ] All shading is hand-drawn parallel hatching or cross-hatching, not gradient or airbrush.
- [ ] Color fills are flat and sit beneath the ink linework.
- [ ] Total palette is ≤5 colors including black ink.
- [ ] Scene is outdoor/wilderness — no urban, interior, or domestic props.
- [ ] No text, borders, logos, or signatures anywhere in the frame.
- [ ] If multi-figure (2–3), figures still read as tiny — not a group portrait.

## Model notes

This style was trained on `gpt-image-1.5` at high quality, 1024×1536. Other capable editorial-illustration models (e.g. `nano-banana-2`, `flux-pro-1.1`) can reproduce it if the prompt template above is followed verbatim. The "hand-drawn ink hatching" + "flat color UNDERNEATH the ink" + "dwarfed by the landscape" instructions are load-bearing — paraphrasing them tends to drift toward soft watercolor or photographic landscape. The explicit "Moebius / Christophe Chaboute lineage" cue strengthens the ink-hatching texture significantly; keep it in.

## Reference pieces

The four anchor variations (in this directory):

- `varA.jpg` — L1, sage-plains, lone walker under towering hatched cumulus clouds
- `varB.jpg` — L2, sunset-warm, two hikers gazing across a desert valley toward snow peaks
- `varC.jpg` — L2, coastal-teal, three hikers atop chalk cliffs above turquoise ocean
- `varD.jpg` — L3, cool-mist, lone cyclist on path beside river inside a misty gorge (anchor for L3 vista)
