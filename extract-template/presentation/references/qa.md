# Presentation QA and delivery readiness

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

Use `.deck > .slide` with exactly one `.stage` per slide and a `.fit` content root.
Add disjoint `data-fit-region` hooks to independently replaceable title/body areas;
do not nest fitting regions. Put text in real HTML or SVG text nodes, not a full-page
bitmap or CSS pseudo-element. Hidden pages need their authored `data-fit-display`
when a stylesheet conceals the display mode. Preserve source-compatible backgrounds,
image crops, frames and absolute overlays: no foreign palette, universal 6% margin,
forced contain mode or blanket decoration-hiding policy is imported.

## One final mechanical command

```bash
node <dir>/tools/qa.mjs --final <assembled.html> \
  --expected-pages <planned-count> --report <qa-report.json> \
  --prepared <assembled.ready.html>
```

`--expected-pages` comes from the generation plan or representative rebuild plan,
not from recounting the output. Zero pages, indirect/unreachable slides, count
mismatches, <10px effective text, clipped or unsafe text, collapsed nonzero chart
marks, unresolved/unmeasurable fitting, required chrome mistakes, broken images,
failed used webfonts and broken four-direction navigation are blocking. Background
images and fonts settle before measuring; `fonts.ready` alone is not font success.
Known solid-background contrast below 3:1 is blocking, including same-colour text.

The JSON is primary; errors identify page, element and reason. `READY_TO_PUBLISH`
and zero `hardGateFailures` are required. Fix failures together and rerun only after
changing input. Do not repeatedly render passing pages or count style advisories as
mechanical blockers. Brand/source fidelity is a separate representative comparison.

Text on imagery or gradients yields `NEEDS_VISUAL_REVIEW`, not an automatic pass.
Compare the relevant page images with the source. A `--review <json>` receipt can
record `deckSha256`, reviewed `pages`, existing `sourceReferences` and nonempty
`notes`. It must match the exact HTML bytes and cover all requested review pages;
any HTML change invalidates it. Freeze local assets throughout review and delivery.
This is evidence of a performed review, not permission to bypass a hard failure.

## Capture and export the measured state

`--prepared` writes a **separate** capture-only HTML copy beside the local input,
only after QA passes. It contains measured styles, immutable baseline declarations
and an explicit capture marker; automatic refitting is disabled in this copy.
The source and interactive authored deck remain unchanged. Keeping it beside the
input preserves package-relative assets. Use this exact copy for deliverable capture:

```bash
okou presentation screenshot --input <assembled.ready.html> --out <validation-dir>
okou presentation convert --input <assembled.ready.html> --verify --out <deck.pptx>
```

Render the actual PPTX with `okou presentation screenshot` when PPTX is delivered.
Check page count, font/crop/reflow/geometry and any rasterised SVG labels against the
HTML images. Conversion `--verify` checks text coverage, not layout, minimum size
or fidelity. Preserve units: 10px means logical HTML canvas pixels, not 10pt; native
point sizes depend on slide-to-canvas mapping. Unsupported conversion is a blocker,
not proof that the template is a native PPTX in-place editing engine.

## Two validation stages

- Extraction: check every source page is inventoried, rebuild representative distinct
  compositions/profiles/backgrounds, run final QA, then compare to original page
  images. Keep source-page images separate from reconstruction evidence.
- Generation: source-first selection, selected local-layout adaptation, automatic
  fitting, final QA and source-style review of newly adapted compositions. Capture
  and export only the measured working copy. Never modify the stored source package.

The portable package retains its runtime QA and 10px fitter. Repository CI checks
skill metadata and JavaScript syntax; it does not certify rendered layout quality.
Run the packaged final QA on actual reconstructions/generated decks and compare
representative page images with the user's source before delivery.
