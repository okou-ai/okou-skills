---
name: vm0-illustration
description: "Generate vm0-style vm0 in-app spot illustrations: bold hand-drawn ink line art with white-filled interiors, a soft rounded color backdrop, transparent output, and simple iconic metaphors for product states."
---

# vm0 Illustration

Use this register-only image style when the user asks for a vm0 in-app spot illustration, empty-state artwork, billing/permission/error state artwork, or a small product UI illustration in the vm0 style.

This style is separate from Notion Illustration. Notion Illustration is black brush-pen editorial character artwork on pure white. vm0 Illustration is a vm0 product illustration style built around a single iconic object or metaphor, white-filled line art, and one soft color backdrop.

## Locked Style

- Square spot illustration, usually 1024 x 1024.
- Transparent final background in the delivered artifact.
- Preferred generation setup: generate on a flat full-canvas warm gray background (`#eeeeee`), then remove only that gray background to transparency. This preserves pure-white object interiors. Direct transparent-background generation often creates unwanted glow/vignette and gray object fills.
- One central product metaphor or object, not a character scene.
- Bold confident black brush-pen ink line drawing, with thick chunky decisive strokes and natural hand-drawn wobble. Lines should look committed and drawn once, not ruler-straight or vector-clean.
- Outlines have intentional small gaps and breaks for a breathy hand-drawn quality.
- Minimal detail: only essential contours and one or two key details. No fine textures, no crosshatching, no heavy shading.
- Pure white (`#FFFFFF`) filled interior inside the line art so the drawing stays opaque over the color shape. The interior must not be gray, dark, shaded, translucent, or blended with the backdrop.
- The black ink drawing sits firmly on top of the white fill. Where the subject overlaps the color block, the white-filled object completely hides the color underneath.
- One solid opaque flat soft-rounded color block behind the drawing, like a halo, chunky oval, generous pill, or rounded-square badge.
- The color block has no gradient, no watercolor, no texture, no glow, and no transparency. Slightly imperfect hand-drawn edges are fine.
- The color block supports the drawing; it should not fully contain it.
- The drawing extends beyond the color block on at least 2-3 sides.
- The color block occupies roughly 30-40% of the canvas and may be slightly off-center or rotated for editorial flair.
- The full composition fills roughly 60-75% of the canvas with generous breathing room around it.
- Pixels outside the line art and color block must be transparent in the final artifact. Do not add any glow, vignette, cast shadow, ambient lighting, gray paper, or background wash.
- No logo, no text, no letters, no numbers, no UI chrome, no watermark, no border, no third color.

## Color Direction

Prefer one accent color from the vm0 avatar/product palette:

- yellow: `#EDC43E`
- teal: `#3EB7B8`
- grey: `#97918A`
- pink: `#FF81B2`
- brown: `#E88033`
- wheat: `#EDC183`
- light pink: `#F3BAB1`
- sienna: `#C77242`
- peach: `#EBC2AA`

Pick one color per image. Use vibrant colors for friendly states and warmer neutral colors for permission, billing, or security states. Use pink sparingly.

## Prompt Construction

Turn the user's request into a short concrete metaphor, then generate one polished image in this style.

Good metaphors:

- no permission: a chunky padlock with a rounded shackle and keyhole, with a small key beside it
- empty schedule: a simple calendar page with one loose checkmark and a small sparkle
- empty chat: two rounded speech bubbles overlapping, one with a small sparkle
- billing plan: a small receipt or stacked card with a coin and checkmark
- product update: a gift box with lid lifting and a few sparkles
- retry/loop: two curved arrows chasing each other in a circular refresh loop

Use a concise prompt with these constraints. If the generation tool supports background removal or post-processing, prefer the warm-gray-background workflow:

```text
vm0-style vm0 in-app spot illustration of <metaphor>.
Square 1:1 spot illustration on a flat full-canvas warm gray #eeeeee background that will be removed to transparency after generation. Bold confident black brush-pen ink line art with thick chunky decisive strokes, natural hand-drawn wobble, and intentional small contour breaks. The object has an opaque pure white #FFFFFF filled interior, not gray, not dark, not shaded, and not blended with the backdrop. The white-filled object sits on top of a single solid opaque flat soft-rounded <color name> color block using <hex>, like a pill, chunky oval, or rounded-square halo. The color block has no gradient, no watercolor, no texture, no glow, and no transparency. The drawing extends beyond the color block on at least 2-3 sides and fills 60-75% of the canvas. Minimal iconic detail only. No text, no letters, no numbers, no logo, no UI, no border, no shadows, no glow, no vignette, no hatching, no third color.
```

If direct transparent-background generation is the only available path, keep the same style constraints and additionally require that all pixels outside the drawing and color block are fully transparent. Be strict about no glow/vignette and pure white subject interiors, because direct transparent generation tends to drift there.

## Evaluation Checklist

- The image reads as one simple iconic product metaphor.
- The line art is bold and hand-drawn, not vector-clean.
- The object interior is pure white-filled, not transparent, gray, dark, shaded, or backdrop-colored.
- The color block sits behind the drawing and does not trap it inside.
- The color block is solid flat color, not gradient/watercolor/textured.
- The final background is transparent.
- There is no glow, vignette, cast shadow, gray wash, or background outside the color block.
- There is no text, letters, numbers, logo, UI chrome, border, watermark, or third color.
