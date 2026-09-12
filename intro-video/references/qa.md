# QA: accept or reject against the brief

A rendered file is a candidate, not an accepted one — but it is still the user's file, already paid for. Hand it over as soon as it exists, name any defect you already know of in one sentence, and run these checks after that, not before. QA decides what to say about the video and whether to propose a retry; it never decides whether the user may see it. Compare the output with the brief, keep the evidence in the workspace, and never repeat a billed job automatically. QA results stay in the workspace; the final message to the user never lists them.

## Inspect

- Probe the file: container, duration, dimensions, frame rate, audio tracks, decodability.
- Extract frames from the opening, the closing, each scene transition, every presenter shot, and every text-dense scene. Use `okou video frames --at ...` on the managed artifact URL or a local decode.
- Transcribe when wording, language, silence, or brand names matter: `okou video transcribe` gives timestamped segments. Verbatim mode, non-default languages, and briefs with brand terms always transcribe. Every narrated output transcribes at least its closing segment, because narration completeness cannot be judged from the duration or the frames.
- Read the recorded request: `style_id`, `avatar_id`, `voice_id`, `orientation`, script mode, the look classification from the capability check, and the prompt actually submitted.
- When a presenter scene looks wrong and a read-only HeyGen credential is available, `GET /v3/videos/{video_id}/scenes` shows whether the presenter scenes used a derived landscape look with a baked-in environment or the raw studio look on a color background; record which one, with the look dimensions, in the workspace. The payload omits `engine` for accepted Avatar III requests, so a missing engine field says nothing; framing comes from the look and the prompt. A session lookup can return not found while the video and scenes endpoints work, so verify by video ID.

## Two tiers

**Tier A, brief violations.** Something the prompt or route controls went wrong. Reject the output, record what a corrected prompt or route would change, and tell the user in one sentence what is wrong and what you propose.

**Tier B, provider-control gaps.** The requirement was met as far as the prompt can carry it, and HeyGen's API has no field to enforce it. Deliver the file with one plain sentence that names the gap, says a retry with the same prompt will not change it, and offers the concrete alternatives (another look, the controlled route, or acceptance); keep the frames in the workspace as evidence. Never call it polished. If the brief had marked the property as a hard requirement, the capability check should have routed away before payment; record it as an accepted risk that materialized, not as a skill defect.

## Native gate

| Check | Pass condition | Tier on failure |
| --- | --- | --- |
| Narration language | in the brief's language | A |
| Facts | numbers, names, labels, headings, counts, and interface details match the verified brief; an invented statistic or label is a failure even when the narration is right | A |
| On-screen text | every `on_screen_text` string appears literally; readable at delivery size on a contrasting panel | A |
| Brand names | the transcript spells brand terms correctly or the mispronunciation is recorded in the workspace | A when a hint was omitted, B when the hint was present |
| Presenter presence | on camera where the recipe says; a native job always has a presenter, since `presenter: none` routes to controlled composition and its absence is checked by the controlled gate | A |
| Orientation | requested landscape or portrait | A |
| Decode | audio and video decode cleanly; no long silences (transcript gaps over a few seconds) | A |
| Narration completeness | the transcript's last sentence is grammatically complete and carries the brief's ask or recap. Duration alone never settles this, so transcribe before judging, and always when the video came in under about 0.9× the target: a short video usually means the agent compressed a narration longer than its target and dropped the ending, which a retry with the same narration repeats | A |
| Duration, approximate | 0.8× to 1.4× the target passes; 1.4× to 1.75× is B with the billing impact stated; above 1.75× or below 0.8× is A | A or B as stated |
| Duration, verbatim | within about 20% of the pre-submission estimate | A |
| Resolution | at least 1280×720 landscape or 720×1280 portrait; record the actual value. 1080p is a gate only on the controlled route or when the provider exposes a resolution field | B when below the baseline |
| Presenter scene | a real integrated background when the brief or style expects one | A when the prompt lacked the presenter sentences, the expansion directive its `facts` setting calls for, or the BACKGROUND NOTE; B when the full prompt was present, the look is transparent, solid, or empty, and the brief left `scene: any`; A when the brief made it a hard `scene: integrated` and the complete prompt still produced no environment, with the controlled route named as the alternative; A for a `photo_avatar` with an environment |
| Presenter framing | complete head with clear headroom in every representative frame | A always: a cropped head is never delivered. Record whether the prompt was complete and which look the scenes used; a crop means a non-landscape look was fitted to the width, so the fix is the adaptation directive when it was missing, then a look with lower crop risk, then a landscape look with a real environment where the catalog offers one, and otherwise the controlled route; never the same prompt or a different engine |
| Style | style-bearing scenes visibly reflect the selected style; the recorded `style_id` matches the selection (a matching ID alone does not prove adherence) | A |

## Controlled gate

When the build was handed to `video-composition`, its four-phase review owns the composition mechanics — lint, layout, contrast, motion and the render itself — and is not repeated here. What stays with this gate on either controlled path is everything the brief fixed: the checks above, plus: no presenter in any frame when the brief says `presenter: none` — the reason that requirement routes here, so it is checked on the frames rather than assumed from the composition; every required page or segment present, in order, unstretched and uncropped; no covered text; no duplicate audio from a presenter take; original audio retained when required; the transparent presenter take has real alpha and fits without cropping essential content; the composition renders at the resolved 1920×1080 or 1080×1920. On this route presenter scene, framing, and resolution are Tier A because Okou controls them.

## When it fails

Retain the generation, session, and video IDs and the artifact as evidence in the workspace, and record each failed check there with what would change on a retry. Tell the user in one or two plain sentences what is wrong and what you propose, without the check list or tier labels. A Tier A failure is delivered like any other output and described as what it is — never as polished — with what you propose in one sentence. Obtain the user's direction before a route change, and their authorization before a materially different or paid retry. A retry never reuses the identical prompt.
