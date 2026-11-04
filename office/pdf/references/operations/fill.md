# FILL or inspect a PDF form

Fill fields without altering layout or design. An existing PDF does not authorize
restyling. This route needs Python and `pypdf`, not the browser pipeline; do not
make the user install Chromium for form inspection or filling.

Always inspect first for exact field names, types, choices and radio values:

```bash
python3 "$SKILL_DIR/scripts/fill_inspect.py" --input form.pdf
```

For an authorized fill, use the observed names and choices:

```bash
python3 "$SKILL_DIR/scripts/fill_write.py" --input form.pdf --out filled.pdf \
  --values '{"FirstName": "Jane", "Agree": "true", "Country": "US"}'
```

| Field type | Value format |
|---|---|
| `text` | Any string |
| `checkbox` | `"true"` or `"false"` |
| `dropdown` | Must match a choice value from inspection |
| `radio` | Must match a radio value from inspection, often beginning with `/` |

For read-only inspection, stop after reporting the findings; do not write a
filled copy. For a requested fill, reopen the output and check stored fields and
visible appearances using [VALIDATE](validate.md). A correct stored value alone
does not establish that every PDF reader paints its widget correctly.
