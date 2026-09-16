---
name: customer-intel
description: Research customer context across docs, tickets, CRM, email, and web sources with cited confidence.
---

## Investigation Framework

### Phase 1 — Define the Inquiry

Before touching any source, characterize what you need to find:

- **Definitive fact**: A single correct answer exists (e.g., "Does the API support batch requests?")
- **Contextual picture**: Multiple viewpoints must be assembled (e.g., "What has this account's experience been over the last quarter?")
- **Open exploration**: The boundaries of the question are still forming (e.g., "Why are enterprise customers struggling with onboarding?")
- **Audience awareness**: Determine who will consume the answer — the customer directly, an internal team member, or executive leadership — as this shapes tone, depth, and what to include.

### Phase 2 — Map Sources to the Question Type

| Question Category | Primary Sources |
|---|---|
| Product capabilities | Official docs, API references, knowledge base, product specs |
| Account history and context | CRM records, email threads, meeting notes, chat logs |
| Internal process or policy | Wikis, runbooks, policy documents |
| Technical troubleshooting | Documentation, engineering resources, past support tickets |
| Market or competitive landscape | Web search, analyst reports, competitive intelligence |

### Phase 3 — Gather Evidence Across Tiers

Work through sources from most to least authoritative. Never rely on a single hit — corroborate across channels.

**Tier 1: Canonical Internal Records** (Reliability: Strong)
Official documentation, published knowledge base articles, API references, policy and SLA documents, internal product roadmaps. Trust these unless they carry stale dates.

**Tier 2: Organizational Memory** (Reliability: Moderate-Strong)
CRM account notes and activity logs, resolved support tickets and known-issue databases, shared documents and specifications, recorded decisions from meeting notes.

**Tier 3: Informal Team Channels** (Reliability: Moderate)
Slack or chat discussions, email correspondence, calendar and agenda notes. These often hold the freshest information but may lack full context or reflect speculation.

**Tier 4: Public and External Sources** (Reliability: Variable)
Company and competitor websites, community forums and user discussions, partner documentation, industry news and analyst commentary.

**Tier 5: Reasoning by Analogy** (Reliability: Weak)
Precedent from similar past situations, patterns from comparable accounts, general industry conventions. Always label these as inference.

### Phase 4 — Assemble the Answer

Pull together findings, flag any contradictions between sources, and assign an overall confidence rating.

### Phase 5 — Attribute Everything

Every claim in your response must trace back to a named source. No unsourced assertions.

## Confidence Rating System

Attach one of these ratings to every answer you deliver:

### Strong Confidence
- Backed by canonical documentation or an authoritative internal record
- Corroborated by at least two independent sources
- Verified as current
- Phrasing: "This is well-supported by [source]."

### Moderate Confidence
- Found in informal channels (chat, email) without official documentation backing
- Rests on a single uncorroborated source
- Possibly dated but likely still accurate
- Phrasing: "According to [source], this seems correct. I would suggest confirming with [team/person]."

### Weak Confidence
- Derived from indirect or analogical reasoning
- Sources are old or of uncertain reliability
- Multiple sources conflict with one another
- Phrasing: "No definitive source was found. Based on [context], my working assessment is [answer]. Verification is recommended before communicating to the customer."

### Insufficient Information
- No relevant material located anywhere
- The question demands expertise beyond what available sources cover
- Phrasing: "I was unable to locate relevant information. I recommend consulting [suggested expert or team]."

## Resolving Source Conflicts

When different sources tell different stories:

1. Surface the discrepancy explicitly — never silently pick one version
2. Evaluate recency and authority of each conflicting source
3. Lay out both positions with context for the reader
4. Propose a path to resolution (e.g., check with the product team)
5. For customer-facing answers, default to the most conservative position until the conflict is settled

## Structured Response Format

```
**Answer:** [Lead with the bottom line]

**Confidence:** [Strong / Moderate / Weak]

**Evidence:**
- [Source A]: [What it states]
- [Source B]: [Corroborating or contrasting detail]

**Limitations:**
- [Conditions or edge cases that could change the answer]
- [Context-specific factors to be aware of]

**Next Steps:**
- [Whether this is safe to relay to the customer as-is]
- [Any recommended verification actions]
```

## Deciding When to Escalate

### Safe to Answer Directly
- Official docs address the question unambiguously
- Multiple trustworthy sources agree
- The topic is factual and non-sensitive
- No commitments about timelines, pricing, or legal terms are involved

### Route to a Specialist
- Roadmap commitments or delivery timelines are in play
- The question touches pricing, contracts, or legal terms
- Security, compliance, or data-handling topics
- The response could set a binding precedent or create expectations
- Conflicting information was found and remains unresolved
- A customer-specific configuration is involved
- The account is at risk and an incorrect answer could worsen the situation

### Escalation Directory
1. **Domain experts** — technical or specialized knowledge gaps
2. **Product team** — capability, roadmap, or feature questions
3. **Legal / compliance** — regulatory, privacy, or contractual matters
4. **Finance / billing** — pricing, invoicing, payment issues
5. **Engineering** — bugs, custom setups, root-cause analysis
6. **Leadership** — strategic decisions, policy exceptions, high-stakes situations

## Capturing Research for Reuse

### Worth Documenting When:
- The same question has surfaced before or is likely to recur
- The investigation required substantial effort
- The answer corrects a widespread misconception
- Nuance exists that is easy to get wrong

### Reusable Entry Format
```

## [Topic or Question]

**Verified On:** [date]
**Confidence:** [rating]

### Finding
[Concise, direct answer]

### Context and Nuance
[Background, conditions, and subtleties]

### Source Trail
[Where this information originated]

### Adjacent Topics
[Related questions this entry may also answer]

### Freshness Notes
[When to re-check, what developments could invalidate this]
```

### Maintaining the Knowledge Store
- Timestamp every entry
- Mark entries tied to specific product versions or feature states
- Schedule periodic reviews to retire stale content
- Tag entries by domain, product area, and customer segment for discoverability

## Operating Principles

1. Pin down exactly what you are looking for before searching
2. Work through source tiers methodically — do not skip levels on assumption
3. Corroborate across multiple channels whenever possible
4. Never present uncertain findings as established fact — always surface your confidence level
5. When unsure whether an answer is safe to share externally, verify first
6. Record your findings so the next person does not repeat the work
7. If your research uncovers a knowledge gap, flag it for documentation
