# Targeted content checks

Use the applicable checks for substantive analysis or consequential dependencies
that need review. Choose by actual content, not by file format or document label.
Routine source-backed instructions and straightforward restatements use the
default author's coverage, accuracy and consistency check.

## Author only the needed analysis

Preserve source facts and meaning; retain exact wording only where required by
the request or source constraints. Keep facts, assumptions and proposed actions
distinct. Research only missing information needed for the requested
outcome; retain traceable source locations for factual claims. When the supplied
evidence cannot establish a cause or decision, identify the missing input and
next verification step. A qualifier such as "probably" does not supply evidence.

For interacting rules or procedures, check who acts, when, under which conditions,
and how exceptions return to the normal process. Resolve conflicting roles,
deadlines, prerequisites and permissions without inventing new policy. Advice
must address the problem it claims to solve. Preserve uncertainty when the
necessary evidence is absent.

Only when values must be derived, keep the needed calculation in a small data
file or script and reuse its results in text, tables and charts. Literal supplied
numbers and dates do not need a model. Use one set of units, periods and labels;
generate requested simulated data once. Recompute important results from the
raw inputs rather than treating numbers copied from the draft as expectations.

Do not add forecasts, scenarios, counterfactual decompositions, payback models
or numeric thresholds unless needed for the user's requested analysis. State
each finding where it supports the document instead of repeating every table.
For financial material, preserve the source's accounting scope: unspecified
"cost" is not automatically direct cost, gross profit or net profit. Use a
neutral label or one explicit, consistently applied assumption.

## Review dependencies in parallel with preparation

For substantive inferences beyond the supplied facts, conflicting evidence, or
consequential dependencies among rules and exceptions, use one bounded independent
review when agent tools are available. Routine instructions, straightforward
source summaries and isolated arithmetic checked directly use author mode.
Give the reviewer the original
request, raw sources, complete draft and any actual calculations; exclude the
author's passing conclusions. Use the same default model without an override.

Start a background review once the draft is complete; continue preparation and
the overview inspection while it runs. Pass `--content-review independent` to
`prepare_document.py`. Where delegation is unavailable, perform these checks
yourself, use the author mode, and record that limitation in the content note.

The reviewer returns only specific errors with locations and evidence, or a
concise passing assessment. Check requested coverage and source fidelity, then
the actual dependencies present:

- For rules and procedures, follow normal and exception paths to find
  contradictions, missing handoffs and unreachable steps.
- For computed material, recompute key results and reconcile repeated numbers,
  targets, assumptions, units and time periods throughout the draft.
- For explanations, verify that the evidence supports the named result. A
  correct number does not prove its interpretation: averages are not marginal
  contributions, observed changes are not causes, and required volume does not
  establish available capacity. Cash timing and accounting results can differ.
- For sufficiency, impossibility or efficiency claims, try a counterexample
  under the stated assumptions. Missing evidence calls for a narrower statement
  or validation action, not a new speculative model.

The reviewer reads the full draft, not just a list of claims chosen by the author.
Do not expand the report or propose cosmetic changes during this check. Collect
content and visible layout defects, repair them together, then perform the full
page review on the final candidate. Recheck changed conclusions and dependencies;
do not repeat an unchanged passing assessment. Record the current outcome in
`qa/review.json` under `content`, preserving the required reviewer mode and a
specific observation. Complete both content and page review before acceptance.
