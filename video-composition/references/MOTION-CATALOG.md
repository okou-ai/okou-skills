# HyperFrames Motion Candidate Catalog

This document is the submission and operational source.

Use this catalog only after `MOTION.md` identifies an exception to the mapped Router item. It supplies bounded alternatives without turning any Registry item into a required template.

## How the AI chooses

1. Write one sentence describing the semantic move, not the visual effect: for example, “build four quarterly bars from a common zero baseline and land exact values.”
2. Query the current HyperFrames Registry in English with that sentence.
3. Keep at most two installable candidates total. Add one relevant candidate from the matching family below only when the word-ranked search misses a useful synonym.
4. Reject a candidate immediately if it fails semantic correctness, exact data, readable hold, stable-stage compatibility, or presenter safety.
5. Prefer a component when the layout should remain intact. Use a block when the semantic system genuinely needs most of the content region, such as a map or full chart.
6. Install and inspect the winner. Adapt tokens, typography, density, and geometry; preserve behavior, labels, axes, connectors, sources, and deterministic timing.
7. Leave a short source comment beside the timeline:

```html
<!-- Motion choice: chart-story; exact bars + labels fit the beat. Considered: data-chart. -->
```

This comment records judgment in the authored HTML. It is not a content manifest or layout schema.

## Selection filters

Apply these in order. A failure is a rejection, not a small score penalty.

1. **Meaning:** Does the motion express the actual relationship: reading order, quantity, change, causality, geography, status, or evidence?
2. **Truth:** Does it retain exact values, units, labels, sources, bounds, and uncertainty?
3. **Readability:** Does it settle early enough for narration and reading?
4. **Stage fit:** Can the background, presenter, and recurring rail remain still?
5. **Economy:** Is one primary behavior sufficient? Reject decorative motion that competes with the evidence.

## Candidate index

| Content family | Primary candidates | Search cue |
| --- | --- | --- |
| Headline and text hierarchy | `line-by-line-slide`, `soft-blur-in`, `inline-highlight`, `tracking-in`, `text-shimmer` | line, word, emphasis, replacement |
| Paragraph, checklist, or ordered list | `mk-specs-list`, `line-by-line-slide`, `grid-card-assemble` | readable rows, ordered facts, checklist |
| Deadline, date, or single value | `number-pop-in`, `count-up`, `number-wheel`, `mk-progress-stat` | static date, changing number, threshold |
| Bar, line, or time-series chart | `chart-story`, `animated-bar-chart`, `data-chart`, `mk-line-graph`, `bar-chart-race` | baseline, series, exact values, ranking |
| Progress, share, or completion | `mk-progress-stat`, `conic-progress-ring`, `mk-usage-arc`, `chart-story` | percent, fraction, completion, target |
| Process, milestones, or timeline | `tracing-beam`, `onboarding-stepper-flow`, `beat-timeline`, `flowchart` | causal order, connector, milestone |
| Quantitative or before/after comparison | `animated-bar-chart`, `chart-story`, `comparison-split`, `before-after-wipe` | common scale, delta, reveal boundary |
| Geography | `world-map`, `us-map`, `us-map-bubble`, `us-map-flow`, `us-map-hex` | region value, location, flow, equal weight |
| Relationship or network | `constellation-hub`, `avatar-cloud`, `flowchart` | hub, node, connector, dependency |
| Status or state change | `state-chip-rail`, `onboarding-stepper-flow`, `tabs-slide-indicator`, `icon-swap` | pending, active, complete, state snap |
| Source evidence or quote | `testimonial-proof-card`, `testimonial-card`, text primitives | quote, citation, evidence sentence |
| Affected groups or categorical counts | `animated-bar-chart`, `chart-story`, `mk-specs-list`, `grid-card-assemble` | categories, shared count scale, group emphasis |
| Uncertainty or scenario range | custom chart band using HyperFrames atomic rules | lower bound, upper bound, estimate, scenario |

## Headline and text hierarchy

Query example: `reveal a decision headline line by line, then underline one action phrase`.

- Choose `line-by-line-slide` for two to five readable lines with a clear order.
- Choose `soft-blur-in` for one restrained headline or caption, not a full paragraph.
- Choose `inline-highlight` when the sentence is already visible and one phrase must gain meaning.
- Choose `tracking-in` for a short organizational label or section identifier.
- Choose `text-shimmer` only for one finite emphasis pass; never use it as ambient decoration.
- Use `line-swap` or `strikethrough-replace` only when the message genuinely changes from one statement to another.

Avoid `headline-slam`, scramble, glitch, or elastic text by default; they imply urgency, instability, or spectacle that most scenes do not support.

## Paragraph, checklist, or ordered list

Query example: `reveal four implementation requirements as professional readable rows`.

- Choose `mk-specs-list` for compact professional rows with labels and values.
- Adapt `line-by-line-slide` for short prose or facts whose reading order matters.
- Choose `grid-card-assemble` only when the items are genuinely parallel capabilities or categories.
- Use a direct row stagger when none of the components fit, capped so the list arrives as one beat.

Do not use `marker-checklist-card` unless the entire piece intentionally adopts a handwritten evidence treatment; it conflicts with the default material language.

## Deadline, date, or single value

Query example: `land one deadline date immediately, then emphasize the action window`.

- Choose `number-pop-in` for a static value or date that must arrive decisively.
- Choose `count-up` only when the change from start to end carries meaning.
- Choose `number-wheel` when digit rolling is semantically appropriate, such as a live count; avoid it for a calendar date.
- Choose `mk-progress-stat` when the number needs a visible target or denominator.
- Pair a settled value with `inline-highlight` when the action phrase, rather than the number, is the true emphasis.

Never count through invented intermediate values for a date, vote, legal threshold, or other discrete fact.

## Bar, line, or time-series chart

Query example: `draw a two-series line chart left to right and land exact quarterly labels`.

- Choose `chart-story` for bars, line, donut, or progress with one emphasized datum.
- Choose `animated-bar-chart` for compact categorical comparison.
- Choose the `data-chart` block for a fuller editorial bar-plus-line story.
- Choose `mk-line-graph` for one or two minimal line series.
- Choose `bar-chart-race` only when rank changes over time are the message.
- Add the `chart-scrub-readout` atomic rule only when narration follows the series through time.

Axes, units, labels, and exact values are part of the content. Never replace them with decorative bars.

## Progress, share, or completion

Query example: `fill a verified completion percentage and keep the target visible`.

- Choose `mk-progress-stat` for value, target, and explanation in one composition.
- Choose `conic-progress-ring` for a compact part-to-whole reading.
- Choose `mk-usage-arc` for a restrained gauge.
- Choose the progress mode of `chart-story` when several values must build in reading order.

Animate the number and graphic from the same progress driver so they cannot disagree.

## Process, milestones, or timeline

Query example: `advance three implementation milestones with connectors in causal order`.

- Choose `tracing-beam` when one path activates a small number of steps.
- Choose `onboarding-stepper-flow` for a milestone rail with current and next states.
- Choose `beat-timeline` when rows must align to named timeline labels.
- Choose `flowchart` for a branching decision tree with anchored connectors.
- Compose `svg-path-draw` with node-state changes when the geometry is too specific for an installed component.

Do not reduce a process to unrelated cards fading in. Connectors and active state must explain causality.

## Quantitative or before-and-after comparison

Query example: `compare two outcomes on one baseline and reveal the delta`.

- Choose `animated-bar-chart` or `chart-story` for numerical comparison on a shared scale.
- Choose `comparison-split` or `before-after-wipe` for two states of the same object or scene.
- Use `grade-split-reveal` only when the comparison is specifically between two media grades.

The comparison basis must stay visible. Do not animate two unrelated entrances and ask the viewer to infer the difference.

## Geography

Query example: `reveal regional values on a choropleth with labels and a legend`.

- Choose `world-map`, `us-map`, or another verified region-specific map for choropleth values.
- Choose `us-map-bubble` for proportional city values.
- Choose `us-map-flow` for origin-destination relationships.
- Choose `us-map-hex` only when equal visual weight is more important than geographic area.

Use published geometry and sourced locations. Never approximate administrative boundaries with invented SVG shapes.

## Relationship or network

Query example: `draw anchored connectors from one composition hub to four responsible agencies`.

- Choose `constellation-hub` for one central entity and ordered outward relationships.
- Choose `avatar-cloud` for a community or stakeholder network with a proof center.
- Choose `flowchart` when edges express decisions or dependencies rather than association.
- Use the `avatar-cloud-network` atomic rule for a custom fixed hub-and-ring layout.

Every connector must terminate on the correct node at every sampled frame.

## Status or state change

Query example: `advance a permit status from pending to active to complete on exact cues`.

- Choose `state-chip-rail` for discrete public states with active, done, and pending semantics.
- Choose `onboarding-stepper-flow` when state is coupled to milestones and next action.
- Choose `tabs-slide-indicator` for a simple mutually exclusive state selector.
- Choose `icon-swap` only for one compact binary or categorical state.

Use state snaps or coupled indicator motion; do not imply continuous interpolation between discrete legal or operational states.

## Source evidence or quote

Query example: `reveal a sourced document excerpt at reading pace and underline the exact evidence sentence`.

- Choose `testimonial-proof-card` or `testimonial-card` only for an attributed human quotation.
- For an official document excerpt, combine a line or mask text reveal with `inline-highlight`, while keeping source, document title, date, and page context visible.
- Keep the document surface static; animate reading order and evidence emphasis, not a floating paper card.

The current Registry has no exact sourced-document evidence component; this gap has been reported. Preserve citation context in the authored scene.

## Affected groups or categorical counts

Query example: `build affected groups with exact counts on one shared scale and emphasize the largest group`.

- Choose `animated-bar-chart` or `chart-story` when counts are comparable.
- Choose `mk-specs-list` when groups carry heterogeneous labels and facts rather than one common metric.
- Choose `grid-card-assemble` only when the categories have equal weight and no numeric comparison is implied.

The current Registry has no exact affected-group categorical grid with shared counts; this gap has been reported. Use a real shared scale whenever magnitude matters.

## Uncertainty or scenario range

Query example: `draw an estimate with exact lower and upper confidence bounds, then hold all units and labels`.

The current Registry has no matching component; this gap has been reported. Hand-author the content with HyperFrames atomic rules:

- draw the central estimate path or mark with `svg-path-draw`;
- reveal a precomputed confidence or scenario band from the same x-domain;
- land lower bound, estimate, upper bound, unit, and confidence/scenario label together;
- use `chart-scrub-readout` only when time traversal is part of the narration.

Never animate uncertainty as decorative blur, jitter, or random motion. It is a numeric range and must remain measurable.

## Diversity across a sequence

Reuse behavior when consecutive scenes share the same evidence form; consistency is useful. Otherwise vary the visual verb with the content. A normal sequence should not use one universal entrance, but it also should not select a different effect merely for novelty.

Before release, review the sequence as a whole and confirm that each motion choice explains information that would be harder to understand in a static frame.
