---
name: folk-storybook
description: "Folk-art children's picture-book illustration style — hand-painted gouache/watercolor scene on aged paper, anthropomorphic animal characters with closed-crescent-eye smiles, dusty muted folk palette, decorative pattern surfaces (wallpaper, rugs, textiles), and a hushed lullaby mood. Trigger when users ask for a folk-art illustration, storybook scene, cozy animal illustration, or any new piece in this Eastern European picture-book style."
---

# Folk Storybook Illustration

Use this register-only image style when the user asks for a folk-art children's picture-book illustration, a cozy storybook scene, an anthropomorphic animal vignette in a folk-art palette, or any new piece in this hand-painted Eastern European picture-book style.

This style is distinct from Notion Illustration (which is line-only ink) and vm0 Illustration (which is line-art product spot). Folk Storybook is a fully-painted scene with patterned surfaces, soft characters, and lived-in interior or outdoor mood.

Bundled reference imagery — three canonical outputs that demonstrate the framework in action:

- `ref-reading-nook.jpg` — Charcoal tabby cat curled in a dusty-slate-blue armchair reading a tiny book, sage-green lamp, cream star pillow, dusty-blue wallpaper with cream florets. Establishes the **default cool-folk palette** (dusty blue dominant, oatmeal cream + muted sage support, tiny warm accents only) and the cozy-interior L2 archetype.
- `ref-puzzle.jpg` — Long-haired calico cat (cream + caramel + charcoal patches) belly-down on a folk-pattern rug working on a jigsaw puzzle. Demonstrates **cast rotation** — a completely different character from the reading-nook scene, no scarf, looser posture. Same palette discipline; different wallpaper motif (cream berry-and-leaf sprigs).
- `ref-chill-tussle.jpg` — Tuxedo cat + scruffy brown terrier mid-tumble, paws raised, tail puffed, fur tufts drifting, knocked-over star pillow, unspooled yarn. Demonstrates the **chill-face rule under action**: both characters keep closed crescent eyes + soft smiles even while wrestling. All energy lives in the body posture and scene props, never in the face.

## Locked Style Fundamentals (never vary)

| Axis | Spec |
|---|---|
| **Medium** | Hand-painted gouache + watercolor on aged paper |
| **Texture** | Visible brushwork and paper grain across every surface |
| **Linework** | Soft hand-drawn outlines, no harsh black ink, no vector cleanness |
| **Shape language** | Flat painterly fills with subtle hand-painted shading; slightly naive composition |
| **Character face** | Closed crescent eyes + small soft content smile on every character, every scene |
| **Sensibility** | Eastern European folk picture-book; hushed, lullaby-like, slightly dreamy |

### The chill-face rule (critical)

The closed-crescent-eye smile applies to **every** scene, **including action beats** (tussles, chases, splashes, dances). Do not relax it. Express the action entirely through:

- Body posture — paws raised, tail puffed, ears tilted, mid-tumble silhouettes
- Scene props — knocked-over pillows, fur tufts drifting, unspooled yarn, scattered toys
- Composition — motion implied by overlap and lean, not by facial alarm

Allowed face variants: closed eyes / one slightly cracked open / soft half-lidded sleepy look. Forbidden: wide-open alert eyes, open shouting mouths, visible teeth, frenzy. If the brief is an action moment, explicitly restate "closed crescent eyes, soft content smile" in the model prompt — without that restatement, the model will default to opening eyes for excitement.

## Variable Axes (brief dials)

Every invocation declares values for these eight axes. The locked fundamentals above stay fixed regardless.

### 1. Palette — temperature × saturation

- **Temperature**: cool-leaning ↔ neutral ↔ warm-leaning
- **Saturation**: faded pastel ↔ muted lived-in ↔ moderately saturated folk
- **House default (cool folk)**: dusty slate blue + oatmeal cream + muted sage, with warm tones (caramel, mustard, rust) as small accents only — never as dominant surfaces
- **Alternates**: warm folk (terracotta + cream + mustard + honey); soft pastel (blush + powder blue + butter)
- **Distribution rule**: declare dominant (~60%) / secondary (~30%) / accent (~10%). If output drifts too warm, demote warm tones from wallpaper/chair surfaces to small props only.

### 2. Scene archetype
- Cozy interior — bedroom, reading nook, kitchen, playroom, bath
- Outdoor folk — picnic, garden, meadow, orchard
- Seasonal — autumn harvest, winter hearth, spring bloom

### 3. Character cast (rotate per scene)
- Species: cat, fox, bear, mouse, owl, rabbit, dog, hedgehog
- Coat (cats as example): charcoal tabby, ginger, cream buff, black, calico, tuxedo, grey silver, long-haired, siamese
- Anthropomorphism level: bare animal / small accessory (scarf, bow) / full clothing (dress, vest)
- Count: solo / pair / group of 3+
- **Rule**: rotate cast per scene. Never reuse the same character across a series unless the user explicitly asks for mascot continuity. The series gets its charm from a varied cast, not one character relabeled into different rooms.

### 4. Activity
Reading, sleeping, baking, picnicking, gardening, gazing out a window, sharing a meal, playful tussle, splashing in a puddle, decorating, etc.

### 5. Complexity (prop density)
- **L1** — character + 1-2 props (single chair, window)
- **L2** — character + 3-5 props building a room (chair, lamp, plant, side table, picture)
- **L3** — full storybook scene with patterned wallpaper, multiple textiles, framed pieces, decorative borders

### 6. Pattern density
- Surfaces eligible for pattern: wallpaper, quilt, cushion, rug, lampshade, clothing
- Motif vocabulary: small repeating florets, stars, herringbone, stripes, folk leaves, tulips, berries, sprigs
- Density: sparse (one surface) / moderate (two surfaces) / dense (everywhere)
- **Variation rule**: pick a different motif per scene when building a series, to avoid wallpaper fatigue.

### 7. Mood / time of day
Hushed evening (warm lamp, dark window with crescent moon) / bright morning / quiet afternoon / dreamy nighttime.

### 8. Format
- Square spot (1024×1024) — default
- Landscape spread
- Portrait cover

## Prompt template

Once the locked fundamentals are honored, an invocation is one line per axis. Have the model render this brief into a full painted scene.

```
Palette:    cool-leaning, muted, dusty blue + cream + sage
Scene:      cozy interior — reading nook
Cast:       charcoal tabby cat, solo, cream scarf
Activity:   curled up reading a tiny book
Complexity: L2 (chair + lamp + side table + plant + framed picture)
Pattern:    dusty-blue wallpaper with cream/sage florets; cream pillow with stars
Mood:       hushed evening
Format:     1024×1024 square
```

When constructing the model prompt, weave the locked fundamentals back in explicitly. A good prompt opens with:

> "A cozy folk-art children's storybook illustration of [activity and cast]. CRITICAL FACE RULE: every character has closed crescent eyes and a small soft content smile — chill, serene, almost sleepy expressions. No open eyes, no teeth, no frenzy. Action lives in posture and props, never in the face."

…then describes the cast, the scene, the palette distribution (dominant / secondary / accent), the wallpaper motif, and finally:

> "Hand-painted gouache and watercolor texture with soft visible brushwork, flat shapes with subtle painterly shading, slightly naive and charming, like a vintage Eastern European picture book on aged paper. Soft hand-drawn outlines, no harsh black lines, gentle paper-grain texture throughout. Mood: [mood description]."

## Worked example — puzzle scene (cool folk palette, calico cat)

```
A cozy folk-art children's storybook illustration of a soft cream-and-
caramel long-haired calico cat lying belly-down on a folk-patterned rug,
intently working on a jigsaw puzzle.

CRITICAL FACE RULE: closed crescent eyes, soft content smile, ears tilted
forward in lazy concentration. No open eyes, no teeth.

The cat has a cream base with caramel-orange and dusty-charcoal patches,
white chest and paws, fluffy long fur. One paw nudging a puzzle piece.

The puzzle is partially assembled showing a half-finished image of a
sunny meadow with a haystack. Loose puzzle pieces scattered on the rug.
A small wooden toy block in the corner. A pot of sage-green leaves on a
side table.

PALETTE — cool-leaning earthy folk palette. Dusty slate blue and oatmeal
cream lead; muted sage green supports; warm caramel and faded rust appear
only on the cat's patches and small rug accents.

The wallpaper is dusty blue with small repeating cream berry-and-leaf
sprigs. The rug is a folk pattern with cream, sage, and dusty rust bands.

Hand-painted gouache and watercolor texture with soft visible brushwork,
flat shapes with subtle painterly shading, slightly naive and charming,
like a vintage Eastern European picture book on aged paper.

Mood: quiet afternoon, gently absorbed, lazy.
```

## Model guidance

This style is designed for narrative compositions with multiple props, characters, and patterned surfaces — the kind of scene a strong text-to-image model can compose in one pass from a detailed prompt. Recommended pairing: `gpt-image-2` at `high` quality, square 1024×1024, with prompt enhancement disabled so the locked-fundamentals language reaches the model verbatim.

The bundled reference images (`ref-reading-nook.jpg`, `ref-puzzle.jpg`, `ref-chill-tussle.jpg`) are canonical outputs of this framework — provided for *human* style study and prompt authoring. They are not required as image inputs at generation time — the style transfers entirely through the detailed prompt language. If output drifts (paper grain too clean, palette too saturated, brushwork too smooth, faces too alert), tighten the prompt by re-emphasizing "gouache + watercolor on aged paper, visible paper grain, soft hand-drawn outlines, no harsh black lines" and (for action scenes) restate the chill-face rule — rather than reaching for image-to-image.

## Quality checklist

Before delivering, verify:

- [ ] Closed crescent eyes on every character (even mid-action)
- [ ] Soft content smile, no open mouth or teeth
- [ ] Dominant palette correct (cool dusty-blue + cream + sage by default)
- [ ] Warm tones contained to small accents, not dominant surfaces
- [ ] Visible gouache brushwork and paper grain
- [ ] At least one patterned surface (wallpaper / rug / textile)
- [ ] Wallpaper motif different from the previous scene if part of a series
- [ ] Cast genuinely new from prior scenes (different species, coat, or accessories)

If any check fails, regenerate with the corresponding constraint re-emphasized in the prompt.
