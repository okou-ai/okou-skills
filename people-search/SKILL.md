---
name: people-search
description: Find, verify, rank, and enrich professional contacts using profiles and public sources. Use for people-search requests, including numeric targets, additional candidates, or finding as many as possible. Deliver useful verified matches early while completing the requested scope, and keep inferred leads separate from verified matches.
---

# People Search

Find people who meet the user's requirements, with supporting evidence and usable professional contacts. Interleave discovery, verification, early delivery, and contact enrichment; adapt search depth without treating an interim batch as completion.

## Core principles

- **Broad discovery:** Cover complementary candidate pools with targeted searches, adjusting the strategy as gaps emerge.
- **Strict verification:** Count or present a candidate as a match only after verifying they meet the user's criteria.
- **Complete accounting:** Keep every candidate's outcome explicit and preserve the full qualified set through ranking and delivery.

## Plan the search and choose tools

Identify the required qualifications, whether the goal is a fixed number or as many people as possible, prior matches to exclude from requests for additional people, and explicit scope, time, or cost limits.

Choose tools by evidence need rather than running every available tool. The examples below are recommended uses, not mutually exclusive capability boundaries:

| Example need | Useful tools |
| --- | --- |
| Natural-language discovery of professional profile pages | `people_search_semantic` |
| Exact current title, current employer, profile-country, or skill filters | `people_search_structured` |
| Public professional profile search by identity, role, employer, education, skill, or location | `people_search` |
| Discovery of public sources documenting cases, interviews, projects, or experience | `web_search` |
| Reading source text from known public pages | `web_contents` or `web_scrape` |
| Work-email lookup or professional contact enrichment for a known person | `contact_enrich` |

Use enabled tools and their current schemas. Treat search results as leads, not verified qualifications.

For `people_search_structured`, title and employer filters refer to current roles; profile-country is the country in the person's profile location, not nationality or the employer's headquarters country. Do not turn current-role filters into extra eligibility requirements for requests about past experience.

## Discover, verify, and track candidates

- Prefer responses with useful profile fields and source text. Reuse source-linked facts when they sufficiently support the requirement for the right person and timeframe; screening does not require a fresh API call or a full biography for everyone.
- Exclude supported mismatches early. For potentially qualifying people, research material gaps such as missing proof, ambiguous identity, conflicting sources, or stale evidence. Search for the missing fact and consider another relevant source when one page lacks it; uncertainty is not proof of ineligibility.
- Stop checking a fact once it is sufficiently supported, clearly contradicted, or the necessary evidence is unavailable from relevant sources. Avoid repeated searches merely for reassurance.
- Assess candidates against the same requirements, keeping evidence distinct. Use supported batch reads or bounded parallel checks to reduce waiting, and reuse existing or in-flight checks.
- Keep one lightweight record per deduplicated person, with supporting evidence, a review outcome, and any remaining check. Merge duplicate identities, not distinct people; ranking or missing contacts must not silently remove candidates. Preserve the pool and pending checks on continuation.

Use these mutually exclusive review outcomes; never relabel unfinished work to clear the queue:

| Outcome | Meaning |
| --- | --- |
| `verified match` | Evidence supports the user's required qualifications. |
| `excluded` | A supported mismatch, with its reason recorded. |
| `unresolved` | Material gaps remain after targeted checks, with no known feasible decisive check left. |
| `pending review` | Not yet screened, or still awaiting an actionable qualification check. |

For example, reuse a source that explicitly describes someone leading a team's first implementation. A relevant job title alone may suggest that experience, but leaves the ownership requirement unverified.

## Share useful results early

- Unless the user requests final-only delivery, share the first useful verified match or small batch as soon as it is ready in a user-visible intermediate update. Do not wait for all searches, the whole pool's review, a preset batch size, or contact enrichment; a contact method only gates qualification when the user makes it an explicit requirement.
- Label the batch as partial. Include each person's name, relevant professional context, why they qualify, supporting source links, and any contacts already available. Mark contacts not yet looked up as pending or not checked rather than implying none exist; keep unverified leads separate.
- Continue the remaining discovery, qualification checks, and enrichment in the same run without asking the user to request more. Share later batches or updates when they add meaningful matches, contacts, or corrections; avoid repetitive status-only messages.
- Keep one accumulating, deduplicated result set across batches. An early batch is useful progress, not a reason to stop or replace the final consolidated handoff.

## Enrich professional contact details

- For legitimate professional searches, attempt contact enrichment for each verified person being delivered unless the user opts out. State that you will look up work emails or public business contact channels before making enrichment calls; respect the user's scope, time, and cost limits.
- Reuse source-backed contact details already found. For missing work emails, discover and describe the enabled `contact_enrich` tool and use its current schema. Explicitly select `fields: ["work-email"]` with the person's name and verified current employer domain; a default profile lookup does not reveal an email. Send only the public professional identifiers needed for the lookup, and match identity and current affiliation before attributing a result.
- Prefer one work email plus relevant public professional contact channels, such as an official contact form, professional website, or LinkedIn/profile link. Do not guess email addresses from naming patterns or request private-email or phone-number reveals. If no email is found or enrichment is unavailable, check an official professional page for an alternative contact channel.
- Keep each contact's source URL or provider attribution and any returned verification or deliverability status; label provider claims as reported, not independently verified. Distinguish `found`, `not found` after a completed lookup, `not checked` due to unavailable tools or limits, and `pending/failed`; a failed or incomplete lookup is not evidence that no email exists.
- Enrich deduplicated matches being delivered, not every discovery lead. Do not exclude otherwise qualified people for missing contact details unless contactability is an explicit user requirement. Contact research does not authorize sending messages or starting outreach.

## Count candidate-discovery calls

- Count **one successfully completed API request to find additional people** as **one candidate-discovery call**. Classify by purpose, not tool name: a `web_search` for new candidate names counts; the same tool used to verify a known candidate does not.
- Exclude qualification or identity checks, profile or contact-enrichment lookups, evidence-page reads, tool discovery, and job status/result reads. Also exclude failed, errored, or incomplete attempts; accepted/running jobs count only when successfully completed.
- Count outer API requests, not provider-internal queries, search directions, steps, or individual results. A valid empty or all-duplicate discovery response still counts; each successful candidate-discovery next-page request counts once.
- Apply this definition to both the discovery budget and any reported discovery count or “search rounds.” Report failures and verification work separately when useful; never add them to the discovery total.

## Separate discovery stopping from task completion

- **Adjust search effort:** For numeric or open-ended searches, use **eight successful candidate-discovery calls** as an adjustable default, **not a hard cap or minimum**. Freely increase or reduce this number based on task complexity, coverage, and the likely value of further search. Explicit user call, time, cost, and stopping limits take priority.
- **Expand useful coverage:** Explore complementary candidate pools across roles, organizations, communities, and sources. Pivot when results are mostly duplicates or irrelevant; cosmetic query rewrites do not broaden coverage.
- **Stop discovery, not review:** Saturation or a discovery-call limit can end expansion; it does not finish review of people already found or impose the same limit on verification. Respect explicit limits on the overall task.
- **Meet numeric targets:** Prioritize promising candidates and decisive checks. Once enough distinct, evidence-supported people meet the requested number, the remaining pool need not be fully reviewed unless the user also asks for comprehensive screening. Previously delivered matches do not satisfy a request for additional people.
- **Stop open-ended discovery:** Continue while meaningful expansions produce additional qualified people. Consider ending discovery when relevant channels are reasonably covered and further distinct searches add little. A duplicate-heavy batch alone is a reason to pivot, not stop.
- **Complete open-ended review:** Before declaring an open-ended request complete, screen the whole current pool, not just the obvious matches, and finish actionable qualification checks so that `pending review` is zero. If a real scope, time, cost, or access constraint prevents this, return partial results with pending counts and the blocking reason. Keep genuinely inconclusive candidates `unresolved`, not excluded.

## Deliver a consolidated result

- Reconcile all batches into one deduplicated list of verified matches, ranked by relevance, respecting the user's result limit. For long lists, provide a complete deliverable and label any inline shortlist as a preview; do not silently truncate to the strongest few.
- Prefer Markdown tables with qualification evidence, available work emails or professional contact links, and contact sources and lookup status. Explain material gaps, missing contacts, target shortfalls, and stopping limits; correct earlier claims if evidence changed.
- For open-ended requests, report the deduplicated pool total and counts for all four review outcomes; their sum must equal the pool total. If review remains unfinished, label the handoff partial and identify what remains. Distinguish completed review of the current pool from exhaustive discovery; do not describe a budget-limited or low-yield search as exhaustive.
