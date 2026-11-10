# Local font licenses

These are **unmodified Latin and Latin Extended WOFF2** files under SIL Open Font
License 1.1. Load `fonts.css`; all font URLs are local. Chinese needs a separately
licensed CJK family. Package versions, source tarballs, integrity values, file
SHA-256, family/weight/style and Unicode ranges are in [manifest.json](manifest.json).

| CSS family | Pinned Fontsource package | Faces | Full license | Copyright notice |
| --- | --- | --- | --- | --- |
| Bodoni Moda | `@fontsource/bodoni-moda@5.3.0` | 400/500 normal; 400 italic | [bodoni-moda/LICENSE](bodoni-moda/LICENSE) | [bodoni-moda/COPYRIGHT.txt](bodoni-moda/COPYRIGHT.txt) |
| Familjen Grotesk | `@fontsource/familjen-grotesk@5.3.0` | 400/500/600/700 normal | [familjen-grotesk/LICENSE](familjen-grotesk/LICENSE) | [familjen-grotesk/COPYRIGHT.txt](familjen-grotesk/COPYRIGHT.txt) |
| Big Shoulders Display | `@fontsource/big-shoulders-display@5.3.0` | 800/900 normal | [big-shoulders-display/LICENSE](big-shoulders-display/LICENSE) | [big-shoulders-display/COPYRIGHT.txt](big-shoulders-display/COPYRIGHT.txt) |
| Source Serif 4 | `@fontsource/source-serif-4@5.3.1` | 400 normal/italic | [source-serif-4/LICENSE](source-serif-4/LICENSE) | [source-serif-4/COPYRIGHT.txt](source-serif-4/COPYRIGHT.txt) |

Retain each full `LICENSE`, `COPYRIGHT.txt` and embedded notice with font
redistribution. OFL allows use, embedding and redistribution, including commercial
work; it does not require the resulting document to be OFL. Do not sell fonts by
themselves or imply author endorsement. Modified fonts remain subject to OFL and
reserved-name restrictions. **Source Serif 4 reserves the name `Source`.**

CSS aliases follow the Fontsource package CSS without renaming font binaries:
Bodoni Moda's internal family includes `11pt`; Familjen's legacy names include
weight suffixes; Big Shoulders' internal typographic name contains `Thin`, but
its actual supplied OS/2 weights are 800/900. Use listed weights/styles, not the
internal-name wording. Source Serif retains its original family and reserved name.
The full embedded author copyrights are preserved alongside package licenses,
including where the original package license header only says `Google Inc.`.

Download/build logs are intentionally not shipped; the manifest retains exact
sources and hashes. No runtime fetch, package execution or font conversion is needed.
