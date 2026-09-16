# Direct Media Generation

Use this reference for `image`, `video`, `avatar-video`, and `voice` after applying any attached-template instructions from the entrypoint.

## Select the Execution Path

Read `okou generate <type> --help` once for the selected type. Use its current flags and defaults.

- Prefer `--provider built-in` when the user wants a direct artifact, names no connector, and the built-in path supports the request.
- Use `--provider <connector>` when the user names that provider or needs one of its capabilities. The command returns connector skill guidance; follow it rather than translating it into a built-in call.
- List providers by running the type command without generation input only when a provider choice is unresolved. Use `--all` only when unavailable or not-yet-authorized connectors matter.
- Ask before choosing when missing input prevents a useful result, plausible choices materially change cost, account usage, licensing, fidelity, latency, or format, meaningful credit spend was not implied, or high-stakes brand/person/legal/medical/financial accuracy needs missing source material. A clear generation request already authorizes a reasonable supported path; do not manufacture another approval step or broaden the requested spend.

Preserve the user's subject, constraints, audience, brand, source media, dimensions, duration, format, and delivery target. Use a file or supported stdin for long or quote-sensitive text.

## Type-Specific Inputs

### Image

Treat the image styles shown by `okou generate image --help` as the live registry.

- When a registered style clearly matches, compile with `--style <id> --prompt <brief> --compile`, follow the returned compilation packet, then generate with its final text through `--compiled-prompt`.
- Use `--raw-prompt` for an explicitly unstyled or model-native result, a fully specified final prompt, photorealism, or when no registry style fits.
- Preserve reference images, masks, fidelity, output size, format, and transparency requirements through flags supported by the selected model. Never invent a style or model ID.

### Video

Read and complete [video preview](video-preview.md) before the first submission, including template and connector routes. Follow current help for model-specific duration, resolution, audio, and reference limits. Do not pass `--model` unless the user named one when current help gives that instruction.

When generating keyframes, preserve the selected video direction rather than adding an unrelated image-registry style.

For BytePlus/Seedance, choose one supported input group: first/last frames, or reference image/video/audio inputs. Do not combine the groups. Resolve a conflict with the user instead of silently dropping supplied media.

### Avatar Video

Use exactly one driving input: `--script` (or supported stdin) or `--audio-url`. Discover public avatar and voice IDs with the command's current list flags before generation; never invent IDs. Avatar video uses these inputs rather than a generic `--prompt`.

### Voice

Pass the speech text with `--prompt` or supported stdin. Preserve requested language, wording, voice, and delivery style using only voices and instruction flags shown by current help.

## Execute, Recover, and Deliver

Run the selected command once and wait for completion. Direct built-in media generation creates a server-side `/f/` artifact and may charge organization credits; it does not create a local file. The default output is human-readable, while supported direct-media commands use `--json` for the complete result object. Filtering shell output can hide fields, but does not undo the generation or its charge.

Keep the returned file URL and metadata. Do not rerun merely to recover output already present in the result. If the command reports insufficient credits, run `okou doctor credit`; buy or upgrade only when that diagnostic says the current user and plan can do so. For connector authentication or permission failures, use the shared flow documented by `okou connector --help` and its child help instead of duplicating or guessing account, scope, or permission steps here.

Deliver the artifact through a user-accessible returned URL and mention material parameters such as provider, model, style or raw mode, dimensions/aspect ratio, duration, and voice. If a connector returns only an expiring provider URL, preserve a durable copy when the selected provider guidance requires it.
