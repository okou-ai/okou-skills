# Tools and Evidence

Identify the fact you need to establish and check what the tool actually read. When a tool's capabilities or fields are unclear, check its current documentation and existing responses. Use a representative source to confirm behavior when needed.

| Material returned | What it can support |
| --- | --- |
| Search titles, snippets, and indexing dates | Candidate and source discovery. Verify hard requirements, attribution, and dates on the original publishing page. |
| Page text and public links | Check what the organization or person publicly states about responsibilities, terms, and contact channels. Inspect the link target when an email is behind a button. If the page refers to a team, look for a source that identifies the individual's responsibilities. |
| Account or work metadata | Confirm the account, work attribution, format, publication date, and public metrics supported by the returned fields. Record the platform, metric definition, and verification date. |
| Original posts, public updates, and disclosures | Verify who disclosed which collaboration, hiring, or purchasing action and when. Distinguish paid work, gifted products, affiliate promotion, and ordinary content. Assess Intent against the statement's scope and validity period. |
| Transcripts, captions, or generated summaries | Locate relevant segments and understand language and spoken content. A reliable timestamped transcript can verify wording. Mark visual claims based solely on a transcript as Unobserved. Treat audience descriptions in a summary as the apparent audience the content targets. |
| Original footage and audio | Verify on-camera presence, actions, and timestamps from the footage. To confirm who speaks a specified language, compare the footage with the audio or a reliable transcript for the same segment. Use the download receipt to retrieve the material, then inspect and cite the relevant segment. |
| Audience analytics with a defined scope | Verify actual audience characteristics for the platform and reporting period. Record follower or subscriber counts, self-reported location, the market the content targets, and actual audience geography separately. |

For conference speakers, search by event and topic, then use the agenda to verify the speaker, year, and type of participation. To fill a gap for a known person, search with their name, organization, and the fact to verify, using the local language when useful. If a transcript-only summary says a creator never demonstrated grinding coffee, mark the action Unobserved and check the original footage.

When an agenda, roster, or release note covers multiple people, extract the relevant entries in one pass and reuse the original source. Record the specific credit or passage for each person and distinguish the role, team result, and contribution attributable to the individual.

## Audio and video attribution and language

- Verify attribution on the original publishing page, the channel, or in the program credits. For team accounts and episodes with guests, confirm who speaks using the introduction, credits, audio, or footage for the segment before assessing what they explain.
- When verifying the original spoken language, prefer a caption or transcript tool that accepts a language parameter. Check the actual language and caption type returned. If you receive a translation, use original-language captions or audio as additional evidence. If attribution or original language remains unresolved, record the gap and move to a source that can answer it directly or to another candidate.

## Professional history search and contact previews

- **`people_search_structured`.** Returns professional histories. Title and employer filters apply to current roles. The country filter applies to the person's profile location. For historical work, verify the responsibilities and location in the relevant period and apply a current-role filter when the task calls for it. Different filter fields must all match. Within a field, any listed value can match. `skills: ["python", "sql"]` matches either skill, so verify both per person if the task requires both.
- **Professional history pagination.** Results are billed per record. To request the next page, keep the same filters and pass the previous page's `scroll_token` as `scrollToken`. The provider's total counts matches in its dataset. The task count reflects deduplicated, verified candidates.
- **`contact_search`.** Returns business contact previews that may include a partially masked name, a contact ID, and `has_email`. Use the ID to enrich selected contacts. `has_email` indicates the provider may have an email available. Perform a separate lookup to retrieve the actual work email.

## Professional profiles and work email

- **Enrich professional profiles.** When a gap in identity, responsibilities, or organization affects the decision, use the default profile mode of `contact_enrich`. Pass a `contact_search` result ID, a known LinkedIn profile URL, or a name and employer domain.
- **Look up work email.** Start with an appropriate public professional channel when the deliverable needs contact information. If a work email is needed, provide the person's name, their verified current employer's domain, and `fields: ["work-email"]`. Record the provider, who owns the channel, the verification result, and the verification date if available. Use source-backed work email addresses and limit contact lookups to public professional channels.

## Handle failed or partial results

- **Asynchronous submission.** When a call returns `submitted`, save the job ID and use the documented retrieval operation, such as `web_contents_get`. Check the provider status and actual returned material before recording evidence.
- **Missing or inaccessible results.** Distinguish invalid parameters, service errors, unavailable captions, and inaccessible footage. Choose an alternative source based on the missing fact. When the task allows it, use another work by the same person. Mark any remaining gap Unverified.
- **More pages available.** Record the sources and time period covered. Before assigning Low Intent, verify that the sources relevant to the task have been checked. Use Unverified when access problems leave too little evidence to assign a level.
