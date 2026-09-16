---
name: chinese-ink-art
description: A Chinese ink-wash (shuimo) video style — monochrome ink gradients, generous white space, visible brushstroke texture, mist-and-mountain composition, and a calm classical-poetry mood. Applies to whatever subject the user brings. Trigger on /chinese-ink-art, "Chinese ink painting", "shuimo", "ink wash animation", or "Eastern zen ink style".
---

# Chinese Ink Painting

A **Chinese ink-wash (shuimo) style**, not a fixed scene. Keep the user's subject exactly as briefed — a mountain, a crane, a figure, an object — and render it as flowing ink on paper in the look below. The style supplies the *look*; the user supplies the *what*. Tuned for **Seedance** (the platform's default video model): the prompt follows Seedance's `subject → scene → motion → camera → light → style` ordering.

## Video preview

1. Before generating a video, prepare a few keyframes matching the user's subject, style, and aspect ratio. Reuse suitable supplied or already approved images.
2. Show the actual images through accessible links, briefly describe the intended motion, and ask the user to confirm. End the turn and wait; do not start a video job before confirmation. Revise the preview if requested.
3. After confirmation, generate the video. Use the approved images as first/last frames or references when supported by the selected model; otherwise follow the approved visual direction in the prompt. Reuse existing confirmation for an unchanged preview.

Keep the preview message short: the images, a brief motion description, and one confirmation question.

## What this style is

**The essence:** **stillness and emptiness as beauty** — a few confident ink strokes floating in vast white space, evoking a classical Chinese poem. The goal is **calm, breath, and negative space**: what's left unpainted matters as much as the ink.

**Touchstones:** classical Chinese shuimo painting (Qi Baishi, Xu Beihong), *Shanshui* landscapes, the ink-animation of *Where Is Mama / Feeling from Mountain and Water* (Shanghai Animation Film Studio).

**What makes it distinct:** **monochrome ink + negative space + brushstroke**. Not color photography, not photoreal, not Western painting — black ink gradients on bright paper, mist, and generous emptiness, with at most a single tiny spot of color (e.g. a red seal or lantern).

## Style dimensions (locked)

- **Visual tone — cold / monochrome**: black ink gradients on bright off-white paper; desaturated; at most one tiny accent of color.
- **Camera — slow push-in**: a slow, gentle drift or push; meditative, weightless.
- **Editing pace — slow & meditative**: long, breathing shots; no cutting.
- **Narrative mode — abstract / mood**: poetic suggestion, not narrative.
- **Production type**: rendered as **ink-wash painting** (painterly, not photoreal). Mist and ink may animate softly.
- **Emotional tone — calm & meditative**: serene, contemplative, zen.
- **Style reference — Chinese ink wash (shuimo)**: brushstroke elegance, mist, and classical negative space.

## Prompt construction

Write **one cohesive video prompt in your own words**, adapted to the subject. Hit these beats in Seedance order:

`subject (as briefed) → misty ink-wash setting with vast white space → gentle motion (drifting mist, flowing ink, ripples) → slow push-in → soft diffuse light → monochrome ink-wash brushstroke style`

**Always convey:** Chinese ink-wash painting · monochrome black-ink gradients on bright paper · generous white negative space · visible brushstroke texture · mist / classical-poetry mood · calm slow motion · (optional) one tiny red-seal accent.

**Never:** color photography, photorealism, Western oil-painting look, busy/cluttered composition, saturated color, harsh light.

Adapt the subject and what little surrounds it; keep the emptiness. Put aspect ratio, negatives, and seed in the **params**.

## Generation parameters

- **aspectRatio**: `16:9` (handscroll-like) or `21:9` for a wide scroll feel.
- **resolution & model tier**: pick a tier that supports the resolution — fast tiers cap lower (often `720p`); `1080p` needs a full tier.
- **duration**: `5–8s`; let mist drift and ink bleed slowly.
- **negativePrompt**: `color photography, photorealistic, Western oil painting, saturated colors, cluttered composition, harsh lighting, 3D render, low resolution`.
- **generateAudio**: optional — soft guqin / water ambience suits it; often added in edit.
- **seed**: mild lever for text-to-video; for look consistency use `firstFrameImageUrl`.
- **firstFrameImageUrl**: use the approved opening frame when the selected model supports this input.

## How to apply

Render the user's subject as ink on paper with lots of empty space and mist. Keep monochrome (one tiny color accent at most). If the brief needs realistic color or a busy scene, this isn't the fit.

## Worked examples

Same ink-wash look; the subject changes.

1. **"misty mountains"** → layered ink peaks fading into mist, a tiny boat and a single red lantern, vast white space, slow drift (the picker thumbnail).
2. **"a crane by the water"** → a single ink crane among brushed reeds, mist, one small red seal stamp as the only color (see reference still).
3. **"a lone pine on a cliff"** → a wind-bent ink pine, empty paper sky, soft mist, slow push-in.
4. **"koi in a pond"** → a few ink koi and ripples in vast white water, minimal, meditative.

## Reference output

| Field | Value |
| --- | --- |
| Picker thumbnail | `https://cdn.vm0.io/artifacts/user_3EWY21Oe3f15kfs3yYmbGgDb3NV/35a45e0a-095f-476c-9586-840b3e591947/thumbnail-chinese-ink-art.jpg` |
| Reference still — ink crane (Seedream, seed 54) | `https://cdn.vm0.io/artifacts/user_3EWY21Oe3f15kfs3yYmbGgDb3NV/a8c55beb-59ac-4362-8abc-83a669d88ebb/image-a8c55beb.png` |
| Canonical | monochrome ink · vast white space · brushstroke · mist · one tiny red accent · slow drift |

> The reference still holds the ink-wash look on a different subject (crane vs. mountains/boat) — the style is subject-invariant. Use an approved frame of the user's subject when supported.
