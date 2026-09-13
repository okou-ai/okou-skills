# Authoring Exceptions

Open this guide only for an existing authored project, a starter migration, a capacity exception, or an unclear review result. The normal path is `SKILL.md + ROUTER.md`, then one bootstrap command.

## Bootstrap once

Choose all Router rows and record the compact scene contract before running the command:

```bash
node <SKILL_DIR>/scripts/bootstrap-project.mjs \
  --project <HYPERFRAMES_PROJECT> \
  --host-id <composition-id> \
  --presenter on \
  --presenter-scenes cover,close \
  --color-system navy-cobalt \
  --language en \
  --scenes cover:8,evidence:10,close:7 \
  --layout-map cover=orientation/headline-cover,evidence=data/kpi-grid,close=orientation/public-action-close
```

For the first Chinese, Japanese, or Korean build, add one licensed local font with `--content-font`. Bootstrap initializes a blank HyperFrames project when needed, stages only the selected proofs and executable starters, installs deduplicated official dependencies, and scaffolds the host, scenes, and motion sidecars. Existing installed items with valid targets and a receipt are reused without another Registry request.

Bootstrap does not research, select layouts, write claims, or render. Do not use `--force` on an authored project unless replacing its host is intentional.

Built-in names are `navy-cobalt`, `monumental-minimal`, `black-gold`, `obsidian-champagne`, `petrol-brass`, `parchment-oxblood`, and `porcelain-carbon`. Use `--color-system custom --color-tokens <CSS_FILE>` for a user-supplied collection. This single project-level name is propagated to all scenes and recorded in `.style-reference/video-composition/COLOR-SYSTEM.json`. The supplied CSS defines the complete `--palette-*` contract from `STYLE.md`; layout geometry is unchanged.

After content authoring, switch the whole project without scaffolding again:

```bash
node scripts/set-color-system.mjs --project . --color-system black-gold
```

## Edit an executable starter

Each selected proof has a matching file under `.style-reference/video-composition/layouts/source/`. The scaffold copies that executable contract into the real scene.

- `C` starters fuse the installed official component into the scene and bake their initial variable defaults into the frame. Replace only marked `default` values there.
- `M` starters do the same with the supplied content adapter that combines the mapped official text behaviors.
- `B` starters copy the official block per scene. Edit only visible literals or data inside the marked slot.
- Never edit a shared installed source or the official behavior structure after scaffolding.
- Keep scene ID, host mount, timeline key, duration, and motion sidecar aligned. Scaffolding also extends every child clip authored for the component's full original window to the requested scene duration, preventing a shorter inner clip from disappearing during the hold.
- Preserve complete labels, axes, legends, sources, uncertainty, and final values. Reselect or split before shrinking required copy below readable video size.

Do not trace a proof PNG into new DOM. The proof verifies the settled visual result; the linked starter preserves the executable HyperFrames behavior.

## Existing authored projects

Stage dependencies and references without overwriting the host:

```bash
node <SKILL_DIR>/scripts/stage-authoring-kit.mjs \
  --project <HYPERFRAMES_PROJECT> \
  --presenter on \
  --language en \
  --layouts data/time-series,text/source-quote \
  --content-font /absolute/path/to/licensed-content-font.woff2 \
  --install \
  --clean-managed
```

Omit the font after it has been staged. The command keeps the managed content font, reuses valid installed Registry items, and writes `SELECTION.md` plus `REGISTRY-INSTALLS.json`. It does not modify `index.html`.

Migrate a scene by copying one selected executable starter and reconciling its IDs and duration with the existing host. If the existing host has bespoke shared geometry, integrate one scene first and run Preflight before repeating the operation.

## Review with one deterministic entry point

```bash
node scripts/review-project.mjs --project . --phase preflight
node scripts/review-project.mjs --project . --phase static
node scripts/review-project.mjs --project . --phase preview
node scripts/review-project.mjs --project . --phase release
```

- `preflight` runs package contract, local-font, path, timing, and sidecar checks plus one HyperFrames lint command.
- `static` captures every selected scene once and writes a contact sheet.
- The first `preview` runs one complete HyperFrames check with contrast at derived scene midpoints.
- A later `preview` compares shared and per-scene fingerprints. It reuses the result when nothing changed, checks only changed scenes when shared sources did not change, and falls back to full coverage when a shared dependency changed.
- `release` reuses current successful Preview coverage; changed or incomplete coverage triggers the required check.

Each phase writes `report.json` and `summary.md`. Run a manual `--scenes id,id` only when deliberately overriding automatic selection. Start one persistent preview after Preview succeeds, and run native HyperFrames render only after user approval.

## Boundaries

- No content JSON, coordinate mapper, or content-to-layout renderer.
- No title chrome or decorative rail without source-required meaning.
- No presenter-free comparison composition for a presenter scene.
- No downscaled full presenter, floating crop, cropped official item, or hidden required content.
