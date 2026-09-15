# Provider capability is not platform capability

Capability reference; execute through the managed commands documented by this skill. Sources: the [official HeyGen OpenAPI](https://developers.heygen.com/openapi/external-api.json) and the [Video Agent guide](https://developers.heygen.com/docs/video-agent). The default route requires the Okou release containing the managed Video Agent command; the controlled route uses managed speech and transparent-avatar takes. Personal accounts and connector flows remain outside this Intro Video skill.

## Video Agent and public styles

`POST /v3/video-agents` can author and render a whole video from a brief. Its request fields are `prompt`, `mode`, `avatar_id`, `voice_id`, `style_id`, `brand_kit_id`, `brand_glossary_id`, `orientation`, `files`, `callback_url`, `callback_id`, and `incognito_mode`. Prompt length is 1–10,000 characters; attachments are limited to 20 native media/PDF references. Orientation is landscape or portrait.

Duration, language, narrative, captions, and exclusions are prompt directions, not explicit guaranteed render controls. There is no background, crop, scale, position, or safe-area field, and no general no-avatar/no-voice switch; omitted/null IDs mean automatic selection.

Video Agent always writes and voices narration. Attached MP3/WAV files are reference material; no field makes them the soundtrack, and nothing removes narration or audio from the render. `No voiceover`, `silent`, and `Original audio` are therefore Okou-orchestrated (controlled-route) outcomes. Stripping the audio track from a finished native video is not equivalent: the pacing and captions were composed around narration, and the narrated seconds are still billed.

`No avatar` is not in that group. There is no field for it either, but the prompt is a working mechanism: a submission that omits `avatar_id` and opens with the no-presenter directive renders without a digital human, confirmed on the frames of a verified run. The distinction is what the API can be asked versus what it can be made to do — narration cannot be asked away, a presenter can. Because it is a request rather than a contract, the native route pairs it with the mandatory no-presenter frame check in [QA](qa.md), and a user who needs the exclusion guaranteed before rendering still buys the controlled route. A pasted script is treated as a concept unless the prompt says otherwise; verbatim narration can be requested but not guaranteed, so exact wording plus exact timing is also a controlled-route job.

A completed video also carries `captioned_video_url`, `subtitle_url` (SRT), `thumbnail_url`, and `gif_url` upstream; the managed route currently persists only the MP4.

Presenter framing on the direct video endpoint (`POST /v3/videos`) is decided by `fit`: `cover` fills the frame width and crops a near-square look at the head, `contain` keeps the whole look, and a landscape look with a baked-in environment keeps the head under either. The environment comes only from the look image; the engine (`avatar_iii` or `avatar_iv`) changes neither framing nor background, and the scenes endpoint omits `engine` for accepted `avatar_iii` requests. Video Agent has no fit field. Engines are priced differently upstream, but no decision here needs a rate: what matters is that the managed route bills only the Avatar III presenter path and the Video Agent path, so an Avatar IV request never buys anything on it.

Presenter composition depends on the look type and on the prompt. HeyGen's own Video Agent guidance treats a `photo_avatar` as a presenter whose environment is generated together with the avatar, while a `studio_avatar` (a preset cutout) and any transparent preview receive only prompt guidance. In observed managed-route runs, the complete skeleton produced a transparent studio presenter inside a generated environment with a full head; incomplete or long scene-by-scene prompts produced cutout or cropped presenters. These observations do not guarantee framing in a new render. Output resolution has no parameter on this endpoint and follows the HeyGen account plan: a paid Creator account rendered 1920×1080, a wallet account renders 1280×720 at 25 fps; the "default 1080p" statement in HeyGen's output specifications belongs to `/v3/videos`. The managed route is billed by output second, so a video that overshoots its target costs more than one that lands on it, and each submission is a fresh charge. What a job actually cost comes back on the job as `creditsCharged`; credit and plan failures go through `okou doctor credit`. Duration targets and caps remain prompt guidance; the actual output can undershoot or overshoot them.

The managed route uses the platform's server-side `HEYGEN_API_KEY`; a personal HeyGen connector token (`HEYGEN_TOKEN`) plays no part in it, so rotating or connecting a personal token does not change managed generation. `brand_kit_id` and `brand_glossary_id` exist upstream but are not passed by the managed route yet, so brand pronunciation is prompt-guided only. When a session fails upstream, the managed status currently exposes `HEYGEN_GENERATION_FAILED` without the provider's failure message; report the identifiers and do not infer a cause. Exact scripts, original pages/frames/audio, avatar placement, and overlay geometry are not guaranteed. `mode: chat` is not a reliable user-review barrier because the agent may proceed to generation.

A public style ID is applied natively on this endpoint. The default route passes the exact selected ID, including a concrete catalog ID chosen by Okou when style selection is delegated. The provider permits omission, but omission does not satisfy the product's Auto-style behavior. In controlled composition, previews can inform permitted added layers; state that adaptation and resolve an explicit native-render requirement if it conflicts with preservation constraints. Do not relabel a style as a Studio template.

Creation returns a session ID and an optional video ID. Track the session until a video is assigned, then retrieve its result. Handle waiting/input, failure, and interruption without duplicate creation. Native session lifecycle and whole-video pricing are distinct from the transparent presenter path. Use the managed artifact result rather than a temporary provider URL.

## Avatar and Studio video

`POST /v3/videos` supports distinct typed inputs. A direct avatar video takes exactly one script/audio source; scripts are capped at 5,000 characters and input speech at 600 seconds. Background-free WebM requires a compatible matting engine. The platform's managed command specifically supplies an audio source to Avatar III and returns a transparent presenter take, not a full authored narrative.

Studio scenes can sequence up to 50 full-frame avatar, image, or video scenes. This is not arbitrary overlapping composition; a picture-in-picture presenter on the same source slide needs a suitable template or an authored composition. Do not mix the old v2 `video_inputs` shape with v3 typed scenes.

## Studio templates

`GET /v3/templates` lists workspace API-ready templates, not the public styles in the form. Native rendering requires inspecting variables and calling `/v3/templates/{template_id}`. V3 text variables use `{"type":"text","content":"..."}` rather than v2 nested properties. Omitted text variables can leave literal placeholders. Layout, avatar removal, and exact voice replacement depend on the variables actually exposed.

This API is not a current managed Intro Video route. If the user supplies a rendered deck/video as a visual source, composition can preserve that material; it is not equivalent to native template-variable rendering.

## Translation and lipsync

`POST /v3/video-translations` translates existing spoken content and uses returned supported language names. It has no general top-level `voice_id`; source-speaker voice preservation and enterprise stock-voice options are not interchangeable with an arbitrary selected public voice.

`POST /v3/lipsyncs` takes existing video plus prepared replacement audio. It does not research, write, or translate the script. A faceless recording does not benefit from mouth-matching; managed translated speech plus local composition can replace its narration. Original-speaker voice preservation and visible-face lip matching cannot be promised by the current managed flow.

## HyperFrames Cloud

`POST /v3/hyperframes/renders` renders a packaged authored HTML project, with explicit fps/format/resolution/ratio controls. It does not create a narrative from a prompt. The preservation route requires the release containing the managed `okou video render` command and APIs. That route accepts an owned Okou ZIP, submits it with the platform’s server-side `HEYGEN_API_KEY`, and returns a persisted Okou artifact. The existing Intro Video switch gates new jobs; admitted jobs remain recoverable. The first release exposes 1080p/30 fps standard-quality MP4 in 16:9 or 9:16. It does not use `HEYGEN_TOKEN`, a personal connector or a direct `hyperframes cloud render` login. Local authoring flags and cloud output controls are not interchangeable. If the managed release is unavailable, report that dependency; do not silently substitute another account or export route.
