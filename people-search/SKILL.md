---
name: people-search
description: Find people or enrich existing lists, covering the requested scope as fully as possible. Deliver basic information, task-relevant profiles, and public professional contacts with sources, preferably as a Markdown table or XLSX file.
---

# People Search

Find relevant people across the user's scope, establish their basic information, and add task-relevant profiles and public professional contacts. Deliver a table that helps the user understand, compare, and contact them.

## Find people and establish basic information

Use the request and context to determine the search direction, scope, and number of people. For a broad request, start with relevant responsibilities, experience, or work without adding eligibility thresholds. Ask only when missing information would materially change the direction.

Choose enabled Okou data tools by the evidence needed. These are task-relevant entry points, not provider-native endpoints or a mandatory all-tools pipeline. Run `okou data tools` to check availability and `okou data describe <tool>` for supported inputs before use. When given a list, start by enriching those people; when asked for more, deduplicate against previous results.

Continue beyond the first batch. Cover relevant organizations, locations, descriptions of responsibilities, or platforms using complementary sources and queries. If results repeatedly return the same people, switch to an entry point that reaches a different pool. For a defined scope such as a team roster or event list, check each member. For an open-ended search, consolidate when the main relevant sources have been covered and further expansion yields few new people; state the coverage and remaining gaps.

| Situation | Okou data tool | Use and limits |
| --- | --- | --- |
| Discover professional profiles or resolve a person's identity | `people_search` | Search by identity, role, employer, education, skill, or location using a natural-language query. Use source-backed profiles as leads; verify model-extracted fields. |
| Describe responsibilities, expertise, or experience in natural language | `people_search_semantic` | Discover semantically relevant professional profile pages and source text across job titles. Results are leads, not verified biographies or a complete candidate pool. |
| Filter professional records by exact current title, employer, profile-country, or skill | `people_search_structured` | Match supported fields exactly, with OR within a filter and AND across filters. Title and employer filters concern current employment; country concerns the person's profile location, not company headquarters. Requested fields also include work history and education, but these are not exposed as search filters. |
| Identify target companies or establish company context | `company_search`, `company_profile` | Discover companies from supported name, domain, location, size, or keyword criteria; resolve a known domain for company details. Use the results to guide people searches, not as evidence of an individual's role or contribution. |
| Find professional prospects at target companies | `contact_search` | Search by supported title, seniority, location, and employer criteria. Results are previews, not revealed contacts; matching a title does not establish decision-making authority. |
| Discover people and supporting sources across the public web | `web_search` | Search public pages for people, rosters, personal sites, projects, papers, talks, interviews, or cases. Supports query, result-count, recency, and domain filters; use dedicated professional-record or social tools when those sources are needed. |
| Read known public source pages | `web_scrape`, `web_contents` | Extract Markdown or links from one URL with `web_scrape`, or full text and source metadata from 1–20 supplied URLs with `web_contents`. Reuse sufficient text already returned. |
| Read known LinkedIn profiles, company pages, or posts | `linkedin_profile`, `linkedin_company`, `linkedin_post`, `linkedin_company_posts` | Read public member details, company context, individual posts, or recent company posts from known URLs. Company-level information alone does not verify an individual's responsibilities. |
| Discover indexed Instagram creator accounts | `creator_search` | Search by handle, display name, or bio. Returns basic public profile information, not a cross-platform creator search or private contact enrichment. |
| Discover creators through relevant videos or Reels | `youtube_search`, `tiktok_search`, `instagram_reels_search` | Search public content and follow its publisher to the relevant account. Content search is not an exhaustive account directory; verify authorship and task relevance. |
| Find relevant podcast shows as leads to people | `podcast_search` | Search show metadata by name, with optional language and topic. Verify hosts or guests in named episode or show sources; the tool does not supply transcripts or establish a complete guest list. |
| Search or read public accounts and content on Xiaohongshu, Douyin, Weibo, or other supported social platforms | `social_data_quote` → `social_data_create` | Quote one bounded platform operation, then submit it. Check support for the requested platform and operation; do not assume every platform supports account search, content search, or the same inputs. |
| Explicitly enrich a selected person's professional profile | `contact_enrich` in default profile mode | Resolve one selected person using a supported ID, LinkedIn URL, or name plus employer domain. Do not silently enrich every discovered result or treat profile enrichment as a work-email lookup. |
| Explicitly look up a person's work email | `contact_enrich` with `fields: ["work-email"]` | Use the person's name and verified current employer domain when a work-email lookup is requested. Reuse public professional contacts already found; do not guess addresses. This mode does not retrieve phone numbers or private email addresses. |
| Inspect specific work, public metrics, transcripts, or visible actions | Platform-specific content, statistics, or transcript tools; `social_download_create` when footage is needed | Follow the tool reference for supported platform tools. Use transcripts for spoken content and inspect footage for visible actions; download only when needed and supported. |

Consult the [tool reference](references/tool-evidence.md) as needed for platform-specific tools, result limits, supported pagination, and saved-job readers.

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

Choose and split profile columns to suit the task and support comparison. Add fields such as location or work metrics when relevant. Write profile fields as specific facts such as projects, dates, and numbers. Follow each key fact with a short quote and its link rather than relying on the sources column. Prefer public pages that name the person.

Keep contacts in a separate column, listing the actual public professional contact details and whose channel they are. Extract contacts already present in sources into the table rather than substituting a paper or profile link. Note when none were found.

Prefer a Markdown table or XLSX file containing the complete list, ordered by relevance to the user's needs. Honor a requested result count; otherwise preserve all relevant people supported by facts rather than showing only the first few to keep the table short. Follow an explicitly requested format. Briefly explain any shortfall in people, coverage, or important information. Before delivery, check duplicates, key facts, and source links.
