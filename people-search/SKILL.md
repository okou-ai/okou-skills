---
name: people-search
description: Find people or enrich existing lists, covering the requested scope as fully as possible. Deliver basic information, task-relevant profiles, and public professional contacts with sources, preferably as a Markdown table or XLSX file.
---

# People Search

Find relevant people across the user's scope, establish their basic information, and add task-relevant profiles and public professional contacts. Deliver a table that helps the user understand, compare, and contact them.

## Find people and establish basic information

Use the request and context to determine the search direction, scope, and number of people. For a broad request, start with relevant responsibilities, experience, or work without adding eligibility thresholds. Ask only when missing information would materially change the direction.

Choose enabled Okou data tools for the information currently missing. Their coverage overlaps: select by source, supported inputs, and returned format, not a mandatory sequence or a requirement to use every matching tool. Use known URLs or selected records directly and reuse sufficient information already returned. Run `okou data tools` to check availability and `okou data describe <tool>` for supported inputs before use. When given a list, start by enriching those people; when asked for more, deduplicate against previous results.

For explicit requests to "find all" or "find as many as possible," prefer the selected discovery tool's maximum supported result or page size, subject to the user's quantity, time, and cost limits. Use only supported size controls; reaching the limit does not establish complete coverage or replace deduplication and verification.

Continue beyond the first batch. Cover relevant organizations, locations, descriptions of responsibilities, or platforms using complementary sources and queries. If results repeatedly return the same people, switch to an entry point that reaches a different pool. For a defined scope such as a team roster or event list, check each member. For an open-ended search, consolidate when the main relevant sources have been covered and further expansion yields few new people; state the coverage and remaining gaps.

| Next action | Tool choice | Selection rule |
| --- | --- | --- |
| Find professional profiles or resolve an identity from a text brief | `people_search` or `people_search_semantic` | Both accept natural-language briefs. Choose `people_search` for model-extracted profile fields with sources; choose `people_search_semantic` for matching profile pages and extracted text. |
| Find professional records or prospects using filters | `people_search_structured` or `contact_search` | Choose `people_search_structured` for exact current title/employer, profile-country, or skill filters and professional records. Choose `contact_search` for title/seniority, person-location, employer-domain, company-location, or company-size filters; it returns previews, not revealed contacts. |
| Discover people and sources across the public web | `web_search` | Search for people or public pages such as personal sites, rosters, projects, papers, talks, interviews, and cases. Use it for public-page discovery, not only professional-profile records. |
| Find people through a specific platform or podcasts | Account, content, or show search in the [platform table](references/tool-evidence.md#platform-tools) | Search accounts by handle, name, or bio when supported; search content by topic or work and follow its publisher. Podcast search returns shows, not a guest directory. Select the route for the platform and operation needed. |
| Read a known profile, page, or piece of work | Platform readers in the [platform table](references/tool-evidence.md#platform-tools); `web_contents` or `web_scrape` for accessible public pages | Prefer a matching platform reader when its supported output fits the need. `web_contents` reads full text and metadata from 1–20 known public URLs; `web_scrape` extracts Markdown or links from one known public page. |
| Add company context | `company_search` or `company_profile` | Use `company_search` to discover companies by supported criteria; use `company_profile` when the company domain is already known. Company context is not a person's work history or contribution. |
| Explicitly fill a selected person's professional profile | `contact_enrich` in default profile mode | Use a supported ID, LinkedIn URL, or name plus employer domain. Enrich the selected person, not every discovery result automatically; this is distinct from a work-email lookup. |
| Explicitly look up a person's work email | `contact_enrich` with `fields: ["work-email"]` | Use name plus current employer domain for the requested lookup. Reuse public professional contacts already found; do not guess addresses. No phone numbers or private email addresses are retrieved. |

Consult the [tool reference](references/tool-evidence.md) as needed for platform-specific tools, result limits, supported pagination, and saved-job readers.

Basic information usually includes name or account, organization and role, and public profile links; add location when relevant. Resolve identities against sources to avoid combining different people's records.

## Handle large result files

Keep candidate coverage separate from how much text is read into context at once. When results are too large for one read or file:

- Preserve the complete returned response locally, including full text and source metadata. Do not load the whole response into context; note any upstream truncation.
- Build a compact index covering every candidate: stable ID, name, source URL, task-relevant evidence excerpts, missing evidence, and the saved full-record location.
- Review the entire index in manageable batches and use IDs to read saved full records for verification as needed. Keep missing evidence unverified, not disqualified. Do not replace full coverage with the first few candidates or fixed-length text prefixes.
- If file-size limits require splitting, write candidate-aligned JSONL volumes with a manifest of file names, IDs, and counts; check that no record is lost. Preserve the user's delivery format and complete verified list, making raw files or archives available when useful. Compression reduces transfer size, not search charges or decompressed context size.

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
