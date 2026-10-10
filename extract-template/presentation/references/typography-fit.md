# Source typography and the fixed 10px floor

Source font families, sizes, weights, leading, tracking and mixed-run relationships
remain the initial style. Resolve effective PPTX styles through runs, paragraphs,
placeholders, layouts, masters, themes and existing source autofit, then compare
with rendered source pages. PDF/image estimates remain inferred, not extracted.

Map typography and geometry with the same uniform source-to-canvas transform.
A 24pt font on a 960pt-wide slide becomes 40px on a 1600px-wide canvas. Record original
units, aspect adaptation and scale. Do not treat 24pt as 24px or apply viewport zoom
to the immutable source baseline.

The sole runtime minimum is **10px on the logical 1600px-wide HTML canvas**. Never
use the source's smallest font, a role-specific inferred minimum or a foreign
preset as the lower bound. A source run below 10px is retained as evidence but its
rendered size is raised to 10px. This applies even when the page does not overflow,
and includes captions, footers, inline runs and SVG labels. SVG viewBox transforms
and text-only scale transforms count; outer viewport zoom does not change the policy.

The supplied `dom-metrics.js` and `fit-text.js` expose `PresentationFit.fit()` and
`PresentationFit.ready`. The installer inlines them once in the shell. The runtime:

1. Restores immutable baseline declarations before each fit, including serialized
   reloads; final fitted pixels never become new source defaults.
2. Reveals explicitly adapted hidden pages for measurement without changing their
   authored flex/grid display or navigation state.
3. Waits for used fonts, all images/background images and paint frames; failure or
   zero geometry cannot pass as "already fits".
4. Enforces the 10px floor, then changes type only in overflowing declared regions.
   It measures safe-area/ancestor clipping, not only the stage's outside edge.
5. Searches the largest fitting scale with bounded remeasurement, rather than
   stopping at a fixed 80%. Font sizes, leading and tracking move together;
   source families, weights, assets, palette and the whole canvas do not change.
6. Rechecks neighbours after fitting. At the 10px limit, still-unfit content is
   `unresolved`: inspect the text box, glyph bounds, computed line height and ancestor
   clipping before changing copy. Fix geometry first; shorten, recompose or split only
   when measurements show a genuine content-capacity limit. Keep text visible and editable.

Use disjoint `data-fit-region` areas with meaningful `data-text-role` labels.
Source-layout clones and selectively adapted local fragments use the same runtime.
Do not build a token compiler or redraw every library layout during extraction.
Run final QA and prepare the measured capture copy as documented in `qa.md`.

Synthetic fixture success demonstrates code behaviour, not source fidelity. Real
source rebuilds, actual font availability, and the delivery screenshot/export path
still require validation before a template is reported as published or shipped.
