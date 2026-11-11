# Generate event base artwork

Use the available image tool with `templates/prompts.md` to generate a complete design containing artwork, typography, and an empty QR area. Generate one asset at a time. Do not ask the tool to draw a working QR.

Before invoking the tool, read `okou generate image -h` and choose an available size from the current help. The pack's prompts already contain the full visual requirements: use raw-prompt without adding unrelated illustration styles. Replace `<supported-size>` with a currently supported size close to the target aspect ratio.

```bash
okou generate image \
  --raw-prompt "$(< "$OUT/front-prompt.txt")" \
  --size "<supported-size>" --quality high --format png \
  --wait --visibility only-me --json > "$OUT/front-generation.json"
```

- Wait for completion and use the returned image. Save the original prompt, job ID, and actual returned width and height.
- After a timeout, query the same generation ID: `okou generate get <generation-id> --refresh --json`. Do not resubmit to check progress.
- Once complete, download the actual artwork: `okou generate get <generation-id> --out "$OUT/front-generated.png"`.
- If the returned dimensions differ from the target, use `formats.py normalize` to fit the artwork proportionally into the target canvas before overlaying the real QR. Do not stretch the artwork or silently crop text. Inspect any extended edges.
- Inspect the local reference image first. If it must be supplied to the tool, use only a method supported by the current interface and authorized by the user; do not make it public without permission. Inspecting it and describing its visual language is usually sufficient.
- If generation fails, retain the receipt and follow the current tool's diagnostics. Do not retry indefinitely or repeat paid test runs.

Local scripts handle four-up assembly, rotated stacking, and final QR verification without further image-service calls.
