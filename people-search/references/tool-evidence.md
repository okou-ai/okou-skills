# Tool Reference

Use this reference for platform-specific tools, parameters, or saved jobs. Use only enabled Okou-managed data tools and inputs exposed by the current `okou data describe <tool>` schema; do not import provider-native parameters into a managed-tool request.

## Platform tools

| Platform | Discover and read content | Additional information |
| --- | --- | --- |
| YouTube | `youtube_search`, `youtube_videos` | `youtube_channel_stats`, `youtube_stats`, `youtube_transcript`. |
| TikTok | `tiktok_search`, `tiktok_hashtag_search`, `tiktok_channel_videos` | `tiktok_channel_stats`, `tiktok_stats`, `tiktok_transcript`. |
| Instagram | `creator_search` for indexed accounts; `instagram_reels_search`, `instagram_channel_posts`, `instagram_channel_reels` for content | Search accounts by `handle`, `name`, or `bio`; this is not cross-platform creator search. Read metrics or speech with `instagram_channel_stats`, `instagram_stats`, `instagram_transcript`. |
| Podcasts | `podcast_search` | Search show metadata by name, with optional language and topic. Verify hosts or guests in named episode or show sources; no transcripts are returned. |
| LinkedIn | `linkedin_profile`, `linkedin_company`, `linkedin_post`, `linkedin_company_posts` | `linkedin_transcript` when available. |
| X/Twitter | General social-data route; for known URLs, `twitter_profile`, `twitter_tweets`, `twitter_tweet`, `twitter_thread` | `twitter_transcript` when available. |
| Facebook | General social-data route | `facebook_stats`, `facebook_channel_stats`, `facebook_transcript`. |
| Xiaohongshu, Douyin, Weibo, WeChat Official Accounts, Threads | `social_data_quote` → `social_data_create`, with the search or reading operation for the selected platform | Supported operations vary by platform; check the current description. |

General social-data search example: `{"platform":"xiaohongshu","operation":"search","query":"<topic>","limit":10}`. Use `query` for search and `url` to read known content. Do not assume all platforms support the same operations.

## Professional profiles and email

- `people_search_structured` requires at least one of `titles`, `companyNames`, `companyDomains`, `countries`, or `skills`. Filters use exact matches after lowercase normalization, with OR within one field and AND across fields. Title and employer filters concern current employment; country concerns the person's profile location, not company headquarters, and uses full country names rather than country codes. Requested fields include work history and education, but these are not exposed as search filters; there is no semantic `query` input.
- For another structured-search page, repeat the same filters and pass the returned `scroll_token` as `scrollToken`. Every returned record is chargeable; each explicit next-page request buys another page.
- `contact_search` previews may mask names; `has_email` does not mean an email has been retrieved. Explicitly use a selected ID with `contact_enrich` when a full profile is needed; do not silently enrich every discovered result.
- Extract public professional contacts from papers, personal pages, or organization pages already read into each person's contact line, retaining the source. If a paper already provides the email, neither repeat a paid lookup nor leave only the paper link as the contact.
- For a separate work-email lookup, use `contact_enrich` with `fields: ["work-email"]`; default mode only enriches the profile. Use the person's name and verified current employer domain. This mode does not retrieve phone numbers or private email addresses. Do not guess addresses. Actual outreach requires user authorization.

## Public web search and page extraction

- `web_search` accepts `query`, optional `limit` (default 5, maximum 10), `recency` (`hour`, `day`, `week`, `month`, or `year`), and `domains` (up to 20 allowed domains or subdomains, without protocols or paths). It searches public pages for both people and supporting sources, not a structured professional-record database. No pagination or provider-native search-mode controls are exposed.
- `web_contents` accepts only `urls`, reading full text and source metadata for 1–20 distinct public URLs per batch. Do not pass provider-native content, summary, or freshness options that its schema does not expose. Check the status and content returned for each URL.

## Saved jobs and media

Use `social_download_create` only when footage is needed and the platform supports it.

| Submitted task | Read the result |
| --- | --- |
| Professional profile, contact, or company job that is still submitted | `company_contact_get` with `jobId`. |
| `web_contents` job that is still submitted | `web_contents_get` with `jobId`. |
| `social_data_create` | `social_data_get` with `jobId`. |
| `social_download_create` | `social_download_get` with `downloadId`. |

Read the existing job while it is running rather than resubmitting. Check the actual returned content and errors. If a source fails or is inaccessible, try another suitable source; explain any gap that remains.
