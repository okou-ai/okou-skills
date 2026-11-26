---
name: people-search
description: Find relevant people or enrich existing lists with broad coverage, verified identities, public professional contacts, and task-relevant profiles. Deliver results as a Markdown table or XLSX file.
---

# People Search

Discover relevant people across the requested scope, verify their identities and relevance, extract or enrich public professional contacts, and build profiles that support comparison and outreach. Deliver the results in a structured table.

## 1. Define scope and search strategy

- **Scope the request**: Use the user's goal and context to determine the search direction, target profile, geography/industry, and desired count. For broad requests, start from core responsibilities, relevant experience, or representative work without adding arbitrary thresholds. Ask clarifying questions only when missing details would materially change the search direction.
- **Handle existing lists**: When given a list, prioritize enriching and verifying those individuals first. When asked to find more, deduplicate strictly against previous results.
- **Check tools first**: Run `okou data tools` to check availability and `okou data describe <tool>` to confirm supported parameters before use. Do not pass provider-native parameters that the schema does not expose.

## 2. Multi-source discovery: Ensure broad coverage

Do not stop after the first batch. Combine complementary sources based on where the target audience is active to avoid single-channel blind spots:

- **Expand queries**: Run batched searches using title synonyms (including bilingual titles and common variations), adjacent subfields, and target company/organization lists.
- **Cross-channel entry points**:
  1. **Direct profile search**: Query structured or semantic professional databases directly.
  2. **Company-to-people**: Identify target organizations and domains via `company_search` or `company_profile`, then look up key role holders.
  3. **Work-to-people**: Use `web_search` or niche platforms to find papers, open-source repositories, talks, podcasts, industry articles, or award lists, then trace back to the authors and leads.
- **Maximize coverage and pagination**: When asked to "find all" or "find as many as possible," use the maximum supported page size and paginate (e.g., via `scrollToken` in `people_search_structured`) within the user's quantity, time, and cost limits. If an entry point repeatedly returns the same people, switch to another platform or search angle.
- **Convergence and gaps**: For closed scopes (e.g., a team roster or event speaker list), verify every member. For open-ended searches, consolidate once primary sources are covered and new queries yield few fresh candidates; clearly note **coverage and remaining gaps** upon delivery.

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

## 3. Verify identities and deduplicate: Ensure accuracy

- **Identity resolution**: Before merging records from multiple sources, cross-check organization, profile links, or career history to confirm they belong to the same person and avoid combining different individuals with the same name.
- **Distinguish current vs. past roles**: Clearly separate current employment from historical experience. Note in the results if a profile shows someone has left a role or has not been updated in years.
- **Rank by relevance**: Prioritize candidates who strongly match the request and are backed by public facts. Check each mandatory criterion against available evidence. List useful leads with unresolved requirements separately as "To be confirmed" and exclude them from the confirmed count.
- **Batch-process large result sets**:
  - Save complete tool responses locally and build a lightweight index per candidate (ID, source, evidence/gaps, full-record pointer) instead of loading raw JSON into context.
  - Review all candidates in batches, reading full records by ID as needed rather than substituting the first N results for full coverage.

## 4. Contact discovery funnel: Ensure reachability

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

## 5. Build task-relevant profiles

For confirmed matches, extract profile details aligned with the user's goal and split them into comparable table columns as needed:

| Profile dimension | What to capture |
| --- | --- |
| **Match rationale & tags** | A one-sentence explanation of why they fit the request, plus core professional tags. |
| **Role & capability scope** | Current role, business/technical ownership, and evidenced core skills. |
| **Practical experience & personal contribution** | Representative projects, products, or research, specifying what the person personally owned (distinguishing personal contribution from team outcomes). |
| **Outcomes & impact** | Observable results, papers/patents, open-source projects, product milestones, or public talks. |
| **Business context & network** | Organizational, business, or technical context, plus key collaborators, co-authors, or institutional backing. |
| **Recent activity / Outreach hook** | Recent posts, new launches, talks, or public hiring/collaboration signals useful for breaking the ice. |

**Facts and citations**:
- **Cite concrete facts**: Ground profile points in project names, dates, metrics, tangible outputs, or direct quotes rather than generic praise. Follower counts and views do not establish audience quality.
- **Include inline citations**: Follow key facts directly with brief evidence and a source link (preferring public pages that name the person) rather than dumping all links into the final column. Mark unverified details as "To be confirmed" instead of guessing.

## 6. Delivery standards

- **Clear structure**: One row per person, ordered from highest to lowest relevance.
- **Core columns**: `Name / Handle`, `Organization & Role`, `Location (if relevant)`, `Profile Link`, `Contacts (dedicated column: actual work phone, email, or contact URL and ownership)`, `Match Rationale`, `Profile Details (split into 2–4 comparable columns by task)`, and `Sources`.
- **Output format**: Prefer a complete **Markdown table** or **XLSX file** (following any explicitly requested format). Honor a requested count; otherwise preserve all fact-backed relevant candidates rather than truncating the list for brevity.
- **Pre-delivery check**: Verify there are no duplicates, confirm contacts are extracted into their own column, ensure key facts include working source links, and briefly note **coverage, key gaps, or enrichment shortfalls** after the table.
