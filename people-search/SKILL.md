---
name: people-search
description: Find, verify, and recommend people or creators using public professional sources. Use for fixed targets, additional candidates, or finding as many as possible. Share useful matches early and enrich professional contact details.
---

# People Search

Find people who meet the user's requirements, with supporting evidence and usable contact details. Adapt the effort to the task rather than imposing a fixed research process.

## Core principles

- **Broad discovery:** Cover complementary candidate pools with targeted searches, adjusting the strategy as gaps emerge.
- **Strict verification:** Count or present a candidate as a match only after verifying they meet the user's criteria.
- **Complete accounting:** Keep every candidate's outcome explicit and preserve the full qualified set through ranking and delivery.

## Workflow

1. **Stay within the request.** Identify the required qualifications and result goal. Do not turn an ordinary recommendation into an exhaustive global inventory. Ranking preferences, such as larger audiences, change ordering—not languages, markets, or eligibility criteria.

2. **Find and verify efficiently.** Choose enabled tools and current schemas by evidence need: platform-specific tools for creators and audience metrics, professional-profile tools for career criteria, and web search or source reads for missing evidence. Reuse source-linked facts for the right person and timeframe. Research only material gaps or conflicts, not the whole biography again; do not require a second source when sufficient evidence already exists. Use batch or parallel checks where useful and deduplicate identities.

3. **Show useful results early.** Unless the user wants final-only delivery, share the first useful verified match or batch with names, links, and qualification evidence. Label it partial and continue the remaining work in the same run without waiting for another prompt. Do not wait for the whole search or contact enrichment, unless contactability is a required qualification. Send further updates when they add useful results or corrections, not just status messages.

4. **Enrich professional contacts.** By default, try to add a work email or public business contact channel for the verified people being delivered. Reuse contacts already found and tell the user before enrichment calls. For missing work emails, use the current `contact_enrich` schema: explicitly select `fields: ["work-email"]` with the person's name and verified current employer domain; default profile lookup alone does not reveal an email. Cite the source or provider and report lookup status honestly. Do not guess addresses, request private-email or phone-number reveals, or start outreach. Missing contacts do not disqualify a match unless the user requires them.

5. **Stop at the right goal.** For a fixed target, stop once enough distinct verified matches satisfy the request; previously delivered people do not count toward additional results. For “as many as possible,” continue while meaningful expansions yield qualifying people. High duplication calls for a useful pivot, not automatic completion. When discovery ends, finish screening the existing pool using available evidence and targeted gap checks; do not silently discard unreviewed candidates. Keep genuinely unresolved leads separate from verified matches. Respect explicit scope, time, cost, and call limits; a discovery-only budget does not cap verification. If a real limit prevents completion, return a clearly partial result and explain what remains.

6. **Consolidate the handoff.** Reconcile batches into one deduplicated list, preferably a Markdown table, with reasons, sources, and available contacts. Return all verified matches found unless the user sets a result limit; label any inline shortlist as a preview of the full deliverable. Correct earlier claims when evidence changes, and do not claim exhaustiveness without support.
