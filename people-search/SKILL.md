---
name: people-search
description: Find people or verify an existing list using public professional sources. Check the user's requirements and build profiles of qualified candidates with verified facts, sources, and details relevant to the task.
---

# People Search

## Define the decision

- Identify the decision the user needs to make, the hard requirements, the ranking preferences, and the search scope. For each hard requirement, specify who or what to verify, the relevant time period or geography, and what evidence is sufficient to pass. When a current role is required, verify it with current evidence and record the candidate's role and responsibilities at the time of any historical case separately. Use the user's examples to derive criteria. Record any relationship between the examples and the user that the evidence establishes.
- Define what to learn about each qualified candidate. Turn the user's intended use of the list into questions about relevant experience, work, or circumstances. Identify the facts that could change selection or follow-up. See the [Qualification guide](references/qualify.md) for evidence and enrichment. Ask a clarifying question only if missing information would materially change eligibility and cannot be inferred from context.
- Record the required deliverable contents, format, and visibility for handoff and final validation.
- Start with the supplied list when asked to verify it or fill profile gaps. When finding additional people, deduplicate against earlier batches and count the newly verified candidates.

## Choose search sources and maintain candidate records

Start with the source most likely to establish the key requirements directly. Run independent queries in parallel and read known URLs in batches when supported. Switch sources when results duplicate existing evidence or consistently lack key facts. Use the tools' current parameters. See [Tools and evidence](references/tool-evidence.md) for filtering, pagination, result types, and failure handling.

| Lead | Where to start | What to verify |
| --- | --- | --- |
| Event, project, paper, case study, or credited work | Use `web_search` with the event, work, topic, or time period. | Check the original agenda or credits for the person's role, contribution, and timing. |
| Similar responsibilities across different job titles | Describe the actual responsibilities and experience in `people_search_semantic`. | Review the professional profiles and relevant experience in the results. |
| Known name and organization, or a specific question about who qualifies | Use `people_search` with the name and organization, or ask who meets a verifiable criterion. | Discover or check candidates. If the response includes `sourceIds`, follow them to verify against the underlying sources. |
| Specific current title, employer, profile country, or skill | Use `people_search_structured` to filter professional histories. | Check the experience, time period, and geographic scope. |
| Business contacts at a target company | Use `contact_search` with company, title, seniority, or person and company location filters. | Select contacts from the previews for further verification. |
| Creator or work on a specific platform | Start with content search for that platform. On Instagram, `creator_search` can find accounts by name or bio. | Verify the account and the attribution of the original work. For speaker identity or language, see [Audio and video attribution and language](references/tool-evidence.md#audio-and-video-attribution-and-language). Verify visible actions in the original footage and audience geography using audience analytics. |
| Known public URL or a specific evidence gap | Use `web_scrape` for a single page or its links and `web_contents` for batches. Use `linkedin_profile` or `linkedin_post` for known LinkedIn URLs when useful. | Check the relevant passage, credit, or link destination, including who or what it refers to and where it came from. |

Maintain one exportable record per person. Record their identity and profile link, the verdict and evidence for each hard requirement, and any unresolved questions. For qualified candidates, use the same record to build the task-specific profile and add relevant contact channels. Link verified facts to the original source, the relevant passage or timestamp, and applicable dates. Deduplicate by person or account before detailed verification. Treat the same original page returned by multiple APIs as one source.

For parallel work, share eligibility criteria, record fields, and allowed status values across groups. Split discovery by lead or source, assign detailed verification by person or account, and reuse existing evidence. When groups keep separate records, confirm that the first record from each group merges into the shared format.

## Decide what to do next based on the evidence

- **Verify the user's basic requirements.** Carry forward evidence found during discovery and start with the requirement most likely to block inclusion. If a candidate falls short or a key gap has no credible source, record why and move to other candidates.
- **Start building the task-specific profile as soon as the person qualifies.** Include the key facts and source links that established eligibility. Use them to explain why the person is relevant, then fill gaps in [the profile](references/qualify.md#when-to-enrich-candidate-profiles) that could affect the user's choice or next action. Stop when the profile supports the decision or available sources are unlikely to resolve the remaining gaps.
- **Check professional profiles and contact channels.** Use the default profile mode of `contact_enrich` when identity, responsibilities, or organization still need verification. When contact channels are needed, start with an existing public professional channel and look up a work email separately when needed. See [Professional profiles and work email](references/tool-evidence.md#professional-profiles-and-work-email). If contact information is a hard requirement, verify eligibility against it. Outreach requires explicit user authorization.
- **Finish the overall search.** For a fixed count or an enumerable scope, verify candidates against the user's requirements. For open-ended searches, continue while new sources are likely to yield more qualified people, distinct options, or key evidence. When results repeat, look for a source that reaches a different pool. When qualified people are scarce, prioritize sources that can verify the blocking requirement directly. When the remaining sources are unlikely to improve the results, deliver the verified list with the scope covered and any gaps.

## Deliver from candidate records

- **Decide whether to deliver an interim shortlist.** Follow the user's delivery instructions. When none are given, use the purpose of the task to decide whether a partial result independently supports a next step. For candidate-pool expansion or tasks where screening can begin while research continues, share an initial batch once enough evidence supports the candidates and state what the batch covers. When the decision depends on a full comparison, complete coverage, or resolving a unique identity, consolidate the verified results before delivering them.
- For each qualified candidate, deliver the task-specific profile with the key eligibility evidence, relevant findings, and any open questions. When the user needs to choose among candidates, explain the verified differences that matter to that choice. Include relevant public contact channels with their ownership and verification status when needed.
- Generate, sort, and consolidate deliverables from the same candidate records, including previously delivered batches in the final result. Check format, visibility, deduplication, counts, links to evidence, and deliverable usability against the requirements recorded at the start. Deliver the finished output once validated. If the complete list is a file, give a summary and link in chat. When the user asks to see the full list in chat, reuse the generated content. Label any excerpt from a long list as a preview.
- When coverage is limited, deliver verified results and state the scope searched and facts that still lack evidence. Claim completeness only for an enumerable scope that has been fully covered.
