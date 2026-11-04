---
name: people-search
description: Control people-search stopping conditions and review timing. Use for requests with a target number of people or open-ended requests to find more candidates.
---

# People Search Stopping Policy

Prioritize explicit user limits and stopping instructions. Reuse the same task's
candidate pool, verified results, and round history.
Use `okou data tools` and `okou data describe <tool-name>` before calling tools.

## Numeric target

Use this mode for total or additional targets, including minimum-count requests.

1. While below target, repeat **search → deduplicate → review → count qualified people**.
   Review newcomers and pending candidates with new evidence. Count only distinct
   people verified against every requirement; additional targets exclude prior results.
2. Do not stop below target because of duplication or relax requirements. Stop short
   only at explicit user limits or reasonable exhaustion of useful alternatives and pending leads.
3. At target, skip/stop numeric discovery. Deliver exactly N for exact-count requests;
   retain verified extras for minimum-count requests. Switch to open-ended discovery
   only if further unnumbered expansion was also requested.

## Open-ended / more people

Use this mode for open-ended requests or separately requested unnumbered expansion.

1. Repeat **search → deduplicate**. Between rounds, do only identity checks, not
   qualification research. Keep all candidates, including unverified or unsuitable people.
2. From round two, compare this round's distinct identities with the cumulative
   seen set **before adding this round**, regardless of qualification:

   `duplicate_rate = this round's repeated people / this round's distinct total`

3. Record total/repeated/new counts; add all newcomers to the seen set and pool.
   Stop immediately if the **unrounded** `duplicate_rate > 0.80`.
   **Exactly 80% means continue.**
4. After stopping, review the **entire unique pool**, including final-round newcomers.
   Do not restart discovery solely because few qualify.

## Counting and closure

- Count distinct people, not names, URLs, or provider IDs. Keep seen identities
  separate from verified qualifying people.
- Treat each completed discovery search as one round; exclude verification,
  enrichment, failed searches, and pending calls.
- For an empty successful round, leave the ratio undefined; try useful alternatives
  or stop on reasonable exhaustion. Source failure or a bounded first page alone
  does not establish exhaustion.
- Report the stopping reason, qualified count, shortfall, and incomplete review.
  Do not count unverified people as qualified or claim exhaustive coverage.
