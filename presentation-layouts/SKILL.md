---
name: presentation-layouts
description: Borrow six public, theme-neutral presentation structures on demand, bind a small source-aware token set mechanically, and fit only measured text overflow. Prefer the user's source layouts and keep the delivered deck self-contained.
---

# Shared presentation structures · pilot v1

This is a structure library, not a visual template, shell, full PPTX extractor, or universal design-token dictionary. It has no dependency on a private repository, a theme font, or a brand stylesheet.

## 1. Select only when needed

Prefer a suitable source layout or validated extension already saved in the user template. During upload-time extraction, read this public six-structure pilot's [references/catalog.md](references/catalog.md) and **only the chosen fragments**. Use matching local resources or fetch the catalogue, fragments, geometry and tools from the same exact public `okou-ai/okou-skills` commit. No private catalogue or GitHub credentials are required. Do not download example decks, unselected fragments, or another theme's shell.

Follow `extract-template/presentation` when building a reusable custom template: adapt selected structures to the source style during extraction, validate them, and save those adaptations plus provenance in the package's local extension index. Do not bundle the entire six-layout library, its catalogue, or synthetic skins. Later generation copies and edits saved layouts without fetching this library. For a one-off deck without an extraction stage, an adaptation may stay in that deck and its notes. If the public reference is unavailable, retain saved layouts or document the gap/composition; do not retry indefinitely.

## 2. Bind reliable values, not a complete dictionary

Read [references/token-contract.md](references/token-contract.md). The compiler requires only six tokens: a canvas background/foreground pair and title/body font-family/font-size. The shell also needs known canvas and safe-area geometry, but these can already exist in the user template. Add only the roles, profiles, surface pairs and components actually needed. Omit unobserved values and record them as unknown; never fabricate an extracted field to satisfy a schema.

Use source-specific roles when known. Explicit aliases are acceptable for missing roles; the compiler labels its automatic aliases and spacing mappings **inferred**. A metric aliasing title type does not mean a metric style was discovered in the source. Optional boldness/leading stay unspecified when unknown, not forced to a library preset. All inferred mappings require representative visual verification.

Run from this skill directory (Python 3, standard library only):

```bash
python3 scripts/bind_tokens.py \
  --input <template-theme.tokens.json> \
  --roles title,body,heading,caption \
  --css <work-dir>/bindings.css \
  --report <work-dir>/bindings.json
```

Select observed variants with `--profile <id>` and `--surface <id>` when provided. Output is scoped to matching `data-type-profile="<id>"` / `data-surface="<id>"` attributes on `.okp-theme`, so profiles do not overwrite other slides. Changed surfaces must explicitly bind the whole color quartet and cannot change typography or geometry. Program output resolves aliases, checks missing dependencies/types/layers/name collisions and binds role selectors; do not have the agent expand every token by hand. Inspect `inferredTokens`, `roleMap`, `origins` and `unobservedComponents` before acceptance.

For optional literal PPTX evidence:

```bash
python3 scripts/inspect_pptx.py \
  --input <source.pptx> --out <work-dir>/evidence.json \
  --width 1600 --height 900
```

This inventories native XML values and normalizes point sizes through one uniform canvas transform. It deliberately reports `effective: false`: it does **not** resolve the complete run/placeholder/layout/master/theme inheritance chain, identify semantic roles, or apply source autofit. Verify effective styles against the rendered source; unresolved semantic mappings remain inferred/unknown. PDF/screenshots cannot be passed to this inspector and require explicitly estimated values.

## 3. Materialize and keep the user's skin

Read the selected HTML and [styles/geometry.css](styles/geometry.css). Fragments declare regions, repeat prototypes and text/component hooks, not a templating runtime. Replace all `{{...}}` placeholders, expand `data-repeat` items, and supply local meaningful image assets with accurate alt text. Never publish unfinished prototypes or synthetic fixture facts as user content.

The geometry is scoped to `.okp-layout`. It uses a bounded title/body grid (default 1:5), paired columns, and fixed available fit regions. Adjust `--okp-layout-title-height`, spacing and column parameters to the user's safe areas and observed geometry; these are structural choices, not new extracted styles. A natural-height text line is not its available fit rectangle.

Assemble through the user's shell and chrome. Use `.okp-theme` on the user-skinned canvas and `data-text-role` / `data-component` hooks. Reuse source sizes and components. Do not copy the synthetic skins from `examples/` or `build_preview.py`. Missing card styling means no fabricated fill/border/radius; the process connector has a neutral one-unit stroke unless explicitly bound. Pair each observed surface with primary/secondary text and border roles, never assume white foreground. Keep chart entity-to-color order stable across pages.

Inline selected structure, geometry/binding CSS, runtime and required assets in the final artifact. GitHub links are authoring provenance only, never render-time imports.

## 4. Fit before capture, without changing baselines

Prefer the template's existing conformant fitter. [scripts/fit-text.js](scripts/fit-text.js) is an optional shared implementation that can be copied as the template's **runtime**, not as a bundled layout library. It has no built-in font-size minimum.

Mark fixed available text rectangles with `data-fit-region`, use unique slide/region IDs, and supply explicit role limits from the template or a documented user/inferred policy. Pass the compiler's `roleMap` so an inferred role can reuse its base role's policy:

```js
window.presentationReady = OkpFit.fit(document.querySelector('.deck'), {
  roleMap: bindings.roleMap,
  roleBounds: templateFitPolicy.roleBounds
});
const fitReport = await window.presentationReady;
```

Wait for fonts, layout-affecting images and intrinsic-size layout. Hidden slides must have explicit intrinsic geometry. The runtime prepares all hidden pages offscreen before awaiting font readiness and retains their authored Flex/Grid display. Attribute or inline hiding is temporarily removed; if a stylesheet still sets `display:none`, declare the actual layout on that hidden element with `data-fit-display="grid"` or `data-fit-display="flex"` (or another valid display). An unknown display is unmeasurable, not guessed as block. Hidden attributes and original inline values/priorities are restored even when readiness fails. A scale of `1` is unchanged; only actual measured overflow triggers a bounded largest-fit search. Related text can share a multiplier; inline runs retain their size ratios. Container text struts are scaled when necessary, not graphics containers. Missing/disabled/conflicting bounds return unresolved, not a guessed floor. Zero geometry and failed readiness return unmeasurable, not success.

Source style snapshots remain separate from fitted DOM styles (`data-okp-baseline-style` survives serialization). Replacing long content with short content restores the baseline. Call `OkpFit.reset` before an intentional source-inline-style edit and recreate its affected baseline snapshot; never use a fitted value as a new token. Run one top-level lifecycle, await its promise before capture/export, and recheck peer geometry. The fitter measures DOM/line-box bounds and ordinary overflow-clipping ancestors conservatively, not exact glyph outlines, clip paths, masks or arbitrary widget internals; visual QA remains mandatory.

## 5. Verify honestly

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
node --check scripts/fit-text.js
python3 scripts/build_preview.py --out <work-dir>/preview
okou presentation screenshot --input <work-dir>/preview/deck.html --out <work-dir>/pages
```

`build_preview.py` materializes six structures under two **synthetic** skins. It tests portability, not successful real-template extraction. For browser regression tests, install `playwright-core@1.64.0` in a separate QA directory and use an installed Chromium:

```bash
npm install --prefix <qa-dir> --no-save --package-lock=false playwright-core@1.64.0
NODE_PATH=<qa-dir>/node_modules CHROMIUM_PATH=<chromium-executable> \
  node tests/browser-test.cjs --input <work-dir>/preview/deck.html --out <work-dir>/browser-report.json
```

Exercise unchanged, bounded-fit, mixed-run/CJK, cannot-fit, repeat/reset, hidden Flex/Grid geometry under attribute/inline/stylesheet hiding, delayed hidden-page fonts, font/layout timeouts, zero-geometry and broken-image cases. Compare hidden-page results with visible-page fitting and verify hidden-state cleanup on both success and failure. Check screenshots for clipping, overlap, contrast and readability. Do not infer better first-pass quality, fewer reworks or faster generation from these fixtures; those require comparative runs with real sources and content. This skill does not publish templates or activate production instructions.
