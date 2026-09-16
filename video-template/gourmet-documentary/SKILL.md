---
name: gourmet-documentary
description: A sensory culinary-documentary video style — macro food texture, rising steam, warm backlight, rich saturated color, shallow depth of field, and artisan hands in frame. Applies to whatever food/craft the user brings. Trigger on /gourmet-documentary, "food documentary", "Chef's Table style", "appetizing food video", or "sensory food close-up".
---

# Gourmet Documentary

A **sensory food-documentary style**, not a fixed dish. Keep the user's food or craft exactly as briefed — sashimi, coffee, bread, a cocktail — and shoot it in the intimate macro look below. The style supplies the *look*; the user supplies the *what*. Tuned for **Seedance** (the platform's default video model): the prompt follows Seedance's `subject → scene → motion → camera → light → style` ordering.

## Video preview

1. Before generating a video, prepare a few keyframes matching the user's subject, style, and aspect ratio. Reuse suitable supplied or already approved images.
2. Show the actual images through accessible links, briefly describe the intended motion, and ask the user to confirm. End the turn and wait; do not start a video job before confirmation. Revise the preview if requested.
3. After confirmation, generate the video. Use the approved images as first/last frames or references when supported by the selected model; otherwise follow the approved visual direction in the prompt. Reuse existing confirmation for an unchanged preview.

Keep the preview message short: the images, a brief motion description, and one confirmation question.

## What this style is

**The essence:** make food feel **irresistible and crafted by human hands** — get close enough to read every texture, catch the steam, and feel the care. The goal is **appetite and craft reverence**, an intimate sensory moment.

**Touchstones:** *Chef's Table*, *Salt Fat Acid Heat*, high-end recipe films, artisan-craft documentaries, premium food advertising macro work.

**What makes it distinct:** **macro intimacy + warmth + the human hand**. Not a wide table scene, not cold or clinical — tight, warm, tactile, with a craftsperson's hands in the frame.

## Style dimensions (locked)

- **Visual tone — warm & natural**: warm appetizing tones, rich saturated food color, soft naturalistic light.
- **Camera — extreme close-up / macro**: tight on texture and detail; subtle slow moves (slow push or slow slide) that explore the surface.
- **Editing pace — slow & meditative**: lingering shots that let texture and steam breathe. No fast cutting.
- **Narrative mode — observational**: no narrator; the food and hands tell it.
- **Production type — live action**: photoreal food footage.
- **Emotional tone — warm & nostalgic**: comforting, sensory, hand-made warmth.
- **Style reference — gourmet documentary**: the macro, steam-and-texture register of prestige food films.

## Prompt construction

Write **one cohesive video prompt in your own words**, adapted to the food. Hit these beats in Seedance order:

`food/craft (as briefed) → close intimate setting → a craft action + rising steam/motion → macro slow camera → warm backlight → rich warm grade, shallow focus`

**Always convey:** macro close-up on food texture · visible steam or motion (a pour, a sprinkle, a cut) · artisan hands in frame · warm backlight catching the surface · rich saturated warm color · shallow depth of field · slow lingering pace.

**Never:** cold/clinical lighting, fast editing, wide industrial/canteen setting, flat desaturated color, plastic-looking food.

Adapt the dish, the craft action, and the texture to the brief. Put aspect ratio, negatives, and seed in the **params**.

## Generation parameters

- **aspectRatio**: `16:9` (or `9:16` for social food clips).
- **resolution & model tier**: pick a tier that supports the resolution — fast tiers cap lower (often `720p`); `1080p` needs a full tier.
- **duration**: `5–8s`; let one slow macro move and the steam breathe.
- **negativePrompt**: `cold lighting, clinical look, fast cuts, wide industrial kitchen, flat desaturated color, plastic food, low resolution`.
- **generateAudio**: **on** — sizzle / pour / ambient kitchen sound strengthens the sensory feel.
- **seed**: mild lever for text-to-video; for look consistency use `firstFrameImageUrl`.
- **firstFrameImageUrl**: use the approved opening frame when the selected model supports this input.

## How to apply

Get intimate and warm: macro on texture, catch the steam, keep a craftsperson's hands in frame. If the brief wants a wide restaurant scene or a fast hype edit, this isn't the fit.

## Worked examples

Same warm macro look; the food changes.

1. **"latte art"** → macro of a barista pouring a rosetta, steam rising, warm backlight, slow push-in, shallow focus (see reference still).
2. **"fresh bread"** → hands tearing a warm loaf, steam escaping the crumb, golden backlight, slow lingering macro.
3. **"a cocktail"** → a slow pour over ice, condensation and citrus oils catching light, warm tones, shallow focus.
4. **"sashimi plating"** → chef's hands placing micro-herbs with tweezers, macro on the fish grain, warm key light (the picker thumbnail).

## Reference output

| Field | Value |
| --- | --- |
| Picker thumbnail | `https://cdn.vm0.io/artifacts/user_3EWY21Oe3f15kfs3yYmbGgDb3NV/30ab1733-bec0-4ddb-9e15-8f707377af7b/thumbnail-gourmet-documentary.jpg` |
| Reference still — latte pour (Seedream, seed 52) | `https://cdn.vm0.io/artifacts/user_3EWY21Oe3f15kfs3yYmbGgDb3NV/71642cf3-f879-4684-a6a1-afeb52fb723a/image-71642cf3.png` |
| Canonical | macro texture · rising steam · warm backlight · artisan hands · shallow focus · slow pace |

> The reference still holds the warm macro look on a different subject (coffee vs. sashimi) — the style is subject-invariant. Use an approved frame of the user's subject when supported.
