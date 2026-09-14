# Content Motion Policy

This document is the submission and operational source.

## Load boundary

Read this file only when the deliverable is an actual video or animation. Static archetype HTML and PNG references contain no timeline or transition logic. HyperFrames owns deterministic timing, seeking, media playback, semantic motion primitives, and validation.

## Stable stage

The stage is present from the first frame and normally remains still:

- background fields and structural surfaces;
- the presenter wrapper and presenter media;
- recurring source, location, deadline, or public-service rails;
- decorative motifs that do not carry changing information.

Do not add entrance, drift, pulse, breathing, parallax, or idle motion to those elements merely to create activity. A presenter or stage transition is allowed only when the user or the narrative explicitly requires a spatial change. Content motion must never cross the presenter's face or hands.

## Route by content meaning

Identify the evidence form before choosing motion. Start with the motion family and official item already mapped in [ROUTER.md](ROUTER.md). Install that item directly and preserve its native semantic timeline when it fits. Do not reopen motion selection merely to seek variety.

Use [MOTION-CATALOG.md](MOTION-CATALOG.md) only on an exception: the mapped item is unavailable, fails the real capacity, or expresses the wrong relationship. Search the HyperFrames Registry in English with the exact move the beat needs, compare no more than two viable candidates, then install and inspect the stronger result.

```bash
npx hyperframes catalog --query "build a bar chart from baseline with labels and exact values" --json
npx hyperframes add chart-story
```

Prefer these families when they fit:

| Content form | HyperFrames starting points | Required expression |
| --- | --- | --- |
| Headline and supporting text | `line-by-line-slide`, `soft-blur-in`, `inline-highlight` | Build by line, word, or emphasis hierarchy; settle fully readable. |
| Bar, line, donut, or progress chart | `chart-story`, `animated-bar-chart`, `data-chart` | Establish axes or frame, grow/draw marks from their data origin, then land exact labels and values. |
| One important number | `count-up`, `number-wheel`, `mk-progress-stat` | Interpolate the value and its graphic together; hold the final value. |
| Process or ordered steps | `onboarding-stepper-flow`, `tracing-beam`, `beat-timeline` | Advance connectors, active state, and labels in causal order. |
| Quantitative or before/after comparison | `animated-bar-chart`, `chart-story`, `comparison-split` | Keep a common comparison basis; animate the delta or reveal boundary, not two unrelated entrances. |

If a Registry item fits, preserve its semantic behavior and adapt its tokens, typography, density, and geometry to this system. If neither exception candidate fits, report the Registry miss and compose the smallest sufficient set of HyperFrames atomic rules such as `stat-bars-and-fills`, `svg-path-draw`, `chart-scrub-readout`, or `waterfall-entry`. Do not build a style-local substitute for behavior HyperFrames already owns.

## Timeline ownership

- Build one deterministic paused timeline per composition.
- Keep stage and presenter selectors out of the ordinary content timeline.
- Start the primary content behavior at scene time zero unless narration explicitly requires a delayed cue.
- Use one primary content behavior and at most one supporting emphasis for a normal scene.
- Components merge into the content region; blocks remain sub-compositions wired by the host.
- Register the timeline only after its content behavior is complete.
- Duration follows narration, reading load, and the content primitive's settling time, not the static reference frame.

## No generic fallback

Do not run a universal fade-and-slide timeline across every scene. Text, chart, number, process, comparison, and map scenes have different visual verbs. A simple inline text reveal is acceptable for a text-only beat; it is not a fallback for a chart or diagram.

## Release checks

- Before browser work, run `node scripts/review-project.mjs --project . --phase preflight` once. It rejects contract, sidecar, local-font, path, and HyperFrames lint failures.
- Finish all settled scenes, then run `node scripts/review-project.mjs --project . --phase static`.
- After motion, run `node scripts/review-project.mjs --project . --phase preview`. The first call derives explicit scene midpoints and runs one complete HyperFrames check with contrast. Later calls automatically check only changed scenes when shared inputs are stable, reuse the result when nothing changed, and fall back to full coverage after shared changes.
- Hand over one persistent preview after that pass; do not repeat a sequence-wide check for every edit.
- After Preview checks pass and any user-requested preview approval is received, run `node scripts/review-project.mjs --project . --phase release` immediately before final render. It reuses an unchanged successful full Preview report; changed sources trigger another check.
- Do not run separate `npm run check` or standalone lint around this flow; Preflight already owns lint and Preview owns browser QA.
- Sample the opening to confirm the background and presenter are already settled.
- Sample every semantic build boundary: each text tier, chart axis and mark, value landing, connector activation, comparison handoff, and final hold.
- Verify exact data values, labels, units, axes, sources, and uncertainty.
- Check content, media, presenter silhouette, face, hands, and connectors at every sample.
- Keep all render-critical fonts and assets local or bundled.
- Treat a reported motion status of `unverified` as unresolved: composition sidecars exist but the host-level check did not load them.
- Generate an animation map only for unresolved motion diagnosis or final assurance, not as an ordinary authoring step.
