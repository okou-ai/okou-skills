---
name: people-search
description: Research professional people through multi-channel discovery, identity deduplication, and goal-dependent review order. Use when sourcing experts, instructors, speakers, creators, or business contacts, or extending an existing people search.
---

# People Search

Choose the execution order from the user's goal:

- **Numeric target:** search → deduplicate → review → count qualified people → repeat until the target is met.
- **Open-ended / more people:** search → deduplicate → repeat until the duplicate rate exceeds 60% → review the entire candidate pool.

## 1. Set the goal and search plan

Record the requested qualifications, total or additional-person target, exact
versus minimum wording, and any explicit scope, time, budget, or stopping limits.
Honor explicit user limits before the default rules below. If the user combines
a numeric target with an unnumbered request for more, meet the target first,
then switch to open-ended discovery.

Map relevant channels: professional profiles and datasets, organization sites,
event archives, publications, portfolios, or project pages. Combine people search,
web search, and source rosters; vary useful queries and channels rather than
repeating the same query merely to trigger a stopping condition.

For follow-ups, reuse the same search's existing people, sources, review outcomes,
and round notes. Use `okou data tools` to discover available tools and
`okou data describe <tool-name>` to read the current schema before calling.

## 2. Maintain the candidate pool and round counts

Keep a cumulative seen-person set for the same search across tools and follow-ups.
Track verified qualifying people separately from all discovered candidates.
Preserve identity clues, source links or result references, open questions,
and channels covered, including for people whose qualifications are not yet known.

Resolve identities through profiles, affiliations, and work, not names alone.
Merge repeated identities while retaining useful sources; count people, not
webpage URLs, profile rows, or provider result IDs. During discovery-only work,
look up only the identity ambiguity needed for reliable deduplication, not the
person's full background or qualifications. Do not guess a duplicate match to
force a stopping decision.

Treat one completed discovery search and its extracted people as one round.
Exclude targeted verification, enrichment, failed searches, and pending calls.
Deduplicate the round, compare its people with the seen-person set as it stood
before that round, and record distinct total/repeated/new counts. Retain every
new person, including new people from a stop-triggering round, then update the
seen-person set.

## 3. Numeric target: search and review in rounds

Check existing verified progress first; if the applicable target is already met,
skip to Step 4 without a new discovery search.

1. Search for candidates, then deduplicate and retain that round's people.
2. Review the round's new candidates and revisit pending candidates with materially
   new evidence using Section 5 before the next discovery round. Update the count
   of distinct, verified people meeting the requested qualifications. Do not count
   unverified, unsuitable, or duplicate people.
   For an additional-person target, count only people new to the previous result.
3. If the count is below target, search useful new directions and review again.
   Do not stop an unmet numeric target because the duplicate rate exceeds 60%,
   and do not relax qualifications to fill the count. Stop short only at an
   explicit limit or after useful alternatives and pending leads have been
   reasonably checked without enough qualifying people; report the shortfall.
4. Stop discovery once the target is met. If the user also explicitly asks for
   further people without a fixed count, switch to Section 4 with the existing
   pool and seen-person set. Preserve exact versus minimum wording in delivery;
   do not silently drop extra verified people from a minimum-count result.

## 4. Open-ended / more people: collect first, review afterward

1. Search and pool candidate people even when their qualifications are not yet
   established. Perform only identity deduplication and source retention between
   discovery rounds; defer person-by-person qualification research until
   discovery ends.
2. From the second completed discovery round onward, calculate the unrounded ratio:

   `duplicate_rate = distinct people in this round seen before it / distinct people in this round`

   Use all discovered identities, not just verified or recommended people.
   Apply the duplicate-rate stop only when `duplicate_rate > 0.60`: exactly 60%
   means continue; 7 previously seen people out of 10 means stop. Do not require
   another high-duplicate round or full channel coverage before applying this rule.
3. For a successful zero-person round, leave the ratio undefined rather than
   dividing by zero. Try useful alternative queries or channels; close only when
   meaningful alternatives are reasonably exhausted or an explicit limit is
   reached. Do not treat a failed source or bounded first page as proof of saturation.
4. After discovery stops, review **every unique person in the pooled results**
   using Section 5, including people from the final round and people who may
   prove unsuitable. Do not review only an initial shortlist or claim unreviewed
   people were checked. Do not restart discovery solely because few candidates
   qualify after review; explain the outcome and gaps.

## 5. Review candidates at the chosen mode's review point

Run this section after each discovery round in numeric-target mode, or only
after discovery ends in open-ended mode. Perform contact enrichment only when
explicitly requested, and only at this mode's review point.

Read attributable profiles, project materials, publications, or event records.
Keep URLs beside the facts they support and distinguish historical from current
information.

Follow important evidence gaps into other relevant sources rather than inferring
experience from titles or completed work from announcements. Stop targeted checks
when the gap is resolved or the evidence is clearly unavailable after reasonable
alternatives. Label remaining uncertainty; do not keep searching for reassurance.
Keep these verification searches separate from discovery-round duplicate counts.

Record the review outcome for each candidate and recommend only people supported
against the user's qualifications. If a resource limit prevents full review,
mark the unfinished candidates and incomplete review explicitly; never pad the
qualified count or invent facts or contact information.

## 6. Deliver

Incorporate newly verified people and facts directly into the complete updated
result, including on follow-up, rather than saying they should be added. Use
the requested information and format; retain useful verified findings and attach
sources to important claims. Explain the stopping reason, any target shortfall,
review completeness, uncertainty, and material uncovered channels. Do not claim
universal completeness. Provide an accessible file when needed for the full result.
