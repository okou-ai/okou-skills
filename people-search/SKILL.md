---
name: people-search
description: Research professional people through multi-channel discovery, original-source checks, and deduplication. Use when sourcing experts, instructors, speakers, creators, or business contacts, or extending an existing people search.
---

# People Search

Follow discovery → source checks → deduplication → useful expansion.

## 1. Choose the starting point

For a new search, map relevant channels: professional profiles and datasets,
organization sites, event archives, publications, portfolios, or project pages.
For a follow-up, reuse existing people and sources; target missing channels
and unresolved questions. Record whether the user requests a total count,
an additional count, or open-ended discovery, and preserve exact versus
minimum-count wording.

## 2. Discover across channels

Continue discovering people across relevant channels.
Combine people/profile search, web search, and source rosters. Expand broad
roles and topics with related terms, platforms, and newly discovered names;
split over-constrained queries without changing the user's scope.

Use `okou data tools` to discover available tools and `okou data describe <tool-name>`
to read the current schema before calling.

## 3. Resolve important evidence gaps

Read attributable profiles, project materials, publications, or event records.
Keep URLs beside the facts they support; distinguish historical from current
information. Follow missing facts into other relevant sources rather than
inferring experience from titles or completed work from announcements.

Stop targeted checking once the gap is resolved or the evidence is clearly
unavailable after reasonable alternatives. Label remaining uncertainty and
avoid repeated searches merely for reassurance. Continue other discovery
where useful; completing one person's checks does not finish the whole search.

## 4. Merge verified findings

Resolve identities through profiles, affiliations, and work, not names alone.
Merge duplicate records while retaining useful sources. Keep a cumulative
seen-person set for the same search across tools and follow-ups, and separately
track people whose requested qualifications are verified. Retain sources,
open questions, and channels covered.

Treat one completed discovery search and its extracted people as a round;
exclude targeted verification, enrichment, failed searches, and pending calls.
Deduplicate each round's people, compare them with the previously seen set,
record total/repeated/new counts, then update that set. Count people, not source
URLs or provider result IDs. Resolve material identity ambiguities before using
them to trigger a stop.

Incorporate newly verified people and facts directly into the updated result,
including on follow-up, rather than merely saying they should be added.

## 5. Expand or close

Apply explicit user scope, time, budget, and stopping instructions first. Choose
the branch below; do not relax qualifications or count duplicates to fill a target.

**Numeric target:** Prioritize reaching the requested number of distinct,
verified people. For an additional-person target, count only people new to the
previous result. While below target, expand useful queries and channels even
when the duplicate rate reaches 60%; that threshold must not end this branch.
Stop short only when an explicit limit is reached or meaningful alternatives
and pending leads have been reasonably checked without enough supported people;
report the shortfall and evidence gaps. Once the target is met, stop for an exact
count; for a minimum count or an unnumbered request for further people, continue
with the open-ended branch rather than treating the minimum as a cap.

**Open-ended discovery or more people without a fixed count:** From the second
completed discovery round onward, calculate:

`duplicate_rate = people in this round already seen before it / distinct people in this round`

Stop expansion when `duplicate_rate >= 0.60`, including exactly 60%. For example,
stop if 6 of the round's 10 distinct people were already seen. Use all discovered
identities for this ratio, not only verified or recommended people; keep target
progress separate. Do not require another high-duplicate round or complete
channel coverage before applying this stopping rule.

For a zero-person round, do not divide by zero or invent a duplicate rate.
Check useful alternative queries, channels, and pending leads before concluding
that further meaningful discovery is unavailable. Never count a source failure
as an empty successful search or treat a bounded first page as proof of saturation.

Stopping expansion does not cancel necessary checks on already found people.
Explain the stopping reason, remaining uncertainty, and material uncovered
channels; do not claim universal completeness.

## 6. Deliver

Use the requested information and format. Attach sources to important claims,
make uncertainty clear, and preserve useful verified findings. Provide an
accessible file when needed for the complete result; do not invent missing
facts or contact information.
