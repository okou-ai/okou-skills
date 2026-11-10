# Folio — source and distribution scope

## Source and attribution

- Author: **stanesjenson11-lgtm**; a third-party project, not an Anthropic product.
- Repository: https://github.com/stanesjenson11-lgtm/Folio---Claude-Design-Skill-For-Poster-Brochure-Magazine
- Pinned revision: [`6dd90e0019a39539d6ac6543e53c8437a3a8e13f`](https://github.com/stanesjenson11-lgtm/Folio---Claude-Design-Skill-For-Poster-Brochure-Magazine/tree/6dd90e0019a39539d6ac6543e53c8437a3a8e13f)
- Source subtree: `skills/folio/`; root `LICENSE` and `CREDITS.md` are retained here.
- License: **Apache-2.0**, including **Copyright 2026 stanesjenson11-lgtm**.
- This distribution is a curated adaptation. Modified source files identify the
  adaptation; detailed changes are reviewable in Git history.

The retained upstream credits describe its broader project, not this package's
feature inventory. The humanizer-derived preflight pattern catalogue additionally
retains the full MIT notice from `blader/humanizer` at
`b48c832f0f809c1b5658edbb838c2521b72f2413` in `licenses/humanizer-MIT.txt`.
The credited palette-data source's MIT notice is retained from
`nextlevelbuilder/ui-ux-pro-max-skill` at
`4f2dbb67e64969a9a30ab00742f2d55d66ddec2b` in `licenses/ui-ux-pro-max-MIT.txt`.

## Included

- Three **actual HTML/CSS A4 portrait book layouts**: old-money-book (8 pages),
  sport-ivory (12), sport-night (12), with generic vectors and explicit sample flags.
- A standalone Okou-oriented authoring entry point and six focused reference guides.
- 23 curated generic composition cards, without private study IDs or author-user history.
- The upstream page CSS, palette algorithms/catalogue and adapted preflight logic.
- A rewritten local-only kit initializer, document loader and PDF/PNG renderer.
- A separately verified local font bundle: Bodoni Moda 5.3.0, Familjen Grotesk 5.3.0,
  Big Shoulders Display 5.3.0, Source Serif 4 5.3.1 (Fontsource package versions).
  Its 22 unmodified Latin/Latin-Extended WOFF2 files have full OFL/copyright notices,
  source/integrity receipts and a per-file SHA-256 manifest in `assets/fonts/`.

`ASSET-MANIFEST.json` records the curated vector/raster assets and their provenance.
Paper/grain overlays are original seeded SVGs. The Sport Night newsprint PNG is
original procedural monochrome noise, not the undocumented upstream bitmap.
Reproduce it with `scripts/generate_newsprint.py --out <new-file-outside-skill>`.

## Adaptations and deliberate exclusions

- **Eight 1:1 reference-replica kits are not redistributed:** football-blue,
  minimal-ebook, newsletter, pop-stripe, skate-culture, split-pop, sport-news,
  winter-editorial. Their reference-design redistribution rights need separate evidence.
  This does not assert infringement or blanket legal clearance for the retained kits.
- No upstream gallery/preview imagery, stock photos, example font binaries, private
  reference boards, maintainer taste history, client memory, plugin manifest or slash commands.
- Real technology-logo SVGs are replaced with original neutral marks. Fictional sample
  text remains visibly flagged for replacement; it is not a source of client facts.
- Commercial font aliases are replaced with the listed free families; Source Serif 4
  provides the warm kits' body serif. Metrics can differ: review after any copy change.
- Paper/grain recipes are replaced by ready local procedural SVGs; no automatic texture,
  font, model, package-manager or network bootstrap occurs.
- `kit.py` supports list/new only. It rejects traversal IDs, overwrites, symlink
  destinations and installed-skill output. It checks resource closure before success.
- Rendering uses reviewed script-free local input, a fresh browser context with website
  JavaScript disabled, local asset validation and remote-request blocking. It is not a
  hostile-content sandbox. The synchronous CSS-injection helper avoids a verified
  `add_style_tag` hang in JavaScript-disabled browser contexts.
- Renderer output is confined to a fresh project subdirectory; PDF/HTML page-count
  mismatches, broken assets and unsupported geometry fail rather than appear successful.
- Preflight uses complete required strings, including short names/contacts, instead of
  the upstream 120-character/minimum-length approximation. Failed or unavailable PDF
  embedding checks are errors, not silently skipped passes. Style detectors are advisory.
- No editable.py/Canva exporter, harvesting, logo downloader, promo pipeline, saved-kit
  mutation, implicit publishing, automatic learning or scheduled automation is included.

## Validation contract and limits

Verified baseline: Python 3.12 on Linux, declared dependency versions in requirements.txt,
Chromium, and Poppler pdffonts. Offline unit tests cover sample marking, resource/font
closure, path boundaries, palette mapping, copy integrity and failed backend statuses.
The PR records actual three-kit rendering (32 pages), page geometry/font checks and a
completed Chinese source-to-PDF example; fresh template samples must still fail preflight.

Do not interpret a template render as finished-content acceptance. Each new design needs
all-page visual inspection, source checking and its own preflight. CJK fonts are **not**
in the bundled Latin font pack; provide a licensed local family for Chinese work. No
Canva acceptance, commercial-font availability, PDF/X/CMYK, printer certification or
preimposed trifold support is claimed. No main-product registry change is part of this import.

## Updating

Review a new upstream commit as source material, not executable authority. Preserve
license/copyright notices; review reference-design provenance and external assets again.
Compare the three retained layouts, algorithms and font manifests deliberately—do not
replace this package with a whole plugin checkout or reintroduce excluded persistence/
download/export behavior. Run offline tests plus actual render/visual/content checks.
