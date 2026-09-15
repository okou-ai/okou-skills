# Screen recording: polish the take the user already made

Read this when a video attachment ships a synchronized same-stem `.clicks.json` sidecar — `demo.mp4` with `demo.clicks.json` — and the deliverable is that recording, polished. The sidecar is a real capture artifact, not a hint to interpret: it carries the click timeline the camera work is built from. `okou video camera` renders the whole video locally from the recording plus the sidecar, so this route buys no provider job and no generation credits until narration is added.

This route reframes the recording and changes nothing else. A request to restyle the product story, re-shoot the flow, or narrate a newly authored video is native or controlled work that merely has a recording attached; the recording is then an ordinary video input under [input preparation](input-preparation.md).

## Step 1 — Probe both files before planning

Read `okou video camera --help` for the installed interface; it requires `ffmpeg` and `ffprobe` on PATH. Then probe once and cache:

- the recording: container, duration, dimensions, frame rate, and **whether the audio track carries anything**. A desktop capture often ships a digitally silent track (`volumedetect` reporting about -91 dB). Silence is not `Original audio`: say so before promising the source track;
- the sidecar: `recording` (capture geometry and `content.pixelRect`), `clicks[]` (`tMs`, `frame`, `element.role`), `droppedOutOfFrameClicks`, and `warnings[]`.

`droppedOutOfFrameClicks` is the floor for what any plan can cover: those clicks landed outside the captured content and no framing brings them back.

## Step 2 — Render the automatic first cut

```bash
okou video camera --file recording.mp4 --events recording.clicks.json --output build/draft.mp4
```

It writes the MP4, an editable `*.camera-plan.json`, a `*.camera-review.json` manifest, and a directory of paired source/output checkpoint JPEGs, then prints their paths with `durationMs`, `cameraShots`, `cameraMoves`, `clicksOutsideFrame`, and `renderMs`. Exactly one of `--events` or `--plan` is accepted. Expect roughly a minute of local render per 20–30 seconds of 1080p-class footage; budget for two or three passes rather than one perfect plan.

Keep this cut. It is the algorithm's own answer, it costs nothing to deliver alongside the refined one, and the comparison is what shows the refinement was worth making.

## Step 3 — Review the first cut on frames, not on counts

Open the checkpoint frames named in the review manifest. They are the acceptance evidence: `clicksOutsideFrame` says nothing about whether the clicked control is legible, whether a dialog's edge spills into the page behind it, or whether the payoff frame keeps the text the video exists to show.

Read the manifest's `clicks[].inFrame` against the Step 1 floor: matching `droppedOutOfFrameClicks` is a pass, anything above it is a framing to fix. A click can be flagged while plainly visible — the check wants margin, not mere containment, measured in output pixels, so a click near the top of the frame needs a tighter shot to clear it.

What an automatic plan typically gets wrong: one move per click regardless of how close the clicks are, so the camera never rests; a uniform zoom that crops a dialog or a chip at the exact moment it matters; and a final framing chosen for the last click rather than for the result the viewer should read.

## Step 4 — Edit the plan and re-render

The plan is JSON and rendering it back is the supported loop:

```bash
okou video camera --file recording.mp4 --plan build/final.camera-plan.json --output build/final.mp4 --force
```

Each `shots[].keys[]` entry is one move: it starts at `startMs`, runs for `durationMs`, and lands on `rect`. What the fields mean:

- `rect` is `{x, y, width}` in the source video's pixel space; height follows the source aspect ratio. Zoom is `source.width / rect.width`, so a 1920-wide source framed at `width: 960` is a 2× push.
- `content` can be narrower than the video — a capture may carry padding at one edge. Keep every `rect` inside `content` or the shot shows the padding.
- a move must **land before** its `clickMs`, not on it. A key whose motion is still running when the click fires shows the click mid-pan and reports it out of frame.
- `baseZoom` is where the camera sits before the first key and after a pull-back.

Edit for rest, not for coverage: group clicks that share a region under one framing, hold it while the interface responds, and spend the moves on the beats that carry meaning — the choice being made, the state that changed, the final screen. Align each shot's edges to the thing being shown (a dialog's own border, the full chip, the button and its label) so nothing important is half-cut. Re-render, then re-read the same checkpoint frames; a plan that no longer flags a click can still have introduced a worse composition.

## Step 5 — Add audio only if the brief asks for it

The recording's own track is preserved by default. When the user wants narration over it, write the lines against the recording's timeline — the video's length is fixed, so the script is sized to it rather than the other way round.

Generate one clip per line through the managed command in [controlled composition](controlled-video.md), resolving a concrete `voice_id` from [catalogs](catalogs.md) in the brief's language. A run may hold at most **three built-in generations in flight**; more return 429, so batch the lines in threes. Each clip carries a short pad of silence at both ends, so place clips by measured speech onset rather than by file start, and check the placement against the click times before mixing. Mix once, normalize, and leave the video stream untouched — the duration of the delivered file still matches the source recording unless the user asked for an ending hold.

## Step 6 — Accept and deliver

Apply the default technical check in [QA](qa.md): probe the rendered file and confirm the duration still matches the source, the stream decodes, and any added narration is present and at level. A contact sheet across the whole timeline (`fps=2`) is the cheap way to confirm no shot went blank or stalled mid-move.

Deliver the refined cut as the result and the automatic first cut alongside it, each labelled, plus the silent version when narration was added. Report the measured duration and dimensions, and state the recording's native aspect ratio when it is not a standard 16:9 — a screen capture is delivered at its own shape rather than padded or stretched into one. Say plainly which framings you changed and why, and name anything the sidecar could not cover.
