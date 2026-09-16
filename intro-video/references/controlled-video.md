# Controlled video: Okou orchestrates the content, audio, and timeline

Read this only after the main skill selects controlled composition. It is the route for requirements HeyGen Video Agent cannot honor: no added narration (`No voiceover`), no audio at all (`silent`), a retained source track (`Original audio`), exact pages, frames, footage, timing, layout, or geometry, and a verbatim script that must also hit an exact duration. Video Agent always writes and voices narration and treats attached audio as reference material, so these outcomes exist only because Okou composes the video itself. A source attachment, Auto style, missing native access, or a failed native job is not a trigger for this route. A screen recording that ships a synchronized same-stem `.clicks.json` sidecar is not one either: preserving that footage is what [screen recording](screen-recording.md) already does, locally and without a composition.

`No avatar` on its own is **not** a trigger: the native route honours it through the prompt and verifies it on the frames. It reaches this route only alongside one of the requirements above — a deck whose pages must be preserved and narrated as voice-over is the ordinary case — or when the user needs the exclusion guaranteed before rendering rather than checked after. Where it does apply here, it is implemented by leaving the presenter layer out.

The lanes, validation and render steps below are the preservation path. A build handed to `video-composition` follows that skill's own bootstrap, authoring and review instead; what this file still governs there is the locked plan and the brief-level acceptance in [QA](qa.md).

## Resolve the composition skill once

For a library-based build, use the mounted `video-composition` skill or the sibling `../../video-composition/SKILL.md` in this repository. A revision reuses the checkout recorded by the accepted project. If neither is available, fetch the official source into a new resource directory once:

```bash
git clone --depth 1 --filter=blob:none --sparse https://github.com/vm0-ai/vm0-skills.git <RESOURCE_DIR>
git -C <RESOURCE_DIR> sparse-checkout set video-composition
git -C <RESOURCE_DIR> rev-parse HEAD
```

Record that commit and skill directory with the brief; read `<RESOURCE_DIR>/video-composition/SKILL.md` and its selected references. Do not repeat discovery or update the checkout during the build. This fallback does not depend on an `okou resource` registry alias, a web search for skills, or the legacy HyperFrames intro workflow. If the official source cannot be obtained, report that concrete dependency failure and retain any completed media.

## Exact pages, footage, audio, or layout

Okou owns the scene list, prepared visuals, narration mapping, and time-based composition. The managed HeyGen integration generates optional speech and transparent presenter takes using Okou credits; Okou’s managed cloud-render command finishes the composition using the platform HeyGen account. **No voiceover**, **silent**, and **original audio** are implemented by including or omitting audio layers in the composition, not by asking a generative agent to remember an exclusion; where a job on this route also has no digital human, the presenter layer is simply left out. Okou owns the audio decision on this route.

Resolve Auto style from the [managed catalog](catalogs.md) only when the brief calls for a style treatment. Use the selected style only for permitted added graphics and treatments. Preserve original page/footage pixels and geometry where required; explain that the resulting treatment is a controlled adaptation, not native preset execution. Resolve a conflict only when the user explicitly requires both native preset execution and incompatible preservation controls.

A style selection buys a treatment, not extra decorative layers. Where the user permits no visual additions, record the selected style and explain that the original visuals determine the appearance.

## Lock the plan

Before asset generation, lock the required pages or footage, scene order, preservation geometry, source-audio policy, narration units, presenter overlay, output ratio, and fixed timing requirements. For page-for-page work, retain every page as a static bitmap with no restyling or invented marketing arc. For recordings, retain the selected segments and verify crop/readability. Choose custom motion only when requested.

When there are no pages or footage to preserve, the visual system comes from the [`video-composition`](../../video-composition/SKILL.md) skill, which owns the executable layout library, the scene contract, and the two-lane plan that authors content on provisional windows while voice or a talking avatar generates. Hand it the locked plan and let it run its own review; the lanes below describe the preservation path, not that one. The two vocabularies compose rather than compete: the recipe arc in [recipes](recipes.md) still orders the scenes, and each scene takes the smallest Router row that holds its content. When its layout vocabulary cannot carry the material, say so and let the user choose another treatment rather than assembling a visual system for the occasion. For static deck conversion, the mounted `ppt-avatar-video` skill's **composition builder** and geometry probes are reusable, but its JoggAI generation instructions do not accept the selected HeyGen IDs. Reuse only the builder after reading its manifest schema. Keep source pages static. For a non-speaking avatar, use an available still; if a transparent still is unavailable, resolve the presentation choice instead of manufacturing an unrelated person.

## Prepare independent lanes

After the plan is locked, run these lanes concurrently and cache every probe, conversion, catalog result, and generated asset:

1. **Visuals:** prepare only the required page bitmaps, footage segments, and permitted added graphics.
2. **Narration/audio:** finalize one narration unit per scene. `No voiceover` omits added narration but does not delete source audio; `silent` removes every audio track. For original audio, probe that the intended track exists and extract or retain it without TTS. For synthetic speech with a compatible exact voice, use the managed command:

   ```bash
   okou __intro-video-voice --voice-id VOICE_ID --text "FINAL_SCRIPT" --json
   ```

   Keep long or quote-sensitive scripts in a file and pass their contents as one safely quoted argument; the command does not accept stdin. Split only for its 5,000-character limit. Retain each permanent audio URL and download needed assets into the project.
3. **HyperFrames project:** initialize the project from the locked plan without waiting for visuals or narration. Inspect `npx hyperframes@VERSION skills --help`; if the entrypoint is missing, inspect `skills update --help`, install the needed `hyperframes` skill, then read and follow it. Use the version the project already pins, and never change it mid-project. For a new project, resolve the current version once (`npm view hyperframes version`), pin it in the project, and record it with the plan; `0.8.26` was the version verified when this reference was written, so treat it as the floor rather than the value to copy. If installation fails, report the dependency instead of inventing CLI flags or HTML attributes.

Generate a speaking presenter only if requested. Its sole preparation dependency is the finalized narration audio; start it as soon as that audio is available while other lanes continue, and reuse that same audio:

```bash
okou __intro-video-presenter --avatar-id LOOK_ID --avatar-group-id GROUP_ID \
  --audio-url NARRATION_URL --json
```

The managed renderer produces a landscape transparent WebM. Verify alpha, duration, and framing: on the direct video endpoint a near-square look fitted to the frame width (`cover`) loses the top of its head, while `contain` keeps it, and the managed command exposes no fit control. If a take arrives cropped, report it as a platform fit defect with the look dimensions instead of retrying the same take. It is a composition layer, not the final MP4. For other ratios, fit it without cropping essential content. The flags this command accepts are the ones `--help` lists, and it runs on the platform's credentials.

Check real speech duration with `ffprobe`; use transcription/timestamps only as needed to map scene cuts. A presenter take uses at most 600 seconds of audio. Split longer narratives into bounded takes aligned to narration segments. Mix narration once and mute duplicate presenter audio. Reuse the prepared assets, and keep preparation to the selected route.

## Assemble, validate, and render once

When the lanes finish, assemble the cached assets and final timings once. Validate before the final render:

```bash
npx hyperframes@VERSION lint PROJECT --json
npx hyperframes@VERSION check PROJECT --strict --samples 5 --json
npx hyperframes@VERSION snapshot PROJECT --at FIRST,MIDDLE,LAST --no-end --describe false
```

Use numeric snapshot times, check every required page/segment, and confirm no stretching, covered text, duplicate audio, or missing assets. A public Video Agent style ID is not a controlled-render option; any similar custom treatment is an adaptation and must have been described as such.

The preservation path requires the Okou API and CLI release containing `okou video render`, under the existing Intro Video switch. Check `okou video render --help` once. If the command or platform access is unavailable, report the missing release/access; do not invoke the personal HeyGen connector or silently switch export routes.

Set the independently resolved dimensions in the composition: 1920×1080 for 16:9 or 1080×1920 for 9:16. Reflow permitted added graphics; fit fidelity-critical pages or footage without cropping. The first managed release accepts 1080p, 30 fps, standard-quality MP4 in those two ratios. Output dimensions must match the composition’s `data-width` and `data-height`.

Inspect the exact packaged inputs, then submit once:

```bash
okou video render PROJECT --dry-run --json
okou video render PROJECT --json
```

The command honors `.hyperframesignore`, excludes generated renders, snapshots and development files, and rejects ZIPs over 200 MiB. Inspect the largest included files before submission. Exclude only verified unused intermediates; keep original page bitmaps, transparent presenter WebM, narration, fonts, scripts and all referenced assets. Never extract every presenter frame merely to upload a cloud project. The managed renderer receives authored HTML and assets, not a Video Agent prompt that could redesign the source.

The CLI uploads the ZIP through Okou, retains a durable request ID and returns the job. Save the returned generation ID and continuation command. The backend keeps the provider key, freezes the project input, submits to HeyGen, persists the finished MP4, and settles cloud-render credits separately from the existing voice/presenter assets.

```bash
okou video render status GENERATION_ID --json
okou video render resume GENERATION_ID --json
```

Use `status` to check the existing task; follow its retry interval instead of polling rapidly. After interruption, use `resume` with that same ID. It replays a submission only when the server explicitly permits it, with the original request and idempotency key. The provider retains idempotency records for 24 hours; Okou leaves a safety margin. If the server returns `manual_check`, retain the ID and report the unresolved submission rather than allocating a replacement. Closing a CLI process does not cancel a cloud render.

A completed job returns the permanent Okou artifact and actual `creditsCharged`; pending billing is not zero-cost rendering. Download the returned MP4 for one final verification pass: decode it, probe actual dimensions/frame rate/duration, inspect frames and audio, and compare required pages/segments and narration with the plan. Use that same accepted artifact URL for delivery; a second upload of identical output is unnecessary. Record local pack/upload time separately from cloud status intervals, and label polling-derived timings as estimates.

The managed APIs own provider credentials, billing, and artifact persistence. Save returned results and any generation identifier before subsequent steps, wait for the existing job, and reuse completed assets after interruption. A command or request that timed out is reconciled by inspecting its existing generation status, which is what a billed retry would otherwise duplicate.

The presenter CLI already waits for the managed job. A `GENERATION_TIMEOUT` error includes its `generationId`; resume with `GET /api/built-in-generations/{generationId}` on the same API origin, authenticated with the run's `OKOU_TOKEN`, and use its completed `result`. The CLI's origin is `OKOU_API_BACKEND_URL` (add HTTPS only if no scheme is present), otherwise `https://api.okou.ai`. A queued/running response is not failure. If an interruption left no known generation ID, reconcile the existing job before resubmitting, using the resume guidance above rather than a CLI flag.
