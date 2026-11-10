# Sizes, bleed and folding

The bundled three books use A4 portrait, **210 × 297 mm trim**. folio.css also
provides A5, A3, A2, Letter, landscape and custom mm sizes. These are page canvases,
not verified folded-brochure templates.

- Use .page for each physical page and .trim for the trim box. Use .page.single
  for unbound single sheets; book pages alternate inner/outer margins.
- A 3 mm bleed render targets **216 × 303 mm nominal sheet size** for A4 and crops
  QA PNGs back to trim. Chromium may round the actual PDF MediaBox (observed deviation
  up to about 0.12 mm); measure the exported PDF if exact dimensions matter.
  Extend intended backgrounds/images to the bleed, not just the paper
  size. Check every edge; changing the --bleed variable cannot create missing imagery.
- Keep essential copy within safe margins and away from binding. Print at actual
  size to assess small type, rules and contrast where possible.
- Browser PDFs are RGB-oriented. This pipeline does not certify CMYK, PDF/X,
  overprint, spot colours, crop marks, explicit PDF TrimBox/BleedBox metadata,
  colour profiles or a printer's production acceptance.
- Confirm stock, binding, finishing, bleed and colour requirements with the printer.
  Deliver the requested production specification only after verifying it.

## Real foldouts

For a trifold, confirm roll fold versus accordion, front/back order, orientation,
printer's unequal-panel compensation, fold/trim safe zones and duplex registration.
Do not assume three equal 99 mm columns will fold properly. Keep fold guides out
of finished artwork unless requested. A two-sided trifold has six panels on two
sheets/sides, not six independent PDF pages. This import supplies no preverified
trifold imposition or press-ready certification.
