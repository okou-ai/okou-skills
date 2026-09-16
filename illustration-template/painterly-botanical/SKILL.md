---
name: painterly-botanical
description: Painterly watercolor + gouache portrait illustration with a single figure embraced by lush botanicals. Closed-eye introspective subject, loose translucent washes with visible bleeds, sparse crisp ink line accents, and a softly tinted paper-wash background (never pure white). Use when a brief describes a contemplative figure with foliage, a "watercolor portrait", a "botanical embrace" composition, or asks for a piece in this painterly editorial style.
---

# /painterly-botanical — locked painterly botanical portrait style

This skill produces a single watercolor + gouache portrait of one figure embraced by botanicals (leaves, blossoms, grasses). The mood is always introspective and gentle. Every invocation locks the medium, line treatment, light, and signature; the user composes the scene by filling in eight orthogonal axes.

## Prompt interpretation

The user supplies a brief that picks from each axis (subject, hair, pose, botanicals, palette, background, complexity, format). If any axis is missing, infer a sensible default that fits the other choices — never refuse and never re-ask the user. Translate the brief into a single rich paragraph that names every locked invariant (medium, line treatment, eye state, background tint, signature) plus the chosen axis values. Then generate one image.

Bias toward concrete sensory detail: which leaf is the dominant hero shape, where pigment pools at petal edges, where one crisp ink line sits on a leaf vein.

## Locked style invariants (NEVER vary)

### Medium
- Digital watercolor mixed with gouache
- Translucent washes with visible pigment bleeds
- Pigment pools at the edges of shapes — leaf tips, petal margins, hair tips
- Subtle paper grain across the whole canvas
- NOT vector, NOT flat-fill, NOT 3D-rendered, NOT anime-cel

### Linework
- Sparse, crisp dark ink accents on key edges only — leaf veins, lash line, hair contour, petal stamens
- Never full outlines around figure or foliage
- Lines breathe — pressure variation, organic taper
- A handful of accents per piece, not a network

### Eyes & expression
- Eyes are always gently closed or near-closed — no direct gaze, never open
- Soft contemplative expression: peaceful, dreamy, slightly melancholic, never smiling broadly
- Optional dusty rose on the cheek

### Light
- Soft and diffused — no hard shadows, no rim light, no chiaroscuro
- Figure and foliage share the same overall wash; they belong to one painting, not pasted layers

### Signature
- A tiny handwritten cursive signature in pale gray-ink in one upper corner
- Low contrast, barely legible — part of the paper's atmosphere, not a logo

### Background
- ALWAYS a tinted color wash filling the entire canvas
- NEVER pure white, NEVER pure black, NEVER a flat solid block
- The tint is one of the palette swatches (axis 6), painted as if the figure was rendered on that paper

### Mood
- Introspective, gentle, dreamy
- Editorial register — like the inside cover of a literary magazine, not a children's book and not commercial art

## User-controllable axes

### Axis 1 — Subject
Who the figure is. Pick one:
- young man
- young woman
- child
- androgynous youth
- elder
- figure from behind (only the back of the head and shoulders visible)

### Axis 2 — Hair
Pick one:
- short tousled crop
- dark bob
- long flowing
- braided (single braid over shoulder)
- wisps over face
- wet hair / just-bathed
- shaved / very short

### Axis 3 — Pose & framing
Pick one:
- side profile (subject faces left or right)
- three-quarter view
- front bust (head and shoulders, facing viewer)
- curled up hugging knees
- head resting on arm, leaning into the leaves
- looking down at hands
- head tilted to leaves (subject's cheek touches a leaf)

### Axis 4 — Botanical companion
Pick one:
- monstera + palm fronds (jungle)
- lily + magnolia (floral)
- wisteria + cherry blossom (delicate)
- ferns + moss (forest floor)
- wildflowers + grass (meadow)
- sunflower + wheat (warm field)
- roses + ivy (garden)
- lotus + reeds (water)

### Axis 5 — Palette
Pick one:
- cool greens + peach skin (sage, emerald, seafoam + warm peach) — the classic
- warm peach + coral + teal
- emerald + ivory + gold
- dusty lavender + sage + cream
- burnt sienna + olive + bone
- slate blue + blush + pearl
- mustard + forest + clay

### Axis 6 — Background wash (always tinted)
Pick one. The tint should harmonize with the palette but read as paper, not as scene:
- cream paper
- pale sage
- dusty blue
- blush pink
- warm sand
- soft lavender
- faded sepia
- mint wash

### Axis 7 — Complexity
Pick one density level:
- L1 minimal — figure + 2-3 hero leaves, generous negative space, sparse signature accents only
- L2 balanced — figure embraced by a full bouquet of foliage, foliage covers ~40-60% of canvas
- L3 dense — figure half-hidden in a lush botanical wall, foliage fills nearly all of the canvas, only the face and one shoulder clearly visible

### Axis 8 — Format
Pick one aspect ratio. The reference set is portrait tall — other ratios still work but adjust the foliage flow:
- portrait tall (e.g. 1024×1536) — recommended default
- portrait square (e.g. 1024×1024) — tighter bust framing
- landscape wide (e.g. 1536×1024) — figure offset to one side, foliage filling the rest

## Brief template

```
Subject:      <axis 1>
Hair:         <axis 2>
Pose:         <axis 3>
Botanicals:   <axis 4>
Palette:      <axis 5>
Background:   <axis 6>
Complexity:   <axis 7>
Format:       <axis 8>
```

## How to render

Generate this style with a high-quality image model that handles watercolor and gouache realism well. The reference set was produced with OpenAI's `gpt-image-2` at portrait 1024×1536, high quality — that combination is the current recommendation. Other strong painterly models (Flux Pro, Seedream 5, Qwen Image) will also produce acceptable results; lower-fidelity models tend to lose the translucent-wash quality and the crisp ink accent restraint.

Translate the filled-in brief into a single dense paragraph that names:
1. The medium and rendering style ("soft painterly watercolor and gouache digital illustration")
2. The subject and hair (axes 1–2)
3. The pose, framing, and the closed-eye expression (axis 3 + locked rule)
4. The botanical companion and how it embraces the figure (axis 4)
5. The palette with explicit color names (axis 5)
6. The brushwork — loose strokes, translucent washes, pigment bleeds, sparse crisp ink accents on specific edges (locked rule)
7. A CRITICAL line specifying the background as a tinted wash (axis 6), not pure white
8. The tiny pale handwritten signature in an upper corner (locked rule)
9. The complexity level (axis 7) and format orientation (axis 8)
10. The introspective editorial mood (locked rule)

## Anti-patterns (rejects)

- Pure white background — always tint it
- Open-eye gaze — always closed or near-closed
- Full ink outline around figure or leaves — only sparse vein and contour accents
- Hard cast shadows — light is always diffused
- Anime / chibi proportions — subjects should read as editorial illustration, not character art
- Smiling teeth-showing expression — softness only
- Flat solid color background — must read as painted paper, with grain
- A "scene with a figure in it" composition — the figure and the botanicals are the entire piece, no environmental context (no buildings, no rooms, no sky)

## Reference set

Eight rendered references demonstrate the full axis space. Each filename tags the dominant axis values it exercises:

| File | Subject | Botanicals | Palette | Background | Complexity |
|------|---------|------------|---------|------------|------------|
| `ref-young-man-monstera.png` | young man, side profile | monstera + palm | cool greens + peach | cream paper | L2 |
| `ref-curled-up-peach-coral.png` | young woman, hugging knees | monstera + lily | warm peach + coral + teal | cream paper | L3 |
| `ref-magnolia-emerald-ivory.png` | young woman, three-quarter | lily + magnolia | emerald + ivory + gold | cream paper | L2 |
| `ref-wisteria-lavender.png` | young woman, head resting on arm | wisteria + cherry blossom | dusty lavender + sage + cream | soft lavender | L2 |
| `ref-sunflower-sand.png` | young man, looking down at hands | sunflower + wheat | burnt sienna + olive + bone | warm sand | L2 |
| `ref-lotus-dusty-blue.png` | androgynous youth, three-quarter | lotus + reeds | slate blue + blush + pearl | dusty blue | L3 |
| `ref-child-wildflower-sage.png` | child, front bust | wildflowers + grass | emerald + ivory + gold | pale sage | L1 |
| `ref-from-behind-sepia.png` | figure from behind, long hair | ferns + moss | mustard + forest + clay | faded sepia | L2 |

Use the references as ground-truth examples of the locked invariants — translucent wash quality, pigment edge pooling, sparse ink accents, tinted paper backgrounds, closed-eye introspection, single-figure embrace composition.

## Output evaluation checklist

Before delivering an image, verify:

- [ ] Background is tinted, not pure white
- [ ] Eyes are closed or near-closed
- [ ] At least three visible watercolor bleed edges or pigment pools
- [ ] Ink line accents are sparse and only on key edges
- [ ] Figure and foliage are the entire composition (no buildings, rooms, or sky)
- [ ] Tiny handwritten signature in an upper corner
- [ ] Palette matches axis 5; background matches axis 6
- [ ] Complexity matches axis 7 (L1 sparse, L2 balanced, L3 dense)
