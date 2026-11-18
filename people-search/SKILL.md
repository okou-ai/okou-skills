---
name: people-search
description: Find, verify, and rank people or creators using public professional sources. Use for fixed targets, additional candidates, or finding as many as possible. Deliver ranked interim batches and a final table or spreadsheet with professional contact details when relevant to the request.
---

# People Search

Understand the user's needs, plan a suitable search, and find evidence-supported matches. Rank qualifying candidates, share useful interim results, and deliver a consolidated final version.

## Core principles

- **Broad discovery:** Cover complementary candidate pools with targeted searches, adjusting the strategy as gaps emerge.
- **Strict verification:** Count or present a candidate as a match only after verifying every qualification the user requires. Keep candidates with unresolved requirements as leads.
- **Complete accounting:** Keep every candidate's outcome explicit and preserve the full qualified set through ranking and delivery.

## Workflow

1. **Clarify the need.** Establish the purpose, required qualifications, relevant scope, result goal, and ranking priorities from the request and context. Ask focused questions only when missing information would materially change the search; do not repeat questions already answered.

2. **Plan the search.** Select promising candidate pools, complementary sources, query directions, and the checks needed to establish eligibility. Briefly explain the approach before searching. Match the breadth to the user's goal and adjust as evidence or gaps emerge.

3. **Find and verify efficiently.** Choose tools from the table below and check their current schemas. Deduplicate people and accounts before detailed verification. Reuse evidence for the right person and period. If two tools return the same page, count it as one source. Use batch or parallel checks for the remaining gaps.

4. **Rank by confidence.** By default, order qualified candidates from highest to lowest confidence in both interim and final results. Judge confidence that they meet all required qualifications by source reliability, attribution to the person, and fit to the required scope and timeframe. Use the user's preferences to order candidates with similar confidence, and honor any explicit sort order for qualified results. When useful results are ready, share a ranked subset labeled interim with source links and qualification evidence, then continue the work in the same run. Respect final-only requests. When contactability is optional, share interim results as soon as the qualification evidence is ready.

5. **Fill gaps that matter to the request.** If identity, role, or affiliation still needs resolving, use `contact_enrich` in profile mode with a `contact_search` result ID, a LinkedIn profile URL, or the person's name and employer domain. Look up contact details when the deliverable calls for a way to reach the person. Reuse a suitable public business channel when available. To look up one work email, pass the person's name, verified current employer domain, and `fields: ["work-email"]`. Announce enrichment before calling, cite the source or provider, and record the outcome. Do not guess addresses, request private-email or phone-number reveals, or start outreach. Missing contacts affect eligibility only when required by the user.

6. **Complete the requested scope.** For a fixed target, finish once enough distinct verified matches satisfy the request; previously delivered people do not count toward additional results. For “as many as possible,” continue while meaningful expansions yield qualifying people. High duplication calls for a useful pivot. Respect explicit scope, time, cost, and call limits; if a real limit prevents completion, explain what remains.

## Tool roles

Start with the source most likely to connect a person to the required qualification. Choose the next call based on what the first result leaves unresolved.

| What you know | Tool and input | What to use from the result |
| --- | --- | --- |
| Duties or expertise that can span several job titles | `people_search_semantic` with a natural-language brief | Read the matched profile text for what the person actually did. |
| A project, publication, interview, or event where people are credited | `web_search` with the work, topic, and relevant date or venue | Find original pages that name people and specify their contributions. |
| A known person, or a question whose answer names people across public sources | `people_search` with a name and organization, or with the question itself | Follow the extracted profile's `sourceIds` to the search results. Check the original wording for each hard condition, such as whether a location is current. |
| Exact current employer, title, profile country, or skill | `people_search_structured`, e.g. `{"companyDomains":["gitlab.com"],"titles":["software engineer"],"limit":1}` | Inspect individual résumé records and their experience. Results are billed per record. For another page, repeat the filters and pass the returned `scroll_token` as `scrollToken`. |
| Potential business contacts at target companies | `contact_search` with titles, seniorities, person or company locations, company domains, or sizes | The preview can include a masked surname, an ID, and a `has_email` flag. Use the ID for a selected person's profile lookup. An email lookup is a separate operation. |
| A known public URL with a missing fact | `web_scrape` for one page or its links, `web_contents` for a batch | Read the relevant passage. For a LinkedIn sign-in page or missing text, try `linkedin_profile` or `linkedin_post` with the known public URL, if available. |
| Creators or works on a named platform | `creator_search` for Instagram handles, names, or bios, or the platform's content search for a topic | Check the account and original work. A transcript can locate spoken content. Inspect the original footage for visible actions and use audience data for audience demographics. |

For example, to find speakers on logical replication at a particular conference, search the event and topic first. Read each session page for the speaker, year, and session type. To find people who teach PostgreSQL across roles, start with the duties in a semantic query. If a source credits only the organization, look for the individual's role in the work. For a known candidate, search their name, organization, and the specific gap, using local-language terms when relevant.

Structured title and employer filters refer to current roles. Apply them to past-experience searches only if the user also requires that current role or employer. The country filter refers to the person's profile location. Records must match every supplied filter, but values within one filter are alternatives. For example, `skills: ["python", "sql"]` matches either skill. If both are required, check both on each candidate. Each provider's total counts matches in its own dataset. Count people toward the user's target after verification and deduplication.

When a lookup returns `submitted`, use the saved job ID with the matching reader (`company_contact_get` or `web_contents_get`). Check the provider status and actual result before recording an outcome. A completed job can contain a provider error.

## Delivery

- Prefer **Markdown tables or a Sheet/spreadsheet**. Choose columns suited to the request for the person or channel, profile link, qualification evidence or metrics, ranking rationale, and sources. Include contact details and lookup status when relevant to the requested deliverable.
- After interim batches, deliver a **final consolidated version**, not just a progress summary or references to earlier messages. Reconcile duplicates and corrections, and include all verified matches within the requested scope and result limit. For long lists, provide the complete table or Sheet and label any inline shortlist as a preview.
- If work remains because of a real limit, label the handoff partial rather than complete and state the remaining gaps. Do not claim exhaustiveness without support.
