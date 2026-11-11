---
name: event-flyer-pack
description: "Create event flyers with real, scannable QR codes. Use for single flyers, coordinated promo packs, A6 fronts and backs, A4 four-up sheets, tent cards, and Story assets. Generate artwork with the available image tool, then overlay a real QR and verify every final asset."
---

# Event Flyer Pack

Turn event details into a coordinated set of promotional assets. Use the image tool for artwork and typography, then local scripts to generate, overlay, and verify real QR codes. Never ask the image tool to draw a working QR.

## Scope and preparation

- Use the available image tool for artwork; see `references/image-generation.md` for invocation steps.
- Default to large, high-contrast serif titles, dark atmospheric lighting, and cobalt, cream, and charcoal. Read `references/style.md` and inspect the bundled reference image. Borrow its visual language, not its fictional event details. The user's current style or brand requirements take precedence.
- For a single-flyer request, make only that flyer. A full pack includes A6 fronts and backs, A4 four-up front/back PDFs, a folded tent card, and a 1080×1920 Story. If scope is unclear, ask only whether the user wants a single flyer or a full pack. Start with one version per independent design; add another only if QA fails or the user requests alternatives.
- Invoke manually only. Do not create automations, automatically post, send bulk messages, publish publicly, place print orders, or create short links. Files are private by default. Follow current authorization and platform rules for third-party accounts and costs.

Set `SKILL_DIR` to this skill's absolute directory and `OUT` to the current task's output directory. Treat skill resources as read-only and write all outputs to the task directory. The reference image is stored as lossless base64. Restore it, verify its checksum, then inspect it with the image-reading tool:

```bash
mkdir -p "$OUT"
python3 "$SKILL_DIR/scripts/restore_reference.py" "$OUT/style-reference.png"
```

If verification fails, stop using that reference; do not silently skip the failure. Preparation does not call an image service.

## 1. Confirm event details

Record the current inputs using the structure in `templates/event-spec.json`; do not modify the bundled template. Confirm the title, date, start/end times and timezone, venue or online entry point, admission, CTA, QR URL, language, asset scope, and dimensions. Optional fields include a tagline, agenda, highlights, host, and authorized images or logos.

Ask only for missing essential details. Do not reuse demo dates, addresses, or URLs, or assume free entry. Concept drafts may use TBA. Without a real destination URL, do not fabricate a QR or describe the result as ready to publish. Clearly label fictional demos. Resolve date/weekday conflicts before proceeding.

Use HTTPS by default and preserve the user-confirmed URL exactly. Do not add UTM parameters, remove parameters, or substitute a third-party short link without approval. For long URLs, suggest a user-owned short link or a larger QR. Reject phishing or malicious uses. Never encode secrets, sessions, or one-time login tokens in promotional QR codes.

## 2. Generate the complete base artwork

Read the relevant template in `templates/prompts.md`. Fill in the exact copy, scene, palette, and placeholder coordinates, and remove optional fields that were not supplied. Request a complete design with an empty QR area. Do not let placeholder braces appear in the artwork.

Generate each independent design separately: front, back, two upright tent-card halves, and Story. Local scripts handle four-up assembly and tent-card rotation; do not generate extra artwork for those operations.

Require a solid pure-white square QR placeholder with a fixed position and side length. It must contain no patterns, text, shadows, or rounded corners, and must not overlap the copy. Even if the artwork includes a fake QR, completely cover it with opaque white before replacing it with a real code.

Wait for generation to finish. Save the job ID, prompt, original file, and actual returned dimensions; do not resubmit to check progress. Before printing, normalize dimensions as described in `references/print-and-qa.md`, then overlay the QR. A6 is 105×148 mm, approximately 1240×1748 px at 300 DPI, not 2:3. Do not stretch artwork or silently crop text. Visually inspect any canvas extensions. Upsampling does not add detail.

## 3. Generate and overlay a real QR

Install `scripts/requirements.txt` in a task-specific virtual environment. Keep the same `SKILL_DIR` and `OUT`, and set `EVENT_URL` to the user-confirmed final URL.

```bash
python3 -m venv ./generated/flyer-env
./generated/flyer-env/bin/python -m pip install -r "$SKILL_DIR/scripts/requirements.txt"
PY=./generated/flyer-env/bin/python

"$PY" "$SKILL_DIR/scripts/generate_qr.py" --url "$EVENT_URL" \
  --error H --border 4 --box-size 16 --png "$OUT/qr.png" --svg "$OUT/qr.svg"

"$PY" "$SKILL_DIR/scripts/overlay_qr.py" "$OUT/front-base.png" \
  "$OUT/qr.png" "$OUT/front.png" --auto-detect --verify "$EVENT_URL"
```

If automatic detection finds multiple candidates, finds none, or selects the wrong position, inspect the image and use `--x X --y Y --size S`. Do not blindly select the largest white region or combine manual coordinates with `--auto-detect`.

The script checks bounds, clears the entire white card, redraws the real QR with integer-pixel modules and a four-module quiet zone, then decodes a native-pixel crop from the final export. Any URL mismatch is a failure; do not deliver that file. Reuse the same QR across other assets and verify each asset separately. Default to plain black and white, without logos or gradients.

## 4. Assemble the requested assets

Use `scripts/formats.py` as described in `references/print-and-qa.md`:

- `normalize`: fit the base artwork proportionally into the target canvas before overlaying the QR.
- `four-up`: create A4 four-up front/back PDFs at 95% A6 by default, leaving room for crop marks. Disclose the actual tile dimensions.
- `tent`: rotate and stack two QR-verified A6 halves into PNG/PDF outputs. Rotate the top half by 180°; never horizontally mirror the text.
- `story`: export a QR-verified 1080×1920 PNG to JPEG, then verify the JPEG again.

Decode multi-code outputs one panel or half at a time. For PDFs, render the final pages before checking. Failure to detect a whole multi-code page does not prove that every individual code is broken. A successful base image does not establish that the full pack passed QA.

## 5. Review and deliver

Visually inspect the final files using `references/print-and-qa.md`. Compare the title, date/weekday, time/timezone, venue, admission, CTA, and URL against the approved copy. Check hierarchy, omissions, garbled text, clipping, and QR overlaps. Automated decoding verifies encoded content, not whether the event is real, the website is available, a phone can scan it, or the printed result is acceptable. Report only checks actually performed.

Save `qa.json` in the task directory with copy-check status, actual dimensions, job IDs, expected/decoded URLs for every asset, PDF page counts, and print limitations. Do not label files as approved finals if QR verification fails or essential information remains unchecked.

Before Web delivery, read `okou web upload-file -h` and upload every final image to be shown. A full pack may also be bundled in a private ZIP. Do not provide only local paths, upload unselected drafts, secrets, or caches, or automatically send files to external platforms.

Reply briefly with file links, the actual scope produced, per-asset QR results, and any necessary print limitations. If only one flyer was made, say so; do not claim the full print pack was tested.

## Resources

- `templates/prompts.md`, `templates/event-spec.json`: prompts and a blank event-input structure.
- `references/image-generation.md`, `references/style.md`, `references/print-and-qa.md`: artwork generation, visual direction, assembly, and QA.
- `assets/style-reference.png.b64`, `scripts/restore_reference.py`: the reference image and checksum-verified restoration tool.
- `scripts/generate_qr.py`, `scripts/overlay_qr.py`: real QR generation, overlay, and verification.
- `scripts/formats.py`, `tests/test_tools.py`: asset assembly and local tool tests that do not call an image service.
- `NOTICE.md`, `LICENSE.upstream.md`: attribution and the upstream MIT declaration; retain both when redistributing.
