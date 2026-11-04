---
name: people-search
description: Find, verify, and rank people through repeated candidate-search API calls. Use for requests with a target number of people, or requests to find as many as possible, build a complete list, find more candidates, or keep searching. Preserve all verified matches instead of silently returning a shortlist.
---

# People Search

Find as many distinct, qualified people as the request and budget allow. A useful first batch is progress, not completion. Never relax the user's requirements to increase the count.

Apply this policy to exhaustive searches and numeric targets, not single-person lookups or requests for a few examples. Explicit user limits, cancellation, and stopping instructions take priority.

## Core principles

- **Broad discovery:** Expand coverage through a deliberate search strategy, not indiscriminate searching.
- **Strict verification:** Qualify only people who satisfy the user's stated conditions.
- **Complete accounting:** Account for every discovered candidate so none are silently discarded.

## Set up the search run

- Count one candidate-search API request initiated by Okou, such as one `people_search` request, as **one discovery API call**. Provider-internal queries, search directions, steps, and results never count as additional discovery API calls.
- Default discovery budget: **8 discovery API calls**, including failed attempts. Profile lookups, verification, and tool discovery are not discovery API calls. An explicit user search budget replaces this default.
- Before stopping for low yield, complete **at least 3 successful discovery API calls with 3 meaningfully different request focuses**. User limits can end the run earlier.
- Evaluate each API call after deduplication and qualification review of its entire returned candidate batch. Do not increment successful-call or zero-yield counters for individual internal queries or directions.
- Choose distinct focuses for the initial API requests, such as role/title variants, different organizations, or relevant communities/sources. These requests can use the same tool. Cosmetic query rewrites are not different request focuses; broader discovery must not relax the criteria used to qualify a person.
- Reuse the task's candidate pool, evidence, and previously delivered results. An explicit request to continue starts a new run with fresh run counters, but retains this pool for deduplication. Never silently restart a run to reset its budget, or reset an explicit task-wide budget.
- When using Okou data tools, run `okou data tools` and `okou data describe <tool-name>` before using an unfamiliar tool. Use only supported parameters; do not invent pagination or exclusion fields.

## Repeat: API call → deduplicate → verify → record → decide

1. Make a discovery API call with an unused request focus or meaningfully extend a productive one. Use supported pagination when available. If a call returns mostly repeats or irrelevant people, pivot rather than resubmitting essentially the same query.
2. Deduplicate across the API call's entire returned candidate batch and against the existing pool. Prefer canonical public profile URLs or stable person IDs; otherwise compare names, affiliations, and supporting evidence. Citation/result numbers are not cross-call person IDs. Do not merge people solely because their names match, or count one person again because their title changed.
3. Review newcomers and actionable pending candidates against every hard requirement. Classify each as qualified, rejected, or unresolved, and retain their evidence and rejection or uncertainty reasons in the pool. Count only distinct, evidence-supported matches; a returned profile is not automatically a qualified person. For a request for additional people, exclude previously delivered matches from the new results, not from the pool.
4. Update the run record after each discovery API call, before deciding whether to finish:

   `successful_api_calls | request_focus | new_qualified | total_candidates | total_qualified | empty_call_streak | discovery_api_calls / budget`

   - `new_qualified` counts people newly qualified after this API call, not raw profiles, repeats, or already qualified people.
   - If `new_qualified > 0`, reset `empty_call_streak` to **0** and continue unless a completion condition below applies.
   - If a successful, fully reviewed API call adds **0** qualified people, increment `empty_call_streak` and use a different request focus for the next API call.
   - Errors, incomplete responses, and unresolved candidates are **unknown yield, not zero yield**: reset `empty_call_streak` to **0** and resolve the uncertainty or try another request focus within budget.

## Completion gate

Finish only when one of these conditions applies:

- **Target met:** the explicit numeric target has been reached with distinct, verified people. This can happen before three successful discovery API calls.
- **Low yield:** at least three successful discovery API calls cover at least three different request focuses, and the last **two consecutive discovery API calls** each add zero qualified people. Those two calls must use different request focuses and have no actionable unresolved candidates. This is a practical stopping heuristic, not proof that everyone has been found.
- **Budget reached:** the discovery API call budget or an explicit user time/cost limit has been reached. Do not make another discovery API call. Use the remaining permitted verification work to support the final results.
- **Blocked or cancelled:** the user stops the search, or a concrete access/tool failure prevents useful continuation. Explain the blocker; do not label a failed search as exhausted.

Otherwise, make the next discovery API call. Do not substitute a final answer, a long progress report, or “Would you like me to keep searching?” for required continuation.

A high duplicate rate is a reason to **change the next API request's focus**, never a standalone reason to finish the entire task. Finding a plausible-looking shortlist is not a completion condition.

## Final response

- By default, return **every verified, deduplicated match for the current request**, with supporting sources, **sorted by descending relevance to the user's criteria and preferences**. Ranking determines order, not inclusion: do not silently return only the top 5, top 10, or a representative sample. Without an explicit user result limit, the returned count must equal the verified-match count for this request.
- Limit the presented results only when the user explicitly requests a result limit; state how many additional verified matches are not shown and retain them in the pool. If the full list is too long for an inline response, provide it as a complete deliverable and clearly label any inline shortlist as a preview.
- Report the distinct candidate total, qualified/rejected/unresolved counts, number returned, successful discovery API calls, total discovery API attempts, and actual stopping reason. State any numeric-target shortfall. Keep unresolved people separate from verified matches, and never describe a budget-limited or low-yield search as a complete census.
