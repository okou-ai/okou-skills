---
name: grainy-duotone
description: Hand-drawn editorial spot illustration — grainy charcoal-stippled black-ink figures on a warm cream background, paired with free-floating two-tone color blocks (no outlines) filled with internal patterns and surrounded by small scattered ambient marks. Trigger when the user says /grainy-duotone, asks for a "grainy two-tone editorial illustration", "charcoal-stippled hand illustration", "duotone editorial spot", or briefs with a scene metaphor + two-color palette + complexity.
---

# /grainy-duotone — locked grainy two-tone editorial style

This style produces small editorial spot illustrations in a warm hand-drawn idiom: grainy charcoal-stippled black-ink figures (almost always a hand or pair of hands) interacting with free-floating flat color blocks, set on a warm cream background and dotted with scattered ambient marks. The base is locked; each invocation spins five creative dials.

## Prompt interpretation

The user will usually give a short brief — sometimes a scene phrase ("hand raising a flag"), sometimes a metaphor + palette ("celebrating a launch, teal + yellow"), sometimes the full row of dials. Translate the brief into a complete scene without stopping to ask:

1. **Pick a scene metaphor.** Identify the verb the illustration is about (launch, grow, connect, discover, communicate, reflect, navigate, care, transform, build). If the user only gave a feeling, choose the most evocative everyday gesture that conveys it.
2. **Pick a two-color palette.** Two flat hues only. Lean cool for calm / reflective scenes, warm for celebratory / driven scenes.
3. **Pick a complexity level (L1 / L2 / L3).** L1 for a single quiet gesture, L2 for a balanced 1–2 prop scene, L3 for a layered editorial-collage piece.
4. **Pick the mood.** The mood should flow from posture + palette + density together; do not contradict it with a clashing color or busy density.
5. **Honor the locked frame** — cream background, grainy charcoal hands, outline-free color blocks, patterns layered on top, scattered ambient marks. Those never move.

Bias toward gestural compositions where a hand or pair of hands is the focal point and color blocks support the gesture (cuff, prop, surround). Avoid full bodies, faces, and crowded narrative scenes — this style is editorial spot illustration, not full scene illustration.

## Locked style axes (NEVER vary)

### Background
- **Warm cream off-white** — `#F5F1EA` or close — fills the canvas edge to edge
- **No vignette, no edge shading, no gradient, no paper texture, no border, no frame**
- The cream is unbroken negative space around the scene

### Figures (hands, arms, faces, any organic body part)
- Drawn in **grainy stippled charcoal-texture black ink** — rough sketchy fill that reads as pencil/charcoal grain, not smooth flat black
- Tone variation lives inside the grain — lighter stipple for highlights, denser for shadows
- Contour lines are confident hand-drawn black ink, slight wobble allowed
- Never smooth vector fills, never crosshatched engraving, never airbrush
- Hands are the typical subject — palms, fists, grips, cupped shapes. Faces and full figures are rare.

### Color blocks (the two-tone shapes)
- **Two flat hues per piece** plus black ink — no third color, no gradient, no shading
- **Zero black outlines on color shapes** — the shapes are free-floating, painted-first, with rough hand-painted edges (see `feedback-blue-blocks-no-border` rule from the broader spec)
- Ink lines may sit *on top* of a color block but must never trace its perimeter
- Color blocks are typically cuffs/sleeves under the hand, props the hand interacts with, or supporting silhouettes behind the gesture
- Color blocks are often a slightly irregular blob rather than a geometrically precise shape

### Internal patterns (the texture inside color blocks)
- Every color block carries a pattern layered **on top** of its flat fill, drawn in black ink
- Pattern vocabulary: **grid · dots · spiral · diagonal hatching · cross-hatching · wavy parallel lines · squiggles · concentric circles · tiled triangles · plus-signs · halftone dots**
- One block typically carries one pattern; if two blocks coexist, give them different patterns (e.g. spiral vs. grid)
- Patterns are loose and slightly imperfect — not a CAD grid

### Ambient marks (the scattered confetti)
- A handful of small black-ink marks float in the cream space around the scene
- Mark vocabulary: **small zigzag · tiny triangle · x mark · small circle · short straight line · plus sign · dot · curly squiggle · dashes · chevron**
- Counts: L1 ≈ 2–3 marks, L2 ≈ 5–7 marks, L3 ≈ 10–12 marks
- Marks are scattered, never aligned to a grid, never forming a recognizable pattern of their own

### Composition
- Square 1:1, centered, with breathing room around the focal gesture
- One clear focal point (the hand or pair of hands) — never two competing subjects
- No text, no logos, no captions, no headlines, no borders

## Variable axes (the five dials)

These are the only things that should change between pieces.

| # | Axis | What it controls | Example values |
|---|---|---|---|
| 1 | **Palette** | Emotional temperature of the piece | teal + butter yellow · coral + sage · lavender + mustard · navy + peach · burgundy + dusty pink · plum + champagne · forest + cream-yellow · cobalt + warm gray · brick + olive · cerulean + ochre |
| 2 | **Elements** | The literal nouns drawn in the scene | hand(s); plus one or two of: flag · balloon · clock · sprout · megaphone · book · envelope · key · lightbulb · compass · ladder · telescope · magnifier · kite · candle · mug · bell · ribbon · gift box · sailboat · arrow |
| 3 | **Scene** | The verb / metaphor that ties the elements together | Launch · Grow · Connect · Discover · Communicate · Reflect · Navigate · Care · Transform · Build |
| 4 | **Complexity** | Density and breathing room | L1 minimal (1 hand + 1 prop + 1 color block + 2–3 ambient marks) · L2 balanced (1–2 hands + 1–2 props + 2 color blocks + 5–7 ambient marks) · L3 rich (full gesture + 3–4 props + 3+ color blocks layered + 10+ ambient marks + multiple pattern types) |
| 5 | **Mood** | The emotional register | Celebratory · Calm/tender · Curious/playful · Reflective · Determined/driven · Warm/connected · Quiet/archival |

## Brief template

```
Palette:    {two colors}
Elements:   {hand(s) + 1-3 props}
Scene:      {Launch | Grow | Connect | Discover | Communicate | Reflect | Navigate | Care | Transform | Build} — {one-line metaphor}
Complexity: {L1 minimal | L2 balanced | L3 rich}
Mood:       {Celebratory | Calm | Curious | Reflective | Determined | Warm | Quiet}
```

## Generation guidance

This style was tuned with a multimodal image-edit model that accepts both a written prompt and a reference image set. Pass the seven reference PNGs in this folder as the style anchor — the prompt alone is not sufficient to keep the grain texture, outline-free color rule, and ambient-mark vocabulary aligned.

**Model-specific note (`fal-ai/nano-banana/edit`, the model the style was tuned on):**
- Always restate every locked-style rule in the prompt. The model does not retain locked rules across calls.
- Especially restate: (a) outline-free color blocks (b) cream background with no vignette (c) grainy stippled fill on the hand, not smooth black (d) two colors only, no third hue.
- Never write "match the reference grid" — the model interprets that as a multi-cell layout request. Write "match the reference style".
- For the ladder / climb scene archetype, explicitly state that the ladder is rendered in plain black ink lines, NOT colored — otherwise the model colors the ladder.

If you are running a different multimodal edit model, keep the same semantic instructions: rules first, then scene, then references. Square 1:1 output.

## Reference images (locked anchors)

These seven PNGs are the style anchors and should be passed as image references on every generation. They are NOT user-supplied source material — they are codified outputs from the framework's tuning round.

| File | Dials |
|---|---|
| `ref-launch-pennant-1.png` | teal + yellow · hand + pennant · Launch · L2 · celebratory |
| `ref-launch-pennant-2.png` | teal + yellow · hand + pennant + blob · Launch · L2 · celebratory |
| `ref-launch-pennant-3.png` | teal + yellow · hand + pennant + blob · Launch · L2 · celebratory |
| `ref-sprout-sage-coral-l1.png` | sage + coral · open palm + sprout · Grow · L1 · tender |
| `ref-magnifier-lavender-mustard-l2.png` | lavender + mustard · hand + magnifier · Discover · L2 · curious |
| `ref-balloons-navy-peach-l3.png` | navy + peach · two hands + balloons + ribbon · Launch · L3 · celebratory |
| `ref-ladder-burgundy-pink-l2.png` | burgundy + dusty pink · hand + ladder + peak · Navigate · L2 · determined |

## Evaluation checklist

After generation, the piece should pass:

- [ ] Background is warm cream — no white edge halo, no gradient.
- [ ] Hand(s) and any skin are grainy charcoal stipple — not smooth flat black.
- [ ] Color blocks have **zero** black outlines tracing their perimeter.
- [ ] At least one pattern (grid / dots / spiral / hatching / squiggles / wavy lines) sits inside each color block.
- [ ] Exactly two color hues + black are present — no third color.
- [ ] Ambient marks count matches the complexity level.
- [ ] One clear focal gesture — no competing subjects.
- [ ] No text, no logo, no border.

If any item fails, regenerate with the failed rule restated more emphatically in the prompt.
