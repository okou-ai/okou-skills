---
name: people-search
description: Find professional people through multi-channel discovery, identity deduplication, and goal-dependent review. Use when sourcing experts, instructors, speakers, creators, business contacts, or more candidates.
---

# People Search

## 1. Plan

Record qualifications, total/additional targets, and exact/minimum wording.
Honor explicit user scope, time, budget, and stopping instructions first.
Reuse the same search's existing people, sources, reviews, and round notes.
Vary queries across professional profiles, organization sites, events,
publications, and project pages; do not repeat queries just to trigger a stop.
Use `okou data tools` and `okou data describe <tool-name>` before calling tools.

## 2. Track people and rounds

Keep cumulative seen identities separate from verified qualifying people.
Resolve identity through profiles, affiliations, and work—not names alone.
Count people, not URLs or provider IDs; never guess identity matches.

Count each completed discovery search as a round; exclude verification,
enrichment, failed searches, and pending calls. Deduplicate each round, compare
against the **prior** seen set, and record total/repeated/new counts. Retain
sources and all new people—including those in the stop-triggering round—then
update the seen set.

## 3. Numeric target: search and review in rounds

**Search → deduplicate → review → count qualified people → repeat if below target.**

Count only distinct, verified people meeting the qualifications; additional-person
targets exclude previous results. Review new candidates and pending candidates
with new evidence before searching again. Skip discovery if already at target.

Do not stop below target because of duplication or relax qualifications to fill
it. Stop short only at user limits or reasonable exhaustion of useful alternatives
and pending leads. Once met, stop discovery; if the user also asks for unnumbered
further people, switch to Section 4. Honor exact/minimum delivery wording and
retain already-verified extras for minimum-count requests.

## 4. Open-ended / more people: collect, then review

**Search → deduplicate → repeat until duplicates exceed 60% → review the full pool.**

Between discovery rounds, do only identity checks and source retention—not
person-by-person qualification research. Keep unverified or possibly unsuitable
candidates in the pool.

From the second completed discovery round, calculate the unrounded ratio using
all candidate identities, not only qualifying people:

`duplicate_rate = this round's distinct people already seen / this round's distinct people`

Stop immediately when `duplicate_rate > 0.60`; **exactly 60% means continue**.
Then review every unique pooled candidate, including the final round's newcomers,
not just a shortlist. Do not restart discovery solely because few qualify.
For an empty successful round, leave the ratio undefined; try useful alternatives
or close on reasonable exhaustion. Do not confuse source failure with empty results
or treat a bounded first page as proof of saturation.

## 5. Review and deliver

At the chosen review point, read original sources to verify qualifications;
retain evidence URLs and distinguish historical from current facts. Follow
important gaps until resolved or clearly unavailable after reasonable alternatives.
Label uncertainty; do not equate titles with experience or announcements with
completed work.
Perform contact enrichment only when explicitly requested, at review time.

Recommend supported people only; never pad counts or invent facts or contacts.
Update the complete result in the requested format, preserving useful verified
findings. Honor explicit limits and disclose the stopping reason, target shortfall,
unreviewed candidates, uncertainty, and material uncovered channels. Do not claim
universal completeness. Provide an accessible file when needed for the full result.
