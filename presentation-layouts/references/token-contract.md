# Progressive token contract · v1.0.0

**Core required, extensions on demand, unknowns explicit, program binding.** This is an output/binding interface, not a checklist requiring every source to contain every visual role.

## Minimum and responsibility

The compiler needs just six source-aware tokens:

| Key | Type |
| --- | --- |
| `color.surface.canvas` | color |
| `color.on-surface.canvas.primary` | color |
| `type.title.font-family` | font-family |
| `type.title.font-size` | dimension |
| `type.body.font-family` | font-family |
| `type.body.font-size` | dimension |

Canvas transform and safe areas must also be known for assembly. They can reside in the existing shell/source inventory; do not force redundant token entries. Source roles, inline runs and per-layout differences remain preserved in the user's source layouts. Optional weight, leading, tracking, spacing, secondary roles, components, profiles, backgrounds and charts are added only when needed and supported by evidence.

If a required value is unavailable, record that fact and obtain a documented estimate or user decision before binding; do not mark an estimate extracted. Missing optional values are omitted, with unknowns kept in extraction notes. A source with six useful values can legitimately produce many aliases but still has only six useful source values.

## Naming, layers and formats

Dot-separated paths, lowercase kebab-case within segments. No ambiguous ad hoc abbreviations. CSS names are `--okp-` plus dots replaced by hyphens; the compiler rejects collisions such as `type.a-b.font-size` and `type.a.b-font-size`.

| Layer | Namespace | Rule |
| --- | --- | --- |
| L0 | `ref.*` | Literal source values with provenance; no semantic dependencies |
| L1 | `color.*`, `type.*`, `space.*`, `shape.*`, `stroke.*`, `chart.*` | Semantic roles; can reuse L0 or compatible L1 values |
| L2 | `component.*` | Component skin through semantic roles, not direct source primitives |
| L3 | `layout.<id>.*` | Structural geometry in catalogue/assembly metadata; not input to the skin compiler |
| L4 | `fit.*` / fit-policy file | Explicit runtime limits; never interpreted as extracted source styling |
| L5 | `runtime.*` / fit-report file | Measured results, never dependencies of L0-L4 or new baselines |

`theme.tokens.json` is flat: `contractVersion: "1.0.0"`, `$tokens: { "dot.path": { "$type": ..., "$value": ..., "$extensions": ... } }`. [minimal.tokens.json](../examples/minimal.tokens.json) has only six fields and is explicitly synthetic. [token-contract.schema.json](token-contract.schema.json) checks syntax; `bind_tokens.py` performs cross-token/context/dependency validation.

Supported pilot value types: lowercase hex `color` (`#rrggbb` or `#rrggbbaa`), ordered `color-list`, `font-family` array, finite `dimension` (`{"value":40,"unit":"px"}`), finite `number`, boolean, and a limited surface-binding string enum. `$value: "{ref.type.body-size}"` is an alias, not CSS `var(...)` and not a new source observation. Do not use `null`, `0px`, a made-up color, or a library font-size preset to represent unknown styling.

Every literal has `$extensions.origin`:

- `kind: "extracted"` requires `documentId` and an exact `location`; keep original units and transform evidence there or in the source inventory.
- `kind: "inferred"` requires a nonempty `reason`; include uncertainty/verification notes when relevant.
- `kind: "user"` records an explicit user choice; `kind: "library"` is reserved for acknowledged non-source structural defaults, not a claim about the source.
- An alias inherits its value provenance unless its semantic mapping carries an explicit origin. Record inferred role selection separately when a raw value is native but its role is not.

PPTX XML is evidence, not automatically an effective style. Literal master sizes, theme references, source autofit, hidden layouts and transformed colors require inheritance/context/render verification. The inspector reports these limits explicitly. PDF/screenshot estimates remain inferred; precision must not imply certainty.

Normalize geometry and type using **one uniform source-canvas-to-target transform**. For contain mapping, `scalePxPerPt = min(targetWidthPx/sourceWidthPt, targetHeightPx/sourceHeightPt)` and `fontPx = sourcePt * scalePxPerPt`. Retain offsets/aspect adaptation. A 24pt font on a 960pt-wide 16:9 source becomes 40px on a 1600px canvas, not 24px and not 53.33px. Outer viewport zoom never changes this intrinsic baseline.

## Conditional roles and contexts

Known pilot text roles are title, body, heading, metric-value, metric-label, label, caption, table-header, table-cell. The last seven are **not extraction requirements**. When absent, the compiler maps heading/metric-value to title and other roles to body, retaining sizes and explicitly reporting inferred bindings. Optional properties inherit only when available. New roles may be passed through `--roles` with explicit font-family/font-size bindings; no classifier guesses their semantics.

Optional properties: `type.<role>.font-weight`, `.line-height` (unitless), `.letter-spacing`, `.paragraph-gap`. Missing values are not silently replaced with a themed preset. Preserve mixed runs in source HTML; apply a common fit multiplier rather than flattening them.

Use `contexts.profiles.<id>.$tokens` for observed layout-role variants (e.g. cover vs dense table). Do not merge their distinct defaults into one global size. `contexts.surfaces.<id>.$tokens` changes only color/palette bindings, never typography or geometry. Explicit lowercase kebab-case selection is required; unknown IDs fail. Compiled CSS is scoped to matching `data-type-profile` and `data-surface` attributes on `.okp-theme`, so one profile cannot overwrite all other pages.

Each observed surface uses a complete quartet: `color.surface.<id>`, `color.on-surface.<id>.primary`, `.secondary`, `color.border.<id>`. Canvas secondary/border may explicitly alias primary when unobserved; the compiler reports that inference. Other declared surfaces require all four entries. A selected surface override must explicitly include the complete quartet for every surface it changes, including intentionally retained or aliased values; it cannot leave old secondary text/borders behind. Never infer white text from a brand-colored background. Card/table surface selections rebind the whole quartet, including captions. Validate actual composited contrast after alpha/texture/image backgrounds.

The pilot binds card surface/padding/per-edge padding/border width/color/radius; table header surface/cell padding/per-edge padding/rule width/color; connector color/stroke width. Other component tokens can be declared for custom CSS but are not automatically rendered as a complete reconstructed component. Unobserved card/table properties are not emitted and do not reset existing user CSS. Background binding sets only `background-color`, preserving source textures/images. Low-specificity neutral line fallbacks (solid when a border width is declared, one-unit connector when unbound) yield to existing user component CSS; they are not extracted source styles.

`chart.series.colors` is an ordered palette; map source entities to indices once and reuse that order across slides. A palette does not constitute a chart renderer, and the six pilot structures do not supply one.

## Fit and runtime are separate files

A fit-policy file supplies `roleBounds.<role>.minScale` and/or `minFontSizePx`, plus optional `enabled:false`. No universal minimum is provided by the library. Source defaults remain unchanged; policy limits are user/configuration choices or explicit inferences validated for the target canvas. Reuse a base-role policy only through the recorded role map. If a limit conflicts with a source run, report `FIT_BOUND_CONFLICT`, not a silently weakened floor.

The shared fitter records baseline/final sizes, group scale, slide/region IDs and one of `unchanged`, `fitted`, `unresolved`, `unmeasurable`. Missing limits, cannot-fit content, broken assets and zero geometry are not passes. Preserve immutable source inline-style snapshots across reruns and serialized reloads. Final sizes never overwrite tokens or extracted evidence.

## Acceptance, not aspiration

A valid minimal token file is not proof of source fidelity. The literal inspector is not a complete extractor. Resolved aliases are not newly observed roles. Successful DOM fitting is not visual QA. Synthetic cross-skin fixtures are not real-template extraction benchmarks. Publication still requires representative source rebuilds, original-content baseline preservation, local overflow handling, rendered checks and a verified capture/export path. Measure first-pass rate, rework and speed separately on real generation runs before making improvement claims.
