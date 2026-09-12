# Prompt compiler: from brief to one native prompt

The prompt is HeyGen Video Agent's whole content interface. `style_id`, `avatar_id`, `voice_id`, and `orientation` travel as parameters; everything below is prompt text. Assemble it once from the cached brief, in this order. There is no house length limit: the prompt runs as long as the narration, the on-screen list, and the fixed literals require, and the only ceiling is the provider's 10,000 characters. What degrades the result is structure, not size — see below. This file is the only home of the fixed English literals.

## Skeleton

```text
<brief paragraph>
<presenter adaptation directive, for any look without a baked-in environment>

Narration:
“<script, or one narration paragraph written from the key messages, in the narration language>”

CRITICAL ON-SCREEN TEXT (display literally):
- "<at most 6 words or one figure plus a label>"

<one usage sentence per attached file the viewer must see>
<production lines that change the result, ending with the text legibility line>

<script-mode directive>
<pronunciation hints>
<translation-ready framing, only when requested>

<FRAMING NOTE, only when triggered>
<BACKGROUND NOTE, only when triggered>
```

## Why the skeleton looks like this

- A cropped head is a fit problem: a near-square studio look fitted to the frame width (`cover`) loses the top of the head, the same look fitted inside the frame (`contain`) keeps it, and a landscape look with a baked-in environment keeps it under either fit; the environment comes from the look image. Video Agent exposes no fit field, so a good presenter scene comes from a landscape look the agent derives during planning, and a bad one from the raw studio look on a plain background filled to the width. The presenter sentences make the agent plan that derivation; the adaptation directive asks for it by name and tells the agent to keep the presenter inside the frame.
- The script-mode directive keeps the agent composing instead of assembling; prompts without it, and long scene-by-scene prompts with `Media:` blocks, revert to the cutout, the cropped head, and invented on-screen details.
- The FRAMING NOTE and BACKGROUND NOTE describe the correction the agent should make; on their own they are ignored, together with the sentences and the directive they are followed.
- One narration paragraph, one length, one topic: every extra structure is a chance for the agent to fall back to templates.

## Slots

1. **Brief paragraph** (English). One format sentence: kind of video, one approximate length, orientation, narration language, audience; in verbatim mode say `The narration length follows the script below.` instead of a length. Then the three presenter sentences below, in that order — every native prompt is a presenter run, because `presenter: none` routes to controlled composition. Optionally one placement sentence (`The selected presenter opens and closes on camera.`). Refer to the presenter only as "the selected presenter". For any look without a baked-in environment (`studio_avatar`, `digital_twin`, or a transparent, solid, or empty preview) add the presenter adaptation directive as its own paragraph right after the brief paragraph, with the output orientation filled in.
2. **Narration** (narration language). Adapt mode: `Narration:` followed by the script or one flowing paragraph composed from the key messages in arc order, in quotation marks, with no scene labels and no timestamps at any length. The skeleton is the default form; HeyGen's scene-by-scene level is a deliberate departure from it, with the cost recorded in [recipes](recipes.md). Verbatim mode: `Script (narrate exactly as written):` followed by the script unchanged.
3. **CRITICAL ON-SCREEN TEXT** block: one quoted string per line from `on_screen_text`. Without it the agent rephrases numbers and quotes; long strings get split across cards.
4. **Attachment sentences** (English), one per `show` attachment: `Use the attached <what> as B-roll when <topic>.` `Display the attached logo in the intro and the end card.` An attached file without a usage sentence is ignored.
5. **Production lines** (English, only what changes the result): media types by content (`Use motion graphics for the statistics; use the attached screenshot rather than stock footage for the product.`), brand colors as hex, logo placement, then always the text legibility line. No style paragraph when a `style_id` is passed; the style is named once in the brief paragraph.
6. **Directives** (English literals, verbatim): the script-mode directive (adapt, source-only, or verbatim), one pronunciation hint per brand term a transcript would misspell, and the translation-ready framing when the user plans to translate or asked for a direct-to-camera message.
7. **Presenter notes** (English literals, verbatim, always last, FRAMING before BACKGROUND), chosen from the look classification in [catalogs](catalogs.md): `photo_avatar` with a real environment gets no BACKGROUND NOTE and a FRAMING NOTE only when its orientation does not match the output; `studio_avatar`, `digital_twin`, or any transparent, solid, or empty preview gets the FRAMING NOTE when `cropRisk` is high, then the BACKGROUND NOTE.

## Fixed literals

**Presenter sentences** (brief paragraph, every presenter run; fill the placeholders, keep the wording):

```text
The selected presenter delivers the narration in a <tone> tone. Use the selected <style name> style. Keep the entire head and hair visible in every presenter shot.
```

**Presenter adaptation directive** (own paragraph after the brief paragraph; every look that is not already a landscape or portrait image with a real environment; fill in `16:9 landscape` or `9:16 portrait`; never name an engine):

```text
Before building any scene, adapt the selected presenter into a natural <16:9 landscape> studio framing: create an AI-extended <16:9> version of the selected presenter with the entire head, hair, and shoulders inside the image and a complementary professional environment behind them, wait until that extended presenter is ready, and use it in every presenter scene. Fit the presenter entirely inside the frame; never fill the frame width with the original cutout or place it on a plain background.
```

**Text legibility line** (last production line, every prompt with on-screen text):

```text
Place every on-screen text on a solid or semi-opaque high-contrast panel, dark text on a light panel or white text on a dark panel, large enough to read at the delivery size.
```

**Script-freedom directive** (adapt mode with `facts: open`, exactly once):

```text
This script is a concept and theme to convey — not a verbatim transcript. You have full creative freedom to expand, elaborate, add examples, and fill the duration naturally. Do not pad with silence or pauses.
```

**Source-only expansion directive** (adapt mode with `facts: source-only`, exactly once, instead of the freedom directive):

```text
This script is a concept and theme to convey — not a verbatim transcript. Expand it only by restating or connecting the facts above, and fill the duration naturally. Every number, name, label, example, and interface detail on screen must come from the key messages or the CRITICAL ON-SCREEN TEXT list. Do not pad with silence or pauses.
```

**Verbatim directive** (verbatim mode, exactly once, never with either directive above):

```text
SCRIPT MODE: verbatim. Narrate the script above exactly as written, sentence by sentence and in order, without adding, removing, or rephrasing sentences. Let the video's length follow the script and keep the pacing natural.
```

**Pronunciation hint** (one line per brand term):

```text
Pronounce "Okou" as "oh-koh".
```

**Translation-ready framing** (only when the video will be translated or the user wants a direct-to-camera message):

```text
This is a direct-to-camera message. Think of it like a FaceTime call — one person, one camera, sincere eye contact throughout. The presenter should be visible and speaking for the entire video.
```

**FRAMING NOTE, look narrower than the landscape output** (source wording `square (1:1)` for any `cropRisk: high` look, `portrait` only for a genuinely portrait look):

```text
FRAMING NOTE: The selected avatar image is in square (1:1) orientation but this video is landscape (16:9). Frame the presenter from the chest up, centered in the landscape canvas. Use AI Image tool to generative fill to extend the scene horizontally with a complementary background environment that matches the video's tone (studio, office, or contextually appropriate setting). Do NOT add black bars or pillarboxing. The avatar should feel natural in the 16:9 frame.
```

**FRAMING NOTE, look wider than the portrait output** (source wording `square (1:1)` for any `cropRisk: high` look, `landscape` only for a genuinely landscape look):

```text
FRAMING NOTE: The selected avatar image is in square (1:1) orientation but this video is portrait (9:16). Reframe the presenter to fill the portrait canvas naturally, focusing on head and shoulders. Use AI Image tool to generative fill to extend vertically if needed. Do NOT add letterboxing. The avatar should fill the portrait frame comfortably.
```

**BACKGROUND NOTE** (preview transparent, solid, or visually empty):

```text
BACKGROUND NOTE: The selected avatar has no background or a transparent backdrop. Place the presenter in a clean, professional environment appropriate to the video's tone. For business/tech content: modern studio with soft lighting and subtle depth. For casual content: bright, minimal space with natural light. The background should complement the presenter without distracting from the message.
```

The notes guide the agent; `POST /v3/video-agents` has no background, crop, scale, position, or safe-area field, so report these notes as guidance when you describe what was controlled. A note is written only when the look's orientation and the output's differ.

## Rules

- Build the whole skeleton. The presenter sentences, the script-mode directive and the notes work as one set, and the notes alone are ignored.
- Keep it plain, not short. No per-scene `Media:` blocks, no production paragraphs, no style manifesto — those are what send the agent back to templates. Length itself is not the defect: a 60-second English narration needs about 700 characters and a 120-second one about 1,400, and the prompt simply gets that much longer. Never trim the narration to hit a character count; the narration is sized by the target duration.
- One approximate length only. Caps written into the prompt, such as `no longer than 30 seconds`, are ignored. For a soft preference set the target below the ceiling (about 18 seconds for a 30-second one) and size the narration to that target; a ceiling the deliverable genuinely must not exceed is a controlled-route requirement, not a wording problem.
- Measure the narration against the stated length before submitting: count the characters or words in the `Narration:` block and convert them at the pace in [brief](brief.md). If they exceed the stated length, trim the narration or restate the length — never submit a prompt that asks for more words than its own length holds, because HeyGen honours the length and cuts the closing sentence.
- End the narration on the ask or recap as a complete sentence. An end card or CTA line repeats that thought on screen; the narration is what completes it.
- Positive framing: describe what to show, not what to avoid. Restrictive lists make the agent play safe.
- No per-scene timestamps and no layout coordinates. Describe motion with verbs (counts up, slides in, draws itself) only when a description is needed at all.
- With `avatar_id`, say "the selected presenter"; the look supplies hair, clothing, and everything else about the person.
- One topic per video; split multi-topic requests.
- Narration and on-screen strings in the brief's language; every directive, note, and production line in English.
- Name the selected style once, in the brief paragraph.
- Each CRITICAL string at most 6 words or one figure plus a label; source citations and full sentences belong to the narration.
- Over 10,000 characters: compress the narration and attachment sentences, keeping the directives, the on-screen list, and any verbatim script whole. A verbatim script that alone exceeds the limit is a controlled-route job.

## Style paragraph (user-requested override only)

When the user asks for a look beyond the selected style, add one paragraph after the production lines: a name for the look, the exact palette as hex codes, the art direction, how things move, the transitions, and one closing line for the mood; five or six sentences. Defaults for any authored override: colors from the subject or brand rather than a fixed accent; no small caption text; every text-over-background pair at contrast ratio 4.5 or higher; composition and color varied across scenes.

## Worked example

Brief: `product-launch`, about 25 seconds, landscape, en-US narration, adapt mode with `facts: source-only`, selected Minimalism style, a `studio_avatar` look with a square transparent preview, one dashboard screenshot and one logo attached.

```text
Create one polished 25-second landscape (16:9) product launch video in English for operations managers at small and mid-sized companies. The selected presenter delivers the narration in a confident, conversational tone. Use the selected Minimalism style. Keep the entire head and hair visible in every presenter shot.

Before building any scene, adapt the selected presenter into a natural 16:9 landscape studio framing: create an AI-extended 16:9 version of the selected presenter with the entire head, hair, and shoulders inside the image and a complementary professional environment behind them, wait until that extended presenter is ready, and use it in every presenter scene. Fit the presenter entirely inside the frame; never fill the frame width with the original cutout or place it on a plain background.

Narration:
"Every Monday morning, an operations lead spends two hours stitching a weekly report out of five systems. Okou Smart Reports turns those two hours into two minutes: connect your sheets and boards, and a send-ready report writes itself. In the first month, pilot teams saved an average of 1.8 hours a week. A 14-day free trial is open now."

CRITICAL ON-SCREEN TEXT (display literally):
- "Two hours to two minutes"
- "1.8 hours saved weekly"
- "14-day free trial"
- "okou.ai"

Use the attached dashboard screenshot as B-roll when describing the automatic report. Display the attached logo in the intro and the end card.
Use motion graphics for the time-saving statistics and the end card. Place every on-screen text on a solid or semi-opaque high-contrast panel, dark text on a light panel or white text on a dark panel, large enough to read at the delivery size.

This script is a concept and theme to convey — not a verbatim transcript. Expand it only by restating or connecting the facts above, and fill the duration naturally. Every number, name, label, example, and interface detail on screen must come from the key messages or the CRITICAL ON-SCREEN TEXT list. Do not pad with silence or pauses.
Pronounce "Okou" as "oh-koh".

FRAMING NOTE: The selected avatar image is in square (1:1) orientation but this video is landscape (16:9). Frame the presenter from the chest up, centered in the landscape canvas. Use AI Image tool to generative fill to extend the scene horizontally with a complementary background environment that matches the video's tone (studio, office, or contextually appropriate setting). Do NOT add black bars or pillarboxing. The avatar should feel natural in the 16:9 frame.

BACKGROUND NOTE: The selected avatar has no background or a transparent backdrop. Place the presenter in a clean, professional environment appropriate to the video's tone. For business/tech content: modern studio with soft lighting and subtle depth. For casual content: bright, minimal space with natural light. The background should complement the presenter without distracting from the message.
```
