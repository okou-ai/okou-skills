---
name: people-search
description: Find professional people through multi-channel discovery, identity deduplication, and goal-dependent review. Use when sourcing experts, instructors, speakers, creators, business contacts, or more candidates.
---

# People Search

## 1. Prepare

Record hard requirements vs preferences, total/additional and exact/minimum targets;
prioritize explicit limits and stopping instructions. Reuse this search's people,
evidence, reviews, and round history.
Use `okou data tools` and `okou data describe <tool-name>` before calling tools.

## 2. Run a discovery round

1. Vary queries across profiles, organization sites, events, publications, and
   projects; never repeat queries merely to trigger a stop.
2. Extract all identifiable people and source URLs, not just provider summaries.
   Resolve identities through profiles/affiliations/work; never guess matches or
   count names, URLs, or provider IDs as people.
3. Deduplicate within the round; log total/repeated/new people against the
   **prior** seen set, then add all newcomers. Keep seen and verified-qualified
   people separate.

Treat each completed discovery search as one round; exclude verification,
enrichment, failed searches, and pending calls.

## 3. Follow the matching loop

### Numeric target: review each round

Repeat **discover → review → count** only while below target:
- Review newcomers and pending candidates with new evidence; count only distinct
  people verified against every requirement. Additional targets exclude prior results.
- Continue despite high duplication; never relax requirements. Stop short only at
  explicit limits or reasonable exhaustion of useful alternatives and pending leads.

At target, skip/stop numeric discovery. Deliver exactly N for exact-count requests;
retain verified extras for minimum-count requests. Switch to open-ended discovery
only if further unnumbered expansion was also requested.

### Open-ended / more people: collect first

Repeat discovery; between rounds, do only identity checks, not qualification
research. Keep all candidates, including unverified or possibly unsuitable people.
From round two, use **unrounded**, all-candidate round counts:

`duplicate_rate = this round's repeated people / this round's distinct total`

Stop immediately at `duplicate_rate > 0.80`; **exactly 80% means continue**.
For empty rounds, leave the ratio undefined; try useful alternatives or stop on
reasonable exhaustion. Never treat failed sources as empty results or a bounded
first page as proof of saturation.

Then review the **entire unique pool**, including final-round newcomers.
Do not restart discovery solely because few qualify.

## 4. Review and deliver

- Verify every requirement from original sources; resolve material gaps or mark
  unavailable only after reasonable alternatives. Label uncertainty and separate
  current/historical facts; do not infer experience from titles or completed work
  from announcements.
- Enrich contacts only when explicitly requested, at review time.
- Rank verified matches by preferences, never use preferences as eligibility gates;
  separate unverified leads. Deliver complete results with evidence URLs and reasons
  in the requested format; provide an accessible file if needed.
- Report stop reason, shortfall, unreviewed people, uncertainty, and uncovered
  channels. Never pad counts, invent facts/contacts, or claim exhaustive coverage.
