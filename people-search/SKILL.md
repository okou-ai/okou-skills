---
name: people-search
description: >-
  Find people who meet the user's requirements across the requested scope, or enrich an existing list. Use complementary sources to expand coverage, support each match with evidence, and develop task-relevant profiles and public professional contacts for comparison and outreach.
---

# People Search

Find the people who meet the user's requirements, as many as public evidence supports. Show the evidence for each person, and add the profile details and public contacts the user needs to compare and reach them.

## How to work

1. **Plan the search.** Read the user's goal, hard requirements, preferences, scope and count. List the directions where matching people can be found: role titles and synonyms (including other languages), target organizations, projects, publications or cases, platforms, and regions. If the user gives a list, verify and enrich those people first; when asked for more, exclude people already delivered. Ask a question only when missing details would change the search materially.
2. **Search and skim.** Work through each direction with the matching tool below. Skim titles, links and snippets first, and open full pages only for promising results.
3. **Confirm and record.** Count a person only when public evidence shows each hard requirement is met, including requirements about their organization, such as which processes its systems cover; a title, keyword or project announcement alone is not enough. Keep the link, a short quote, and the profile facts from the same page. Write each confirmed person to `people.md` as soon as you have them, and anyone with a requirement still unconfirmed as a lead with what is missing.
4. **Keep going.** Use what you learn, such as co-authors, teammates and related organizations, to open new directions. Paid search tools bill per returned record, so request about 10 records first and page further only while the results stay relevant. Continue until every direction is covered or new searches mostly return people already in `people.md`, within the user's count, time and cost limits.
5. **Deliver from `people.md`.** Keep every confirmed person unless the user set a count.

## Tools

Run `okou data tools` and `okou data describe <tool>` before using a tool, and pass only the parameters its schema exposes. Platform tools, pagination, saved jobs and email lookups are covered in the [tool reference](references/tool-evidence.md).

| To | Use | How |
| --- | --- | --- |
| Find people from a description | `people_search`, `people_search_semantic` | `people_search` returns extracted profile fields with sources; `people_search_semantic` returns matching profile pages and text. |
| Filter people by exact criteria | `people_search_structured`, `contact_search` | `people_search_structured` filters current title, employer, country or skill, bills per returned record and pages with `scrollToken`; `contact_search` filters seniority, company size, domain or location and returns previews only. |
| Find people through their work | `web_search` | Search team pages, personal sites, papers, repositories, talks, interviews and case studies, then trace the work to the people behind it. |
| Find people on social or niche platforms | Platform tools in the [tool reference](references/tool-evidence.md#platform-tools) | Search accounts by handle, name or bio, or content by topic. Podcast search returns shows; confirm hosts and guests in episode sources. |
| Read a profile or page | Platform readers such as `linkedin_profile`, `web_contents`, `web_scrape` | Prefer platform readers. `web_contents` reads 1–20 URLs; `web_scrape` extracts one page. |
| Find organizations | `company_search`, `company_profile` | Use `company_profile` when the domain is known. Company facts do not prove a person's own work. |
| Enrich a selected person | `contact_enrich` | Default mode returns a full profile from an ID, LinkedIn URL, or name plus employer domain. Use it for selected people, not every result. |
| Find a work email | `contact_enrich` with `fields: ["work-email"]` | Needs the name and verified current employer domain. Returns work emails only. |

## Profiles

Research the profile details that matter for this request and this person instead of filling a fixed template, for example their role and scope, the specific work they did, its outcomes, and the context they worked in. Read each recommended person's main source in full, and look for one source in their own words, such as an interview, talk or post. Write the specifics you read, with links, rather than labels: steps, prices, timelines, test methods and results, modules or transactions handled, and who they worked with. Separate personal contributions from team or company results, keep current and past roles distinct, and mark what is unconfirmed. Missing profile details do not remove a person who meets the requirements.

## Contacts

Take published professional contacts first: emails or phone numbers on papers, personal or team pages, GitHub and company pages, or business contacts in platform bios. Record the source, and label shared, press or agency channels as indirect. Look up a work email with `contact_enrich` only for selected people without a public one. Never guess an email or look for personal phone numbers or emails; write "No public contact found" when there is none.

## Deliver

- Use the format the user asks for. Otherwise give a numbered list ordered by relevance to the user's goal, one entry per person with labeled lines: role and organization, evidence for each requirement, profile, sources, and contact. A table may summarize the list but must not replace these entries; put a long list in an attached Markdown file.
- List unconfirmed leads separately with what is missing, and note the coverage reached and the remaining gaps.
- Before delivering, check that everyone confirmed in `people.md` is in the list, the counts match, and each key claim has a working link.
