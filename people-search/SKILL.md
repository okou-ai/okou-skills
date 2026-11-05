---
name: people-search
description: Find, verify, and rank people using professional profiles and public sources. Use for people-search requests, including numeric targets, additional candidates, or finding as many as possible. Reuse sufficient evidence, research material gaps, and keep inferred leads separate from verified matches.
---

# People Search

Find people who meet the user's requirements, with evidence that supports the recommendation. Adapt the search depth and approach to the request.

## Core principles

- **Broad discovery:** Cover complementary candidate pools with targeted searches, adjusting the strategy as gaps emerge.
- **Strict verification:** Count or present a candidate as a match only after verifying they meet the user's criteria.
- **Complete accounting:** Keep every candidate's outcome explicit and preserve the full qualified set through ranking and delivery.

## Understand the request and choose tools

Choose tools by evidence need rather than running every available tool:

| Need | Useful tools |
| --- | --- |
| Natural-language professional brief | `people_search_semantic` |
| Exact title, employer, profile-country, or skill filters | `people_search_structured` |
| Complementary profile discovery or identity lookup | `people_search` |
| Cases, interviews, projects, or other experience evidence | `web_search` |
| Additional text from known public pages | `web_contents` or `web_scrape` |

Use enabled tools and their current schemas.

## Reuse evidence before researching further

- Start with the source-linked facts and text already returned. When they sufficiently support a requirement for the right person and timeframe, use them directly.
- Focus follow-up research on material gaps: missing proof, ambiguous identity, conflicting sources, or insufficient freshness. Search for the specific missing fact rather than researching the whole biography again. If one page lacks evidence, consider another relevant source.
- Stop checking a fact once it is sufficiently supported, clearly contradicted, or the necessary evidence is unavailable from relevant sources. Avoid repeated searches merely for reassurance; keep remaining uncertainty explicit.
- Exclude clear mismatches early. Treat missing, stale, or conflicting evidence as unresolved rather than proof that someone is ineligible.

For example, reuse a source that explicitly describes someone leading a team's first implementation. A relevant job title alone may suggest that experience, but still leaves the ownership requirement unverified.

## Work efficiently

- Prefer responses with useful profile fields and source text when supported. Assess candidates together against the same requirements, keeping each person's evidence distinct.
- Use supported batch reads or bounded parallel lookups when they reduce waiting. Reuse existing or in-flight checks where practical instead of fetching the same evidence twice.

## Count candidate-discovery calls

- Count **one successfully completed API request to find additional people** as **one candidate-discovery call**. Classify by purpose, not tool name: a `web_search` for new candidate names counts; the same tool used to verify a known candidate does not.
- Exclude qualification or identity checks, profile lookups, evidence-page reads, tool discovery, and job status/result reads. Also exclude failed, errored, or incomplete attempts; accepted/running jobs count only when successfully completed.
- Count outer API requests, not provider-internal queries, search directions, steps, or individual results. A valid empty or all-duplicate discovery response still counts; each successful candidate-discovery next-page request counts once.
- Apply this definition to both the discovery budget and any reported discovery count or “search rounds.” Report failures and verification work separately when useful; never add them to the discovery total.

## Adapt search depth and decide when to stop

- **Adjust search effort:** For numeric or open-ended searches, use **eight successful candidate-discovery calls** as an adjustable default, **not a hard cap or minimum**. Freely increase or reduce this number based on task complexity, coverage, and the likely value of further search. Explicit user call, time, cost, and stopping limits take priority.
- **Expand useful coverage:** Explore complementary candidate pools across roles, organizations, communities, and sources. Pivot when results are mostly duplicates or irrelevant; cosmetic query rewrites do not broaden coverage.
- **Meet numeric targets:** Prioritize promising candidates and decisive checks. Stop expanding when enough distinct, evidence-supported people meet the current request. Previously delivered matches do not satisfy a request for additional people.
- **Judge open-ended completion:** Continue while meaningful expansions produce additional qualified people. Consider stopping when relevant channels are reasonably covered and further distinct searches add little; weigh actionable unresolved leads before concluding that useful options are exhausted. A duplicate-heavy batch alone is a reason to pivot, not stop.
- **Build on prior progress:** Reuse the candidate pool, supporting evidence, and unresolved gaps on continuation, and reassess how much further search is useful. Keep lightweight notes and count each person once across duplicate and parallel results.

## Present useful results

- Return all verified, deduplicated matches for the current request, ranked by relevance, unless the user sets a result limit. For long lists, provide a complete deliverable and label any inline shortlist as a preview.
- Prefer Markdown tables for presenting candidate lists.
- Keep **evidence-supported matches**, **inferred possible fits**, and **pending verification** visibly separate. Count only people whose hard requirements are supported as verified; explain the material inference or gap for other leads.
- Share an early batch when useful without waiting for every uncertain lead. Continue the remaining work in the same run and reconcile the complete list at the end; correct earlier claims if later evidence changes them.
- Include supporting sources and briefly explain material gaps, target shortfalls, or stopping limits. Summarize coverage or counts when useful. Do not describe a budget-limited or low-yield search as exhaustive.
