---
name: flux-analysis
description: Explain financial variances with driver analysis, period comparisons, waterfall bridges, and commentary.
---

## Decomposition Techniques

Use comparable periods, populations, units, and cost structures. A bridge allocates an arithmetic change; it does not by itself establish a business cause. State the order of substitutions, reconcile the components to the observed change, and keep unexplained amounts visible rather than naming them as a known driver.

### Price x Volume Separation

The foundational split for any metric expressible as unit price multiplied by quantity.

**Two-factor formulas:**
```
Total Movement = Actual Result - Baseline (budget or prior period)

Quantity Component  = (Actual Units - Baseline Units) x Baseline Unit Price
Pricing Component   = (Actual Unit Price - Baseline Unit Price) x Actual Units

Check: Quantity Component + Pricing Component = Total Movement
       (when the interaction term is absorbed into one of the two factors)
```

**Three-factor revenue bridge (quantity, mix, then price):**

Let Q0 and Q1 be total baseline and actual quantities, m0_i and m1_i each product's quantity share, and p0_i and p1_i its unit price. Each period's shares sum to 1.

```
Quantity = (Q1 - Q0) x Sum(m0_i x p0_i)
Mix      = Q1 x Sum((m1_i - m0_i) x p0_i)
Price    = Q1 x Sum(m1_i x (p1_i - p0_i))

Check: Quantity + Mix + Price = Actual Revenue - Baseline Revenue
```

This order allocates interactions to the later components; do not add another interaction term. Other orders can be valid but yield different component values. For one product changing from 100 units at $10 to 110 at $12, the bridge is +$100 quantity, $0 mix, +$220 price = +$320. Using baseline units for the price effect would omit $20.

Only pool quantities with comparable units. New or discontinued products need explicit counterpart prices to separate mix from price; a missing price is not zero. If a period has zero total quantity or counterpart prices cannot be justified, use a direct product-revenue bridge or disclose an unallocated new/discontinued-product component instead of forcing this decomposition.

For repeatable calculations, use the bundled [bridge calculator](scripts/decompose.py):

```bash
# SKILL_DIR is the absolute path to this flux-analysis skill directory.
python3 "$SKILL_DIR/scripts/decompose.py" --help
python3 "$SKILL_DIR/scripts/decompose.py" --mode revenue --input inputs.json
```

Input JSON has `baseline` and `actual` arrays with matching, unique `segment` IDs and numeric `quantity` and `price` fields. Prefer decimal strings. Quantities must be nonnegative, in common units, with positive totals in both periods. Supply prices explicitly even for zero-quantity segments. Output values are exact rational strings; round only for presentation. The calculator checks arithmetic, not source quality or whether this model fits the business.

**Worked example — top-line revenue:**
- Baseline plan: 10,000 units at $50/unit = $500,000
- Actual outcome: 11,000 units at $48/unit = $528,000
- Net movement: +$28,000 favorable
  - Quantity uplift: +1,000 units x $50 = +$50,000 (favorable — higher volume)
  - Pricing drag: -$2 x 11,000 = -$22,000 (unfavorable — reduced average selling price)

### Blended Rate / Composition Separation

Applicable when aggregated results blend multiple segments with distinct unit economics.

**Formulas:**
```
Blended Rate = Sum(w_i x r_i)  # weights sum to 1 in each period
Mix Effect  = Sum((w1_i - w0_i) x r0_i)
Rate Effect = Sum(w1_i x (r1_i - r0_i))

Check: Mix Effect + Rate Effect = Actual Blended Rate - Baseline Blended Rate
```

Use the denominator of the rate as the weight: revenue shares for gross margin percentages, not unit shares. These effects are rates, not currency amounts; multiply fractional rates by 100 to express percentage points. To explain gross-profit dollars, reconcile revenue and cost dollars separately. The calculator's `--mode weighted-rate` takes `segment`, `weight`, and `rate` fields; weights are nonnegative with positive period totals and are normalized internally.

**Worked example — gross margin compression:**
- Segment X earns 60% margin; Segment Y earns 40% margin
- Plan assumed a 50/50 revenue split -> blended 50% margin
- Actual revenue split was 40/60 -> blended 48% margin
- The 2-point margin decline is attributable to the shift toward the lower-margin segment

### People-Cost Decomposition

Purpose-built for analyzing compensation and headcount-driven expense lines.

```
For comparable spend = paid FTE-periods H x average cost per FTE-period C:

Staffing Effect  = (H1 - H0) x C0
Cost-Rate Effect = H1 x (C1 - C0)

Check: Staffing Effect + Cost-Rate Effect = Actual Spend - Planned Spend
```

Use paid time or period-average FTE, not closing headcount, when hires and departures occur during the period. Reconcile costs outside this model separately. Hiring, attrition, phasing, and workforce composition can explain these components if supported by payroll or roster data; they are not additional additive components unless a mutually exclusive bridge is defined. An unexplained residual does not prove a composition change.

### Functional Expense Decomposition

For operating cost categories where a price-times-volume model does not apply naturally.

```
Total OpEx Movement = Actual Operating Costs - Planned Operating Costs

Segment into:
1. Headcount-linked costs       (wages, benefits, payroll taxes, recruiting fees)
2. Activity-linked costs        (cloud hosting, payment processing fees, sales commissions, freight)
3. Discretionary programs       (travel, conferences, outside services, campaign spend)
4. Committed / fixed costs      (facility leases, insurance, enterprise software licenses)
5. Non-recurring charges        (severance, litigation, asset write-downs, project-specific outlays)
6. Timing / phasing differences (spend that shifted between periods relative to the plan)
```

## Significance Thresholds & Prioritization

### Calibrating Thresholds

Thresholds govern which movements warrant formal investigation and written explanation. Base them on:

1. **Approved materiality:** Use the task's or organization's threshold and its stated benchmark; financial-statement materiality is not a universal operating-variance rule
2. **Relative line-item scale:** Apply tighter percentage gates to larger balances
3. **Historical volatility:** Allow wider bands for inherently variable accounts to filter noise
4. **Decision relevance:** Would this size of movement influence a management decision or board discussion?

If no threshold is supplied, prioritize by absolute effect and decision consequence. Label any proposed dollar or percentage gates as assumptions and explain which decisions they would change; do not present generic percentages as company policy.

### Triage Order When Multiple Items Exceed Thresholds

1. **Greatest absolute dollar impact** — largest influence on the bottom line
2. **Greatest percentage deviation** — may signal a process breakdown or data error
3. **Counter-trend movements** — direction opposite to what history or forecasts predicted
4. **Newly emerged variances** — items previously on track that have just diverged
5. **Compounding variances** — gaps that have widened in each of the last several periods

## Writing Effective Variance Narratives

### Recommended Structure

```
[Line Item]: [Favorable / Unfavorable] movement of $[amount] ([X]%)
relative to [budget / prior period / forecast] for [reporting period]

Primary driver: [Brief label]
[Two to three sentences explaining the business cause, quantifying each
contributing factor where possible.]

Outlook: [One-time event / Likely to persist / Improving / Worsening]
Next step: [No action / Monitor / Deeper review / Adjust forecast]
```

### Quality Criteria

Strong narratives consistently satisfy these tests:

- **Precise:** Names concrete factors rather than restating the variance itself
- **Measured:** Attaches dollar or percentage weight to each cited driver
- **Explanatory:** Addresses why the movement occurred, not merely that it did
- **Prospective:** States whether the movement is expected to continue, reverse, or evolve
- **Directive:** Identifies any follow-up action or decision prompted by the finding
- **Compact:** Two to four sentences — not padded filler

### Pitfalls to Avoid

- Restating the outcome as its own cause ("Revenue rose because revenue was higher")
- Labeling a variance as "timing" without specifying what shifted and when normalization is expected
- Calling something "one-time" without describing the actual event
- Sweeping a material movement under "various small items" instead of decomposing further
- Explaining only the dominant driver while ignoring meaningful offsets
- Using vague qualifiers ("elevated," "slightly higher") without attached numbers

## Bridge / Waterfall Presentation

### Concept

A bridge (waterfall) chart traces the path from a starting value to an ending value through a sequence of additive and subtractive contributors. It is the visual companion to variance decomposition.

### Data Architecture

```
Starting point:   [Baseline figure — plan, prior period, or forecast]
Contributors:     [Ordered list of signed driver amounts]
Ending point:     [Actual figure]

Integrity check:  Starting point + Sum(all contributors) = Ending point
```

### Text-Format Bridge (When No Charting Tool Is Available)

```
BRIDGE: Operating Expenses — Q4 Actual vs. Q4 Plan

Q4 Planned OpEx                                       $8,000K
  |
  |--[+] Incremental headcount above plan              +$500K
  |--[+] Unplanned outside counsel fees                +$200K
  |--[-] Open-role savings (delayed hiring)            -$350K
  |--[-] Travel spend below budget                     -$180K
  |--[+] Cloud infrastructure overrun                  +$130K
  |--[-] Marketing program deferrals                   -$100K
  |
Q4 Actual OpEx                                        $8,200K

Net Movement: +$200K (+2.5% unfavorable)
```

### Companion Reconciliation Table

| Driver | Amount | Share of Total Movement | Running Total |
|---|---|---|---|
| Incremental headcount | +$500K | 250% | +$500K |
| Outside counsel | +$200K | 100% | +$700K |
| Open-role savings | -$350K | -175% | +$350K |
| Travel underspend | -$180K | -90% | +$170K |
| Cloud overrun | +$130K | 65% | +$300K |
| Marketing deferrals | -$100K | -50% | +$200K |
| **Net movement** | **+$200K** | **100%** | |

*Individual shares can exceed 100% when favorable and unfavorable drivers offset each other.*

### Presentation Guidelines

1. Sequence drivers from most favorable to most unfavorable (or in a logical business narrative order)
2. Group small items when it improves readability; retain material offsets and a traceable breakdown of any "All other" bucket
3. Verify arithmetic: opening value plus all drivers equals closing value
4. Use color to distinguish direction — green for favorable, red for unfavorable — in graphical renderings
5. Annotate each segment with both the dollar amount and a short label
6. Include a summary segment showing the net total movement

## Multi-Scenario Comparisons

### Three-Column Layout

| Line Item | Annual Plan | Latest Forecast | Actual | Plan Var ($) | Plan Var (%) | Forecast Var ($) | Forecast Var (%) |
|---|---|---|---|---|---|---|---|
| Revenue | $X | $X | $X | $X | X% | $X | X% |
| Direct costs | $X | $X | $X | $X | X% | $X | X% |
| Gross profit | $X | $X | $X | $X | X% | $X | X% |

### Choosing the Right Baseline

- **Actual vs. annual plan:** Governance and incentive evaluation; the plan is fixed at the start of the fiscal year
- **Actual vs. rolling forecast:** Operational steering and early-warning detection; the forecast is refreshed monthly or quarterly
- **Forecast vs. plan:** Gauges how management expectations have shifted since planning; highlights planning-accuracy gaps
- **Actual vs. prior period (sequential):** Reveals trend direction; especially useful for new ventures or post-acquisition integration where a plan may not yet exist
- **Actual vs. prior year (year-over-year):** Growth assessment adjusted for seasonality

### Tracking Forecast Precision

Measure forecast quality over time to tighten future planning:

```
Period Accuracy = 1 - |Actual - Forecast| / |Actual|

MAPE (Mean Absolute Percentage Error) = Mean of |Actual - Forecast| / |Actual| across all periods
```

These percentage measures are undefined when actual is zero and unstable near zero; `1 - error` can be negative and is not a probability. Choose an appropriate absolute or scaled error measure when needed, disclose zero treatment, and do not silently exclude difficult periods. Compare forecast versions at the same horizon using the same scoring population.

| Month | Forecast | Actual | Deviation | Accuracy |
|---|---|---|---|---|
| Jan | $X | $X | $X (X%) | XX% |
| Feb | $X | $X | $X (X%) | XX% |
| ... | ... | ... | ... | ... |
| **Full Year** | | | **MAPE** | **XX%** |

### Reading Variance Trends Across Time

- **Persistently favorable:** Plans may be overly conservative (potential sandbagging)
- **Persistently unfavorable:** Targets may be unrealistic or execution is lagging
- **Widening unfavorable gap:** Performance is deteriorating or external conditions are shifting
- **Narrowing gap:** Forecast accuracy is improving through the year (a healthy signal)
- **Erratic swings:** Business is inherently unpredictable or the forecasting methodology needs refinement
