---
name: people-search
description: Find, verify, and rank people using professional profiles and public sources. Use for people-search requests, including numeric targets, additional candidates, or finding as many as possible. Reuse sufficient evidence, research material gaps, and keep inferred leads separate from verified matches.
---

# People Search

Find people who meet the user's requirements, with evidence that supports the recommendation. Adapt the search depth and approach to the request.

## Understand the request and choose tools

Choose tools by evidence need rather than running every available tool:

| Need | Useful tools |
| --- | --- |
| Natural-language professional brief | `people_search_semantic` |
| Exact title, employer, profile-country, or skill filters | `people_search_structured` |
| Complementary profile discovery or identity lookup | `people_search` |
| Cases, interviews, projects, or other experience evidence | `web_search` |
| Additional text from known public pages | `web_contents` or `web_scrape` |

Use enabled tools and their current schemas. Avoid turning current-role filters into extra requirements for past-experience searches. For submitted jobs, read results with `company_contact_get` or `web_contents_get`, as appropriate.

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

For example, 3 successful professional searches + 4 successful public-web searches for new candidates + 1 command quoting failure + later evidence-page checks = **7 candidate-discovery calls**, not 8.

## Expand the search and judge when to stop

- Cover complementary candidate pools through meaningful changes in roles, organizations, communities, or sources. Pivot when results are mostly duplicates or irrelevant; cosmetic query rewrites do not broaden coverage.
- For open-ended requests, continue while meaningful expansions produce additional qualified people. Consider stopping when the relevant channels are reasonably covered and further distinct searches yield little or nothing.
- For numeric targets, prioritize promising candidates and inexpensive, decisive checks. Stop expanding when enough distinct, evidence-supported people meet the current request. Previously delivered matches do not satisfy a request for additional people.
- For numeric or open-ended searches without a user-specified budget, use **eight successful candidate-discovery calls** as the default budget, not a quota to consume. Respect any overall time or cost limit even when failures do not consume discovery calls. A single-person lookup or request for a few examples need not use this expansion budget.
- Reuse the existing pool on continuation. An explicit request to continue can start a fresh discovery budget.
- Keep lightweight notes on distinct people, supporting sources, and unresolved gaps. Count people once across duplicates and parallel results.

## Present useful results

- Return all verified, deduplicated matches for the current request, ranked by relevance, unless the user sets a result limit. For long lists, provide a complete deliverable and label any inline shortlist as a preview.
- Prefer Markdown tables for presenting candidate lists.
- Keep **evidence-supported matches**, **inferred possible fits**, and **pending verification** visibly separate. Count only people whose hard requirements are supported as verified; explain the material inference or gap for other leads.
- Share an early batch when useful without waiting for every uncertain lead. Continue the remaining work in the same run and reconcile the complete list at the end; correct earlier claims if later evidence changes them.
- Include supporting sources and briefly explain material gaps, target shortfalls, or stopping limits. Summarize coverage or counts when useful. Do not describe a budget-limited or low-yield search as exhaustive.
