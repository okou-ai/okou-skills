---
name: illustration-reverse-template
description: "Reverse-engineer reference images into a loadable illustration template: SKILL.md, design-system.md and the reference art. Use when asked to reverse an image style, save a picture's look as a reusable template, build a style from reference art, or make more images in the style of an uploaded picture."
---

# Reverse reference images into an illustration template

Input: images of one style. Output: a directory holding `SKILL.md`,
`design-system.md` and the references as `ref-<subject>-<dial>.png`.

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

State the style under these heads, from the references only:

| Head | State |
|---|---|
| Medium | painted, inked, vector, 3D, collage, print, photographic, mixed |
| Line | present or absent, closed or open, uniform or tapered, cap shape |
| Shape | rounded or angular, geometric or organic, how forms simplify |
| Value | flat fill, cel steps and how many, gradient modelling, hatching, wash |
| Colour | what the lead, support and accent each do |
| Texture | brush, grain, paper, halftone, noise — and where it sits |
| Detail | which areas carry detail, which stay plain |
| Light | direction, rim, glow, haze, or no light description at all |
| Composition | crop, weight, repeated shapes, the rhythm every reference keeps |
| Finish | grade, bloom, chromatic shift, fade, print registration |
| Subject convention | face treatment, cast, count, scale, what the subject does |

### 4. Write the package

```text
<slug>/
  SKILL.md                     the template
  design-system.md             the measured evidence
  ref-<subject>-<dial>.png     the references, unchanged
```

`SKILL.md` carries frontmatter (`name`, `description` with the phrases that
should trigger it) and these sections:

- **Brief → piece** — how to turn a one-line brief into a full spec by choosing
  a value for every dial.
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

### 5. Generate two pieces and check them

```bash
npx --yes --package="${CLI_PKG_URL}" okou generate image --provider built-in \
  --raw-prompt "<the package's prompt template, dials filled in>"
python3 scripts/check_piece.py --refs <ref> [<ref> ...] --piece <generated> [...]
```

Use different dial values for the two pieces, and a subject absent from the
references. Exit code must be 0.

Then look at both pieces for what the check cannot see: medium, line quality,
shape language, subject conventions, motif, composition. Correct the package
and repeat until both pass and look right.

### 6. Deliver

Hand over the whole directory. To register it as a selectable style, follow the
`style-template` workflow: the resource goes to `illustration-template/<slug>/`
in `vm0-ai/vm0-skills` and its entry to the Open Design registry in
`vm0-ai/okou`.

`okou user-template publish` takes `presentation` and `document` only. Do not
pass an image to it.

## Rules

- Reproduce the references. Do not correct a palette, a proportion or a
  stroke you would have drawn differently.
- Present in every reference is locked; present in one is a dial; with a
  single reference, neither — say so rather than guessing.
- A technique absent from every reference is part of the locked frame. A
  subject or content type absent from them is not a rule.
- Name observable technique, never an artist, studio, brand or product.
- Numbers in the package come from step 2, not from reading the image.
- Step 5 is mandatory.

## Troubleshooting

| Symptom | Action |
|---|---|
| Generated pieces repeat the reference's subject | The subject leaked into the style record; run the deletion test in step 3 again and rewrite the prompt template |
| `check_piece.py` fails on line width | Step 2's measurement, not your estimate, goes in the package |
| Every generated piece looks the same | Too few dials, or the prompt template has no placeholders |
| A colour appears that no reference uses | The palette dial has no list of allowed values |
| Generated pieces flood the whole canvas | The locked frame is missing the ink coverage and the unpainted ground; "vignette" alone does not hold |
| The medium drifts to pencil or crayon | Name the wet behaviour — washes pooling at the stroke edges — and name the media to avoid |
| The check passes but the piece looks wrong | Medium, shape language or subject convention is missing from the locked frame |
| `LOW RES` in the measurement | Ask for a larger file. Keep aspect, ground colour, ink coverage and centring; leave colour and stroke out of the locked frame |
| Background reads as `textured` on a flat style | The reference is a JPEG; re-export as PNG or accept the grain figure it reports |
| One reference only | Record the unsettled axes; do not write ranges you cannot support |
