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
- **`READY_TO_PUBLISH` with zero `hardGateFailures`:** content QA passed; continue
  to step 4 for delivery. No receipt, repeated content QA or separate
  interaction check is needed on an unchanged deck; see the
  [interaction scope](runtime-contract.md#interaction-check-scope) for uncovered behavior.

## 3. Review only when required

Read the report's `captures`: QA has already captured `reviewRequired` pages in its
rendered browser, after fitting, navigation and asset loading. Filenames retain
original page numbers. No separate layout-QA screenshot command or single-page HTML
copies are needed. Add `--capture-all` only for a requested full visual review or
to investigate conversion diagnostics. These limits apply only to content QA.

Compare those pages with the source. `unknownTextGround` asks whether text remains
readable over textures, imagery or gradients. Overlap and transparent image margins
alone need no changes; adjust actual obscuration or poor contrast.

Save `<qa-dir>/review.json` with `deckSha256` (from `captures`), `pages` (original
one-based numbers), `sourceReferences` (existing evidence files relative to the
receipt) and nonempty `notes` from actual review. Rerun QA with
`--review <qa-dir>/review.json`; proceed when it passes. A valid receipt avoids
recapturing unchanged pages. Changed HTML or assets return to step 1 and required review.

## 4. Deliver

After authoring the HTML deck, choose the delivery format from the current prompt's
explicit request, otherwise the user's remembered presentation-format preference,
otherwise HTML. Deliver one format unless the user requests multiple formats.
Template authoring and content QA apply to both delivery paths; follow the platform's
publishing and conversion instructions for the selected format.

For HTML, use the passing web directory. Its asset filenames already meet the host's
content-hash rule. No prepared copy, cleanup or extra content-QA pass is needed.
Publish once and return the hosted HTML URL.

When PPTX is selected, add `--prepared <web-dir>/index.ready.html` to the final
QA command (the copy must be beside the input). Move this capture-only copy to a
separate conversion directory and copy its relative asset tree unchanged. Preserve
the passing interactive HTML and assets as local source files. Convert the prepared
HTML directly:

```bash
okou presentation convert --input <conversion-dir>/index.ready.html --verify --out <output-dir>/deck.pptx
```

Upload the successfully converted PPTX once and return its file link. Do not also
publish or deliver the HTML unless the user requests it. Successful conversion needs
no additional AI review or rendered-page comparison; `--verify` checks text coverage.
Investigate reported conversion failures or unsupported content before delivery.
Use `okou presentation screenshot` only for a requested visual check or to investigate
conversion diagnostics. Keep conversion files and any captures outside the web directory.
