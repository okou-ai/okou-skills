---
name: video-motion-template
description: Okou-branded intro and outro motion templates for product videos. Use this skill when a video needs a fixed brand opening or closing — 36 deterministic 16:9 templates with the official Okou wordmark, configurable colourway, terminal hold, direction and action speed, plus a seek-and-capture player for frame-accurate rendering.
---

# Video Motion Template

36 approved brand-motion templates that bracket a product video: a short appearance at the head, the same identity at the tail. Every template is a deterministic browser composition — seek to a time, get the same frame — so intros and outros can be captured, rendered or previewed without a video editor.

The package lives in `package/`. Serve it over static HTTP(S); no build step, no account, no API key.

## Inventory

| Collection | Count | IDs | Runtime |
| --- | --- | --- | --- |
| Brand compositions | 12 | `brand-*` (VM-01 … VM-12) | GSAP / Three.js HTML timelines |
| Reveal templates | 24 | `reveal-*` (VM-13 … VM-36) | Canvas 2D, no external dependency |

`package/templates/manifest.json` is the machine-readable inventory: stable ID, display code, use case, exact default timing, supported controls, provenance and preview image. Names repeat across motion families — always address a template by its stable ID.

Defaults: 1920 × 1080, 16:9, no audio, Okou preset, dark colourway, standard speed, appearance, 0.25 s terminal hold.

## Pick a template

1. Read `package/templates/manifest.json` and match the request against `useCase`, `family` and `collection`.
2. For a repeatable, low-risk opener prefer `brand-mask-sweep-lockup` (VM-01); for a closing beat prefer `brand-stroke-draw-lockup`; for an energetic assembly prefer `reveal-particles`.
3. Show the gallery when the user should choose: open `package/templates/index.html`, or the hosted library at https://okou-video-motion-templates.okou.app.

## Configure and capture

Open a clean, UI-free player with query parameters:

```
package/templates/player.html?template=brand-mask-sweep-lockup&theme=dark&hold=0.25&placement=intro
package/templates/player.html?template=reveal-particles&theme=light&hold=0.25&speed=standard&direction=out&placement=outro
```

The player starts paused at time zero; add `autoplay=1` for ordinary playback. Wait for `window.VideoMotionTemplate.ready` before reading state or capturing a frame. The API uses seconds:

```js
await VideoMotionTemplate.ready;
await VideoMotionTemplate.configure({
  templateId: 'reveal-particles',
  brandPreset: 'okou',
  placement: 'intro',
  theme: 'dark',
  holdSeconds: 0.25,
  speed: 'standard',
  direction: 'in'
});
VideoMotionTemplate.seek(0.6);                       // pauses on a deterministic frame
const { duration, formationSeconds } = VideoMotionTemplate.state();
const clip = VideoMotionTemplate.recipe();           // video-motion-clip/v1
```

Capture at a 1920 × 1080 viewport to match the reviewed stage. To assemble a product video: render the selected intro, append the product body, then render the selected outro. Use the duration reported by the configured player instead of padding to an assumed common length.

## Controls

| Control | 12 brand compositions | 24 reveal templates |
| --- | --- | --- |
| Placement | Intro or outro | Intro or outro |
| Colourway | Dark or light | Dark or light |
| Terminal hold | 0, 0.25 or 0.5 s | 0, 0.25 or 0.5 s |
| Motion | Appearance | Appearance or reverse exit |
| Action speed | Reviewed speed | Fast, standard or slow |

Placement is metadata: choosing outro places the same brand appearance at the end. Reverse exit is a separate setting, available on the 24 reveal templates. For an appearance the hold contains the complete brand; for an exit it contains the empty background. Changing the hold never stretches the formation.

## Identity

The preset is Okou, drawn from the official identity: the wordmark uses the logotype outlines shipped as `package/assets/okou-motion.otf` (icon + `kou`), the mark uses the official icon contour, and the palette is `#242121` ink, `#FAF5F3` paper and `#F8A101` accent. Geometry is a 156 px icon, a 26.35 px gap and a -20.06 px optical offset.

Swapping in another brand is not a runtime control. A new identity needs a coordinated source adaptation — logotype outlines, measured geometry, mark contour and regenerated particle/bitmap samples — so traced, sliced and particle states stay consistent with the final frame.

## Dependencies and limits

- The 12 brand compositions load pinned GSAP and Three.js from their existing CDNs, so they need network access; the 24 canvas templates have none.
- Templates render 16:9 with no audio track and ship no MP4 master. Render one with the capture flow above, or with a HyperFrames/headless-browser frame capture.
- Licensing and upstream provenance for the brand compositions are recorded in `package/refined/NOTICE.md` and `package/refined/HyperFrames-LICENSE.txt`.
