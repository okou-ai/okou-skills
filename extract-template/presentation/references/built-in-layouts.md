# Public built-in expressions for upload-time extension

Select and adapt built-in expressions **during extraction after upload**, before the custom template is published. Later generation uses saved local adaptations; it must not fetch a catalogue and restyle layouts on each run.

## Public resources only

Use the independently authored, theme-neutral `presentation-layouts/` library in the public **okou-ai/okou-skills** repository. No private repository, authenticated catalogue, themed shell, or external brand package is an extraction dependency.

Canonical public index (discovery, not a render dependency):

https://github.com/okou-ai/okou-skills/blob/main/presentation-layouts/references/catalog.md

Reviewed public baseline:

https://github.com/okou-ai/okou-skills/blob/1004a653cdfcef8881a28f8735f93ab01e26d37c/presentation-layouts/references/catalog.md

Use matching local library files when present. Otherwise resolve the available public revision once; during PR validation, use the guide's exact public PR head. Fetch the selected index, fragments, geometry, contract, and any needed tools from that same full commit, never a mixture of `main` and pinned files. The baseline identifies verified public structures, not authority to override this extraction guide's upload-time packaging rules. Record the actual revision used as provenance.

The current pilot has **six structures**, not a 40+ layout catalogue:

| Expression | Public layout ID |
| --- | --- |
| Indicators | `kpi-grid` |
| Records and detail | `table` |
| Peer narratives | `two-column` |
| Two options compared | `comparison` |
| Ordered process | `process` |
| Image and narrative | `image-text` |

Read only selected fragments plus shared geometry and the [progressive token contract](../../../presentation-layouts/references/token-contract.md). Preserve the uploaded source's typography, safe areas, foreground/background pairs, components, and chrome. The library contains no font, palette, decoration, theme shell, or chart implementation. Capacities are hints, not measured guarantees under the user's fonts and content.

Uncovered charts, timelines, and other expressions may reuse a suitable source layout or become a documented source-styled custom extension. Label custom work explicitly; do not fabricate catalogue provenance or invent content to fill a structure. If public access fails, use matching local resources or disclose the gap, not a private fallback or a request for GitHub credentials.

## Adapt once, save, reuse

Follow [layout-reuse.md](layout-reuse.md): identify useful gaps, select complementary public IDs, reuse the closest source layout/components, and adapt the expression to the source's typography and framing. Validate each adaptation with source fonts and representative replacement content, compare it visually with source pages, then save it in `layouts/extended/` and `layouts/extended-index.json`.

Save only selected, validated, source-styled adaptations and their necessary local resources. Do not bundle the whole structure library or copy synthetic fixture skins/data. Temporary test decks stay outside the package; reusable adapted layouts stay inside it.

The generated package instructions point to the local source/extension indexes. Keep public repository, exact commit and fragment path for catalogue-derived entries, or an explicit custom origin, together with source-style basis, inferred changes, capacity/test scope, and validation outcome. External links are provenance only; ordinary generation, viewing, QA, and export must work without GitHub access.
