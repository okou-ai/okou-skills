# Behavioral checks

These synthetic cases evaluate method selection and supported conclusions.
Run the candidate `analysis-methods` skill with only the task and named fixture.
Give the evaluator this rubric after completion, not to the agent doing the task. Use a
temporary workspace; do not send messages, publish files, or call paid services.
Helper tests do not substitute for these behavioral checks. Install only this
skill for the analytical cases to check that it works without `gen` or
`office-files`.

## Conversion change

Task: "Using only conversion.csv, explain why overall conversion fell in September.
Was the product worse? Give a short Chinese management brief, show your arithmetic,
and identify what we should check next. Do not generate an Office file."

Expected behavior:

- Inspect data and compute total conversions / total eligible users.
- August: 28%; September: 14.3%; change: -13.7 percentage points.
- Search improves from 10% to 12%; referral improves from 30% to 35%.
- Identify the shift toward the lower-converting search channel. A decomposition
  using baseline channel rates gives -16 points from mix and +2.3 from within-channel
  rates; another valid explicitly reconciled convention is acceptable.
- Separate the arithmetic explanation from causal claims about the product or
  why the channel mix changed. No unsupported forecast or external research.
- Deliver a concise brief without starting an artifact pipeline.

## Incomplete procurement quote

Task: "Use vendor-quotes.txt to recommend the better vendor within our budget.
Show the first-year cost and explain what would change your recommendation."

Expected behavior:

- Vendor A: USD 12,000 plus unknown migration; Vendor B: USD 17,000 total.
- A is cheaper if migration is below USD 5,000, ties at USD 5,000, and exceeds
  the stated budget if migration exceeds USD 6,000.
- Do not treat missing migration as zero or fabricate scores, probabilities,
  service-quality differences, discounts or additional constraints.
- Give a conditional recommendation and a targeted request for A's migration
  quote. Do not block the already possible cost comparison.

## Formatting only

Task: "Rewrite this supplied report sentence in more formal English without
adding facts: 'Sales were 10 in August and 12 in September.'"

Expected behavior:

- Preserve the statement and scope. Do not launch research, generate a file,
  demand a source ledger, or create a market framework.

## Assessment

Record the skill revision, fixture, actual tools/calculations, method used,
answer, unsupported claims, and result against each criterion. Critical failures
are wrong arithmetic, claiming an unsupported cause, silently filling missing
data, or violating source/output restrictions. Framework terminology and fluent
writing do not compensate for those failures. These small cases establish local
behavior only; they are not a report-quality benchmark or production acceptance.
