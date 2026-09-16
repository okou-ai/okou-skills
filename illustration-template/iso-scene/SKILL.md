---
name: iso-scene
description: Isometric editorial-magazine scene illustration in a locked flat-vector style — ultra-fine hairline outlines, monochromatic saturated background filling the canvas, and a single composed scene whose props themselves embody the theme. Trigger when users say /iso-scene, ask for an "isometric editorial illustration", a "scene illustration in the editorial machine style", or brief with palette + scene archetype + complexity.
---

# /iso-scene — Isometric Editorial Scene Illustration

Generates a single composed isometric scene in a locked house style. Each invocation varies the **palette**, **scene archetype**, and **complexity**; everything else stays locked. The defining commitment is that **the scene IS the metaphor** — never a generic filing-cabinet box with the theme labelled on folder tabs.

## Prompt interpretation

The user supplies a short brief — typically a scene archetype (e.g. "city construction", "sky garden", "castle in the sky") plus an optional palette. It is your job to **flesh that brief out into a fully composed scene** with theme-native props. Do not stop to ask. Do not default to a generic container shape.

For each invocation:

1. **Take the brief as a seed.** A two-word theme is enough to start.
2. **Choose a scene archetype** whose structural parts come from the theme itself (see archetype catalog below). The shape of the scene must read as that theme to a viewer who can't see any labels.
3. **Resolve the palette** to four colour roles (BG / BODY / FOLIAGE / ACCENT). Pick from presets or accept custom hex.
4. **Set complexity** (L1 / L2 / L3) — see complexity scale below.
5. **Compose the scene** as one self-contained object centred on a flat saturated background. Vary silhouette with optional modules (cranes, smokestacks, ladders, airships, antennas) so the machine/scene never reads as a plain rectangular box.
6. **Render at 1024×1024** with a high-fidelity text-to-image model that adheres tightly to detailed prompts.

## Locked style axes (NEVER vary)

### Perspective
- 3D **isometric**, axonometric — no vanishing-point perspective
- Centred composition with generous monochromatic negative space on all sides

### Linework
- **Ultra-fine, delicate, wispy hairline strokes** — uniform weight, ~0.5pt ink-pen feel
- NEVER bold, NEVER chunky, NEVER variable-weight
- Refined architectural-drawing or fashion-illustration sensibility — the **colour blocks do the heavy lifting**, the lines are structural guides only
- If the output reads as "graphic / poster / sticker", the linework is too heavy — regenerate thinner

### Fills
- **Flat colour fills, no gradients, no airbrush shading, no inner highlights**
- Subtle drop-shadow on the ground beneath the scene is allowed; no other shading

### Background
- The ENTIRE canvas, edge-to-edge, is filled with one solid flat saturated colour (the BG role of the palette)
- **No white. No transparency. No vignette. No background scenery.**
- If the output puts the scene on white, the prompt failed — regenerate with stronger BG-fill instruction (capitalise CRITICAL, repeat the hex)

### Aesthetic
- Editorial magazine-print quality — Monocle / Kinfolk / The New Yorker / Bloomberg / Wes Anderson sensibility
- Sophisticated, dusty, **slightly muted but saturated**
- NEVER neon, NEVER fluorescent, NEVER blacklight, NEVER bubblegum, NEVER cartoon-saccharine
- Words to avoid in the prompt: "neon", "fluorescent", "glow", "blacklight", "kawaii", "cute", "bold outlines", "thick strokes"

## CRITICAL: the scene IS the metaphor

Each theme produces a scene whose structural parts come from the theme itself.

❌ **Anti-pattern:** A generic rectangular box-machine with a file-drawer on one side, a megaphone funnel on the other, and folder tabs relabeled per theme (PLANS/LABOR/FUNDS, EMAIL/ADS/SOCIAL, DRAFT/EDIT/PUBLISH). This makes every output look like the same accounting machine with different stickers. Do not do this.

✅ **Correct approach:** Pick props native to the theme so the silhouette itself reads as the subject.

**Archetype catalog (extend liberally — these are seeds, not a closed list):**

| Theme | Scene archetype |
|---|---|
| City construction | Half-built tower + crane + cement mixer + scaffold + bricks + drafting board + hard-hat figure |
| Marketing | Broadcast tower + signal waves + envelopes radiating + studio booth at the base |
| Hiring | Conveyor belt of empty chairs + résumé sheets + "HIRED" stamp + sorting station |
| Publishing | Printing press with rollers + ink wells + paper feed + finished book stack |
| Product launch | Rocket on launchpad + steam jets + mission-control console + countdown timer |
| Sky garden | Terraced garden tower + hanging vines + gazebo + fountain + gardener with watering can |
| Floating island park | Island chunk with grassy top + gazebo + benches + paths + lamp posts + dock + rowboat |
| Castle in the sky | Floating rocky island with hanging roots + multi-tower castle with flying buttresses + banners + airship + clouds + crystal at the underside |
| Customer support | Ticket-roll dispenser + headset + queue line of envelopes + bell on counter |
| Financial close | Vault door + ledger book stand + abacus + calculator tape + coin stacks |
| Onboarding | Welcome desk + kiosk + red carpet + swag boxes + door with tiny figure stepping through |
| Lighthouse at dusk | Rocky cliff + tall lighthouse + lantern beam + waves at the base + a single boat |

If the user names a theme not in the table, **invent the archetype**. The rule is always: the silhouette must read as the theme to a viewer who can't see any labels.

## Customisable axes

### Axis 1 — Palette (4 colour roles within one hue family)

| Role | Function |
|---|---|
| `BG` | Saturated mid-tone, fills the whole canvas |
| `BODY` | Deeper shade — main structural elements (stone, metal, wood) |
| `FOLIAGE` / secondary | Mid-shade for plants or secondary structures (optional, used in plant-heavy scenes) |
| `ACCENT` | Warm complement (cream / butter / sunflower / yellow) — small elements, fabrics, fixtures, lit windows |
| `PAPER` | White — highlights, water, small details, cloud-puffs |

**Presets:**

| Name | BG | BODY | FOLIAGE | ACCENT |
|---|---|---|---|---|
| green | `#5BD43A` grass | `#1F5C2E` forest | — | `#F4C430` sunflower |
| blue | `#3A7BD5` cobalt | `#1B3B7A` navy | — | `#F4C430` sunflower |
| coral | `#F4A0B0` dusty pink | `#7A2E4E` berry | `#C76B89` mauve | `#F5E4C8` cream |
| yellow | `#F2C94C` mustard | `#8B5A2B` cinnamon | `#9E8C2F` olive | `#F8EDB5` cream |
| terracotta | `#D27D4A` clay | `#5C2A14` dark brown | — | `#F5E4C8` cream |
| lavender | `#C7A7E0` lavender | `#4A2B5C` aubergine | — | `#F4E4B8` butter |
| mint | `#A8E0C8` mint | `#1E5C50` teal | — | `#F4B58A` peach |
| sunset | `#F2A07B` peach | `#8C3A2A` brick | — | `#F5E4C8` cream |
| sky | `#A8D0F2` sky-blue | `#2B4A7A` steel-navy | — | `#F8EDB5` cream |

The user may also supply a custom triplet: `palette=#xxxxxx/#xxxxxx/#xxxxxx`.

### Axis 2 — Scene archetype

User-supplied theme (see catalog above). Resolve to a list of theme-native props, materials, and a small figure or two when the scene calls for it.

### Axis 3 — Complexity

| Level | Element count | Description |
|---|---|---|
| **L1 Minimal** | 4–6 visible elements | One central object + 1–2 supporting props |
| **L2 Standard** *(default)* | 8–12 elements | Central object + supporting props + small figure + atmospheric details (clouds, birds, small flora) |
| **L3 Rich** | 15+ elements | Populated scene with multiple sub-vignettes, multiple figures, hovering airships or clouds, ambient props |

### Axis 4 — Optional modules (silhouette variety)

For machine-style themes especially, pick 2–4 extra modules so the outline is varied and asymmetric, never a plain rectangle:
- Mechanical: gears, pipes, conveyor belt, crane-arm, lever, pressure-gauge
- Atmospheric: smokestack with paper-puff smoke, steam-vent, antenna/dish, signal-light bulb
- Structural: wheels, tripod legs, side ladder, scaffolding, periscope, fuel tank
- Human-scale: tiny operator figure, gardener, hard-hat worker, traveller
- Aerial: hovering airship, floating crystal, dangling root cluster, cloud-puffs

## Reusable prompt template

```
Isometric editorial vector illustration of a stylized miniature {SCENE_NAME} — a small, self-contained scene as a single composed object.

BACKGROUND — CRITICAL: The ENTIRE canvas, edge to edge, is filled with one solid flat saturated {BG_NAME} ({BG_HEX}). No white. No transparent areas. The {BG_NAME} IS the canvas. The scene sits centred with generous {BG_NAME} negative space around it.

LINE STYLE: All outlines are ULTRA-FINE, delicate, wispy hairline strokes — 0.5pt ink pen weight, uniform line weight throughout, no variation, NEVER bold strokes. Refined architectural-drawing feel — colours do the heavy lifting, lines are structural guides only.

COLOUR & FILL: Flat colour fills, no gradients. Strictly {HUE_FAMILY}-family palette:
- Canvas background: saturated {BG_NAME} ({BG_HEX}) covering the WHOLE image
- Main structural body: {BODY_NAME} ({BODY_HEX})
- Foliage / secondary structures: {FOLIAGE_NAME} ({FOLIAGE_HEX}) [if applicable]
- Accent surfaces: {ACCENT_NAME} ({ACCENT_HEX})
- Highlights (water, clouds, small details): white
Editorial magazine-print quality, sophisticated and dusty — NOT neon, NOT saccharine, NOT cartoon. Monocle / Kinfolk / Wes Anderson.

COMPOSITION: 3D isometric perspective, centred, with the saturated {BG_NAME} filling every corner of the canvas.

The scene contains:
{SCENE_PROPS_LIST — 4–15 props with materials and colours, drawn from the theme itself, never relabelled-folder-tabs}

Soft drop-shadow on the {BG_NAME} ground beneath the scene. No background scenery beyond the flat {BG_NAME} fill. No text. No filing drawers, no megaphone funnels, no labelled folder tabs (unless the scene IS literally about filing or broadcasting). Editorial magazine illustration aesthetic — Monocle / Kinfolk / New Yorker spot-illustration sensibility, ultra-fine linework.
```

## Generation notes

- **Model recommendation:** a high-fidelity text-to-image model with strong long-prompt adherence (gpt-image-2 is the current best for this style — supersedes gpt-image-1.5 with stronger long-prompt adherence and cleaner flat-vector output). Image-to-image is not required — the locked style is fully describable in text.
- **Output:** 1024×1024 PNG, high quality
- **Cost / determinism:** since this is text-to-image, output varies slightly between runs even with the same prompt. For exact reproductions, pin a seed if the underlying model supports it.

## Failure modes and how to recover

| Failure | Symptom | Fix |
|---|---|---|
| Background dropped to white | Scene floats on white instead of the BG colour | Re-prompt with `BACKGROUND — CRITICAL: …` capitalised, repeat hex 2–3×, mention "fills edge to edge" |
| Linework too bold | Looks like a poster / sticker | Re-prompt emphasising "ultra-fine", "0.5pt ink pen", "colours do the heavy lifting" |
| Generic filing-cabinet shape | Output looks like the accounting-machine reference with relabelled tabs | Explicitly forbid "filing drawer", "folder tabs", "megaphone funnel"; describe the theme-native silhouette concretely |
| Saccharine / neon palette | Output reads cartoon | Add "sophisticated, dusty, NOT neon, NOT saccharine, Wes Anderson palette" |
| Foliage reads as a different hue family | E.g. green leaves in a pink scene | Specify the foliage hex explicitly within the monochromatic family |

## Reference outputs

The four images below are user-approved generations that anchor the style:

| File | Palette | Scene |
|---|---|---|
| `references/sky-castle.png` | `sky` | Floating rocky island + multi-tower castle ruin + airship + clouds + crystal |
| `references/coral-hanging-garden.png` | `coral` | Three-tiered terraced garden tower + cascading vines + gazebo + fountain + gardener |
| `references/yellow-floating-island-park.png` | `yellow` | Floating island park + gazebo + benches + lamp posts + dock + rowboat + visitors |
| `references/blue-city-construction.png` | `blue` | Half-built skyscraper + crane + cement mixer + scaffold + drafting board + hard-hat figure |

Use these as the canonical look. New scenes should match their linework weight, background saturation, and "scene-as-metaphor" composition.
