---
name: people-search
description: Find people or enrich existing lists, covering the requested scope as fully as possible. Deliver basic information, task-relevant profiles, and public professional contacts with sources, preferably as a Markdown table or XLSX file.
---

# People Search

Find relevant people across the user's scope, establish their basic information, and add task-relevant profiles and public professional contacts. Deliver a table that helps the user understand, compare, and contact them.

## Find people and establish basic information

Use the request and context to determine the search direction, scope, and number of people. For a broad request, start with relevant responsibilities, experience, or work without adding eligibility thresholds. Ask only when missing information would materially change the direction.

Choose a search entry point from the table below. When given a list, start by enriching those people; when asked for more, deduplicate against previous results.

Continue beyond the first batch. Cover relevant organizations, locations, descriptions of responsibilities, or platforms using complementary sources and queries. If results repeatedly return the same people, switch to an entry point that reaches a different pool. For a defined scope such as a team roster or event list, check each member. For an open-ended search, consolidate when the main relevant sources have been covered and further expansion yields few new people; state the coverage and remaining gaps.

| Situation | API | Purpose |
| --- | --- | --- |
| Known name or organization | `people_search` | Find profiles and establish identity and professional background. |
| Search by responsibilities, expertise, or experience | `people_search_semantic` | Describe the person in natural language to discover people across job titles. |
| Filter by a specific current role, company, country, or skill | `people_search_structured` | Select candidates from professional records. |
| Find relevant decision-makers at target companies | `contact_search` | Search contacts by company and responsibilities; if target companies are unclear, start with `company_search` and `company_profile`. |
| Find people through projects, papers, talks, or cases | `web_search` | Find original work, credits, and participants, and add relevant experience. |
| Read known pages | `web_scrape`, `web_contents` | Read one page or a batch to extract person-specific information and sources. |
| Read known LinkedIn profiles or updates | `linkedin_profile`, `linkedin_company`, `linkedin_post`, `linkedin_company_posts` | Add professional background, company context, or relevant updates. |
| Find creators on video or content platforms | `youtube_search`, `tiktok_search`, `instagram_reels_search` | Discover publishers through relevant content. |
| Search people or content on Xiaohongshu, Douyin, Weibo, and other platforms | `social_data_quote` → `social_data_create` | Search or read accounts and works on the selected platform. |
| Enrich a known person's professional profile | `contact_enrich` in default profile mode | Resolve identity, organization, role, and other profile details. |
| Find a work email | `contact_enrich` with `fields: ["work-email"]` | Look up a work email using the name and verified current employer domain. |
| Inspect a creator's work, performance, or video content | The platform's work, statistics, or transcript APIs; `social_download_create` when footage is needed | Add specific works, public metrics, or evidence from speech and footage. |

Use `okou data describe <tool>` for current parameters. Consult the [tool reference](references/tool-evidence.md) as needed for specific platform APIs and saved-job readers.

Basic information usually includes name or account, organization and role, and public profile links; add location when relevant. Resolve identities against sources to avoid combining different people's records.

## Build task-relevant profiles

Use the purpose of the search to identify professional information that helps the user understand and compare people. Select the relevant content from the six categories below, establish specific facts, and split them into table columns as useful.

| Profile content | What to learn |
| --- | --- |
| Professional role and responsibilities | In what role does the person work, and what do they usually take responsibility for? |
| Professional knowledge and skills | What relevant knowledge or skills are supported, and what is their scope? |
| Practical experience and personal contribution | What relevant work has the person done, and what did they personally undertake and complete? |
| Outcomes and performance | What work products, results, or observable performance did the work produce? |
| Business and working context | Whom does the work serve, and under what business, technical, or organizational conditions? |
| Professional collaboration | With whom has the person worked, in what relationship, and on what shared work? |

Add findings to the same person record and describe outcomes and limitations accurately. Keep sources for important facts; mark uncertain information for confirmation rather than guessing. Distinguish current roles from historical experience and personal contributions from team achievements. Inspect footage for visible actions; follower and view counts do not establish actual audience characteristics.

## Deliver a table

Use one row per person, with basic columns for **name or account, organization and role, profile link, contacts (phone, email, or another channel), and sources**.

Choose and split profile columns to suit the task and support comparison. Add fields such as location or work metrics when relevant.

Keep contacts in a separate column, listing the actual public professional contact details and whose channel they are. Extract contacts already present in sources into the table rather than substituting a paper or profile link. Note when none were found.

Prefer a Markdown table or XLSX file containing the complete list, ordered by relevance to the user's needs. Honor a requested result count; otherwise preserve all relevant people supported by facts rather than showing only the first few to keep the table short. Follow an explicitly requested format. Briefly explain any shortfall in people, coverage, or important information. Before delivery, check duplicates, key facts, and source links.
