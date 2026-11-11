---
name: research-synthesis
description: Synthesize user research into insights, personas, opportunities, themes, and prioritized actions.
---

This skill covers user/customer research such as interviews, usability observations, and surveys. Scientific literature reviews and study-level evidence synthesis require methods suited to those designs; do not route them into personas or interview coding by default.

Preserve source and participant IDs in working notes so claims and quotes can be traced. Separate direct observations, self-reports, analyst interpretations, and proposed actions. Report contradictory or missing evidence that could change a recommendation. Adapt the methods below to the actual question and available data rather than requiring every output type.

## Core Analytical Methods

### Thematic Coding

A systematic approach to extracting meaning from qualitative data:

1. **Immersion** — Read the full dataset end-to-end without annotating. Build an intuitive sense of the landscape before imposing structure.
2. **Open coding** — Walk through every data point, attaching descriptive labels. Over-code rather than under-code; collapsing is easier than retroactive splitting.
3. **Pattern grouping** — Cluster related codes into candidate themes. Each theme should represent a meaningful pattern relevant to your research questions.
4. **Validation pass** — Revisit the raw data to stress-test each theme. Confirm sufficient supporting evidence exists, themes do not overlap excessively, and together they form a coherent narrative.
5. **Sharpening** — Give each theme a precise name and a one-to-two sentence definition capturing its essence.
6. **Reporting** — Write up themes as findings, each backed by concrete evidence from the data.

### Bottom-Up Clustering (Affinity Approach)

A technique for letting structure emerge organically from observations:

1. **Atomize** — Record every discrete observation, quote, or data point as an individual unit
2. **Group by similarity** — Arrange units into clusters without predefined categories; let the data dictate the groupings
3. **Name each cluster** — Assign a label that captures the shared thread binding the items together
4. **Build hierarchy** — If natural super-groups appear across clusters, organize them into higher-level categories
5. **Read the map** — The cluster structure and inter-cluster relationships reveal your key themes

**Practical guidance:**
- Keep each unit to a single observation — do not bundle multiple insights together
- Rearrange freely; initial placements are provisional
- Oversized clusters typically contain multiple themes and should be subdivided
- Isolated observations that resist grouping are worth examining — outliers often carry signal
- The clustering process itself generates understanding, not just the final arrangement

### Cross-Validation Through Triangulation

Strengthen any finding by confirming it through independent lines of evidence:

- **Method triangulation**: Probe the same question via different techniques (e.g., interviews, surveys, and analytics)
- **Participant triangulation**: Examine the same question across different user segments or cohorts
- **Temporal triangulation**: Look for the same pattern at multiple points in time

Converging evidence can strengthen a finding when sources are relevant and sufficiently independent. Repeated quotes from the same participant, a survey and interview of the same people, or dashboards derived from one log are not independent replications. When sources diverge, investigate populations, timing, and measurement differences before resolving the disagreement.

## Working with Interview Data

### Extracting Signal from Individual Sessions

For every interview, pull out four categories of information:

**Observed behaviors and expressed attitudes**
- Separate what participants describe doing from what they feel or believe
- Record situational context: frequency, setting, collaborators involved
- Examine workarounds as possible signals of friction or adaptation, checking whether participants consider them a problem

**Illustrative quotations**
- Select quotes that are specific and vivid, not generic platitudes
- Use non-identifying participant IDs with relevant broad context; keep IDs traceable internally without exposing identifying combinations of details
- Remember: a quote is evidence supporting a finding, not a finding in itself

**Gaps between stated preferences and actual behavior**
- What people claim to want frequently diverges from what they actually do
- Observable behavior is stronger evidence than self-reported preference
- When a participant requests a feature but their workflow shows no use of analogous existing features, note the discrepancy

**Intensity signals**
- Emotional markers: frustration, enthusiasm, resignation
- Frequency of encounter: daily pain versus rare annoyance
- Effort invested in workarounds
- Downstream consequences when the problem occurs

### Patterns Across Multiple Sessions

After coding individual interviews:
- Count unique participants supporting each theme and give the eligible/answered denominator; quote counts are not participant counts. Distinguish an unasked question from an explicit negative response
- Segment by user type — different roles or contexts often yield different patterns
- Surface contradictions between participants; these frequently indicate meaningful audience segments
- Highlight anything that defied your initial expectations

## Interpreting Survey Data

### Quantitative Response Analysis

- **Sample quality**: Identify recruitment, target population, invitations/eligibility, response rate when known, item nonresponse, and weighting. Convenience or self-selected samples do not establish population prevalence merely because N is large
- **Look at distributions, not just means**: A bimodal spread (concentrated at extremes) tells a fundamentally different story than a bell curve, even if the averages match
- **Slice by segment**: Aggregate numbers can conceal critical differences between user groups
- **Respect sample size**: Small samples make minor numerical differences unreliable
- **Contextualize with benchmarks**: Compare against available, comparable sources using the same question, scale, recruitment, and population; respect closed-data tasks

### Free-Text Response Analysis
- Apply the same thematic coding process used for interview data
- Tally theme frequency across responses
- Extract representative quotes per theme
- Watch for themes that appear in open text but were absent from the structured questions — these reveal blind spots in your survey design

### Frequent Pitfalls in Survey Analysis
- Reporting means without showing distributions — identical averages can mask radically different response shapes
- Overlooking non-response bias — those who skipped the survey may differ systematically from those who completed it
- Calling a score fluctuation meaningful or dismissing it as noise without considering uncertainty, sampling, scale, and practical importance
- Assuming equal intervals on Likert scales — the psychological distance between "Strongly Agree" and "Agree" is not necessarily the same as between "Agree" and "Neutral"
- Drawing causal conclusions from cross-tabulated correlations

## Bridging Qualitative and Quantitative Evidence

### The Iterative Loop

- **Start qualitative**: Interviews and observation reveal experiences and possible explanations; self-reports alone do not establish a causal mechanism.
- **Quantify**: Surveys and analytics can measure prevalence/frequency within their sampling and tracking scope. Population estimates require an appropriate sampling or modeling basis.
- **Return to qualitative**: Dive back in to explain surprising quantitative results.

### Combining Evidence Effectively
- Use supported quantitative reach alongside severity and decision relevance; a rare critical failure can matter, and missing reach estimates do not make a qualitative finding unimportant
- Use qualitative data to propose explanations for quantitative anomalies, then check timing, alternative explanations, and any available behavioral evidence
- Present integrated evidence with its scope: "42% of the 100 respondents answering this item flagged X; interviews suggest Y as a possible explanation." Do not convert respondent percentages into all-user prevalence or a suggested explanation into a proven root cause

### When Data Sources Conflict
- Conflicting evidence across methods is a feature, not a flaw — it demands investigation
- Check whether the divergence stems from different populations being measured
- Consider whether self-reported preferences (survey) diverge from actual behavior (analytics)
- Verify whether the survey question truly captured the intended construct
- Report the conflict transparently and pursue follow-up rather than arbitrarily choosing one source

## Building Personas from Data

### From Behavioral Clusters to Profiles

Personas must be grounded in observed patterns, not assumptions:

1. **Detect behavioral clusters**: Identify groups of participants who share similar goals, behaviors, and contexts
2. **Isolate differentiating dimensions**: Determine what separates one cluster from another — usage intensity, company size, technical sophistication, primary job-to-be-done, etc.
3. **Draft persona profiles** for each cluster:
   - Descriptive label and summary
   - Characteristic behaviors and objectives
   - Core frustrations and unaddressed needs
   - Contextual details (role, organization type, adjacent tools)
   - Supporting quotes from research
4. **Check against quantitative data where suitable**: Estimate segment size only if the data identifies those behavioral clusters in the target population; demographic counts alone may not map to them

### Persona Profile Structure

Include only fields and quotations supported by the research; omit unsupported fields instead of filling the template with assumptions.

```
[Label] — [One-sentence characterization]

Background:
- Role, organization type and scale, experience level
- How they discovered and adopted the product

Objectives:
- Primary goals and jobs to be done
- How they define success

Product Relationship:
- Usage frequency and depth
- Key workflows and features relied upon
- Complementary tools in their stack

Frustrations:
- Decision-relevant unmet needs
- Workarounds they have built

Decision Drivers:
- What they prioritize in a solution
- What would push them to leave or upgrade

Voice of the User:
- Available, traceable verbatim quotes capturing this persona's perspective
```

### Persona Anti-Patterns
- **Demographic framing**: Defining personas by age, gender, or geography instead of behavior. Behavioral attributes predict product needs far more reliably.
- **Unsupported segmentation**: Let distinguishable, decision-relevant patterns determine whether personas are useful and how many are justified; do not fill a persona quota
- **Assumption-based personas**: Profiles invented without research data are fiction, not tools.
- **Stale personas**: Personas that are never revisited as the product and market shift lose their usefulness.
- **Decorative personas**: If a persona does not influence at least one product decision, it is not earning its keep.

## Sizing and Scoring Opportunities

### Estimating the Scale of Each Opportunity

For opportunities where sizing would change the decision, estimate what the evidence supports and leave unknowns explicit:

- **Affected population**: How many users face this problem? Ground the estimate in analytics, survey data, or market sizing.
- **Encounter frequency**: How often does the problem occur for each affected user? (Daily, weekly, monthly, one-time)
- **Impact when it occurs**: What is the severity — complete blocker, meaningful friction, or minor irritant?
- **Commercial signal**: Would solving this drive upgrades, reduce churn, or attract new customers?

### Scoring Framework

Rank opportunities along four dimensions:

- **Impact**: Consider affected users, frequency, and severity. Multiplication is useful only with defined units and meaningful scales; ordinal severity labels do not automatically support arithmetic
- **Evidence quality**: Assess recruitment, measurement, source independence, relevance, and contradictory evidence, rather than counting sources or assuming all behavioral data outranks self-report
- **Strategic fit** = Does this align with company direction and product vision?
- **Execution feasibility** = Can this realistically be built? Consider technical complexity, resource requirements, and time to value.

### Communicating Opportunity Estimates
- Make your assumptions visible — show the reasoning chain, not just the conclusion
- Give bounds only when supported by data or named scenario assumptions; a range does not make an unsupported population estimate valid
- Keep units and denominators separate: ticket counts are not unique affected users, and interview severity counts do not estimate population percentages without a suitable basis
- Rank opportunities relative to each other — comparative positioning is often more useful than absolute scores
