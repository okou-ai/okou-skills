---
name: hand-drawn-fantasy-anime
description: A hand-drawn fantasy animation video style - painterly 2D backgrounds, expressive simple characters, lush nature, soft diffused light, warm storybook color, and gentle magical wonder. Applies to any fantasy, character, nature, or adventure subject. Trigger on /hand-drawn-fantasy-anime, "hand-drawn fantasy animation", "painterly 2D fantasy", "storybook anime", or "warm forest animation".
---

# Hand Drawn Fantasy Anime

A **hand-drawn fantasy animation style**, not a fixed character, studio, or franchise. Keep the user's subject exactly as briefed - a child, creature, village, forest path, airship, animal companion, or magical object - and render it in the locked painterly 2D fantasy look below. The style supplies the *look*; the user supplies the *what*. Tuned for **Seedance** (the platform's default video model): the prompt follows Seedance's `subject -> scene -> motion -> camera -> light -> style` ordering.

## Video preview

1. Before generating a video, prepare a few keyframes matching the user's subject, style, and aspect ratio. Reuse suitable supplied or already approved images.
2. Show the actual images through accessible links, briefly describe the intended motion, and ask the user to confirm. End the turn and wait; do not start a video job before confirmation. Revise the preview if requested.
3. After confirmation, generate the video. Use the approved images as first/last frames or references when supported by the selected model; otherwise follow the approved visual direction in the prompt. Reuse existing confirmation for an unchanged preview.

Keep the preview message short: the images, a brief motion description, and one confirmation question.

## What this style is

**The essence:** make the world feel **handmade, alive, and gently enchanted** - simple expressive characters moving through lush painted nature, with soft light and small magical details. The goal is **wonder, warmth, and emotional innocence**, not spectacle or combat.

**Touchstones:** hand-painted family fantasy animation, classic cel-animation character design, watercolor and gouache forest backgrounds, storybook adventure films, nature-centered animated fables.

**What makes it distinct:** **painterly background + simple expressive 2D character + gentle natural magic**. The picker thumbnail shows a child in a glowing forest with soft blue-green depth, painted tree trunks, floating light creatures, and a calm sense of discovery.

**Brand-safety note:** do not name or request any specific protected studio, director, franchise, or character. Describe only the visual traits: hand-drawn 2D animation, painterly backgrounds, expressive characters, lush nature, soft diffused light, and gentle wonder.

## Style dimensions (locked)

- **Visual tone - warm natural fantasy**: lush greens, amber light, soft blues in depth, warm highlights, gentle color richness.
- **Camera - slow push-in**: a patient drift or slow push toward the character or discovery moment.
- **Editing pace - slow and meditative**: let the painted world breathe; no rapid cutting.
- **Narrative mode - linear story moment**: a clear small encounter or discovery, not abstract graphics.
- **Production type - 2D animation**: hand-drawn or painterly digital 2D; visible brushwork in backgrounds, clean simple character linework.
- **Emotional tone - playful wonder**: gentle, curious, kind, childlike.
- **Style reference - hand-drawn fantasy animation**: painterly storybook nature with expressive animated characters.

## Prompt construction

Write **one cohesive video prompt in your own words**, adapted to the subject. Hit these beats in Seedance order:

`subject (as briefed) -> lush painterly fantasy setting -> gentle motion or discovery beat -> slow push-in -> soft diffused natural light -> hand-drawn 2D fantasy animation`

**Always convey:** hand-drawn 2D animation, painterly background with visible brushwork, expressive simple character design, lush natural setting, soft diffused light, warm storybook palette, gentle magical details, calm wonder.

**Never:** 3D CGI, photorealism, live action, hard digital render, plastic textures, harsh neon, generic flat vector art, dark gritty combat mood, copied franchise character, named protected studio style.

Adapt the creature, character, environment, and small motion to the brief. Put aspect ratio, negatives, and seed in the **params**.

## Generation parameters

- **aspectRatio**: `16:9` for storybook cinematic scenes; `9:16` for vertical character moments.
- **resolution and model tier**: pick a tier that supports the resolution - fast tiers cap lower (often `720p`); `1080p` needs a full tier.
- **duration**: `5-8s`; one slow discovery moment is stronger than a busy sequence.
- **negativePrompt**: `3D CGI, photorealistic, live action, hard digital render, plastic texture, harsh neon, flat vector art, dark gritty combat, copied franchise character, named protected studio style, low resolution`.
- **generateAudio**: optional - soft forest ambience, tiny chimes, wind, or gentle creature sounds can help.
- **seed**: mild lever for text-to-video; use `firstFrameImageUrl` for look consistency.
- **firstFrameImageUrl**: use the approved opening frame when the selected model supports this input.

## How to apply

Keep the world soft, painted, and emotionally clear. Give the subject a small discovery or encounter, not a noisy action plot. If the brief asks for photoreal fantasy, 3D game cinematics, or a named franchise look, this style is not the fit.

## Worked examples

Same hand-drawn fantasy register; the subject changes.

1. **"a child in a glowing forest"** -> expressive child character walking through blue-green trees, floating light creatures, soft painterly forest depth (the picker thumbnail).
2. **"a young apprentice and a moss creature"** -> apprentice kneeling on an overgrown stone bridge beside a tiny moss creature, warm painted forest, glowing motes (see reference still).
3. **"a fox delivering a letter"** -> small fox courier crossing a sunlit meadow path, hand-painted grass, gentle wind in flowers, soft amber light.
4. **"a floating village at dusk"** -> simple expressive villagers looking up at a small airship, painted clouds, warm windows, slow push-in.

## Reference output

| Field | Value |
| --- | --- |
| Picker thumbnail | `https://cdn.vm0.io/artifacts/user_3EWY21Oe3f15kfs3yYmbGgDb3NV/ad08022e-5b28-4e80-a67f-cbe5d27cbc03/thumbnail-hand-drawn-fantasy-anime.jpg` |
| Reference still - apprentice and moss creature (Seedream, seed 63) | `https://cdn.vm0.io/artifacts/user_3EWY21Oe3f15kfs3yYmbGgDb3NV/d892e1cb-a7af-465c-89a0-79b1380011ac/image-d892e1cb.png` |
| Canonical | hand-drawn 2D, painterly forest, expressive simple character, soft diffused light, warm storybook palette, gentle wonder |

> The reference still holds the hand-drawn fantasy animation look on a different subject (apprentice and moss creature vs. child in glowing forest) - the style is subject-invariant. Use an approved frame of the user's subject when supported.
