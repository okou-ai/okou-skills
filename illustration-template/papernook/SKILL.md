---
name: papernook
description: Hand-drawn editorial illustration set in a cozy cluttered personal-studio scene. Loose scratchy black ink outlines that wobble, textured gouache fills with visible brush marks, warm cream paper background, simplified dot-eye face, and a DENSE edge-to-edge composition where a centered character is orbited by thematic props that visually act out the idea. Modern editorial palette (coral / dusty blue / sage / cream) on warm cream — no mustard or burnt-orange. Trigger when user says /papernook, asks for a "papernook illustration", a "cozy cluttered editorial scene", a "warm-cream desk scene", or a new piece in this hand-drawn studio-clutter editorial style.
---

# /papernook — locked warm-cream studio-clutter editorial illustration

This skill produces editorial illustrations in a single locked house style: a centered character on warm cream paper, surrounded edge-to-edge by hand-drawn thematic props that act out an idea as a *scene metaphor*. The character has a tiny dot-eye face. The line work is loose, scratchy, slightly wobbly. Fills are painterly gouache with visible brush marks. The palette modernizes the classic warm-folk look — coral pink, dusty cornflower blue, sage green — while keeping the cream paper background warm.

Each invocation swaps ONE of the **scene metaphor + character** axes. Every other style axis stays locked.

## Prompt interpretation

The user typically gives a short prompt — a persona + an activity (e.g. "designer meditating", "engineer debugging at 2am", "barista pulling espresso"). Brainstorm and expand it into a vivid scene yourself — don't ask the user to flesh it out. Pick a *scene metaphor* (the structural archetype below) that fits, then list 15–25 thematic props that fill the canvas and make the metaphor unmistakable.

For each invocation:

1. **Read the prompt as a seed**, not a complete brief.
2. **Pick a scene metaphor** from the framework below that fits the activity.
3. **Cast the character** with a specific outfit silhouette that uses the locked palette.
4. **List 15–25 thematic props** that crowd the canvas edge-to-edge. The props are the metaphor — they should make a marketing manager, an engineer, a researcher, a barista immediately legible without reading any text.
5. **Compose at L3 density** by default — props orbit the centered character, filling every corner of the warm-cream paper.
6. **Hold every other axis locked** — palette, texture intensity, face style, background, line quality.

Bias toward concrete, lived-in details: a half-eaten ramen cup, a sleeping cat curled by the laptop, a Polaroid clipped to yarn, a wall clock reading 2:00. The clutter is the personality.

## The 6-axis brief framework

A papernook brief is six dials. Five are usually held at default; the user generally only varies axis 2 and 4.

### 1. Palette (色系) — default: `modern-editorial`

| Token | Foreground colors | When to use |
|---|---|---|
| `modern-editorial` *(default)* | dusty cornflower blue, soft coral pink, fresh sage green, charcoal black, warm cream | Default modern editorial feel — fresh and contemporary |
| `museum-rich` | burnt-orange, forest green, navy, terracotta, warm cream | Cultural / historical / book-y subjects |
| `cool-studio` | slate blue, mint, blush pink, charcoal, warm cream | Tech / lab / minimalist subjects |
| `mono-warm` | single hue (e.g. coral) + charcoal accents + warm cream | High-contrast hero illustrations |

**The cream paper background ALWAYS stays warm** (slightly yellow-tinted, not cool off-white). This is non-negotiable — it's the lock that makes the style feel cozy rather than corporate.

### 2. Scene metaphor (场景隐喻) — vary per invocation

What the character is *doing as a metaphor for an idea*. Pick one:

| Token | What it looks like | Good for |
|---|---|---|
| `desk-review` | Character at a cluttered desk reviewing artifacts on a screen / paper | Work, debugging, analysis, writing |
| `wall-of-evidence` | Character in front of a pinned wall (corkboard / sticky notes) | Research, synthesis, planning, investigation |
| `field-discovery` | Character inside a richly-detailed environment (library, museum, lab, greenhouse) | Discovery, learning, exploration |
| `crafting` | Character holding or making a tangible object (chart, prototype, bouquet) | Building, launching, creating, presenting |
| `ritual` | Character mid-routine (meditating, pouring coffee, journaling) | Calm, focus, mood, daily practice |

The scene metaphor IS the metaphor — don't reuse generic filing-cabinet props relabeled for a new theme. Pick props that are *native to the moment*.

### 3. Complexity (复杂度) — default: `L3`

| Token | Props | Feel |
|---|---|---|
| `L1` | 3–5 props, breathable cream space | Spot illustration |
| `L2` | ~12 props, half-filled wall | Editorial column |
| `L3` *(default)* | 25+ props, edge-to-edge cram | Magazine spread / hero |

papernook is intentionally a *dense* style. Default to L3.

### 4. Character (角色) — vary per invocation

| Sub-axis | Options |
|---|---|
| Gender / age | Free choice — but ALWAYS use the locked face style |
| Hair | Curly bob, short curls, wavy, straight, buzz — solid color or simple shape |
| Outfit silhouette | Cardigan + pants, hoodie + jeans, blazer + tee, apron + striped shirt, oversized sweater + loose pants — colors must come from the active palette |
| Pose | Seated centered, standing front-facing, holding-object, pointing, eyes-closed-calm, hunched-focused |

**Face is LOCKED**: two dot eyes (or two closed-eye arcs `⌒⌒` when meditating / focused / eyes-closed), tiny nose mark (a single small curve or dot — never a triangular bump), small soft mouth (a tiny curve). No rendered features. No detailed shading. The face is a simple symbol of a person.

### 5. Composition (构图) — default: `centered-portrait`

| Token | Layout |
|---|---|
| `centered-portrait` *(default)* | Character in middle, props orbit/float around them filling every corner |
| `desk-frontal` | Character behind a desk in the lower third, wall of props behind |
| `environment-immersive` | Character placed inside a room/place — shelves, walls, windows visible as the container |
| `peek-frame` | Character cropped at chest in the lower portion, props fill the rest |

Always portrait aspect ratio.

### 6. Texture intensity (笔触) — default: `H`

| Token | Quality |
|---|---|
| `L` | Cleaner, more tidy ink |
| `M` | Some wobble, mostly controlled |
| `H` *(default)* | Very scratchy, wobbly, loose — the ink looks like a real brush pen on rough paper |

The references are all `H`. Don't go below `M` — the style stops feeling hand-drawn.

## Locked style axes (NEVER vary)

These are not dials — they are constants that make papernook recognizable.

### Background — warm cream paper
- A slightly yellow-tinted cream, NOT cool off-white
- Visible canvas / paper texture under the strokes
- Never a flat white, never a colored backdrop, never a gradient
- Cream extends to all four edges — no border frame

### Line quality
- Black ink outlines, scratchy and slightly wobbly — looks hand-painted, not vector
- Variable line weight from natural brush-pen pressure
- Visible imperfections — ink density shifts, organic wobbles, small breaks where the pen lifted
- NOT digital-clean, NOT uniform marker stroke, NOT geometric

### Fills — textured gouache
- Painterly color fills with visible brush marks INSIDE the shape (not flat solid color)
- Slight overspill of color past the ink outline, occasional white speckle showing the cream paper through
- Color sits *on top of* the cream — never replaces it

### Face — locked symbol
- Two small dot eyes OR two closed-eye `⌒⌒` arcs
- Tiny nose hint (one small curve or dot)
- Small soft mouth (a tiny curve)
- Soft round head
- NO detailed eyes, NO eyebrows beyond a tiny mark, NO rendered nose, NO teeth

### Composition density
- Every corner of the canvas has something in it
- Props float / orbit / pin to the wall — they are not in a grid
- The character anchors the center; props are slightly smaller and crowd around them
- Visual weight balanced — no one quadrant should be empty

### Color discipline
- Always pick ONE palette and stick to it
- No mustard, no burnt-orange, no ochre, no earthy folk-art tones in `modern-editorial` (default)
- Cream paper always wins as the dominant "color"
- Charcoal black is the ink — never use it as a fill color for clothing or props beyond small details

## Reference images

Five locked refs are included alongside this SKILL.md.

| File | Role |
|---|---|
| `ref-anchor.png` | **Locked style anchor** — pass this as the image-to-image reference on every invocation so the warm-cream paper, ink texture, and density transfer. Subject: a young woman with curly brown hair, holding a chart, surrounded by sticky notes and design tools. |
| `ref-meditation.png` | Scene metaphor: `ritual`. Designer meditating in lotus, enso halo, surrounded by Wacom / Pantone / brushes / incense / pebbles. |
| `ref-engineer.png` | Scene metaphor: `desk-review`. Engineer in coral hoodie debugging at 2am, red ERROR text, rubber duck, sleeping cat, ramen. |
| `ref-researcher.png` | Scene metaphor: `wall-of-evidence`. Researcher in blue blazer pointing at a giant pinboard of quote cards and charts. |
| `ref-barista.png` | Scene metaphor: `ritual`. Barista in coral apron pulling espresso at a counter, MORNING BREW chalkboard, hanging cups. |

## Scene brainstorm playbook

This is **inspiration, not a template**. Always go beyond the starter combos — pick details specific to the moment you're imagining.

| Scene metaphor | Activity seed | Possible props (pick 15–25 for L3) |
|---|---|---|
| `desk-review` | Engineer debugging | Laptops with red ERROR scribbles, terminal windows, energy drink cans, ramen cup with chopsticks, rubber duck, mechanical keyboard, headphones, sleeping cat, GitHub Octocat doodle, Slack notification balloon, coffee mug, wall clock reading 2:00, USB cables, sticky-notes with code snippets, "NIGHT MODE" Post-it, snake plant |
| `desk-review` | Writer drafting | Open notebook with handwritten lines, fountain pen, coffee cup with ring stains, dictionary, crumpled paper balls, candle, eyeglasses, typewriter sketch, pinned manuscript pages, bookmark sticking out of stacked books |
| `wall-of-evidence` | Researcher synthesizing | Corkboard of index quote cards, color-coded yarn connecting clusters, persona portrait sketches, Post-its labeled PAIN/GOAL/IDEA, hand-drawn bar and pie charts, spiral notebook, recorder with mic, headphones, succulent, Polaroid clipped to string |
| `wall-of-evidence` | PM planning launch | Kanban columns with sticky-notes, hand-drawn roadmap with arrows, milestone dates circled, stakeholder photos pinned, sprint board, calendar with launch date, Slack message bubbles, GANTT bars, espresso cup |
| `field-discovery` | Botanist in greenhouse | Hanging plants, terracotta pots, watering can, plant tags, magnifying glass, leaf sketches, butterfly, gardening shears, seed packets, sun streaming through window panes, gardening journal |
| `field-discovery` | Librarian among stacks | Tall bookshelves, ladder, stack of books, brass desk lamp, reading nook chair, card catalog drawers, tea cup with steam, glasses, scroll, bookmark, owl on shelf |
| `crafting` | Designer presenting work | Held-up portfolio page, easel with sketch, color swatch fan, Pantone book, iMac with wireframe, ruler, x-acto knife, washi tape, glue stick, magazine clippings on wall |
| `crafting` | Florist arranging bouquet | Buckets of flowers, ribbons, brown wrapping paper, scissors, twine, glass vases, plant cuttings, watering can, wooden bench, tags handwritten with names |
| `ritual` | Barista morning brew | Espresso machine with steam wand, milk pitchers, coffee bean grinder, glass jar of beans, MORNING BREW chalkboard menu, hanging cups, tip jar, plant, paper cups, vinyl record, arched window with morning rays, latte-art curlicues floating in air |
| `ritual` | Yoga / meditation | Lotus pose, enso halo behind head, candle, incense stick with curling smoke, pebble stack, small singing bowl, prayer beads, plant, rolled mat, water bottle |

**Brainstorming heuristic when stuck:**
- 3–5 props that ground the activity (the obvious ones)
- 5–10 props that add personality / specificity (the unexpected ones — the kicked-off shoe, the half-eaten snack, the bookmark)
- 5–10 atmospheric details (wall calendar, plant, coffee mug, sticky notes, hanging artwork)

## Style brief structure

When generating, write a single rich prompt that explicitly references the locked style and the locked anchor reference image. Skip technical endpoint mechanics — those depend on the execution environment — but DO tell the model to use the included anchor reference as an image-to-image input so the warm-cream paper, ink texture, and density transfer reliably.

```
Generate a NEW illustration that EXACTLY matches the source anchor reference's hand-drawn editorial style — same loose scratchy black ink outlines that wobble, same textured gouache fills with visible brush marks, same WARM CREAM paper background showing canvas texture (do not cool it down, do not flatten it to off-white), same simple dot-eye face (no rendered features), same DENSE edge-to-edge L3 composition with the character centered and thematic props orbiting/filling every corner.

NEW scene metaphor: {{SCENE_METAPHOR — desk-review / wall-of-evidence / field-discovery / crafting / ritual}}.

CHARACTER: {{CHARACTER_DESCRIPTION — e.g. a young woman with chin-length wavy brown hair wearing a DUSTY CORNFLOWER BLUE blazer over a coral t-shirt, standing centered, pointing at an index card she holds up, calm focused expression}}. Face is the locked dot-eye symbol — two small dot eyes (or two `⌒⌒` closed-eye arcs if eyes-closed), tiny soft nose hint, small soft smile. No rendered features.

PROPS — fill the canvas edge-to-edge with 15–25 thematic objects:
{{PROP_LIST — list each prop concretely. Example for a designer meditating:
- A faint hand-drawn enso (zen circle) glowing softly behind the character's head like a halo
- A Wacom tablet with stylus floating to her left
- An iMac tilted with a wireframe sketch on screen
- An open sketchbook with bezier curves
- A jar of paint brushes
- Pantone color chip booklets fanned open
- Hex code swatch cards hand-lettered #F4A6A6 / #8FB9C6 / #B5C9A6
- A typography specimen poster pinned to the wall
- A tiny succulent in a terracotta pot
- A coffee mug with steam
- Sticky notes in coral / dusty blue / sage
- Washi tape rolls
- A ruler, scissors, a small camera
- A folded magazine
- A small candle with flame
- An incense stick with curling smoke
- A pebble stack (zen cairn)
- A small singing bowl
}}

PALETTE: {{PALETTE_TOKEN — default modern-editorial}} — dusty cornflower blue, soft coral pink, fresh sage green, charcoal black ink, WARM cream background. NO mustard, NO burnt-orange, NO ochre, NO earthy folk-art tones. The cream paper stays WARM (slightly yellow-tinted, never cool off-white).

COMPOSITION: portrait aspect ratio, centered-portrait layout — character in the middle, props orbit and fill every corner with no empty quadrant.

TEXTURE: H (scratchy, wobbly, loose — looks like real brush pen on rough paper, not vector, not digital-clean).

Match the locked exemplar style precisely. Do NOT copy any text or UI from the references.
```

Pass `ref-anchor.png` to the image-to-image model on EVERY call as the locked style+background+density reference. This is how the cream paper warmth and brush-stroke texture survive across all generations.

## Style correction guide

If the output misses a specific style axis, correct with a focused instruction:

| Issue | Correction |
|---|---|
| Background reads cool / off-white | "The background must stay WARM CREAM — slightly yellow-tinted paper texture. Do not flatten to white." |
| Mustard / burnt-orange leaking in | "Remove ALL mustard, burnt-orange, ochre, and earthy folk tones. The palette is dusty cornflower blue, soft coral pink, fresh sage green, charcoal, warm cream — nothing else." |
| Composition too sparse | "Pack the canvas to L3 density — add 10+ more thematic props until every corner has something in it. Edge-to-edge cram." |
| Face too detailed / rendered | "Replace the face with the locked symbol: two small dot eyes (or `⌒⌒` arcs for closed), a tiny nose mark, a small soft mouth. No shading, no detailed features." |
| Lines too clean / digital | "Loosen the ink — scratchy, wobbly, hand-painted, visible pressure variation and small organic imperfections. NOT vector, NOT uniform marker." |
| Fills too flat | "Add visible brush marks inside each color fill — painterly gouache, not flat color blocks. Allow occasional cream paper to show through." |
| Character off-center | "Re-center the character. Props orbit around them filling every corner." |
| Props feel generic / template-y | "Make the props NATIVE to the activity — pick objects that someone doing this thing specifically would have. Not generic file-cabinet shapes relabeled." |
| Aspect ratio wrong | "Portrait aspect ratio (vertical)." |

## Anti-patterns

- ❌ White background — must be WARM cream
- ❌ Cool / blue-tinted off-white — must be WARM, slightly yellow
- ❌ Flat vector color fills — must be painterly with visible brush marks
- ❌ Mustard / burnt-orange / ochre in `modern-editorial` palette — must be coral / dusty blue / sage
- ❌ Realistic face features — must be the locked dot-eye symbol
- ❌ Sparse composition with empty quadrants — must be L3 dense
- ❌ Grid-aligned props — must orbit / float organically
- ❌ Clean uniform line weight — must be scratchy and varied
- ❌ Generic relabeled props — must be thematically native to the activity
