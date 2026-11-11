---
name: analysis-qa
description: Quality-check data analysis for joins, metrics, denominators, date ranges, leakage, and statistical pitfalls.
---

## Review Checklist

Select checks relevant to the question, data, and method. Prioritize failures that could change the conclusion or action. Keep calculations and source traces in working notes; include methods, caveats, and supporting detail in the user's requested format where they affect interpretation. Preserve the task's permitted sources and deliverable scope.

### Data Foundation

- [ ] **Correct sources**: Confirmed that the tables and datasets used are the appropriate ones for this question
- [ ] **Freshness**: Data recency is sufficient; the "data as of" date is noted
- [ ] **Coverage**: No unexpected time gaps or missing segments in the dataset
- [ ] **Null treatment**: Null rates in critical columns have been reviewed; nulls are excluded, filled, or explicitly flagged
- [ ] **Duplicate control**: Keys, cardinalities, and totals at the intended grain confirm no unintended double-counting; row counts alone are insufficient
- [ ] **Filter accuracy**: Every WHERE clause and filter condition has been verified; nothing is accidentally excluded or included

### Computation Integrity

- [ ] **GROUP BY correctness**: All non-aggregated columns appear in GROUP BY; the aggregation grain matches the analytical question
- [ ] **Denominator validity**: Rates and percentages use the intended base population; division by zero is prevented
- [ ] **Temporal alignment**: Period boundaries, business timezone, exposure, and completeness are comparable; unequal durations or partial periods are handled explicitly
- [ ] **Join behavior**: JOIN types are intentional (INNER vs. LEFT); many-to-many relationships have not silently inflated totals
- [ ] **Metric fidelity**: Calculated metrics align with how the business defines them; any deviations are documented
- [ ] **Additive consistency**: Sub-totals sum to the reported total where expected; non-additive cases (overlap, double-counting) are explained

### Plausibility Assessment

- [ ] **Definition-based bounds**: Values satisfy the metric's actual domain. A bounded proportion lies in 0-100%; growth rates, event-per-person ratios, ROI, and driver shares may exceed those limits. Net revenue may be negative due to returns or adjustments; investigate the definition before treating a sign as an error
- [ ] **Trend coherence**: Time series show no unexplained jumps or drops
- [ ] **Source agreement**: Compare with available, authorized controls using the same definition, snapshot, scope, and period; explain discrepancies. Do not fetch external benchmarks for a closed-data task
- [ ] **Ballpark math**: Total revenue roughly equals per-user revenue times user count, etc.
- [ ] **Boundary behavior**: Results make sense for edge cases — a single day, a single user, a single category

### Presentation Quality

- [ ] **Accurate visuals**: Bar charts begin at zero; axes have labels; scales are consistent across panels
- [ ] **Clean formatting**: Numbers use appropriate precision, consistent currency/percent notation, and thousands separators
- [ ] **Descriptive titles**: Headings convey the insight, not just the metric name; date ranges are included
- [ ] **Transparent caveats**: Material limitations and assumptions appear beside the conclusions they constrain
- [ ] **Reproducibility**: Working records retain the inputs, transformations, and calculations needed to recreate material claims; share them when requested or necessary for the audience

## Recognizing Common Mistakes

### Join Grain and Inflated Totals

**What goes wrong**: A join changes the row grain, and a measure is then aggregated as if its original grain were preserved. Even a legitimate one-to-many join repeats the parent's measures.

**Detection method**:
```sql
-- Compare row counts before and after the join
SELECT COUNT(*) FROM orders;          -- 1,000 order rows
SELECT COUNT(*) FROM orders o
JOIN line_items li ON o.id = li.order_id;  -- 3,500 may be correct line-item rows
```

**Prevention**:
- Define the output grain and expected cardinality, then inspect matched/unmatched keys and before/after counts
- `COUNT(DISTINCT o.id)` can count matched orders; it does not repair duplicated order revenue or restore orders lost to an INNER JOIN
- Aggregate child facts to the required parent grain before joining when appropriate. When joining multiple child tables, prevent a line-item-by-payment cross-product
- Reconcile both entity coverage and measure totals; do not use `SUM(DISTINCT amount)` as a repair, since different orders can have the same amount

### Survivorship Bias

**What goes wrong**: The analysis only covers entities that still exist, ignoring those that were removed, churned, or failed.

**Typical scenarios**:
- Studying behavior of "active users" while ignoring everyone who left
- Benchmarking against "companies on our platform" while skipping those who evaluated and moved on
- Analyzing traits of "successful" cases without any "unsuccessful" comparison group

**Prevention**: Before drawing conclusions, ask: "Who is absent from this dataset, and would their presence change the story?"

### Partial Period Comparisons

**What goes wrong**: A month, week, or quarter that is still in progress gets compared to a completed one.

**Typical scenarios**:
- "January revenue is $500K vs. December's $800K" when January is only half over
- "Signups are down this week" when checked on Tuesday against a full prior week

**Prevention**: Compare completed or matched elapsed periods where possible. Equal day counts alone do not adjust for weekdays, holidays, exposure, or late-arriving data; disclose those differences. Extrapolation of a partial period is a separate assumption, not an observed total.

### Shifting Denominators

**What goes wrong**: The population used as a denominator changes between periods, making rate comparisons invalid.

**Typical scenarios**:
- Conversion rate appears to improve because the definition of "eligible visitor" was narrowed
- Churn rate shifts because "active user" was redefined mid-analysis

**Prevention**: Lock in consistent definitions across every period being compared. Flag any definition changes.

### Averaging Pre-Computed Averages

**What goes wrong**: Taking the mean of group-level averages ignores differences in group size, producing an incorrect overall figure.

**Illustration**:
- Segment A: 100 orders, $50 average order value
- Segment B: 10 orders, $200 average order value
- Incorrect overall average: ($50 + $200) / 2 = $125
- Correct weighted average: (100 * $50 + 10 * $200) / 110 = $63.64

**Prevention**: Recompute from raw records or combine group sums and the correct denominator counts. An unweighted mean of group means answers a different question (equal weight per group) and equals the pooled mean only under appropriate conditions, such as equal group sizes.

### Timezone Inconsistencies

**What goes wrong**: Different source systems record timestamps in different zones, causing misaligned daily rollups and join mismatches.

**Typical scenarios**:
- Backend events logged in UTC while the reporting layer uses US Pacific
- Two tables that define "today" with different cutoff hours

**Prevention**: Parse each source's timezone and align timestamps as instants before joining. Bucket dates in the requested business/reporting timezone, accounting for daylight-saving changes. UTC storage is compatible with local reporting, but UTC calendar days need not match business days. If the source timezone is unknown and boundary records matter, disclose the ambiguity rather than assuming it away.

### Circular Segmentation

**What goes wrong**: Segments are defined using the very outcome being measured, creating tautological findings.

**Typical scenarios**:
- "Users who finished onboarding retain better" — finishing onboarding is itself a retention signal
- "Power users drive more revenue" — revenue generation is what made them power users

**Prevention**: Base segment definitions on characteristics measured before the outcome period, not on the outcome itself.

## Sanity-Checking Results

### Quick Magnitude Tests

| Metric Category | Validation Approach |
|---|---|
| User counts | Cross-reference against known DAU/MAU benchmarks |
| Revenue totals | Reconcile to a comparable revenue control; ARR is a run-rate measure, not interchangeable with period revenue |
| Conversion proportions | 0-100% only when the numerator is a subset of unique eligible trials; event-per-user ratios can exceed 100% |
| Growth rates | Verify the base, sign, and coverage; a zero base is undefined and rapid growth is not itself an error |
| Averages | Verify sums, weights, and denominator grain; inspect the relevant distribution |
| Segment shares | Sum to 100% only for an exhaustive, mutually exclusive partition; explain overlap or missing segments |

### Cross-Validation Approaches

1. **Dual calculation**: Derive the same metric via two independent query paths and confirm they match
2. **Record-level spot checks**: Select a handful of specific entities and manually trace their numbers end to end
3. **Benchmark comparison**: Use available, authorized dashboards, finance controls, or prior outputs only when their definitions are comparable
4. **Arithmetic reversal**: If total revenue is X and there are N users, does X / N approximate the reported per-user figure?
5. **Micro-slice testing**: Filter to a single day, user, or category and confirm the micro-result is sensible

### Signals That Demand Investigation

- Movements material to the decision or unusual for the metric's history and exposure, without a supported explanation
- Totals or sums that land on suspiciously round numbers (possible filter or default-value artifact)
- Rates pegged at exactly 0% or 100% (may indicate missing data rather than perfect outcomes)
- Results that confirm the hypothesis too neatly (real data is almost always messy)
- Identical values appearing across different time periods or segments (suggests a dimension is being ignored)

## Ensuring Reproducibility

### Working Record and Reader-Facing Detail

Retain enough detail internally to reproduce the material calculations. Use the fields below as relevant working notes or as a methods appendix when requested; they are not a mandatory report structure. A concise answer or requested Office artifact need not ship all SQL/code, a separate audit file, or a second deliverable.

```markdown

## Analysis: [Title]

### Business Question
[The precise question this work answers]

### Sources
- Table: [schema.table_name] (snapshot date: [date])
- Table: [schema.other_table] (snapshot date: [date])
- External file: [filename] (origin: [description])

### Metric and Segment Definitions
- [Metric A]: [Precise calculation formula]
- [Segment X]: [Exact inclusion/exclusion criteria]
- [Time window]: [Start] through [end], [timezone]

### Analytical Approach
1. [First step and its purpose]
2. [Second step]
3. [Third step]

### Assumptions and Known Limitations
- [Assumption and why it holds]
- [Limitation and its potential effect on conclusions]

### Results
1. [Finding with supporting evidence]
2. [Finding with supporting evidence]

### Calculations and Queries
[Relevant workings, source locations, query/code versions, and reconciliation checks]

### Warnings for the Reader
- [Anything the audience should weigh before acting on these results]
```

### Annotating Analytical Code

For SQL or Python that others may reuse:

```python
"""
Title: Monthly Cohort Retention
Author: [Name]
Created: [Date]
Sources: events, users
Last cross-checked: [Date] — matched dashboard within 2%

Objective:
    Build monthly retention cohorts anchored on each user's first event date.

Assumptions:
    - "Active" = at least one recorded event in the calendar month
    - Internal and test accounts excluded (user_type != 'internal')
    - Event timestamps aligned as instants; cohort months use [reporting timezone]

Output:
    Retention grid: rows are cohort months, columns are months since first event.
    Cell values are retention percentages (0-100).
"""
```

### Maintaining an Audit Trail

- Retain relevant queries, scripts, or calculation traces in the task's permitted workspace; publish or share them only when authorized
- Record the exact data snapshot date used for each analysis run
- When refreshing a recurring analysis, document what changed and why
- Link current results to prior versions so trends in the analysis itself are traceable
