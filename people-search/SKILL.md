---
name: people-search
description: Find, verify, and rank people or creators using public professional sources. Use for fixed targets, additional candidates, or finding as many as possible. Clarify requirements, plan the search, enrich results for the user's purpose, and deliver ranked interim batches followed by a final table or spreadsheet.
---

# People Search

Understand the user's needs, plan a suitable search, and find evidence-supported matches. Rank qualifying candidates, share useful interim results, and deliver a consolidated final version.

## Core principles

- **Broad discovery:** Cover complementary candidate pools with targeted searches, adjusting the strategy as gaps emerge.
- **Strict verification:** Count or present a candidate as a match only after verifying every qualification the user requires. Keep candidates with unresolved requirements as leads.
- **Complete accounting:** Keep every candidate's outcome explicit and preserve the full qualified set through ranking and delivery.

## Workflow

1. **Understand the request.** Use the request and its context to identify the user's goal, scope, any requested count, and what makes a person a match. Use preferences to rank matches. Clarify unresolved details when they would materially change who qualifies or where to search.

2. **Work out where to look.** Identify where relevant people are likely to be named and what would show they meet the request. When the best route is unclear, sample promising sources or queries to learn how they describe these people and what they can verify. Use the sample to choose search terms, sources for finding candidates, and sources for checking their fit.

3. **Verify each recommendation.** Deduplicate candidates and check each requirement against evidence tied to the person, including the relevant role, place, and timeframe. Check shared sources for what they support about each person. Keep the source link and the specific detail that supports the match. Reuse sufficient evidence and batch checks where useful. For missing, inaccessible, or conflicting evidence, seek a source that directly addresses the claim and update your assessment.

   Assess the work the person actually did against the user's requirements. A reliable, specific role description or a named project can be sufficient on its own. When past experience qualifies, assess it in the period it occurred and check current status separately for the contact label. Before setting aside an otherwise supported match, make a targeted check for the missing requirement.

4. **Rank by confidence.** By default, order qualified candidates from highest to lowest confidence in both interim and final results. Judge confidence that they meet all required qualifications by source reliability, attribution to the person, and fit to the required scope and timeframe. Use the user's preferences to order candidates with similar confidence, and honor any explicit sort order for qualified results. When useful results are ready, share a ranked subset labeled interim with source links and qualification evidence, then continue the work in the same run. Respect final-only requests. When contactability is optional, share interim results as soon as the qualification evidence is ready.

5. **Enrich each recommendation for the user's purpose.** Use the requested fields and the intended use of the list to choose what to add, such as representative work for evaluating collaborators or a public contact channel for outreach. Reuse sourced details and verify additions. For a professional profile lookup, use `contact_enrich` in its default profile mode with a `contact_search` result ID, a LinkedIn profile URL, or the person's name and employer domain. For work email, select `fields: ["work-email"]` with the person's name and verified current employer domain. Do not guess contact details, request private-email or phone-number reveals, or start outreach. Missing contacts do not disqualify a match unless required by the user.

6. **Complete the requested scope.** For a fixed target, finish once enough distinct verified matches satisfy the request. Count only new people when the user asks for more. For “as many as possible,” follow productive sources to related records. If results repeat or a likely group is missing, try a route that could reach people the current search misses. Use the number of newly verified people and the remaining routes to judge when to stop expanding. Finish screening the candidates already found using available evidence and targeted checks. Respect explicit scope, time, cost, and call limits. If a real limit prevents completion, explain what remains.

## Tool roles

Use the table to choose available tools for the evidence you need.

| Need | Useful tools |
| --- | --- |
| Find candidates from a natural-language description of their experience, responsibilities, or expertise | `people_search_semantic` |
| Build a candidate pool from exact current titles, employers, profile countries, or skills | `people_search_structured` |
| Check a known person's identity or role using their name and organization | `people_search` |
| Find public cases, interviews, projects, or credited work that show what a person did, where, or when | `web_search` |
| Read several known public URLs in one batch | `web_contents` |
| Read one known public page | `web_scrape` |
| Read a known public LinkedIn profile or post when general extraction returns a sign-in page or misses the relevant text | `linkedin_profile` or `linkedin_post`, if available |
| Resolve a known person's professional profile or look up their work email | `contact_enrich` |

Cases, interviews, projects, and credited work can surface people with relevant experience. For a known candidate, search their name, organization, and the missing requirement. Use local-language terms when relevant. If a source describes only the organization's work, look for a source that connects the candidate to that work.

Structured title and employer filters refer to current roles, and country filters refer to the person's profile location. For past-experience searches, assess eligibility against the relevant period and any current-role requirement the user specified. For creators and audience metrics, use enabled tools for the named platform.

## Delivery

- Prefer **Markdown tables or a Sheet/spreadsheet**. Show each person or channel, the evidence for their fit, and sources. Choose other columns, such as representative work, metrics, or public contact channels, based on the request.
- Build the **final consolidated version** from the verified candidate list. Check that every distinct match within the requested scope and result limit appears in the ranked recommendations, including verified past experience when eligible. Keep unresolved leads separate. For long lists, provide the complete table or Sheet and label any inline shortlist as a preview.
- If work remains because of a real limit, label the handoff partial rather than complete and state the remaining gaps. Do not claim exhaustiveness without support.
