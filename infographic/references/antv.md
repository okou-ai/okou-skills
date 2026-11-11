# AntV: native DSL → PNG, SVG, HTML

Use this route for editable geometry and exact text. Copy one starter, replace its content, render, then inspect the PNG. These six layouts are tested examples, not a promise that every AntV template or style fits every dataset.

## Setup

From this skill directory:

```bash
npm ci
node scripts/render.mjs --help
```

Dependencies are pinned to `@antv/infographic@0.2.20` and `playwright-core@1.65.0`. Node 22.12.0+ is required for AntV's CommonJS-to-ESM dependencies. Chromium must already be installed separately. No browser or global package is installed by this helper.

Browser lookup: `--chromium`, then `CHROMIUM_PATH`, then `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH`, then common Chrome/Chromium installation paths and executable names on `PATH`. An invalid explicitly configured path fails rather than silently falling back.

Install suitable system fonts before rendering. The supplied starters use `sans-serif`; `Noto Sans CJK SC` was also tested for Chinese. AntV's registered CDN font URLs are disabled through its public font API. A font name is not a font download; absent fonts may fall back or show missing glyphs, which require visual inspection.

## Render

Keep authored files outside the installed skill directory:

```bash
cp templates/process.antv /absolute/task/graphic.antv
# Edit graphic.antv; replace every example fact and label.
node scripts/render.mjs \
  --input /absolute/task/graphic.antv \
  --out /absolute/task/rendered \
  --width 1600 --height 900 --scale 2 \
  --copy '["Your exact title","Your exact label"]'
```

`--copy /absolute/task/copy.json` also accepts a UTF-8 JSON file containing the same array. Include all required visible strings, including numbers, units, captions and qualifications. Matching is case-sensitive, without whitespace or punctuation normalization: each required string must be a contiguous substring of one visible text element **in the exported SVG**, not merely present in the embedded source. It does not check occurrence counts, invented extra labels or factual correctness.

| Flag | Meaning |
| --- | --- |
| `--input` | Required native `.antv` file; nonempty UTF-8, up to 1 MB. Supplied HTML is never executed. |
| `--out` | Required output directory; created when rendering starts. Reusing it overwrites the four named outputs. |
| `--width`, `--height` | Canvas dimensions; defaults `1600`, `900`; integers `64–8192`. Override DSL canvas dimensions. |
| `--scale` | PNG device scale, default `1`, range `0.25–4`; at most 64 million output pixels. SVG/HTML retain canvas dimensions. |
| `--copy` | Optional JSON string array, or path to its JSON file. Nonempty strings only. |
| `--chromium` | Explicit browser executable. No automatic browser downloads. |
| `--no-sandbox` | Explicit opt-out for a trusted container that cannot run Chromium's sandbox. **Not the default.** |

The trusted-container smoke tests used `--chromium /usr/bin/chromium --no-sandbox` explicitly. Use this opt-out only where needed; do not carry it into ordinary environments or silently retry a failed sandboxed launch without it.

## Choose and edit a starter

Native syntax is indentation-based, not YAML, JSON or a generic diagram schema. Use two-space indentation, `key value` lines, and `- label Text` list entries. Put the title and caption in `data.title` and `data.desc`. Text after the key is literal; do not add YAML-style quote characters unless wanted. Preserve nesting when changing content.

| File | Tested built-in template | Required data shape |
| --- | --- | --- |
| `templates/process.antv` | `sequence-steps-badge-card` | `data.sequences`: ordered entries with `label`, `desc`. Horizontal arrows follow source order. |
| `templates/comparison.antv` | `compare-hierarchy-left-right-circle-node-plain-text` | `data.compares`: **two** groups, each with `label` and `children` containing criterion `label`s. Use the same criterion order on both sides; these nodes do not display separate item descriptions. |
| `templates/timeline.antv` | `sequence-timeline-simple` | `data.sequences`: `label` contains the actual date/event; `desc` contains detail. Author chronological order yourself; no date parsing or automatic sorting. Its native `simple` item retains descriptions. |
| `templates/hierarchy.antv` | `hierarchy-tree-tech-style-rounded-rect-node` | One `data.root` object with `label` and recursive `children`. Node text is label-only. Keep `design.title default` so the title/caption is included. |
| `templates/relation.antv` | `relation-dagre-flow-lr-compact-card` | `data.nodes`: unique `id`, `label`, `desc`; `data.relations`: explicit `from`/`to` entries referencing those IDs. Arrows mean the relationship you describe, not automatically causation. |
| `templates/list.antv` | `list-grid-badge-card` | `data.lists`: independent `label`, `desc` entries. Native `design.structure.columns 3` controls the grid. |

For example, relation entries are nested like this:

```text
  nodes
    - id a
      label Evidence
    - id b
      label Decision
  relations
    - from a
      to b
```

Change `theme.colorBg`, `colorPrimary`, `palette`, and `theme.base.text.font-family` for styling. The starters show their exact nesting. Keep labels short; AntV auto-fits native geometry into the canvas. Enlarging the canvas alone does not repair dense content, long labels or incorrect item sizing. Native item props such as `design.item.width` change layout units; font-size overrides may require matching layout changes and a fresh visual check.

All six starters are icon-free and render offline. For a custom illustration, use a vetted inline SVG resource in the native `icon`/`illus` field supported by the selected item, for example `icon data:image/svg+xml,<percent-encoded-safe-svg>` (encode with `encodeURIComponent(svg)`). A percent-encoded local SVG icon was tested and retains SVG paths; base64 SVGs are instead treated by AntV as image assets. This does not make every item illustration-capable. Keep the SVG self-contained: no scripts, event attributes, stylesheets, links, animations or remote resources. Outgoing browser requests are blocked; attempted remote icons/fonts fail instead of being silently omitted. Do not feed untrusted HTML to the browser or depend on a public CDN.

The template name must match an installed built-in exactly; this helper rejects AntV's fuzzy template-name fallback. If using a different native template, check its real data fields and verify every required string with `--copy`. No custom schema or registration layer is supplied.

## Outputs and checks

- **`infographic.png`**: screenshot of the actual exported SVG, after AntV's `loaded` event, font readiness and browser paint. Dimensions are recorded in `qa.json`; `1600×900 --scale 2` produces `3200×1800` pixels.
- **`infographic.svg`**: real AntV vector geometry and text, including `foreignObject` text. Native `data.title`/`data.desc` are exported with the diagram; there is no separate HTML-only title or footer. Add any required source caption inside supported native data, not outside the SVG. This uses browser text layout; Illustrator import fidelity or native editable PPTX objects are **not promised**. Some non-browser SVG editors do not support `foreignObject` accurately.
- **`infographic.html`**: self-contained local browser source with the native DSL stored as safely escaped JSON, the pinned browser bundle embedded, and AntV's full MIT license retained. Edit the original `.antv` and rerender for durable revisions; this is not a custom source editor. Native engine edits do not update the `.antv` file. Preserve the embedded license and the package's `licenses/antv-MIT.txt` when redistributing bundled library/source material.
- **`qa.json`**: engine/browser versions, actual dimensions, errors, visible text, missing required strings, viewport/CSS-overflow clipping and text extending outside its declared box. Invalid CLI/input syntax fails before rendering. Render failures exit nonzero and save diagnostics once the output directory has been initialized; stale PNG/SVG/HTML outputs are removed before a new render.

`status: "passed"` means **automatic checks passed only**. `visualReview.status` remains `"required"`. Geometry uses browser text ranges and axis-aligned viewport/CSS-overflow bounds; it is not a full SVG clip-path, overlap, contrast, missing-glyph or legibility proof. `outsideTextBoxes` can flag visible overflow for review even when no clipping is detected. Always open the PNG and check all copy, arrows, hierarchy, spacing, overlap, font size and meaning before delivery.

## Smoke tests

Set your installed browser path. Only add the test sandbox opt-out in the trusted container described above:

```bash
CHROMIUM_PATH=/usr/bin/chromium \
ANTV_TEST_NO_SANDBOX=1 \
ANTV_TEST_OUT=/absolute/task/test-artifacts \
npm test
```

Without `ANTV_TEST_NO_SANDBOX=1`, the browser sandbox stays enabled. Tests cover argument/file/syntax rejection, a minimal real render, all authored copy in all six starters, PNG scaling, inline/file `--copy`, missing-copy and empty-output failures, early engine errors, blocked remote resources, safe inline SVG, and offline HTML source preservation with Chinese and script-like text. `ANTV_TEST_OUT` keeps screenshots and diagnostics for inspection; otherwise tests use a temporary directory. These are smoke/automatic checks, not visual approval or a paid image-generation test.
