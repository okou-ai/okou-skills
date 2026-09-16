# Cozy Parlor — locked spec

A hand-painted watercolor + ink-line illustration style — one anthropomorphic animal in a quiet domestic interior, on **clean cool-white paper** (never amber-tinted cream), with a neutral cool palette and a single hot accent pop. Cozy, hushed, picture-book mood.

## Locked frame (never change across pieces)

- **Medium**: hand-painted watercolor washes + brushy black ink line drawn ON TOP of the washes. Visible brushstrokes and translucent pigment bleeds.
- **Paper**: clean, cool, bright neutral-white watercolor paper. **No amber tint, no warm cream overlay, no sepia wash.** The paper itself is the cool anchor.
- **Subject**: ONE anthropomorphic animal character, mid-quiet-activity in a domestic interior.
- **Character face**: closed crescent eyes + tiny triangle nose. Minimal facial features. Sometimes a soft pink cheek dot. **Expression is conveyed through posture, never through the face.**
- **Setting**: cozy domestic interior — a study, kitchen, parlor, greenhouse, studio, etc. Never outdoors, never abstract, never an open landscape.
- **Patterned surfaces**: at least 2 surfaces in frame carry decorative pattern (wallpaper, upholstery, rug, curtain, tile, textile, ceramic, smock, cushion). This is non-negotiable.
- **Palette structure**: cool/neutral lead (sage, slate-blue, cornflower, lavender, dove-gray, mint, chalk-white) + ONE hot accent pop (cherry-red, mustard, magenta-pink, terracotta — single object only). **No warm cream/butter/peach/amber overlay.** Hot accent is a single object, not a wash.
- **Object-rich staging**: personality props placed throughout — books, jars, records, plants, dishes, lamps, paintings, tools of the activity. The space feels lived-in.
- **Canvas**: portrait 1024x1536 (2:3 portrait), gpt-image-1.5, quality high.

## Dials (vary per piece)

- **Cast** — cat, frog, mouse, hedgehog, otter, rabbit, fox, bear, capybara, owl, badger, raccoon… One per piece. Don't reuse the same animal across a series — vary it. (Per [[feedback_illustration_character_variety]].)
- **Scene metaphor / activity** — writing letters, baking bread, kneading dough, listening to records, reading, painting at an easel, watering plants, brewing tea, knitting, mixing potions, repairing a watch. The activity IS the metaphor — pick props native to the activity. (Per [[feedback_illustration_scene_not_template]].)
- **Palette family** — pick one cool-neutral lead pair + one hot accent:
  - **Sage-Study**: sage-green + dusty slate-blue + chalk-white, MUSTARD accent
  - **Cornflower-Kitchen**: dusty cornflower-blue + mint-green + chalk-white, CHERRY-RED accent
  - **Lavender-Lounge**: pale-lavender + dusty teal + chalk-white, MAGENTA-PINK accent
  - **Mint-Studio**: soft mint-green + dove-gray + chalk-white, CHERRY-RED accent
  - **Slate-Parlor**: dove-gray + slate-blue + chalk-white, CHERRY-RED accent (A2 anchor)
  - …or compose a new cool/neutral family. Never lead with amber/cream/butter/peach. (Per [[feedback_watercolor_neutral_paper]].)
- **Pattern motif stack** — pick 2–3 from: stripes, gingham, polka-dot, small florals, delft tile, wavy/scallop, checkered, lattice. Vary the motif mix across pieces.
- **Hot accent object** — choose ONE object to carry the accent color (a lamp, a book, a tulip, a teapot, a record sleeve, a towel, an apple, a hibiscus). Never a wash, never a wall color, never a "lighting" tint.
- **Complexity level**:
  - **L1** — close character + 1 prop, tight crop, fewer patterned surfaces (2 max), lots of paper breathing room
  - **L2** — corner vignette, medium-shot, 2–3 patterned surfaces, 4–6 props
  - **L3** — full-room vignette, layered staging, 3+ patterned planes (wall + floor + textile), 6+ props
- **Posture** — chill, focused, blissful, contemplative, mid-action. **Always closed-eye soft smile**, even mid-action. (Per [[feedback_illustration_chill_expressions]].)

## Example prompt template

```
Hand-painted watercolor + brushy black ink line on CLEAN COOL-WHITE watercolor paper — no amber tint, no warm cream overlay, the paper itself reads bright neutral white. Cozy domestic interior. ONE anthropomorphic animal character with simple closed crescent eyes and a tiny triangle nose — minimal facial features, expression through posture. At least two patterned surfaces in frame. Object-rich personality staging. Visible brush strokes and translucent watercolor washes. Picture-book illustration mood. Portrait composition.

PALETTE (cool/neutral): {PALETTE_LEAD}, one HOT {ACCENT_COLOR} accent on {ACCENT_OBJECT}. Avoid cream, butter, peach, amber, terracotta. Overall wash cool and balanced.

SCENE: {CAST_DESCRIPTION} {ACTIVITY_DESCRIPTION}, in a {SETTING}. PATTERN MOTIFS: {PATTERN_1}, {PATTERN_2}, {PATTERN_3}. PROPS: {PROP_LIST}. COMPLEXITY: {L1 | L2 | L3 description}.
```

Generation command:

```bash
okou generate image --provider built-in --skip-style --model gpt-image-1.5 \
  --size 1024x1536 --quality high --prompt "<filled template>"
```

## Reference pieces

The four anchor variations that confirmed the spec (all neutral-palette, locked frame intact):

1. **B3 — Frog writing letters** (L3, Sage-Study palette, mustard lamp accent)
   `https://cdn.vm0.io/artifacts/user_36PnTFtD4dBQ9zg5jj6E5r918aV/e1c9a7a4-fbaf-43cd-818a-acd8cbbd6222/image-e1c9a7a4.png`

2. **C3 — Mouse baking bread** (L2, Cornflower-Kitchen palette, cherry-red tulip accent)
   `https://cdn.vm0.io/artifacts/user_36PnTFtD4dBQ9zg5jj6E5r918aV/e4985ab1-c39b-4ae1-9368-e8873598ce43/image-e4985ab1.png`

3. **D3 — Hedgehog with headphones** (L3, Lavender-Lounge palette, magenta hibiscus accent)
   `https://cdn.vm0.io/artifacts/user_36PnTFtD4dBQ9zg5jj6E5r918aV/23e755b4-4816-4aaf-a877-66d3b9407f33/image-23e755b4.png`

4. **E3 — Otter painting** (L2, Mint-Studio palette, cherry-red palette accent)
   `https://cdn.vm0.io/artifacts/user_36PnTFtD4dBQ9zg5jj6E5r918aV/8257edff-b275-4631-af02-daa5bce9dc97/image-8257edff.png`

## Anti-patterns

- ❌ Warm cream / amber / butter / peach paper background — paper must stay cool-neutral.
- ❌ Reusing the same animal cast across the series — every piece picks a fresh animal.
- ❌ A generic editorial scene (filing cabinets, megaphones, "office shapes") — the activity itself is the metaphor.
- ❌ Open eyes, eyebrows, or visible mouth on the character — closed crescents only, smile via posture.
- ❌ Outdoor scenes, landscapes, abstract backgrounds — always a domestic interior.
- ❌ Only one patterned surface — must have at least two.
- ❌ Hot accent used as a wash or wall color — it's always a single object.
