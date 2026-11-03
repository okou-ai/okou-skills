# Managed Data Tools

## Discover and inspect

Discover enabled tools:

```bash
okou data tools
```

Select relevant people/profile, web-search, or page-extraction tools from the
result. Read their current schemas before calling. If these names are returned:

```bash
okou data describe people_search
okou data describe web_search
okou data describe web_scrape
```

## Call documented fields

Use requests matching the current schema, for example:

```bash
okou data call people_search --input '{"query":"Customer onboarding specialists and workshop facilitators"}'
okou data call web_search --input '{"query":"customer onboarding workshop facilitator case study","limit":10}'
```

Replace the placeholder with a source URL actually found in the results:

```bash
okou data call web_scrape --input '{"url":"https://<source-domain>/<source-page>","format":"markdown"}'
```

## Continue safely

Treat result limits as per-call bounds, not complete population coverage.
Follow documented pagination and approval rules; expand queries or channels if
continuation is unsupported. Do not guess fields or replay ambiguous requests
that may already have executed. Read source pages before relying on extracted
profile fields or snippets. Keep private context out of public queries, follow
enrichment and access restrictions, and obtain authorization before outreach.
