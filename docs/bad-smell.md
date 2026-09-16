# SKILL.md Bad Smells

Common anti-patterns to avoid when writing SKILL.md documentation.

---


## 1. Useless `| jq .`

**Problem:** Using `| jq .` without any transformation only formats JSON but adds no value, making commands unnecessarily complex.

### ❌ Bad Case

```bash
curl -s -X POST "https://api.example.com/data" -H "Content-Type: application/json" -d @/tmp/request.json | jq .
```

**Issue:** The `| jq .` only pretty-prints the JSON without extracting or transforming any data.

### ✅ Good Case

**Option 1: Remove jq entirely**
```bash
curl -s -X POST "https://api.example.com/data" -H "Content-Type: application/json" -d @/tmp/request.json
```

**Option 2: Use jq for actual transformation**
```bash
curl -s -X POST "https://api.example.com/data" -H "Content-Type: application/json" -d @/tmp/request.json | jq '.data.items[] | {id, name}'
```

**When to keep jq:**
- ✅ Extracting specific fields: `| jq '.data.id'`
- ✅ Transforming structure: `| jq '.items[] | {name: .title}'`
- ✅ Filtering: `| jq '.[] | select(.active == true)'`
- ❌ Just formatting: `| jq .` (remove it)

---

## 2. Inline JSON in curl Commands

**Problem:** Constructing complex JSON directly in curl commands leads to escaping hell and makes examples hard to read and maintain.

### ❌ Bad Case

```bash
curl -X POST "https://api.example.com/sessions" -H "Content-Type: application/json" -d "{\"projectId\": \"${PROJECT_ID}\", \"browserSettings\": {\"context\": {\"id\": \"${CONTEXT_ID}\", \"persist\": true}}}"
```

**Issues:**
- Complex quote escaping: `\"`
- Hard to read nested JSON
- Difficult to maintain
- Error-prone when copying

### ✅ Good Case

**Write to file and reference it in curl**

Write to `/tmp/request.json`:

```json
{
  "projectId": "your-project-id",
  "browserSettings": {
    "context": {
      "id": "<your-context-id>",
      "persist": true
    }
  }
}
```

```bash
curl -X POST "https://api.example.com/sessions" -H "Content-Type: application/json" -d @/tmp/request.json
```

**Benefits:**
- ✅ Clean, readable JSON
- ✅ No escaping issues
- ✅ Easy to modify
- ✅ Works with any content (JSON, JS, form data)

**Alternative for URL-encoded data:**
```bash
# Write query.txt with: user_metadata['env']:'production'
curl -G "https://api.example.com/sessions" --data-urlencode "q@/tmp/query.txt"
```

---

## 3. Using $VAR for URL Parameters

**Problem:** Using shell variables like `$CONTEXT_ID` in URLs creates dependency on unstable variable expansion and makes examples harder to follow.

### When to Use `${VAR}` vs `<placeholder>`

| Type | Format | Example | Keep as Variable? |
|------|--------|---------|-------------------|
| **Prerequisites env vars** | `${VAR}` | `${API_KEY}`, `${API_TOKEN}`, `${DOMAIN}` | ✅ Yes |
| **Dynamic values from API** | `<placeholder>` | `<context-id>`, `<session-id>`, `<item-id>` | ❌ No, use placeholder |

**Keep as `${VAR}`** — Environment variables defined in the Prerequisites section:
- API tokens/keys: `${API_KEY}`, `${API_TOKEN}`, `${ACCESS_TOKEN}`
- Base URLs/domains: `${API_HOST}`, `${DOMAIN}`, `${BASE_URL}`
- Account identifiers: `${ACCOUNT_ID}`, `${ORG_ID}` (when set in Prerequisites)
- Credentials: `${EMAIL}`, `${USERNAME}` (when set in Prerequisites)

**Use `<placeholder>`** — Dynamic values obtained from previous API responses:
- Resource IDs: `<context-id>`, `<session-id>`, `<project-id>`
- Temporary tokens: `<upload-token>`, `<refresh-token>`
- User-specific values: `<your-item-id>`, `<your-file-key>`
- Any value returned from a previous API call that the user needs to copy

### ❌ Bad Case

**Example 1: Save Parameter**
```bash
CONTEXT_ID=$(curl -X POST "https://api.example.com/contexts" -H "X-API-Key: ${API_KEY}" -d '{"projectId": "proj123"}' | jq -r '.id')
```

**Example 2: Use Parameter**
```bash
curl -X POST "https://api.example.com/sessions" -H "X-API-Key: ${API_KEY}" -d "{\"contextId\": \"${CONTEXT_ID}\"}"
```

**Example 3: Use Parameter**
```bash
DATASET_ID="gd_xxxxx"

curl -s -X POST "https://api.brightdata.com/datasets/v3/trigger?dataset_id=${DATASET_ID}" --header "Authorization: Bearer ${BRIGHTDATA_API_KEY}" --header "Content-Type: application/json" -d @/tmp/brightdata_request.json
```

**Issues:**
- Requires setting shell variable between examples
- Variable expansion can fail
- Examples become interdependent
- Users must understand shell variable mechanics

### ✅ Good Case

**Example 1: Create context**
```bash
curl -X POST "https://api.example.com/contexts" -H "X-API-Key: ${API_KEY}" -d @/tmp/request.json
```

**Example 2: Use context**
Replace `<your-context-id>` with the actual context ID from the previous response:

```
{
    "id": "<your-context-id>",
}
```

```bash
curl -X POST "https://api.example.com/sessions" -H "X-API-Key: ${API_KEY}" -d @/tmp/request.json
```

Or more explicitly:

```bash
curl -X DELETE "https://api.example.com/contexts/<your-context-id>" -H "X-API-Key: ${API_KEY}"
```

**Example 3: Use Parameter**

Replace `<dataset-id>` with the actual dataset id.

```bash
curl -s -X POST "https://api.brightdata.com/datasets/v3/trigger?dataset_id=<dataset-id>" --header "Authorization: Bearer ${BRIGHTDATA_API_KEY}" --header "Content-Type: application/json" -d @/tmp/brightdata_request.json
```

**Documentation Pattern:**
Use clear placeholder text and instructions:

```markdown
### Delete Context

Delete a context when no longer needed. Replace `your-context-id` with the actual context ID:

```bash
curl -X DELETE "https://api.example.com/contexts/your-context-id" -H "X-API-Key: ${API_KEY}"
```

**Benefits:**
- ✅ Clear, self-contained examples
- ✅ No shell variable dependencies
- ✅ Easier for AI agents to parse and execute
- ✅ Works in any context

---

## 4. Inline JSON with -d Parameter

**Problem:** Using `-d '{"key": "value"}'` format for JSON data creates inconsistency with the file-based pattern and makes examples harder to maintain.

### ❌ Bad Case

```bash
curl -s -X POST '.../query' -d '{"page_size": 100}'
curl -s -X POST '.../query' -d '{"page_size": 100, "start_cursor": "abc123"}'
```

**Issues:**
- Inconsistent with file-based pattern used elsewhere
- Hard to modify for complex JSON
- Doesn't scale for nested structures
- Mixed patterns confuse users

### ✅ Good Case

**Write to `/tmp/notion_request.json`:**
```json
{
  "page_size": 100
}
```

```bash
curl -s -X POST "https://api.notion.com/v1/databases/<your-database-id>/query" --header "Authorization: Bearer $NOTION_TOKEN" --header "Notion-Version: 2022-06-28" --header "Content-Type: application/json" -d @/tmp/notion_request.json
```

**Benefits:**
- ✅ Consistent with file-based pattern across all skills
- ✅ Easy to modify and extend
- ✅ Works with any JSON complexity
- ✅ Clear separation of data and command
- ✅ Follows established pattern from other skills

**Pattern Rule:** Always use `-d @/tmp/filename.json` for JSON data, never inline JSON with `-d '{"key": "value"}'`.

---

## 5. Simple --data-urlencode Parameters

**Problem:** Using `--data-urlencode "key=value"` for simple parameters can cause escaping issues with special characters like `!`, `&`, `?`, etc., creating potential shell escaping nightmares.

### ❌ Bad Case

```bash
# Query with special characters can break
--data-urlencode "q=best restaurants! & cafes in NYC"
--data-urlencode "query=type:ticket status:open created<30"
--data-urlencode "url=https://example.com/path?param=value&other=123"
```

**Issues:**
- Special characters require shell escaping
- Complex URLs with query parameters break parsing
- Search queries with symbols cause failures
- Inconsistent with file-based patterns

### ✅ Good Case

**Write to `/tmp/query.txt`:**
```
best restaurants! & cafes in NYC
```

```bash
--data-urlencode "q@/tmp/query.txt"
```

**Or for complex URLs:**
**Write to `/tmp/url.txt`:**
```
https://example.com/path?param=value&other=123
```

```bash
--data-urlencode "url@/tmp/url.txt"
```

**Benefits:**
- ✅ No shell escaping issues with special characters
- ✅ Handles complex URLs and queries safely
- ✅ Consistent with JSON file pattern
- ✅ Easy to modify and test
- ✅ Works with any content complexity

**When to use file mode:**
- ✅ URLs with query parameters: `--data-urlencode "url@/tmp/url.txt"`
- ✅ Search queries with symbols: `--data-urlencode "q@/tmp/query.txt"`
- ✅ Complex filter strings: `--data-urlencode "query@/tmp/filter.txt"`
- ✅ Any parameter that might contain special characters

**Pattern Rule:** Always use `--data-urlencode "key@/tmp/file.txt"` for parameters that might contain special characters or complex content.

---

## 6. `printenv` and `bash -c` Wrappers

**Problem:** Using `$(printenv VAR)` instead of `$VAR`, or wrapping curl in `bash -c '...'`, was a workaround for an old Claude Code bug that silently cleared environment variables in pipelines. That bug is fixed — these patterns are now unnecessary noise.

### ❌ Bad Case

```bash
curl -s "https://api.example.com/data" \
  -H "Authorization: Bearer $(printenv API_TOKEN)" | jq '.data'
```

```bash
bash -c 'curl -s "https://api.example.com/data" -H "Authorization: Bearer $API_TOKEN" | jq ".data"'
```

### ✅ Good Case

```bash
curl -s "https://api.example.com/data" \
  -H "Authorization: Bearer $API_TOKEN" | jq '.data'
```

**Pattern Rule:** Always use `$VAR` directly. Never use `$(printenv VAR)` or wrap commands in `bash -c '...'`.

---

## Quick Checklist

When writing SKILL.md, verify:

- [ ] Remove `| jq .` unless doing actual transformation
- [ ] Use `/tmp/file` with `-d @/tmp/file` instead of inline JSON/data
- [ ] Use placeholder text (`<your-context-id>`) instead of shell variables (`$CONTEXT_ID`) in URLs
- [ ] Always use `-d @/tmp/filename.json` for JSON data, never `-d '{"key": "value"}'`
- [ ] Always use `--data-urlencode "key@/tmp/file.txt"` for parameters with special characters
- [ ] Use `$VAR` directly, never `$(printenv VAR)` or `bash -c '...'` wrappers
