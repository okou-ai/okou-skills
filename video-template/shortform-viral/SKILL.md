---
name: shortform-viral
description: A short-form viral video style — vertical 9:16, fast hook, authentic handheld creator energy, bright saturated casual look, and a fast cut rhythm. Applies to whatever the user is filming. Trigger on /shortform-viral, "TikTok style", "Reels style", "viral short video", or "UGC creator clip".
---

# Shortform Viral

A **social short-form style**, not a fixed scene. Keep the user's subject exactly as briefed — a product, a moment, people, a place — and shoot it like a creator's phone clip below. The style supplies the *energy*; the user supplies the *what*. Tuned for **Seedance** (the platform's default video model): the prompt follows Seedance's `subject → scene → motion → camera → light → style` ordering.

## Video preview

1. Before generating a video, prepare a few keyframes matching the user's subject, style, and aspect ratio. Reuse suitable supplied or already approved images.
2. Show the actual images through accessible links, briefly describe the intended motion, and ask the user to confirm. End the turn and wait; do not start a video job before confirmation. Revise the preview if requested.
3. After confirmation, generate the video. Use the approved images as first/last frames or references when supported by the selected model; otherwise follow the approved visual direction in the prompt. Reuse existing confirmation for an unchanged preview.

Keep the preview message short: the images, a brief motion description, and one confirmation question.

## What this style is

**The essence:** feel like a real person filmed it on their phone and it blew up — **authentic, immediate, high-energy**. The goal is **relatable spontaneity and a fast hook**, not polish. It should look unproduced on purpose.

**Touchstones:** TikTok / Reels creator content, GRWM and day-in-the-life clips, candid travel/lifestyle UGC, run-and-gun phone footage.

**What makes it distinct:** **vertical, handheld, fast, bright**. The opposite of a locked tripod and a slow cinematic grade — its credibility comes from looking casual and real.

## Style dimensions (locked)

- **Visual tone — warm & natural, bright saturated**: punchy daylight, casual phone-camera look, lively color; not a graded "film" look.
- **Camera — handheld raw**: natural handheld movement, slight shake and reframes, follows the action; feels human-held.
- **Editing pace — fast cut**: quick rhythmic cuts; a strong hook in the **first second**. (Seedance can do multi-shot — use it here.)
- **Narrative mode — observational**: candid, in-the-moment; no formal narration.
- **Production type — live action**: real-world phone-grade footage.
- **Emotional tone — playful & fun**: upbeat, joyful, casual energy.
- **Style reference — short-form viral**: authentic creator content built to stop the scroll.

## Prompt construction

Write **one cohesive video prompt in your own words**, adapted to the subject. Hit these beats in Seedance order:

`subject (as briefed) → casual real-world setting → energetic action → handheld camera following it → bright natural light → playful creator vibe`

**Always convey:** vertical 9:16 phone framing · a strong action/hook right away · natural handheld movement · bright saturated casual daylight · playful authentic energy · fast pacing.

**Never:** formal studio/tripod look, slow meditative pacing, cinematic letterbox, heavy color grade, staged stiffness.

Adapt the action and setting to the subject. Put aspect ratio, negatives, and seed in the **params**.

## Generation parameters

- **aspectRatio**: `9:16` (vertical — non-negotiable for this style).
- **resolution & model tier**: pick a tier that supports the resolution — fast tiers cap lower (often `720p`); `1080p` needs a full tier.
- **duration**: `5–8s`; pack a hook + a beat or two of payoff. Multi-shot is welcome.
- **negativePrompt**: `formal studio look, tripod locked frame, cinematic letterbox, slow pacing, heavy color grade, staged, stiff, low resolution`.
- **generateAudio**: **on** — casual ambient/energy helps the authentic feel (swap for trending audio in edit).
- **seed**: mild lever for text-to-video. For look consistency use `firstFrameImageUrl`.
- **firstFrameImageUrl**: use the approved opening frame when the selected model supports this input.

## How to apply

Shoot the user's subject like a creator would: vertical, in the moment, energetic, bright. If the brief wants a slow, premium, cinematic feel, this is the wrong style — pick a cinematic or product style instead.

## Worked examples

Same casual creator energy; the subject changes.

1. **"unboxing our snack product"** → hands ripping open the pack to camera, quick cuts to a bite and a reaction, vertical, bright kitchen daylight, playful.
2. **"a beach day with friends"** → friends running and laughing toward the water, handheld follow, bright saturated, fast cuts (see reference still / picker thumbnail).
3. **"a coffee shop morning"** → POV walking in, quick cuts of the order and first sip, casual handheld, warm daylight.
4. **"a sneaker drop"** → fast hook on feet stepping into frame, quick spins and angles, vertical, energetic.

## Reference output

| Field | Value |
| --- | --- |
| Picker thumbnail | `https://cdn.vm0.io/artifacts/user_3EWY21Oe3f15kfs3yYmbGgDb3NV/40ab801f-16bc-4e29-8370-6b10cd394e30/thumbnail-shortform-viral.jpg` |
| Reference still — rooftop party (Seedream, seed 51, 9:16) | `https://cdn.vm0.io/artifacts/user_3EWY21Oe3f15kfs3yYmbGgDb3NV/06064f7a-abdb-4284-9562-507d6dce7ed4/image-06064f7a.png` |
| Canonical | vertical 9:16 · handheld · bright saturated · fast cuts · playful creator energy |

> The reference still holds the casual bright-energy look on a different subject (rooftop party vs. beach crew) — the style is subject-invariant.
