# Execute the saved prompt

Use these instructions only after selecting a template and saving its complete
prompt. Keep provider mechanics here, separate from portable art-direction data.

## Okou Harness: native default

1. Inspect `okou generate image -h`. When provider discovery is needed, run
   `okou generate image` without a generation prompt. Respect a provider explicitly
   named by the user; do not infer a connection or permission from this package.
2. Use the built-in backend when no provider is specified and it is available.
   It uses the model selected in Settings. No per-call `--model` exists. This
   package does not require choosing Nano Banana over another available model.
3. Submit exactly once and wait. Use the current help's flags; a representative
   supported invocation is:

   ```bash
   PROMPT_FILE=/absolute/output/prompt.txt
   okou generate image --provider built-in \
     --raw-prompt "$(< "$PROMPT_FILE")" \
     --size 1280x720 --format png --wait --json \
     > /absolute/output/generation-receipt.json
   ```

   This shell example requires Bash. The prompt is quoted data, never executable
   shell code. Do not use `eval`. Do not put a secret in the prompt or CLI arguments.
   Inspect model-specific size support first; an approximate 16:9 preset may need
   the bundled export step. Record actual model and source dimensions returned,
   not merely requested dimensions.
4. With reference assets, use the supported image-to-image/reference controls
   shown by current help, preserving role labels and passing the real image bytes
   or supported URLs. Do not send private signed URLs to an arbitrary fetcher.
   Prefer the authorized platform file flow. Missing reference support is a
   limitation to disclose, not a reason to invent a person's identity.
5. If waiting times out or execution is uncertain, use the **existing generation
   ID** with `okou generate get <id> --refresh --json`; inspect `get -h` if needed.
   Never submit a new generation merely to see whether the first finished. If no
   recoverable ID is available, report the unknown state instead of blind retry.
6. Once complete, inspect `okou artifact download -h` and download the exact
   returned artifact URL or ID. Do not assume public HTTP access to a private file.
7. Export and visually inspect the downloaded output, then upload the final JPEG
   using the current integration. Report success only after a completed image and
   a user-openable artifact exist.

On insufficient credits, run `okou doctor credit`; do not buy credits automatically.
On an external connector failure, diagnose it with current
`okou connector check --help` and the failed operation before requesting access.
A queued job or successful permission grant is not an image.

## Other agent runtimes

Use an available authorized raster image-generation tool with the saved prompt,
16:9 output and actual supplied reference assets. Keep its receipt and actual
model identity. Do not install the upstream repositories or collect API keys just
because they appear in provenance. If no image backend is available, say that
only the prompt is ready and ask for a supported backend; do not substitute an
HTML/CSS screenshot, SVG or design brief and call it an AI-generated thumbnail.

## Named upstream integrations

NanoThumbnail presets in this package are adapted source material. Its MCP server,
browser studio and provider accounts are optional, separate integrations. Only
claim an upstream integration test if its real tools were available, generation
completed, and the returned output was inspected. A native Okou render is not an
MCP test. If the user requires the original integration and it is unavailable,
explain the blocker and obtain agreement before switching the execution route.
