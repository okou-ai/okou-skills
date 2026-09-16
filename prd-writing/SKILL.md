---
name: prd-writing
description: Draft PRDs with problem framing, users, requirements, acceptance criteria, scope, and measurable outcomes.
---

## Document Architecture

Organize every PRD around these core sections. Adapt the depth of each section to the complexity of the initiative.

### The Problem Frame

Ground the entire document in a clearly articulated problem:

- Identify the specific user pain point in concrete, observable terms
- Quantify who suffers from this problem and at what frequency
- Articulate the consequences of inaction: lost revenue, user attrition, operational burden, or competitive exposure
- Anchor claims in evidence drawn from support tickets, user interviews, behavioral data, or market signals

### Desired Outcomes

Translate the problem into 3-5 measurable targets:

- Frame each outcome around observable change: behavior shifts, efficiency gains, error reduction
- Separate user-facing outcomes (what improves for the customer) from organizational outcomes (what the business gains)
- Express outcomes as results rather than deliverables: "cut onboarding duration by half" instead of "redesign the onboarding flow"
- Every outcome must answer: "what evidence will confirm we achieved this?"

### Boundaries and Exclusions

Prevent runaway scope by documenting 3-5 items that are deliberately excluded:

- Name adjacent capabilities that will not be addressed in this iteration
- Provide a brief rationale for each exclusion: insufficient data, low leverage, better suited to a follow-up phase, or separate workstream
- Explicit exclusions protect the team during implementation and set honest expectations with stakeholders

### User Narratives

Capture user needs using the pattern: "As a [specific persona], I need [capability] because [underlying motivation]"

Guidance for effective narratives:

- Personas should be specific enough to guide design tradeoffs ("billing administrator" rather than "user")
- Describe the desired outcome, not interface mechanics
- The motivation clause must explain what value the user gains
- Account for error scenarios, empty states, and edge conditions
- Represent every distinct persona the feature touches
- Sequence narratives from highest to lowest priority

Sample narratives:
- "As a billing administrator, I need to export invoice history by date range because our finance team requires quarterly reconciliation reports"
- "As a new team member, I need to see a summary of recent project activity because joining mid-project without context slows my contribution"

### Characteristics of Strong User Narratives

Apply the INVEST checklist:

- **Independent**: Deliverable without coupling to other narratives
- **Negotiable**: Implementation details remain flexible
- **Valuable**: Produces a tangible benefit for the end user
- **Estimable**: Engineering can gauge the approximate effort
- **Small**: Completable within a single iteration
- **Testable**: Verification criteria are unambiguous

### Pitfalls to Avoid in User Narratives

- Vagueness: "As a user, I want better performance" -- specify which operation and what threshold
- Dictating implementation: "As a user, I want a modal dialog" -- describe the need, not the widget
- Missing motivation: "As a user, I want to click save" -- explain the purpose behind the action
- Oversized scope: "As a user, I want full team management" -- decompose into discrete capabilities
- Internal framing: "As the backend team, we want to migrate the database" -- this is a technical task, not a user narrative

## Requirement Tiers

### Tier Classification

**Critical (P0)**: The initiative is incomplete without these. They represent the minimum threshold for solving the stated problem. Litmus test: "If we remove this, does the core problem remain unsolved?" If yes, it stays at P0.

**Important (P1)**: Materially enhances the experience but the fundamental use case functions without them. These are strong candidates for rapid follow-up after initial release.

**Deferred (P2)**: Intentionally excluded from the first version, but the architecture should accommodate them. Recording these prevents design choices that create future obstacles.

### Prioritization Discipline

- Guard P0 ruthlessly. A lean critical set accelerates learning and delivery.
- When every item is labeled critical, no item is truly critical. Challenge each P0: "Would we genuinely delay release for this?"
- P1 items should represent near-certain follow-ups, not speculative wishes.
- P2 items serve as architectural guardrails, shaping design without consuming implementation effort.

### The MoSCoW Lens

An alternative classification that maps naturally to stakeholder negotiations:

- **Must have**: Without these, the release has no value. Non-negotiable.
- **Should have**: Expected by users and important, but the release remains viable without them.
- **Could have**: Welcome additions if capacity permits. Omitting them does not delay the timeline.
- **Won't have (this cycle)**: Explicitly deferred. Documenting these eliminates ambiguity.

## Measuring Success

### Early Signals (Days to Weeks Post-Launch)

Indicators that shift quickly and reveal immediate reception:

- **Uptake rate**: proportion of eligible users who engage with the new capability
- **Activation rate**: proportion who complete the primary intended action
- **Completion rate**: proportion who accomplish their end-to-end goal
- **Duration**: elapsed time for the core workflow
- **Failure rate**: frequency of errors, dead ends, or abandoned attempts
- **Return frequency**: how often users revisit the capability

### Sustained Signals (Weeks to Months Post-Launch)

Indicators that mature over time and reflect lasting impact:

- **Retention lift**: measurable improvement in user retention attributable to the feature
- **Revenue contribution**: driven upgrades, expansions, or new bookings
- **Satisfaction shift**: movement in NPS, CSAT, or qualitative sentiment
- **Support load reduction**: decrease in related support inquiries
- **Win-rate influence**: improvement in competitive deal outcomes

### Establishing Targets

- Targets must be precise: "60% uptake within the first 14 days" rather than "strong adoption"
- Derive targets from analogous launches, industry norms, or stated hypotheses
- Define both a baseline expectation and a stretch aspiration
- Specify the measurement instrument: which tool, which query, which time window
- Schedule evaluation checkpoints: one week, one month, one quarter after launch

## Verification Criteria

Express acceptance criteria using structured conditions or checklists.

**Structured Conditions**:
- Given [starting state or precondition]
- When [user action]
- Then [expected system behavior]

Example:
- Given the organization has enabled single sign-on
- When an employee navigates to the login screen
- Then the system redirects them to the organization's identity provider

**Checklist Approach**:
- [ ] Administrators can configure the identity provider URL in workspace settings
- [ ] Team members see a branded sign-on option on the login screen
- [ ] First-time SSO authentication provisions a new account automatically
- [ ] SSO authentication links to an existing account when the email matches
- [ ] Authentication failures surface a descriptive error message

### Writing Effective Verification Criteria

- Cover the primary path, error conditions, and boundary scenarios
- Describe observable behavior, not internal implementation
- Include negative cases: what should explicitly not occur
- Each criterion should be independently verifiable
- Replace subjective language ("responsive", "intuitive", "seamless") with concrete thresholds

## Scope Governance

### Indicators of Scope Expansion

Watch for these warning signs:

- Requirements surface after the specification is finalized
- Incremental additions compound into a substantially larger effort
- The team builds capabilities that no user requested ("since we are already in there...")
- Target dates shift without a deliberate re-scoping conversation
- Stakeholders append requirements without corresponding removals

### Containment Strategies

- Anchor every specification with explicit exclusions
- Enforce a tradeoff rule: new scope additions require a corresponding removal or timeline adjustment
- Maintain a clear boundary between the current iteration and subsequent phases
- Periodically verify that every requirement traces back to the stated problem
- Apply time caps to exploratory work: "if we cannot resolve X within two days, we defer it"
- Maintain a "future ideas" backlog for worthy suggestions that fall outside the current scope

## Unresolved Questions

Every PRD should track open items:

- Record questions that require resolution before or during implementation
- Assign each question to a responsible party: engineering, design, legal, data science, or a specific stakeholder
- Classify questions as blocking (must resolve before work begins) or non-blocking (can resolve in parallel with implementation)

## Timing and Sequencing

- Document hard deadlines: contractual obligations, external events, regulatory milestones
- Identify cross-team dependencies and their expected delivery dates
- Recommend phasing if the initiative exceeds a single release cycle
