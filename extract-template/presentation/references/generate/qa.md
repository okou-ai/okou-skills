# Final QA for generated decks

Use after generating a deck from a saved Custom Template. The package supplies the
runtime and source configuration; no need to install or recreate them.

## 1. Run

Assemble a copy of `layouts/_shell.html` directly in the final web directory with
final asset paths. Keep QA reports, receipts and captures in a separate directory.
Use the planned page count:

```bash
node <template-dir>/tools/qa.mjs --final <web-dir>/index.html \
  --expected-pages <planned-count> --report <qa-dir>/report.json \
  --prepared <web-dir>/index.ready.html
```

## 2. Act on the JSON result

- **`BLOCKED`:** fix the reported causes together, then rerun step 1 on the same HTML.
  For `fitFloor`, inspect text boxes, glyph bounds, line height and clipping before
  shortening copy; confirm a real capacity limit first. `fitScale` blocks reductions
  beyond 20%; `smallText` blocks text below the 11px logical-canvas minimum.
- **`NEEDS_VISUAL_REVIEW`:** follow step 3.
- **`READY_TO_PUBLISH` with zero `hardGateFailures`:** proceed to step 4. No need for
  a review receipt, another QA run or repeated passing interaction checks on an
  unchanged deck. See the [interaction scope](runtime-contract.md#interaction-check-scope)
  when checking uncovered behavior.

## 3. Review only when required

Inspect only pages listed in `reviewRequired`, unless a full review was requested.
`unknownTextGround` asks for a readability check: textures, imagery and gradients
may overlap text when the letters remain clear with sufficient visual contrast.
Intersecting boxes or transparent image margins alone are not a defect. If readable,
keep the text and artwork unchanged and record the review; no shortening, moving or
removing content is needed solely to avoid overlap. Adjust actual obscuration or poor
readability.
Capture the authored HTML; the prepared copy becomes available only after QA passes:

```bash
okou presentation screenshot --input <web-dir>/index.html \
  --slides '<selectors-for-review-pages>' --out <qa-dir>/review-pages
```

Compare with the source and save `<qa-dir>/review.json` containing `deckSha256`
(SHA-256 of the exact HTML), `pages` (original one-based page numbers),
`sourceReferences` (existing evidence files, relative to the receipt) and nonempty
`notes` from the actual review. Keep local assets unchanged. Rerun step 1 with
`--review <qa-dir>/review.json`; proceed only when it passes. HTML edits invalidate
the receipt; changed HTML or assets return to step 1 and any required review.

## 4. Deliver

After QA passes, `index.ready.html` is the capture-only copy. Move it to a separate
conversion directory and copy its relative asset tree unchanged. Keep only the
interactive HTML and its runtime assets in the web directory, byte-identical to
the passing input; no second layout QA is needed for this cleanup.

For a requested PPTX, capture the prepared HTML as a reference, convert, and render
the actual PPTX:

```bash
okou presentation screenshot --input <conversion-dir>/index.ready.html --out <qa-dir>/html-pages
okou presentation convert --input <conversion-dir>/index.ready.html --verify --out <output-dir>/deck.pptx
okou presentation screenshot --input <output-dir>/deck.pptx --out <qa-dir>/pptx-pages
```

Compare page count, fonts, crop, reflow, geometry and rasterised SVG labels with
the HTML images; `--verify` covers text only. Resolve conversion issues before
delivery. Keep conversion files and captures outside the web directory. After all
required checks pass, publish once, upload the requested file once and reuse the links.
