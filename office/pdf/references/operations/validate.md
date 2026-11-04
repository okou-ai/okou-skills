# Validate and deliver a PDF

Check the exact completed output, not just intermediate JSON or a successful
merge. Verify requested content, page count/order, source values and applicable
[appearance rules](../common/presentation.md). Package or parser success does not
establish publication compliance or correct visual output.

For a user-requested rendered preview or visual review, create `preview/`, run:

```bash
pdftoppm -png -r 120 output.pdf preview/page
```

Inspect the actual images. For presentations or slide decks, use the platform's
presentation page-rendering command instead; this is the ordinary PDF route.
Text extraction alone cannot establish that charts, math, captions or form
appearances paint correctly. Apply
[feature-specific rendering QA](../implementation/content.md#feature-specific-rendering-qa)
for every content feature used. Check the actual selected fonts and disclose
fallbacks; preset or requested font names are not proof of embedding/rendering.

For FILL, reopen stored values and the affected widget appearances. Different
readers may paint form values differently; state which application/rendering
was actually checked. Do not call a storage-only inspection a viewer pass.

For REFORMAT, compare against source for omissions and changed structure. For a
Word/PDF pair, verify the PDF came from the authored DOCX, not a separate design.
Deliver only requested formats and report unexecuted or unavailable checks.
