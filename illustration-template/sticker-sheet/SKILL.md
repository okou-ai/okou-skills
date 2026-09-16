---
name: sticker-sheet
description: Sticker Sheet — hand-painted gouache sticker-sheet illustration. ~20 small floating themed objects on pure white, punchy saturated palette (coral, mustard, sage, dusty pink, navy, cream, warm brown), flat brushy gouache fills with wobbly hand-drawn ink linework and tiny decorative marks (dots, hatches, squiggles) on every object. Each object slightly tilted, no drop shadows, cheerful cozy lifestyle journal mood. Trigger when user says /sticker-sheet, asks for a "sticker sheet illustration", "hand-painted gouache sticker pack", "themed object sheet", or briefs with a scene theme + object count in this house style.
---

# /sticker-sheet — Hand-painted gouache sticker-sheet illustration

This skill produces a single sheet of roughly 20 themed objects rendered as hand-painted gouache stickers, scattered loosely across pure white. Every piece is a curated little collection — desk objects, kitchen items, travel essentials, plants, self-care things — painted with flat brushy gouache fills, overlaid with wobbly hand-drawn ink, and dotted with small decorative marks. The recipe is locked; only the **theme** and the **object list** vary.

## Prompt interpretation

The user typically supplies a **short theme seed** — usually a setting or activity ("a cozy kitchen breakfast", "weekend travel essentials", "plant-lover indoor jungle", "Sunday self-care reset"). It is your job to **brainstorm and expand it** into a concrete object list of ~18-22 items. Do not stop to confirm. Imagine the collection, then run.

For each invocation:

1. **Take the seed.** Note the theme, mood, time-of-day if given, any specific object the user named.
2. **Imagine the collection.** What are the iconic items someone with this theme would gather on a journal page? What's the hero object, what are the supporting cast, what's the small surprise (the rubber ducky, the vinyl record, the single croissant)?
3. **Set the three dials** (theme, object list, accent palette weighting) — see "Variable axes" below.
4. **Keep every other axis locked.** Medium, palette range, layout style, ink handling, mood — never vary.

Bias toward concrete, lived-in details: a striped mug rather than "a mug", a strawberry-jam jar with a handwritten label rather than "a jar", a croissant with visible flake marks rather than "a pastry". The sheet should feel hand-assembled, not auto-generated.

## Locked style axes (NEVER vary)

### Medium
- **Opaque gouache on white paper.** Flat brushy color fills with visible paint texture and small streaks where the brush lifts.
- **Wobbly hand-drawn black ink linework laid OVER the color** — slightly imperfect, scratchy, traced loosely over the painted shape rather than perfectly aligned. The ink defines silhouettes and adds interior detail.
- **Decorative ink marks on every object**: dots, tiny hatches, squiggles, tiny stars, small line patterns, hand-lettered labels, scribble textures. Every single object carries some kind of small interior detail in ink.
- **NOT** watercolor wash (no transparent bleeds). **NOT** digital vector. **NOT** photorealistic. **NOT** clean cartoon outline. **NOT** 3D-shaded or gradient-rendered.

### Palette (saturated, not pastel)
- **Bright coral / terracotta-red** — primary warm accent (mugs, sweaters, jam jars, lampshades)
- **Mustard yellow** — secondary warm (lamps, bags, kettle, sunflowers)
- **Sage green** — primary cool warm (plants, vases, books)
- **Dusty pink** — soft accent (face masks, slippers, sweaters)
- **Navy blue** — anchor (suitcases, sneakers, sweaters, book spines)
- **Cream / warm off-white** — paper, ceramic, page backgrounds inside objects
- **Warm brown** — wood, cardboard, vinyl sleeves, baskets

**Avoid** pastel-only output (faded mint, beige-on-beige), neon, magenta, pure black fills, gradients, airbrush blends. Colors should read **punchy** like real gouache, not muted lifestyle-stock.

### Composition
- **Vertical aspect** (e.g. 1024 × 1536 / 9:16).
- **Pure white background.** No backdrop color, no paper texture filling the bleed, no scene.
- **~18-22 small objects** floating freely, scattered across the sheet like a real sticker pack.
- **Varied sizes** — a few "hero" objects 1.5-2x the size of supporting items.
- **Each object tilted at a slight playful angle** — never aligned to a strict grid.
- **Breathing room** between objects — they should not overlap or merge.
- **NO drop shadows.** Objects sit on white, not on the page.
- **NO scene context** — no shelf, no desk, no floor. Just objects on white.
- **NO human figures of any kind** — no people, no faces, no portraits, no family photos with figures, no character stickers, no figurines, no avatar badges, no person silhouettes. The sheet is a collection of **objects**. (Small animal characters — a cat, a duck, a bird — are fine as a playful surprise; they are not human figures.) If a brief seems to imply a person (e.g. "a framed family photo", "a passport photo"), substitute an object equivalent (a framed botanical print, a passport with only an ink seal visible).

### Mood
- Cheerful, cozy, lifestyle-journal warm.
- The vibe of a curated journal spread, a print-and-cut sticker book, or a hand-lettered packing list.

## Variable axes (the dials you set per sheet)

### 1. Theme — *what the collection is*
Strong picks:
- Cozy work-from-home desk (laptop, mug, headphones, plants, sticky notes, calendar...)
- Cozy kitchen breakfast (toaster, kettle, French press, croissant, jam, eggs, sourdough...)
- Weekend travel essentials (suitcase, camera, passport, sunglasses, sun hat, sneakers, postcard...)
- Plant-lover indoor jungle (monstera, snake plant, cacti, watering can, pruning shears, terracotta pots...)
- Sunday self-care reset (bath salts, candle, face mask, slippers, teacup, yoga mat, lavender...)
- Cozy reading nook (paperbacks, tea, bookmark, glasses, blanket, lamp, cat...)
- Stationery + journaling kit (notebooks, washi tape, pens, stickers, paperclips, ruler...)
- Camping weekend (tent, lantern, thermos, marshmallows, hiking boots, compass, trail map...)
- Holiday season cozy (mug of cocoa, knit gloves, ornament, cookie, pinecone, candle, scarf...)
- Picnic in the park (basket, sandwich, lemonade, blanket, fruit bowl, frisbee, paperback...)

Each theme should pick **a hero object** (the laptop, the suitcase, the kettle) and let the others orbit it.

### 2. Object list — *the curated ~20*
Brainstorm a list of **18-22 items** that someone with this theme would gather. Aim for:
- 2-3 **hero objects** (large, central, instantly readable)
- 8-10 **supporting cast** (medium-size functional items)
- 5-7 **small accents** (tiny details: a sprig of rosemary, a sticky note, a key, a coin, a pen)
- 1-2 **playful surprises** (the rubber ducky, the vinyl record, the single croissant, the cat) — the thing that makes the sheet feel alive

For each item, picture one specific concrete detail (a striped mug, a handwritten jam label, a folded knit sweater, a vinyl record in a cream sleeve). Vagueness flattens the result.

### 3. Accent palette weighting — *which colors lead*
The palette is locked, but the **proportions shift** with theme:
- **Kitchen / breakfast** → mustard + coral + cream + warm brown lead; navy minimal
- **Travel** → navy + mustard + warm brown lead; coral + sage support
- **Plants / jungle** → sage + terracotta + cream lead; coral + mustard minimal
- **Self-care** → dusty pink + sage + cream lead; coral as the one warm pop
- **Desk / work** → mustard + sage + coral + navy evenly distributed

Pick a weighting that fits the theme — don't paint a self-care sheet in mustard-and-navy or a travel sheet in pink.

## Reference images (the locked set)

Four canonical pieces anchor this style. Use them as visual references when prompting an image model — pass at least one as an image input where the model supports image-to-image.

| File | Theme | What it anchors |
| --- | --- | --- |
| `ref-desk.jpg` | Cozy work-from-home desk | **The canonical exemplar.** Strongest balance of palette weights, dense object count (~20 items), variety of small ink marks, hero-laptop + supporting-monstera composition. Always pass this as the primary reference unless theme strongly suggests another. |
| `ref-kitchen.jpg` | Cozy kitchen breakfast | The warm-palette exemplar. Mustard + coral + warm-brown dominant, French press as hero, hand-lettered jam label, varied food + utensil shapes. |
| `ref-travel.jpg` | Weekend travel essentials | The cool-palette exemplar. Navy + mustard + warm-brown dominant, suitcase as hero, paper-map texture handling, varied soft + hard goods. |
| `ref-plants.jpg` | Plant-lover indoor jungle | The cultural-variant exemplar. Sage + terracotta dominant, dense varied leaf shapes, hand-lettered packet labels, macramé hanger detail. |

## Prompt recipe

When constructing a prompt, follow this structure. Adapt the bracketed slots; keep everything else verbatim.

```
A hand-painted GOUACHE sticker-sheet illustration. Flat brushy gouache color fills with visible paint texture — NO 3D shading, NO gradients. Wobbly hand-drawn black ink linework laid OVER the color, slightly imperfect and scratchy, with small decorative ink marks on every object (dots, tiny hatches, squiggles, tiny stars, small line patterns, hand-lettered labels).

Theme: [theme name in one phrase].

Roughly 20 small floating objects scattered across pure white background like a real sticker sheet, each tilted at a slight playful angle, varied sizes, breathing room between them, NO drop shadows, NO scene context.

Include the following ~20 items: [comma-separated object list with concrete details — e.g. "a chrome toaster with toast popping up, a whistling enamel kettle with steam swirl, a French press half-full of coffee, a striped coffee mug, ..."].

Palette (punchy saturated, NOT muted pastels): [palette weighting for this theme — name 3-4 colors that lead, then 2-3 that support]. Lead colors: [...]. Support: [...].

Vary sizes and rotations. Cheerful cozy lifestyle journal mood. Same charming wobbly hand-painted feel as a real artist's sheet.
```

## Model guidance

This style is generated on the **nano-banana-2** family of image-to-image models (`fal-ai/nano-banana-2/edit`), which supersedes plain nano-banana on fal. Nano-banana-2 (Gemini 3.1 Flash Image) preserves the thick brushy ink linework, wobbly hand-drawn quality, and flat gouache fills that the style requires, and accepts up to 14 reference images for compositing.

**Avoid OpenAI GPT-Image models for this style.** Side-by-side tests on GPT-Image-1.5 showed it returns muted pastel output with thin clean lines and faint 3D shading — even with a strong reference and `input-fidelity high`. The look ends up "lifestyle stock" rather than "hand-painted journal". GPT-Image-2 has not been retested here, but the underlying photographic-fidelity bias is unlikely to have changed.

When the chosen model supports image-to-image, **always pass `ref-desk.jpg` as the primary reference** (it is the canonical anchor with the broadest palette and densest composition). Optionally pass a theme-aligned secondary reference (`ref-kitchen.jpg`, `ref-travel.jpg`, `ref-plants.jpg`) when the brief matches that theme family.

When the model is text-only (no image input), the prompt recipe above is sufficient but expect more drift from the locked style; prefer an i2i model if available.

## Evaluation checklist

Inspect each generated sheet against the locked axes before accepting:

- [ ] Surface reads as **opaque gouache** — flat brushy fills with paint texture, not gradients or 3D
- [ ] Black ink linework is **wobbly and hand-drawn**, laid OVER color, slightly imperfect
- [ ] **Every object carries a small interior ink detail** (dots, hatches, squiggle, lettering)
- [ ] Palette is **punchy and saturated**, not muted/pastel
- [ ] **~18-22 objects**, varied sizes, slight rotations, breathing room
- [ ] **Pure white background**, no scene, no shelf, no drop shadows
- [ ] Theme reads instantly from the object collection
- [ ] At least one **small playful surprise** in the sheet (the unexpected item)
- [ ] Mood reads as **cheerful cozy journal**, not lifestyle-stock
- [ ] **No human figures, faces, or portraits** anywhere on the sheet

If a generation fails on two or more checks, regenerate rather than ship it. Re-running with the same reference + a tighter object list usually fixes drift.

## Anti-patterns (what to reject)

- Muted pastel / faded palette — should be punchy saturated gouache
- Thin clean digital outlines — must be wobbly hand-drawn ink with paint texture
- 3D shading, gradients, airbrush blends — must be flat fills only
- Drop shadows under objects — they sit on pure white, never shadowed
- Scene context (a shelf, a desk, a floor) — objects float freely
- Object count too low (under 15) or too high (over 25) — aim for ~20
- Objects perfectly aligned to a grid — each should tilt at its own angle
- "Lifestyle stock" mood — should feel hand-assembled and journal-warm
- More than 2 generic objects in a row without an ink detail — every object needs its own small marks
- **Any human figure, face, portrait, or person-shaped sticker** — the sheet is objects only (small animal characters are fine; humans are not)
