# Dimensions, assembly, and QA

## Establish production limits first

- A6 trim size is 105×148 mm, approximately 1240×1748 px at 300 DPI, not 2:3.
- A full pack includes A6 front/back PNGs, A4 four-up front/back PDFs, tent-card PNG/PDF outputs, and a Story JPEG. Producing one flyer does not establish that the full pack passed QA.
- A digital-only flyer must use the user's requested and actually exported dimensions; do not substitute A6 without approval.
- Upsampling does not add detail. Record the original resolution, actual output dimensions, and any enlargement.
- Default outputs have no bleed, CMYK/print-ICC/PDF-X certification, die lines, or glue flaps. Do not describe them as printer-approved bleed masters. For commercial printing, first obtain the printer's specifications, generate or extend artwork to the required bleed, and review it separately. Adding a white border is not bleed.
- Four full-size A6 tiles nearly fill an A4 sheet, leaving no room for external crop marks without altering the layout. This adaptation defaults to **95% A6 = 99.75×140.6 mm** tiles with external crop marks; these are explicitly not full-size A6. Print at Actual size / 100%, without an additional Fit to page setting. If full-size A6 is required, use larger paper or first confirm that crop marks may be omitted.
- The unfolded tent card is 105×296 mm, folded at 148 mm; each half is 105×148 mm. Rotate the top half by 180°; do not mirror it horizontally. Not every paper stock will stand unsupported; make a physical proof before a production run.

## Runtime conventions

`PY` is a Python interpreter with `scripts/requirements.txt` installed. `SKILL_DIR` is the skill's absolute directory, `OUT` is the current task's output directory, and `EVENT_URL` is the user-confirmed final URL. Create the output directory before running commands. Treat templates and resources as read-only and write all generated files to the task directory.

### Normalize the base artwork before overlaying the QR

```bash
"$PY" "$SKILL_DIR/scripts/formats.py" normalize "$OUT/front-generated.png" \
  "$OUT/front-base.png" --width 1240 --height 1748 --matte '#181818'

"$PY" "$SKILL_DIR/scripts/formats.py" normalize "$OUT/story-generated.png" \
  "$OUT/story-base.png" --width 1080 --height 1920 --matte '#181818'
```

Do not crop or stretch. Extend the canvas when needed to match the target aspect ratio. Inspect the edges and placeholder position with the image-reading tool, and revise the design if necessary. Do not accept obvious black bars merely to meet the dimensions. A `qr_verified: false` result is expected at this stage: this is base artwork, and the real QR is overlaid next.

### Overlay the QR manually

```bash
"$PY" "$SKILL_DIR/scripts/overlay_qr.py" "$OUT/front-base.png" "$OUT/qr.png" \
  "$OUT/front.png" --x "$X" --y "$Y" --size "$SIDE" --verify "$EVENT_URL"
```

Coordinates are pixels in the exported base image, and the QR must fit entirely inside the canvas. Do not silently resize after the final overlay. The script clears the entire placeholder with opaque white and verifies a native-pixel QR crop from the saved file. Wrong URLs, out-of-bounds placement, and multiple candidate white areas require explicit resolution.

### Four-up sheets

```bash
"$PY" "$SKILL_DIR/scripts/formats.py" four-up "$OUT/front.png" "$OUT/back.png" \
  --out "$OUT" --slug "$SLUG" --verify "$EVENT_URL" > "$OUT/four-up-qa.json"
```

Render all four panels from each final PDF at 300 DPI and decode each panel separately: eight checks across both sides. Duplex alignment depends on the printer. Make a physical proof; paper-feed tolerances are not guaranteed.

### Tent card

```bash
"$PY" "$SKILL_DIR/scripts/formats.py" tent "$OUT/tent-top.png" \
  "$OUT/tent-bottom.png" "$OUT/tent-card.png" --verify "$EVENT_URL" \
  > "$OUT/tent-qa.json"
```

Both source halves must already be A6, upright, and QR-overlaid. The script exports PNG/PDF, crops each half, rotates the top half upright for verification, and performs four checks in total. Do not try to decode the entire two-code canvas with a single-code detector.

### Convert the Story to JPEG last

```bash
"$PY" "$SKILL_DIR/scripts/formats.py" story "$OUT/story.png" \
  "$OUT/instagram-story.jpg" --verify "$EVENT_URL" > "$OUT/story-qa.json"
```

The source must be 1080×1920. The script decodes the final JPEG again; checking only the PNG source is insufficient. Publishing platforms may recompress the file, so a local pass does not establish a pass after platform processing. Keep important content approximately 250 px from the top and bottom edges, and do not place the QR against the bottom edge.

## QA record

Save `qa.json` in the task directory with these fields:

```json
{
  "scope": "single-front-or-full-pack",
  "fictional_demo": false,
  "generation_job_ids": [],
  "copy_check": {"status": "pass-or-unverified", "checked_fields": []},
  "assets": [
    {"file": "front.png", "pixels": [1240, 1748], "expected_url": "user-confirmed-url", "decoded_url": "actual-result", "qr_pass": true}
  ],
  "print": {"bleed_mm": 0, "cmyk_verified": false, "printer_proofed": false},
  "limitations": []
}
```

At minimum, check:
1. The title, date/weekday, time/timezone, venue, price/admission, and CTA exactly match the user-approved copy, without omissions, additions, or garbled text.
2. The QR does not overlap text or get clipped, has a quiet zone of at least four modules, and decodes to the exact destination URL.
3. Checks run on the actual images and PDFs being delivered; a successful base file does not establish a successful final export.
4. Actual image dimensions, paper sizes, and PDF page counts are correct. Disclose the actual tile dimensions on A4 four-up sheets.
5. If claiming that the destination page is available, visit and verify it. The scripts check URL syntax and encoding, not the live website. Follow current public-data/browser rules when a page check is needed, and do not request secrets.
6. Automated decoding is not a physical-phone scan, low-light or long-distance scan test, or print proof. Mark checks not performed as "not tested."
7. Deliver only the selected final files that passed their checks, and retain the corresponding generation receipts.

## Local tool tests without paid generation

```bash
"$PY" -m unittest discover -s "$SKILL_DIR/tests" -v
```

The tests create synthetic artwork and QR codes to check single-code overlays, invalid URLs, wrong destinations, ambiguous white areas, out-of-bounds placement, individual PDF four-up panels, tent-card rotation, and JPEG re-export. They verify the local toolchain, not visual layout for a real event or commercial print proofs.
