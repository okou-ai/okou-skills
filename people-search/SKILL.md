---
name: people-search
description: Find, verify, and rank people or creators using public professional sources. Use for a fixed number of matches, additional candidates, or a broad search. Include qualification evidence and relevant professional contact details.
---

# People Search

Include a person in the recommended list only when the available evidence supports every required qualification. Keep unresolved candidates as leads.

## Workflow

1. **Clarify the need.** Identify the purpose, requirements, scope, result goal, and ranking preferences from the request and context.

2. **Plan the search.** Choose candidate pools and sources that fit the requirements, and decide how to verify eligibility. Adjust the search as evidence reveals gaps.

3. **Find and verify.** Use available tools and their current schemas. Reuse evidence tied to the right person and timeframe. Research material gaps or conflicts, batch checks where useful, and deduplicate identities.

4. **Rank qualified candidates.** Default to highest confidence first in interim and final results. Judge confidence by source reliability, attribution to the person, and fit to the required scope and timeframe. When candidates have similar confidence, rank them by the user's preferences. Follow any sort order the user specifies.

5. **Enrich profiles and contacts.** Before final delivery, fill relevant gaps in each qualified person's role, organization, and profile link. Try to add a work email or public business contact channel. Reuse sourced details, announce enrichment before tool calls, and report the source and lookup status. Treat contactability as required only when the user asks for it. Limit enrichment to looking up professional information and business contact channels.

6. **Complete the requested scope.** For a fixed target, deliver the requested number of distinct verified matches when available. For additional results, count only new people. For open-ended searches, continue while new sources yield qualifying candidates and change the approach when results mostly repeat. Finish screening the existing pool, using targeted checks for remaining gaps. Respect the user's scope, time, cost, and call limits.

## Tool roles

| Need | Useful tools |
| --- | --- |
| Discover professional profiles when duties can be described in different ways | `people_search_semantic` |
| Build a candidate pool from exact current titles, employers, profile countries, or skills | `people_search_structured` |
| Check a known person's identity or role using their name and organization | `people_search` |
| Find public cases, interviews, projects, or credited work that show what a person did, where, or when | `web_search` |
| Read several known public URLs in one batch | `web_contents` |
| Read one known public page | `web_scrape` |
| Read a known public LinkedIn profile or post when general extraction returns a sign-in page or misses the relevant text | `linkedin_profile` or `linkedin_post`, if available |
| Resolve a known person's professional profile or look up their work email | `contact_enrich` |

Look for names in cases, interviews, projects, and credited work to find candidates with relevant experience. For a known candidate, search by name, organization, and the missing requirement, using local-language terms when helpful. If a source describes only the organization's work, look for a source that ties the person to it.

Structured title and employer filters describe current roles, and country filters describe profile location. For past experience, check the relevant period and apply any current-role requirement the user specified. For creators and audience metrics, use enabled tools for the named platform.

Use the default `contact_enrich` profile lookup with a `contact_search` result ID, a LinkedIn profile URL, or the person's name and employer domain. For a work email, explicitly pass `fields: ["work-email"]` with their name and verified current employer domain.

## Delivery

Prefer a Markdown table or spreadsheet with profile links, qualification evidence, ranking rationale, contact details and lookup status, and sources as relevant. Follow the user's requested format. If an interim shortlist would help and fits the request, label it as interim and include links to supporting evidence. Consolidate interim batches into a single final list that reconciles duplicates and corrections and includes all verified matches within the requested scope and result limit. For long lists, share the complete table and label any inline shortlist as a preview.
