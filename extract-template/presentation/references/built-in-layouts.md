# Public shared layout references

Use the public, theme-neutral pilot in **okou-ai/okou-skills**, not a private template repository or a themed fragment catalogue.

Canonical shared index URL:

https://github.com/okou-ai/okou-skills/blob/main/presentation-layouts/references/catalog.md

For PR validation, resolve the current guide's exact PR head and use `https://github.com/okou-ai/okou-skills/blob/<40-hex-commit>/presentation-layouts/references/catalog.md`. After release, resolve the public revision once and record the tested absolute commit-pinned index URL in generated `SKILL.md` and `layouts/README.md`. All selected fragments, geometry, contract and tools must come from that same revision; never mix `main` and a cached pinned fragment.

The index supplies six independently authored neutral structures: KPI grid, table, two-column narrative, comparison, four-step process, and image/text. It links only public resources. It does not ship fonts, palettes, decorations, brand components, a theme shell or chart implementation. Structural hints are estimates, not fit guarantees.

Prefer preserved source layouts. Read only a selected fragment plus shared geometry/binding guidance when a fitting source layout is absent. Reuse the user's source typography, foreground/background pairs, components and fitter. Keep the adapted structure and provenance in the generated deck, not in the reusable custom template.

Do **not** copy the catalogue, built-in layouts, synthetic example skins/decks or pre-adaptations into custom packages. Shared binding/fitting code may be used as a package runtime when required for self-contained rendering; it is not a licence to bundle the structure library. If references cannot be resolved, use source layouts or document a deck-specific composition and record the unavailable reference. Do not repeatedly fetch or silently fall back to a private theme.

The final deck must contain all required HTML, CSS, assets and runtime locally. References are authoring inputs only; viewing, QA screenshots and export cannot require GitHub access.
