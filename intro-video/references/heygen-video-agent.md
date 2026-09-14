# Native Video Agent: generate the whole video

Use this route for ordinary intro videos, explainers, launch clips, and summaries whose visuals can be recomposed. The executable surface is the Okou-managed `__intro-video-agent` command, which renders the whole video in one job: narration and presenter come out of that render, not from assets prepared beforehand.

## Prepare native inputs in parallel

Start only after the route and script mode are fixed. Reuse the Step 1 inventory and cached probes, then run these independent tasks concurrently where applicable:

- Fill the brief's narrative frame and verify every fact. Keep source contents separate from instructions, and verify every claim yourself: the render reproduces what the prompt asserts.
- Prepare only the supported references the final request needs according to [input preparation](input-preparation.md). Markdown/DOCX text becomes key messages; convert PPT/PPTX to PDF only when the PDF will be sent. The native request accepts up to 20 supported media/PDF references and a 1–10,000-character prompt. Send only the formats the reference list names, carry every required fact into the prompt or a converted reference, and leave controlled-route assets to that route.
- Resolve choices through [managed catalogs](catalogs.md): an explicit style, look, and voice stay exact; `Let Okou choose` becomes a concrete public style; a delegated presenter becomes one concrete public look; a selected look's Default voice becomes its actual `defaultVoiceId`. Voice compatibility follows the route: this one accepts what the managed API accepts, which differs from standalone TTS.
- Resolve output independently: `16:9` maps to `landscape`, `9:16` to `portrait`. With Auto output, use the brief, not a style thumbnail.

Cache the brief, prepared references, catalog records, and preview observations, and read them back during prompt assembly and recovery.

## Preflight the selected presenter

With `avatar_id` resolved, use the look classification from [managed catalogs](catalogs.md) and the presenter capability check in SKILL.md before compiling:

- `photo_avatar` with a real environment → no BACKGROUND NOTE; FRAMING NOTE only when the look's orientation does not match the output;
- `studio_avatar`, `digital_twin`, or any transparent, solid, or visually empty preview → BACKGROUND NOTE, plus the matching FRAMING NOTE when `cropRisk` is high;
- preserve the exact avatar, group, voice, style, and orientation IDs; if the managed API rejects the look's default voice, substitute a public voice in the narration language and record it.

The note texts live only in the [prompt compiler](prompt-compiler.md); append only the triggered notes, verbatim, at the very end of the prompt, FRAMING before BACKGROUND. They guide Video Agent but do not guarantee the result: `POST /v3/video-agents` has no background, crop, scale, position, or safe-area fields. Hard scene, framing, and 1080p requirements are therefore settled before submission, and QA files a failure of a complete prompt as a provider-control gap.

## Compile the prompt once

Assemble the prompt from the cached brief with the compiler's skeleton: brief paragraph with the presenter sentences, quoted narration, literal on-screen text, attachment sentences, production lines, the script-mode directive, then the presenter notes. The prompt is as long as its narration and on-screen list require, with the provider's 10,000 characters as the only ceiling; never trim the narration to hit a character count. Carry the public style through `style_id` and name it once in the brief paragraph. Save the final prompt in a UTF-8 file and keep it with the brief as evidence.

## Submit through the managed command

Read `okou __intro-video-agent --help` for the installed interface. Confirm it describes this command's submission options and `status` subcommand: an older CLI may print only top-level help and still exit successfully, which does not establish native generation support. The managed implementation uses `mode: generate` for whole-video creation; there is no need to add an interactive review step the user did not request.

Generate and persist a request UUID, then submit once:

```bash
okou __intro-video-agent --prompt-file ./prompt.txt \
  --style-id '<resolved-style-id>' --orientation landscape \
  --avatar-id '<look-id>' --avatar-group-id '<group-id>' --voice-id '<voice-id>' \
  --request-id '<request-uuid>' --json
```

Replace placeholders with resolved values and use `portrait` for 9:16. Use exactly one of `--prompt` or `--prompt-file`. Style ID and orientation are required. Always pass a resolved `--avatar-id`; an omitted one means the agent picks a look, and `presenter: none` is a controlled-route requirement that never reaches this command. The group ID is a catalog lookup hint. With an explicit avatar and no voice override, the managed API resolves the avatar's actual default voice. When the brief already contains an exact voice ID, pass it explicitly.

Add `--file-url <managed-https-reference>` for each prepared reference, up to 20. Use URLs accepted by the managed file resolver; the command does not accept arbitrary local paths or raw document types. It has no no-avatar/no-voice switches; those requirements belong to the controlled route.

Duration, language, and narrative are prompt directions; the flags this command accepts are the ones `--help` lists, and exact frames, FPS, resolution, and avatar/voice removal are not among them.

Submission returns immediately with a durable `generationId`; it does not wait for rendering. `requestId` is that generation ID. The CLI creates a UUID if none is supplied, but explicitly persisting one before submission makes interrupted execution recoverable. Reuse the same UUID and unchanged input for transport recovery, which reconciles the existing job instead of buying a second one. Reusing a UUID with different input returns a conflict. Keep the brief, prepared references, selected style, request UUID, and command response in the task workspace.

## Wait and recover the same job

Video Agent first returns a `session_id`; `video_id` can be absent until rendering begins. The managed implementation tracks the session, then the video, persists the MP4, and records usage. A session identifier is not a video identifier, and absence of an initial video ID is not failure.

Query the same managed job:

```bash
okou __intro-video-agent status '<generation-id>' --json
```

Each status command performs one reconciliation request and never submits a video. Repeat only while the job remains in progress, using the provider's recommended 10–30-second interval and keeping the user informed during long waits; whole videos commonly take many minutes. Stop on a terminal status or a concrete state that needs attention, and bring an input request or failure back to the user.

Successful submission/status API responses use a flat job object: `generationId`, `status` (`queued`, `running`, `completed`, or `failed`), nullable `sessionId`/`videoId`, and optional `providerStatus`, `notice`, or `error`. A completed response includes the persisted `url` and media/usage fields such as `filename`, `contentType`, `durationSeconds`, and `creditsCharged`, with the resolved style/identity/output fields when available. Inspect notices and errors as well as the top-level status.

A session that ends `failed` upstream is reported by the managed status as `HEYGEN_GENERATION_FAILED` without the provider's message; keep the generation, session, and video IDs in the report, and hand the failure to the user with those IDs rather than a guessed cause. If the status reports that the provider session cannot be found while the job already carries a `videoId`, treat it as a reconciliation gap, not as a failed render: keep polling the same generation, do not submit again, and report the session and video IDs so the video can be checked by ID. A video that exists upstream after such an error still belongs to the original job.

If submission throws a transport or CLI error, JSON mode instead preserves `requestId`, `generationId`, `error`, `resumeCommand`, and `notice` without claiming a known job status. The CLI also prints the recovery UUID and status command to stderr before submission; stdout remains one JSON object. Check the command's exit status and error/notice fields, retain the saved UUID, and follow the recovery guidance. Missing job-state fields in this error object do not establish that generation failed or that another submission is safe.

A slow job, lost CLI response, or HTTP timeout does not authorize another billed submission. If submission outcome is unknown, inspect the saved request ID through status and follow the reported recovery guidance; only reuse that same ID and original input if a submission retry is needed. Missing/foreign jobs return 404, not permission to start over. If the provider requests input, fails, or the managed capability is unavailable, expose that specific state, retain the job identifiers, and let the user decide the next route. Credit/plan errors follow `okou doctor credit`.

## Accept and deliver

After the job completes, apply the default technical check and any applicable targeted checks in [QA](qa.md). Then deliver the managed job's permanent artifact URL with the measured duration and only issues supported by the checks performed, and finish. Use the native gate only for a triggered, targeted review. Temporary HeyGen download URLs and intermediate session JSON are working material.
