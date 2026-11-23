# Tool Reference

Use this reference for specific platforms, parameters, or saved jobs. Follow the current `okou data describe <tool>` output.

## Platform APIs

| Platform | Discover and read content | Additional information |
| --- | --- | --- |
| YouTube | `youtube_search`, `youtube_videos` | `youtube_channel_stats`, `youtube_stats`, `youtube_transcript`. |
| TikTok | `tiktok_search`, `tiktok_hashtag_search`, `tiktok_channel_videos` | `tiktok_channel_stats`, `tiktok_stats`, `tiktok_transcript`. |
| Instagram | `instagram_reels_search`, `instagram_channel_posts`, `instagram_channel_reels` | `instagram_channel_stats`, `instagram_stats`, `instagram_transcript`. |
| LinkedIn | `linkedin_profile`, `linkedin_company`, `linkedin_post`, `linkedin_company_posts` | `linkedin_transcript` when available. |
| X/Twitter | General social-data route; for known URLs, `twitter_profile`, `twitter_tweets`, `twitter_tweet`, `twitter_thread` | `twitter_transcript` when available. |
| Facebook | General social-data route | `facebook_stats`, `facebook_channel_stats`, `facebook_transcript`. |
| Xiaohongshu, Douyin, Weibo, WeChat Official Accounts, Threads | `social_data_quote` → `social_data_create`, with the search or reading operation for the selected platform | Supported operations vary by platform; check the current description. |

General social-data search example: `{"platform":"xiaohongshu","operation":"search","query":"<topic>","limit":10}`. Use `query` for search and `url` to read known content. Do not assume all platforms support the same operations.

## Professional profiles and email

- `people_search_structured` filters titles and employers by current employment. Values within one field are OR; different fields are AND. For another page, repeat the same filters and pass the returned `scroll_token` as `scrollToken`.
- `contact_search` previews may mask names; `has_email` does not mean an email has been retrieved. Use a selected ID with `contact_enrich` when a full profile is needed.
- Extract public professional contacts from papers, personal pages, or organization pages already read into the final table's Contacts column, retaining the source. If a paper already provides the email, neither repeat a paid lookup nor leave only the paper link in the table.
- For a separate work-email lookup, use `contact_enrich` with `fields: ["work-email"]`; default mode only enriches the profile. Do not guess addresses. Actual outreach requires user authorization.
- `web_contents` can read 1–20 distinct public URLs in a batch.

## Saved jobs and media

| Submitted task | Read the result |
| --- | --- |
| Professional profile, contact, or company query | `company_contact_get` with `jobId`. |
| `web_contents` | `web_contents_get` with `jobId`. |
| `social_data_create` | `social_data_get` with `jobId`. |
| `social_download_create` | `social_download_get` with `downloadId`. |

Read the existing job while it is running rather than resubmitting. Check the actual returned content and errors. If a source fails or is inaccessible, try another suitable source; explain any gap that remains.
