---
name: marketing-analytics
description: Analyze marketing performance, attribution, channel metrics, forecasts, A/B tests, and optimization opportunities.
---

## Channel Metric Reference

Use the source platform's definitions and the task's cost basis, reporting window, and cohort. State whether numerators count unique people, sessions, or repeat events; do not mix these silently. A zero denominator makes a ratio undefined, not zero. Compare to supplied targets or genuinely comparable benchmarks with a source and date; the tables below are definitions, not universal performance norms. Observed or attributed outcomes do not by themselves establish incremental impact.

### Email

| Metric | How It Is Calculated | Insight Provided |
|--------|---------------------|-----------------|
| Delivery rate | Delivered / Sent | Delivery and list hygiene |
| Open rate | Unique recorded opens / Delivered | Recorded opening activity; [privacy protections](https://www.apple.com/legal/privacy/data/en/mail-privacy-protection/) and automated opens limit interpretation |
| Click-through rate (CTR) | Unique clicking recipients / Delivered | Recorded response to content and CTA; check bot filtering |
| Click-to-open rate (CTOR) | Unique clicking recipients / Unique recorded openers | Clicks relative to recorded opens; inherits open-tracking limitations |
| Unsubscribe rate | Unsubscribes / Delivered | Audience-content fit and send frequency tolerance |
| Bounce rate | Bounces / Sent | List data quality |
| Recipient conversion rate | Unique converting recipients / Delivered | Full-funnel email response within a stated window |
| Revenue per send | Attributed revenue / Emails sent | Revenue credited per sent email |
| List growth rate | (Closing subscribers - Opening subscribers) / Opening subscribers | Net audience growth, including removals and reactivations |

### Social Platforms

| Metric | How It Is Calculated | Insight Provided |
|--------|---------------------|-----------------|
| Impressions | Times content appeared in feeds | Distribution breadth |
| Reach | Unique users who saw content | Audience coverage |
| Engagement rate | (Reactions + Comments + Shares) / Reach | Interactions per reached account; repeat events can exceed 100% |
| Click-through rate | Link clicks / Impressions | Ability to drive traffic |
| Follower growth rate | Net new followers / Opening followers | Audience expansion pace |
| Share/Repost rate | Shares / Reach | Virality and advocacy signal |
| Video view rate | Views / Impressions | Hook effectiveness for video |
| Video completion rate | Completed views / Total views | Content quality and length fit |
| Share of voice | Your mentions / Category total mentions | Competitive visibility |

### Paid Advertising (Search and Social)

| Metric | How It Is Calculated | Insight Provided |
|--------|---------------------|-----------------|
| Impressions | Times the ad appeared | Budget utilization and audience sizing |
| Click-through rate (CTR) | Clicks / Impressions | Creative and targeting relevance |
| Cost per click (CPC) | Spend / Clicks | Traffic generation efficiency |
| Cost per thousand impressions (CPM) | Spend per 1,000 impressions | Awareness cost efficiency |
| Conversion rate | Conversions / Clicks | Landing page and offer effectiveness |
| Cost per acquisition (CPA) | Spend / Conversions | Full-funnel cost efficiency |
| Return on ad spend (ROAS) | Attributed revenue / Ad spend | Revenue-to-media-spend ratio; not profit ROI or proof of incrementality |
| Quality Score (search) | Platform relevance rating (1-10) | Alignment of ad, keyword, and destination |
| Frequency | Average exposures per user | Ad fatigue risk indicator |
| View-through conversions | Conversions credited to an impression without a click under the platform's window/rules | Impression-based attribution, not demonstrated causal influence |

### Organic Search / SEO

| Metric | How It Is Calculated | Insight Provided |
|--------|---------------------|-----------------|
| Organic sessions | Visits originating from search engines | Overall SEO health |
| Keyword positions | Rank for target search terms | Search result visibility |
| Organic CTR | Clicks / Search impressions | Title and meta description appeal |
| Indexed pages | Pages present in the search index | Crawlability and site architecture |
| Domain authority | Third-party composite score | Aggregate site strength |
| Backlinks / referring domains | Count of links / distinct linking domains, respectively | Separate measures of inbound links |
| Page performance | The source's named loading/interactivity metric and unit | Compare the same measurement definition and environment |
| Organic conversion rate | Conversions / Organic sessions | Intent alignment and content quality |
| Top organic entry pages | Most-visited pages from search | Highest-performing SEO content |

### Content Performance

| Metric | How It Is Calculated | Insight Provided |
|--------|---------------------|-----------------|
| Pageviews | Total views across content pages | Content reach |
| Unique visitors | Distinct measured visitor IDs consuming content | Measured audience; identity resolution can split or merge people |
| Average time on page | Duration spent on content pages | Depth of engagement |
| Bounce rate | Source-defined bounced sessions / Sessions | Definitions vary by analytics product; do not mix legacy single-page and engagement-based definitions |
| Scroll depth | Percentage of page scrolled | Engagement persistence |
| Social shares | Times content was distributed socially | Audience advocacy |
| Backlinks generated | External links earned by content | SEO value and authority |
| Leads attributed | Leads traced to content interaction | Conversion power |
| Content revenue/cost ratio | Attributed revenue / Stated content cost | Revenue multiple, not profit ROI |
| Content profit ROI on content investment | (Revenue - Other included operating costs - Content investment) / Content investment | Profit return on the stated investment denominator; do not subtract the same cost twice |

### Pipeline and Revenue Metrics

| Metric | How It Is Calculated | Insight Provided |
|--------|---------------------|-----------------|
| Marketing qualified leads (MQLs) | Leads passing marketing qualification criteria | Top-of-funnel output |
| Sales qualified leads (SQLs) | MQLs accepted by the sales team | Lead quality |
| MQL-to-SQL conversion | SQLs / MQLs | Marketing-sales alignment |
| Pipeline created | Dollar value of new opportunities | Marketing revenue impact |
| Pipeline velocity | Speed of deal progression | Campaign urgency and quality signal |
| Customer acquisition cost (CAC) | Total marketing + sales spend / New customers | Acquisition efficiency |
| CAC payback period | CAC / Monthly gross profit (or explicitly defined contribution) per acquired customer | Simplified payback at a stable positive monthly contribution; revenue-only payback must be labeled separately |
| Marketing-sourced revenue | Revenue from marketing-originated deals | Direct marketing contribution |
| Marketing-influenced revenue | Revenue from deals with any marketing touchpoint | Broader marketing footprint |

Profit ROI requires costs, not just revenue and ad spend. If those costs are unavailable, report the revenue/cost ratio and the missing inputs instead of relabeling it as ROI. For example, $1,000 revenue / $200 content spend = 5x revenue/spend; with $600 other included costs, profit ROI on content spend is ($1,000 - $600 - $200) / $200 = 100%. State which costs are included and avoid counting them twice. See [Google Ads' ROI definition](https://support.google.com/google-ads/answer/1722066?hl=en).

For stable subscription revenue, monthly gross profit can be approximated as monthly revenue per customer times gross margin. If contribution varies or customers churn, use cumulative cohort contribution to estimate payback; a nonpositive contribution provides no finite payback under the constant-rate model. Do not invent margins. See [Stripe's CAC payback calculation](https://stripe.com/resources/more/what-is-the-cac-payback-period). Align CAC's acquisition cohort and cost allocation with the customers used for payback. Marketing-sourced and influenced revenue can overlap; do not add them as separate incremental revenue.

## Report Structures

### Weekly Snapshot
Designed for rapid team consumption:
- **Three headline metrics** with week-over-week movement
- **Wins**: 1-2 data-backed highlights
- **Watch items**: 1-2 areas requiring attention with supporting numbers
- **Upcoming actions**: 3-5 priorities for the week ahead

### Monthly Performance Review
Standard format for stakeholder reporting:
1. Executive summary (3-5 sentences)
2. Core metrics table with month-over-month and target comparisons
3. Channel-level performance breakdown
4. Campaign results and highlights
5. What succeeded and what underperformed, with working hypotheses
6. Recommendations and priorities for the coming month
7. Budget spent vs. planned

### Quarterly Strategic Review
For leadership-level analysis:
1. Quarter results against stated goals
2. Year-to-date progress and trajectory
3. Channel-by-channel ROI assessment
4. Campaign portfolio performance summary
5. Competitive and market landscape observations
6. Strategic recommendations for the next quarter
7. Budget proposal and reallocation plan
8. Experiment outcomes and key learnings

### Dashboard Construction Principles
- Feature the metrics that tie directly to business goals, not vanity numbers
- Display trends over multiple periods rather than isolated data points
- Provide comparison anchors: prior period, target, industry benchmark
- Apply uniform color signaling: green for on-track, yellow for at-risk, red for off-track
- Organize by funnel stage or the business question being answered
- Confine the dashboard to a single screen; relegate granular data to an appendix
- Match the refresh cadence to the decision cadence (real-time for paid media, weekly for content)

## Trend Analysis and Projection

### Spotting Patterns
When examining performance data, investigate:

1. **Sustained direction**: is the metric consistently rising, falling, or flat across 4+ consecutive periods?
2. **Turning points**: at what moment did the trajectory change, and what event coincided?
3. **Cyclical patterns**: are there recurring fluctuations by day of week, month, or quarter?
4. **Outliers**: isolated spikes or dips — what triggered them, and could the cause be replicated or avoided?
5. **Predictive signals**: which metrics shift first and foreshadow downstream outcomes?

### Analytical Process
1. Plot the available history at a cadence relevant to the decision; sample count alone does not establish statistical relevance or cover seasonal cycles
2. Characterize the overall trajectory (rising, declining, stable, or oscillating)
3. Quantify the rate of change — is the trend accelerating or flattening?
4. Layer in external events (campaign launches, product updates, market shifts)
5. Compare with supplied targets or sourced, comparable benchmarks
6. Look for correlations with related metrics
7. Formulate causal hypotheses and design experiments to test them

### Projection Techniques
- **Trend extension**: project the existing trajectory forward (works best for stable metrics)
- **Rolling average**: average the most recent 3-6 periods to dampen noise
- **Year-over-year overlay**: use the prior year's seasonal pattern, adjusted for a growth coefficient
- **Funnel arithmetic**: forecast outputs from inputs (X leads at Y% conversion rate yields Z customers)
- **Scenario planning**: model optimistic, expected, and pessimistic cases

### Projection Guardrails
- State the horizon, history, assumptions, and validation error when available; no fixed observation count or horizon guarantees reliability
- External disruptions (market shifts, competitive moves, economic changes) can invalidate trend-based models
- Provide supported conditional estimates. Distinguish model-based prediction intervals from scenarios that vary named assumptions; when data cannot support bounds, describe uncertainty without inventing a range

## Attribution Fundamentals

### Why Attribution Matters
Buyers rarely convert after a single interaction. Attribution assigns credit across the multiple touchpoints that precede a conversion, informing channel investment decisions.

### Standard Attribution Models

| Model | Mechanism | Strength | Weakness |
|-------|----------|----------|----------|
| Last interaction | All credit to the final touchpoint | Identifies closing channels | Overlooks awareness and nurture |
| First interaction | All credit to the initial touchpoint | Highlights discovery channels | Ignores conversion drivers |
| Even distribution | Equal credit across all touchpoints | Acknowledges every channel | Fails to reflect relative influence |
| Recency-weighted | Increasing credit as touchpoints approach conversion | Balances awareness and closing | Can undervalue early awareness |
| Position-based | Chosen weights for first, middle, and last touches | Makes a credit policy explicit | Weights are assumptions, not measured influence |
| Algorithmic | Model-estimated credit from observed paths | Can model patterns beyond a fixed rule | Depends on model assumptions, coverage, and selection; not automatically causal |

### Practical Attribution Advice
- Use an attribution rule only when the available tracking supports it; otherwise report observable paths or an unattributed share
- Contrast feasible credit policies to show how investment conclusions depend on the rule
- State lookback windows, eligible touches, deduplication, identity coverage, and how conversion credit is conserved
- Credit allocation is descriptive. Estimating incremental channel effects requires an appropriate experiment or credible causal design with stated assumptions
- More complex attribution is not necessarily more informative; incomplete tracking can make precise-looking allocations misleading

### Attribution Traps
- Optimizing a single channel based on single-touch data can starve the rest of the funnel
- A credit rule can systematically favor touches near its chosen position; check this in the observed paths rather than assuming a universal channel ordering
- Self-reported attribution ("How did you hear about us?") offers useful qualitative signal but is unreliable for quantitative allocation
- Assess cross-device and cross-channel tracking gaps and unobserved paths; do not imply complete coverage without evidence

## Optimization Methodology

### Systematic Improvement Process
1. **Detect**: which metrics fall short of targets or benchmarks?
2. **Locate**: where in the funnel does the breakdown occur? (impressions, clicks, conversions, retention)
3. **Theorize**: what is causing the shortfall? (targeting, messaging, creative, offer design, timing, technical issues)
4. **Rank**: which interventions promise the greatest impact relative to effort?
5. **Experiment**: run a controlled test to validate or disprove the hypothesis
6. **Evaluate**: did the metric improve meaningfully?
7. **Act**: scale successful changes broadly; iterate on inconclusive or negative results

### Intervention Levers by Funnel Position

| Funnel Position | Warning Sign | Available Levers |
|----------------|-------------|-----------------|
| Awareness | Low impressions, limited reach | Budget levels, targeting parameters, channel mix, ad format |
| Interest | Low CTR, weak engagement | Creative execution, headline copy, content hooks, audience refinement |
| Consideration | High bounce rate, low dwell time | Page content, load speed, relevance alignment, user experience |
| Conversion | Low conversion rate | Offer structure, CTA wording, form complexity, trust elements, page layout |
| Retention | Elevated churn, declining re-engagement | Onboarding flow, email sequences, product experience, support quality |

### Impact-Effort Prioritization

Score every optimization idea on two axes:

**Impact** (potential metric movement):
- High: directly addresses the primary bottleneck
- Medium: improves a contributing factor
- Low: yields incremental gains

**Effort** (implementation difficulty):
- Low: copy tweak, targeting adjustment, quick A/B test
- Medium: new creative asset, page redesign, workflow modification
- High: new tooling, cross-team initiative, major content production

Execution order:
1. High impact, low effort — prioritize, subject to evidence, constraints, and authorization
2. High impact, high effort — plan and staff
3. Low impact, low effort — pursue if bandwidth allows
4. Low impact, high effort — defer or deprioritize

### Experimentation Discipline
- Use a single-change comparison or a planned factorial design that can identify the effects and interactions of interest
- Lock in the success metric before the test begins
- Plan sample size, randomization unit, run duration, and stopping rule for the baseline rate/variance and meaningful effect. Account for business cycles, repeated users, and delayed conversions; one week is not a universal sufficient duration
- Record all experiments and outcomes, including negative and null results
- Communicate negative and inconclusive results without calling non-significance proof that variants are equivalent; share only when requested or authorized

### Example Optimization Rhythm

Adapt this cadence to spend velocity, conversion delays, staff capacity, and the test's stopping rule; avoid repeatedly reallocating on noise or interrupting planned experiments.
- **Daily**: check paid campaign pacing, flag anomalies, review ad approval status
- **Weekly**: assess channel-level performance, pause lagging efforts, amplify winners
- **Biweekly**: rotate ad creative and launch new test variants
- **Monthly**: conduct a comprehensive performance review, surface new optimization opportunities, refresh projections
- **Quarterly**: reassess channel strategy, budget distribution, and audience targeting at a strategic level
