# People Search Examples

These are instructional cases, not completed searches or measured benchmark
results. Candidate labels below are fictional. Read the case relevant to the
current task rather than treating every example as a required search channel.

## Managed tool usage

Start with discovery, then describe only relevant tools returned by that runtime:

```bash
okou data tools --family company-contacts
okou data tools --family web-search
okou data tools --family web-extraction
```

If the following names are returned, read their current schemas before calling:

```bash
okou data describe people_search
okou data describe web_search
okou data describe web_scrape
```

Example requests matching those tools' schemas at authoring time:

```bash
okou data call people_search --input '{"query":"Web accessibility instructors who teach developer workshops"}'
okou data call web_search --input '{"query":"web accessibility developer workshop instructor course syllabus","limit":10}'
```

For a source URL actually found in the results, replace the placeholder before
calling page extraction:

```bash
okou data call web_scrape --input '{"url":"https://<source-domain>/<source-page>","format":"markdown"}'
```

Calls can incur provider charges. These are usage examples, not commands to run
merely to validate installation. Re-describe tools after a schema change; never
infer extra fields from an example. For instance, the `people_search` schema at
authoring time accepts a `query`, not a `limit`, `page`, or `cursor`. The
`web_search` limit bounds one response's URLs, not the final number of people.
Read any returned continuation instructions before requesting more data.

## Open-ended instructor search

**Request:** Find as many instructors as possible who have actually taught an
English Web accessibility course or workshop. Its public syllabus must cover
keyboard operation, screen readers, and implementation or remediation. Prefer
form or interactive-component exercises. A published prerecorded course counts.

**Search shape:** Cover course platforms, accessibility-training organizations,
completed-workshop archives, and independent instructors. Professional-profile
search can surface names, but profiles alone cannot prove syllabus coverage.
Use broad terms first, then search each promising instructor's missing criteria.
Do not add a live-private-training or direct-email requirement.

**Working example:**

| Round | Expansion | New unique candidates | Newly verified qualifiers | Next action |
| --- | --- | --- | --- | --- |
| 1 | Training organizations | 6 | 3 | Cover course platforms and historical workshops. |
| 2 | Course platforms | 7 | 4 | Continue; seven people now qualify. |
| 3 | Workshop archives | 4 | 0 | Check the four pending candidates, not an automatic stop. |
| 4 | Targeted syllabus checks | 0 | 2 | Merge the two qualifiers; nine people now qualify. |

The numbers illustrate the difference between discovery and verification, not
a required volume or round count. No saturation decision is supported yet while
independent-instructor coverage or promising evidence gaps remain. Deliver every
verified qualifier when the search legitimately closes, ranked by hands-on fit.

## Missing evidence, preferences, and identity

- **Instructor A:** A published course identifies the instructor, English
  delivery, keyboard and screen-reader work, and code-remediation exercises.
  There is no public email. Include in the main list; a missing supplementary
  contact is not disqualifying.
- **Instructor B:** An attributable syllabus covers keyboard and remediation but
  is silent on screen readers. Search the course lessons or published materials
  for that missing criterion. If still unresolved, list as a lead, not as a
  verified recommendation or a proven failure.
- **Instructor C:** Meets every hard requirement but has no documented form
  exercise. Keep eligible; use the preference when ranking.
- **Instructor D:** Appears only in a workshop announcement, even though the
  advertised date has passed. Find a completed-event record, published course,
  recording, or other credible delivery evidence before counting the person.
- **Two profiles named Alex Lee:** One proves teaching and the other lists an
  unrelated employer. Keep identities separate until attributable evidence
  connects them; do not combine their credentials to pass eligibility.
- **One instructor on three platforms:** Merge the records, retain useful source
  links, and count one person.

## Quantity and stopping decisions

- **"Recommend five speakers":** Research eligible alternatives, rank by the
  business objective, and return five if five qualify. Do not force a globally
  saturated search. If only three can be verified, return three and explain.
- **"At least five; as many as possible":** Five is a floor. Continue meaningful
  expansion while it yields new qualifiers; do not stop on reaching five.
- **API returns its maximum first batch:** Respect documented bounds. Continue
  with supported, authorized pagination or materially different queries and
  channels. Do not invent pagination, silently enrich previews, or describe the
  bounded response as the complete population.
- **A source requires login or fails:** Use a suitable authorized alternative.
  If it remains blocked, report the coverage gap; a source failure is not
  evidence that no more people qualify.
- **Main channels covered and repeated meaningful expansions add no qualifiers:**
  Resolve or label remaining promising gaps, then deliver with the actual scope.
  Do not claim universal completeness or a recall percentage.
- **An explicit spending limit is reached while new candidates remain:** Stop
  within that limit, preserve verified results, and state what remains
  unsearched or unverified. Do not claim saturation or spend beyond the limit.
- **A follow-up verifies another person:** Update the complete ranked list and
  its distinct-person count immediately; do not merely say "should be added."
