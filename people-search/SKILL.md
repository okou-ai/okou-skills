---
name: people-search
description: Find, verify, and rank people using broad API discovery, evidence reuse, and parallel gap-only checks. Use for people-search requests, especially numeric targets, complete lists, additional candidates, or finding as many as possible. Preserve all verified matches and separate inferred or unverified leads.
---

# People Search

Find as many distinct, qualified people as the request and budget allow. A useful first batch is progress, not completion. Never relax the user's requirements to increase the count.

Apply evidence reuse and qualification rules to all people searches. Apply discovery budgets and completion gates to exhaustive searches and numeric targets, not single-person lookups or requests for a few examples. Explicit user limits, cancellation, and stopping instructions take priority.

## Core principles

- **Broad discovery:** Cover complementary candidate pools with targeted searches, adjusting the strategy as gaps emerge.
- **Strict qualification, minimal rechecking:** Require evidence for every hard requirement, but do not confuse verification with making another API call.
- **Low-latency execution:** Batch judgments on returned evidence, parallelize independent gap checks, and show confirmed results without waiting for the whole pool.
- **Complete accounting:** Keep every candidate's outcome explicit and preserve the full qualified set through ranking and delivery.

## API selection

Choose by evidence need, using only enabled tools and their current schemas. This is not a mandatory all-tools pipeline.

| Evidence need | API | Best use |
| --- | --- | --- |
| Natural-language professional brief | `people_search_semantic` | Discover professional profile pages and source text by meaning. |
| Exact current title, employer, profile-country or skill filters | `people_search_structured` | Expand a structured candidate pool; current-role filters must not become extra requirements for past-experience searches. |
| Complementary profile discovery or identity lookup | `people_search` | Find source-backed professional profiles by identity, role, employer, education, skill or location. |
| Cases, interviews, projects or other experience evidence | `web_search` | Find qualification evidence beyond profile records. |
| Read known public source pages | `web_contents` or `web_scrape` | Read source text to verify claims; reuse sufficient text already returned. |

For submitted jobs, use `company_contact_get` for people searches and `web_contents_get` for `web_contents`. These reads are not new discovery calls; each explicit structured-search next-page request is.

## Evidence-first qualification

1. Separate **hard requirements** from ranking preferences; preserve current versus past experience, dates, and geography. Never trade a missing hard requirement for a high overall match score.
2. Maintain a compact evidence record per person and assessed requirement: `person_id | requirement | status | supporting_fact_or_text | source_url | source_date_if_available`. Use `supported`, `inferred`, `missing`, `stale`, `conflicting`, or `contradicted`. Do not invent source dates or treat retrieval time as proof of freshness.
3. Reuse source-linked structured facts or source text already returned when identity, specificity, and temporal relevance are sufficient. **No extra page fetch or independent second source is required solely to reconfirm sufficient evidence**, unless the user requires it. Retrieval scores, match badges, query wording, and unsupported AI summaries are not qualification evidence.
4. Apply clear yes/no checks across the batch first. Reject a person as soon as sufficient, temporally relevant evidence clearly contradicts a hard requirement; treat stale or conflicting evidence as unresolved. Do not research a rejected person's remaining requirements. Missing information is unresolved, not a rejection. Use semantic judgment for nuanced requirements without silently promoting inference to fact.
5. Queue external research **only for material gaps**: unsupported hard requirements, identity ambiguity, conflicting facts, or time-sensitive facts whose freshness is insufficient. Ask a targeted question about the missing requirement; use a profile lookup, relevant case/interview, or original source rather than repeating the whole brief for every person. Search another relevant source when one page lacks evidence; absence on one page is not proof of absence.
6. Stop each gap check once it is supported, contradicted, clearly unavailable from relevant sources, or an applicable time/cost limit is reached. Do not keep searching for reassurance. Keep unresolved cases outside the verified count.

Classify each distinct person:

| Outcome | Admission rule | Presentation |
| --- | --- | --- |
| **Qualified** | Every hard requirement has sufficient supporting evidence; no material identity, freshness, or source conflict remains. | Evidence-supported match, with sources. |
| **Unresolved — inferred fit** | All other hard requirements are supported; the remaining requirements are only inferred. | Possible fit; state the inference and missing proof. Never count as verified. |
| **Unresolved — pending verification** | Material evidence is missing, stale, ambiguous, or conflicting. | Pending verification; name the gap. Never count as verified. |
| **Rejected** | Sufficient, temporally relevant evidence clearly contradicts at least one hard requirement. | Retain the exclusion reason in the pool. |

Use pending verification when missing, stale, ambiguous, or conflicting facts coexist with an inference. Infer preferences when useful for ranking, but label the inference. Keep both unresolved subtypes in the unresolved total; do not count them as additional people.

## Efficient execution

- Prefer supported response options that return task-relevant fields and source text alongside profiles, instead of discovering bare profile links and fetching each biography separately. Do not invent response options.
- Evaluate multiple candidates against the same requirement set in one batch; retain a separate evidence-backed decision for each person. Batch processing must not blur identities or transfer one person's evidence to another.
- For numeric targets, prioritize plausible matches and cheap, decisive gap checks in small verification waves sized to the remaining target, rather than deep-researching the entire pool at once. This schedules work; it is not an unstated shortlist limit for open-ended requests.
- Group independent lookups and known-page reads using supported batch inputs or parallel tool calls. Use bounded concurrency within provider/tool limits; do not invent batch endpoints or unsupported parameters. Avoid a serial search-fetch-evaluate loop per person.
- Share the deduplicated pool and evidence record across workers. Have one coordinator merge evidence and update global outcomes/counters; have workers return evidence keyed to person IDs instead of independently incrementing totals. Coalesce equivalent in-flight checks by canonical person/requirement or reusable source request: attach dependents to the existing work instead of dispatching it twice, and withdraw queued checks made unnecessary by new evidence.
- Reuse fetched URLs and shared facts, such as an employer's industry, only where they actually apply; separately establish each person's relationship and relevant dates. Merge by identity, source relevance, and dates, not arrival order. Do not fetch the same evidence repeatedly.
- Reuse evidence across discovery calls and explicit continuations. Re-evaluate changed requirements against saved facts instead of reusing an old qualification verdict; refresh only facts whose age, relevance, or contradictions make rechecking necessary.
- Pipeline discovery and gap checks when independent and within budget. Reserve a discovery-call slot before dispatch, including parallel attempts, and attribute candidates and outcomes to their originating calls. Pause new discovery as soon as the target or another completion condition is met; settle or cancel in-flight work safely. Triage already-returned candidates and retain all verified matches, even if that exceeds the target. Recompute current-request qualification and the completion gate after triage; resume within budget if the target no longer holds and no other gate applies. Never exceed the budget through parallel dispatch.

## Set up the search run

- Count one candidate-search API request initiated by Okou, such as one `people_search` request, as **one discovery API call**. Provider-internal queries, search directions, steps, and results never count as additional discovery API calls.
- Default discovery budget: **8 discovery API calls**, including failed attempts. Profile lookups, verification, and tool discovery are not discovery API calls. An explicit user search budget replaces this default.
- Before stopping for low yield, complete **at least 3 successful discovery API calls with 3 meaningfully different request focuses**. User limits can end the run earlier.
- Count a successful discovery call once a complete usable candidate response, including a valid empty batch, is available. Accepted/running jobs remain pending; failed or incomplete jobs do not satisfy the three-success minimum. Count once per API call, not per internal query, direction, or result read. Finalize its yield only after its entire returned batch has outcomes and no gap checks for that batch remain in flight. A partial review cannot establish zero yield.
- Choose distinct focuses for the initial API requests, such as role/title variants, different organizations, or relevant communities/sources. These requests can use the same tool. Cosmetic query rewrites are not different request focuses; broader discovery must not relax the criteria used to qualify a person.
- Reuse the task's candidate pool, evidence, and previously delivered results. An explicit request to continue starts a new run with fresh run counters, but retains this pool for deduplication. Never silently restart a run to reset its budget, or reset an explicit task-wide budget.
- Track pool-wide qualified IDs separately from **current-request qualified IDs**. For additional-people requests, exclude previously delivered IDs from the current-request set, not the pool. Use the current-request set for the target, shortfall, and returned-match count. Do not fabricate discovery-call yield for matches supported only by carried-in evidence or standalone lookups.
- When using Okou data tools, run `okou data tools` and `okou data describe <tool-name>` before using an unfamiliar tool. Use only supported parameters; do not invent pagination or exclusion fields.

## Repeat: discover → deduplicate → assess evidence → fill gaps → record → decide

1. Make a discovery API call with an unused request focus or meaningfully extend a productive one. Use supported pagination when available. If a call returns mostly repeats or irrelevant people, pivot rather than resubmitting essentially the same query.
2. Deduplicate across the API call's entire returned candidate batch and against the existing pool. Prefer canonical public profile URLs or stable person IDs; otherwise compare names, affiliations, and supporting evidence. Citation/result numbers are not cross-call person IDs. Do not merge people solely because their names match, or count one person again because their title changed.
3. Batch-assess newcomers and actionable pending candidates using **Evidence-first qualification**. Record qualified, rejected, or unresolved outcomes immediately from existing evidence, then supplement only the remaining material gaps. Count each person once, including when later evidence resolves a pending case. For additional-people requests, exclude previously delivered matches from the new results, not from the pool.
4. Update the run record as discovery responses and gap checks settle, before deciding whether to finish:

   `call_id | successful_api_calls | request_focus | review_status | new_qualified | total_candidates | pool_qualified | request_qualified | total_unresolved | empty_call_streak | discovery_api_calls / budget`

   - Keep `review_status` pending while a batch is partly reviewed or its gap checks are in flight. Show already-qualified people without waiting for that status to settle.
   - Assign `new_qualified` credit only to newly supported matches eligible for the current request, using evidence provenance in **dispatch order**, never response order. For joint support, credit the earliest dispatch-order call prefix whose accumulated evidence establishes every hard requirement; associate gap-check evidence with its originating discovery call and treat carried-in evidence as available before this run. A later duplicate supplying missing proof can earn the person's first credit; an already-qualified duplicate cannot. Retain first-discovery provenance separately, keep each current match credited at most once, and recompute/remove/transfer credit after late evidence, identity merges, or retractions.
   - Calculate the streak in **dispatch order**, not response order. If a call adds qualified people, reset `empty_call_streak` to **0**; if a successful, fully reviewed call adds **0** and has no unresolved cases, increment it and change the next request focus.
   - Errors, incomplete responses, unresolved cases, and in-flight reviews are **unknown yield, not zero yield** and break the streak. Recompute affected call yields and the streak when later evidence changes an outcome; never stop on stale counters.

## Completion gate

Finish only when one of these conditions applies:

- **Target met:** the explicit numeric target has been reached with distinct, verified people eligible for the current request, after triaging already-returned candidates. Previously delivered matches do not satisfy a request for additional people. This can happen before three successful discovery API calls.
- **Low yield:** at least three successful discovery API calls cover at least three different request focuses, and the last **two consecutive discovery API calls** in dispatch order each add zero qualified people. Both calls must be fully reviewed, use different request focuses, and have no unresolved cases; no discovery or verification work may remain in flight. This is a practical stopping heuristic, not proof that everyone has been found.
- **Budget reached:** the discovery API call budget or an explicit user time/cost limit has been reached. Do not make another discovery API call. Use the remaining permitted verification work to support the final results.
- **Blocked or cancelled:** the user stops the search, or a concrete access/tool failure prevents useful continuation. Explain the blocker; do not label a failed search as exhausted.

Otherwise, make the next discovery API call. Do not substitute a final answer, a long progress report, or “Would you like me to keep searching?” for required continuation.

A high duplicate rate is a reason to **change the next API request's focus**, never a standalone reason to finish the entire task. Finding a plausible-looking shortlist is not a completion condition.

## Progressive delivery

- Share a concise first batch of evidence-supported matches as soon as useful results are ready, with sources and a brief statement of what is still being checked. Continue required discovery and verification in the same run; this progress update is not a final answer or permission to stop.
- Keep **evidence-supported**, **inferred possible fit**, and **pending verification** visibly separate. An inferred or pending lead is never a verified recommendation; do not delay confirmed results until every uncertain lead is resolved. Explicitly correct previously shown outcomes if later evidence changes them.
- Do not claim background work will continue after a final response without an explicitly authorized execution mechanism. Finish through the completion gate and reconcile the complete deduplicated list, not just the last batch.

## Decision checks

- Full source-linked API evidence supports all hard requirements → qualify without redundant searches or page reads.
- A relevant title suggests ownership but does not explicitly establish it → inferred fit; check the ownership gap, not the entire biography.
- An old role record cannot establish a required current employer → pending verification; refresh that fact only.
- One requirement is contradicted → reject early; do not research the remaining requirements.
- Duplicate profiles or out-of-order parallel responses → merge evidence, count the person once, and keep pending or unresolved calls out of zero-yield streaks. If calls 1 and 2 jointly supply the proof, credit call 2 regardless of response order.
- A retained pool of 20 previously delivered matches plus a request for five more → require five additional verified people; the old 20 do not meet the new target.

## Final response

- By default, return **every verified, deduplicated match for the current request**, with supporting sources, **sorted by descending relevance to the user's criteria and preferences**. Ranking determines order, not inclusion: do not silently return only the top 5, top 10, or a representative sample. Without an explicit user result limit, the returned count must equal the verified-match count for this request.
- Limit the presented results only when the user explicitly requests a result limit; state how many additional verified matches are not shown and retain them in the pool. If the full list is too long for an inline response, provide it as a complete deliverable and clearly label any inline shortlist as a preview.
- Report the distinct candidate total, qualified/rejected/unresolved counts, number of verified matches returned, successful discovery API calls, total discovery API attempts, and actual stopping reason. State any numeric-target shortfall. Keep inferred and pending leads in separately labeled sections outside the verified count; never describe a budget-limited or low-yield search as a complete census.
