---
name: epic-grandeur
description: A large-format epic cinematic video style — wide-to-extreme-wide framing, sweeping aerial scope, vast environmental scale, warm high-contrast film grade, and a grand awe-struck tone. Applies to whatever subject the user brings; keep their subject and wrap it in this look. Trigger on /epic-grandeur, "epic cinematic", "monumental / grand cinematic", "IMAX look", or "grand cinematic trailer" style requests.
---

# Epic Grandeur

A trailer-grade, large-format cinematic **style**, not a fixed scene. Keep the user's subject exactly as briefed — a city, a product, a person, a landscape — and render it through the look below. The style supplies the *look*; the user supplies the *what*. Tuned for **Seedance** (the platform's default video model): the prompt follows Seedance's `subject → scene → motion → camera → light → style` ordering, and framing/scale/negatives are expressed the way Seedance follows most reliably.

## Video preview

1. Before generating a video, prepare a few keyframes matching the user's subject, style, and aspect ratio. Reuse suitable supplied or already approved images.
2. Show the actual images through accessible links, briefly describe the intended motion, and ask the user to confirm. End the turn and wait; do not start a video job before confirmation. Revise the preview if requested.
3. After confirmation, generate the video. Use the approved images as first/last frames or references when supported by the selected model; otherwise follow the approved visual direction in the prompt. Reuse existing confirmation for an unchanged preview.

Keep the preview message short: the images, a brief motion description, and one confirmation question.

## What this style is

**The essence:** a style whose whole job is to make the subject feel **monumental** — to overwhelm the viewer with scale and reverent awe, like the opening shot of a nature documentary or a prestige-film trailer. The goal is **awe**, not beauty, tension, or nostalgia; every choice below is a means to that end.

**Touchstones** (anchor the look to these, not to loose adjectives): Planet Earth / BBC aerial cinematography · *Dune* and *Interstellar* (Greig Fraser, Hoyte van Hoytema) · Terrence Malick · Ron Fricke's *Baraka* / *Samsara* · large-format IMAX nature films.

**What makes it distinct** from other cinematic styles: **scale + reverence** — not the intimacy and handheld immediacy of indie-naturalistic, not the shadowed tension of film-noir, not kinetic action energy. Two real ingredients combine: the **IMAX part** = large-format scale, depth, and immersion; the **epic part** = the slow, reverent register that lets that scale sink in.

## Style dimensions (locked)

- **Visual tone — cinematic**: high-contrast large-format film look; deep focus front-to-back, rich filmic grade with deep blacks and controlled highlight rolloff, warm golden cast, subtle horizon lens flare.
- **Camera — aerial / drone**: one slow, smooth, stately move using explicit Seedance camera language — `slow push-in`, `crane-up revealing the horizon`, `aerial fly-over`, or `slow orbit`. No abrupt or shaky motion.
- **Shot continuity**: default to **one continuous unhurried long take**. Only when the user wants a montage, allow a `2–3 shot sequence` (Seedance handles multi-shot) — never rapid cutting.
- **Framing & scale (this is how "epic" is rendered)**: lead with shot **size**, not mood words. `wide to extreme-wide establishing shot`, `vast environmental scale`, `layered atmospheric-perspective depth to the horizon`. Vantage suits the subject — high aerial for landscapes and cities, near eye-level for a lone hero. If the subject includes a figure, keep it **small-to-medium within the vast frame — never a close-up**.
- **Light & atmosphere**: low golden backlight (sunrise/sunset), god-rays, haze or cloud layers for depth. Warm, directional, dramatic.
- **Production type — live action**: photoreal real-world footage. Not animation, not stylized CGI.
- **Style reference — IMAX epic**: the large-format scale and immersion of IMAX, rendered in the reverent register of the touchstones above (BBC aerials, *Dune* / *Interstellar*, *Baraka*). Note: the slow, stately pacing comes from the **epic-awe register**, not from IMAX itself — IMAX is the *scale*, "epic" is the *pace*.

## Prompt construction

Write **one cohesive video prompt in your own words**, adapted to the user's subject — don't fill a fixed template. Compose naturally, but hit these beats roughly in Seedance order:

`subject (as briefed) → its grand-scale setting → motion → one slow camera move → golden backlight & atmosphere → warm cinematic grade → epic tone`

**Always convey (the non-negotiable IMAX look):**

- wide / extreme-wide framing; **never a close-up** (a person stays small-to-medium, prominent against a vast backdrop)
- one slow smooth camera move — push-in / crane-up / aerial fly-over / orbit — **pick what fits the subject**
- low golden backlight, lens flare / god-rays, atmospheric depth (haze / clouds)
- warm, high-contrast, deep-focus cinematic grade; photoreal live-action

**Never:** indoor, handheld shake, fast cuts, flat / cold / desaturated, neon.

Adapt everything else to the subject — vantage, exact light moment, and wording should suit what's in frame (a city reads best from a high aerial vantage; a lone hero reads best near eye level on the ridge). If the subject isn't a grand exterior (e.g. a product on white, an indoor scene, an abstract graphic), this style only fits by restaging it in a vast exterior — and if that would distort the user's intent, prefer a different style. See the worked examples below for range.

Put framing ratio, negatives, and seed in the **params** (next section), not in the prose.

## Generation parameters

Set these through the model's own parameters (not in the prompt text):

- **aspectRatio**: `21:9` for the cinematic letterbox (fall back to `16:9` if 21:9 is unavailable).
- **resolution & model tier**: target resolution must be supported by the chosen model tier — fast/draft tiers cap lower (often `720p`), and `1080p` needs a full-quality tier. Confirm the tier supports your resolution before locking it.
- **duration**: `5–10s`; pace the single camera move to fill the whole clip.
- **negativePrompt**: `close-up, indoor scene, handheld shake, fast cuts, flat or desaturated grade, cold color, neon, low resolution, distorted subject`.
- **generateAudio**: Seedance generates ambient sound, not spoken narration. Leave **on** for atmospheric wind / room tone; turn it **off** if you'll add your own voiceover or music in edit.
- **seed**: some run-to-run determinism, but for text-to-video it's a **mild** lever — it does not carry the look across different subjects. Use it to re-roll variations of the *same* prompt, not as the main consistency tool (that's `firstFrameImageUrl`).
- **firstFrameImageUrl**: use the approved opening frame when the selected model supports this input.

## How to apply

Take the user's subject and stage it at grand environmental scale in this look. The subject becomes the epic focal point of a vast space, seen through one slow sweeping aerial move, deep focus, warm golden grade, with an awe-struck tone. Do **not** swap the subject for a generic landscape, and do **not** push in to a close-up.

## Worked examples

Same locked look every time; the subject — and the wording around it — adapts to each brief. These are illustrative, not a fixed template to echo.

1. **"a coastal city at dawn"** *(full paragraph)*
   > A coastal city at dawn, set within a vast environment at grand scale. Wide to extreme-wide large-format establishing shot, high aerial vantage, deep focus, layered atmospheric depth to the horizon. Slow crane-up revealing the full coastline and skyline, one continuous unhurried take. Low golden backlight with god-rays and a subtle horizon lens flare, warm high-contrast cinematic color grade with rich shadow and filmic rolloff. Grand, awe-struck, photoreal live-action, IMAX epic look. Safe for all audiences, positive and uplifting, no violence, no explicit content.

2. **"a mountaineer reaching the summit"** → SUBJECT = `a mountaineer in a red jacket cresting a snow ridge toward camera, a sea of clouds below snow-capped peaks`; CAMERA = `push-in as the horizon opens`. (Canonical look — see reference still.)

3. **"our new sports car"** → SUBJECT = `a sports car on an empty desert salt flat`; CAMERA = `aerial fly-over descending toward the car`. Subject stays small-to-medium in the vast flat; no close-up on the badge.

4. **"a herd of wild horses"** → SUBJECT = `a herd of wild horses crossing a vast open plain`; CAMERA = `slow sweeping aerial alongside the herd`.

## Reference output

| Field | Value |
| --- | --- |
| Picker thumbnail | `https://cdn.vm0.io/artifacts/user_3EWY21Oe3f15kfs3yYmbGgDb3NV/2c0eb943-f65a-4225-beaa-78246f7c4a1b/thumbnail-imax-epic-cinematic.jpg` |
| Reference still — mountaineer (Seedream, seed 42) | `https://cdn.vm0.io/artifacts/user_3EWY21Oe3f15kfs3yYmbGgDb3NV/cf0fe91e-34ba-4760-b2be-c7dd8c020636/image-cf0fe91e.png` |
| Reference still — coastal city (Seedream, seed 43) | `https://cdn.vm0.io/artifacts/user_3EWY21Oe3f15kfs3yYmbGgDb3NV/307a3304-d1a0-41bd-a704-b144790510b2/image-307a3304.png` |
| Canonical | wide vista · subject small-to-medium, never close-up · sunrise + flare · warm saturated · one slow aerial/crane move · 21:9 |

> The two reference stills show the look holding across different **grand-exterior** subjects (a climber vs. a city). Non-exterior subjects (a product on white, an indoor scene, an abstract graphic) fall outside this style and need restaging — or a different style. Use an approved frame of the user's subject when supported.
