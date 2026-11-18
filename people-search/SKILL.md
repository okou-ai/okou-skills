---
name: people-search
description: Find people or verify and enrich an existing list using public professional sources. Build an evidence-backed candidate profile that supports screening, comparison, or follow-up. Report eligibility, Fit, Intent, and public contact channels where relevant.
---

# People Search

## Define the decision

- Identify the decision the user needs to make, the hard requirements, the ranking preferences, and the search scope. For each hard requirement, specify who or what to verify, the relevant time period or geography, and what evidence is sufficient to pass. When a current role is required, verify it with current evidence and record the candidate's role and responsibilities at the time of any historical case separately. Use the user's examples to derive criteria. Record any relationship between the examples and the user that the evidence establishes.
- Identify which aspects of a candidate's profile matter to the decision. Pair each task need with a question about the candidate, then identify the facts and sources that could change eligibility, ranking, follow-up timing, or the next action.
- Before scoring, use the [Qualification guide](references/qualify.md) to define the Fit percentage, Intent levels, and evidence requirements for this task. Ask a clarifying question only if missing information would materially change eligibility and cannot be inferred from context.
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

Maintain one exportable record per person with **identity and profile, the verdict for each hard requirement, key profile details, evidence for Fit and Intent, relevant contact channels, and unresolved questions**. Update the record as each fact is verified. Link it to the original source, the relevant passage or timestamp, and applicable dates. Deduplicate by person or account before detailed verification. Treat the same original page returned by multiple APIs as one source.

For parallel work, share eligibility criteria, record fields, and allowed status values across groups. Split discovery by lead or source, assign detailed verification by person or account, and reuse existing evidence. When groups keep separate records, confirm that the first record from each group merges into the shared format.

## Decide what to do next based on the evidence

- **Check eligibility and Fit first.** Start with requirements most likely to block inclusion and assess the match against the task-specific rubric. Cite the same source when it supports multiple findings. Mark a candidate ineligible when evidence contradicts a hard requirement. Mark the relevant requirement Unverified when attribution is unclear, key evidence is missing, or sources conflict, and state the gap.
- **Check Intent once Fit is established.** Look for recent signals relevant to the task's next action. Verify any Intent signal the user makes a hard requirement before counting the candidate as eligible.
- **Complete the candidate profile.** Use the evidence from Fit and Intent to summarize the candidate. Add facts that could change comparison or follow-up. Use the [profile evidence guidance](references/qualify.md#when-to-enrich-candidate-profiles) to decide whether to gather more evidence or record an open question.
- **Check professional profiles and contact channels.** Use the default profile mode of `contact_enrich` when identity, responsibilities, or organization still need verification. When contact channels are needed, start with an existing public professional channel and look up a work email separately when needed. See [Professional profiles and work email](references/tool-evidence.md#professional-profiles-and-work-email). If contact information is a hard requirement, verify eligibility against it. Outreach requires explicit user authorization.
- **Decide when to finish.** For a fixed count or an enumerable scope, verify candidates against the user's requirements. For open-ended searches, assess whether new candidates could change the recommendations or add distinct options, and whether credible sources remain for key gaps. When the user wants a larger list, check whether a new source could still yield qualified candidates.

## Deliver from candidate records

- **Decide whether to deliver an interim shortlist.** Follow the user's delivery instructions. When none are given, use the purpose of the task to decide whether a partial result independently supports a next step. For candidate-pool expansion or tasks where screening can begin while research continues, share an initial batch once enough evidence supports the candidates and state what the batch covers. When the decision depends on a full comparison, complete coverage, or resolving a unique identity, consolidate the verified results before delivering them.
- In tables and reports, use **Fit as a whole-number percentage** and **Intent as High, Medium, or Low** as the two assessment columns. Include the rationale and evidence for each. Use Unverified for insufficient evidence of intent and Not applicable when intent is irrelevant. Preserve eligibility, key profile details, and follow-up items. Include public contact channels, their ownership, and verification status where relevant. Store Fit as a sortable numeric percentage. When sorting by Intent level, use High, Medium, Low.
- Generate, sort, and consolidate deliverables from the same candidate records, including previously delivered batches in the final result. Check format, visibility, deduplication, counts, links between assessments and evidence, and deliverable usability against the requirements recorded at the start. Deliver the finished output once validated. If the complete list is a file, give a summary and link in chat. When the user asks to see the full list in chat, reuse the generated content. Label any excerpt from a long list as a preview.
- When coverage is limited, deliver verified results and state the scope searched and facts that still lack evidence. Claim completeness only for an enumerable scope that has been fully covered.
