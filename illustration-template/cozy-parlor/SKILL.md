---
name: cozy-parlor
description: "Hand-painted watercolor + ink-line illustration style — one anthropomorphic animal in a quiet domestic interior, on clean cool-white watercolor paper (never amber-tinted), with a neutral cool palette and a single hot accent pop. Cozy, hushed, picture-book mood. Trigger when the user says /cozy-parlor, asks for a 'cozy parlor illustration', a 'watercolor animal scene', a 'picture-book interior', or a new piece in this neutral-palette watercolor style."
---

# Cozy Parlor Illustration

Use this register-only image style when the user asks for a cozy watercolor animal scene, a domestic-interior picture-book illustration, a "/cozy-parlor" piece, or any new piece in this hand-painted-on-cool-white-paper neutral-watercolor style.

This style is distinct from `folk-storybook` (warmer aged-paper folk gouache, fully painted) and `painterly-botanical` (single-figure portrait with foliage). Cozy Parlor is a **scene-based watercolor**: clean cool paper, brushy black ink line over translucent washes, one anthropomorphic animal mid-quiet-activity, and a single hot accent pop against a cool palette.

Bundled reference imagery — four canonical outputs that demonstrate the framework in action:

- `ref-frog-letters.jpg` — Frog at a writing desk dipping a quill, sage curtain + pale-blue stripe wallpaper + slate gingham blotter, mustard lamp accent. Demonstrates the **Sage-Study palette** and the **L3 full-vignette** archetype.
- `ref-mouse-baker.jpg` — Mouse kneading bread on a marble counter, delft tile backsplash + polka-dot dishcloth + striped flour jar, cherry-red tulip accent. Demonstrates the **Cornflower-Kitchen palette** and the **L2 corner-vignette** archetype.
- `ref-hedgehog-records.jpg` — Hedgehog in headphones curled on a tufted pouf, lavender wavy wallpaper + checkered floor + striped throw, magenta hibiscus accent. Demonstrates the **Lavender-Lounge palette** and **L3 full-vignette** at a moodier emotional register.
- `ref-otter-painter.jpg` — Otter in a chalk-stripe smock painting at an easel, floral curtain + gingham smock pocket + checkered rug, cherry-red palette accent. Demonstrates the **Mint-Studio palette** and that the activity itself is the metaphor — never a generic editorial scene.

## Locked Style Fundamentals (never vary)

| Axis | Spec |
|---|---|
| **Medium** | Hand-painted translucent watercolor washes + brushy black ink line drawn ON TOP |
| **Paper** | Clean cool-white watercolor paper — bright neutral white, NO amber tint, NO warm cream overlay, NO sepia wash |
| **Texture** | Visible brushstrokes, watercolor pigment bleeds, faint paper grain |
| **Subject** | ONE anthropomorphic animal character, mid-quiet-activity in a domestic interior |
| **Character face** | Closed crescent eyes + tiny triangle nose. Sometimes a soft pink cheek dot. **No open eyes, no eyebrows, no visible mouth.** Expression lives in posture, never in the face. |
| **Setting** | Cozy domestic interior — study, kitchen, parlor, greenhouse, studio, library, etc. Never outdoors, never abstract, never landscape. |
| **Patterned surfaces** | At least 2 surfaces in frame carry decorative pattern (wallpaper, rug, curtain, upholstery, tile, textile, ceramic, smock, cushion). |
| **Palette lead** | Cool/neutral — sage, slate-blue, cornflower, lavender, dove-gray, mint, chalk-white. **Never lead with cream, butter, peach, amber, terracotta.** |
| **Accent** | Exactly ONE hot pop (cherry-red, mustard, magenta-pink, terracotta) on a SINGLE OBJECT — a lamp, book, tulip, towel, etc. Never a wash, never a wall color. |
| **Staging** | Object-rich personality props — books, plants, dishes, lamps, jars, tools of the activity. Lived-in feel. |
| **Canvas** | Portrait 1024x1536 (2:3) via `gpt-image-1.5`, `--quality high` |

### The chill-face rule (critical)

Every character keeps closed crescent eyes + a soft content smile, **even mid-action**. A bear pouring boiling water keeps closed eyes. A mouse mid-knead keeps closed eyes. An otter mid-brushstroke keeps closed eyes. All energy lives in the body posture, the activity props, and the scene — never in the face. (Per [[feedback_illustration_chill_expressions]].)

### The cool-paper rule (critical)

The paper is the cool anchor of the whole style. If the background reads cream, butter, beige, or amber — **the piece is wrong**. The watercolor must read neutral. Hot accents are welcome as a single object (the lamp, the tulip, the book). Hot accents as a wash or wall color break the style. (Per [[feedback_watercolor_neutral_paper]].)

### The activity-is-metaphor rule

The scene metaphor is the activity itself, not a relabeled editorial template. A "writing" scene shows a real desk, real letters, a real quill — not a filing cabinet labeled "letters". A "baking" scene shows a real counter, real dough, a real oven. (Per [[feedback_illustration_scene_not_template]].)

### The cast-rotation rule

Across a series, **vary the animal**. Don't use the same cat in every piece. Cast is a per-scene dial, not a locked mascot. Mix: cat, frog, mouse, hedgehog, otter, rabbit, fox, bear, capybara, owl, badger, raccoon… (Per [[feedback_illustration_character_variety]].)

## Dials (vary per piece)

- **Cast** — pick one animal from a wide pool; rotate across the series
- **Activity / scene metaphor** — writing letters, baking, kneading dough, listening to records, reading, painting, watering plants, brewing tea, knitting, mixing potions, repairing a watch, drying herbs
- **Palette family** — pick one of the canonical five, or compose a new cool/neutral lead:
  - **Sage-Study**: sage-green + dusty slate-blue + chalk-white → MUSTARD accent
  - **Cornflower-Kitchen**: dusty cornflower-blue + mint + chalk-white → CHERRY-RED accent
  - **Lavender-Lounge**: pale-lavender + dusty teal + chalk-white → MAGENTA-PINK accent
  - **Mint-Studio**: soft mint-green + dove-gray + chalk-white → CHERRY-RED accent
  - **Slate-Parlor**: dove-gray + slate-blue + chalk-white → CHERRY-RED accent
- **Pattern motif stack** — pick 2–3 from: stripes, gingham, polka-dot, small florals, delft tile, wavy/scallop, checkered, lattice
- **Hot accent object** — ONE object carries the hot color
- **Complexity** —
  - **L1**: close character + 1 prop, tight crop, 2 patterned surfaces max
  - **L2**: corner vignette, 2–3 patterned surfaces, 4–6 props
  - **L3**: full-room vignette, 3+ patterned planes, 6+ props

## Prompt template

```
Hand-painted watercolor + brushy black ink line on CLEAN COOL-WHITE watercolor paper — no amber tint, no warm cream overlay, the paper itself reads bright neutral white. Cozy domestic interior. ONE anthropomorphic animal character with simple closed crescent eyes and a tiny triangle nose — minimal facial features, expression through posture. At least two patterned surfaces in frame. Object-rich personality staging. Visible brush strokes and translucent watercolor washes. Picture-book illustration mood. Portrait composition.

PALETTE (cool/neutral): {PALETTE_LEAD}, one HOT {ACCENT_COLOR} accent on {ACCENT_OBJECT}. Avoid cream, butter, peach, amber, terracotta. Overall wash cool and balanced.

SCENE: {CAST_DESCRIPTION} {ACTIVITY_DESCRIPTION}, in a {SETTING}. PATTERN MOTIFS: {PATTERN_1}, {PATTERN_2}, {PATTERN_3}. PROPS: {PROP_LIST}. COMPLEXITY: {L1 / L2 / L3 description}.
```

## Model guidance

This style is designed for narrative scene compositions with multiple props, patterned surfaces, and a single anthropomorphic character — the kind of scene a strong text-to-image model can compose in one pass from a detailed prompt. Recommended pairing: `gpt-image-1.5` at `high` quality, portrait `1024x1536`, with prompt enhancement disabled so the locked-fundamentals language reaches the model verbatim.

The bundled reference images (`ref-frog-letters.jpg`, `ref-mouse-baker.jpg`, `ref-hedgehog-records.jpg`, `ref-otter-painter.jpg`) are canonical outputs of this framework — provided for *human* style study and prompt authoring. They are not required as image inputs at generation time — the style transfers entirely through the detailed prompt language.

If output drifts (paper reads cream/amber, palette unifies under a warm overlay, ink lines feel too vector-clean, character face opens up), tighten the prompt by re-emphasizing **"CLEAN COOL-WHITE watercolor paper, no amber tint, no warm cream overlay, paper reads bright neutral white"** and the closed-crescent-eye rule — rather than reaching for image-to-image.

## Example briefs

### Example 1 — Bear knitting (Sage-Study, L2)

```
PALETTE: sage-green + dusty slate-blue + chalk-white lead, one HOT MUSTARD accent on a ball of yarn.

SCENE: A small brown BEAR in a chunky cardigan sits in a wingback chair knitting a scarf, in a quiet LIVING ROOM CORNER. PATTERN MOTIFS: slate-blue chevron wallpaper, a small floral cushion, a checkered throw. PROPS: a basket of yarn balls, a half-finished scarf trailing, a wooden side table with a mug, a small dachshund-shaped doorstop. COMPLEXITY: L2 corner vignette.
```

### Example 2 — Cat watering plants (Slate-Parlor, L1)

```
PALETTE: dove-gray + slate-blue + chalk-white lead, one HOT CHERRY-RED accent on a watering can.

SCENE: A tuxedo CAT tips a small red watering can over a potted spider plant on a windowsill, in a sun-cool NOOK. PATTERN MOTIFS: a slate-blue chalk-stripe curtain, a small polka-dot pot wrap. PROPS: a wooden stool, a single trailing pothos, a teacup on the sill. COMPLEXITY: L1 close-character composition.
```

### Example 3 — Owl reading (Lavender-Lounge, L3)

```
PALETTE: pale-lavender + dusty teal + chalk-white lead, one HOT MAGENTA-PINK accent on a single peony in a vase.

SCENE: A small barn OWL nestled in an oversized velvet armchair reads a thick book by lamplight, in a quiet STUDY. PATTERN MOTIFS: lavender wavy wallpaper, a tufted chair pattern, a striped rug, a checkered footstool. PROPS: a leaning bookshelf, a tea tray with a flowered cup, a brass desk lamp, a single magenta peony in a vase, a stack of books on the floor. COMPLEXITY: L3 full-room vignette.
```

## Anti-patterns (the deal-breakers)

- ❌ Warm cream / amber / butter / peach paper background — paper must stay cool-neutral. (This is the #1 failure mode.)
- ❌ Reusing the same animal cast across the series — every piece picks a fresh animal.
- ❌ Generic editorial scene with relabeled props (filing cabinets, megaphones, abstract office shapes).
- ❌ Open eyes, eyebrows, or visible mouth on the character — closed crescents only.
- ❌ Outdoor scenes, landscapes, abstract backgrounds — always a domestic interior.
- ❌ Only one patterned surface — must have at least two.
- ❌ Hot accent used as a wall color, lighting tint, or background wash — always a single object.
- ❌ Vector-clean line work or flat color fills — must feel hand-painted with visible brushstrokes.
- ❌ Photorealism, 3D rendering, airbrush gradients — watercolor + ink only.

## Series example — same style across a varied set

A four-piece set for blog covers in this style might include:
1. **Frog writing letters** (Sage-Study, L3) — a study/quiet-focus scene
2. **Mouse baker** (Cornflower-Kitchen, L2) — a kitchen/craft scene
3. **Hedgehog with headphones** (Lavender-Lounge, L3) — a leisure/listening scene
4. **Otter painter** (Mint-Studio, L2) — a creative/making scene

Each piece flexes cast + activity + palette + complexity against the same locked frame. The four feel cousin-related, never identical.
