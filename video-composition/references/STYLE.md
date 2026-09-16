---
name: "Video Composition visual system"
id: "video-composition"
version: "2.4"
kind: "open-visual-style"
domain: "Briefing and informational video"
identity: "One dominant field, a high-contrast decision surface and a single restrained accent, so structure carries the meaning and ornament does not."
style_master_a: "assets/style-master-a.png"
style_master_b: "assets/style-master-b.png"
recognition_anchors:
  - "one dominant field"
  - "high-contrast decision surface"
  - "one restrained accent"
  - "isolated emphasis signal"
feel: "composed, direct, accountable"
palette_variants:
  navy-cobalt:
    background: "#16243B"
    foreground: "#FFFFFF"
    accent: "#2F5BD0"
    support: "#6F8CB9"
    muted: "#C6D0E0"
    panel: "#203657"
  monumental-minimal:
    background: "#FFFFFF"
    foreground: "#16243B"
    accent: "#2F5BD0"
    support: "#4F6485"
    muted: "#5A6678"
    panel: "#F6F8FB"
  black-gold:
    background: "#090806"
    foreground: "#E5C467"
    accent: "#CBA646"
    support: "#806B34"
    muted: "#C2AF78"
    panel: "#17140D"
  obsidian-champagne:
    background: "#0C0F13"
    foreground: "#F1EEE7"
    accent: "#71879A"
    support: "#535D65"
    muted: "#ADB2B5"
    panel: "#171B20"
  petrol-brass:
    background: "#09272A"
    foreground: "#EFEAE0"
    accent: "#6A9390"
    support: "#607B7A"
    muted: "#B8C4C0"
    panel: "#133438"
  parchment-oxblood:
    background: "#EDE7DC"
    foreground: "#1C1B1A"
    accent: "#702A3D"
    support: "#867C70"
    muted: "#5E5A55"
    panel: "#E1D8CA"
  porcelain-carbon:
    background: "#F0F1EE"
    foreground: "#1B2227"
    accent: "#405E68"
    support: "#7C8787"
    muted: "#566267"
    panel: "#E1E5E3"
typography:
  display: "Body 700"
  body: "Body 400"
  data: "Mono 700"
materials:
  - "matte background field"
  - "high-contrast information surface"
  - "restrained alert marker"
signature_motifs:
  - "public brief rail"
  - "deadline block"
  - "decision field"
  - "implementation marker"
presenter:
  media_selector: ".presenter-media"
  wrapper_selector: ".presenter-slot"
  video_mode_attribute: "data-video-presenter"
  video_modes: ["off", "on"]
  scene_presence_attribute: "data-presenter"
  layout_attribute: "data-presenter-layout"
  layouts: ["divider-left", "divider-right", "side-left", "side-right", "corner-left", "corner-right"]
  background_binding: "video-choice-with-scene-level-presence"
  transparent_video_ready: true
  face_safe_required: true
  default_crop: "full"
  crop_modes: ["full", "head-shoulders"]
  full_presenter_size: "fixed-by-template"
  head_shoulders_placement: "bottom-safe-corners-only"
  head_shoulders_boundary: "soft-transparent-circular-fade"
---

# Video Composition visual system

## Identity

One dominant field, a high-contrast decision surface and a single restrained accent, so structure carries the meaning and ornament does not.

It suits updates, briefings, explainers, summaries, and any subject whose value is the information itself. A palette is a tone choice within this one geometry; the subject's own logic shapes the composition, not the copy alone.

## Style Master fidelity

Treat `assets/style-master-a.png` and `assets/style-master-b.png` as the identity pair. A generated sequence should preserve at least three recognition anchors: one dominant background field, a high-contrast decision surface, a restrained composition accent, and an isolated deadline signal. Do not copy either frame mechanically, and do not claim fidelity from palette alone.

## Spatial grammar

Build each frame from one dominant field, one dominant message, and only the secondary structure the content requires. Use public brief rail, deadline block, decision field, implementation marker as semantic devices. The background should read as a coherent environment rather than a collage of cards, labels, rulers, and decorative lines.

The default frame has no template-added title chrome. Presenter use is resolved once for the video, then independently composed per scene. A presenter-free scene centers the complete settled content bounding box on both axes inside the full safe frame. Starters use a generous content scale by default, but the real message remains free to recompose without an occupancy target. A recipe name, category, source rail, or upper-left title appears only when the source message requires it. Full-canvas Registry blocks remain on full 1920×1080 hosts and never share a scene with a presenter.

The forty content-form recipes in `LAYOUT-CATALOG.md` classify the relationship the viewer must understand. `HYPERFRAMES-LAYOUT-MAP.md` records a tested official Registry component or block for each form, and the 1920×1080 PNG gallery proves those items inside the stage. The twelve composition archetypes provide deeper visual evidence for the surrounding style shell. None of these layers defines beats or required scene roles. Choose one semantic recipe first, inspect its official render proof, then borrow from at most two archetypes and install the strongest current Registry item for the real content.

## Color system

Seven named palettes live inside one Palette template. Layout hierarchy, component geometry, presenter grammar, and motion semantics stay identical. The user selects one name once, and bootstrap writes that project-level choice to the host and every scene:

- `navy-cobalt` (default here): navy field, white information, blue composition accent, amber signal.
- `monumental-minimal`: white field, navy/blue information, pale-blue surfaces.
- `black-gold`: black field with restrained gold information and signals.
- `obsidian-champagne`: near-black field, bone-white information, steel accent, champagne signal.
- `petrol-brass`: deep petrol field, warm information, mineral accent, brass signal.
- `parchment-oxblood`: warm parchment field, carbon information, oxblood accent, aged-brass signal.
- `porcelain-carbon`: porcelain field, carbon information, blue-grey accent, umber signal.
- `custom`: a user-supplied collection expressed once through the semantic contract.

Legacy names `blue-white` and `white-blue` remain accepted as aliases, but new projects store the canonical names above.

Layout and scene CSS may consume only `--palette-field`, `--palette-ink`, `--palette-surface`, `--palette-surface-strong`, `--palette-line`, `--palette-muted`, `--palette-accent`, `--palette-signal`, `--palette-on-accent`, `--palette-on-signal`, `--palette-contrast-field`, `--palette-contrast-ink`, and `--palette-shadow`. Concrete color values belong only in `assets/runtime/color-system.css` or `custom-color-system.css`.

For a supplied collection, define the complete token set under `[data-color-system="custom"]` and pass it to bootstrap with `--color-system custom --color-tokens <CSS_FILE>`. Resolve missing roles once at collection level; never improvise scene-local colors.

Use one collection for the whole project. The field and ink establish hierarchy; accent marks the primary state/action; signal is reserved for deadline, exception, or decision. Keep bright color concentrated. Do not switch palettes scene by scene unless the user explicitly requests a semantic section change.


## Typography

- Display: **Body 700**.
- Body: **Body 400**.
- Data and metadata: **Mono 700**, with tabular numerals.
- Prefer headlines at 84px or larger and body copy at 30px or larger on 1920×1080.
- Use large content scale and purposeful negative space before adding boxes. Negative space should clarify hierarchy, not make the message look undersized. Add or reorganize scenes before compressing actual content.

## Materials and motifs

The material world combines a matte background field, a high-contrast information surface, and one restrained alert marker. Signature motifs are the brief rail, deadline block, decision field, and rollout marker. A motif must establish hierarchy, identify state, frame evidence, or connect meaning. Remove it if it only fills space.

## Presenter grammar

Resolve the video-level choice before scene geometry: `off` means zero presenter nodes across the assembled sequence; `on` means a distributed recurrence plan while individual scenes may remain presenter-free. Choose appearances by narrative need rather than a scene-count quota.

Author each selected presenter scene directly in its intended representation. Omit the person whenever it would displace content from the center of its available region, cover required information, force unreadable type, or cause clipping; satisfy `on` recurrence elsewhere. Do not build a presenter-free comparison version. When present, the person is visible from scene opening and remains scene-long by default.

Choose representation in strict preference order. First try a complete `full` presenter at the template's standard size in presenter-led `divider-left|divider-right` or content-led `side-left|side-right`; switching sides is allowed, shrinking the full person is not. If it does not fit, use `head-shoulders` only in a naturally clear `corner-left|corner-right`, grounded on the bottom edge with the soft transparent circular fade. If neither treatment fits, move the person to a presenter-led divider or omit it from that scene.

- `full` is the default. The entire supplied presenter media or meaningful alpha bounds must remain visible inside the safe stage, including above any persistent rail. Keep the template's standard slot geometry; do not reduce it, zoom the media, clip an edge, use negative off-canvas placement, or hide part of the person behind a foreground panel.
- `head-shoulders` is the only cropped alternative. Retain face, neck, and shoulders; anchor the slot to the bottom-left or bottom-right safe corner; use the supplied soft transparent circular fade. Never float it at mid-height or substitute a hard circular edge.

The presenter wrapper is not automatically visible. Integrated and territory treatments have no local background, border, visible circle, or card. Use a framed or portal treatment only when it carries domain meaning.

~~~html
<div class="presenter-slot presenter-integrated presenter-crop-full" data-presenter-treatment="integrated" data-presenter-crop="full" data-face-safe="true">
  <div class="presenter-media" data-presenter-media="pending"></div>
</div>
~~~

~~~html
<div class="presenter-slot presenter-integrated presenter-crop-head-shoulders" data-presenter-treatment="integrated" data-presenter-crop="head-shoulders" data-face-safe="true">
  <div class="presenter-media" data-presenter-media="pending"></div>
</div>
~~~

Replacing only `.presenter-media` with transparent presenter video must preserve geometry. Inspect alpha or media bounds and confirm that no edge, rail, panel, or canvas boundary hides the presenter. Keep the face and any visible hands clear of type, charts, connectors, and motion.

## Domain-native media and information

Use supplied imagery, footage, charts, maps, scans, interfaces, documents, or objects according to the domain. Give essential media one readable territory. When a matching official Registry item exists, it must own the primary text system, chart, diagram, comparison, process, map, or media behavior. Apply this system's surface, hierarchy, and safety around it; do not rebuild it as ordinary DOM.

## AI composition freedoms

- Select, mirror, stretch, simplify, combine, or discard any archetype.
- Invent a new composition when the library fits poorly.
- Choose scene count, order, density, media use, scene-level presenter presence, side, and whether the person is standard-size `full`, grounded `head-shoulders`, moved to a divider, or omitted.
- Keep the approved frames as visual evidence, never content slots.
- Preserve one clear priority, a legible reading path, and purposeful negative space.

## Avoid

- Generic presentation-card grids when one broad field is enough.
- Template-added upper-left titles, recipe labels, category labels, or source rails with no source-required meaning.
- Presenter DOM anywhere in an `off` sequence, an effectively presenter-free `on` sequence, or compulsory presenter/content coexistence on every scene.
- Keeping a presenter on a particular scene when moving it to another scene makes the content clearer, more complete, or better centered.
- Choosing `head-shoulders` when the standard-size full presenter fits, floating it at mid-height, placing it outside a bottom safe corner, or shifting content to manufacture a corner bay.
- Smaller clipped hosts around full-canvas HyperFrames blocks.
- Repeating every motif, label, and accent in every scene.
- Decorative line systems that do not communicate a relationship.
- Downscaled full presenters, unrequested intermediate crops, hard crop edges, or an empty presenter bay.
- Page numbers, slide counters, folios, or pagination UI.

## Capacity and release checks

- Verify all forty official-component render proofs and all twelve archetype references at 1920×1080.
- Inspect every settled state directly in its intended presenter mode; the complete required-content box must be centered inside the actual available region and fully visible.
- Test both video modes. `off` must assemble with zero presenter nodes; `on` should show deliberate recurrence without requiring presenter coexistence on every scene or enforcing a numeric quota.
- For every scene that adds a presenter, inspect the intended settled state and peak motion; keep the presenter only if content completeness, readability, centering, and non-overlap remain acceptable.
- Test short and long headlines, a quotation, one and four values, evidence labels, both presenter assets in standard-size `full` and grounded `head-shoulders` modes, both bottom corners, presenter-led dividers, content sidecars, and presenter-free compositions.
- Keep body type at or above 30px and critical metadata at or above 20px whenever feasible.
- Inspect face, hands, typography, media, and data at rest and at peak motion.
- Confirm that the style remains recognizable without relying on color alone.
