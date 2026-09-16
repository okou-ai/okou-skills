---
name: folk-muse
description: Flat folk-art gouache portrait illustration in the contemporary editorial style of Carson Ellis, Maja Tomljanovic, and Bodil Jane. A single chest-up figure with an elongated mannerist oval face, tiny almond half-lidded eyes, smooth flat hair, one hand pressed against the face, a patterned robe filling the lower frame, and an asymmetric botanical surround filling the background edge-to-edge. Hand-painted matte gouache texture, flat color blocks, no harsh outlines, no photorealism. Calm, slightly melancholic, contemplative mood. Trigger when the user says /folk-muse, asks for a "folk-art portrait", "gouache portrait", "Carson Ellis style portrait", or any new piece in this contemplative folk-portrait style.
---

# /folk-muse — locked folk-art gouache portrait style

This skill produces a single-figure folk-art gouache portrait — a contemplative person framed by an asymmetric botanical surround, painted in flat hand-painted gouache. The locked style is what makes every output read as "the same illustrator's hand." Only the six creative dials below should vary between pieces.

See `ref-canonical.png` (hero), `ref-tropical-butterfly.png`, `ref-winter-cat.png`, and `ref-sunset-dove.png` for the visual target. Match the style of those references exactly; do not borrow from any other portrait reference you may have seen.

## How to use this skill

The user provides a brief that names some or all of the six creative dials. Your job:

1. Fill in any dial the user did not specify by picking a tasteful, coherent choice — palette and botanicals should feel like the same season; companion is optional and should be omitted unless the brief invites it.
2. Compose a prompt from the **Style brief structure** below, with the locked axes preserved verbatim and the six dial fields filled in.
3. Generate at portrait aspect ratio (recommended 1024×1536) with the style-bypass mode of the image model, so the model honors the locked style brief rather than overlaying a host style.
4. Inspect the output against the **Quality checks** list before returning it.

If the brief is empty, default to the canonical reference: young woman, warm olive skin, dark chestnut side-parted hair, hand pressed against cheek, terracotta-rust robe with hand-painted yellow quinces and dark-green leaves, dusty powder-blue background with mustard goldenrod + dark sage olive branches + cream magnolia + scattered coral buds.

## Locked style axes (NEVER vary)

### Medium and surface
- **Flat folk-art gouache** with hand-painted matte texture. Soft visible brushwork, faint paper grain.
- **Flat opaque color blocks** — no airbrush gradients, no photorealistic skin modeling, no 3D rendering, no shading inside shapes beyond the gentlest tone shift on the face and hand.
- **No harsh outlines.** Forms are defined by adjacent color blocks, not by inked contours. Edges are soft-painted.

### Composition
- **Single figure**, chest-up, **three-quarter view** facing slightly toward the viewer.
- Head positioned roughly in the upper-center, hair flowing down to chest, robe filling the lower portion of the canvas, botanical surround filling every remaining inch of background edge-to-edge.
- **Portrait orientation** (recommended 1024×1536).

### Face
- **Elongated narrow mannerist oval face** — long, NOT round, NOT cherubic, NOT chibi.
- **Tiny almond-shaped half-lidded eyes** with **painted irises** (small, sleepy, calm gaze). NOT cartoon dot pupils. NOT big anime/Pixar eyes. NOT closed-eye smile arcs.
- **Single soft curved line** suggesting the nose — almost no protrusion, no triangular nostrils.
- **Small painted lips** in a muted brick-red or terracotta — closed or with the faintest smile.
- **A small soft pink blush dot** on each cheek. Optional faint pink at the tip of the nose.
- Subtle hand-painted tone shift on the face for soft volume; never photorealistic shading.

### Hair
- **Smooth, flat solid color shape.** Side-parted, falling past the shoulders unless the dial specifies short hair.
- Hand-painted texture marks may suggest curl or wave, but the silhouette is a single flat color block.
- No rendered strands, no airbrushed highlights.

### Hand and gesture
- **One simplified elongated hand** visible against the face or near it, long fingers, flat color, gentle tone shift only.
- Default pose: **palm pressed against the cheek**, head softly tilted into it. Alternate poses are dial-driven (see Pose dial below).

### Robe
- The robe fills the lower portion of the canvas.
- Base color is a flat opaque block.
- The robe **must carry a clear repeating hand-painted pattern** — a textile motif scattered as a regular all-over print. Without the patterned robe, the piece reads as a generic portrait and loses the folk-art signature.
- Collar is a simple V or band in a complementary contrast color.

### Background
- **Flat opaque background color** filling edge-to-edge.
- **Loose asymmetric botanical surround** in stylized flat shapes — never a symmetric wreath, never a centered halo. Heavier on one side than the other; stems and leaves emerge from the edges and arch around the figure.
- The botanicals should feel **plant-illustrated**, not photographic — large simplified flowers, leaves drawn as flat color shapes, occasional small berries or buds.

### Mood
- **Calm, slightly melancholic, contemplative.** Adult editorial, not a children's book illustration.
- No grins, no comedy, no action. The figure is present and still.

### Style anchors
Carson Ellis, Maja Tomljanovic, Bodil Jane. Use these names in the prompt to anchor the style.

## Six creative dials (user-controlled)

### 1. Palette
The overall color story. Named palettes that work well in this style:

- **Sage Citrus** (canonical reference): sage-green background, dusty pink florals, deep teal leaves, lemon yellow accents
- **Powder Quince** (canonical hero): dusty powder-blue background, terracotta-rust robe, cream magnolia, mustard goldenrod, dark sage olive
- **Tropical Lush**: dusty turquoise background, coral hibiscus, dark green monstera, dark teal robe with cream and gold
- **Cool Winter**: dusty slate-blue background, dusty rose robe, silver-sage leaves, pale gold and cream accents
- **Sunset Warm**: warm dusty peach background, magenta bougainvillea, dark green olive, cream robe with coral motif and a cobalt collar accent
- **Forest Folk**: deep sage background, ochre + rust robe, cream daisies, dark forest leaves
- **Dusk Plum**: dusty mauve background, deep mustard robe, soft lavender florals, sage leaves
- **Custom**: any tasteful muted, dusty, restrained European folk-art palette. Avoid candy-bright saturation. Avoid neon.

### 2. Character
Age, gender, skin tone, hair color and length. Examples:

- Young woman, warm olive skin, long dark chestnut hair, side-parted
- Young woman, deep brown skin, long curly black hair piled over the shoulders
- Mature woman, pale matte skin with the gentlest hint of age lines, long silver-streaked black hair
- Young man, warm tan skin, short tousled wavy black hair, light stubble
- Young man, pale matte skin, chin-length straight auburn hair
- Older man, warm olive skin, salt-and-pepper short curls, soft beard
- Child or teen, any skin tone, simple short hair

Always: elongated face, painted irises, tiny almond half-lidded eyes, single nose line, small painted lips, pink blush dot. The locked face style applies across age and gender.

### 3. Pose / hand placement
Where the hand is and whether the figure holds something.

- **Hand on cheek** (default, canonical) — palm pressed against the face, head softly tilted
- **Hand near lips** — fingertips brushing the lower lip in a quiet pause
- **Both hands cupped at chest** — holding a small held object (a bird, a candle, a single flower, a small bowl, a teacup)
- **Both hands clasped low** — visible at the lower frame, fingers gently interlocked
- **One hand to the temple** — pressing the side of the head, slightly weary
- **One hand resting on a companion** — gentle touch on the head or back of a small creature on the shoulder

### 4. Robe motif
The repeating hand-painted pattern on the robe. Pick one motif + decide the base color. The motif must be clear and repeated as a regular textile print.

- **Fruit**: lemons, quinces, pomegranates, figs, cherries, pears, grapes, oranges, plums — each fruit drawn with a few simple leaves
- **Florals**: small daisies, poppies, roses, tulips, forget-me-nots, magnolias, wildflowers
- **Botanical**: ferns, leaves, vines, olive branches, eucalyptus sprigs, herb sprigs
- **Celestial**: small stars, crescent moons, scattered dots, sunbursts
- **Abstract**: paisley, simple geometric tiles, stripes, polka dots, scattered crosses
- **Tiny creatures**: small birds, fish, butterflies, moths (rare — use only if the companion dial is set to none)

### 5. Surrounding botanicals
The asymmetric flora that fills the background. Pick 3-5 distinct plant types that share a season or biome with the palette. Examples:

- **Sage Citrus**: dusty-pink star florals, lemon clusters, dark teal leaves, small red berry sprigs
- **Powder Quince**: mustard goldenrod stems, dark sage olive branches with silvery olives, cream magnolia blossoms, scattered coral buds
- **Tropical Lush**: coral hibiscus, dark green monstera leaves, orange birds-of-paradise, small pineapples, gold plumeria
- **Cool Winter**: dark pine branches with tiny white blossoms, dried pale-gold wheat stalks, cream poinsettia with red centers, silver-sage leaves
- **Sunset Warm**: magenta bougainvillea, dark sage olive with silver olives, hanging terracotta figs, small cream blossoms
- **Forest Folk**: tall mullein stems, fern fronds, cream daisies, foxglove, dark moss
- **Dusk Plum**: lavender stems, sage rosemary, plum blossoms, small cream wildflowers

Layout rule: **heavier on one side, sparser on the other.** Stems should appear to grow from the edges of the canvas, arching around the figure.

### 6. Companion creature (optional)
A small creature integrated into the figure or the surrounding flora. Most pieces work beautifully without one. Use sparingly.

- A small bird perched on the figure's hand, shoulder, or among the flora
- A black cat curled on the shoulder
- A butterfly resting on a fingertip
- A small fish in a held bowl
- A snake or lizard winding through a sleeve
- A moth on a flower
- A small fox or hare among the lower botanicals

If used, the companion should be drawn in the same flat painted style — small, simple, integrated into the composition rather than starring in it.

## Style brief structure (fill the bracketed fields, keep everything else verbatim)

```
Flat folk-art gouache portrait illustration, hand-painted matte texture, FLAT color blocks with minimal shading, naive simplified forms. Adult editorial style — NOT a children's book illustration.

[CHARACTER: age + gender + skin tone] with a soft pink blush dot on each cheek, three-quarter view from chest up. Elongated narrow mannerist oval face — long, NOT round, NOT cherubic. Tiny almond half-lidded eyes with painted [EYE COLOR] irises (sleepy, calm gaze, NOT cartoon dot pupils, NOT big anime eyes). Single soft curved nose line. Small painted muted-red lips. [HAIR: length + color + texture, side-parted unless specified] as a flat solid color shape. [POSE: hand placement + optional held object, drawn with elongated simplified fingers and flat color].

The robe fills the lower portion of the canvas, base color [ROBE BASE COLOR] with a [CONTRAST] collar band, carrying a CLEAR REPEATING HAND-PAINTED PATTERN of [ROBE MOTIF] scattered as a regular all-over textile motif.

Background filled edge-to-edge with a flat [BACKGROUND BASE COLOR] base and a LOOSE ASYMMETRIC botanical surround in stylized flat shapes — heavier on the right, sparser on the left (or vice versa): [BOTANICALS — list 3-5 plant types with their colors].

[OPTIONAL COMPANION — describe the small creature and where it sits; OMIT this line if no companion].

Style anchors: Carson Ellis, Maja Tomljanovic, Bodil Jane. Flat opaque gouache color blocks, soft matte texture, no harsh outlines, no airbrush gradients, no photorealism, no 3D rendering. Calm, slightly melancholic, contemplative mood. No text, no logos, no watermarks. Portrait orientation 1024x1536.
```

## Recommended model

This style is now generated on **ByteDance Seedream 5** at 1024×1536 (the v5 lite endpoint on fal). Seedream's flat-painterly bias and willingness to render repeating textile motifs match this aesthetic well; v5 carries the same character anatomy + textile handling as v4 but with sharper edge fidelity.

Other models that have worked at lower fidelity: GPT-Image-2 (occasionally drifts toward cute / children's-book; counter it with stronger anti-pattern phrasing). Avoid flux for this style — it tends to render the face too photorealistically.

When invoking the model, **bypass any host or app style overlay** so the locked style brief above is what the model actually receives. Generate at a portrait aspect ratio; tighten the prompt rather than the size if the figure is being clipped.

## Quality checks (review before returning the image)

- ✅ Face is elongated and oval, NOT round or cherubic
- ✅ Eyes are small almond half-lidded with painted irises, NOT dot pupils or anime eyes
- ✅ Single curved nose line, NOT a sharp triangular nose or photographic shading
- ✅ Pink blush dot is present on the cheek
- ✅ Hair is a flat solid color block, NOT rendered with strands or highlights
- ✅ One hand is clearly visible against or near the face, with simplified elongated fingers
- ✅ Robe shows a CLEAR REPEATING PATTERN — not a solid block, not abstract noise
- ✅ Background is filled edge-to-edge with botanical surround, NOT empty
- ✅ Botanical surround is ASYMMETRIC — heavier on one side, NOT a centered wreath
- ✅ Palette is muted, dusty, restrained — NOT candy-bright, NOT neon
- ✅ Image reads as adult editorial gouache, NOT a children's book
- ✅ No text, logos, watermarks, or signature glyphs

If any of these fail, re-prompt with stronger emphasis on the failed axis (move the failed item earlier in the prompt, and add a specific anti-pattern instruction) rather than regenerating with the same prompt.

## Anti-patterns to actively avoid

- Big round Pixar/Disney eyes — these are NEVER correct for this style
- Symmetric floral wreath surrounding the head — the surround must be asymmetric
- Solid unpatterned robe — the robe must always carry a clear repeating motif
- Photorealistic skin modeling or 3D-rendered face — keep it flat painted
- Saturated candy colors — keep the palette muted, dusty, restrained
- Cluttered foreground props or held objects competing with the figure — companions stay small and integrated
- Two or more figures sharing the frame — this style is a portrait, single-figure only

## Example briefs and resulting prompts

### Example A — Canonical (Powder Quince)
**Brief:** Default / canonical hero.
**Filled:**
- Character: young woman, warm olive skin, long dark chestnut hair side-parted
- Eye color: soft hazel
- Pose: one slim hand pressed against her cheek, head softly tilted
- Robe: deep terracotta-rust base with cream collar, repeating yellow-quince and dark-green-leaf pattern
- Background: dusty powder-blue base
- Botanicals: tall mustard goldenrod stems, dark forest-green olive branches with silvery-sage olives, large cream-white magnolia blossoms with apricot centers, scattered tiny coral buds
- Companion: none

### Example B — Tropical Lush / butterfly
**Brief:** "tropical, young woman with butterfly"
**Filled:**
- Character: young woman, deep brown skin, long curly black hair piled over her shoulders
- Eye color: warm amber
- Pose: one elongated hand raised near her cheek, with a yellow butterfly resting on her index finger
- Robe: dark teal base with cobalt collar, repeating cream-ivory fern fronds and small gold dots
- Background: dusty turquoise
- Botanicals: large coral hibiscus with yellow centers, dark green monstera leaves, tall stems of orange birds-of-paradise, small painted pineapples, scattered gold-yellow plumeria
- Companion: yellow butterfly (in pose)

### Example C — Cool Winter / older woman with cat
**Brief:** "winter, older woman, cat companion, star pattern robe"
**Filled:**
- Character: mature woman, pale matte skin with gentle hint of age lines, long silver-streaked black hair side-parted
- Eye color: soft slate-grey
- Pose: one slim hand resting gently on the head of a small black cat curled at her shoulder
- Robe: dusty rose base with cream collar, repeating muted-gold five-point stars + ivory crescent moons + scattered ivory dots
- Background: dusty slate-blue
- Botanicals: dark green pine branches with tiny white blossoms, dried pale-gold wheat stalks, cream-white poinsettia blooms with deep red centers, scattered silvery-sage leaves
- Companion: small black cat curled at her shoulder, tiny gold dot eyes, tiny pink nose

### Example D — Sunset Warm / young man with dove
**Brief:** "warm sunset palette, young man holding a dove, pomegranate robe"
**Filled:**
- Character: young man, warm tan skin, short tousled wavy black hair, light stubble shadow on his jaw
- Eye color: deep brown
- Pose: both simplified elongated hands cupped together at his chest, holding a small cream-white dove with a tiny soft-pink beak
- Robe: dusty cream-ivory base with cobalt-blue collar band, repeating dark-coral pomegranates and dark-forest-green leaves
- Background: warm dusty peach
- Botanicals: tall magenta bougainvillea stems, dark forest-green olive branches with silvery-sage olives, hanging terracotta figs, scattered small cream blossoms
- Companion: the dove (in pose)
