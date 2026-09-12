# Fast Router

This file is the first stop for scene selection. Take the smallest row that truthfully holds the message, and install its mapped Registry item directly. Search the Registry only when that item is unavailable, fails the real capacity, or expresses the wrong relationship; on that exception compare no more than two candidates total.

Codes: `C` = content-complete component merged into the scene; `B` = content-complete block mounted as a scene-isolated sub-composition; `M` = supplied content adapter combining the named official behaviors. A motion primitive, token skeleton, or slot demo is never a finished layout. Presenter guidance follows the global preference: standard-size `full`, then grounded bottom-corner `head-shoulders`, then divider or omission, always at full size.

| Layout ID | Choose when | Capacity | Default official item | Motion family | Presenter |
| --- | --- | --- | --- | --- | --- |
| `orientation/headline-cover` | One authoritative announcement | 4–12-word headline + 1–2 lines | C `titlecard-lockup` | text hierarchy | optional |
| `orientation/briefing-map` | Preview 3–5 briefing issues | 3–5 short items | M `grid-card-assemble` + `line-by-line-slide` | list | secondary only |
| `orientation/section-pivot` | Reframe the question or responsibility | 1 sentence + short label | C `titlecard-calm` | status | optional |
| `orientation/public-action-close` | Land one public or organizational action | action + date/channel + disclosure | M `cta-close` + `line-by-line-slide` | status/stat | optional |
| `text/claim-support` | One claim needs direct supports | 1 claim + 1–3 supports | M `line-by-line-slide` + `inline-highlight` | text hierarchy | optional |
| `text/two-column-argument` | Two complementary parts explain one point | 2 fields, ≤35 words each | M `split-tilt-cards` | list | normally none |
| `text/three-fact-columns` | Three peer facts need equal weight | exactly 3 peers | C `grid-card-assemble` | category | none |
| `text/bullet-hierarchy` | Rank or group a complex explanation | 3–5 bullets, ≤2 lines each | M `line-by-line-slide` + `inline-highlight` | list | optional |
| `text/action-checklist` | Show concrete steps or requirements | 3–6 verb-led actions | M `grid-card-assemble` | list | optional |
| `text/source-quote` | Verified wording is the evidence | 12–45 words + speaker/source | C `testimonial-proof-card` | quote | attributed speaker only |
| `text/document-excerpt` | Closely read a record or clause | 35–80 words + 1–3 callouts | M `line-by-line-slide` + `inline-highlight` | quote | none |
| `data/single-stat` | One number, date, rate, or threshold must land | value + benchmark + disclosure | M `conic-progress-ring` + `number-pop-in` | stat | optional |
| `data/kpi-row` | Compare peer indicators at one moment | 2–4 values | C `grid-card-assemble` | category/stat | none |
| `data/kpi-grid` | Summarize a compact evidence set | 4–6 values | C `grid-card-assemble` | category | none |
| `data/data-table` | Exact cross-category values must remain tabular | ≤5 rows × 4 values | M `grid-card-assemble` + `inline-highlight` | quote/row emphasis | none |
| `data/ranked-bars` | Rank magnitudes on one basis | 3–7 bars | M `chart-story` | chart | normally none |
| `data/time-series` | Explain change, inflection, or divergence | 1–3 series, 4–12 points | B `mk-line-graph` | chart | none |
| `data/share-ring` | Show progress or part-to-whole | 1 primary + ≤2 support shares | M `conic-progress-ring` | progress | optional |
| `data/scenario-range` | Show forecast spread or uncertainty | 3 scenarios or 1 range | C `chart-story` | uncertainty | none |
| `comparison/balanced-split` | Compare two peers on the same basis | 2 sides × 1–3 attributes | M `split-tilt-cards` | comparison | normally none |
| `comparison/before-after` | Explain a verified state change | 2 states × ≤3 attributes | M `before-after-wipe` | comparison | optional |
| `comparison/benefit-risk` | Present an unresolved tradeoff | 2–4 benefits + 2–4 risks | M `split-tilt-cards` | comparison/list | none |
| `comparison/option-matrix` | Evaluate options against common criteria | 3–4 options × 2–4 criteria | M `grid-card-assemble` + `state-chip-rail` | status | none |
| `comparison/threshold-decision` | Show whether a rule or trigger is crossed | 1 measure + threshold + ≤2 conditions | M `state-chip-rail` + `number-pop-in` | stat/status | optional |
| `time/ordered-steps` | Procedure order is essential | 3–6 steps | M `tracing-beam` + `grid-card-assemble` | process | optional |
| `time/milestone-timeline` | Events share a chronological axis | 3–6 dated milestones | M `beat-timeline` | process | none |
| `time/phased-roadmap` | A plan advances through named phases | 3–4 phases × 1–3 outcomes | M `state-chip-rail` + `grid-card-assemble` | process | optional |
| `time/rollout-lanes` | Parallel workstreams develop over time | 2–4 lanes × 2–5 spans | M `beat-timeline` + `grid-card-assemble` | process | none |
| `time/handoff-flow` | Responsibility moves between owners | 3–6 owners | M `tracing-beam` | process | named owner only |
| `time/deadline-countdown` | Actions lead to one approaching date | date + interval + 2–4 actions | M `titlecard-lockup` + `grid-card-assemble` | stat/list | optional |
| `system/layered-system` | A system is best explained as layers | 3–5 layers | C `grid-card-assemble` | network | normally none |
| `system/decision-flow` | Show conditions, approvals, or exceptions | ≤8 nodes | M `tracing-beam` + `state-chip-rail` | network | none |
| `system/hub-spoke` | One hub affects several peer groups | 1 hub + 3–6 spokes | C `constellation-hub` | network/category | accountable hub only |
| `system/dependency-network` | Dependencies are non-linear | 4–8 nodes, 5–10 edges | M `constellation-hub` + `tracing-beam` | network | none |
| `media/regional-map` | Compare status or values across places | 3–7 regions, 2–5 states | B `us-map` | geography | none |
| `media/flow-map` | Show routes, movement, or spread | 2–6 nodes, 1–8 paths | B `us-map-flow` | geography | none |
| `media/media-left` | One media item leads and text interprets | media + claim + 1–2 callouts | M `particle-image-reveal` + `line-by-line-slide` | quote/media | media itself only |
| `media/media-right` | Context leads into one evidence item | media + claim + 1–3 supports | M `screen-flow-carousel` + `line-by-line-slide` | text/media | avoid competition |
| `media/evidence-hero` | One image, scan, or artifact is primary evidence | media + headline + caption + ≤2 callouts | M `particle-image-reveal` + `inline-highlight` | quote/media | media itself only |
| `media/evidence-grid` | Multiplicity of records or states is evidence | 3–6 media items | M `screen-flow-carousel` + `grid-card-assemble` | quote/comparison | none |

## Exception path

Open the matching section in `LAYOUT-CATALOG.md`, `HYPERFRAMES-LAYOUT-MAP.md`, or `MOTION-CATALOG.md` only when the compact row is insufficient. A Registry search is justified only by a missing item, a real capacity failure, or a semantic mismatch. The Router never generates geometry, content JSON, DOM, or a timeline.
