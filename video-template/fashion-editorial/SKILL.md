---
name: fashion-editorial
description: A high-fashion editorial video style - cold desaturated grade, dramatic high-contrast light, monumental clean architecture or backdrop, deliberate model pose, strong silhouette, and luxury material texture. Applies to fashion, beauty, luxury, and personal-brand subjects. Trigger on /fashion-editorial, "Fashion Editorial", "luxury fashion campaign", "high fashion video", or "editorial model film".
---

# Fashion Editorial

A **high-fashion editorial style**, not a fixed model or outfit. Keep the user's subject exactly as briefed - a garment, model, accessory, beauty look, or luxury brand - and stage it in the locked editorial look below. The style supplies the *look*; the user supplies the *what*. Tuned for **Seedance** (the platform's default video model): the prompt follows Seedance's `subject -> scene -> motion -> camera -> light -> style` ordering.

## Video preview

1. Before generating a video, prepare a few keyframes matching the user's subject, style, and aspect ratio. Reuse suitable supplied or already approved images.
2. Show the actual images through accessible links, briefly describe the intended motion, and ask the user to confirm. End the turn and wait; do not start a video job before confirmation. Revise the preview if requested.
3. After confirmation, generate the video. Use the approved images as first/last frames or references when supported by the selected model; otherwise follow the approved visual direction in the prompt. Reuse existing confirmation for an unchanged preview.

Keep the preview message short: the images, a brief motion description, and one confirmation question.

## What this style is

**The essence:** make fashion feel **untouchable and monumental** - a body, garment, or luxury object held in architectural space with deliberate restraint. The goal is **status, silhouette, and material presence**, not warmth or lifestyle realism.

**Touchstones:** high-fashion magazine editorials, luxury house campaign films, runway lookbook films in museums or galleries, cold architectural fashion photography.

**What makes it distinct:** **cold architecture + strong silhouette + deliberate pose**. The picker thumbnail is a lone model in a vast white arched gallery with hard window shadows. This is not casual creator fashion, not a street lookbook, and not a warm beauty commercial.

## Style dimensions (locked)

- **Visual tone - cold and desaturated**: blue-grey whites, black garments, restrained accent color, polished but not warm.
- **Camera - steady and composed**: locked-off frame, very slow push, or minimal dolly; no handheld energy.
- **Editing pace - slow and meditative**: long deliberate poses. Cuts are acceptable only as sparse editorial beats.
- **Narrative mode - abstract mood**: no literal story; the garment, pose, and space carry the meaning.
- **Setting and framing**: clean architectural backdrop or minimal studio; the model is often centered, small-to-medium in a large space, with strong negative space and graphic shadows.
- **Light**: dramatic high-contrast lighting, hard window shapes or sculpted studio contrast; never warm lifestyle light.
- **Production type - live action**: photoreal fashion campaign footage.
- **Style reference - fashion editorial**: luxury silhouette and material texture in a cold, controlled editorial world.

## Prompt construction

Write **one cohesive video prompt in your own words**, adapted to the subject. Hit these beats in Seedance order:

`fashion subject (as briefed) -> clean architectural or minimal editorial setting -> subtle pose or fabric motion -> locked frame or slow push -> dramatic high-contrast light -> cold desaturated luxury editorial grade`

**Always convey:** deliberate model pose or product stance, strong silhouette, luxury material texture, clean monumental backdrop, cold desaturated editorial grade, dramatic high-contrast light, restrained expensive mood.

**Never:** casual clothes, influencer styling, warm natural light, cheerful lifestyle context, cluttered room, fast social-video energy, soft flat beauty lighting.

Adapt the subject, garment, pose, and backdrop to the brief. Put aspect ratio, negatives, and seed in the **params**.

## Generation parameters

- **aspectRatio**: `16:9` for campaign films; `9:16` for vertical fashion social cuts.
- **resolution and model tier**: pick a tier that supports the resolution - fast tiers cap lower (often `720p`); `1080p` needs a full tier.
- **duration**: `5-8s`; let the pose, fabric, and light breathe.
- **negativePrompt**: `casual clothes, influencer styling, warm color tones, natural lifestyle lighting, cluttered background, soft flat lighting, cheerful commercial look, fast cuts, low resolution, distorted anatomy`.
- **generateAudio**: usually **off**; add music or sound design in edit.
- **seed**: mild lever for text-to-video; use `firstFrameImageUrl` for look consistency.
- **firstFrameImageUrl**: use the approved opening frame when the selected model supports this input.

## How to apply

Treat the subject as a campaign image brought to life. Keep the frame spare, architectural, cold, and deliberate. If the brief needs casual outfit documentation, warm beauty content, or fast influencer energy, this style is not the fit.

## Worked examples

Same editorial register; the subject changes.

1. **"a crimson couture coat"** -> a lone model centered in a white arched gallery, oversized sculptural coat, hard window shadows, cold editorial grade (see reference still).
2. **"a black evening dress"** -> statuesque pose against a clean concrete wall, high-contrast side light, slow push-in on the silhouette.
3. **"a luxury handbag campaign"** -> model holding the bag in a vast minimal lobby, restrained pose, material texture close-up, cold polished light.
4. **"a jewelry editorial"** -> model in a simple black suit, one sharp highlight on the necklace, clean architectural negative space.

## Reference output

| Field | Value |
| --- | --- |
| Picker thumbnail | `https://cdn.vm0.io/artifacts/user_3EWY21Oe3f15kfs3yYmbGgDb3NV/31026908-c354-4cb5-a51b-8ac8e12ac910/thumbnail-fashion-editorial.jpg` |
| Reference still - crimson couture coat (Seedream, seed 60) | `https://cdn.vm0.io/artifacts/user_3EWY21Oe3f15kfs3yYmbGgDb3NV/7e4b718c-b98e-4210-98d1-7bb781dd344e/image-7e4b718c.png` |
| Canonical | cold editorial grade, monumental clean space, hard shadows, deliberate pose, strong silhouette, luxury material |

> The reference still holds the editorial look on a different fashion subject (crimson coat vs. pale skirt look) - the style is subject-invariant. Use an approved frame of the user's subject when supported.
