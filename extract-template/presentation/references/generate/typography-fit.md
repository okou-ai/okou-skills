# Typography while generating a deck

Use the saved source families, sizes, weights, leading, tracking and mixed-run
relationships as initial styles. No need to resolve the original PPTX font hierarchy
again. Use only the approved fallback families recorded in the template.

The QA minimum is **11px on the logical 1600px-wide HTML canvas**, including
captions, footers, inline runs and SVG labels, even when content does not overflow.
SVG viewBox transforms and text-only scaling count; viewport zoom does not change
the floor. Logical pixels are distinct from native PPTX points.

The shell includes `PresentationFit.fit()` and `PresentationFit.ready`. It restores
source baselines, waits for assets and measures the original size first. Only an
overflowing page tries **95%, 90%, 85%, 80%**, in order, with one scale across its
`.fit` content. Each step scales font size, leading and tracking together, reflows
and measures again; the first passing step wins. Fit can be non-monotonic across
line breaks, so each step is measured independently.

The maximum reduction is **20%**. If no step fits, or a step would put text below
11px, restore source typography and mark `data-overflow="fit-floor"`. Existing
source text below 11px stays unchanged for QA to report. No need to recreate this
logic or turn fitted pixels into new source defaults.

`.fit` defines the page's content area. Preserve valid source measurement containers;
use an additional `data-fit-region` only for a genuinely constrained subarea, such as
a fixed content panel. Keep these areas disjoint; all share the page's scale.
For ordinary flow titles/body, `data-text-role` labels are sufficient. No extra fit
boundary is needed on the text element itself: its box can shrink with the font or
exclude naturally overhanging glyphs even when the page has ample space.

For `fit-floor`, compare glyph bounds with the intended container, safe area and
ancestor clipping first. If a self-sized title was incorrectly marked as a fit region,
use its actual container or remove that extra hook before changing the copy or size.
Shorten, recompose or split only for a genuine capacity limit. Keep text visible and
editable. QA blocks `fit-floor`, scaling below 80% and text below 11px independently
of its final overflow checks.

Source layouts and selected library fragments use the same runtime. Follow
[qa.md](qa.md) for final checks, required visual review and delivery.
