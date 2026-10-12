# Presentation runtime contract

Use when extracting a package or changing slide structure, navigation or charts.
Existing shell copies already include the runtime; no need to recreate it.
For final generation QA, follow [qa.md](qa.md).

## Source configuration and authoring hooks

`tools/qa-config.json` records observed source rules. Its shape is:

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

The inset numbers above are an **illustration**. Use the saved source margins,
including any `layoutSafeAreas` keyed by a stage's `data-layout` or
`data-source-profile`. Extraction supplies either a valid global safe area or an
entry for every source profile; package verification rejects missing or invalid rules.
A required chrome rule names `role`, optional `min`/`max`, and optional `layouts`.
Mark only source-required items with `data-chrome="<role>"`; absence in the source
is not a reason to invent a footer, motif or page marker. Fallback font families
must be explicitly approved in design notes before listing them here.
List replacement families (for example `Arial`), not the name of a failed primary
font. When a used webfont fails, the first available family in that text's CSS
font stack must be an approved fallback; approving a later, unused family is insufficient.

Use `.deck > .slide` with exactly one `.stage` per slide and a `.fit` content root.
Add disjoint `data-fit-region` hooks to independently replaceable title/body areas.
Keep text editable in real HTML or SVG text nodes. Hidden pages need their authored
`data-fit-display` when a stylesheet conceals the display mode. Preserve source-compatible backgrounds,
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

## Interaction check scope

Final QA reuses its browser session to check Home/End, all four arrow keys and up to
two consecutive moves per direction on multi-slide decks. Scripted key events check
the active-page marker and target-page visibility.

Page-number synchronization, notes, custom buttons and native keyboard/focus behavior
remain outside this check. Use targeted checks for uncovered behavior when relevant
or explicitly requested.
