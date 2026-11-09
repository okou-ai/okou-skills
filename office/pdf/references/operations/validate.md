# Validate and deliver a PDF

Check the exact final output, not intermediate JSON or a successful merge.
Set `SKILL_DIR` and `OFFICE` per [the entry point](../../SKILL.md).

```bash
python3 "$OFFICE" validate --input output.pdf
python3 "$OFFICE" render --input output.pdf --pages preview/pages
```

Inspect actual pages when visual QA applies: required content, page count/order,
source values, [appearance](../common/presentation.md), selected fonts/fallbacks
and [feature-specific rendering](../implementation/content.md#feature-specific-rendering-qa).
Parser success or text extraction cannot establish that charts, mathematics,
captions or widgets paint correctly; font names do not prove embedding. Receipts
cover executed mechanics, not factual accuracy or publication compliance.

For FILL, reopen stored values and affected widget appearances; identify the
viewer actually checked, since readers can differ. Storage-only inspection is
not a viewer pass. For REFORMAT, compare against source for omissions and changed
structure. For Word/PDF pairs, verify export from the authored DOCX rather than
an independent design. Never overwrite sources; use isolated application checks
with macros disabled and external-link updates disabled.

Fix defects and repeat affected checks. Deliver only requested formats and state
unavailable or unexecuted checks without labeling them passed.
