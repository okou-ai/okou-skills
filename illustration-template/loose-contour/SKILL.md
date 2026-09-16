---
name: loose-contour
description: Flat editorial spot illustration in a locked house style — confident open-contour ink drawings in dark teal-green over flat offset color blobs (printing-misregistration look), with one continuous looping ribbon line weaving through the scene, on warm cream paper. Tight 5-color palette (cream + teal + mustard + soft blue + coral). Trigger when the user says /loose-contour, asks for a "loose-contour illustration", "offset-blob editorial illustration", "cream paper ribbon-line scene", or briefs with a scene metaphor + accent lead + complexity level.
---

# /loose-contour — locked editorial spot illustration

Forge a square editorial spot illustration in the **loose-contour** house style: confident open-contour ink drawings in dark teal-green, over flat offset color blobs (printing-misregistration look), with one continuous looping ribbon line weaving through the scene, on warm cream paper.

Every invocation flexes the dials below against a locked frame. The frame never changes; the dials describe the per-piece scene.

## Locked frame (never change)

- **Canvas** — square aspect ratio (1024×1024 recommended).
- **Background** — warm cream paper `#f0ebdc`, fully flat, no texture, no edges.
- **Line treatment** — single-weight dark teal-green `#1e4d4a` contour line. Confident, hand-drawn, **deliberately broken at edges and joints** — the outline never fully closes around any shape. Reads as relaxed and breathing.
- **Color shapes** — 1–3 flat color blobs **without any outline**, sitting BENEATH the line drawing and **OFFSET from it** like printing misregistration. They spill outside the lines on one side and don't fill them on the other. Never traced to match the outline. This offset is the signature of the style — it is not a subtle accent, it is the whole point.
- **Ribbon line** — exactly ONE continuous, free-flowing looping ribbon of the same teal-green line weight passes through the composition. Reads as steam, a thought-trail, a path, a breeze, a writing-trail. Always present, always single.
- **Palette** — strictly from this 5-color set; no other colors:
  - Cream paper `#f0ebdc` (background only)
  - Dark teal-green ink `#1e4d4a` (all line work)
  - Mustard yellow `#e8a82c`
  - Soft sky blue `#a4c4d0`
  - Coral `#e35b3a`
- **Rendering** — fully flat vector. NO gradients, NO shadows, NO halftone, NO grain, NO 3D modeling, NO outlines on the color blobs.

## Dials (vary per piece)

| Dial | Options |
|---|---|
| **Scene metaphor** | The scene IS the metaphor. Pick theme-native props (coffee mug for morning ritual, laptop for focus, pen+paper for signing, plant for growth, envelope for receiving news, suitcase for travel). Never relabel a generic template. |
| **Cast** | Single hand / two hands / person + object / person mid-action / object-only. Vary across a series; do NOT lock a recurring character. |
| **Complexity** | **L1** — single subject + 1 offset blob + ribbon. Minimal. <br>**L2** — subject + ribbon + 2 offset blobs + 1 small accent shape. <br>**L3** — full vignette: subject + supporting props + 3 offset blobs (using all 3 accent hues) + meandering ribbon. |
| **Accent lead** | `mustard` / `soft-blue` / `coral` / `balanced` (all three). The lead hue claims the largest blob. |
| **Ribbon path** | Where it enters, what it traces, where it exits. Typical motifs: steam-from-cup, trail-from-pen, thought-from-screen, breeze-behind-figure, path-underfoot, line-from-envelope. |

## Prompt template

```
Flat editorial vector illustration on a square 1024x1024 canvas with warm cream background (#f0ebdc).

Subject: {SCENE}.

Drawn as OPEN, BREATHING contour lines in dark teal-green ink (#1e4d4a) — confident hand-drawn outlines, deliberately broken at edges and joints, never fully closed.

Underneath the line art sit {N} flat color shape(s) WITHOUT any outline — deliberately OFFSET from the line drawing like printing misregistration, spilling outside the lines on one side. Lead color: {LEAD_HEX}. {SECONDARY_ACCENTS_IF_ANY}.

ONE continuous looping ribbon line of the same dark teal-green flows freely through the composition as {RIBBON_MOTIF}.

Tight palette: cream + dark teal + {ACCENT_NAMES}. Flat vector, NO gradients, NO shadows, NO texture. Editorial spot illustration style.
```

## How to interpret a brief

The user will usually give a short scene seed (e.g. "morning coffee", "signing the lease", "thinking about a problem"). Expand it into the locked frame:

1. **Pick the cast.** Hand-only is most intimate; person + object is most readable; object-only is most editorial.
2. **Choose accent lead.** Mustard reads warm/optimistic; soft blue reads calm/focused; coral reads urgent/expressive; balanced reads as a full vignette.
3. **Choose complexity.** Default to L2 unless the brief is explicitly minimal (L1) or scenic (L3).
4. **Design the ribbon path.** What does it represent in this scene? Steam? A thought? A writing-trail? A breeze? Make sure it has a believable entry and exit, not a random scribble in dead space.
5. **Place the blobs intentionally.** Each blob belongs behind a meaningful shape (a torso, a cup, a leaf cluster) — never floating in empty space. The offset direction should look like one consistent printing-press misalignment across all blobs.

## Example briefs

**Brief 1 — L1 / mustard / single hand**
> Scene: a hand from below holding a steaming coffee mug. Ribbon: stylized steam looping upward and around the cup. Lead color: mustard, one blob spilling out from behind the cup.

**Brief 2 — L2 / soft-blue / person + device**
> Scene: a person leaning forward into a laptop, focused. Ribbon: thought-trail flowing upward from the laptop screen. Lead color: soft blue (one blob behind torso, one behind laptop). Small mustard rectangle accent on the screen.

**Brief 3 — L2 / coral / two hands**
> Scene: two hands meeting mid-signature — one holding a fountain pen, the other steadying a piece of paper. Ribbon: trail of writing emerging from the pen tip. Lead color: coral, two blobs spilling around the paper. Small soft-blue accent at one cuff.

**Brief 4 — L3 / balanced / vignette**
> Scene: a person walking forward carrying a large potted houseplant, leaves spilling overhead. Ribbon: meanders behind the figure like a breeze. Use all three accent hues — soft blue behind the shirt, mustard behind the pot, coral as a single leaf-shape inside the foliage.

## Anti-patterns

- ❌ Closed/clean outlines that meet themselves — the line must stay broken and breathing.
- ❌ Color blobs traced to match the outline — they must be offset like misregistration.
- ❌ Multiple ribbon lines — there is exactly one per piece.
- ❌ Any color outside the locked 5-color palette.
- ❌ Gradients, shadows, halftone, grain, 3D modeling — all forbidden.
- ❌ Outlines on the color blobs themselves.
- ❌ Locking a recurring character across pieces — cast is a per-scene dial.
- ❌ Filling the cream background with texture, edges, or vignette.

## Output evaluation checklist

Before delivering, confirm:

- [ ] Background is the exact warm cream (`#f0ebdc`), flat, no texture.
- [ ] Line color is the exact dark teal-green (`#1e4d4a`); no other line color appears.
- [ ] At least 3 visible breaks in the outline (joints, sleeves, table edges, cup rims).
- [ ] Every color blob is OUTLINE-FREE and visibly OFFSET from the line art.
- [ ] Exactly one ribbon line is present.
- [ ] Only colors from the locked 5-color palette appear in the image.
- [ ] No gradients, shadows, halftone, or 3D shading anywhere.

## Model notes

This style was trained on `gpt-image-1.5` at high quality, 1024×1024. Other capable editorial-illustration models (e.g. `nano-banana-2`) can reproduce it if the prompt template above is followed verbatim. The "deliberately broken outline" + "offset color blob" + "single ribbon line" instructions are load-bearing — paraphrasing them tends to soften the style toward generic flat editorial.

## Reference pieces

The four anchor variations (in this directory):

- `ref-l1-mustard-hand.png` — L1, mustard, single hand holding coffee mug
- `ref-l2-coral-twohands.png` — L2, coral, two hands signing
- `ref-l2-blue-laptop.png` — L2, soft blue, person at laptop
- `ref-l3-balanced-vignette.png` — L3, balanced palette, person carrying houseplant
- `ref-l2-coral-envelope.png` — L2, coral, hand opening envelope (smoke-test piece)
