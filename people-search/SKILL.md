---
name: people-search
description: Find, verify, and rank people or creators using public professional sources. Use for fixed targets, additional candidates, or finding as many as possible. Clarify requirements, plan the search, enrich professional contacts, and deliver ranked interim batches followed by a final table or spreadsheet.
---

# People Search

Understand the user's needs, plan a suitable search, and find evidence-supported matches. Rank qualifying candidates, share useful interim results, and deliver a consolidated final version.

## Core principles

- **Broad discovery:** Cover complementary candidate pools with targeted searches, adjusting the strategy as gaps emerge.
- **Strict verification:** Count or present a candidate as a match only after verifying they meet the user's criteria.
- **Complete accounting:** Keep every candidate's outcome explicit and preserve the full qualified set through ranking and delivery.

## Workflow

1. **Clarify the need.** Establish the purpose, required qualifications, relevant scope, result goal, and ranking priorities from the request and context. Ask focused questions only when missing information would materially change the search; do not repeat questions already answered.

2. **Plan the search.** Select promising candidate pools, complementary sources, query directions, and the checks needed to establish eligibility. Briefly explain the approach before searching. Match the breadth to the user's goal and adjust as evidence or gaps emerge; ranking preferences are not additional eligibility requirements.

3. **Find and verify efficiently.** Use the tools below and their current schemas. Reuse source-linked facts for the right person and timeframe, researching only material gaps or conflicts. Do not repeat whole biographies or require another source when evidence is already sufficient. Use batch or parallel checks where useful and deduplicate identities.

4. **Rank and share interim results.** Rank qualifying candidates by the user's priorities. When useful results are ready, especially when many candidates qualify, share a prioritized subset rather than making the user wait for the entire list. Label it interim, include links and qualification evidence, and continue the remaining work in the same run. Respect final-only requests; do not delay interim results for contact enrichment unless contactability is a required qualification.

5. **Enrich professional contacts.** By default, try to add a work email or public business contact channel for the verified people being delivered. Reuse existing contacts and announce enrichment before making calls. For missing work emails, explicitly select `fields: ["work-email"]` in `contact_enrich` with the person's name and verified current employer domain; default profile lookup alone does not reveal an email. Cite the source or provider and report lookup status honestly. Do not guess addresses, request private-email or phone-number reveals, or start outreach. Missing contacts do not disqualify a match unless required by the user.

6. **Complete the requested scope.** For a fixed target, finish once enough distinct verified matches satisfy the request; previously delivered people do not count toward additional results. For “as many as possible,” continue while meaningful expansions yield qualifying people. High duplication calls for a useful pivot, not automatic completion. Stopping discovery does not finish screening the existing pool: use available evidence and targeted gap checks, without silently discarding unreviewed candidates. Keep unresolved leads separate. Respect explicit scope, time, cost, and call limits; if a real limit prevents completion, explain what remains.

## Tool roles

Use the table to choose available tools for the evidence you need.

| Need | Useful tools |
| --- | --- |
| Discover professional profiles when duties can be described in different ways | `people_search_semantic` |
| Build a candidate pool from exact current titles, employers, profile countries, or skills | `people_search_structured` |
| Check a known person's identity or role using their name and organization | `people_search` |
| Find public cases, interviews, projects, or credited work that show what a person did, where, or when | `web_search` |
| Read several known public URLs in one batch | `web_contents` |
| Read one known public page | `web_scrape` |
| Read a known public LinkedIn profile or post when general extraction returns a sign-in page or misses the relevant text | `linkedin_profile` or `linkedin_post`, if available |
| Work-email lookup or professional contact enrichment for a known person | `contact_enrich` |

Cases, interviews, projects, and credited work can surface people with relevant experience. For a known candidate, search their name, organization, and the missing requirement. Use local-language terms when relevant. If a source describes only the organization's work, look for a source that connects the candidate to that work.

Structured title and employer filters refer to current roles, and country filters refer to the person's profile location. For past-experience searches, assess eligibility against the relevant period and any current-role requirement the user specified. For creators and audience metrics, use enabled tools for the named platform.

## Delivery

- Prefer **Markdown tables or a Sheet/spreadsheet**, with columns suited to the request: person/channel and profile link, key qualifications or metrics, ranking rationale, contact details, and sources.
- After interim batches, deliver a **final consolidated version**, not just a progress summary or references to earlier messages. Reconcile duplicates and corrections, and include all verified matches within the requested scope and result limit. For long lists, provide the complete table or Sheet and label any inline shortlist as a preview.
- If work remains because of a real limit, label the handoff partial rather than complete and state the remaining gaps. Do not claim exhaustiveness without support.
