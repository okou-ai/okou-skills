---
name: people-search
description: Control people-search stopping conditions and review timing. Use for requests with a target number of people or open-ended requests to find more candidates.
---

# People Search Stopping Policy

Aim for broad coverage and accurate matches: avoid missing potential candidates,
and recommend only people verified to meet all requirements.

Prioritize explicit user limits and stopping instructions. Reuse the same task's
candidate pool, verified results, and round history.
Use `okou data tools` and `okou data describe <tool-name>` before calling tools.

## Numeric target

1. While below target, repeat **search → deduplicate → review → count qualified people**.
   Review newcomers and pending candidates with new evidence. Count only distinct
   people verified against every requirement; additional targets exclude prior results.
2. Stop short only at explicit user limits or reasonable exhaustion of useful alternatives
   and pending leads.

## Open-ended / more people

1. Repeat **search → deduplicate**. Between rounds, do only identity checks, not
   qualification research. Keep all candidates; do not verify qualifications yet.
2. From round two, compare this round's distinct identities with the cumulative
   seen set **before adding this round**, regardless of qualification:

   `duplicate_rate = this round's repeated people / this round's distinct total`

3. **MUST** record total/repeated/new counts; add all newcomers to the seen set and pool.
   **MUST** stop immediately if the **unrounded** `duplicate_rate > 0.80`.
   **Exactly 80% means continue.**
4. After stopping, **MUST** review the **entire unique pool**, including final-round newcomers.
   Do not restart discovery solely because few qualify.
