# Adaptive Presenter Planning

Use this guide after this system is selected and before scene geometry is authored. It governs whether a presenter exists, how the person returns, and how content fits around the standard-size full or grounded head-and-shoulders treatment. A presenter here is always a generated talking-avatar video with a transparent background; the composition supplies everything behind the person. It does not create a scene schema or a layout renderer.

## Resolve one video-level choice

Set the top-level composition to exactly one of these values:

```html
<div id="root" data-video-presenter="off">...</div>
<div id="root" data-video-presenter="on">...</div>
```

- `off`: presenter DOM is structurally absent from every scene. Do not mount a hidden `.presenter-slot`, reserve an empty person bay, or stage a presenter-only scene. Every content scene uses the full safe frame and centers its complete required-content box.
- `on`: the sequence includes a deliberate presenter recurrence plan, while individual scenes may still use `data-presenter="off"`. The presenter is not required to coexist with every chart, text system, map, or media block.

A talking avatar carries its own voice and duration, so follow [VOICE-AVATAR.md](VOICE-AVATAR.md): its measured media duration determines the scene.

Use the user's explicit choice. If no choice is present, ask one short question before scene planning. Do not silently convert `on` to an effectively presenter-free video, and do not silently add a presenter to `off`.

## Plan recurrence by narrative need

An `on` video should feel intentionally presenter-led, but the template does not calculate a required count. Let the person introduce an idea, return after several content-only scenes, clarify a transition, or deliver a final instruction when those appearances improve comprehension. A short sequence may need one strong appearance; a longer explanation will usually benefit from several separated returns.

If dense or full-canvas content prevents coexistence, use a nearby presenter-led divider scene when it helps the narrative. Do not add a divider merely to satisfy a quota, and never reduce or crop the content to keep the presenter on screen.

## Use a fixed representation ladder

For every selected presenter scene, evaluate representation in this order:

1. Try the complete `full` presenter at the template's standard size. Keep the entire supplied media or meaningful alpha bounds visible.
2. Switch the person to the opposite side if the content relationship allows it. Do not reduce the full-presenter size to create room.
3. If a full person does not fit, use `head-shoulders` only when a bottom-left or bottom-right safe corner is naturally clear. Keep it grounded on the bottom edge and use the template's soft transparent circular fade.
4. If neither representation fits, move the appearance to a presenter-led divider or omit it from this scene.

Do not float a head-and-shoulders crop at mid-height, place it away from a bottom safe corner, or use a hard crop. Do not shrink a full person as an intermediate fallback.

## Choose one scene relationship

Presenter-free content scene:

```html
<main class="vc-frame" data-presenter="off" data-title-chrome="off">
  <section class="vc-content-stage">...</section>
</main>
```

Presenter scene:

```html
<main
  class="vc-frame"
          data-presenter="on"
          data-presenter-layout="side-right"
          data-title-chrome="off"
>
  <section class="vc-content-stage">...</section>
  <div class="presenter-slot" data-presenter-crop="full" data-face-safe="true">
    <div class="presenter-media" data-presenter-media="pending"></div>
  </div>
</main>
```

For a talking avatar, keep the same geometry but replace the image with framework-owned media. The visual video is muted and the separate audio element carries its sound:

```html
<div class="presenter-slot" data-presenter-crop="full" data-face-safe="true" data-presenter-media="talking-avatar">
  <video id="avatar-briefing" class="presenter-media clip" src="avatar-long.mp4" data-start="0" data-duration="7.42" data-media-start="18.6" muted playsinline></video>
</div>
<audio id="avatar-briefing-audio" src="avatar-long.mp4" data-start="0" data-duration="7.42" data-media-start="18.6" data-track-index="10" data-volume="1"></audio>
```

`data-media-start` is the source offset for a virtual segment. Omit it for a scene-keyed file that starts at zero. Prefer this ranged mount over physically cutting and re-encoding a long avatar file.

Side and corner relationships require transparent or background-removed avatar media. If the generated clip has a baked background, use it as a presenter-led full-media divider instead of forcing the rectangle into a presenter lane.

Compact head-and-shoulders scene:

```html
<main class="vc-frame" data-presenter="on" data-presenter-layout="corner-right" data-title-chrome="off">
  <section class="vc-content-stage">...</section>
  <div class="presenter-slot" data-presenter-crop="head-shoulders" data-face-safe="true">
    <div class="presenter-media" data-presenter-media="pending"></div>
  </div>
</main>
```

Choose the relationship from the message and the installed HyperFrames item:

| Layout | Use when | Content behavior |
| --- | --- | --- |
| `divider-left`, `divider-right` | The presenter leads a section break, framing statement, or explanation with little supporting content | Presenter is dominant; concise content centers in the opposite region |
| `side-left`, `side-right` | Text, a partial-region chart, comparison, or process remains primary and benefits from a nearby speaker | Content is dominant; the shared CSS reserves a proportional presenter lane |
| `corner-left`, `corner-right` | A full presenter does not fit but a naturally clear bottom corner can hold a head-and-shoulders speaker without covering content | Content keeps the broad stage; the soft circular crop stays grounded on the bottom edge |
| presenter-free | The content needs the complete canvas, the presenter adds no meaning, or whole-media coexistence weakens clarity | Content returns to the full safe frame and centers on both axes |

Never put a full-canvas 1920×1080 Registry block into a presenter sidecar region. Keep that scene presenter-free and place the speaker in a preceding or following divider, or choose an official component genuinely designed for a partial region.

## Choose representation, not scale

`data-presenter-crop="full"` shows the entire supplied presenter media or meaningful alpha bounds at the template's standard size. Do not add a scale variant, reduce the slot, zoom the media, or clip an edge to force coexistence.

`data-presenter-crop="head-shoulders"` is the only cropped alternative. It must:

- use `corner-left` or `corner-right`;
- touch the bottom edge rather than float;
- retain the face, neck, and shoulders;
- use the supplied soft transparent circular fade rather than a hard border;
- remain clear of text, charts, labels, connectors, citations, and media.

If those conditions fail, move the presenter to a divider or omit it from the scene.

## Content-fit guidance

Inspect every presenter scene directly in its intended settled state and at peak motion. The presenter is a good fit when:

- all required content remains visible and readable;
- the content is vertically centered inside its available region;
- face, hands, labels, axes, legends, connectors, citations, and media remain disjoint;
- neither the presenter nor the content is clipped at rest or at peak motion.

If the complete person weakens the composition, switch sides or use the grounded head-and-shoulders treatment. If that still fails, move the presenter to a divider scene or remove it from this scene. Do not shrink the full person or reduce critical copy below the readability floor to preserve coexistence.

## Motion boundary

The presenter's own generated performance supplies its motion. Keep the presenter container spatially settled from the scene's first frame; do not add generic entrance, floating, bobbing, or exit animation. HyperFrames motion belongs to the semantic content layer. A cut from a presenter-free scene to a presenter scene is enough to create a return.

## Review prompts

- `data-video-presenter="off"`: no `.presenter-slot` nodes and no empty presenter bay across the assembled composition.
- `data-video-presenter="on"`: appearances feel deliberate across the explanation rather than accidental or compulsory.
- Every presenter-free scene uses the full safe content region with no empty presenter bay.
- Every presenter scene declares one supported layout and either `data-presenter-crop="full"` or `data-presenter-crop="head-shoulders"`; no presenter scale attribute exists.
- Every talking-avatar video is muted, paired with one uniquely identified audio element, and uses the measured media duration without duplicate narration.
- Every `head-shoulders` presenter is grounded in a bottom safe corner, uses the soft transparent circular fade, and retains face, neck, and shoulders without a hard edge.
- No floating crop, arbitrary intermediate crop, or downscaled full presenter exists in the assembled composition.
- Full-canvas Registry blocks never coexist with a presenter.
- The presenter remains replaceable by transparent image or video without rewriting scene geometry.
