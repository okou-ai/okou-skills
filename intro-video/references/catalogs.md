# Managed catalogs and exact choices

Read this only when the brief contains a delegated choice or an exact ID that needs compatibility checking, and query only the catalog that choice belongs to.

Inspect current help and query only the needed Okou-managed catalog:

```bash
okou __intro-video-catalog styles --page-size 100 --json
okou __intro-video-catalog avatars --page-size 50 --json
okou __intro-video-catalog voices --page-size 100 --json
```

Follow `nextToken` with `--token` when more candidates are needed, and stop if a cursor repeats. A failed request is not an empty catalog: retry or report it, and keep the ID it was meant to resolve.

Preserve exact public IDs. A look is one appearance of an avatar — one outfit, one preview image, its own `avatar_id` and its own default voice; a group ID names the person and groups that person's looks, so it can never replace the selected look's `avatar_id`. Looks in one group differ in preview dimensions, so crop risk is a property of the look, not of the person. With a selected avatar and `Default` voice, resolve its `defaultVoiceId` and pass that actual voice ID when required. On the controlled route with no presenter, a delegated voice still means an independent public voice matching the brief's language; it does not mean mute. A delegated presenter (an older form's `Auto`) is resolved to one concrete public look by the preference order below; record the reason. Never submit a native job without `avatar_id`: `presenter: none` is a controlled-route requirement, and an omitted ID would let the agent pick a look.

For a native presenter, classify the selected look before submission:

- `avatar_type`: read it from the form's `HeyGen avatar type` line or the catalog record (`studio_avatar`, `photo_avatar`, `digital_twin`). HeyGen composes a `photo_avatar` together with its environment; a `studio_avatar` is a preset cutout that the agent places on the style's stage.
- `environment`: transparent by default, since every public look the catalog returns today is a transparent `studio_avatar`. Decode the preview image only to overturn that default, when a look looks like it carries a real scene: an alpha channel with transparent pixels, a solid color, or a visually empty field still means no environment, and only a real scene counts as `real`. `preferredOrientation` and `avatar_type` describe something else and never establish an environment.
- `cropRisk` for the output orientation: compute it from the catalog record's `imageWidth` and `imageHeight`; no download or decode is needed for this. For landscape output a look with `width < 1.20 × height` is `high`; for portrait output a look with `height < 1.20 × width` is `high`. Near-square means `max(width, height) < 1.10 × min(width, height)` and is always `high` unless the output is square.

Preference order when Okou chooses the look, and the alternative named when the user's explicit look is `cropRisk: high`: `photo_avatar` with a real environment and matching orientation; then any look with a real environment; then a `studio_avatar` with `cropRisk: low` (for landscape output `width ≥ 1.20 × height`). Pass the classification to the presenter capability check and the native preflight; the correction text lives only in the prompt compiler.

While the catalog offers no look with a real environment, the first two tiers are unreachable and the third is the normal native presenter path, not a fallback: a low-crop transparent look plus the adaptation directive and the BACKGROUND NOTE. Page the catalog to compare crop risk, not to hunt for an environment that is not there,, and record a transparent preview as transparent even when the order would prefer otherwise.

The managed catalog currently returns only `studio_avatar` looks with transparent previews. A near-square studio look keeps its head only when it is fitted inside the frame or replaced by a landscape look with a baked-in environment; Video Agent chooses the fit itself and, left alone, fills the width, so the presenter adaptation directive asks it to derive a landscape version and keep the presenter inside the frame. A derived look the agent saved in the workspace is a private `photo_avatar`; the managed route accepts only public looks today, so it cannot be reused as `avatar_id` until the platform allows workspace-private looks.

For delegated style, compare relevant tags and actual previews against the material, audience, purpose, tone, and output. Record the selected style ID and a short reason once a justified match is available. Native Video Agent receives that concrete `style_id`; controlled composition may use the preview only as an explicitly described visual adaptation.

Apply compatibility checks only to the chosen route. Standalone managed TTS uses a Starfish-compatible voice, while Video Agent has different restrictions. An avatar's default voice may therefore work natively while being unavailable to standalone TTS. The managed API can also reject a look's default voice as unavailable for Video Agent; when that happens, select a public voice in the narration language, record the substitution, and continue instead of failing the request.
