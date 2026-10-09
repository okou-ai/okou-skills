# Source typography and automatic fitting

Keep the source presentation's typography by default. Longer replacement content may require smaller text; handle this mechanically during the first render so QA does not have to repeatedly rewrite CSS or recapture the deck.

## Establish source-size defaults

For each observed layout/text role, record source page/region, font family, effective size, available weight/leading/spacing, and mixed-run hierarchy. Preserve distinct title/body/metric/table/caption/footer styles when present; do not force every role to exist. If a new content type needs an unobserved role, explicitly alias a suitable source role or document an estimate. This adds a mapping, not a new source observation.

For PPTX, resolve effective text styles through runs, paragraphs, placeholders, layouts, masters, and theme defaults; a missing size on a run does not mean it is absent everywhere. The public `inspect_pptx.py` inventories literal evidence only and normalizes units; it does not resolve this entire chain. If effective inheritance/role selection cannot be confirmed, record it as inferred/unknown, not extracted. Account for existing text autofit when determining the source's rendered size, and compare with its page image. For legacy PPT, inspect a converted PPTX. For PDF, use available font metadata and verify it visually; for images or unavailable metadata, document estimates as inferred.

Convert source sizes using the same uniform scale used to map source geometry to the HTML canvas. Do not equate points with CSS pixels. For example, a 13⅓-inch-wide slide is 960 points wide; mapped to a 1600-pixel-wide canvas, its 24-point text becomes 40 CSS pixels. Record the scale and any aspect-ratio adaptation. Browser zoom or the outer presentation viewport's display scale must not change this baseline.

Store immutable baseline sizes in a small source-aware core plus only needed role/profile tokens. Use the public binding program for aliases, dependency/type/name-collision checks and CSS output, rather than agent-written dictionary expansion. Preserve ratios between differently styled runs within a text region. Use those tokens in both preserved and adapted layouts. Never copy a fixed default or global minimum such as `16.5px` from another template.

## Fit overflowing regions in the shared shell

Implement one shared fitter in `scripts/fit-text.js` and load it from `layouts/_shell.html`. The public neutral library offers a tested optional runtime; reuse it with source-specific bounds and region adapters rather than importing its synthetic preview skin. Store policy limits separately from source tokens, and measured results separately from both. It must run for every assembled deck, including screenshots and export, without waiting for an agent to notice overflow during QA.

1. **Reset and await layout.** Restore baseline sizes before each fitting pass. Prepare every hidden slide for intrinsic-size layout before awaiting `document.fonts.ready`, so fonts first used by those slides begin loading. Preserve its authored Flex/Grid display, not a block substitute. With the public runtime, attribute/inline hiding is temporarily removed; if a stylesheet still hides an element, declare its real display with `data-fit-display="grid"`, `data-fit-display="flex"`, or another valid display. An unknown display is unmeasurable. Wait for fonts, layout-affecting image loads, and a completed layout frame, and restore all hidden state and inline priorities on success or failure. Measure every slide at its intrinsic canvas size, including slides hidden by navigation; zero-sized or unmeasurable regions are not a pass. Expose a completion promise or equivalent readiness signal for capture/export to await, with bounded waits and explicit load failures.
2. **Measure real content.** Use explicit content regions with fixed available bounds, including their padding and safe areas. Check both horizontal and vertical overflow using scroll measurements and text/descendant bounds, including nested cells or boxes that clip content. Ignore declared background decoration. A region that already fits stays at scale `1`; never enlarge it to fill space.
3. **Shrink only the affected region.** Apply one multiplier to that region's baseline font sizes while preserving mixed-run hierarchy and proportional line height. Group related items only when their alignment requires one size, for example the body cells of one table. Keep unrelated titles, metrics, captions, and footers unchanged. Text fitting must not scale the whole slide, graphics, or logo, or conceal content through clipping or ellipsis.
4. **Choose the largest fitting size.** Search between the documented lower bound and scale `1` with a bounded search, such as binary search with a fixed iteration limit and a small measurement tolerance. Re-measure after each candidate. Fit to the actual available region rather than applying a preset reduction to every slide. Resetting from baseline makes repeated renders deterministic and prevents cumulative shrinking.
5. **Report the result.** Record slide/region IDs, baseline and final sizes, applied scale, and whether the region is unchanged, fitted, or unresolved. If no candidate fits within the bound, retain the failure visibly in QA data and try a more suitable layout or split the content. Do not silently drop facts, declare success because overflow is hidden, or continue shrinking indefinitely.

Readability bounds belong to the custom template's text roles and target canvas. Respect an explicit user minimum if present. Otherwise choose and document a limit using the source hierarchy, intended display size, and representative render checks; label it as inferred. The source default is not automatically a hard minimum. Do not inherit a universal floor from a built-in template or reject a source caption merely because it is smaller than body copy.

Include these rules and the fit-report location in the generated package's `SKILL.md` and `layouts/README.md`. If a renderer cannot await the shell's fitting lifecycle, use an explicit pre-render fitting step and persist computed sizes together with immutable baseline metadata before capture/export. A serialized fitted inline size must never become the next source baseline. Validate the actual delivery path; loading the script alone does not prove that a capture used its result.

## Validate before publishing

Use representative source layouts and every extension adapted during extraction, with their actual source fonts. Save validated reusable extension files in the template package; keep temporary fixture decks and validation images outside it:

| Case | Required result |
| --- | --- |
| Source content or short replacement content that fits | Baseline sizes and hierarchy are unchanged. |
| Longer text that fits after a bounded reduction | Only affected regions shrink, to the largest fitting size; first capture includes the adjustment. |
| Mixed font sizes, CJK/mixed-language text where supported, and dense table cells | All relevant regions are measured with loaded fonts; hierarchy and table alignment remain readable. |
| Content that cannot fit within the bound | The fit report remains unresolved and the layout/content needs adjustment. |
| Repeated fitting, then replacing long content with short content | No cumulative shrink; short content returns to its source size. |
| Initially hidden slides and capture/export | Hidden Flex/Grid geometry matches visible-page fitting; hidden-page webfonts finish loading before measurement; hidden state is restored even after readiness failure. Every slide is measured at full canvas size and delivery waits for fitting or the documented pre-render fallback. |

QA still checks clipping, overlap, contrast, and readability on rendered pages; a successful fit report only verifies the measured bounds. Fix shared extraction, layout, or fitting rules when failures repeat. For a local content change, remeasure its regions and inspect the affected pages; rerun deck-wide checks when shared fonts, styles, layout rules, or the fitter change.
