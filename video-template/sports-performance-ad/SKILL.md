---
name: sports-performance-ad
description: A sports performance advertising video style - athlete effort, gear and body close-ups, impact rhythm, motion blur, Dutch or low angles, high-contrast desaturated grade, and dramatic rim light. Applies to any sport, athlete, training action, or performance product. Trigger on /sports-performance-ad, "sports performance ad", "athletic commercial", "training commercial", or "sports brand film".
---

# Sports Performance Ad

A **sports performance advertising style**, not a fixed sport and not a generic motivation montage. Keep the user's athlete, action, or performance product exactly as briefed - running, boxing, cycling, lifting, climbing, team drills, shoes, gloves, a racket, or training gear - and shoot it in the locked commercial look below. The style supplies the *look*; the user supplies the *what*. Tuned for **Seedance** (the platform's default video model): the prompt follows Seedance's `subject -> scene -> motion -> camera -> light -> style` ordering.

## Video preview

1. Before generating a video, prepare a few keyframes matching the user's subject, style, and aspect ratio. Reuse suitable supplied or already approved images.
2. Show the actual images through accessible links, briefly describe the intended motion, and ask the user to confirm. End the turn and wait; do not start a video job before confirmation. Revise the preview if requested.
3. After confirmation, generate the video. Use the approved images as first/last frames or references when supported by the selected model; otherwise follow the approved visual direction in the prompt. Reuse existing confirmation for an unchanged preview.

Keep the preview message short: the images, a brief motion description, and one confirmation question.

## What this style is

**The essence:** make performance feel **physical, precise, and commercially aspirational** - the body under pressure, gear in motion, sweat catching light, every frame selling speed, strength, or endurance. The goal is **performance credibility and premium sports-ad intensity**, not generic inspirational sentiment.

**Touchstones:** sports-brand training commercials, athlete product-launch films, pre-race campaign spots, high-contrast performance gear advertising.

**What makes it distinct:** **performance close-up + gear/body detail + kinetic commercial rhythm**. The picker thumbnail is a low close-up of a runner's shoe and calf over a dark track, with motion blur and lane lines. This is a sports ad register: it can sell the athlete, the training moment, or the performance product. It is not short-form viral creator energy and not a calm wellness scene.

## Style dimensions (locked)

- **Visual tone - cinematic high contrast**: desaturated, gritty, dark track/gym/terrain textures, hard white highlights on sweat, skin, and gear.
- **Camera - extreme close-up commercial coverage**: shoes, hands, tape, grips, chalk, muscles, breath, sweat, product surfaces; low angles and Dutch angles are welcome.
- **Editing pace - fast cut / impact rhythm**: rapid 1-2 second beats, motion blur, and rhythmic effort details. If a single generation cannot create true edits, build the energy inside the shot and assemble cuts in edit.
- **Narrative mode - performance progression**: preparation, exertion, peak action, product or athlete payoff.
- **Production type - live action advertising**: photoreal athlete or sports-product footage.
- **Light**: dramatic backlit rim light at peak effort; sweat and edges should catch the light.
- **Emotional tone - premium competitive intensity**: tough, focused, aspirational, not playful.
- **Style reference - sports performance ad**: sports-commercial close-ups, kinetic detail, and grit.

## Prompt construction

Write **one cohesive video prompt in your own words**, adapted to the sport. Hit these beats in Seedance order:

`athlete, sport action, or performance product (as briefed) -> gritty training or competition setting -> effort motion with body/gear detail -> extreme close-ups, low angle, Dutch angle -> dramatic rim light -> high-contrast desaturated sports-ad grade`

**Always convey:** athlete effort or performance product detail, muscle tension, sweat, gear texture, motion blur, fast rhythmic energy, dramatic backlit rim light, high-contrast desaturated grade, commercial polish.

**Never:** calm atmosphere, static camera, soft lighting, wellness yoga mood, casual creator footage, bright cheerful lifestyle look.

Adapt the sport, body detail, product detail, and action beats to the brief. Put aspect ratio, negatives, and seed in the **params**.

## Generation parameters

- **aspectRatio**: `16:9` for campaign ads; `9:16` for vertical sports commercial cuts.
- **resolution and model tier**: pick a tier that supports the resolution - fast tiers cap lower (often `720p`); `1080p` needs a full tier.
- **duration**: `5-8s`; for true fast-cut ads, generate multiple short shots and assemble them.
- **negativePrompt**: `calm atmosphere, static camera, soft lighting, wellness mood, casual creator footage, bright cheerful lifestyle, slow meditative pacing, clean studio product look, generic motivational poster, low resolution, distorted limbs`.
- **generateAudio**: **on** if supported - breath, foot strikes, glove impact, rope slap, or gym ambience strengthens the ad feel.
- **seed**: mild lever for text-to-video; use `firstFrameImageUrl` for look consistency.
- **firstFrameImageUrl**: use the approved opening frame when the selected model supports this input.

## How to apply

Stay close to performance evidence. Show body mechanics, sweat, gear, product texture, and impact. If the brief is casual sports lifestyle, playful challenge content, or calm wellness, this style is too intense.

## Worked examples

Same sports-ad register; the sport changes.

1. **"a runner training at dawn"** -> low close-up of shoes striking a dark track, calf tension, lane lines streaking, motion blur (the picker thumbnail).
2. **"a boxer before a match"** -> close-up of a boxer tightening white hand wraps, sweat and rim light, gritty gym (see reference still).
3. **"a climber on an overhang"** -> chalked fingers gripping rock, forearm tension, low angle, high contrast, dust in backlight.
4. **"a new running shoe"** -> outsole and laces in extreme close-up during foot strike, track lines streaking behind, rim light catching foam texture.

## Reference output

| Field | Value |
| --- | --- |
| Picker thumbnail | `https://cdn.vm0.io/artifacts/user_3EWY21Oe3f15kfs3yYmbGgDb3NV/5a95669a-b86c-4817-9d82-250da7509b54/thumbnail-athletic-motivation.jpg` |
| Reference still - boxer hand wraps (Seedream, seed 62) | `https://cdn.vm0.io/artifacts/user_3EWY21Oe3f15kfs3yYmbGgDb3NV/be3365b8-9cdc-48b0-ab60-009b14218d3a/image-be3365b8.png` |
| Canonical | sports-ad close-up, athlete effort, gear/product detail, motion blur, Dutch/low angle, high-contrast rim light |

> The reference still holds the sports performance ad look on a different sport (boxing vs. running) - the style is sport-invariant and product-aware. Use an approved frame of the user's subject when supported.
