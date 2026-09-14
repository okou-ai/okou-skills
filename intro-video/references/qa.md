# QA: accept or reject against the brief

A completed render is already the user's file. Deliver its permanent URL first, name any known defect in one sentence, and keep routine QA to the technical check below. Keep evidence in the workspace and never repeat a generation job automatically.

## Default technical check

- Make one lightweight media probe for container, duration, dimensions, frame rate, and audio-track presence, plus a short decode sample. Reuse available metadata and the managed artifact URL where supported; a full-file decode is not a default requirement.
- Report the actual duration and any material mismatch. An approximate duration mismatch alone calls for disclosure, not automatic transcription, speed changes, padding, subtitle work, or re-export.
- For ordinary native videos, stop here. This check establishes basic file readability and parameters; it does not certify every frame, spoken word, or subtitle.

## Targeted review

Inspect further only for an explicit review request, a binding wording, timing, or preservation requirement, or a concrete observed problem. Select the relevant checks below instead of running the whole gate. Reuse existing evidence and stop once the required check or specific issue is resolved.

- Extract only frames needed for the requested visual check or observed issue, using `okou video frames --at ...` or a local decode. Routine delivery does not scan every scene transition, presenter shot, or text-dense scene.
- Use `okou video transcribe` for verbatim fidelity, an explicitly requested narration or subtitle review, or an observed audio problem. Reuse the transcript; neither narration being present, a non-default language, nor brand terms alone requires transcription. Ambiguous recognition is uncertainty to report, not proof of a missing word or a reason for repeated variant exports.
- Read the recorded request: `style_id`, `avatar_id`, `voice_id`, `orientation`, script mode, the look classification from the capability check, and the prompt actually submitted.
- When a presenter scene looks wrong and a read-only HeyGen credential is available, `GET /v3/videos/{video_id}/scenes` shows whether the presenter scenes used a derived landscape look with a baked-in environment or the raw studio look on a color background; record which one, with the look dimensions, in the workspace. A session lookup can return not found while the video and scenes endpoints work, so verify by video ID.

## Two tiers

**Tier A, brief violations.** Something the prompt or route controls went wrong. Reject the output, record what a corrected prompt or route would change, and tell the user in one sentence what is wrong and what you propose.

**Tier B, provider-control gaps.** The requirement was met as far as the prompt can carry it, and HeyGen's API has no field to enforce it. Deliver the file with one plain sentence that names the gap, says a retry with the same prompt will not change it, and offers the concrete alternatives (another look, the controlled route, or acceptance); keep the frames in the workspace as evidence. If the brief had marked the property as a hard requirement, the capability check should have routed away before submission; record it as an accepted risk that materialized.

## Native gate

Use only the rows relevant to the targeted review. A technical pass alone is not a claim that this entire gate passed.

| Check | Pass condition | Tier on failure |
| --- | --- | --- |
| Narration language | in the brief's language | A |
| Facts | numbers, names, labels, headings, counts, and interface details match the verified brief; an invented statistic or label is a failure even when the narration is right | A |
| On-screen text | every `on_screen_text` string appears literally; readable at delivery size on a contrasting panel | A |
| Brand names | the transcript spells brand terms correctly or the mispronunciation is recorded in the workspace | A when a hint was omitted, B when the hint was present |
| Presenter presence | on camera where the recipe says; a native job always has a presenter, since `presenter: none` routes to controlled composition and its absence is checked by the controlled gate | A |
| Orientation | requested landscape or portrait | A |
| Decode | audio and video decode cleanly; no long silences (transcript gaps over a few seconds) | A |
| Narration completeness | when this check is needed, the closing audio and transcript support a complete sentence carrying the brief's ask or recap; record ambiguous recognition as unverified. A short duration alone does not establish a truncated ending or trigger transcription | A when truncation is confirmed |
| Duration, approximate | 0.8× to 1.4× the target passes; 1.4× to 1.75× is B with the overrun stated; above 1.75× or below 0.8× is A | A or B as stated |
| Duration, verbatim | within about 20% of the pre-submission estimate | A |
| Resolution | at least 1280×720 landscape or 720×1280 portrait; record the actual value. 1080p is a gate only on the controlled route or when the provider exposes a resolution field | B when below the baseline |
| Presenter scene | a real integrated background when the brief or style expects one | A when the prompt lacked the presenter sentences, the expansion directive its `facts` setting calls for, or the BACKGROUND NOTE; B when the full prompt was present, the look is transparent, solid, or empty, and the brief left `scene: any`; A when the brief made it a hard `scene: integrated` and the complete prompt still produced no environment, with the controlled route named as the alternative; A for a `photo_avatar` with an environment |
| Presenter framing | complete head with clear headroom in every representative frame | A always: a cropped head is never delivered. Record whether the prompt was complete and which look the scenes used; a crop means a non-landscape look was fitted to the width, so the fix is the adaptation directive when it was missing, then a look with lower crop risk, then a landscape look with a real environment where the catalog offers one, and otherwise the controlled route |
| Style | style-bearing scenes visibly reflect the selected style; the recorded `style_id` matches the selection (a matching ID alone does not prove adherence) | A |

## Controlled gate

When the build was handed to `video-composition`, its four-phase review owns the composition mechanics — lint, layout, contrast, motion and the render itself — and is not repeated here. Reuse that evidence for the relevant checks above and everything the brief fixed: no presenter in any frame when the brief says `presenter: none` — the reason that requirement routes here, so it is checked on the frames rather than assumed from the composition; every required page or segment present, in order, unstretched and uncropped; no covered text; no duplicate audio from a presenter take; original audio retained when required; the transparent presenter take has real alpha and fits without cropping essential content; the composition renders at the resolved 1920×1080 or 1080×1920. On this route presenter scene, framing, and resolution are Tier A because Okou controls them.

## When it fails

Retain the generation, session, and video IDs and the artifact as evidence in the workspace, and record each failed check there with what would change on a retry. Tell the user in one or two plain sentences what is wrong and what you propose, without the check list or tier labels. A Tier A failure is delivered like any other output and described as what it is — never as polished — with what you propose in one sentence. Obtain the user's direction before a route change, and their authorization before a materially different or paid retry. A retry never reuses the identical prompt.
