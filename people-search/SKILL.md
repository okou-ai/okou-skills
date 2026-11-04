---
name: people-search
description: Control people-search stopping conditions. Use for requests with a target number of people or open-ended requests to find more candidates.
---

# People Search Stopping Policy

Aim for broad coverage and accurate matches: avoid missing potential candidates,
and recommend only people verified to meet all requirements.

Prioritize explicit user limits and stopping instructions. Reuse the same task's
candidate pool, verified results, and search-call history.
Use `okou data tools` and `okou data describe <tool-name>` before calling tools.

## Numeric target

1. While below target, repeat **search → deduplicate → review → count qualified people**.
   Review newcomers and pending candidates with new evidence. Count only distinct
   people verified against every requirement; additional targets exclude prior results.
2. Stop short only at explicit user limits or reasonable exhaustion of useful alternatives
   and pending leads.

## Open-ended / more people

1. For each search call, deduplicate identities within its returned results first.
   Keep all candidates, regardless of qualification.
2. Starting with the second call, count how many of those unique identities already
   exist in the seen set from earlier calls. Compute the duplicate rate **before
   updating the seen set**:

   `duplicate_rate = repeated identities from earlier calls / this call's unique identities`

3. **MUST** record total/repeated/new counts; then add all newcomers to the seen set and pool.
   **MUST** stop immediately if the **unrounded** `duplicate_rate >= 0.80`.
   **Exactly 80% means stop.**
4. **MUST** ensure the **entire unique pool** is reviewed, including final-call newcomers.
   Do not restart discovery solely because few qualify.
