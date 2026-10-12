# Evidence and analytical checks

## Collect against the question

Route each important question to a source close to the event or measurement:
original data, official records, filings, first-party documentation, inspectable
studies or attributable interviews. First-party material can establish a
published price or stated feature; it is not independent evidence of effectiveness.
Read the relevant source passage rather than relying only on search snippets.

Record the exact location, producer, publication date when stated, retrieval
date, covered population/period, unit, method and limitations. A source retrieved
today can still describe an old period. For supplied files, preserve filename and
page/table/sheet or query identifiers. Do not invent missing metadata.

Trace syndicated or aggregated material to its producer. Repeated copies are
not independent corroboration. When sources disagree, compare scope, dates,
definitions and methods before choosing; keep unresolved disagreement visible.
Unknown product features or costs remain unknown.

## Keep claims separate from evidence

For substantive reports, retain a compact working evidence record. It can be a
table, notebook or JSON; use the schema below if using the bundled checker.
One source need not support every sentence in a paragraph. A derived value must
point to its inputs and reproducible calculation rather than pretend that a
source published that value. Separate facts, calculations, estimates, forecasts,
interpretations and recommendations.

The [synthetic example](../assets/evidence.example.json) illustrates this structure:

| Record | Fields |
| --- | --- |
| Source | `id`, `locator`, `accessed_on`; optional `title`, `publisher`, `published_on`, `coverage`, `limitations` |
| Claim | `id`, `text`, `kind`, `status`, `source_ids`; `basis` for derived statements; `assumptions` for estimates, forecasts or conditional claims; `limitations` for conditional/unverified claims |

`kind` is `fact`, `calculation`, `estimate`, `forecast`, `interpretation` or
`recommendation`. `status` is the analyst's declared `supported`, `conditional` or
`unverified`. Estimates and forecasts stay conditional unless explicitly
unverified; assumptions are not observations. `source_ids` refer to inputs and
supporting passages. `basis` identifies the inference or local code/query/formula
and output. Conditional and unverified statements must disclose their limits.

From the installed `analysis-methods` skill directory:

```bash
python3 scripts/check_evidence.py /path/to/evidence.json
```

The checker detects missing fields, duplicate IDs, invalid dates, dangling source
references and undeclared uncertainty. It does not fetch sources, verify their
truth, judge source independence, recompute calculations, or establish that a
claim is supported. Its output uses `structure_valid`, never report approval.
Review source support and computations separately, including the synthetic example.

## Challenge important judgments

For each consequential inference, ask:

- What alternative explanation also fits these observations?
- Which evidence distinguishes the alternatives, and what contradicts the favored one?
- Are multiple sources or samples actually independent?
- Does the claim extend beyond the sampled population, time or geography?
- Which assumption or measurement would change the recommendation if wrong?

Distinguish missing reporting from proof that a procedure did not occur. Examine
selection, measurement, confounding and uncertainty where applicable. Explain
confidence in words with its reasons; do not derive a probability or a quality
score from the number of sources or checked boxes.

## Finish or narrow

Continue collecting when a material gap can be resolved within the task's scope
and resources. Otherwise deliver the useful supported portion and explicitly
narrow the conclusion. Describe a targeted next observation, query, interview or
experiment if it would resolve the uncertainty. Do not let unsupported claims
become certain in an executive summary or chart title.
