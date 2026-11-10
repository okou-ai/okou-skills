# Acceptance and diagnostic checks

## Gate order

1. All source facts and exact required strings are accounted for.
2. Every sample text, image, portrait and mark slot is actually replaced/verified.
3. All HTML/CSS/SVG/font dependencies are local and their provenance is documented.
4. Rendering creates the expected fresh PDF/PNG set with matching page count and size.
5. Every page image is inspected for glyphs, clipping, overlap, crop, contrast and rhythm.
6. Preflight has zero structural ERRORs. Review warnings individually; intentional
   minimal palettes, type choices and decorative rules are not automatically defects.
7. With a PDF, run --pdf and verify pdf_fonts.status=passed. Missing/failed pdffonts
   is a failed mandatory font check, not success. With --copy, require copy.status=passed.
8. Independently check exported PDF text, geometry/order and any requested print spec.

The preflight includes inherited heuristic style detectors. Their suggestions are
advisory and can produce false positives/negatives. Its copy test verifies complete
required strings in DOM text, not semantics or all image/metadata content. Its font
check does not prove glyph correctness, licensing or printer acceptance.

## Intentional negative tests

- A fresh kit must fail with kit-sample findings; a forgotten portrait must still fail.
- Remove a referenced image/font/CSS texture: initialization/loading must fail.
- Alter the end of a long required sentence or omit a short contact: copy check must fail.
- Inject a script, remote image/CSS import or ../ asset escape: loader must reject it.
- Reuse a nonempty render output directory: fail rather than leave stale page PNGs.
- Fail or remove pdffonts: report the font check as failed.

## Package tests

From any working directory:

    python3 -m unittest discover -s <skill-dir>/tests -v
    python3 -m doctest <skill-dir>/scripts/palette.py <skill-dir>/scripts/preflight.py

The offline unit suite checks logic and local resource closure. It is not a
substitute for actual Chromium/PDF/visual checks. No test creates a workflow,
installs a plugin, writes personal preferences or publishes a document.
