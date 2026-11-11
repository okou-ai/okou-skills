# Office analysis behavioral checks

These synthetic cases exercise analysis before file construction. They are not
production skill resources, Office interoperability tests or a calibrated product
benchmark. Use fresh sessions and the same model, effort, tools and budget for
each condition. Return content only; rendering is outside this check.

The [2026-11-11 exploratory pilot](pilot-20261111/README.md) preserves raw answers,
hashes, the anonymous review and its limits. It did not demonstrate a consistent
comparative quality improvement.

## Prepare isolated inputs

From a checkout containing this evaluator:

```bash
python3 evals/office-analysis/prepare.py \
  --ref <exact-commit> --case operating-review --out /tmp/office-analysis-run
```

The destination must not already exist. The package contains only the selected
case, the Office Markdown guidance from that Git revision, an execution request and a hash
manifest. It excludes this README and the reviewer instructions. Give the author
only that package. Do not give reference judgments or another condition's answer.
Preserve the request, manifest, raw answer, tool results and actual configuration.
The manifest freezes inputs; it is not evidence that the author read a file or ran
a check. Capture those actions from the actual run.
Isolation here means separate input directories on a shared host, not an
execution sandbox. Record that limitation when reporting the pilot.

Compare main, the previous analysis revision and the candidate. For repeatability
use independent repeats and counterbalance condition order. Keep all attempts;
do not select the best one. Freeze [reviewer.md](reviewer.md) before authoring.
Give reviewers the case inputs and anonymized outputs, without condition labels
or earlier scores. Preserve disagreements and their source evidence.

## Cases and observations

- `operating-review`: a measurable cost-rate residual with an unknown business
  cause; do supported arithmetic without claiming the residual is outsourcing.
- `fixed-cost-review`: the same totals with a fixed-plus-variable cost model;
  [variant review](reviewer-fixed-cost.md) checks that decomposition follows it.
- `launch-plan`: fixed versus variable cost extrapolation and an overloaded
  weekly draft; a proposal must satisfy its own model and resource constraints.
- `research-comparison`: different configurations and source-specific baseline
  results; retain identities and propose a comparison that addresses confounding.
- `narrow-edit`: a wording-only request; preserve the supplied numbers, scope
  and pending status without initiating new analysis.

Review important work performed, source fidelity, assumption consistency and
scope. Do not score section counts, length or specific phrases. Record new
errors and unsupported additions alongside useful analysis. If all conditions
pass, report a ceiling on these cases rather than an improvement. A small
single-run pilot does not estimate a causal effect or establish deployment.

For a later product evaluation, repeat selected tasks through the actual Okou
authoring path with requested native deliverables and the existing file checks.
Add further unseen variants, including genuinely missing inputs,
so the agent cannot obtain credit by mechanically applying a learned formula.

Check input isolation and revision/hash preservation with:

```bash
python3 -m unittest discover -s evals/office-analysis -p 'test_*.py'
```
