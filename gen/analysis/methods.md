# Select methods by the question

Choose a method for the conclusion it can support, then check its inputs. Use
additional methods only for distinct subquestions. Do not fill a fixed quota of
frameworks or force an exploratory brief into a recommendation.

| Question | Candidate method | Minimum inputs | Required analytical result |
| --- | --- | --- | --- |
| What is happening? | Descriptive analysis or structured evidence synthesis | Defined population, period, measures, and attributable observations | Magnitude, distribution or themes, comparison basis, and coverage limits |
| What changed, and where? | Driver decomposition, funnel, segment or cohort analysis | Comparable periods, stable metric definitions, denominators and relevant dimensions | Reconciled contributions or stage/segment changes; candidate causes separated from demonstrated effects |
| Did an intervention make a difference? | Experiment analysis or an appropriate causal design | Outcome, assignment/sampling unit, comparison, timing, dependence, and design assumptions | Effect estimate and uncertainty; design limitations and practical significance |
| Which option should we choose? | Hard-constraint screening, total cost, multi-criteria comparison | Alternatives, requirements, usage, costs, decision criteria and their priorities | Feasible options, comparable costs, tradeoffs, and conditions under which the recommendation changes |
| Is a market opportunity attractive? | Market sizing, competitive structure, customer-job analysis | Market boundaries, disjoint segments, dated demand and competitor evidence, achievable reach | Conditional opportunity estimate, competitive constraints and unmet needs supported by evidence |
| What could happen next? | Baseline forecast or scenario and sensitivity analysis | Dated comparable history or explicit driver assumptions and horizon | Baseline, plausible scenarios, influential assumptions and decision thresholds |
| Which explanation is better supported? | Rival hypotheses and evidence appraisal | Observations, competing explanations, source lineage and relevant counterevidence | Evidence that distinguishes explanations; residual uncertainty and discriminating next observations |

## Business change and growth

For revenue, start with a driver identity such as units times price. For a
conversion change, start with the eligible population and funnel stages. For
retention, compare cohorts at the same age. Inspect segment mix before attributing
an aggregate change to product performance.

Example for one comparable product: with quantity `q` and price `p`,
`delta_revenue = (q1-q0)*p0 + q1*(p1-p0)`. The allocation of the interaction is
explicit here. State the chosen decomposition convention and reconcile it to the
total; a driver identity alone does not establish why behavior changed.

If only aggregate rates are available, explain the observed change and request
or locate denominators and segments before claiming a root cause.

## Options and procurement

1. Apply non-negotiable constraints before scoring. Unknown compliance with a
   requirement stays unknown; it is not a pass or a zero-valued cost.
2. Compare like-for-like usage, currency, period, taxes, support, implementation,
   migration, and ongoing costs. Cite quote dates and contractual assumptions.
3. Derive criteria from the user's goals. Make proposed weights and subjective
   judgments explicit. Do not manufacture a weighted ranking when priorities
   are unresolved; show tradeoffs or conditional rankings.
4. Vary consequential assumptions and find switching or break-even conditions.
   State what a pilot or additional evidence needs to resolve.

## Markets and competition

- **TAM/SAM/SOM:** define buyer, geography, offering, period, unit, and denominator
  before calculating. Bottom-up counts times spending and top-down estimates
  are independent approaches to reconcile, not quantities to add. Keep segments
  disjoint. SOM needs reachable customers, capacity, channels, and conversion
  assumptions rather than an arbitrary market-share percentage.
- **Porter's five forces:** examine supplier and buyer power, substitutes, entry
  barriers, and rivalry using evidence of behavior and economics. It describes
  industry pressures; it does not by itself establish a company's ability to win.
- **JTBD:** use interviews, observed workflows, or attributable customer evidence
  to describe the situation, desired outcome, alternatives and switching costs.
  Inferred motives remain hypotheses; online anecdotes do not estimate prevalence.
- **PESTEL or SWOT:** use selectively to structure relevant context or summarize
  findings. Each consequential item needs evidence and an implication. The
  completed framework is not itself support for a conclusion.
- **DuPont analysis:** for compatible financial statements, decompose return on
  equity into margin, asset turnover, and leverage. Align periods and average
  balance definitions; explain when unusual or negative denominators make the
  decomposition uninformative. It describes accounting drivers, not valuation.

## Experiments and statistical comparisons

Use [data-analysis.md](data-analysis.md) to choose a test from the target effect,
outcome type and sampling design. Before/after observations without a credible
counterfactual support a change description, not an intervention effect. Unknown
assignment, dependence, or selection cannot be repaired by a small p-value.

## Forecasts and scenarios

Compare a forecast against a simple recent-value or seasonal baseline, using
time-ordered evaluation with no future leakage. Show the horizon, data cutoff,
errors and material assumptions. Separate model-based prediction intervals from
scenario ranges; neither is automatically a guarantee or a confidence interval.

When history is inadequate, use explicit low/base/high assumptions and explain
the drivers. Do not invent probabilities or present assumptions as observed data.

## Rival explanations

List plausible alternatives before favoring one. For each important observation,
record whether it supports, contradicts, or cannot distinguish the alternatives.
Seek disconfirming evidence and inspect dependence among sources. Report the
best-supported interpretation and the evidence that would change it. Do not
convert checklist counts into probabilities or evidence-quality scores.
