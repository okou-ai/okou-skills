# Runtime hooks for generated decks

Use when changing slide structure, navigation or charts in a working deck.
The saved shell already includes the runtime and source configuration; no need to
recreate them. Use the recorded safe areas, required chrome and approved font
fallbacks in `tools/qa-config.json`. For final QA, follow [qa.md](qa.md).

The viewer surround is pure black (`#000`). Keep the visible canvas centered on both
axes and fully inside the viewport at its original aspect ratio, including after
resize and navigation. Scale the canvas as a whole; its internal source layout and
typography stay in canvas coordinates. This viewport scaling is separate from text fit.

## HTML hooks

Carry over the selected source layout's `data-layout`/`data-source-profile` and
required `data-chrome` roles so its recorded safe areas and fixed elements still apply.

Use `.deck > .slide` with exactly one `.stage` per slide and a `.fit` content root.
The `.fit` root supplies the default measurement area. Extra `data-fit-region` hooks
are only for genuinely constrained subareas; preserve valid source containers and
keep them disjoint. Ordinary titles/body need `data-text-role` labels, with no extra
fit boundary on a self-sized text element. See [typography-fit.md](typography-fit.md);
the whole content shares one fitting scale.
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
