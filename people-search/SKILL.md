---
name: people-search
description: Find and verify people through multiple search rounds. Use for requests with a target number of people, or requests to find as many as possible, build a complete list, find more candidates, or keep searching. Prevent stopping after the first useful batch.
---

# People Search

Find as many distinct, qualified people as the request and budget allow. A useful first batch is progress, not completion. Never relax the user's requirements to increase the count.

Apply this policy to exhaustive searches and numeric targets, not single-person lookups or requests for a few examples. Explicit user limits, cancellation, and stopping instructions take priority.

## Set up the search run

- Default discovery budget: **8 candidate-search calls**, including failed attempts. Profile lookups, verification, and tool discovery are not candidate-search calls. An explicit user search budget replaces this default.
- Before stopping for low yield, complete **at least 3 successful discovery rounds covering 3 meaningfully different search directions**. User limits can end the run earlier.
- A discovery round is one successful candidate-search call followed by deduplication and qualification review. Reading tool descriptions or checking profiles does not count as a discovery round.
- Choose three initial directions, such as role/title variants, different organizations, or relevant communities/sources. These can use the same tool. Cosmetic query rewrites are not different directions; all directions must preserve the user's hard requirements.
- Reuse the task's candidate pool, evidence, and previously delivered results. An explicit request to continue starts a new run with fresh run counters, but retains this pool for deduplication. Never silently restart a run to reset its budget, or reset an explicit task-wide budget.
- When using Okou data tools, run `okou data tools` and `okou data describe <tool-name>` before using an unfamiliar tool. Use only supported parameters; do not invent pagination or exclusion fields.

## Repeat: search → deduplicate → verify → record → decide

1. Search an unused direction or meaningfully extend a productive one. Use supported pagination when available. If a direction returns mostly repeats or irrelevant people, pivot rather than rerunning essentially the same query.
2. Deduplicate within the response and against the existing pool. Prefer canonical public profile URLs or stable person IDs; otherwise compare names, affiliations, and supporting evidence. Citation/result numbers are not cross-call person IDs. Do not merge people solely because their names match, or count one person again because their title changed.
3. Review newcomers and actionable pending candidates against every hard requirement. Classify each as qualified, rejected, or unresolved. Count only distinct, evidence-supported matches; a returned profile is not automatically a qualified person. For a request for additional people, exclude previously delivered matches.
4. Update the run record before deciding whether to finish:

   `successful_rounds | direction | new_qualified | total_qualified | empty_streak | search_calls / budget`

   - `new_qualified` counts people newly qualified in this round, not raw profiles, repeats, or already qualified people.
   - If `new_qualified > 0`, reset `empty_streak` to **0** and continue unless a completion condition below applies.
   - If a successful, fully reviewed round adds **0** qualified people, increment `empty_streak` and use a different direction next.
   - Errors, incomplete responses, and unresolved candidates are **unknown yield, not zero yield**: reset `empty_streak` to **0** and resolve the uncertainty or try another direction within budget.

## Completion gate

Finish only when one of these conditions applies:

- **Target met:** the explicit numeric target has been reached with distinct, verified people. This can happen before three rounds.
- **Low yield:** at least three successful rounds cover at least three different directions, and the last **two consecutive rounds** each add zero qualified people. Those two rounds must use different directions and have no actionable unresolved candidates. This is a practical stopping heuristic, not proof that everyone has been found.
- **Budget reached:** the discovery-call budget or an explicit user time/cost limit has been reached. Do not make another discovery call. Use the remaining permitted verification work to support the final results.
- **Blocked or cancelled:** the user stops the search, or a concrete access/tool failure prevents useful continuation. Explain the blocker; do not label a failed search as exhausted.

Otherwise, make the next search call. Do not substitute a final answer, a long progress report, or “Would you like me to keep searching?” for required continuation.

A high duplicate rate is a reason to **change direction**, never a standalone reason to finish the entire task. Finding a plausible-looking shortlist is not a completion condition.

## Final response

Return the verified, deduplicated people with supporting sources. Briefly state the qualified count, successful rounds, discovery calls, and actual stopping reason. If a numeric target was missed, state the shortfall. Disclose unresolved leads or verification limits without presenting them as qualified matches. Never describe a budget-limited or low-yield search as a complete census.
