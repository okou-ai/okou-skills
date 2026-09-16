# Content-Form Layout Catalog

This document is the submission and operational source.

Gallery copy is a capacity calibration, not filler: each proof uses roughly 70–85% of the recipe's recommended text load and explains the relationship the layout is built to express. Replacement content should cover the same semantic fields, not imitate the words. Choose a smaller recipe for genuinely sparse content; reselect or split content that exceeds the stated capacity.

This catalog supplies forty reusable content forms. A layout recipe fixes the relationship among information types, not the final coordinates, visual styling, wording, scene order, or animation. The twelve composition archetypes remain visual evidence; these forty recipes are a faster semantic routing layer.

Do not turn this catalog into a JSON manifest, slot renderer, or layout compiler. Select one recipe, borrow visual grammar from one or two relevant archetypes, and author the final HTML and CSS directly.

## Fast selection

1. State the scene's viewing task in one sentence: what must the viewer understand, compare, locate, or do?
2. Route by the dominant information relationship in the family table below.
3. Choose the smallest recipe whose capacity fits the real content. If two relationships compete for priority, split the scene.
4. Use the composition archetypes only for palette, spatial tension, presenter treatment, and visual identity.
5. Resolve a complete static frame, then route the content layer to the matching section of `MOTION-CATALOG.md`.

The background field, presenter, public rail, and recurring palette chrome remain visually settled. Recipes describe only the authored content layer. Presenter presence is optional unless a recipe explicitly makes the person the evidence; representation follows the global standard-size `full` or grounded bottom-corner `head-shoulders` rule.

## Family router

| Content signal | Family | Recipes | Default motion route |
|---|---|---:|---|
| Identity, framing, topic map, or public action | Orientation and closure | 4 | headline/text or status |
| Claims, prose, lists, quotations, or records | Text and evidence | 7 | text, list, or source evidence |
| Values, rankings, tables, trends, shares, or ranges | Metrics and charts | 8 | number, chart, progress, or uncertainty |
| Two alternatives, two states, tradeoffs, or a choice | Comparison and decision | 5 | comparison or status |
| Order, dates, phases, schedules, or handoffs | Time and process | 6 | process/timeline or deadline |
| Layers, branches, hubs, or dependencies | Systems and relationships | 4 | relationship/network |
| Place, movement, photography, footage, or multiple records | Geography and media | 6 | geography or source evidence |

## Recipe contract

Every recipe specifies five things:

- **Use** identifies the semantic reason to choose it.
- **Form** fixes the relationship among content regions without fixing coordinates.
- **Capacity** is a release limit, not a target to fill.
- **Presenter** describes compatibility, never an empty reserved bay.
- **Motion** points to the semantic family to query in HyperFrames after the static layout works.

## Orientation and closure

These recipes may appear anywhere in a sequence. Their names do not prescribe an opening or ending.

### orientation/headline-cover

- **Use:** Establish one authoritative subject, update, or announcement.
- **Form:** One dominant headline, one short descriptor, one organizational or human anchor, and optional source context.
- **Capacity:** Headline of 4–12 words; descriptor of 1–2 lines; one anchor only.
- **Presenter:** Optional when the person is an identity cue. Prefer standard-size `full`; use grounded bottom-corner `head-shoulders` only when the global presenter rules allow it.
- **Motion:** Headline and text hierarchy.

### orientation/briefing-map

- **Use:** Show the bounded set of issues a briefing will address without imitating a table of contents.
- **Form:** One framing statement above 3–5 named issue fields sharing equal status.
- **Capacity:** 3–5 items; each item is a short noun phrase plus at most one qualifier.
- **Presenter:** Optional and visually secondary.
- **Motion:** Paragraph, checklist, or ordered list.

### orientation/section-pivot

- **Use:** Reframe the question, mark a change in responsibility, or introduce a new evidence domain.
- **Form:** One transition claim paired with one incoming category, place, time, or organization.
- **Capacity:** One sentence and one short context label.
- **Presenter:** Optional; keep static and outside the transition claim.
- **Motion:** Status or state change.

### orientation/public-action-close

- **Use:** Land the one action the public, organization, or named group should take next.
- **Form:** One action statement, one deadline or contact route, and one responsibility label.
- **Capacity:** One action; one date or channel; one disclosure line.
- **Presenter:** Optional `full` presenter as reassurance, never as a substitute for the action text.
- **Motion:** Status or state change, with a deadline or single-value support when applicable.

## Text and evidence

### text/claim-support

- **Use:** Explain one claim with a small body of directly supporting evidence.
- **Form:** Dominant claim beside or above 1–3 evidence points with a shared source line.
- **Capacity:** One claim; 1–3 supports; no support longer than two lines.
- **Presenter:** Optional and separated from the evidence field.
- **Motion:** Headline and text hierarchy.

### text/two-column-argument

- **Use:** Present two complementary parts of one explanation, not competing alternatives.
- **Form:** Shared heading above two unequal or equal prose fields connected by one common premise.
- **Capacity:** Two fields; each contains one subhead and up to 35 words.
- **Presenter:** None by default; optional only if one column remains clearly dominant.
- **Motion:** Paragraph, checklist, or ordered list.

### text/three-fact-columns

- **Use:** Present three peer facts, responsibilities, or implications with equal weight.
- **Form:** Shared heading above three aligned fact fields using the same internal hierarchy.
- **Capacity:** Exactly three peers; one short label and 1–2 support lines each.
- **Presenter:** None by default.
- **Motion:** Affected groups or categorical counts, or a restrained text stagger.

### text/bullet-hierarchy

- **Use:** Reduce a complex explanation to a ranked or grouped set of points.
- **Form:** One framing claim followed by a vertical list with one visibly primary item and 2–4 secondary items.
- **Capacity:** 3–5 bullets; one line preferred, two lines maximum.
- **Presenter:** Optional on the opposite side of the list.
- **Motion:** Paragraph, checklist, or ordered list.

### text/action-checklist

- **Use:** Communicate concrete steps, requirements, documents, or safety actions.
- **Form:** One instruction above a checklist whose completed and pending states remain distinguishable.
- **Capacity:** 3–6 actions; one verb-led line per action.
- **Presenter:** Optional and static; do not animate the person as a checklist cursor.
- **Motion:** Paragraph, checklist, or ordered list.

### text/source-quote

- **Use:** Make a verified statement, testimony, or official wording the primary evidence.
- **Form:** One bounded quotation, one attribution block, and one source or date line.
- **Capacity:** 12–45 quoted words; one speaker; one source.
- **Presenter:** Optional only when the shown person is the attributed speaker. Prefer standard-size `full`; use grounded bottom-corner `head-shoulders` only when the global presenter rules allow it.
- **Motion:** Source evidence or quote.

### text/document-excerpt

- **Use:** Closely read a contract clause, record, release, notice, or transcript excerpt.
- **Form:** One excerpt field with 1–3 anchored callouts and a traceable document label.
- **Capacity:** 35–80 visible words; 1–3 callouts; one source record.
- **Presenter:** None by default.
- **Motion:** Source evidence or quote, with inline text emphasis only after the excerpt is legible.

## Metrics and charts

### data/single-stat

- **Use:** Land one decisive number, date, rate, or threshold.
- **Form:** One dominant value, one unit, one interpretation line, and optional benchmark.
- **Capacity:** One value; one benchmark; one disclosure line.
- **Presenter:** Optional and secondary.
- **Motion:** Deadline, date, or single value.

### data/kpi-row

- **Use:** Compare a small set of peer indicators at one moment.
- **Form:** Shared heading above 2–4 aligned KPI fields using identical units or clearly labeled unit changes.
- **Capacity:** 2–4 values; one short label and one qualifier each.
- **Presenter:** None by default.
- **Motion:** Affected groups or categorical counts, or restrained count-up where values are independently meaningful.

### data/kpi-grid

- **Use:** Summarize a dashboard-like evidence set without implying a software interface.
- **Form:** One interpretation claim above 4–6 KPI fields grouped into two meaningful rows.
- **Capacity:** 4–6 values; no ornamental empty cells.
- **Presenter:** None.
- **Motion:** Affected groups or categorical counts.

### data/data-table

- **Use:** Preserve exact cross-category values that cannot be responsibly reduced to a chart.
- **Form:** One compact table with a highlighted row, column, or threshold and a single interpretation claim.
- **Capacity:** Up to 5 rows by 4 value columns, excluding labels; split before type becomes small.
- **Presenter:** None.
- **Motion:** Source evidence or quote for the table reveal, with restrained row emphasis.

### data/ranked-bars

- **Use:** Compare magnitudes or rank categories on a common quantitative basis.
- **Form:** One horizontal or vertical bar field, one shared scale, direct labels, and one stated takeaway.
- **Capacity:** 3–7 bars; one measure; one comparison basis.
- **Presenter:** None by default.
- **Motion:** Bar, line, or time-series chart.

### data/time-series

- **Use:** Explain change over time, an inflection point, or divergence between series.
- **Form:** One shared time axis, 1–3 lines, one annotated event or threshold, and one takeaway.
- **Capacity:** 1–3 series; 4–12 labeled time points; one primary annotation.
- **Presenter:** None by default.
- **Motion:** Bar, line, or time-series chart.

### data/share-ring

- **Use:** Show progress, completion, allocation, or a part-to-whole relationship.
- **Form:** One dominant percentage or fraction paired with a ring, progress track, or bounded share field and one denominator statement.
- **Capacity:** One primary share; at most two supporting shares; denominator always visible.
- **Presenter:** Optional and secondary.
- **Motion:** Progress, share, or completion.

### data/scenario-range

- **Use:** Communicate uncertainty, forecast spread, confidence, or three bounded scenarios.
- **Form:** One central estimate with low/base/high bounds or one band across a shared scale, plus assumptions.
- **Capacity:** Three scenarios or one continuous range; 1–3 assumptions.
- **Presenter:** None by default.
- **Motion:** Uncertainty or scenario range.

## Comparison and decision

### comparison/balanced-split

- **Use:** Compare two peer groups, policies, jurisdictions, or outcomes on the same basis.
- **Form:** One shared comparison question above two fields with mirrored measures and labels.
- **Capacity:** Two sides; 1–3 matched attributes per side.
- **Presenter:** None by default; optional only outside both comparison fields.
- **Motion:** Quantitative or before-and-after comparison.

### comparison/before-after

- **Use:** Explain a verified change between two states.
- **Form:** A previous state and a current or proposed state linked by one explicit change vector.
- **Capacity:** Two states; up to three matched attributes; one date or condition per state.
- **Presenter:** Optional and static.
- **Motion:** Quantitative or before-and-after comparison.

### comparison/benefit-risk

- **Use:** Present tradeoffs without visually privileging an unsupported conclusion.
- **Form:** One decision frame above benefit and risk fields that share evidence standards and source treatment.
- **Capacity:** 2–4 benefits and 2–4 risks; one unresolved condition.
- **Presenter:** None by default.
- **Motion:** Quantitative or before-and-after comparison, or paragraph/list when evidence is qualitative.

### comparison/option-matrix

- **Use:** Evaluate three or four options against common criteria.
- **Form:** Options on one axis, 2–4 criteria on the other, one visible decision rule, and one selected or unresolved state.
- **Capacity:** 3–4 options by 2–4 criteria.
- **Presenter:** None.
- **Motion:** Status or state change after the matrix is readable.

### comparison/threshold-decision

- **Use:** Show whether a measure crosses a rule, target, trigger, or legal threshold.
- **Form:** One measured value, one threshold, one resulting status, and one consequence statement.
- **Capacity:** One measure and one threshold; at most two supporting conditions.
- **Presenter:** Optional and secondary.
- **Motion:** Deadline, date, or single value followed by status or state change.

## Time and process

### time/ordered-steps

- **Use:** Explain a short procedure whose order is essential.
- **Form:** One start condition followed by 3–6 numbered or connected actions and one result.
- **Capacity:** 3–6 steps; one verb-led line and optional short qualifier per step.
- **Presenter:** Optional outside the step path.
- **Motion:** Process, milestones, or timeline.

### time/milestone-timeline

- **Use:** Place events or commitments on a shared chronological axis.
- **Form:** One time axis, 3–6 dated milestones, and one active or current marker.
- **Capacity:** 3–6 milestones; one date and one short event label each.
- **Presenter:** None by default.
- **Motion:** Process, milestones, or timeline.

### time/phased-roadmap

- **Use:** Explain a plan that progresses through named phases rather than exact task dates.
- **Form:** Three or four phase territories with outcomes, gates, and one current phase.
- **Capacity:** 3–4 phases; 1–3 outcomes per phase.
- **Presenter:** Optional and static.
- **Motion:** Process, milestones, or timeline.

### time/rollout-lanes

- **Use:** Show parallel workstreams, jurisdictions, or service channels across time.
- **Form:** A shared time axis across 2–4 labeled lanes with bounded activity spans and key dependencies.
- **Capacity:** 2–4 lanes; 2–5 spans per lane; only critical dates labeled.
- **Presenter:** None.
- **Motion:** Process, milestones, or timeline.

### time/handoff-flow

- **Use:** Explain how responsibility moves between people, agencies, teams, or systems.
- **Form:** Three to six owners connected in sequence, with one named artifact or state passed at each handoff.
- **Capacity:** 3–6 owners; one handoff per connection.
- **Presenter:** Optional only when the presenter represents one named owner.
- **Motion:** Process, milestones, or timeline.

### time/deadline-countdown

- **Use:** Emphasize an approaching date and the actions that must happen before it.
- **Form:** One deadline block, one remaining interval or current state, and 2–4 prerequisite actions.
- **Capacity:** One date; one interval; 2–4 actions.
- **Presenter:** Optional and secondary.
- **Motion:** Deadline, date, or single value, supported by a short ordered-list reveal.

## Systems and relationships

### system/layered-system

- **Use:** Explain a program, service, organization, or technical system as meaningful layers.
- **Form:** Three to five stacked layers with one responsibility per layer and only essential cross-layer links.
- **Capacity:** 3–5 layers; 1–3 labels per layer.
- **Presenter:** None by default.
- **Motion:** Relationship or network.

### system/decision-flow

- **Use:** Explain conditional branches, approvals, eligibility, escalation, or exception handling.
- **Form:** One entry condition, 2–4 decision points, labeled branches, and 2–4 terminal states.
- **Capacity:** Up to 8 total nodes; one question per decision node.
- **Presenter:** None.
- **Motion:** Relationship or network, preserving causal branch order.

### system/hub-spoke

- **Use:** Show one organization, rule, service, or event affecting several peer groups.
- **Form:** One central hub connected to 3–6 labeled spokes with no implied chronology.
- **Capacity:** One hub; 3–6 spokes; one relationship label per spoke when necessary.
- **Presenter:** Optional only if the presenter is the central accountable actor.
- **Motion:** Relationship or network, or affected groups when spokes are categorical counts.

### system/dependency-network

- **Use:** Show multiple dependencies, coordination paths, or a small non-linear relationship network.
- **Form:** Four to eight nodes with directional or typed connections, one focal node, and a concise legend.
- **Capacity:** 4–8 nodes; 5–10 edges; at most two edge types.
- **Presenter:** None.
- **Motion:** Relationship or network.

## Geography and media

### media/regional-map

- **Use:** Compare values or statuses across places.
- **Form:** One geographic field with 3–7 labeled regions, a compact legend, and one spatial takeaway.
- **Capacity:** 3–7 highlighted regions; 2–5 legend states.
- **Presenter:** None by default.
- **Motion:** Geography.

### media/flow-map

- **Use:** Explain movement, spread, routes, supply, migration, or service flow between places.
- **Form:** One map with 2–6 origin/destination nodes, directional paths, and a stated time or quantity basis.
- **Capacity:** 2–6 nodes; 1–8 paths; one primary flow highlighted.
- **Presenter:** None.
- **Motion:** Geography, preserving path direction and data meaning.

### media/media-left

- **Use:** Let one image, footage frame, scan, object, or document lead while text interprets it.
- **Form:** Dominant media on the left; one claim, one caption, and optional callout on the right.
- **Capacity:** One media item; one claim; 1–2 callouts.
- **Presenter:** Use the media region for the presenter only when the person is the evidence; otherwise do not stack them.
- **Motion:** Source evidence or quote, or the semantic family represented by the media.

### media/media-right

- **Use:** Let the explanation establish context before the viewer reaches one evidence image or record.
- **Form:** One claim and 1–3 supports on the left; dominant media with caption on the right.
- **Capacity:** One media item; one claim; 1–3 supports.
- **Presenter:** Optional only when it does not compete with the evidence media.
- **Motion:** Headline/text followed by source evidence or the media's semantic family.

### media/evidence-hero

- **Use:** Make one photograph, footage frame, scan, or artifact the principal evidence.
- **Form:** Near-full-field media with one protected headline zone, one caption, and minimal source metadata.
- **Capacity:** One media item; one headline; one caption; up to two anchored callouts.
- **Presenter:** None unless the presenter is the media itself.
- **Motion:** Source evidence or quote; avoid ornamental camera moves that obscure inspection.

### media/evidence-grid

- **Use:** Compare several records, locations, examples, or visual states whose multiplicity is itself evidence.
- **Form:** A 2-by-2, 3-by-1, or 3-by-2 media set with a shared comparison question and per-item labels.
- **Capacity:** 3–6 media items; one short label each; one shared source line.
- **Presenter:** None.
- **Motion:** Source evidence or quote, or quantitative/before-and-after comparison when the grid encodes matched states.

## Diversity and release rules

- Do not choose a different recipe merely to create novelty. Change recipes when the content relationship changes.
- Do not repeat one recipe more than twice consecutively unless a deliberate series requires stable comparison.
- Do not fill every capacity slot. Empty or invented content is a release failure.
- Keep a shared comparison basis, unit, time range, denominator, source, and uncertainty visible whenever the recipe depends on it.
- Split the scene when real content exceeds capacity; do not solve overflow by shrinking text or crowding the presenter.
- The recipe name is authoring metadata, not visible pagination or palette chrome.
- Motion starts from the content meaning after the static frame passes. Background, presenter, public rail, and recurring chrome remain settled.
