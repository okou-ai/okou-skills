---
name: gen
description: Generate images, presentations, websites, reports, and designs with Okou, and discover connected providers for video, talking avatars, and voice.
---

# Gen

Use this skill to generate user-facing artifacts through the Okou CLI:

```bash
okou generate -h
```

`okou generate` is the source of truth. Always inspect the current command help when exact flags, models, styles, or providers matter.

Okou no longer offers video or avatar templates, built-in video/voice/avatar generation, or the built-in JoggAI avatar and voice catalogs. Video model entries may remain in settings; they do not make these retired pipelines available. Use an authorized connector for new video, avatar, or speech requests. Never retry a retired built-in endpoint or substitute another built-in media command.

## Core Commands

- `okou generate image` - billed image file generation; supports built-in models, image editing/reference inputs, image style registry selection, and connector guidance.
- `okou generate video` - list connected video providers and get connector skill guidance; no built-in execution or video templates.
- `okou generate avatar-video` - discover video connectors for talking-avatar requests; avatar and voice discovery and generation follow the selected connector skill.
- `okou generate voice` - discover audio connectors for speech requests; synthesis follows the selected connector skill.
- `okou generate presentation` - returns an Open Design resource-selection packet for an HTML presentation that the agent authors and hosts.
- `okou generate website` - returns website authoring instructions / an Open Design packet that the agent uses to build and host a static site.
- `okou generate report`, `docs-design`, `poster`, `dashboard-design`, `mobile-app-design` - return Open Design resource-selection packets for static HTML artifacts.
- `okou generate text`, `code`, `document`, `music` - list connector-backed options and print connector skill-invocation guidance; these do not have built-in platform pipelines unless the CLI help says otherwise.

Run `okou generate <type>` with no generation input to list available providers for that artifact type. Add `--all` when unavailable or not-yet-authorized connectors are relevant.

## Generation Workflow

1. Identify the artifact type from the user's request.
   - Use `image` for raster images, edits, references, thumbnails, icons, illustrations, and visual assets.
   - Use `video` for generated motion, animated frames, product clips, or reference-driven video.
   - Use `avatar-video` for a talking avatar driven by a narration script or public audio URL.
   - Use `voice` for speech audio from text.
   - Use Open Design artifact commands for websites, decks, reports, posters, docs, dashboards, and mobile UI prototypes.
   - Use connector-listing commands for text, code, document, or non-speech audio generation.

2. Discover current capability before committing.
   - Run `okou generate <type> -h` for flags and built-in model support.
   - Run `okou generate <type>` to see available providers.
   - If the user asked for a connector/provider by name, run `okou generate <type> --provider <name>` to get invocation guidance, then follow that provider skill.

3. Determine whether style discovery is needed.
   - For styled images, inspect the current style registry from `okou generate image -h`.
   - Do not hardcode style names or style descriptions in this skill. Treat the registry printed by the CLI as the live source.
   - Choose a registered style when the user's wording clearly matches a trigger, named style, or visual direction in the registry.
   - To obtain style-specific prompt guidance, run `okou generate image --style <id> --prompt "<brief>" --compile`, follow the returned packet, then generate with `--compiled-prompt "<final prompt>"`.
   - Use `--raw-prompt "<final prompt>"` when the user explicitly wants no registry style, wants photorealism/model-native output, supplies a fully specified prompt, or no registry style is a good match. For video keyframes, preserve the selected video's visual direction; do not add an unrelated image style.
   - When no style is obvious but style materially affects the result, ask the user to choose among a few options summarized from the live registry or ask whether to proceed without a style.

4. Decide provider and model.
   - Prefer `--provider built-in` when the user wants a direct artifact, does not name a connector, and the built-in pipeline supports the request.
   - Use connector guidance when the user names a provider, needs a provider-specific capability, or the requested artifact type is connector-only.
   - Ask the user when the choice changes cost, latency, fidelity, licensing, account usage, or final format in a way that is not implied by the request.
   - Otherwise choose a sensible default from the CLI help and proceed.

5. Build the prompt.
   - Preserve the user's core intent, constraints, audience, brand, source materials, aspect ratio, duration, size, format, and delivery target.
   - Add operational details only when they improve generation reliability: composition, visual hierarchy, must-include/must-avoid elements, target medium, and reference handling.
   - For avatar video, discover supported avatar and voice IDs through the selected connector skill. Never invent IDs or substitute an identity or voice. Follow that provider's input contract.
   - For style-guided image generation, let the selected registry style drive stylistic details through the compilation packet.
   - For prompt text that is long or quote-sensitive, use a file and a safely quoted argument, or stdin when the selected prompt mode supports it.

6. Execute and wait for completion.
   - For connector-backed video, follow **Video preview** below before submitting a video job.
   - For built-in artifact types, run the selected `okou generate <type>` command. For video, avatar, or voice, use `--provider <connector-name>` for guidance, then execute through that connector skill; the CLI does not accept generation input for these retired built-in types.
   - For commands that return an Open Design resource-selection packet, follow the packet: author the artifact, verify it locally if needed, and host static outputs with `okou host`.
   - For commands that return `/f/` file URLs, keep the URL and metadata for the user.
   - If generation fails because of missing credits, run `okou doctor credit`.
   - If connector auth fails, run `okou connector check --help` and diagnose the failing URL or environment name from the provider guidance.

7. Deliver the result.
   - Give the user the generated URL or hosted artifact URL.
   - Mention important parameters used: provider, model, selected style or raw prompt mode, size/aspect ratio, duration, voice, or site slug.
   - If the output is temporary or provider-hosted with expiration, download or host a durable copy when appropriate.

## Video preview

1. Before generating a video, prepare a few keyframes matching the user's subject, style, and aspect ratio. Reuse suitable supplied or already approved images.
2. Show the actual images through accessible links, briefly describe the intended motion, and ask the user to confirm. End the turn and wait; do not start a video job before confirmation. Revise the preview if requested.
3. After confirmation, generate the video. Use the approved images as first/last frames or references when supported by the selected model; otherwise follow the approved visual direction in the prompt. Reuse existing confirmation for an unchanged preview.

Follow the selected connector's supported input modes for first/last frames and reference media. Do not reuse retired Okou generation flags for a provider API or silently drop supplied inputs. Correct conflicting inputs before retrying.

Keep the preview message short: the images, a brief motion description, and one confirmation question.

## Asking vs. Choosing

For video, obtain the preview confirmation above before proceeding.

Ask the user before generation when:

- The prompt is too underspecified to produce a useful artifact.
- Multiple provider/style/model choices are plausible and materially different.
- The command will spend meaningful credits and the request did not imply that spend.
- The user requested brand, person, legal, medical, financial, or other high-stakes accuracy that needs source material.
- Required inputs are missing, such as source images, brand assets, narration text, dimensions, or audience.

Proceed without asking when:

- The user gave enough context for a reasonable first version.
- The built-in default clearly fits the request.
- The user asked for speed or explicitly delegated choices.
- The missing details can be safely inferred and refined after the first artifact.

## Common Patterns

List current providers:

```bash
okou generate image
okou generate video
okou generate voice
```

Get JoggAI connector skill guidance for BYOK operations:

```bash
okou generate avatar-video --provider joggai
```

Inspect current image styles and flags:

```bash
okou generate image -h
```

Compile a styled image prompt after selecting a live registry style, then use the packet's final prompt:

```bash
okou generate image --style "<style-id>" --prompt "<brief>" --compile
okou generate image --provider built-in --compiled-prompt "<final prompt>"
```

Generate an unstyled/model-native image:

```bash
okou generate image --provider built-in --raw-prompt "<prompt>"
```

Use connector guidance instead of built-in generation:

```bash
okou generate video --provider "<connector-name>"
```

Generate a static Open Design artifact:

```bash
okou generate website --prompt "<brief>"
```

Then follow the returned packet to build and host the artifact.
