---
name: ppt-avatar-video
description: Convert a PPT, PPTX, or PDF directly into a narrated video by preserving each page as a static slide, with an optional transparent talking avatar in a fixed side layout or adaptive overlay. Use for fast deck-to-video requests with voice only or avatar plus voice; do not use for cinematic intros, slide redesign, or tutorial screen recordings.
---

# PPT Narrated Video

Produce the final video quickly. This is a conversion workflow, not a motion-design workflow.

## Scope boundary

- Preserve every source page as a static image in the original order. Voice-only and overlay modes keep the slide full-frame; the two side-by-side modes fit it inside their fixed slide rectangle without cropping.
- Always include the selected narration. Overlay a transparent talking avatar only when the user selected one.
- Use hard cuts between pages by default. Add only a short dissolve when the user explicitly requests it.
- Do not select a design preset, construct an arc, search the HyperFrames catalog, choose blueprints or rules, redesign slides, or author per-slide animation.
- Do not invoke a general intro-video or motion-graphics workflow unless the user explicitly asks for custom motion.
- Default to direct final delivery. Pause for preview approval only when the user asks to review first.

## Preserve the requested configuration

Use the supplied source, aspect ratio, and voice exactly. Treat avatar configuration as optional: never add or choose an avatar when the user supplied only a voice. When an avatar is supplied, preserve its ID, presenter placement, and presenter scale exactly. Do not list or search avatars or voices when compatible identifiers are already supplied.

For avatar mode, map 16:9 to `landscape`, 9:16 to `portrait`, and 1:1 to `square`. Transparent JoggAI output requires `--screen-style 3 --no-caption`. If scale is absent, use a visible presenter width of 14% of the frame. Scale refers to the non-transparent avatar bounds, not the full video canvas.

If an exact supplied avatar or voice is rejected, report that blocker. Never silently substitute another identity or voice.

## Select presenter placement

The product exposes exactly three placement choices. Normalize their prompt labels to these manifest values:

- **`left` — presenter on the left, slide on the right.** This is fixed geometry: presenter visible left `3%`; slide left `20%`, top `11.5%`, width `77%`, height `77%`.
- **`right` — presenter on the right, slide on the left.** This is fixed geometry: slide left `3%`, top `11.5%`, width `77%`, height `77%`; presenter visible right `3%`.
- **`overlay` — presenter over a full-frame slide.** This is the only adaptive mode. Analyze each slide and place the presenter at the less busy bottom corner.

For both fixed side modes, align the visible presenter's bottom edge with the fixed slide rectangle's bottom edge (`11.5%` above the frame bottom). Do not inspect slide whitespace, choose a corner, or move the presenter between pages in these modes.

For overlay, align the visible presenter with the frame bottom. Treat the product prompt's bottom-right wording as the default and tie-break anchor, not as a reason to skip per-slide blank-space detection. If the user's own editing direction separately requires one fixed overlay corner, honor that explicit override and skip adaptive placement.

When placement is genuinely absent, use `left`, matching the product default. Existing manifests without `presenter.placement` remain valid in the builder and retain their legacy full-frame overlay behavior.

## Select the media mode

Choose one mode before starting a billed generation:

- **Avatar mode:** an avatar is explicitly supplied. Generate one transparent talking-avatar WebM. Its audio is also the narration track; do not generate standalone TTS.
- **Voice-only mode:** no avatar is supplied and a voice is supplied. Generate one narration audio file. Do not select a default avatar, create a hidden avatar, download an avatar cutout, or run the alpha-bound probe.

Run the relevant generation type's current help before generation. A provider-specific voice ID is not interchangeable with another provider's voice name. In particular, do not pass a JoggAI `voice-id` to `okou generate voice --voice`. Use a voice-only provider only when it accepts the exact selected voice; otherwise report the unsupported voice-only configuration instead of substituting.

## Fast path

### 1. Rasterize the deck once

For a web-chat upload, download it with `okou web download-file`. Render ordered pages with:

```bash
okou presentation screenshot --input SOURCE --out PROJECT/assets/slides --width WIDTH --height HEIGHT --json
```

Use the requested final frame size, normally 1920x1080. Do not separately convert PPT to PPTX unless text or speaker-note extraction genuinely requires it. Never recreate or restyle a source page.

### 2. Write one narration unit per page

Prefer, in order: user script, speaker notes, visible slide text, then a concise literal description of the page. Keep one sentence or short paragraph per page and preserve page order. Do not invent a marketing story arc merely because the deck is sparse.

Join the page units into one script and retain the page-to-unit mapping. As soon as the script is stable, start exactly one generation job for the selected media mode.

Put long or quote-sensitive narration in a file and pipe it through standard input.

Avatar mode:

```bash
okou generate avatar-video --provider built-in \
  --avatar-id AVATAR_ID \
  --voice-id VOICE_ID \
  --aspect-ratio AVATAR_RATIO \
  --screen-style 3 \
  --no-caption \
  --video-name VIDEO_NAME \
  --json < PROJECT/narration.txt
```

Voice-only mode, when the selected voice is supported by the built-in voice generator:

```bash
okou generate voice --provider built-in \
  --voice VOICE \
  --json < PROJECT/narration.txt
```

While that provider job runs, stage the slide assets and prepare the composition manifest. Run these independent branches concurrently when the execution surface permits it.

### 3. Recover page timings

Download the generated media and probe its exact duration. Use `assets/presenter.webm` in avatar mode and `assets/narration.wav` or the returned audio extension in voice-only mode. Transcribe that media once with `okou video transcribe --file MEDIA` and align each narration unit to its page. Put a cut at the start of the next unit, or at the midpoint of a real silence gap between units. The first page starts at zero and the final page extends through the exact narration duration.

If transcription is unavailable, distribute the measured duration in proportion to spoken word counts, then assign rounding residue to the last page. Do not use the provider's rounded duration when `ffprobe` is available.

### 4. Measure avatar and slide geometry only when needed

Skip this entire step in voice-only mode.

Resolve this skill's mounted directory from the path shown in the available-skills list, then run:

```bash
node SKILL_DIR/scripts/probe-alpha-bbox.mjs PROJECT/assets/presenter.webm
```

Copy its `sourceWidth`, `sourceHeight`, and `bbox` values into the manifest. The composition builder uses CSS clipping and positioning so the visible cutout has the requested width and bottom alignment. Do not crop or transcode the VP9 WebM locally.

For `left` and `right`, stop here: their geometry is fixed and must not run a whitespace detector.

For `overlay` only, probe every slide after the presenter bbox is known:

```bash
node SKILL_DIR/scripts/probe-slide-blank-space.mjs PROJECT/assets/slides \
  --bbox=BBOX_WIDTHxBBOX_HEIGHT \
  --visible-width-fraction=0.14
```

The probe compares visual complexity in the two bottom candidate regions sized to the visible presenter. It chooses `bottom-left` or `bottom-right` per page and keeps the prior side when scores differ by no more than the tie threshold, avoiding needless side-to-side jitter. Copy each returned `presenterAnchor` into the matching slide entry. Do not run the probe for either fixed side mode.

In avatar mode, stage only the final presenter WebM and slide images. Do not keep an uncropped duplicate or an unused still inside the cloud-render project. In voice-only mode, stage only the narration audio and slide images.

### 5. Build the static composition

For a fixed-left layout, create `composition-input.json` using this schema. Use `"placement": "right"` for the mirrored fixed layout; neither mode accepts per-slide anchors.

```json
{
  "id": "deck-video",
  "width": 1920,
  "height": 1080,
  "fps": 30,
  "background": "#000000",
  "hyperframesVersion": "0.8.26",
  "slides": [
    { "path": "assets/slides/page-001.png", "duration": 4.2 },
    { "path": "assets/slides/page-002.png", "duration": 5.1 }
  ],
  "narration": { "path": "assets/presenter.webm" },
  "presenter": {
    "path": "assets/presenter.webm",
    "sourceWidth": 1920,
    "sourceHeight": 1080,
    "bbox": { "x": 618, "y": 184, "width": 596, "height": 874 },
    "visibleWidthFraction": 0.14,
    "placement": "left"
  }
}
```

For adaptive overlay, keep slides full-frame, set `"placement": "overlay"`, and copy the probe result into each page:

```json
{
  "slides": [
    {
      "path": "assets/slides/page-001.png",
      "duration": 4.2,
      "presenterAnchor": "bottom-right"
    },
    {
      "path": "assets/slides/page-002.png",
      "duration": 5.1,
      "presenterAnchor": "bottom-left"
    }
  ],
  "narration": { "path": "assets/presenter.webm" },
  "presenter": {
    "path": "assets/presenter.webm",
    "sourceWidth": 1920,
    "sourceHeight": 1080,
    "bbox": { "x": 618, "y": 184, "width": 596, "height": 874 },
    "visibleWidthFraction": 0.14,
    "placement": "overlay"
  }
}
```

For voice-only mode, omit `presenter` entirely:

```json
{
  "id": "deck-video",
  "width": 1920,
  "height": 1080,
  "fps": 30,
  "background": "#000000",
  "hyperframesVersion": "0.8.26",
  "slides": [
    { "path": "assets/slides/page-001.png", "duration": 4.2 },
    { "path": "assets/slides/page-002.png", "duration": 5.1 }
  ],
  "narration": { "path": "assets/narration.wav" }
}
```

Use the project-pinned HyperFrames version rather than updating during a job. Then run:

```bash
node SKILL_DIR/scripts/build-project.mjs --manifest PROJECT/composition-input.json --out PROJECT
```

The builder creates one `data-no-timeline` root composition with static image clips and one narration audio clip. It adds one persistent transparent video clip for fixed placement or an overlay that stays on one side. When adaptive overlay changes sides, it creates only the minimum consecutive presenter segments and uses `data-media-start` to keep the take synchronized. That marker is the HyperFrames contract for an intentionally static composition; do not add a fake GSAP tween merely to make geometry change. Do not replace the composition with individually authored slide HTML files.

### 6. Run one pre-render gate

After inputs and timing are final, run one `lint`, one strict `check`, and a small snapshot set covering the first, middle, and last pages. Fix failures and rerun only the affected fast check; run the full strict check once more only if composition structure or timing changed.

```bash
npx --yes hyperframes@0.8.26 lint PROJECT --json
npx --yes hyperframes@0.8.26 check PROJECT --strict --samples 5 --json
npx --yes hyperframes@0.8.26 snapshot PROJECT --at FIRST,MIDDLE,LAST --no-end --describe false
```

Do not run text-layout or contrast audits against bitmap slide contents. Those pixels belong to the source presentation and contain no authored DOM text. Verify instead:

- page count and order;
- no stretching or unintended cropping;
- avatar mode: transparent avatar decoding, requested visible width, placement geometry, and captions absent;
- fixed `left` or `right`: one presenter segment, the 77% slide rectangle is on the configured side, and no whitespace-probe output appears in the manifest;
- adaptive `overlay`: slides remain full-frame, every page has a valid probe-derived anchor, and media offsets remain continuous when the side changes;
- voice-only mode: no presenter video element or avatar asset;
- final slide timing equals the narration duration.

### 7. Render in the cloud once

Cloud is the default final renderer. If `HYPERFRAMES_API_KEY` and `HEYGEN_API_KEY` are absent but `HEYGEN_TOKEN` is present, pass it to the command as `HEYGEN_API_KEY="$HEYGEN_TOKEN"` without printing the token.

Run a dry-run size check, then one idempotent render using the same key for any safe retry:

```bash
npx --yes hyperframes@0.8.26 cloud render PROJECT --dry-run --json

HEYGEN_API_KEY="$HEYGEN_TOKEN" npx --yes hyperframes@0.8.26 cloud render PROJECT \
  --fps FPS --quality high --format mp4 --resolution 1080p \
  --aspect-ratio ASPECT --wait --output PROJECT/renders/final.mp4 \
  --idempotency-key IDEMPOTENCY_KEY --json
```

Use local final rendering only when the user explicitly requests it or cloud access is unavailable. Do not render a full local copy merely as a cloud comparison.

### 8. Final verification and delivery

Run `ffprobe`, a full `ffmpeg` decode, and final ASR comparison concurrently where possible. Confirm resolution, fps, frame count, video duration, audio duration, page order, and narration completeness. Confirm presenter placement only in avatar mode, and confirm presenter absence in voice-only mode. For web chat, deliver the verified file with `okou web upload-file -f PROJECT/renders/final.mp4`.

Report a compact timing table with: deck download, page rasterization, narration preparation, media generation, composition build, pre-render QA, cloud package/upload, queue/render, download, final QA, and delivery. Include alpha-bound probe only in avatar mode. Distinguish provider time from agent/tool overhead.

## Retry and cost rules

- Use an idempotency key for every cloud render.
- Retry one transient provider or cloud failure at most once. Do not submit a second billed media generation when the first job may still be running.
- A request to create the final video authorizes one media-generation job for the selected mode and the cloud-render charge. Any materially different regeneration needs fresh user direction.
