---
name: video-composition
description: "Compose a video with HyperFrames from an executable layout library, with generated voice or a talking avatar and a deterministic review. Use when Okou composes the video itself: exact pages, frames, timing or geometry, voice-over with no digital human, a retained source track, or a binding duration."
---

# Video Composition

## Workflow ownership

This owns the workflow after HyperFrames. Work from the brief and sources alone, and edit the starter-based scenes inline. For a revision, retain the accepted project, scene sources, palette, voice ID, complete content font, and pinned runtime. Update the scene contract and narration for the requested change; use the existing-project path in [AUTHORING.md](references/AUTHORING.md) instead of bootstrapping again.

## Fast production workflow

### 1. Lock the scene contract, then start media immediately

Record one semantic or narration beat per scene:

`scene-id | Router layout id | presenter: off|talking-avatar | viewer outcome`

Fix silent/static scene timing now. For voice or a talking avatar, open [VOICE-AVATAR.md](references/VOICE-AVATAR.md) and generate media alongside draft assembly: authoring runs on provisional windows while media generates, then both join on measured seconds. Measured media replaces provisional estimates; it does not override a binding duration or preservation constraint. Dispatch media first once those constraints have a feasible plan.

### 2. Select from the executable layout library

Read only [ROUTER.md](references/ROUTER.md) with this file; it maps all 40 layouts to capacity, official items, motion, and presenter guidance.

- Choose the smallest sufficient row.
- If names are insufficient, inspect the [gallery](assets/layouts/index.html) or [contact sheet](assets/layouts/contact-sheet.jpg); every proof links to its executable HTML starter.
- Keep the context to this file and ROUTER.md; catalogs, media generation and generic video Skills stay closed.

### 3. Resolve presenter, palette, and language once

- Presenter `off`: no presenter DOM or reserved bay.
- Presenter `talking-avatar`: a generated transparent take, staged with bootstrap `--presenter on`; the composition supplies the background, so follow the fast path rather than any avatar output with a scene behind it.
- For `zh`, `ja`, or `ko`, reuse a complete licensed local `--content-font`. If only a font collection or source font is available, follow the short font preparation section in [AUTHORING.md](references/AUTHORING.md). Avoid a hand-picked character subset before the visible copy is complete.
- Choose one palette: `navy-cobalt`, `monumental-minimal`, `black-gold`, `obsidian-champagne`, `petrol-brass`, `parchment-oxblood`, `porcelain-carbon`, `custom`. Geometry is identical across them, so this is tone: a light field for dense figures, a dark one for a single claim, `custom` for brand colours. Name the choice before generating; define custom palettes through [STYLE.md](references/STYLE.md).

### 4. Bootstrap once

For a new or blank project, run one command from any directory:

```bash
node <SKILL_DIR>/scripts/bootstrap-project.mjs \
  --project <PROJECT_DIR> \
  --host-id <id> \
  --presenter <off|on> \
  --media-mode none \
  --color-system navy-cobalt \
  --presenter-scenes <optional-id,id> \
  --language <tag> \
  --content-font <required-for-first-zh-ja-ko-build> \
  --scenes cover:8,evidence:10,close:7 \
  --layout-map cover=orientation/headline-cover,evidence=data/kpi-grid,close=orientation/public-action-close
```

Bootstrap initializes HyperFrames, stages starters, installs deduplicated official items, isolates blocks, creates host/scene/motion contracts, records `COLOR-SYSTEM.json`, and propagates the palette; layout choice, content, and rendering stay with you.

New projects use HyperFrames **0.8.38**; revisions keep the existing project's pinned version.

For a supplied collection, use `--color-system custom --color-tokens <CSS_FILE>`; geometry is unchanged.

Recolor an authored project with `node <SKILL_DIR>/scripts/set-color-system.mjs --project . --color-system <name>`; content and scenes stay intact.

An existing authored project takes the narrow staging or migration command in [AUTHORING.md](references/AUTHORING.md) instead.

### 5. Replace scene-local content slots; preserve the layout

Each generated scene contains its stage. Bootstrap fuses components and isolates every block source.

- `C` uses a content-complete official component, `M` a content adapter combining official behaviors: replace only `default` values inside `CONTENT_SLOT`. `B` scenes: only visible literals or data inside the marked slot under `compositions/official/`.
- Ship real content in every slot; a component lacking required fields stays behind an `M` adapter. The shared installed Registry source and the frame's official mount stay as installed.
- Do not reconstruct a preview PNG with ordinary DOM.
- Keep source, host mount, timeline key, and motion sidecar IDs and durations identical.
- Defaults sit at 70–85% capacity. Replace every sample; take a smaller layout for sparse content, or split overflow.

Insert verified facts, values, units, dates, uncertainty, disclosures, and citations into the bounded slots.

### 6. Use native semantic motion

Keep background, presenter, and recurring structure settled. Preserve semantic behavior: text hierarchy, data-based charts, exact values, causal processes, shared-basis comparisons, intact geography. Open [MOTION.md](references/MOTION.md) only when required.

### 7. Run deterministic review

After the first representative scene, run Preflight before repeating that treatment:

```bash
node <SKILL_DIR>/scripts/review-project.mjs --project . --phase preflight
```

Preflight combines the package contract and font checks with HyperFrames lint, so asset paths, invalid IDs, unsupported scripts, and structural failures stop before browser sampling.

After all static content is complete:

```bash
node <SKILL_DIR>/scripts/review-job.mjs start --project . --phase static
node <SKILL_DIR>/scripts/review-job.mjs status --project . --job JOB_ID
```

The local review job survives the calling tool session and returns its own ID, log path, and state. Wait for `passed`, inspect the scene contact sheet, then start `--phase preview` with the same helper and follow its returned ID. Do not edit inputs or start another phase while a check is active. Read status at reasonable intervals while doing independent work; if interrupted, inspect the existing job log before explicitly starting another check. An old PASS report is not the state of the new job.

Preview runs the full check with contrast; a later call checks only changed scenes, or reuses the result. A changed narration file also invalidates cached review. Reports record `startedAt`, `completedAt`, and `durationMs` so tool execution can be separated from time between commands.

Start `npx hyperframes@<pinned> preview --background` only when interactive Studio review is needed and the environment provides a user-accessible URL. An unattended cloud-render build needs no local Studio server; a sandbox-local URL is not a deliverable.

If the user requested preview approval before rendering, wait for that approval. Otherwise, an authorized video-creation request or `intro-video` handoff proceeds to rendering after the checks pass, without an additional approval gate. The composition renders through Okou's managed cloud, the same path the intro-video controlled route uses. Check `okou video render --help` once; if the command or platform access is missing, report that rather than rendering locally.

```bash
node <SKILL_DIR>/scripts/review-project.mjs --project . --phase release
okou video render . --dry-run --json
okou video render . --json
```

The dry run packages and inspects the archive without spending render credits. It honours `.hyperframesignore` and leaves out generated renders, snapshots and development files, so inspect the largest included files before submitting. Submission returns a durable generation ID and the deliverable is the persisted artifact URL that job returns.

```bash
okou video render status GENERATION_ID --json
okou video render resume GENERATION_ID --json
```

Poll `status` at the interval it reports instead of resubmitting, and after an interruption continue the same ID with `resume`.

Release reuses current successful Preview coverage. Every `hyperframes` call uses the version the project pins in `package.json`, the one `review-project.mjs` resolves; a bare `npx hyperframes` floats to the latest release mid-project.

## Content and presenter invariants

- Content completeness, readable scale, and centering inside the real available region outrank presenter presence and chrome.
- Omit layout names, counters, source rails, and upper-left title blocks unless the source requires them.
- A full presenter stays at the template standard size. It may switch sides but must not be shrunk to force coexistence.
- If it does not fit, use the grounded bottom-corner `head-shoulders` treatment with the supplied soft transparent circular fade, move the person to a presenter-led divider, or omit it there.
- Keep a person grounded and whole: at rest and at motion peaks, face, hands, text, axes, legends, connectors, citations, and media stay disjoint.
- Full-canvas Registry blocks remain presenter-free.

## Open an exception guide only when needed

- [AUTHORING.md](references/AUTHORING.md): existing projects, staging, migration, capacity exceptions.
- [PRESENTER-ADAPTATION.md](references/PRESENTER-ADAPTATION.md): ambiguous presenter recurrence or fit.
- [MOTION.md](references/MOTION.md): native motion is inadequate or fails inspection.
- [LAYOUT-CATALOG.md](references/LAYOUT-CATALOG.md), [HYPERFRAMES-LAYOUT-MAP.md](references/HYPERFRAMES-LAYOUT-MAP.md), [MOTION-CATALOG.md](references/MOTION-CATALOG.md): inspect only the selected entry.
- [STYLE.md](references/STYLE.md): invent beyond supplied evidence, or correct drift.

English files are the operational source.
