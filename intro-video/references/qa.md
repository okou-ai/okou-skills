# QA: accept or reject against the brief

After rendering completes, run the default technical check and any applicable targeted checks below. Then deliver the permanent URL and measured duration, reporting only issues supported by the checks performed. Keep evidence in the workspace and never repeat a generation job automatically.

## Default technical check

- Make one lightweight media probe for container, duration, dimensions, frame rate, and audio-track presence, plus a short decode sample. Reuse available metadata and the managed artifact URL where supported; a full-file decode is not a default requirement.
- Report the actual duration and any material mismatch. An approximate duration mismatch alone calls for disclosure, not automatic transcription, speed changes, padding, subtitle work, or re-export.
- For ordinary native videos, deliver after this check and finish. This check establishes basic file readability and parameters; it does not certify every frame, spoken word, or subtitle. Unchecked content has no pass/fail result.
- **With `presenter: none`, add the no-presenter frame check before delivering.** Sample the whole video densely enough that no shot can hide between samples — 2 frames per second covers a video of ordinary intro length — and inspect the samples for a digital human. A contact sheet keeps this to one or two images: `ffmpeg -i <file> -vf "fps=2,scale=300:-1,tile=7x6" -frames:v 1 sheet.png`. Record the sheet and the sampling rate in the workspace. This is the only content check that runs without a targeted trigger, because it is the sole evidence that the prompt's exclusion held.

## Targeted review

Inspect further only for an explicit review request, a binding wording, timing, or preservation requirement, or a problem found by a performed check or reported by the user. Select the relevant checks below instead of running the whole gate. Reuse existing evidence and stop once the required check or specific issue is resolved.

- Extract only frames needed for the requested visual check or observed issue, using `okou video frames --at ...` or a local decode. Routine delivery does not scan every scene transition, presenter shot, or text-dense scene.
- Use `okou video transcribe` for verbatim fidelity, an explicitly requested narration or subtitle review, or an observed audio problem. Reuse the transcript; neither narration being present, a non-default language, nor brand terms alone requires transcription. Ambiguous recognition is uncertainty to report, not proof of a missing word or a reason for repeated variant exports.
- Read the recorded request: `style_id`, `avatar_id`, `voice_id`, `orientation`, script mode, the look classification from the capability check, and the prompt actually submitted.
- When a presenter scene looks wrong and a read-only HeyGen credential is available, `GET /v3/videos/{video_id}/scenes` shows whether the presenter scenes used a derived landscape look with a baked-in environment or the raw studio look on a color background; record which one, with the look dimensions, in the workspace. A session lookup can return not found while the video and scenes endpoints work, so verify by video ID.

## Two tiers

**Tier A, brief violations.** A performed check confirms that a requirement was missed. Mark that requirement as failed, retain the original artifact for delivery, and record what a corrected prompt or route would change. Tell the user in one sentence what the check found and what you propose.

**Tier B, provider-control gaps.** A performed check identifies a gap that the submitted prompt addressed but HeyGen's API cannot enforce. Deliver the file with one plain sentence naming the observed gap and relevant alternatives; the same prompt adds no new control and does not guarantee improvement. Keep the evidence in the workspace. Use the check's Tier A classification when a binding requirement was missed; do not infer user acceptance of a risk merely from the provider's limitations.

## Native gate

Use only the rows relevant to the targeted review. A technical pass alone is not a claim that this entire gate passed.

| Check | Pass condition | Tier on failure |
| --- | --- | --- |
| Narration language | in the brief's language | A |
| Facts | numbers, names, labels, headings, counts, and interface details match the verified brief; an invented statistic or label is a failure even when the narration is right | A |
| On-screen text | every `on_screen_text` string appears literally; readable at delivery size on a contrasting panel | A |
| Brand names | the transcript spells brand terms correctly or the mispronunciation is recorded in the workspace | A when a hint was omitted, B when the hint was present |
| Presenter presence | with a look in the brief, on camera where the recipe says. With `presenter: none`, **always checked**: sample the rendered frames across the whole video and confirm no digital human appears in any of them. This is the one native check that is never skipped, because the exclusion is a prompt direction rather than an API contract | A |
| Orientation | requested landscape or portrait | A |
| Decode | audio and video decode cleanly; no long silences (transcript gaps over a few seconds) | A |
| Narration completeness | when this check is needed, the closing audio and transcript support a complete sentence carrying the brief's ask or recap; record ambiguous recognition as unverified. A short duration alone does not establish a truncated ending or trigger transcription | A when truncation is confirmed |
| Duration, approximate | 0.8× to 1.4× the target passes; 1.4× to 1.75× is B with the overrun stated; above 1.75× or below 0.8× is A | A or B as stated |
| Duration, verbatim | report the measured duration and any material difference from the pre-submission estimate; exact timing belongs to the controlled route | An estimate mismatch alone is disclosed, not a wording failure |
| Resolution | at least 1280×720 landscape or 720×1280 portrait; record the actual value. 1080p is a gate only on the controlled route or when the provider exposes a resolution field | B when below the baseline |
| Presenter scene | a real integrated background when the brief or style expects one | A when the prompt lacked the presenter sentences, the correct script-mode directive, or a triggered BACKGROUND NOTE; B when the full prompt was present, the look is transparent, solid, or empty, and the brief left `scene: any`; A when the brief made it a hard `scene: integrated` and the complete prompt still produced no environment, with the controlled route named as the alternative; A for a `photo_avatar` with an environment |
| Presenter framing | when checked, the inspected frames match the user's composition preference, with full head and headroom as the default goal | A for a confirmed mismatch; retain and deliver the original artifact with the finding. Describe only what the frames establish; another look or route is a proposal governed by the user's choices and paid-retry rules |
| Style | style-bearing scenes visibly reflect the selected style; the recorded `style_id` matches the selection (a matching ID alone does not prove adherence) | A |

## Controlled gate

When the build was handed to `video-composition`, its four-phase review owns the composition mechanics — lint, layout, contrast, motion and the render itself — and is not repeated here. Reuse that evidence for the relevant checks above and everything the brief fixed: no presenter in any frame when the brief says `presenter: none` — checked on the frames rather than assumed from the composition, even though this route omits the layer by construction; every required page or segment present, in order, unstretched and uncropped; no covered text; no duplicate audio from a presenter take; original audio retained when required; the transparent presenter take has real alpha and fits without cropping essential content; the composition renders at the resolved 1920×1080 or 1080×1920. On this route presenter scene, framing, and resolution are Tier A because Okou controls them.

## When it fails

Retain the generation, session, and video IDs and the artifact as evidence in the workspace, and record each failed check there with what would change on a retry. Tell the user in one or two plain sentences what is wrong and what you propose, without the check list or tier labels. A Tier A failure is delivered like any other output and described as what it is — never as polished — with what you propose in one sentence. Obtain the user's direction before a route change, and their authorization before a materially different or paid retry. A retry never reuses the identical prompt.
