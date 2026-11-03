# Tool Examples

Use these names only if current discovery returns them; read their schemas first:

```bash
okou data describe people_search
okou data describe web_search
okou data describe web_scrape
```

Example requests:

```bash
okou data call people_search --input '{"query":"Customer onboarding specialists and workshop facilitators"}'
okou data call web_search --input '{"query":"customer onboarding workshop facilitator case study","limit":10}'
```

To read a source page found in the results, replace the URL placeholder first:

```bash
okou data call web_scrape --input '{"url":"https://<source-domain>/<source-page>","format":"markdown"}'
```

Calls can incur provider charges. These examples are not installation checks.
Follow current schemas and continuation rules: `people_search` may not expose
pagination, and a `web_search` result limit bounds URLs per call, not final people.
