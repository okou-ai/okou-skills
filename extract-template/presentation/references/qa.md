# QA for decks generated after extraction

This guide is for a presentation assembled later from the saved Custom Template.
It is not an extraction acceptance checklist: do not run `tools/qa.mjs` on the
source archive or build a sample deck merely to save the template. Extraction uses
`tools/verify-package.mjs` for package completeness and local resource paths.

Copy the supplied implementation with `node scripts/install-qa.mjs --package <dir>`;
do not ask the authoring model to recreate the fitter or audit. The installer
copies the untouched neutral library, scripts and tools, and inlines the common
runtime once in `layouts/_shell.html`. Installing it again updates that block,
not the user's source layouts, CSS, assets or uploaded original.

## Source-specific contract

Before installation, write `<dir>/tools/qa-config.json` using observed source rules:

```json
{
  "minFontSizePx": 10,
  "safeArea": {"left": 0.06, "right": 0.06, "top": 0.14, "bottom": 0.1},
  "layoutSafeAreas": {},
  "requiredChrome": [],
  "allowedFontFallbacks": [],
  "minContrastRatio": 3
}
```

The inset numbers above are an **illustration**, not extraction defaults. Record
actual source margins, including separate `layoutSafeAreas` keyed by a stage's
`data-layout` or `data-source-profile`. An absent safe-area contract blocks QA.
A required chrome rule names `role`, optional `min`/`max`, and optional `layouts`.
Mark only source-required items with `data-chrome="<role>"`; absence in the source
is not a reason to invent a footer, motif or page marker. Fallback font families
must be explicitly approved in design notes before listing them here.
List replacement families (for example `Arial`), not the name of a failed primary
font. When a used webfont fails, the first available family in that text's CSS
font stack must be an approved fallback; approving a later, unused family is insufficient.

Use `.deck > .slide` with exactly one `.stage` per slide and a `.fit` content root.
Add disjoint `data-fit-region` hooks to independently replaceable title/body areas;
do not nest fitting regions. Put text in real HTML or SVG text nodes, not a full-page
bitmap or CSS pseudo-element. Hidden pages need their authored `data-fit-display`
when a stylesheet conceals the display mode. Preserve source-compatible backgrounds,
image crops, frames and absolute overlays: no foreign palette, universal 6% margin,
forced contain mode or blanket decoration-hiding policy is imported.

The shared runtime owns keyboard navigation. Remove competing keyboard handlers;
wire source next/previous buttons to `PresentationNavigation.next()`/`previous()`
or use `go(index)` with a zero-based index. These return a promise and wait for any
active text fit before changing pages. Startup scripts should first await
`PresentationNavigationReady`. Scrolling decks may run horizontally,
vertically or in document flow. Decks with hidden slides automatically use paged
mode; `data-navigation-mode="paged"` on `.deck` can select it explicitly. Give
each CSS-hidden `.slide` its authored `data-fit-display`, such as `flex` or `grid`.
The runtime switches visibility and preserves that display mode. It recognizes
`active`/`is-active`; name a different source class with
`data-navigation-active-class="selected"` on `.deck`.

Mark actual quantitative SVG/HTML shapes with `data-plot-mark="bar"` or `"area"`
and a finite `data-value` taken from the source data. Nonzero values, including
negative bars, need nonzero width and height; genuine zero values may have zero
geometry. Use `data-plot-mark="point"` for visible observation markers and `"line"`
for data-series paths (a horizontal/vertical line may have one zero extent).
Axes and decorative guides are not data marks. Every `svg[data-chart-kind]` needs
marked data geometry; missing marks or unfilled values block QA. Use
`data-overlap-ok` only for labels intentionally drawn over a mark, as in pie labels.

## Generated-deck final QA command

Assemble directly in the final web directory and resolve asset paths before the
first QA. Create a separate QA directory for reports, receipts and rendered captures.

```bash
node <template-dir>/tools/qa.mjs --final <web-dir>/index.html \
  --expected-pages <planned-count> --report <qa-dir>/report.json \
  --prepared <web-dir>/index.ready.html
```

`--expected-pages` comes from the later deck-generation plan, not from recounting
the output. Do not use this command as an extraction gate. Zero pages,
indirect/unreachable slides, count mismatches, <10px effective text, clipped or unsafe
text, collapsed nonzero chart marks, unresolved/unmeasurable fitting, required chrome
mistakes, broken images,
failed used webfonts and broken four-direction navigation are blocking. Background
images and fonts settle before measuring; `fonts.ready` alone is not font success.
Known solid-background contrast below 3:1 is blocking, including same-colour text.

The JSON is primary; errors identify page, element and reason. `READY_TO_PUBLISH`
and zero `hardGateFailures` are required. Diagnose the reported geometry before
editing copy. For unresolved fitting at 10px, inspect text boxes, glyph bounds, line
height and clipping; shorten text only when measurements show a genuine capacity
limit. Fix failures together and rerun on the same HTML after changes. No need to
rebase paths and repeat QA on a second web copy, or render passing pages for another
visual check. Review only QA-designated pages unless a full pass is requested.

Text on imagery, gradients, painted pseudo-elements or overlapping background
layers yields `NEEDS_VISUAL_REVIEW`, not an automatic pass. Ancestor background
colours cannot establish contrast when another layer may be behind the text.
Compare the relevant page images with the source. A `--review <json>` receipt can
record `deckSha256`, reviewed `pages`, existing `sourceReferences` and nonempty
`notes`. It must match the exact HTML bytes and cover all requested review pages;
any HTML change invalidates it. Freeze local assets throughout review and delivery.
After review, rerun the same final QA command with `--review <qa-dir>/review.json`.
The receipt records actual review; all hard failures still need resolution.

## Interaction checks already included

Final QA reuses its browser session to check Home/End, all four arrow keys and up to
two consecutive moves per direction on multi-slide decks. Scripted key events check
the active-page marker and target-page visibility.

No need to repeat passing checks on an unchanged deck. Rerun QA after edits; use
targeted checks for failures, uncovered behavior or an explicit user request.
Page-number synchronization, notes, custom buttons and native keyboard/focus behavior
remain outside this check. Keep source-style review and requested PPTX validation.

## Targeted review and requested output

`--prepared` writes a **separate** capture-only HTML copy beside the generated deck,
only after QA passes. It contains measured styles, immutable baseline declarations
and an explicit capture marker; automatic refitting is disabled in this copy. The
source package and interactive authored deck remain unchanged. Keeping it beside the
input preserves package-relative assets.

For targeted review, select the relevant slides. Use the authored HTML while QA
requests visual review; the prepared copy is available only after it passes.
Retain the original page numbers in any review receipt.

```bash
okou presentation screenshot --input <web-dir>/index.html \
  --slides '<selectors-for-review-pages>' --out <qa-dir>/review-pages
```

Use the prepared HTML and omit `--slides` when a full set of page images is requested.

Before conversion, move `index.ready.html` to a separate conversion directory and
copy its relative asset tree there unchanged. Clean the web directory to retain
only the final interactive HTML and its runtime assets. Reports, receipts, captures,
PPTX files and conversion inputs stay outside it. The final web HTML and assets
remain byte-identical to the passing QA input, so cleanup needs no second layout QA.

Only when a later task explicitly requests a PPTX, convert the prepared HTML and
render the actual PPTX for roundtrip review:

```bash
okou presentation convert --input <conversion-dir>/index.ready.html --verify --out <output-dir>/deck.pptx
okou presentation screenshot --input <output-dir>/deck.pptx --out <qa-dir>/pptx-pages
```

Check page count, font/crop/reflow/geometry and any rasterised SVG labels against the
HTML images. Conversion `--verify` checks text coverage, not layout, minimum size
or fidelity. Preserve units: 10px means logical HTML canvas pixels, not 10pt; native
point sizes depend on slide-to-canvas mapping. Unsupported conversion is a blocker,
not proof that the template is a native PPTX in-place editing engine.

After the required checks pass, publish the clean web directory once and upload the
final requested file once. Reuse these delivery links in the response.

## Keep extraction and generation separate

- **Extraction:** run `tools/verify-package.mjs` to check required package files,
  source-index coverage, ordered source-page capture count, local library links and
  package-local asset paths, including every `srcset` candidate and resources in
  linked/imported CSS and SVG files. If source-to-HTML reconstruction creates a specific
  fidelity risk, compare one or two unchanged representative pages. Do not build a
  full sample deck, run final-deck QA or compare every reconstructed page by default.
  Save the Custom Template only after the package check succeeds.
- **Generation:** follow the five-step authoring path in the package. Run final QA on
  the final web HTML, review QA-designated pages, and rerun with the receipt or after
  fixes. Keep the stored source package unchanged.

The portable package retains its runtime QA and 10px fitter for future generation.
Repository CI checks skill metadata and JavaScript syntax; it does not certify rendered
layout quality. Run packaged final QA on generated decks only, not during extraction.
