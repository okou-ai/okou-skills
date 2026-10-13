# Final QA for generated decks

Use the saved package's runtime and source configuration. No installation is needed.

## 1. Stage final paths, then run QA

Author a copy of `layouts/_shell.html` with its local assets in a draft directory.
Before the first QA, build a **new** publication directory:

```bash
python3 <template-dir>/tools/prepare-web.py --input <draft-dir>/index.html --out <web-dir>
node <template-dir>/tools/qa.mjs --final <web-dir>/index.html \
  --expected-pages <planned-count> --report <qa-dir>/report.json \
  --capture-dir <qa-dir>/review-pages
```

The helper copies referenced assets, hashes their final contents and rewrites
HTML/CSS/SVG paths; the draft stays unchanged. For assets beside the draft,
`--root <common-parent>` sets their allowed boundary. JS module graphs/dynamic
resource paths need bundling before this static staging step. Keep QA output outside
the web directory. No manual renaming or directory cleanup is needed.

## 2. Act on the JSON result

- **`BLOCKED`:** fix the reported causes together in the draft, stage a new web
  directory, then rerun QA. Existing bundles stay available.
  For `fitFloor`, inspect text boxes, glyph bounds, line height and clipping before
  shortening copy. `fitScale` blocks reductions beyond 20%; `smallText` blocks text
  below the 11px logical minimum. Preserve the shared black, centered viewer when
  resolving `viewportBackground` or `viewportFrame`.
- **`NEEDS_VISUAL_REVIEW`:** follow step 3.
- **`READY_TO_PUBLISH` with zero `hardGateFailures`:** deliver. No receipt, repeated
  QA or separate interaction check is needed on an unchanged deck; see the
  [interaction scope](runtime-contract.md#interaction-check-scope) for uncovered behavior.

## 3. Review only when required

Read the report's `captures`: QA has already captured `reviewRequired` pages in its
rendered browser, after fitting, navigation and asset loading. Filenames retain
original page numbers. No separate screenshot command or single-page HTML copies
are needed. Add `--capture-all` only for a requested full review or PPTX comparison.

Compare those pages with the source. `unknownTextGround` asks whether text remains
readable over textures, imagery or gradients. Overlap and transparent image margins
alone need no changes; adjust actual obscuration or poor contrast.

Save `<qa-dir>/review.json` with `deckSha256` (from `captures`), `pages` (original
one-based numbers), `sourceReferences` (existing evidence files relative to the
receipt) and nonempty `notes` from actual review. Rerun QA with
`--review <qa-dir>/review.json`; proceed when it passes. A valid receipt avoids
recapturing unchanged pages. Changed HTML or assets return to step 1 and required review.

## 4. Deliver

For HTML, publish the passing web directory directly. Its asset filenames already
meet the host's content-hash rule. No prepared copy, cleanup or extra QA pass is needed.

Only for a requested PPTX, add `--prepared <web-dir>/index.ready.html` to the final
QA command (the copy must be beside the input). Move this capture-only copy to a
separate conversion directory and copy its relative asset tree unchanged. Preserve
the passing interactive HTML and assets. Then convert and render the actual PPTX:

```bash
okou presentation convert --input <conversion-dir>/index.ready.html --verify --out <output-dir>/deck.pptx
okou presentation screenshot --input <output-dir>/deck.pptx --out <qa-dir>/pptx-pages
```

Compare page count, fonts, crop, reflow, geometry and rasterised SVG labels with
QA's HTML captures; `--verify` covers text only. Resolve conversion issues before
delivery. Keep conversion files and captures outside the web directory. After all
required checks pass, publish once, upload the requested file once and reuse the links.
