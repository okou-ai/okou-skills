---
name: illustration-reverse-template
description: "Reverse a reference picture into a style prompt, show the user pictures made from it, revise until they approve, then save it as their template. Use when a user uploads an image style to reuse, asks to extract a prompt from a picture, wants their own image template, or asks for more images in the style of a picture they supplied."
---

# Turn a reference picture into the user's own style

Input: images of one style, or a brief when no reference exists. Output: a
style prompt the user has approved, saved as their template.

No reversal is complete. Measurement settles canvas, ground, palette, stroke,
coverage and placement. Medium, drawing and subject convention are read by eye
and are partly wrong on the first pass. The user closes that gap by looking at
pictures, so the path is: reverse, show, revise, save.

Choose among your own candidates without asking — the gate ranks them. Stop
before saving, always: never save a prompt the user has not seen pictures from.

Run every command below from `reverse-template/illustration/`.

## Before anything — a style, or this one picture?

A style makes new pictures: another subject, another scene, the same look. A
picture is one arrangement the user wants back.

For one picture, write the prompt that recreates it and stop. Continue here
only for a style.

## Prerequisites

```bash
python3 -c "import pymupdf"     # else: pip install pymupdf
```

## Steps

### 1. Collect the references

Download every `[Web file]` with `okou web download-file`. Keep PNG or JPEG.

With no reference at all, ask for the intended use, which decides the canvas,
then write the frame from the brief and go to step 4. Steps 2 and 3 need pixels.

Three or more references separate a locked axis from a dial. With one, ask for
more; if none arrive, record in `design-system.md` which axes stay unsettled
and give them no range.

Ask for files at least 400px on the short side. Below that the palette fills
with anti-alias blends and the stroke is one pixel wide, so colour and line
describe the downscaling.

### 2. Measure

```bash
python3 scripts/measure_style.py <ref> [<ref> ...] --json style.json
```

Take these numbers over your own reading of the image. The verdict column
decides where each axis goes:

| Verdict | Where it goes |
|---|---|
| `CONSTANT` | the locked frame, as a value |
| `RANGE` | the locked frame, as a range |
| `VARIES` | a dial |

The shared-colour line is the locked palette; every other colour is a palette
dial.

### 3. Read what the numbers cannot reach

Keep two records apart:

- **content** — subject, action, props, setting, placement;
- **style** — how it is drawn, carrying no content noun.

Then delete every subject, object, place and name from the style record. What
remains must still describe a way of drawing; move anything else back to
content.

Write every style line as a drawing instruction that names the near miss it
excludes. A line that only names the family collapses into the nearest common
style — flat vector, cel anime, stock watercolour — whatever the reference
actually was.

| Instead of | Write |
|---|---|
| flat gouache shapes | paint varies in value inside every shape, never a flat digital fill |
| thin dark contour | shapes meet at their colour edges, no outline; only the eyes and leaf veins carry a drawn line |
| botanical motifs | each sprig painted with its own texture and veins, not a single-colour silhouette |
| soft watercolour | wet washes that bloom and granulate; almost nothing in the picture is a flat area |
| closed eyes | heavy lids as grey-shadowed lens shapes under one fine dark line |

State the style under these heads, from the references only:

| Head | State |
|---|---|
| Medium | painted, inked, vector, 3D, collage, print, photographic, mixed |
| Line | the measurement's contour verdict first, then closed or open, uniform or tapered, cap shape |
| Shape | rounded or angular, geometric or organic, how forms simplify |
| Value | flat fill, cel steps and how many, gradient modelling, hatching, wash |
| Colour | what the lead, support and accent each do |
| Texture | brush, grain, paper, halftone, noise — and where it sits |
| Detail | which areas carry detail, which stay plain |
| Light | direction, rim, glow, haze, or no light description at all |
| Composition | crop, weight, repeated shapes, the rhythm every reference keeps |
| Frame | how the art meets the canvas: edge to edge, a vignette, or a visible margin — and how wide |
| Finish | grade, bloom, chromatic shift, fade, print registration |
| Subject convention | face treatment, cast, count, scale, what the subject does |

### 4. Write the style prompt

Write the prompt first; it is the deliverable. Its first third carries the
locked frame, then the subject, then the dials, then what must not appear.

Keep these behind it, and write them into files only when the user asks for a
template:

- **Locked frame** — one line per axis, measured values included. State the
  contour width in pixels at the canvas the package delivers, not only as a
  percentage: the references are rarely that size. State how much of the sheet
  the art covers and whether the ground stays unpainted — without it the model
  floods the sheet and the paper stops being a colour.
- **Dials** — one line per axis, with the values the references used.
- **Not in the frame** — techniques absent from every reference.
- **Prompt template** — one prompt with a placeholder per dial, opening on the
  locked frame.
- **References** — one line per file naming the dial values it demonstrates.

`design-system.md` carries the measurement table per reference, the verdict
table, and the axes a single reference could not settle.

Write the prompt template so the locked frame occupies its first third.

### 5. Generate, measure, choose

```bash
npx --yes --package="${CLI_PKG_URL}" okou generate image --provider built-in \
  --raw-prompt "<the style prompt, dials filled in>"
python3 scripts/check_piece.py --refs <ref> [<ref> ...] --piece <generated> [...]
```

Generate three at a time — that is the ceiling on generations in flight —
each on a subject the references do not carry. Keep the ones with the fewest
axes outside range.

Read the failing axes: they name what the prompt did not hold. Correct the
prompt and generate again.

Some axes never come back from the prompt. When two rounds do not move one,
stop rewriting and fix it after the fact where that is possible. Scale and
placement on a plain ground is the common one:

```bash
python3 scripts/compose.py --ref <reference> --piece <generated> --out <placed>
```

It scales the drawing's ink box to the fractions the reference measures and
places it at the reference's margins, touching nothing inside the drawing.

Show only pieces the gate passes, or say which axes still fail and why the
prompt could not hold them.

The check cannot see medium, line quality, shape language, subject conventions,
motif or composition. Look at the kept piece for those before delivering.

### 6. Show the set and ask what to change

Put in the reply:

- the pictures as markdown images, one line of subject under each;
- the style prompt in a fenced block, `{PLACEHOLDER}` for every dial;
- the axes that still fail, one line each, in plain words.

Then ask one question: what should change. Name two or three things you already
suspect are off, drawn from the failing axes and from what you see, so there is
something to react to instead of a blank prompt. Three is the ceiling; a list
longer than that reads as a survey.

Stop there. Do not save anything yet.

### 7. Revise, then show again

The user speaks about the look — the lines are too heavy, it is too colourful,
the faces are wrong. Turn each correction into one line of the locked frame
that names the near miss it excludes, the same form as step 3. Nothing else in
the prompt changes.

Regenerate the set with step 5 and show it again. One round of corrections at a
time; do not bundle two rounds into one reply.

Repeat until the user says it is right.

### 8. Save it as the user's template

Only after the user approves.

`okou user-template publish` takes `presentation` and `document` only:
`USER_TEMPLATE_KINDS` has no image kind, and passing an image fails. Until it
does, save the approved prompt as a workflow the user can call by name:

```bash
mkdir -p <slug> && cp <approved-prompt>.md <slug>/SKILL.md
npx --yes --package="${CLI_PKG_URL}" okou workflow create <slug> --dir <slug>/ \
  --display-name "<Display Name>" --description "<one line, with the trigger phrases>"
```

`<slug>/SKILL.md` carries frontmatter (`name`, `description` with the phrases
that should trigger it), the locked frame, the dials, the prompt with its
placeholders, and the approved pictures as references.

Register it as a selectable style only when the user asks: the resource goes to
`illustration-template/<slug>/` in `vm0-ai/vm0-skills`, its entry to the Open
Design registry in `vm0-ai/okou` as `vm0:image-style:<slug>`, and each pull
request links the other.

## Rules

- Reproduce the references. Do not correct a palette, a proportion or a
  stroke you would have drawn differently.
- Present in every reference is locked; present in one is a dial; with a
  single reference, neither — say so rather than guessing.
- A technique absent from every reference is part of the locked frame. A
  subject or content type absent from them is not a rule.
- Name observable technique, never an artist, studio, brand or product.
- Numbers in the package come from step 2, not from reading the image.
- Step 5 is mandatory. Show pictures you generated, never only a prompt.
- Choose among your own candidates yourself. Do not hand the user a menu of
  variations.
- Step 6 stops. Saving before the user has seen pictures and approved them is
  the one thing this skill must never do.
- A correction from the user is one more line in the locked frame, not a
  rewrite of the prompt.
- Rotate the cast and the scene across a series. A locked frame is not a
  locked mascot.

## Troubleshooting

| Symptom | Action |
|---|---|
| Generated pieces repeat the reference's subject | The subject leaked into the style record; run the deletion test in step 3 again and rewrite the prompt template |
| `check_piece.py` fails on line width | Step 2's measurement, not your estimate, goes in the package |
| Generated pieces carry outlines the reference has none of | The measurement said `NO drawn contour`; remove every outline word from the prompt and say shapes meet at their colour edges |
| A generated piece mounts the art inside a paper border | The Frame line is missing or too weak; say the paint reaches all four edges |
| Generated pieces read as flat vector against a painted reference | Flatness under about 60% means paint varies inside each shape; say so, and name what must not be flat |
| Every generated piece looks the same | Too few dials, or the prompt template has no placeholders |
| A colour appears that no reference uses | The palette dial has no list of allowed values |
| Generated pieces flood the whole canvas | The locked frame is missing the ink coverage and the unpainted ground; "vignette" alone does not hold |
| The medium drifts to pencil or crayon | Name the wet behaviour — washes pooling at the stroke edges — and name the media to avoid |
| A generated piece renders on a black ground | It is RGBA with a transparent ground; the scripts composite over white, and so must anything you hand the user |
| The drawing fills the frame however the prompt words it | Two rounds is enough; place it with `compose.py` |
| The check passes but the piece looks wrong | Medium, shape language or subject convention is missing from the locked frame |
| `LOW RES` in the measurement | Ask for a larger file. Keep aspect, ground colour, ink coverage and centring; leave colour and stroke out of the locked frame |
| Background reads as `textured` on a flat style | The reference is a JPEG; re-export as PNG or accept the grain figure it reports |
| One reference only | Record the unsettled axes; do not write ranges you cannot support |
| The user approves without comment on the first showing | Save it. Do not invite more rounds |
| The user's correction contradicts the reference | Follow the user. Note in the saved file which axis now departs from the reference |
| Two corrections arrive at once | Fold both into the locked frame, regenerate once, show once |
