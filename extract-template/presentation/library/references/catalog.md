# Local reference layout catalogue

Prefer the user's preserved source layouts. Select a complementary layout from this table only when the originals do not fit the content. Follow the layout link to inspect its HTML; read content slots and repeated groups directly from that file rather than maintaining separate JSON metadata. Paths are relative to this catalogue.

Capacity is a selection hint, not a fixed slide count or a guarantee of fit. Adapt selected layouts to the user's original PPT style as described in the [README](../README.md).

| Layout (HTML) | Category | Purpose | Capacity hint |
|---|---|---|---|
| [cover](../layouts/fragments/cover.html) | Framing | Opening title and audience context | One title, one subtitle and short attribution |
| [toc](../layouts/fragments/toc.html) | Framing | Agenda and reading order | 3–6 concise sections; preserve order |
| [section-divider](../layouts/fragments/section-divider.html) | Framing | Section transition | One section number and a short summary |
| [close](../layouts/fragments/close.html) | Framing | Conclusion and next action | One conclusion and one explicit next action |
| [statement](../layouts/fragments/statement.html) | Narrative | One central argument | One claim with concise support |
| [executive-summary](../layouts/fragments/executive-summary.html) | Narrative | Decision summary, evidence and action | One decision and 2–4 supporting findings |
| [two-column](../layouts/fragments/two-column.html) | Narrative | Two independent narratives | Two independent medium-length prose blocks |
| [three-column](../layouts/fragments/three-column.html) | Narrative | Three parallel narratives | Three concise peer readings |
| [longform](../layouts/fragments/longform.html) | Narrative | Structured prose with a supporting aside | Several short paragraphs and one aside |
| [bullets](../layouts/fragments/bullets.html) | Narrative | Unordered findings | 3–5 concise points; do not invent order |
| [numbered-list](../layouts/fragments/numbered-list.html) | Narrative | Ranked or explicitly ordered findings | 3–5 ordered points; retain supplied order |
| [todo-checklist](../layouts/fragments/todo-checklist.html) | Narrative | Action, owner and completion state | 3–5 actions with explicit states and owners |
| [comparison](../layouts/fragments/comparison.html) | Comparison | Compare evidence under the same criteria | Two comparable options; consistent criteria |
| [pros-cons](../layouts/fragments/pros-cons.html) | Comparison | Benefits and limitations of one choice | Two balanced groups, not different options |
| [versus](../layouts/fragments/versus.html) | Comparison | Two opposing headline measures | Two values with units and comparable bases |
| [stat-highlight](../layouts/fragments/stat-highlight.html) | Metrics | One primary metric and its meaning | One large value and a concise interpretation |
| [kpi-grid](../layouts/fragments/kpi-grid.html) | Metrics | A small set of peer indicators | 2–4 concise indicators per row; adapt for more |
| [dashboard](../layouts/fragments/dashboard.html) | Metrics | Indicators combined with diagnosis | A short KPI row and two concise diagnostic blocks |
| [scorecard](../layouts/fragments/scorecard.html) | Metrics | Criteria, scores and status | Several scored criteria; state units and thresholds |
| [period-comparison](../layouts/fragments/period-comparison.html) | Metrics | Two periods with a stated change basis | Two periods and one comparable change |
| [actual-vs-target](../layouts/fragments/actual-vs-target.html) | Metrics | Actual value against an explicit target | Actual, target and variance with matching units |
| [metric-deep-dive](../layouts/fragments/metric-deep-dive.html) | Metrics | Metric, trend and named drivers | One indicator and 2–3 explanatory drivers |
| [table](../layouts/fragments/table.html) | Records | Records under consistent headers | Start with 3–6 columns and short rows; measure real content |
| [detail-summary](../layouts/fragments/detail-summary.html) | Records | Detailed records with a short conclusion | A compact table and one supporting conclusion |
| [case-study](../layouts/fragments/case-study.html) | Narrative | Situation, intervention and outcome | One case; retain evidence and causal qualifications |
| [big-quote](../layouts/fragments/big-quote.html) | Narrative | One attributed quotation | One short quotation and its attribution |
| [quote-cards](../layouts/fragments/quote-cards.html) | Narrative | Several attributed perspectives | 2–3 short quotes; do not invent endorsements |
| [process-steps](../layouts/fragments/process-steps.html) | Time/process | An ordered method with meaningful connections | 3–4 ordered stages; state their relationship |
| [timeline](../layouts/fragments/timeline.html) | Time/process | Dated events in chronological order | 3–5 events; retain actual dates and order |
| [roadmap](../layouts/fragments/roadmap.html) | Time/process | Future horizons and deliverables | Three horizons; distinguish commitments from proposals |
| [gantt](../layouts/fragments/gantt.html) | Time/process | Task intervals on one time scale | A few tasks with explicit dates and a shared scale |
| [flow-diagram](../layouts/fragments/flow-diagram.html) | Diagrams | Directed branches and transitions | 3–6 nodes; draw only supported transitions |
| [arch-diagram](../layouts/fragments/arch-diagram.html) | Diagrams | Systems, boundaries and interfaces | A few components and explicit interfaces; no implied causality |
| [mindmap](../layouts/fragments/mindmap.html) | Diagrams | One topic and its subordinate branches | One root and a few labelled branches |
| [image-left](../layouts/fragments/image-left.html) | Images | Image evidence beside a narrative | One meaningful image with concise supporting prose |
| [image-right](../layouts/fragments/image-right.html) | Images | Narrative leading to image evidence | A narrative first, then one meaningful image |
| [image-hero](../layouts/fragments/image-hero.html) | Images | One dominant evidence image | One supplied image; no invented decorative media |
| [image-grid](../layouts/fragments/image-grid.html) | Images | A repeated visual series | 3–6 related supplied images with captions |
| [team](../layouts/fragments/team.html) | Commercial | Named people, roles and responsibilities | A few real people; no fabricated profiles |
| [pricing](../layouts/fragments/pricing.html) | Commercial | Comparable plans and their economics | 2–3 plans with prices, units and qualifications |
| [chart-bar](../layouts/fragments/chart-bar.html) | Charts | Magnitude on one quantitative baseline | A short set of categories with a shared scale |
| [chart-line](../layouts/fragments/chart-line.html) | Charts | Values over time | A few dated observations; preserve gaps and units |
| [chart-pie](../layouts/fragments/chart-pie.html) | Charts | A non-negative whole partition | A few parts with an explicit sum and denominator |
| [chart-radar](../layouts/fragments/chart-radar.html) | Charts | Several comparable dimensions | Comparable dimensions with stated normalization |
| [stacked-bar](../layouts/fragments/stacked-bar.html) | Charts | Contribution within comparable totals | A few categories and labelled series; preserve segment sums |
| [waterfall](../layouts/fragments/waterfall.html) | Charts | Signed contributions bridging two totals | Starting total, signed contributions and ending total |
| [funnel](../layouts/fragments/funnel.html) | Charts | Sequential volumes and stated denominators | 3–5 actual stages; distinguish volume from conversion |
| [heatmap](../layouts/fragments/heatmap.html) | Charts | A matrix of numeric intensity | A compact matrix and a source-compatible quantitative colour scale |
| [scatter-plot](../layouts/fragments/scatter-plot.html) | Charts | Two quantitative dimensions | A few observations with units and comparable axes |
| [bubble-chart](../layouts/fragments/bubble-chart.html) | Charts | Two coordinates and a third size dimension | Encode the stated non-negative third quantity by area, not radius |
| [forecast-scenarios](../layouts/fragments/forecast-scenarios.html) | Analysis | Explicit conditional future cases | A few scenarios; do not present forecasts as observations |
| [risk-recommendations](../layouts/fragments/risk-recommendations.html) | Analysis | A signal paired with an accountable response | 2–3 supported risks with owners and next steps |
| [methods-definitions](../layouts/fragments/methods-definitions.html) | Analysis | Definitions and calculation boundaries | A few definitions/formulas, units and exclusions |
| [appendix-index](../layouts/fragments/appendix-index.html) | Framing | References and supporting material | A few real references; retain original identifiers |
