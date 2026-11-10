# Typography and font portability

## Curated local Latin bundle

assets/fonts/ contains pinned Fontsource WOFF2 files, per-family SIL Open Font
License notices, FONT-LICENSES.md and a SHA-256 manifest. kit.py copies the bundle
into the project without network access. Retain notices with source handoffs.

- **Bodoni Moda:** high-contrast editorial display and italic accents.
- **Familjen Grotesk:** labels, information and compact sans-serif body copy.
- **Big Shoulders Display:** oversized condensed sports/launch display.
- **Source Serif 4:** readable serif body copy and a free Times-like alternative.

Use actual supplied weights. Do not assume a commercial family is available or
embeddable merely because Canva, Adobe or an upstream CSS stack names it. No
commercial font binaries or upstream example WOFF2 files are redistributed here.

## Chinese

The Latin bundle does not include CJK glyphs. For Chinese work, add an appropriately
licensed local CJK font (for example, an authorized Noto/Source Han distribution),
its complete license/copyright notice, source/version and hash to the project.
Use project-local @font-face URLs. Do not reference a machine-specific absolute
font path or silently depend on another user's system font installation.

Set lang="zh-CN" and assign CJK families to display/body/label roles. As a starting
point use roughly 10–11 pt body and 1.5–1.7 leading, then assess at finished size.
Chinese characters are wider than Latin letters: shorten display lines, rebalance
columns and remove Latin letter-spacing/text-transform where unsuitable. Check
punctuation, mixed Latin/numerals, rare characters, weight, fallback and line breaks.

## Verification

Wait for local fonts to load; inspect every rendered page and the PDF font report.
A font-ready promise does not prove coverage of every character. Unexpected
DejaVu/Liberation/etc. in the PDF may reveal a failed intended face; if such a family
is intentionally the user's licensed brand font, declare it via --brand-fonts and
review the actual output. Confirm embedding with pdffonts. No font-service login,
implicit download or global font installation is part of this skill.
