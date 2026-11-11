---
name: stats-methods
description: Apply statistics for summaries, tests, distributions, experiments, outliers, and trends.
---

## Summarizing Numeric Data

### Choosing a Center Metric

| Data Characteristic | Recommended Measure | Rationale |
|---|---|---|
| Numeric, meaningful additive scale | Mean | Reflects the total per observation; sensitive to extremes |
| Skewed numeric data | Median and relevant quantiles | Describes the middle and tails without letting extremes dominate |
| Nominal categories | Counts, proportions, mode | Category labels have no numeric order or mean |
| Ordinal responses | Distribution, median, ordered quantiles | Preserves ranking without assuming equal spacing |
| Revenue per user or other skewed economic data | Mean for economics; median/quantiles for typical experience | Different summaries answer different questions |

Choose summaries for the question and measurement scale. Do not average IDs or category codes, or require both mean and median for every KPI. A mean-median gap can suggest asymmetry but does not diagnose the distribution on its own.

### Quantifying Variability

- **Standard deviation**: Root mean squared deviation (with the appropriate population or sample denominator); useful beyond bell-shaped data, but not resistant to extremes.
- **IQR (interquartile range)**: Gap between the 25th and 75th percentiles; resistant to extreme values.
- **Coefficient of variation**: Standard deviation divided by the mean; meaningful for ratio scales with a meaningful zero and positive mean. It is unstable near zero and usually unsuitable for negative means or arbitrary origins such as Celsius.
- **Range**: Maximum minus minimum; gives a quick but outlier-sensitive view of data spread.

### Telling the Story with Percentiles

Choose percentiles relevant to the decision; extreme quantiles in small samples are unstable and depend on interpolation. The following are positions, not guaranteed boundaries of "typical" values:

```
p1:   First percentile (not the minimum)
p5:   Fifth percentile
p25:  First quartile
p50:  Median
p75:  Third quartile
p90:  Top 10% threshold (heavy users, premium tier)
p95:  Ninety-fifth percentile
p99:  Extreme top 1%
```

**Sample insight:** "Half of all sessions last under 4.2 minutes, yet the top decile exceeds 22 minutes, which pushes the average to 7.8 minutes."

### Characterizing Distributions

For numeric measures relevant to the question, examine:

- **Shape**: Gaussian, right-tailed, left-tailed, bimodal, uniform, heavy-tailed
- **Center**: Mean vs. median and the magnitude of their difference
- **Spread**: Standard deviation or IQR as appropriate
- **Extremes**: Count and severity of outliers
- **Boundaries**: Limits implied by the metric definition; growth and other ratios need not lie between 0% and 100%

## Trend Analysis and Projection

### Smoothing Noisy Time Series

```python
# Weekly smoother — useful for daily data with weekday/weekend cycles
df['smooth_7'] = df['metric'].rolling(window=7, min_periods=1).mean()

# Four-week smoother — reduces short-term noise; does not remove all seasonality
df['smooth_28'] = df['metric'].rolling(window=28, min_periods=1).mean()
```

### Period Comparisons

- **Week-over-week**: Full week versus prior full week; for daily values, match weekdays
- **Month-over-month**: Calendar month versus prior calendar month
- **Year-over-year**: Matched periods across years; check holiday shifts, trading days, and definition changes
- **Same-calendar-day**: Matches the exact date from the prior year

### Measuring Growth

```
Simple rate:   (current - prior) / prior
CAGR:          (final / initial) ^ (1 / n_years) - 1
Log rate:      ln(current / prior)
```

Simple growth is undefined at a zero base and often misleading for negative bases; show absolute change and explain the sign convention. Use CAGR and log growth for strictly positive values, with a valid elapsed interval. Do not silently replace zero or negative inputs. Log growth is additive over time, not a general fix for volatility.

### Spotting Seasonal Cycles

1. Visually inspect the raw series first
2. Aggregate by day-of-week to surface weekly rhythms
3. Aggregate by calendar month to surface annual rhythms
4. Use matched-period comparisons where informative; holiday shifts and changing business conditions can still confound them

### Lightweight Forecasting Approaches

For analysts who need quick projections rather than full modeling:

- **Naive**: Forecast equals the most recent observation. Serves as the minimum-viable baseline.
- **Seasonal naive**: Forecast equals the value from the same period in the prior cycle.
- **Linear extrapolation**: Fit a straight line to recent history. Only appropriate when the trend is clearly linear.
- **Trailing average**: Use a rolling mean as the projected value.

Report a conditional point forecast when supported and explain the method, horizon, and assumptions. Add a prediction interval only when a model, validation errors, or another stated method supports its coverage. A sensitivity scenario varies explicit assumptions; it is not a confidence or prediction interval. If uncertainty cannot be quantified from the available data, say so instead of inventing bounds. Backtest against a simple baseline when sufficient history is available.

**Hand off to a specialist** when the pattern is non-linear, multiple seasonal cycles overlap, external drivers (ad spend, holidays) matter, or when forecast precision drives resource decisions.

## Detecting and Handling Outliers

### Identification Techniques

**Z-score approach** (assumes approximate normality):
```python
z = (df['val'] - df['val'].mean()) / df['val'].std()
outliers = df[abs(z) > 3]  # beyond 3 standard deviations
```

**IQR fence approach** (a descriptive flag, not a distribution-free error detector):
```python
q1 = df['val'].quantile(0.25)
q3 = df['val'].quantile(0.75)
iqr = q3 - q1
lo = q1 - 1.5 * iqr
hi = q3 + 1.5 * iqr
outliers = df[(df['val'] < lo) | (df['val'] > hi)]
```

**Percentile cutoff approach** (selects tails even in valid data; not proof of anomalies):
```python
outliers = df[(df['val'] < df['val'].quantile(0.01)) |
              (df['val'] > df['val'].quantile(0.99))]
```

### What to Do with Outliers

Never strip outliers automatically. Follow this decision process:

1. **Diagnose**: Is this a recording error, a legitimately extreme observation, or a sign of a separate population?
2. **Errors**: Verify against source definitions before correcting or excluding (e.g., an impossible age; an epoch timestamp may be valid or a missing-value sentinel)
3. **Legitimate extremes**: Retain but switch to robust summaries (median, IQR)
4. **Distinct populations**: Analyze separately (e.g., enterprise accounts vs. self-serve)

**Document every exclusion**: "We set aside 47 records (0.3% of the dataset) with order values above $50K; these bulk enterprise transactions are covered in a separate section."

### Detecting Anomalies in Time Series

1. Establish an expected baseline (rolling average or year-ago value)
2. Compute the residual: actual minus expected
3. Choose an alert rule using the residual distribution, seasonality, dependence, and acceptable false alarms; a 2-3 standard-deviation rule is only a heuristic
4. Differentiate one-off spikes (point anomalies) from lasting shifts (change points)

## Hypothesis Testing Essentials

### When It Applies

Use formal testing when a sampling or experimental design and its assumptions support inference:

- Evaluating A/B experiment results
- Comparing before/after outcomes (a test alone does not identify the change's causal impact)
- Comparing metrics across customer segments

### Step-by-Step Process

1. Define the estimand, unit of assignment/observation, sampling design, and any pairing or clustering
2. State H0 and H1 (including direction) before inspecting results; a no-difference null is one possible choice
3. Choose a test and significance level appropriate to the decision; alpha controls a procedure's Type I error under H0 and its assumptions, not the probability this finding is false
4. Check assumptions and calculate the estimate, uncertainty, test statistic, and p-value as appropriate
5. Interpret evidence and practical consequences together; non-rejection is not proof of no effect or equivalence

### Selecting the Right Test

| Question | Appropriate Test | Conditions |
|---|---|---|
| Two independent group means differ? | Welch t-test | Independent observations; adequate behavior of the mean's sampling distribution; small, heavy-tailed samples need care |
| Two independent conversion proportions differ? | Proportions z-test or suitable exact method | Defined binary trials; check expected successes and failures for the approximation; repeated users need dependence-aware methods |
| Same entities measured twice? | Paired t-test | Correct pairing, independent pairs, suitable distribution of within-pair differences; pairing does not remove time confounding |
| Three or more independent group means? | ANOVA or Welch ANOVA | Independence; classical ANOVA additionally assumes equal variances; assess residual behavior and planned comparisons |
| Two independent ordinal or continuous distributions differ? | Mann-Whitney U | A rank/distribution test; not a generic test of medians. Location/median interpretations require additional shape assumptions; handle ties and exact/asymptotic choice explicitly |
| Two categorical variables related? | Chi-squared or suitable exact test | Independent counts, mutually exclusive cells, sufficient expected counts for the chi-squared approximation |

For clustered, repeated, censored, or time-dependent data, use a design-aware method rather than treating every row as an independent observation. See the [SciPy Mann-Whitney documentation](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html) for its specific null, alternatives, and implementation assumptions.

### Beyond p-values: Practical Impact

A p-value measures how incompatible the observed test statistic is with a specified null model, through its probability of an equally or more extreme statistic under that model. It is not the probability that H0 is true or that chance alone produced the result. Statistical significance does not measure effect size, practical importance, or causality. See the [ASA statement on p-values](https://www.amstat.org/asa/files/pdfs/P-ValueStatement.pdf). Accompany test results with:

- **Effect magnitude**: "Variant B lifted conversion by 0.3 percentage points"
- **Confidence interval**: Estimate uncertainty with a stated method and level; frequentist coverage concerns the procedure over repeated samples, not a posterior probability for this realized interval
- **Business translation**: Revenue, user, or efficiency implications

### Sample Size Awareness

- Small samples often yield imprecise estimates; validity depends on the design and method, not a universal minimum N
- For proportions, check expected successes and failures in both arms; no single "30 events" rule guarantees reliability
- Detecting subtle effects (e.g., a 1-point conversion shift) can demand thousands of observations per arm
- Use baseline rate/variance, minimum meaningful effect, alpha, power, and design effects for planning; do not invent a detectable-effect threshold from N alone

## Guarding Against Statistical Pitfalls

### Correlation vs. Causation

Whenever a correlation surfaces, explicitly evaluate:
- **Reverse direction**: Perhaps B drives A rather than A driving B
- **Hidden third factor**: Some unmeasured variable C could be behind both
- **Coincidence**: Enough variable pairs will show spurious associations

**Safe phrasing**: "Users who adopt feature X exhibit 30% higher retention"
**Unsafe phrasing**: "Feature X causes 30% higher retention" (requires experimental evidence)

### The Multiple Testing Trap

Running many tests inflates false positives:
- Under 20 true nulls and valid tests at alpha = 0.05, the expected false-positive count is one; this is not a guarantee for any particular set of tests
- If you explored numerous segments before finding the "interesting" one, acknowledge that
- For confirmatory families, use a suitable multiplicity procedure (e.g., Holm/Bonferroni for family-wise error or an appropriate false-discovery-rate method). Reporting the number of tests does not itself control error. Label post hoc exploration and seek independent confirmation

### Simpson's Paradox

An overall trend can invert when you break the data into subgroups:
- Verify that aggregate conclusions hold within each key segment
- Classic scenario: total conversion rises while every segment's conversion falls, because traffic shifted toward a naturally higher-converting segment

### Survivorship Bias

Your dataset only contains entities that persisted long enough to be recorded:
- Studying current users ignores everyone who already left
- Profiling winning products overlooks the failures
- Routinely ask: "Who is absent from this data, and would including them change the conclusion?"

### Ecological Fallacy

Group-level patterns may not describe individuals:
- "Nations with higher X tend to have higher Y" does not mean the same holds per person
- Resist applying aggregate statistics to individual-level predictions

### Illusory Precision

Overly specific numbers suggest unjustified confidence:
- "Churn will be 4.73% next quarter" implies an accuracy that rarely exists
- Use supported intervals or explicitly defined scenarios; arbitrary ranges also imply unjustified confidence
- Round to the level of certainty you actually possess
