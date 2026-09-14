# Recipes: what kind of intro video this is

A recipe fixes the narrative spine, defaults, and production guidance for one intent. The spines reuse the narrative arcs and beat roles of the Okou intro-video template packs ([`Template-artifact/Template-IntroVideo`](https://github.com/vm0-ai/Template-artifact/tree/main/Template-IntroVideo)), so a controlled-route composition and a native HeyGen prompt tell the same story.

Recipes are never shown to the user and the form has no intent selector; classify from the brief.

## Beat vocabulary

Use these roles to structure the script. They are writing tools, not prompt labels.

| Role | Meaning |
| --- | --- |
| hook | grab attention in the first sentence |
| claim | the one thing the video says |
| conflict | why now, what is wrong today |
| concept | define the term |
| mechanism | how it works |
| breakdown | the parts |
| example | one concrete case |
| evidence | data, chart, before/after |
| proof | someone else vouches (quote, logo, result) |
| turn | so what changes |
| boundary | when it does not apply |
| recap | the one sentence to remember |
| cta | the next action |
| credits | who is speaking |
| disclosure | required compliance text |

## Recipe table

| id | Use when | Spine (arc) | Duration band | Orientation | Presenter | Media | On-screen text | Style tags |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `product-launch` | new product, feature, release | hook → conflict → turn → concept → breakdown → evidence → proof → recap → cta (`lau_keynote`) | 45–60 s | landscape | opens and closes on camera | product screenshots as B-roll; motion graphics for numbers | product name, headline number, CTA | retro-tech, print, cinematic |
| `company-intro` | who we are, brand story, about us | hook → example → conflict → turn → proof → evidence → breakdown → recap → cta (`mkt_story`) | 60–90 s | landscape | on camera for claim and ask | stock for real environments; logo in intro and end card | company name, tagline, URL | print, cinematic, handmade |
| `personal-intro` | founder / creator self-introduction, outreach, "video of me" | hook → example → conflict → concept → turn → proof → breakdown → recap → cta (`cre_personal`) | 30–45 s | landscape | direct-to-camera throughout | minimal overlays only | name, role, one contact | cinematic, handmade |
| `sales-outreach` | pitch to one prospect or segment | hook → conflict → evidence → turn → breakdown → proof → example → boundary → cta (`sal_consult`) | 30–60 s | landscape | on camera | motion graphics for the cost/benefit numbers | the one number, the offer, next step | print, retro-tech |
| `promo` | campaign, event, webinar, offer | hook → conflict → turn → evidence → proof → breakdown → example → recap → cta (`mkt_funnel`) | 20–30 s | by destination | a look on native, voice-over only if the user asks | motion graphics; stock for atmosphere | date, place, registration URL | pop-culture, print |
| `onboarding` | new hire or new customer welcome | hook → concept → breakdown → example → mechanism → boundary → proof → recap → cta (`hr_onboard`) | 60–120 s | landscape | on camera plus overlays | motion graphics checklists | first steps, names of tools, dates | handmade, print |
| `course-intro` | lesson or series opener | hook → concept → breakdown → example → evidence → mechanism → boundary → recap → cta (`edu_linear`) | 45–60 s | landscape | on camera plus chapter cards | motion graphics diagrams | lesson title, outline items | print, handmade |
| `explainer` | how something works, tech or process | claim → concept → mechanism → breakdown → example → evidence → boundary → turn → recap (`tec_teardown`) | 60–90 s | landscape | suits voice-over, but a native job still carries a look | motion graphics diagrams; AI-generated for abstractions | term definitions, key numbers | retro-tech, print |
| `report-summary` | deck, report, or data → short briefing | claim → evidence → breakdown → mechanism → example → boundary → turn → recap → disclosure (`con_pyramid` / `fin_report`) | 60–120 s | landscape | suits voice-over, but a native job still carries a look | motion graphics for every figure; attached charts | every number shown, source line, disclosure | print, retro-tech |
| `care-update` | health, patient, or wellbeing information | hook → concept → mechanism → evidence → example → boundary → recap → turn → cta (`hea_care`) | 45–60 s | landscape | on camera, calm | minimal; no dramatization | dosages, contacts, disclosure | handmade, print |
| `social-short` | one idea for Reels / TikTok / Shorts | one continuous thought, hook first | 15–30 s | portrait | direct-to-camera | minimal overlays | at most two short lines | styles whose `aspect_ratio` is 9:16 |

Style tags are preferences for `Let Okou choose`; an explicit style always wins.

For an inferred adapt-mode target, estimate the drafted narration at the pace in [brief](brief.md) and use the recipe band as a planning bound. An explicit user duration takes precedence over that default band. Verbatim copy follows the brief's unchanged-script timing rule, even when its estimate falls outside the band. When no duration was requested, identify the length as an estimate rather than a user requirement.

## The narrative frame comes first

Before compiling any prompt, fill the brief's five answers: claim, conflict, turn, proof, ask. Proof must be a checkable fact from the request or a source (a number, a named customer, a file). Waive an answer only with a written reason ("no ask: internal announcement"). A video with an empty frame is a list, and lists produce forgettable output.

## Script rules

These guide narration authored or adapted by Okou on either route. Preserve user-locked verbatim scripts unchanged; plan the duration and visuals around them instead of applying these writing edits.

- The script is the biggest quality lever. Write for the ear: short sentences, active voice, contractions, one idea per video.
- Fit editable narration to the target estimate. When material exceeds the available time, drop the weakest key messages before submission; do not assume which words the provider would omit.
- Stories beat lists. First person and a concrete case ("we lost the evening enquiries") beat neutral summaries.
- Front-load the hook. The first sentence carries the claim or the conflict.
- Use the arc as an order, and never as timestamps. Per-scene timestamps make the delivery robotic; that is the one point HeyGen's prompting guide and its own effectiveness research agree on, so they are banned at every length on both routes.
- One flowing narration paragraph is the default at any length. HeyGen documents a scene-by-scene level (a scene type, a visual, and the VO for each) as maximum control for long or data-heavy videos, and it remains available — but this package does not reach for it by default, because our own runs show a long scene-by-scene prompt with per-scene media notes pulling Video Agent back to templates, the cutout, the cropped head, and invented on-screen detail. Order the sentences by the arc and let the production lines carry the visuals. On the controlled route the question does not arise: Okou lays out the timeline, so scene structure is simply the plan.
- Do not build the script around questions to the viewer; a single presenter asking questions reads as unnatural.
- Keep the presenter's words in the narration language and keep every technical directive in English.
- End with the ask in plain words. Put dates, prices, URLs, and names in `on_screen_text` so they render literally.
- Every claim traces to a source. Do not round or invent numbers; if the material does not contain a figure, the script does not either.
