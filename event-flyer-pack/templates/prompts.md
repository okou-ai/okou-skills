# Event asset prompts

Choose the required template, replace the braced fields with user-approved copy, and remove empty optional lines. The visual structure is adapted from event-flyer-pack in razbakov/skills. The user's current brand requirements take precedence. By default, inspect the restored style-reference.png using the preparation steps in SKILL.md; do not copy its demo event details.

## Common composition constraints

Use the approved event copy verbatim. Let the final designed artwork fill the canvas edge to edge; not a photograph of a poster, not a mockup. Create a coherent editorial hierarchy: very large expressive high-contrast serif display title, readable sans-serif event details, optional small italic serif tagline. Use a dark atmospheric scene with controlled light and a dark vignette behind text. Default palette, unless overridden: cobalt #2456FF, warm cream #F7F2E8 and charcoal #181818; at most a small lime #DFFF70 accent. Do not add text, sponsors, logos, watermarks, QR patterns, fake scan labels, UI chrome or hands holding phones. Preserve exactly the specified language, punctuation, event facts and line breaks where feasible. Keep all copy outside the QR square.

**QR PLACEHOLDER — CRITICAL:** At the specified position, render a SOLID PURE-WHITE SQUARE with hard straight edges. LEAVE IT COMPLETELY EMPTY: no modules, dots, patterns, pixels, lettering, outlines, shadows or rounded corners. A real QR will be composited there later. Reserve its full area before placing the copy.

## 1. Flyer front

```text
Create a portrait event flyer for "{title}".
Target canvas/aspect: {canvas_and_aspect}. For A6 use approximately 105:148, not 2:3; for a digital-only flyer follow the user's exact requested format.
Aesthetic: {aesthetic}. Scene: {scene_description}.

Render only this exact copy:
- Small letter-spaced eyebrow: "{eyebrow}"
- Dominant serif title: "{title_line_1}" / "{title_line_2}"
- Optional italic tagline: "{tagline}"
- Medium-size date: "{date_display}"
- Clear time / timezone: "{time_display}"
- Venue / city: "{venue_display}"
- Optional program: "{program}"
- Entry and CTA: "{entry_and_cta}"
- Optional readable event URL: "{display_url}"

Apply all common composition constraints above.
QR placeholder: bottom-center; its bottom sits 8% of canvas height above the bottom edge. Square side = 22% of canvas width; for A6 aim for 23–26 mm including the quiet-zone card. Keep the entire square and nearby copy safely inside the canvas.
```

## 2. Flyer back

```text
Create the portrait BACK for "{title}", matching the approved front's typography, color palette and atmosphere. Target {canvas_and_aspect}. Use a calmer dark tonal field rather than repeating a busy hero scene. Do not revert to an unrelated template palette.

Exact copy:
- Small eyebrow: "{eyebrow}"
- Large serif title: "{title}"
- Date: "{date_display}"
- Time / timezone: "{time_display}"
- Venue / entry: "{venue_display} · {entry}"
- Program label in event language: "{program_label}"
- Program: "{program}"
- Optional highlights: "{highlights}"
- CTA: "{cta}"
- Optional readable URL: "{display_url}"

Apply all common composition constraints above.
QR placeholder: bottom-center, bottom 8% above the bottom edge, side 22–25% of canvas width. Keep it empty and pure white.
```

## 3. Tent card half — generate two independent upright panels

```text
Create ONE upright portrait tent-card panel for "{title}", target A6 105:148. This is one of two halves: {panel_variant}; keep both halves in the same visual language. Do not draw a folded mockup, rotate text, or generate both halves in one image. The halves will be physically composed later.
Use large readable typography intended for a table display.

Exact copy:
- Event / optional host: "{title_or_host}"
- Optional program: "{program}"
- Date: "{date_display}"
- Time: "{time_display}"
- Venue / entry: "{venue_display} · {entry}"
- CTA: "{cta}"

Apply all common composition constraints above.
QR placeholder: bottom-center; bottom 6% above the panel bottom; side 26–30% of panel width (aim for at least 27 mm including quiet zone at final print size). Keep it empty and pure white.
```

Overlay and verify each upright half first. Rotate the complete top half by 180°, then stack above the second upright half with formats.py; never horizontally mirror letters.

## 4. Story

```text
Create a 9:16 portrait Story for "{title}", final delivery 1080×1920. Match the approved flyer typography, palette and atmosphere. Use dark tonal areas behind text without obscuring the hero image.

Exact copy:
- Large serif title in the upper-middle area: "{title_line_1}" / "{title_line_2}"
- Date and time: "{date_display} · {time_display}"
- Venue / entry: "{venue_display} · {entry}"
- CTA above QR: "{cta}"

Apply all common composition constraints above.
Keep essential text out of the top 250 px and bottom 250 px reserved for app overlays. QR placeholder: bottom-center, 300 px above the bottom edge, a solid pure-white 300×300 px square; it must not touch the CTA. If generating at another 9:16 resolution, scale these positions proportionally.
No fake platform UI, link stickers, swipe-up arrows, handles or unrequested text.
```

## Optional second version

Change only one axis, such as warm/cool lighting, tight/wide framing, or type weight/artwork balance. Keep all event facts, palette, and QR-placeholder constraints unchanged. Do not automatically generate two versions of every asset without a request.
