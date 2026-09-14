# Video Motion Templates v1

36 approved motion templates for product-video intros and outros, using the official Okou brand preset. The collection contains 12 refined brand compositions and 24 reveal studies. The recovered archives and older Okou originals are reference material, outside this template release.

Live library: https://okou-video-motion-templates.okou.app

## Template contract

`manifest.json` is the portable inventory for this artifact. Its `video-motion-template-library/v1` schema belongs to this collection; it is not an assertion that the templates have been installed in a production video-generation picker.

Each template has a stable ID, a display code (VM-01 through VM-36), a version, a use case, a runtime source, supported controls, exact default timing, provenance and source SHA-256 values. Names can overlap across motion families; integrations must use the stable ID.

Defaults: 1920 × 1080, 16:9, no audio, Okou, dark colourway, standard action speed, appearance, 0.25-second terminal hold. The geometry uses the official Okou logotype outlines (shipped as assets/okou-motion.otf), a 156 px icon, 26.35 px gap and a -20.06 px optical offset.

| Control | 12 brand compositions | 24 reveal templates |
| --- | --- | --- |
| Placement | Intro or outro | Intro or outro |
| Colourway | Dark or light | Dark or light |
| Terminal hold | 0, 0.25 or 0.5 seconds | 0, 0.25 or 0.5 seconds |
| Motion | Appearance | Appearance or reverse exit |
| Action speed | Reviewed speed | Fast, standard or slow |

Placement is composition metadata. Choosing outro places the same brand appearance at the end of a product video; it does not automatically reverse the motion. Reverse exit is a separate setting for the 24 reveal templates. For an appearance the hold contains the complete brand; for an exit it contains the empty background. Changing hold never stretches the formation.

The reviewed identity preset is Okou. Changing an arbitrary brand name or logo is not an exposed runtime control. A new identity needs a coordinated source adaptation: logo paths, measured wordmark geometry, glyph cuts, and regenerated particle/bitmap samples. This keeps the traced, sliced and particle states consistent with the final frame.

## Preview and capture entry

Serve the package as a static HTTP(S) directory. `index.html` opens the template gallery. The refined HTML compositions load pinned GSAP and Three.js scripts from their existing external CDNs, so those templates require network access. The 24 Canvas templates have no external runtime dependency.

Open a clean, UI-free player with supported query parameters:

```
templates/player.html?template=brand-mask-sweep-lockup&theme=dark&hold=0.25&placement=intro
templates/player.html?template=reveal-particles&theme=light&hold=0.25&speed=standard&direction=out&placement=outro
```

The player starts paused at time zero. Add `autoplay=1` for ordinary playback. Wait for `window.VideoMotionTemplate.ready` before capturing a frame. The public API uses seconds:

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
VideoMotionTemplate.seek(0.6);
const { duration, formationSeconds } = VideoMotionTemplate.state();
const clip = VideoMotionTemplate.recipe();
```

`play()` plays once, `pause()` stops playback, and `seek(seconds)` pauses at a deterministic frame. Capture at a 1920 × 1080 viewport to match the reviewed stage. To assemble a product video, render the selected intro, append the product body, then render the selected outro. Use the duration reported by the configured player instead of padding to an assumed common length. The recipe records all selected settings and the clean player URL.

The gallery's “保存模板配置” button exports this `video-motion-clip/v1` recipe as JSON; it is not an MP4 download. The source package contains the template runtimes, official Okou assets, previews, manifest, and licenses. No MP4 master is included in this release.

## Source and licenses

The 12 refined compositions derive from `vm0-ai/Template-artifact` at `c451624f122b3e100ab5254baa4594cf8c46b86f`, re-cut to the official Okou identity and the reviewed timing. `NOTICE.md` and `HyperFrames-LICENSE.txt` are preserved under `refined/`. The 24 Canvas studies and library adapter are original work from this chat. Method references remain in the parent library's research section. Approved source files are unchanged by this packaging step; verification hashes are recorded in the release evidence.

This release packages browser motion sources and a reusable playback interface. It does not publish templates into Okou's production template registry or render a full product video.

## Release verification

`release-verification.json` records 72 source-runtime cases across the two colourways, exact configured durations, repeat seeks and final frames, 15 control cases, a downloaded clip recipe, restored sharing settings and desktop/mobile layout checks. Existing motion and archive files retain all 420 recorded hashes. Browser SVG antialiasing is compared with the stated small raster tolerance. Public browser requests from the agent environment reached a Cloudflare verification challenge; hosting publication is checked separately.
