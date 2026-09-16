# Screen recording: polish the take the user already made

Read this when a video attachment ships a synchronized same-stem `.clicks.json` sidecar — `demo.mp4` with `demo.clicks.json` — and the deliverable is that recording, polished. The sidecar is a real capture artifact, not a hint to interpret: it carries the click timeline the camera work is built from. `okou video camera` renders the whole video locally from the recording plus the sidecar, so this route buys no provider job and no generation credits until narration is added.

This route reframes the recording and changes nothing else. A request to restyle the product story, re-shoot the flow, or narrate a newly authored video is native or controlled work that merely has a recording attached; the recording is then an ordinary video input under [input preparation](input-preparation.md).

One division of labour governs the whole route, and most of its cost comes from breaking it. **`okou video camera` plans the video and arithmetic checks the plan; you judge what neither can — whether a framing is on the right subject and reads.** Planning the video a second time, whether by hand or by writing something to search the framing space, competes with the command that already did it and costs more than everything else here combined.

## Step 1 — Probe both files before planning

Read `okou video camera --help` for the installed interface; it requires `ffmpeg` and `ffprobe` on PATH. Then probe once and cache:

- the recording: container, duration, dimensions, frame rate, and **whether the audio track carries anything**. A desktop capture often ships a digitally silent track (`volumedetect` reporting about -91 dB). Silence is not `Original audio`: say so before promising the source track;
- the sidecar: `recording` (capture geometry and `content.pixelRect`), `clicks[]` (`tMs`, `frame`, `element.role`), `droppedOutOfFrameClicks`, and `warnings[]`.

`droppedOutOfFrameClicks` is the floor for what any plan can cover: those clicks landed outside the captured content and no framing brings them back.

A desktop capture is usually variable frame rate: `avg_frame_rate` and `r_frame_rate` disagree and the real frame count sits well below duration × nominal fps. Any later frame-index work must put an `fps=` filter ahead of the selection, or indices computed from the timeline address frames the file does not contain and the extraction silently comes up short:

```bash
ffmpeg -i recording.mp4 -vf "fps=30,select='eq(n\,150)+eq(n\,420)'" -vsync 0 frame_%03d.jpg
```

The sidecar carries two different geometries and only one of them is pixel-accurate. `clicks[].frame` is the click position the renderer consumes. `clicks[].element.frame` is accessibility geometry and has been observed tens of pixels off the rendered pixels on a macOS capture, so do not compose against it.

A capture usually also carries the recording tool's own control bar: a contiguous dark band a few tens of pixels tall, present in every frame, belonging to no part of the product. It is not `content` padding and the sidecar does not describe it, so nothing warns you about it — and because the renderer shows the full source frame before the first key, an unguarded plan opens and closes on it. Measure its extent before planning and keep every `rect` clear of it. Identify it by the **longest unbroken run** of dark pixels in a row, not by how many dark pixels the row holds: a bar narrower than a third of the frame is a small fraction of any row, so a percentage threshold reads it as ordinary UI.

## Step 2 — Render the automatic first cut

```bash
okou video camera --file recording.mp4 --events recording.clicks.json --output build/draft.mp4
```

It writes the MP4, an editable `*.camera-plan.json`, a `*.camera-review.json` manifest, and a directory of paired source/output checkpoint JPEGs, then prints their paths with `durationMs`, `cameraShots`, `cameraMoves`, `clicksOutsideFrame`, and `renderMs`. Exactly one of `--events` or `--plan` is accepted. Expect roughly a minute of local render per 20–30 seconds of 1080p-class footage; budget for two or three passes rather than one perfect plan.

Keep this cut. It is the algorithm's own answer, it costs nothing to deliver alongside the refined one, and the comparison is what shows the refinement was worth making. It is also the only render that emits click-moment checkpoint frames: a plan render places checkpoints on move boundaries alone, so this is the only click-level acceptance evidence the renderer produces.

## Step 3 — Review the first cut on frames, not on counts

Open the checkpoint frames named in the review manifest. They are the acceptance evidence: `clicksOutsideFrame` says nothing about whether the clicked control is legible, whether a dialog's edge spills into the page behind it, or whether the payoff frame keeps the text the video exists to show.

Open them in batches. A 3×3 tile of nine output frames scaled to 2560px wide stays legible down to button labels, because the camera move has already magnified them 1.6–2.5×; one look covers a whole pass, where reading them singly costs a round trip each. Unmagnified source frames take a 2×2 at the same width. Reserve a full-size read for the one or two frames the tile shows as wrong.

```bash
ffmpeg -i cp-005-output.jpg -i cp-013-output.jpg -i cp-018-output.jpg \
       -i cp-026-output.jpg -i cp-033-output.jpg -i cp-041-output.jpg \
       -i cp-046-output.jpg -i cp-051-output.jpg -i cp-059-output.jpg \
  -filter_complex "[0:v][1:v][2:v]hstack=3[a];[3:v][4:v][5:v]hstack=3[b];\
[6:v][7:v][8:v]hstack=3[c];[a][b][c]vstack=3,scale=2560:-2" -frames:v 1 tile.jpg
```

Read the manifest's `clicks[].inFrame` against the Step 1 floor: matching `droppedOutOfFrameClicks` is a pass, anything above it is a framing to fix. A click can be flagged while plainly visible — the check wants margin, not mere containment, measured in output pixels, so a click near the top of the frame needs a tighter shot to clear it. The threshold is undocumented and sits near 125 output pixels: aim for about 155, and treat anything under 130 as a framing to fix.

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
- `baseZoom` does **not** do what its name promises: it is inert. The renderer shows the full source frame before the first key whatever it is set to. Give every plan an explicit opening key, or the video opens on the raw capture, recording control bar and all.

`--events` and `--plan` are mutually exclusive, and that has one consequence worth stating plainly: **a plan render carries no click timeline at all.** Its review manifest reports `clicks: []` and `clicksOutsideFrame: 0` — zero out of zero, not zero out of twelve. The field looks exactly like the Step 3 check passing, and it is not a check. Accept a refined plan against computed margins and against output frames sampled at each `clickMs`; never against that number.

Edit for rest, not for coverage: group clicks that share a region under one framing, hold it while the interface responds, and spend the moves on the beats that carry meaning — the choice being made, the state that changed, the final screen. Align each shot's edges to the thing being shown (a dialog's own border, the full chip, the button and its label) so nothing important is half-cut. Verify on frames at the click moments rather than on the plan render's own checkpoints, which land on move boundaries and can miss every moment that matters.

### Check the plan without rendering, then judge what is left on one tile

`--events` has already planned the video. What is left is judgement, which is the part no plan file can do for itself: whether a framing actually reads. The automatic plan is usually right about *where* each beat sits and wrong only about how tightly it is held, so correct it rather than re-deriving framings from scratch — a re-derived plan costs far more and starts from less.

At a hold — and every click lands on one — the renderer does nothing more than crop `rect` out of the source and scale it to the output size. So any framing, the plan's or one you are considering, can be previewed by cropping the source directly, in a fraction of a second, with no render at all:

```bash
# height follows the source aspect ratio: width * source_height / source_width
ffmpeg -ss <clickMs/1000> -i recording.mp4 -frames:v 1 \
  -vf "crop=<width>:<height>:<x>:<y>,scale=<out_width>:-2" -q:v 2 preview.jpg
```

That preview is exact rather than indicative: measured against the rendered frame it differs by 2–4 grey levels, which is the resampling noise floor, while a crop misplaced by as little as 3 px differs by twice that. Use it for every check below and keep renders for delivery.

**Resolve what is arithmetic before looking at anything.** Timing and clipping are measurable, and most of what an automatic plan gets wrong is one of the two:

- a move that lands after its own `clickMs`;
- a `rect` reaching into the capture overlay, or outside `content`;
- a click closer to an edge than the margin threshold;
- an edge falling inside a run of non-background pixels — that is a clipped word, chip or card, and the nearest gap is the fix.

All four are arithmetic over the plan, the sidecar and one greyscale frame per beat. Settle them in a single pass and apply them in one edit, before spending a look on them.

This pass **detects and nudges; it does not search**. Each defect has one smallest edit that clears it — move the edge to the nearest gutter, start the key earlier, raise the zoom just enough for the click to clear the margin — and that edit is the whole fix. The moment it turns into scoring candidate rectangles, or re-solving `x`, `y` and zoom together, it has become a second planner competing with `--events`, and it will cost more than the rest of the route put together. Change the one number the defect names and move on.

**Then use the tile for the judgement that is actually left.** The division of labour is the point of this step: arithmetic checks every beat, because that costs nothing, and the reader checks a *representative* sample, because that is what costs. Crop a preview for each beat the arithmetic pass touched, plus the opening, the payoff and the closing beat; tile them and read the tile once. Judge only what a number cannot — whether the shot is on the right subject, whether it reads at that size, whether two beats are really one shot, and whether the closing frame shows the result rather than a cursor.

Sampling here is deliberate rather than a shortcut. Reading every beat turns each incidental observation into another correction round, and those rounds, not the reading, are where this step's time goes. What matters and is not sampled has already been checked by the arithmetic, which did look at all of them.

```bash
python3 - <<'PY'
import json, subprocess
plan = json.load(open("build/draft.camera-plan.json"))
src = plan["source"]; keys = plan["shots"][0]["keys"]
for i, c in enumerate(json.load(open("recording.clicks.json"))["clicks"]):
    k = [x for x in keys if x["startMs"] + x["durationMs"] <= c["tMs"]][-1]
    r = k["rect"]; w = r["width"]; h = w * src["height"] / src["width"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{c['tMs']/1000:.3f}",
                    "-i", "recording.mp4", "-frames:v", "1", "-q:v", "2",
                    "-vf", f"crop={w:.0f}:{h:.0f}:{r['x']:.0f}:{r['y']:.0f},scale=960:-2",
                    f"build/f_{i:02d}.jpg"], check=True)
PY
ffmpeg -v error -y -f image2 -i build/f_%02d.jpg -vf "scale=640:418,tile=4x3" -frames:v 1 build/tile.jpg
```

Scale the cells to an exact size rather than with `-2`: crops of different widths round to heights that differ by a pixel, and `tile` then silently composites only the first input and leaves the rest of the grid empty. The tile looks plausible and is missing almost every frame you meant to check.

Record a verdict for every beat before changing anything — **and with each verdict, the number the fix will need**: the gap a left edge should land on, the true extent of the chip being clipped, the bounds of the dialog in play. A verdict alone is not actionable, and discovering that one beat at a time turns a single review into a chain of measure-judge-measure rounds, which is where this step's time actually goes. Collect the whole list from the one read, resolve it in **one** measurement pass, then apply every correction in one edit of the plan.

Each verdict maps to one mechanical change to a `rect` that already exists, so nothing has to be solved again:

| What the frame shows | Correction to the existing key |
|---|---|
| A word, chip or card cut at a side edge | widen `width` about its centre, or shift `x` onto the nearest measured gap |
| The clicked control too small to read | reduce `width`, keeping every click of the beat clear of the edges |
| The cursor mid-move when the click fires | move the key earlier so `startMs + durationMs` lands before `clickMs` |
| Two adjacent keys on the same region | drop one and extend the other across both clicks |
| Opening or closing frame showing capture chrome | add an explicit opening or closing key inside the safe area |
| Subject against one edge with dead space opposite | re-centre on the block being used, not on the click coordinate |

Anchor a framing on the **UI block in play** — the dialog, the card, the composer — rather than on the click coordinate or on the busiest part of the screen. A click coordinate centres the shot on a point and slices whatever sits beside it; the busiest region pulls the shot towards whatever carries the most ink, which is usually a list or a sidebar rather than the control being used.

Two edits that fail quietly and cost a pass each: `sed` on the plan, where a pattern that does not match leaves the old rect in place, and a key inserted by hand, which is rejected at render time unless it carries every field the generated keys carry — copy an existing key and change it rather than writing one. Edit the plan as JSON, then assert it against itself **before** rendering — every `rect` inside the safe area, every `startMs + durationMs` earlier than its `clickMs`, and every click's distance to each edge in output pixels. All three are arithmetic over the plan file and the sidecar, they take no render, and each one of them is a defect that otherwise costs a full pass to find.

Two renders is the budget: the automatic cut and the delivered one. Nothing in between needs rendering — a revised framing is a crop, so trying one costs a second rather than a minute, and confirming the whole corrected plan costs about ten. A third render means something was rendered before it was checked.

### The pass is finished when all of these hold

Check them once and stop. Framing has no natural stopping point, and a further look will always find something worth another edit; these are the conditions that make the cut deliverable, and beyond them the route is spending time rather than earning it.

- every move lands before its own `clickMs`;
- every `rect` sits inside `content` and clear of the capture overlay;
- every click clears the margin threshold in output pixels;
- no `rect` edge falls inside a run of non-background pixels at any click;
- the opening and closing keys are explicit, and show the product rather than capture chrome;
- the sampled beats read: the shot is on the subject in play, and legible at that size;
- the delivered render matches the plan at the sampled click moments.

To place an edge exactly, measure it; do not estimate it by eye. One row of greyscale pixels names every card gap, dialog border and padding edge to the pixel, and a column does the same for top and bottom:

```bash
ffmpeg -ss <t> -i recording.mp4 -frames:v 1 -vf "crop=<width>:1:0:<y>,format=gray" -f rawvideo -
```

Runs of bright values are the gaps between cards and the dialog's own background; runs of dark values are thumbnails and text rows; the first long run of pure black at the right names `content`'s edge and cross-checks the sidecar. Sweep a range of rows rather than probing one, counting non-background pixels per row: the text bands, image bands and the gaps between them fall out of the profile without having to guess which row to read first. Eyes are for judging whether a composition reads, not for reading coordinates off a frame.

## Step 5 — Add audio only if the brief asks for it

The recording's own track is preserved by default. When the user wants narration over it, write the lines against the recording's timeline — the video's length is fixed, so the script is sized to it rather than the other way round.

Generate one clip per line through the managed command in [controlled composition](controlled-video.md), resolving a concrete `voice_id` from [catalogs](catalogs.md) in the brief's language. A run may hold at most **three built-in generations in flight**; more return 429, so batch the lines in threes. Each clip carries a short pad of silence at both ends, so place clips by measured speech onset rather than by file start, and check the placement against the click times before mixing. Mix once, normalize, and leave the video stream untouched — the duration of the delivered file still matches the source recording unless the user asked for an ending hold.

## Step 6 — Accept and deliver

Apply the default technical check in [QA](qa.md): probe the rendered file and confirm the duration still matches the source, the stream decodes, and any added narration is present and at level. A contact sheet across the whole timeline (`fps=2`) is the cheap way to confirm no shot went blank or stalled mid-move.

Deliver the refined cut as the result and the automatic first cut alongside it, each labelled, plus the silent version when narration was added. Report the measured duration and dimensions, and state the recording's native aspect ratio when it is not a standard 16:9 — a screen capture is delivered at its own shape rather than padded or stretched into one. Say plainly which framings you changed and why, and name anything the sidecar could not cover.
