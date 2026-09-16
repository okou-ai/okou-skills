# Voice and Talking-Avatar Fast Path

Open this guide only when the video uses generated voiceover or a talking digital human. A talking avatar is generated video with a performed voice and an intrinsic duration, and here it is always a **transparent take**: the composition supplies the background, so an avatar with a baked-in scene cannot be mounted.

## Lock the shared contract first

Before starting external generation, lock one narration beat per scene:

`scene-id | narration text | Router layout id | media: voice|talking-avatar|silent | presenter position | viewer outcome`

The narration text, scene IDs, selected layouts, language, one voice ID, and the set of talking-avatar scenes are shared prerequisites. Resolve the voice once and reuse it across voice-only and talking-avatar scenes. Check feasibility against any binding duration before dispatch; estimates are not final media timing. Preserve user-locked wording unchanged. Do not change editable narration after dispatch unless the media job is intentionally restarted under the applicable retry authorization.

## Run two lanes concurrently

### Media lane

**A talking avatar, from the script.** One managed command produces the take and its narration together, so no separate speech job is needed and nothing waits:

```bash
okou generate avatar-video --provider built-in \
  --avatar-id AVATAR_ID \
  --voice-id VOICE_ID \
  --aspect-ratio landscape \
  --screen-style 3 \
  --no-caption \
  --video-name SCENE_ID \
  --json < narration/SCENE_ID.txt
```

`--screen-style 3` is the transparent WebM with alpha, and it is the only style this route can mount: style `1` bakes a scene behind the person and style `2` returns a green screen that still needs keying. `--no-caption` keeps the provider from burning subtitles over a layout that already carries its own on-screen text. Pipe long or quote-sensitive narration through stdin. Discover identities with `--list-avatars` and `--list-voices`, which take `--avatar-style`, `--avatar-gender`, `--voice-language` and similar filters.

The returned video and its audio are one media result; that scene needs no separate speech synthesis.

**A talking avatar, from an audio file you already have.** Pass it instead of a script — `--audio-url URL` on the same command. The HeyGen presenter renderer is the other route to a transparent take and accepts audio only:

```bash
okou __intro-video-presenter --avatar-id LOOK_ID --avatar-group-id GROUP_ID \
  --audio-url NARRATION_URL --json
```

It returns a landscape transparent WebM and accepts at most 600 seconds of audio per take; split longer narratives at narration boundaries. Because it has no script input, speech must finish before the take can start: that dependency is serial inside the media lane, and it is the reason the script-driven command above is the default. The visual lane runs concurrently either way.

**Voice only, no person on screen.** For a short cohesive narrative, synthesize one continuous script while authoring its scenes:

```bash
okou __intro-video-voice --voice-id VOICE_ID --text "FINAL_SCRIPT" --json
```

This command returns one audio file per request with its URL, file ID, and duration; it does not promise scene segments or word timestamps. Keep the scene-to-script mapping separately. Use separate requests only when independent takes serve the brief or the command's 5,000-character limit requires a split. Save each result immediately and reuse the accepted voice ID on revisions. Download via the exact returned URL or file ID; do not infer a file ID from an artifact alias. Long or quote-sensitive scripts must be passed as one safely quoted `--text` argument; this command does not accept stdin.

**An existing long track.** Keep one source file, voice or avatar, and derive scene boundaries from its transcript or word timings, mounting ranges out of that single source rather than re-encoding a file per scene.

Independent avatar scenes generate concurrently. Parallel submission changes wall time, not the seconds generated; cost rises when content is regenerated or handles and pauses are duplicated.

Physical cutting is a fallback, not the default workflow. Use FFmpeg only when a provider cannot return scene-keyed media, HyperFrames cannot consume the source as a time range, or the requested deliverable explicitly requires standalone segment files.

### Visual lane

Initialize HyperFrames, install the deduplicated Registry items, generate the real scene HTML with provisional windows, and fill its content slots while media generates:

```bash
node <SKILL_DIR>/scripts/bootstrap-project.mjs \
  --project <PROJECT_DIR> \
  --host-id <id> \
  --presenter <off|on> \
  --presenter-scenes <talking-avatar-scene-ids> \
  --media-mode <voice|talking-avatar> \
  --language <tag> \
  --content-font <required-for-first-zh-ja-ko-build> \
  --scenes cover:auto,evidence:auto \
  --layout-map cover=orientation/headline-cover,evidence=data/kpi-grid
```

`auto` creates a six-second authoring window marked `data-vc-timing="provisional"`; it is not a duration estimate. Use `--presenter on` when any talking-avatar scene exists. If scene IDs or layouts are not locked yet, use `--prepare-only` instead and delay scene creation. Never render provisional timing.

## Join once, from real media timing

Measure each downloaded media file with `ffprobe`; use returned word timings only when actually present. For continuous speech without timestamps, transcribe once to identify semantic cuts; if the segments are coarse, local silence detection can refine those boundaries without another transcription. Preserve the original generated speaking rate when it fits. Actual media timing replaces provisional scene estimates, not a binding total duration or preservation constraint. If the media cannot fit those constraints with the permitted edits, resolve the conflict before rendering; do not silently change locked wording, source audio, or the required duration. Silent scenes retain their planned duration. Add only an intentional bounded pause, never a speculative percentage buffer.

**Prepare any permitted speech-speed adjustment before finalizing timing.** Runtime `data-playback-rate` can disagree with the media-fit check, which reads the file's intrinsic duration. If a pace adjustment is appropriate for editable generated narration, produce one pitch-preserving derivative with FFmpeg `atempo`, leaving the source intact. Probe that derivative, map cuts to its timing, and mount it at playback rate 1. Do not retime locked original audio or a talking-avatar take independently of its performance. Preflight rejects non-unit audio playback rates on this composition path.

```bash
ffmpeg -n -i narration-original.mp3 -vn -af atempo=0.88 -c:a pcm_s16le narration-paced.wav
ffprobe -v error -show_entries format=duration -of json narration-paced.wav
```

The rate above is an example, not a default. At rate 1, the audio window is the measured file duration minus any intentional source offset; its end is `data-start + data-duration`. Confirm it fits the host before Static or Preview. After a derivative replaces a source, keep only the referenced derivative inside the render package and retain the original outside it.

Finalize the existing host and frames with exact seconds; this updates cumulative starts, full-window clip durations, and motion sidecars without rebuilding or overwriting authored scene content:

```bash
node <PROJECT_DIR>/scripts/finalize-timing.mjs \
  --project <PROJECT_DIR> \
  --scenes cover:7.42,evidence:9.18
```

Then replace the marked content slots and attach media:

- Scene-keyed voice files: use one uniquely identified `<audio>` per returned line, grouped as `voiceover` when there are several clips.
- One continuous voice file: mount it once across the host timeline. Scene starts come from its transcript or word timings; do not split or duplicate it.
- Talking avatar: replace the scene's empty `<div class="presenter-media" data-presenter-media="pending">` with a timed `<video class="presenter-media clip" muted playsinline>`, and add a separate uniquely identified `<audio>` using the same source. HyperFrames owns both; never call `play()`, `pause()`, or seek in script.
- Reused long avatar source: set `data-media-start` to that scene's measured source offset and `data-duration` to the scene range. Multiple scene mounts may point at the same source file.
- Never play the avatar video's embedded audio and a duplicate narration track together. The video stays muted; the separate audio element carries sound.
- Put `data-start` on the media or its plain wrapper, not both. Keep the avatar and its audio on the same scene-local window.
- Verify the take before mounting it: it must carry real alpha, not a matte painted onto opaque pixels. A clip that arrives with a baked background was generated at the wrong screen style and is regenerated, not keyed by hand.

Motion is fitted inside the real speech window. The presenter container remains still; the generated performance supplies human movement. Run Preflight only after media is mounted, then continue the normal Static and Preview review.
