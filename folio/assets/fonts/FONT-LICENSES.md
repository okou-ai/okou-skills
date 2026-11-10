# Curated free-font bundle

All four families are distributed under **SIL Open Font License 1.1 (OFL-1.1)**. Only the selected unmodified Latin and Latin Extended WOFF2 files are included. Source Serif 4 italic 400 is included for body-copy emphasis.

## Pinned sources

Current npm versions and their exact tarball URLs were fetched and recorded in `metadata/pins.json` **before any tarball download**. Requests were restricted to `registry.npmjs.org`. Tarball SHA-512 SRI and SHA-1 both matched npm metadata before archive reading. Per-file SHA-256 values are in `manifest.json`.

| CSS family | npm package / pinned version | Faces | Original full license |
|---|---|---|---|
| Bodoni Moda | `@fontsource/bodoni-moda@5.3.0` | 400 normal, 500 normal, 400 italic | [bodoni-moda/LICENSE](bodoni-moda/LICENSE) |
| Familjen Grotesk | `@fontsource/familjen-grotesk@5.3.0` | 400 normal, 500 normal, 600 normal, 700 normal | [familjen-grotesk/LICENSE](familjen-grotesk/LICENSE) |
| Big Shoulders Display | `@fontsource/big-shoulders-display@5.3.0` | 800 normal, 900 normal | [big-shoulders-display/LICENSE](big-shoulders-display/LICENSE) |
| Source Serif 4 | `@fontsource/source-serif-4@5.3.1` | 400 normal, 400 italic | [source-serif-4/LICENSE](source-serif-4/LICENSE) |

## Copyright and reserved-name verification

The complete OFL body (preamble, definitions, all five conditions, termination and final disclaimer) was compared against standard OFL 1.1 wording, ignoring only whitespace and decorative separators. All four matched. Original package `LICENSE` files are retained byte-for-byte. Every retained font was decoded read-only using system FreeType; its copyright, family names, OS/2 weight and italic flag were checked. Detailed evidence: `metadata/license-verification.json` and `metadata/font-inspection.json`.

### Bodoni Moda

Package license attribution, retained verbatim: Bodoni Moda `LICENSE` and `metadata/bodoni-moda/metadata.json`.

Embedded font copyright notice(s):

> Copyright 2020 The Bodoni Moda Project Authors (https://github.com/indestructible-type/Bodoni)

Also retained in `bodoni-moda/COPYRIGHT.txt`.

No additional reserved-name declaration was found in the retained LICENSE or font copyright records; this is not a claim about uninspected upstream materials.

### Familjen Grotesk

Package license attribution, retained verbatim: Familjen Grotesk `LICENSE` and `metadata/familjen-grotesk/metadata.json`.

Embedded font copyright notice(s):

> Copyright 2021 The Familjen Grotesk Project Authors (https://github.com/Familjen-Sthlm/Familjen-Grotesk)

Also retained in `familjen-grotesk/COPYRIGHT.txt`.

No additional reserved-name declaration was found in the retained LICENSE or font copyright records; this is not a claim about uninspected upstream materials.

### Big Shoulders Display

Package license attribution, retained verbatim: Big Shoulders Display `LICENSE` and `metadata/big-shoulders-display/metadata.json`.

Embedded font copyright notice(s):

> Copyright 2019 The Big Shoulders Project Authors (https://github.com/xotypeco/big_shoulders)

Also retained in `big-shoulders-display/COPYRIGHT.txt`.

**Upstream packaging detail:** the package LICENSE header and package attribution say only `Google Inc.`. This generic header has not been replaced or treated as the original author notice; the fuller embedded copyright above is additionally preserved.

No additional reserved-name declaration was found in the retained LICENSE or font copyright records; this is not a claim about uninspected upstream materials.

### Source Serif 4

Package license attribution, retained verbatim: Source Serif 4 `LICENSE` and `metadata/source-serif-4/metadata.json`.

Embedded font copyright notice(s):

> © 2014 - 2021 Adobe Systems Incorporated (http://www.adobe.com/), with Reserved Font Name ‘Source’.

Also retained in `source-serif-4/COPYRIGHT.txt`.

**Upstream packaging detail:** the package LICENSE header and package attribution say only `Google Inc.`. This generic header has not been replaced or treated as the original author notice; the fuller embedded copyright above is additionally preserved.

**Reserved Font Name:** `Source`, explicitly stated in every retained font copyright record. Font data and name tables are unchanged.

## Family naming

CSS uses the exact Fontsource-provided family names, not arbitrary replacement names. Internal font naming is documented rather than edited:

- **Bodoni Moda:** the supplied static instances use typographic family `Bodoni Moda 11pt`; the 500 instance has legacy family `Bodoni Moda 11pt Medium`. CSS retains Fontsource’s public `Bodoni Moda` alias.
- **Familjen Grotesk:** internal legacy family names can carry Medium/SemiBold suffixes; CSS groups the real 400/500/600/700 faces under `Familjen Grotesk`.
- **Big Shoulders Display:** this package’s static instances report typographic family `Big Shoulders Display Thin`, with ExtraBold/Black subfamilies. The actual OS/2 weights are **800/900**, not Thin. CSS retains Fontsource’s public `Big Shoulders Display` alias and verified numeric weights.
- **Source Serif 4:** internal family is `Source Serif 4`; normal/italic and reserved name `Source` are preserved.

These CSS family aliases come from the package CSS; no font binaries, internal names, formats or glyphs were modified.

## Reuse obligations

- Keep the full family `LICENSE` plus `COPYRIGHT.txt` with distributed font files; preserve embedded notices.
- OFL permits use, embedding and redistribution, including in commercial projects; these are not proprietary/commercial-license font files. Do not sell the fonts by themselves.
- Modified font software must remain under OFL; reserved names require the corresponding permission for a modified version. No modifications were made here.
- The copyright holders/authors must not be used to endorse modified versions without permission.
- Documents or artwork made using these fonts are not forced under OFL.

## Integration

Copy this directory intact and load `fonts.css`. Every runtime `src` URL is relative to that CSS file; no CDN, `@import`, remote URL, `.woff`, or `local()` source is used. `unicode-range` is copied exactly from the matching package CSS subset blocks. Use only the listed weights/styles to avoid synthetic faces.

```html
<link rel="stylesheet" href="./curated-fonts/fonts.css">
```

Do **not** import CSS stored under `metadata/`: those files are verbatim upstream provenance receipts and intentionally still reference other subsets/formats not included in this bundle. Only the root `fonts.css` is the portable runtime stylesheet.

## Evidence and scope

- `manifest.json`: one record per WOFF2 with family, weight/style/subset, package/version, pinned tarball URL, SHA-256, license/copyright paths and unicode range.
- `metadata/*.npm.json` and `*.metadata-receipt.json`: raw registry metadata, headers, retrieval time and metadata hash.
- `metadata/*.tarball-receipt.json` and `downloads.json`: exact source URLs, timestamps, whole-tarball hashes, verified integrity and original member-to-local-file hashes.
- `metadata/<family>/`: original package JSON, font metadata, unicode metadata (when supplied) and selected-face CSS receipts.
- `metadata/font-inspection.json`: actual name tables and binary weight/style inspection for every font.
- `metadata/license-verification.json`: full OFL verification and copyright/reserved-name findings.
- `metadata/validation.json`: final local validation results.

Archives were read in memory using safe member reads, never filesystem extraction. Absolute/traversal paths, duplicate paths, symlinks/hardlinks, special files and excessive sizes were rejected. No package code was executed, no package manager/install was used, and tarballs were not retained. No proprietary fonts or photos are present. All outputs are confined to this directory; no target repository, PR, merge, upload, hosting or publication was touched.
