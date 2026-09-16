---
name: stats-methods
description: Apply statistics for summaries, tests, distributions, experiments, outliers, and trends.
---

## Summarizing Numeric Data

### Choosing a Center Metric

| Data Characteristic | Recommended Measure | Rationale |
|---|---|---|
| Symmetric, outlier-free | Mean | Maximally efficient estimator |
| Asymmetric or outlier-heavy | Median | Unaffected by extreme values |
| Non-numeric or ranked | Mode | Sole option for categorical data |
| Business KPIs like revenue per user | Both mean and median | The gap between them reveals skewness |

**Guideline:** For any business metric, present the mean alongside the median. When they differ substantially, the distribution is skewed and the mean by itself will mislead.

### Quantifying Variability

- **Standard deviation**: Typical distance from the mean; best suited to bell-shaped data.
- **IQR (interquartile range)**: Gap between the 25th and 75th percentiles; resistant to extreme values.
- **Coefficient of variation**: Standard deviation divided by the mean; enables apples-to-apples variability comparison across different scales.
- **Range**: Maximum minus minimum; gives a quick but outlier-sensitive view of data spread.

### Telling the Story with Percentiles

Go beyond averages by reporting a percentile ladder:

```
p1:   Floor of the distribution (bottom 1%)
p5:   Lower boundary of typical values
p25:  First quartile
p50:  Median — the representative observation
p75:  Third quartile
p90:  Top 10% threshold (heavy users, premium tier)
p95:  Upper boundary of typical values
p99:  Extreme top 1%
```

**Sample insight:** "Half of all sessions last under 4.2 minutes, yet the top decile exceeds 22 minutes, which pushes the average to 7.8 minutes."

### Characterizing Distributions

For every numeric column, document:

- **Shape**: Gaussian, right-tailed, left-tailed, bimodal, uniform, heavy-tailed
- **Center**: Mean vs. median and the magnitude of their difference
- **Spread**: Standard deviation or IQR as appropriate
- **Extremes**: Count and severity of outliers
- **Boundaries**: Natural limits such as zero floors or 100% ceilings

## Trend Analysis and Projection

### Smoothing Noisy Time Series

```python
# Weekly smoother — useful for daily data with weekday/weekend cycles
df['smooth_7'] = df['metric'].rolling(window=7, min_periods=1).mean()

# Four-week smoother — irons out both weekly and monthly rhythms
df['smooth_28'] = df['metric'].rolling(window=28, min_periods=1).mean()
```

### Period Comparisons

- **Week-over-week**: Same weekday, one week apart
- **Month-over-month**: Calendar month versus prior calendar month
- **Year-over-year**: The gold standard for businesses with seasonal patterns
- **Same-calendar-day**: Matches the exact date from the prior year

### Measuring Growth

```
Simple rate:   (current - prior) / prior
CAGR:          (final / initial) ^ (1 / n_years) - 1
Log rate:      ln(current / prior)   # more stable for volatile series
```

### Spotting Seasonal Cycles

1. Visually inspect the raw series first
2. Aggregate by day-of-week to surface weekly rhythms
3. Aggregate by calendar month to surface annual rhythms
4. Always use year-over-year or matched-period comparisons to separate trend from seasonality

### Lightweight Forecasting Approaches

For analysts who need quick projections rather than full modeling:

- **Naive**: Forecast equals the most recent observation. Serves as the minimum-viable baseline.
- **Seasonal naive**: Forecast equals the value from the same period in the prior cycle.
- **Linear extrapolation**: Fit a straight line to recent history. Only appropriate when the trend is clearly linear.
- **Trailing average**: Use a rolling mean as the projected value.

**Always express forecasts as ranges, not point estimates:**
- Good: "Next month should bring 10,000 to 12,000 registrations based on the trailing quarter"
- Misleading: "Next month will yield exactly 11,234 registrations"

**Hand off to a specialist** when the pattern is non-linear, multiple seasonal cycles overlap, external drivers (ad spend, holidays) matter, or when forecast precision drives resource decisions.

## Detecting and Handling Outliers

### Identification Techniques

**Z-score approach** (assumes approximate normality):
```python
z = (df['val'] - df['val'].mean()) / df['val'].std()
outliers = df[abs(z) > 3]  # beyond 3 standard deviations
```

**IQR fence approach** (works regardless of distribution shape):
```python
q1 = df['val'].quantile(0.25)
q3 = df['val'].quantile(0.75)
iqr = q3 - q1
lo = q1 - 1.5 * iqr
hi = q3 + 1.5 * iqr
outliers = df[(df['val'] < lo) | (df['val'] > hi)]
```

**Percentile cutoff approach** (most straightforward):
```python
outliers = df[(df['val'] < df['val'].quantile(0.01)) |
              (df['val'] > df['val'].quantile(0.99))]
```

### What to Do with Outliers

Never strip outliers automatically. Follow this decision process:

1. **Diagnose**: Is this a recording error, a legitimately extreme observation, or a sign of a separate population?
2. **Errors**: Correct or exclude (e.g., negative ages, epoch-zero timestamps)
3. **Legitimate extremes**: Retain but switch to robust summaries (median, IQR)
4. **Distinct populations**: Analyze separately (e.g., enterprise accounts vs. self-serve)

**Document every exclusion**: "We set aside 47 records (0.3% of the dataset) with order values above $50K; these bulk enterprise transactions are covered in a separate section."

### Detecting Anomalies in Time Series

1. Establish an expected baseline (rolling average or year-ago value)
2. Compute the residual: actual minus expected
3. Flag residuals exceeding 2-3 standard deviations of historical residuals
4. Differentiate one-off spikes (point anomalies) from lasting shifts (change points)

## Hypothesis Testing Essentials

### When It Applies

Use formal testing whenever you need to distinguish a real signal from random noise:

- Evaluating A/B experiment results
- Measuring the impact of a product change (before vs. after)
- Comparing metrics across customer segments

### Step-by-Step Process

1. **State the null (H0)**: No difference exists (default position)
2. **State the alternative (H1)**: A difference exists
3. **Set the significance threshold (alpha)**: 0.05 is standard (5% false-positive tolerance)
4. **Calculate the test statistic and p-value**
5. **Decide**: p < alpha means sufficient evidence to reject H0

### Selecting the Right Test

| Question | Appropriate Test | Conditions |
|---|---|---|
| Two group means differ? | Independent samples t-test | Roughly normal, two groups |
| Two conversion rates differ? | Proportions z-test | Binary outcomes |
| Same entities measured twice? | Paired t-test | Pre/post on identical subjects |
| Three or more group means? | ANOVA | Multiple variants or segments |
| Non-normal data, two groups? | Mann-Whitney U | Skewed or ordinal metrics |
| Two categorical variables related? | Chi-squared test | Frequency table data |

### Beyond p-values: Practical Impact

A statistically significant result only means the effect is unlikely due to chance. It does not guarantee the effect matters in practice. Always accompany test results with:

- **Effect magnitude**: "Variant B lifted conversion by 0.3 percentage points"
- **Confidence interval**: The plausible range of the true effect
- **Business translation**: Revenue, user, or efficiency implications

### Sample Size Awareness

- Small samples yield unreliable conclusions even when p-values look good
- Proportions require roughly 30 or more events per group for baseline reliability
- Detecting subtle effects (e.g., a 1-point conversion shift) can demand thousands of observations per arm
- When data is limited, say so: "With 200 observations per group, effects smaller than X% would likely go undetected"

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
- At alpha = 0.05, testing 20 metrics yields roughly one spurious hit by chance
- If you explored numerous segments before finding the "interesting" one, acknowledge that
- Apply Bonferroni correction (alpha / number of tests) or transparently report total tests conducted

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
- Prefer honest ranges: "Churn is likely between 4% and 6%"
- Round to the level of certainty you actually possess
