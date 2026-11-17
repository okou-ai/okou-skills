# FILL or inspect a PDF form

Fill existing fields, not a redesigned document. An input alone does not authorize
restyling. This route needs Python and `pypdf`, never the cover/body browser
pipeline. Check that input is an existing PDF first; if setup is missing, only an
authorized `make.sh fix --only fill` installs it. No implicit installs occur.

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
filled copy. For a requested fill use only the [FILL checks in VALIDATE](validate.md#fill),
not CREATE's design/content checklist. Requested invalid/unknown fields fail
without replacing the destination. Reopen requested stored values and inspect
only affected widget appearances/pages (expand if evidence requires). A correct
stored value does not establish that every reader paints its widget correctly.
