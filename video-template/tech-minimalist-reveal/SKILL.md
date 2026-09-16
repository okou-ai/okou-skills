---
name: tech-minimalist-reveal
description: A minimalist tech/product reveal video style — a single product floating in a bright white seamless studio void, precise soft studio light, clean shadow, glossy reflection, cool neutral grade, and generous negative space. Applies to whatever product the user brings. Trigger on /tech-minimalist-reveal, "product reveal", "Phone Product Showcase", "Apple-style product video", or "clean studio product shot".
---

# Phone Product Showcase

A premium **product-reveal style**, not a fixed product. Keep the user's product exactly as briefed — a phone, a watch, a bottle, a gadget — and present it in the locked studio look below. The style supplies the *look*; the user supplies the *what*. Tuned for **Seedance** (the platform's default video model): the prompt follows Seedance's `subject → scene → motion → camera → light → style` ordering, and framing/negatives are expressed the way Seedance follows most reliably.

## Video preview

1. Before generating a video, prepare a few keyframes matching the user's subject, style, and aspect ratio. Reuse suitable supplied or already approved images.
2. Show the actual images through accessible links, briefly describe the intended motion, and ask the user to confirm. End the turn and wait; do not start a video job before confirmation. Revise the preview if requested.
3. After confirmation, generate the video. Use the approved images as first/last frames or references when supported by the selected model; otherwise follow the approved visual direction in the prompt. Reuse existing confirmation for an unchanged preview.

Keep the preview message short: the images, a brief motion description, and one confirmation question.

## What this style is

**The essence:** make a single object feel **precious and inevitable** — isolate it in clean empty space and let pristine light do all the talking. The goal is **focus and reverence for the object**, nothing else in the frame to distract.

**Touchstones:** Apple product films, premium consumer-tech keynote reveals, high-end e-commerce hero shots, minimalist studio still-life.

**What makes it distinct:** **emptiness + precision**. One product, a seamless white void, controlled studio light — the opposite of lifestyle context, clutter, or warmth. Not a scene; a reverent object study.

## Style dimensions (locked)

- **Visual tone — cool & desaturated**: clean, near-neutral white-to-grey, slightly cool grade; pristine, no warm cast.
- **Camera — slow push-in**: one slow, smooth dolly toward the product; controlled, weightless, never handheld.
- **Shot continuity**: one continuous unhurried take. No cuts.
- **Setting & framing**: a **bright white seamless studio void** (cyclorama), product centered with generous negative space; glossy subtly reflective floor; one clean soft shadow. Macro inserts on key detail are allowed, but the establishing frame stays wide and empty.
- **Light**: precise soft studio lighting — large soft sources, gentle gradient falloff, a clean rim; no hard speculars, no colored gels.
- **Production type — live action**: photoreal product footage / CGI-grade realism. Not illustration.
- **Style reference — minimalist tech reveal**: the empty-studio precision of a flagship product film.

## Prompt construction

Write **one cohesive video prompt in your own words**, adapted to the user's product. Compose naturally, hitting these beats in Seedance order:

`product (as briefed) → seamless white studio void → subtle motion (slow rotation / float) → slow push-in → precise soft studio light → cool neutral grade`

**Always convey:** a single product isolated in a bright white seamless void · generous negative space · precise soft studio lighting with one clean shadow · cool neutral grade · slow push-in or slow product rotation · pristine macro-sharp detail · photoreal.

**Never:** cluttered or lifestyle background, warm/colored light, hard speculars, handheld shake, fast cuts, props or hands (unless the user asks).

Adapt the product, its material highlights, and the exact move to what's briefed. Put aspect ratio, negatives, and seed in the **params**, not the prose.

## Generation parameters

- **aspectRatio**: `16:9` (hero) or `9:16` for social product clips.
- **resolution & model tier**: target resolution must be supported by the chosen model tier — fast/draft tiers cap lower (often `720p`); `1080p` needs a full-quality tier.
- **duration**: `5–8s`; pace one slow push-in or half-rotation to fill it.
- **negativePrompt**: `cluttered background, lifestyle context, warm color, colored light, hard glare, handheld shake, fast cuts, busy scene, low resolution, distorted product`.
- **generateAudio**: usually **off** for a clean product cut (add music/VO in edit); leave on only for a subtle ambient hum.
- **seed**: mild lever for text-to-video; use it to re-roll the *same* prompt. The real consistency tool is `firstFrameImageUrl`.
- **firstFrameImageUrl**: use the approved opening frame when the selected model supports this input.

## How to apply

Drop the user's product into the empty white studio and let it own the frame. Do **not** add lifestyle scenery, hands, or warm light. If the brief needs the product *in use* or in context, this style isn't the fit — prefer a lifestyle or commercial style.

## Worked examples

Same locked studio look; the product changes.

1. **"our new wireless earbuds"** → an open earbuds case floating and slowly rotating in a white seamless void, precise soft light, one clean shadow, slow push-in, cool neutral grade.
2. **"a smart water bottle"** → the bottle standing on a glossy reflective floor, slow push-in revealing condensation macro detail, pristine studio light.
3. **"a luxury perfume bottle"** → the bottle on a low pedestal, slow orbit catching glass refractions, generous negative space (see reference still).
4. **"a flagship phone"** → the phone floating upright, screen edge catching a clean rim light, slow push-in to a macro of the camera module.

## Reference output

| Field | Value |
| --- | --- |
| Picker thumbnail | `https://cdn.vm0.io/artifacts/user_3EWY21Oe3f15kfs3yYmbGgDb3NV/c3219368-a46b-43ce-9e98-5b5826fcaa8d/thumbnail-tech-minimalist-reveal.jpg` |
| Reference still — perfume (Seedream, seed 50) | `https://cdn.vm0.io/artifacts/user_3EWY21Oe3f15kfs3yYmbGgDb3NV/6a2bf374-0049-4ade-80f9-bbd419787825/image-6a2bf374.png` |
| Canonical | single product · white seamless void · clean shadow + reflection · cool neutral · slow push-in · 16:9 |

> The reference still holds the studio look on a different product (perfume vs. phone) — the style is product-invariant. Use an approved frame of the user's subject when supported.
