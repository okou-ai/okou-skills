---
name: people-search
description: Find people or enrich a list with evidence that helps the user judge fit. Provide sourced professional contact details and identify important gaps.
---

# People Search

## Define the search

Identify the decision the user wants to make. Turn their criteria into questions that evidence can answer. For example, if they need a speaker for engineering managers, investigate subject expertise, prior speaking, and experience with that audience. Use stated requirements for eligibility. Ask for clarification only if the answer would materially change the search.

Start with the people on a supplied list. For discovery, search relevant roles, work, organizations, and platforms. Run `okou data tools` for availability and `okou data describe <tool>` for supported inputs. Choose tools by the missing information using the [tool reference](references/tool-evidence.md). Reuse records already retrieved.

For a roster, check every member. For “as many as possible,” use the largest supported page size within the user's limits, continue across batches, and change sources when results repeat. For large responses, index every candidate with an ID and pointer to the full record, then review in batches. Deduplicate against earlier results and resolve namesakes using role, affiliation, and work.

Check each candidate against the stated requirements and retain the supporting facts. Keep candidates with unresolved requirements separate from confirmed matches. Continue searching until the requested count or scope is covered, or relevant sources yield few new people. Treat preferences as comparison criteria.

## Profile the confirmed matches

For each confirmed match, read sources that identify both the individual and their work. Start with a primary source such as a project credit, publication, talk, portfolio, or staff page. If a decisive question remains open, seek a source that addresses it directly.

- Describe what the person did, when, for whom, and with what observable outcome, wherever those details bear on the request. Attribute team results and distinguish past roles from current responsibilities.
- Connect each judgment to a criterion and a concrete fact. Place the source link beside the fact whenever available. For user-supplied material without a URL, cite the document and page or section.
- Explain the limit of the evidence where it could change the decision. A conference program crediting a candidate with a database migration talk supports speaking experience on that topic. Personal ownership of the migration needs separate evidence. Surface conflicting evidence and leave unresolved criteria open.

## Find a way to reach the person

Check the person's professional site, employer directory, publications, or verified professional accounts. Record available public work phone numbers, work email addresses, and direct links to the person's LinkedIn, professional messaging account, or contact form. Include the actual number, address, or URL with its source. Label a team inbox or office switchboard as an indirect route. A profile link can serve as a contact route without implying that private messaging is open.

If contacts are missing, search specifically for the person's contact page or professional account. For a requested work-email lookup, follow the tool reference. Never infer addresses from naming conventions. If no public professional route is found, say where you checked.

## Deliver the results

Honor the requested format and count. Otherwise provide a Markdown table or XLSX with one row per person, ordered by relevance. Include name, current affiliation and role, criterion-specific findings with linked facts, important unknowns, and contact details. Split findings into columns when the same criteria apply across candidates. Preserve the full supported list and briefly state the search coverage and any shortfall. Check identities, attribution, links, and contact ownership before delivery.
