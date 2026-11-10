# Upstream provenance and licenses

This is a curated **adaptation**, not an unchanged mirror, an upstream product
integration or a collection of pre-verified CTR winners. `templates/catalog.json`
contains new composite art directions built from the licensed source families
below. The compiler, exporter, tests, generic briefs and Okou execution adapter
are package-authored. No upstream application, provider code, gallery, photo,
logo or rendered sample is redistributed.

## Selection and immutable source pins

Repository stars were checked on **2026-11-10 UTC**. They describe the entire
repository, not the individual skill, number of users or visual effectiveness.
Popularity prioritizes discovery; an explicit source license and an executable,
inspectable adapted render are separate requirements. Keep all full MIT notices
in `licenses/` when copying or distributing this package.

| Source ID | Repository | Stars at check | Role | License notice |
| --- | --- | ---: | --- | --- |
| `baoyu` | [jimliu/baoyu-skills](https://github.com/jimliu/baoyu-skills/tree/ca703c2d7c2c4399a1dc0cf82224f8551e05a96d) | 27,442 | Cover composition, palette and rendering families; adapted, not a YouTube-only source | [MIT, © 2026 Jim Liu](licenses/baoyu-MIT.txt) |
| `jake` | [Jakeschincariol/youtube-agent-skill](https://github.com/Jakeschincariol/youtube-agent-skill/tree/a2feb2104981a375ffd4f87ee04f4f5344ac43c6) | 5,378 | Supporting title-thumbnail pairing and truthful claims only; not an image template/backend | [MIT, © 2026 Jake Schincariol](licenses/jake-MIT.txt) |
| `swyxio` | [swyxio/skills](https://github.com/swyxio/skills/tree/da1b8a06f9063155365338d69508e7977e984af2) | 198 | Dark thematic tech imagery and topic-to-prompt influence | [MIT, © 2026 Shawn Wang (swyx)](licenses/swyxio-MIT.txt) |
| `craig` | [TheCraigHewitt/skills](https://github.com/TheCraigHewitt/skills/tree/fdbf39b61fbc8cb7cea67949bfb5e8fc567bbc51) | 172 | Supporting design brief and mobile glance test only; not an image backend | [MIT, © 2026 Craig Hewitt](licenses/craig-MIT.txt) |
| `nanothumbnail` | [yoanbernabeu/NanoThumbnail](https://github.com/yoanbernabeu/NanoThumbnail/tree/5eb2c34bafe3f9569d858c88d6649f9f5bad5c5b) | 54 | Focused, lower-star but concrete thumbnail art-direction presets and craft workflow | [MIT, © 2025 Yoan Bernabeu](licenses/nanothumbnail-MIT.txt) |

### Exact source material

- **baoyu:** [baoyu-cover-image/SKILL.md](https://github.com/jimliu/baoyu-skills/blob/ca703c2d7c2c4399a1dc0cf82224f8551e05a96d/skills/baoyu-cover-image/SKILL.md),
  [type composition](https://github.com/jimliu/baoyu-skills/blob/ca703c2d7c2c4399a1dc0cf82224f8551e05a96d/skills/baoyu-cover-image/references/types.md),
  [screen-print rendering](https://github.com/jimliu/baoyu-skills/blob/ca703c2d7c2c4399a1dc0cf82224f8551e05a96d/skills/baoyu-cover-image/references/renderings/screen-print.md),
  [dark palette](https://github.com/jimliu/baoyu-skills/blob/ca703c2d7c2c4399a1dc0cf82224f8551e05a96d/skills/baoyu-cover-image/references/palettes/dark.md)
  and [digital rendering](https://github.com/jimliu/baoyu-skills/blob/ca703c2d7c2c4399a1dc0cf82224f8551e05a96d/skills/baoyu-cover-image/references/renderings/digital.md).
- **nanothumbnail:** actual [STYLES art-direction array](https://github.com/yoanbernabeu/NanoThumbnail/blob/5eb2c34bafe3f9569d858c88d6649f9f5bad5c5b/src/app/lib/styles.ts),
  [prompt construction](https://github.com/yoanbernabeu/NanoThumbnail/blob/5eb2c34bafe3f9569d858c88d6649f9f5bad5c5b/src/app/lib/prompt.ts)
  and [thumbnail craft](https://github.com/yoanbernabeu/NanoThumbnail/blob/5eb2c34bafe3f9569d858c88d6649f9f5bad5c5b/skills/nanothumbnail/references/craft.md).
- **swyxio:** [youtube-thumbnails/SKILL.md](https://github.com/swyxio/skills/blob/da1b8a06f9063155365338d69508e7977e984af2/youtube-thumbnails/SKILL.md).
- **jake:** [yt-package/SKILL.md](https://github.com/Jakeschincariol/youtube-agent-skill/blob/a2feb2104981a375ffd4f87ee04f4f5344ac43c6/skills/yt-package/SKILL.md).
- **craig:** [youtube/thumbnail-design/SKILL.md](https://github.com/TheCraigHewitt/skills/blob/fdbf39b61fbc8cb7cea67949bfb5e8fc567bbc51/youtube/thumbnail-design/SKILL.md).

All five root licenses were read as complete MIT texts at the pinned commits,
not inferred from search snippets or a README badge. The corresponding complete
texts are retained locally above. These are source-code/document permissions;
they do not grant rights in third-party faces, brands, videos, sample artwork or
model outputs, nor permission to use an upstream account.

## Template lineage and local changes

All six templates are adaptations. Each entry's `source_ids` names its source
influences, not a claim that the full local direction is literal upstream text.

| Local template | Exact upstream family | Package-authored adaptation |
| --- | --- | --- |
| `tech-after-hours` | NanoThumbnail `tech`; swyx dark thematic tech prompt | Replace creator/brand with an original fictional robot or supplied subject; introduce the after-hours workspace, warm practical light, 43% quiet left zone, chartreuse accent and simpler props. Remove Latent Space branding, logo searches, date footer, Gemini web and Studio upload. |
| `product-spotlight` | baoyu `hero` composition; NanoThumbnail `reaction` hero-object separation | Use a product-only concept rather than a mandatory face; set three-quarter geometry, right-side placement and generic-product/reference-fidelity rules. |
| `versus` | NanoThumbnail `versus` | Preserve equal-scale split comparison; make colors configurable and remove the mandatory central VS badge unless explicitly requested as overlay copy. |
| `before-after` | NanoThumbnail `before-after` | Preserve matched framing and muted/bright states; add a headline zone and supported-transformation rules. No invented health, money or performance result. |
| `cinematic-mystery` | NanoThumbnail `cinematic`; baoyu dark palette + digital rendering | Combine atmospheric cool/warm depth with a large phone-readable object, quiet text half and non-sensational intrigue. |
| `bold-editorial` | baoyu `metaphor` / `minimal` types + `screen-print` rendering | Adapt article-cover vocabulary to a short YouTube hook, three-color object metaphor, restrained texture and duration-safe export. Do not copy an existing poster or artist's named work. |

The supporting `jake` and `craig` sources inform briefing/QA, not the art-direction
count. Do not describe five source repositories as five separately executed
generators or call the 54-star NanoThumbnail repository broadly high-star.

## Deliberate exclusions

- **inference-sh/skills** (805 repository stars at check): inspected at
  `0cbf91c26ada28702c79962406286f0c14292150`; no complete repository-specific
  LICENSE/COPYING/NOTICE grant was found in the complete tree. A README MIT badge
  was insufficient for this import. **No material from that guide is included.**
- **aiagentwithdhruv/skills** (22 stars, MIT): optional niche prompt material,
  omitted to avoid a fixed creator identity, mandatory laptop/clothing and
  clutter-heavy duplicate tech direction. The separate face-swap workflow is
  outside scope; an MIT code license does not clear downloaded thumbnails/faces.
- **deeployCO/youtube-seo-skills** (22 stars, MIT): analysis workflow rather than a
  finished image-template family. No CV/CLIP dependency or unvalidated CTR score
  was imported; its documentation advertises features beyond the inspected code.
- **AgriciDaniel/claude-youtube** (731 stars, MIT): the thumbnail sub-skill is
  primarily a brief with conditional external MCP generation. Omitted as a
  duplicate supporting source, not counted as a tested image backend.

## Execution and effectiveness boundary

The adapted templates execute through the available runtime image backend. They
do not install or test NanoThumbnail MCP/studio, Gemini web, inference.sh belt,
YouTube uploads, baoyu provider adapters or any upstream analytics service.

Live sample prompts, output images, failures and fixes are maintained separately
under `docs/ai-youtube-thumbnail-generator/` in this repository. A successful
render and mobile review validate an example's usability, **not** audience CTR,
retention, statistical significance, universal likeness preservation or a fixed
provider/model's availability. Follow current runtime consent and billing rules.
