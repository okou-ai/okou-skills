# Screen recording: polish the take the user already made

Read this when a video attachment ships a synchronized same-stem `.clicks.json` sidecar — `recording.mp4` with `recording.clicks.json` — and the deliverable is that recording, polished. The sidecar is a real capture artifact, not a hint to interpret: it carries the click timeline the camera work is built from. `okou video camera` renders the whole video locally from the recording plus the sidecar, so this route buys no provider job and no generation credits until narration is added.

This route reframes the recording and changes nothing else. A request to restyle the product story, re-shoot the flow, or narrate a newly authored video is native or controlled work that merely has a recording attached; the recording is then an ordinary video input under [input preparation](input-preparation.md).

**`okou video camera` decides the camera work.** Check the cut it produces, fix the framings that do not read, and leave the rest alone.

## Step 1 — Probe both files before planning

Read `okou video camera --help` for the installed interface; it requires `ffmpeg` and `ffprobe` on PATH. Then probe once and cache:

- the recording: container, duration, dimensions, frame rate, and **whether the audio track carries anything**. A desktop capture often ships a digitally silent track (`volumedetect` reporting about -91 dB). Silence is not `Original audio`: say so before promising the source track;
- the sidecar: `recording` (capture geometry and `content.pixelRect`), `clicks[]` (`tMs`, `frame`, `element.role`), `droppedOutOfFrameClicks`, and `warnings[]`.

`droppedOutOfFrameClicks` is the floor for what any plan can cover: those clicks landed outside the captured content and no framing brings them back, so they are not framings to fix in Step 3.

The sidecar carries two different geometries and only one of them is pixel-accurate. `clicks[].frame` is the click position the renderer consumes. `clicks[].element.frame` is accessibility geometry and has been observed tens of pixels off the rendered pixels on a macOS capture, so do not compose against it.

A capture usually carries the recording tool's own control bar too — a dark band at the top of every frame, belonging to no part of the product. It is not `content` padding and the sidecar does not describe it, so it stays visible in the output.

## Step 2 — Render the cut

```bash
okou video camera --file recording.mp4 --events recording.clicks.json --output build/cut.mp4
```

It writes the MP4, an editable `*.camera-plan.json`, a `*.camera-review.json` manifest, and a directory of paired source/output checkpoint JPEGs, then prints their paths with `durationMs`, `cameraShots`, `cameraMoves`, `clicksOutsideFrame`, and `renderMs`. Exactly one of `--events` or `--plan` is accepted.

## Step 3 — Check every framing, fix the ones that fail

Sample one output frame per `clickMs`, plus the opening and closing framings, tile them, and read the tile once:

```bash
python3 - build/cut.mp4 <<'SAMPLE'
import json, subprocess, sys
video = sys.argv[1]
clicks = [c["tMs"] / 1000 for c in json.load(open("recording.clicks.json"))["clicks"]]
# the opening and closing framings carry no click, so seek to them explicitly
seeks = [["-ss", "0.2"], *[["-ss", f"{t:.3f}"] for t in clicks], ["-sseof", "-0.2"]]
for i, seek in enumerate(seeks):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *seek, "-i", video,
                    "-frames:v", "1", "-q:v", "2", f"build/f_{i:02d}.jpg"], check=True)
SAMPLE
ffmpeg -v error -y -f image2 -i build/f_%02d.jpg -vf "scale=640:418,tile=4x4" -frames:v 1 build/tile.jpg
```

The `4x4` above fits twelve clicks plus the two bookend frames; size the grid to however many the sidecar holds. Scale the cells to an exact size rather than with `-2`: crops of different widths round to heights that differ by a pixel, and `tile` then silently composites only the first input, leaving a grid that looks plausible and is missing almost every frame you meant to check.

Ask one question of each frame — the one that decides whether a framing works:

> **Could someone seeing this for the first time still say which panel, menu or area the action is happening in?**

A framing that fails is either too tight or aimed at the wrong thing. Widening is usually the fix: the click lands on a control, but the subject is the panel, card or dialog that contains it, and a shot that crops that away leaves the viewer unable to place the action.

Change only the keys that failed. The plan is JSON, and rendering it back is the supported loop:

```bash
okou video camera --file recording.mp4 --plan build/cut.camera-plan.json --output build/final.mp4 --force
```

- `rect` is `{x, y, width}` in the source video's pixel space; height follows the source aspect ratio, so zoom is `source.width / rect.width`.
- Keep every `rect` inside `content`, or the shot shows the capture's own padding.
- Keep every `rect` below the control bar from Step 1: widening a shot towards the top is what brings that bar into frame.
- A move must land **before** its `clickMs`. A key still moving when the click fires shows the click mid-pan.
- A `--plan` render carries no click timeline: its manifest reports `clicks: []` and `clicksOutsideFrame: 0` whatever the framings do. Check a re-render on frames, never on that number.

Re-render to a new path: the command writes a plan beside its output, and rendering over `build/cut.mp4` would overwrite the plan it is reading. Then sample `build/final.mp4` the same way and read that tile once. Leave every framing that already reads.

## Step 4 — Add audio only if the brief asks for it

The recording's own track is preserved by default. When the user wants narration over it, write the lines against the recording's timeline — the video's length is fixed, so the script is sized to it rather than the other way round.

Generate one clip per line through the managed command in [controlled composition](controlled-video.md), resolving a concrete `voice_id` from [catalogs](catalogs.md) in the brief's language. A run may hold at most **three built-in generations in flight**; more return 429, so batch the lines in threes. Each clip carries a short pad of silence at both ends, so place clips by measured speech onset rather than by file start, and check the placement against the click times before mixing. Mix once, normalize, and leave the video stream untouched — the duration of the delivered file still matches the source recording unless the user asked for an ending hold.

## Step 5 — Accept and deliver

Apply the default technical check in [QA](qa.md): probe the rendered file and confirm the duration still matches the source, the stream decodes, and any added narration is present and at level. A contact sheet across the whole timeline (`fps=2`) is the cheap way to confirm no shot went blank or stalled mid-move.

Deliver `build/final.mp4` when Step 3 changed a framing and `build/cut.mp4` when it did not, plus the silent version when narration was added. Report the measured duration and dimensions, and state the recording's native aspect ratio when it is not a standard 16:9 — a screen capture is delivered at its own shape rather than padded or stretched into one.
