# Work with data

## Establish the measurement

Record the source or query, snapshot time, row meaning, key, metric definition,
units, population, exclusions, period, timezone, and comparison. Inspect schema
and a small sample before writing a calculation. Preserve raw inputs and record
cleaning steps separately.

Check duplicate keys, missingness, join cardinality, group sizes, partial periods,
outliers and unit consistency. A left join can multiply rows; reconcile counts
and totals before and after joins. Missing values are unknown unless the source
definition explicitly makes them zero. Diagnose unusual values before exclusion.
Keep identifiers as strings when leading zeros matter.

For spreadsheets inspect formulas and cached results. A missing cached formula
result is not zero; use a compatible calculation engine or a transparent
recalculation. Check date encodings, merged headers and totals embedded in data.
Do not claim to have read sheets or recalculated formulas that were not inspected.

## Compute descriptive and business results

- Report the relevant counts and denominators alongside rates. Aggregate rates
  as total numerator divided by total eligible denominator; averaging segment
  rates answers a different question unless explicitly weighted as intended.
- Distinguish percentage points from percent change. A zero baseline makes
  relative growth undefined; negative baselines need an explicit interpretation.
- Use mean/median and spread according to the distribution and question. Quantile
  estimates need their convention and sample size when those matter.
- Align cohort age, period completeness, currency, inflation basis, definitions
  and segment boundaries before comparing. Diagnose changing population mix.
- Reconcile subtotals and independently spot-check important calculations.
  Retain queries, formulas, input references, and actual computed results.

## Select inference by design

State the target effect, outcome type, independent unit, pairing or clustering,
planned comparisons, meaningful effect threshold, and uncertainty level. Label
exploratory decisions that were made after seeing outcomes.

| Design and target | Candidate approach | Check before interpreting |
| --- | --- | --- |
| Two independent groups, difference in continuous means | Welch t-test and interval | Independent units, sample size, distribution and influential values; consider justified robust sensitivity analysis |
| Paired observations, mean within-unit difference | Paired t-test on aligned differences | Genuine pairing; distribution of differences; do not treat repeat observations as independent |
| Multiple independent groups | Appropriate ANOVA/Welch ANOVA and planned contrasts | Variance/design assumptions and multiplicity across the comparison family |
| Binary outcomes or contingency counts | Proportion interval and suitable chi-square or exact test | Denominators, independence, sparse cells and sampling design |
| Relationships between variables | Correlation or outcome-appropriate regression | Functional form, dependence, confounding, residuals and out-of-sample use |
| Repeated, clustered or time-dependent observations | Model dependence explicitly | Cluster/subject/time structure; use qualified guidance if the design is outside available capability |

Rank tests answer rank/distribution questions, not automatically differences in
medians. Select methods from the question and design rather than switching tests
at a normality-test p-value threshold. Use plots and diagnostic checks together.

Report effect estimates and uncertainty, sample sizes, missingness, assumptions,
and practical consequences. A non-significant test does not prove no effect, and
a p-value is not the probability a hypothesis is true. Account for multiple
comparisons and repeated peeking; do not report a selected favorable comparison
as if it were the only planned test. Avoid post-hoc observed power as an
explanation for a null result.

## Interpret limits

Associations, predictive accuracy and before/after movement do not on their own
identify causation. Check selection, attrition, measurement changes, confounding,
overlapping samples and survivorship. Aggregate and subgroup trends can disagree.
If data cannot support the requested inference, report the descriptive result
and the design or evidence needed to answer the stronger question.

## Reusable SQL patterns from DeerFlow

The following patterns retain the upstream examples. Use an available SQL engine or task-local Python environment after inspecting actual tables and column names; replace the example names with the input schema. Check join cardinality and reconcile totals. This integration does not install DeerFlow’s runtime or its DuckDB helper, which installs dependencies and a spatial extension automatically.


### Basic Exploration
```sql
-- Row count
SELECT COUNT(*) FROM Sheet1

-- Distinct values in a column
SELECT DISTINCT category FROM Sheet1

-- Value distribution
SELECT category, COUNT(*) as cnt FROM Sheet1 GROUP BY category ORDER BY cnt DESC

-- Date range
SELECT MIN(date_col), MAX(date_col) FROM Sheet1
```

### Aggregation & Grouping
```sql
-- Revenue by category and month
SELECT category, DATE_TRUNC('month', order_date) as month,
       SUM(revenue) as total_revenue
FROM Sales
GROUP BY category, month
ORDER BY month, total_revenue DESC

-- Top 10 customers by spend
SELECT customer_name, SUM(amount) as total_spend
FROM Orders GROUP BY customer_name
ORDER BY total_spend DESC LIMIT 10
```

### Cross-file Joins
```sql
-- Join sales with customer info from different files
SELECT s.order_id, s.amount, c.customer_name, c.region
FROM sales s
JOIN customers c ON s.customer_id = c.id
WHERE s.amount > 500
```

### Window Functions
```sql
-- Running total and rank
SELECT order_date, amount,
       SUM(amount) OVER (ORDER BY order_date) as running_total,
       RANK() OVER (ORDER BY amount DESC) as amount_rank
FROM Sales
```

### Pivot-style Analysis
```sql
-- Pivot: monthly revenue by category
SELECT category,
       SUM(CASE WHEN MONTH(date) = 1 THEN revenue END) as Jan,
       SUM(CASE WHEN MONTH(date) = 2 THEN revenue END) as Feb,
       SUM(CASE WHEN MONTH(date) = 3 THEN revenue END) as Mar
FROM Sales
GROUP BY category
```
