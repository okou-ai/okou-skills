# People Search Examples

These are illustrations of the research method, not completed searches or a
required evaluation framework. Candidate labels are fictional. Adapt channels,
verification depth, and presentation to the actual request.

## Managed tool usage

Discover the relevant tools in the current runtime:

```bash
okou data tools --family company-contacts
okou data tools --family web-search
okou data tools --family web-extraction
```

If these names are returned, read their current schemas before calling:

```bash
okou data describe people_search
okou data describe web_search
okou data describe web_scrape
```

These requests illustrate the corresponding schemas at authoring time:

```bash
okou data call people_search --input '{"query":"Customer onboarding specialists and workshop facilitators"}'
okou data call web_search --input '{"query":"customer onboarding workshop facilitator case study","limit":10}'
```

For a source URL actually found in the results, replace the placeholder first:

```bash
okou data call web_scrape --input '{"url":"https://<source-domain>/<source-page>","format":"markdown"}'
```

Calls can incur provider charges; do not run them merely to validate installation.
Use the current schemas, not guessed extensions to an example. At authoring time,
`people_search` accepts `query`, not `limit`, `page`, or `cursor`. The `web_search`
limit bounds one response's URLs, not the number of people in the final answer.
Follow returned continuation instructions and any required approval.

## Discover, verify, and expand

**Example request:** Find people who could help a team improve customer onboarding.

1. Search several relevant channels, such as practitioner profiles, specialist
   firms, published workshops, and case studies. Do not assume one database or
   event roster contains everyone worth considering.
2. Open original project writeups, professional sites, and workshop materials
   to understand what each person actually did. Let the user's question decide
   which details are worth following up; do not invent a scoring rubric.
3. Merge duplicate profiles and incorporate supported findings into the answer.
   Explain each person's relevance in the amount of detail the user needs.
4. If broader coverage is needed and another channel keeps yielding relevant
   people, continue. Otherwise close proportionately to the requested scope,
   noting any material gaps rather than claiming exhaustiveness.

## Gaps and identity

- **A profile lists a broad title but not the relevant work:** Search project
  materials or an attributable professional site for the missing detail. Do not
  infer specific experience from the title alone. If it remains unknown, say so.
- **An event page is only an announcement:** Look for a recording, post-event
  account, or other appropriate evidence before saying the person delivered it.
- **Two profiles share a name:** Keep them separate until sources connect their
  identities; do not combine their experience.
- **The same person appears in three sources:** Merge the records and preserve
  useful evidence. Three records do not mean three people.
- **A fact is already clearly supported:** Use the evidence rather than repeatedly
  searching for reassurance. Other useful discovery can still continue.

## Expansion and delivery decisions

- **A bounded API response has been read:** Follow supported, authorized
  continuation or use materially different queries and channels. Do not invent
  pagination or treat the response as the entire relevant population.
- **A source fails or requires login:** Use an appropriate authorized alternative.
  Report a material remaining gap; a failure does not prove nobody else exists.
- **New channels keep yielding relevant people and the user wants more:** Keep
  expanding within the authorized scope and resources; do not impose an arbitrary
  small shortlist.
- **Useful channels have been covered and repeated expansions add little:** Resolve
  or describe material unfinished questions, then deliver. Do not manufacture a
  coverage percentage or a claim of universal completeness.
- **The task is bounded or the actual time/spending limit is reached:** Respect
  that boundary and explain material unfinished work rather than extending the
  task indefinitely or claiming saturation.
- **A follow-up verifies a new person or fact:** Incorporate it into the updated
  result, deduplicating against earlier findings. Do not merely say it should
  be added or force the user to ask again.
