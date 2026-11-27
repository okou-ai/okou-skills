---
name: people-search
description: >-
  Find people who meet the user's requirements across the requested scope, or enrich an existing list. Use complementary sources to expand coverage, support each match with evidence, and develop task-relevant profiles and public professional contacts for comparison and outreach.
---

# People Search

Help the user discover and understand people relevant to their goals. Bring together information from professional profiles, organizations, projects, publications, and other public sources to create a useful, source-backed list for comparison and outreach.

Discovery, fact-checking, and profile development work together throughout the research. Early leads guide further investigation; information about a person's work clarifies their relevance and can reveal additional people and sources. Use this growing understanding to expand coverage and develop the details that matter to the user.

## Understand the request

- **Scope the request**: Use the user's goal and context to determine the search direction, target profile, geography/industry, and desired count. For broad requests, start from core responsibilities, relevant experience, or representative work without adding arbitrary thresholds. Ask clarifying questions only when missing details would materially change the search direction.
- **Handle existing lists**: When given a list, prioritize enriching and verifying those individuals first. When asked to find more, deduplicate strictly against previous results.
- **Check tools first**: Run `okou data tools` to check availability and `okou data describe <tool>` to confirm supported parameters before use. Do not pass provider-native parameters that the schema does not expose. Consult the [tool reference](references/tool-evidence.md) for platform-specific tools, pagination, work-email lookups, and saved-job results.

## Discover people and develop coverage

Choose complementary sources and search entry points according to where evidence for the user's requirements can be found. Requirements about an organization can guide discovery of relevant organizations and the people responsible within them; requirements about personal experience can guide discovery through documented work and its contributors. Follow connections between people, organizations, responsibilities, projects, and publications to reach additional relevant groups and strengthen the evidence for each match.

- **Expand queries**: Run batched searches using title synonyms (including bilingual titles and common variations), adjacent subfields, and target company/organization lists.
- **Cross-channel entry points**:
  1. **Direct profile search**: Query structured or semantic professional databases directly.
  2. **Company-to-people**: Identify target organizations and domains via `company_search` or `company_profile`, then look up key role holders.
  3. **Work-to-people**: Use `web_search` or niche platforms to find papers, open-source repositories, talks, podcasts, industry articles, or award lists, then trace back to the authors and leads.
- **Maximize coverage and pagination**: When asked to "find all" or "find as many as possible," use the maximum supported page size and paginate (e.g., via `scrollToken` in `people_search_structured`) within the user's quantity, time, and cost limits. If an entry point repeatedly returns the same people, switch to another platform or search angle.

- **Coverage and consolidation**: For a defined population, such as a team roster or event speaker list, work through the full population. For an open-ended search, assess coverage across relevant groups and source pools by the additional people found who meet the user's requirements. A decline in new matches from one entry point can guide a move to other relevant sources or search angles. Consolidate when complementary searches yield few additional supported matches, considering the user's goals, requested scope and count, and actual time or resource constraints. Explain the coverage achieved and the gaps that remain.

| Next action | Recommended tool | Selection rule |
| --- | --- | --- |
| Find profiles or resolve identities from a natural-language brief | `people_search` / `people_search_semantic` | Use `people_search` for model-extracted profile fields with sources; use `people_search_semantic` for matching profile pages and semantic text search. |
| Filter professional records by exact criteria | `people_search_structured` / `contact_search` | Use `people_search_structured` for current title, employer, country, or skill filters. Use `contact_search` for seniority, company size/domain/location, or person-location filters (returns previews only, not unlocked contacts). |
| Discover people and public evidence across the web | `web_search` | Search personal sites, team directories, papers, projects, interviews, and case studies—not just professional databases. |
| Find people via niche platforms or podcasts | Platform tools in [tool reference](references/tool-evidence.md#platform-tools) | Search accounts by handle, name, or bio, or search content by topic to trace publishers. Podcast search returns shows rather than a guest directory; verify hosts/guests in episode sources. |
| Read known profiles or public pages | Matching platform readers / `web_contents` / `web_scrape` | Prefer platform-specific readers when available. Use `web_contents` for full text and metadata from 1–20 public URLs, or `web_scrape` to extract Markdown/links from a single page. |
| Add company context | `company_search` / `company_profile` | Use `company_profile` when the domain is known; otherwise use `company_search`. Company context does not substitute for an individual's work history or contribution. |
| Enrich a selected person's full profile | `contact_enrich` (default profile mode) | Pass a supported ID, LinkedIn URL, or name + employer domain. Enrich selected targets on demand rather than every discovery result automatically. |
| Look up a work email | `contact_enrich` (`fields: ["work-email"]`) | Pass the person's name + verified current employer domain. Retrieves work emails only—no personal emails or phone numbers. Never guess email formats. |

## Research people and build task-relevant profiles

Develop profiles from the information that helps the user understand and compare people. Begin with relevant leads and enrich the understanding of each person through their roles, experience, work, contributions, and organizational context. The information gathered supports both the profile and the assessment of how the person relates to the request; it can also open further discovery paths.

Choose the dimensions and depth needed for the user's decision. Balance continued discovery, evidence needed to establish whether promising candidates meet the user's requirements, and profile development according to the gaps that most affect the result. Reuse relevant organizational or project facts while verifying each person's connection, responsibilities, and contribution. Within the requested scope and count, retain people who meet the user's requirements even when some profile details remain unknown. Use those profile gaps to guide further research and make remaining limitations visible; profile completeness is not an additional requirement.

- **Identity and context**: Cross-check names or handles, organizations, profile links, and career history when connecting information across sources. Keep current roles and historical experience clear.
- **Relevance to the request**: Use the available facts to explain how each person relates to the user's needs, updating that assessment as more information becomes available. Distinguish the user's requirements from their preferences and make remaining uncertainty about each match visible.
- **Profile content**: Select and develop the professional information useful for the user's questions. Use concrete work and sources to show what the person knows, has done, and has contributed, together with the scope and limitations of that experience.
- **Per-person research record**: Keep the facts supporting each candidate's match to the user's requirements alongside the task-relevant profile facts, source URLs and relevant passages or locations, dates, attribution to the person, team, or organization, and open questions. Use these records to guide further research and prepare the delivered profiles.
- **Follow information gaps**: Read relevant source sections and use targeted follow-up queries to establish personal actions, observable outputs, and working context. Choose follow-ups by the missing facts that matter to the user's decision. A title, project name, or organization-level result alone does not establish a person's skills, actions, or outcomes.

| Profile dimension | What to capture |
| --- | --- |
| **Professional role and responsibilities** | The person's role, responsibilities, scope, and relevant dates, distinguishing current from historical work. |
| **Professional knowledge and skills** | Knowledge or skills supported by concrete work, how and where they were applied, and any supported limitations. |
| **Practical experience and personal contribution** | Specific projects or work episodes, the person's actions or ownership, and the circumstances and boundaries of their contribution. |
| **Outcomes and performance** | Concrete work products, actual service or process delivery, observed behavior, results or setbacks, with attribution and supported limits. Quantified gains or success claims are not required. |
| **Business and working context** | The organizational, business, technical, or operating conditions relevant to the request, such as the users, products, channels, systems, or workflows involved. |
| **Professional collaboration** | Relevant collaborators, co-authors, teams, or organizations, what they worked on together, and whether the relationship is personal or organizational. |

Organize these details into comparable fields suited to the task. Describe facts and outcomes accurately, distinguish personal contributions from team or organizational achievements, and make clear which information is established and which remains uncertain.

For large result sets, save complete tool responses locally and maintain a lightweight index for each candidate, including identity, sources, relevant information, open questions, and a full-record pointer. Work through the candidates in batches, reading full records as needed while preserving coverage of the whole result set.

**Facts and citations**:
- **Cite concrete facts**: Ground profile points in project names, dates, metrics, tangible outputs, or direct quotes rather than generic praise. Follower counts and views do not establish audience quality.
- **Include inline citations**: Follow key facts directly with brief evidence and a source link (preferring public pages that name the person) rather than dumping all links into the final column. Mark unverified details as "To be confirmed" instead of guessing.

## Public professional contacts

Follow a **public extraction first, targeted enrichment second** approach. Record the actual public work number, email address, or direct professional contact URL alongside its source. A personal LinkedIn profile can serve as a contact route; messaging availability may vary.

1. **Extract from public sources**: Pull published work phone numbers, professional emails, or official business/press contacts directly from papers (corresponding author sections), personal sites, GitHub profiles, company team pages, social bios, or press releases, keeping the source link. Check who owns each contact; label shared office, press, and agency channels as indirect.
2. **Targeted work-email enrichment**: If no public email is found for a high-relevance candidate (or when explicitly requested), use `contact_enrich` (`fields: ["work-email"]`) with their name and verified current employer domain.
3. **Reachable social/public channels**: Record public accounts suitable for professional outreach and clearly label channel ownership.
4. **Compliance and transparency**: Do not search for or guess private phone numbers or personal emails. If no valid contact is found, explicitly state "No public contact found."

**Priority public channels by audience**:

| Target audience | Priority public sources & reachable channels |
| --- | --- |
| **Executives / Business decision-makers** | LinkedIn, company team pages, conference/podcast speaker pages, `contact_enrich` (work email) |
| **Engineers / Developers** | GitHub profile with a published professional contact, personal blogs/sites, X/Twitter, LinkedIn |
| **Researchers / Academics** | University or lab pages, paper corresponding-author blocks, Google Scholar, personal academic sites, LinkedIn |
| **Creators / KOLs / Industry bloggers** | Business/partnership emails or agency contacts listed in primary platform bios (Xiaohongshu, Douyin, WeChat Official Accounts, YouTube, Instagram, etc.) |

## Deliver a useful, source-backed list

Present the people and the information needed to compare, assess, and contact them in a clear structure. Preserve the relevant people supported by facts across the requested scope, and explain how the evidence supports their relationship to the user's requirements.

- **Structure**: Use one row per person, ordered according to the user's needs and the relevance supported by the available information.
- **Core information**: Include name or handle, organization and role, location when relevant, profile links, task-relevant profile details, public professional contacts, and sources. Choose profile columns that support meaningful comparison for the task.
- **Profile delivery**: State the researched facts in the delivered material with citations. When a concise comparison table cannot carry the full profiles, include the supporting detail in the requested file or an accompanying attachment, with a clear pointer from each person. Preserve the information needed to understand their work, contribution, outcomes, and context when summarizing.
- **Contacts**: Keep contact details in a dedicated column, with the actual work phone, email, or professional contact URL and its ownership clearly identified.
- **Evidence and uncertainty**: Keep selection status separate from profile completeness. Distinguish supported matches from promising leads with unresolved selection requirements, and keep confirmed counts consistent. Show missing profile details for otherwise qualifying people without moving them out of the matching set solely for those gaps.
- **Format and scope**: Prefer a complete Markdown table or XLSX file, following any format and result count requested by the user. When no count is specified, retain the relevant, fact-backed people found across the research rather than shortening the list for presentation.
- **Coverage**: Briefly explain the scope covered, remaining gaps, and any material research or enrichment limitations.

**Pre-delivery check**:

- **Coverage and counts**: Reconcile the candidate records, supporting evidence, and delivered list with the user's requirements, scope, and count. Account for relevant people still awaiting evidence and for gaps in source coverage. Ensure people who meet the user's requirements have not been lost while enriching, batching, or summarizing their profiles.
- **Profile completeness**: For each delivered person, compare the task-relevant dimensions and recorded facts with what the user will actually receive in the answer or attachment. Follow up on material gaps within the task's constraints and explicitly describe what remains unknown. A source link alone does not deliver the facts contained in that source.
- **Evidence and attribution**: Check that the delivered claims have working supporting links, preserve relevant dates and limitations, and distinguish personal contributions from team or organizational results.
- **Delivery integrity**: Remove duplicates, confirm contacts are in their own column, keep counts consistent with selection status, and briefly note **coverage, key gaps, or enrichment shortfalls** after the table.
