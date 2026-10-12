# Typography while generating a deck

Use the saved source families, sizes, weights, leading, tracking and mixed-run
relationships as initial styles. No need to resolve the original PPTX font hierarchy
again. Use only the approved fallback families recorded in the template.

The runtime minimum is **10px on the logical 1600px-wide HTML canvas**, including
captions, footers, inline runs and SVG labels, even when content does not overflow.
SVG viewBox transforms and text-only scaling count; viewport zoom does not change
the floor. Logical pixels are distinct from native PPTX points.

The shell includes `PresentationFit.fit()` and `PresentationFit.ready`. The fitter
restores source baselines, waits for assets, preserves hidden-page display modes
and adjusts overflowing regions while respecting safe areas and clipping. It
scales font size, leading and tracking together and rechecks neighbours. No need
to recreate this fitting logic or turn fitted pixels into new source defaults.

Keep title/body `data-fit-region` areas disjoint with meaningful `data-text-role`
labels. At unresolved fitting at 10px, inspect text boxes, glyph bounds, line height
and ancestor clipping first. Shorten, recompose or split only when measurements
show a genuine content-capacity limit. Keep text visible and editable.

Source layouts and selected library fragments use the same runtime. Follow
[qa.md](qa.md) for final checks, required visual review and delivery.
