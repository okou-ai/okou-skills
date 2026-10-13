# PDF → HTML → template package

Use the original PDF for extraction, page captures and Custom upload. The helpers
preserve pdf2htmlEX page geometry and reuse the HTML inventory/package contract.

## 1. Prepare once

From this guide's directory, run conversion and original-page capture in parallel:

```bash
python3 scripts/prepare-pdf.py --input <source.pdf> --work-dir <work-dir> --inspect
okou presentation screenshot --input <source.pdf> --out <work-dir>/source-pages
```

The converter is reused or cached from the checksum-pinned official Linux x86_64
AppImage, without root/FUSE. Other platforms can pass `--converter <executable>`.
Visual defaults stay intact; CSS, fonts and images are external files.

After capture, create contact sheets and sampled source colors in one pass:

```bash
python3 scripts/source-derivatives.py --work-dir <work-dir> --contact-sheet
```

Pillow uses the active Python or an automatically prepared work-local venv.

## 2. Review bounded evidence; write source notes

Read `pdf-html/inspection-summary.json` and `previews/source-summary.json`; review
all contact sheets. These map decimal page numbers to actual background filenames,
show dimensions, visible/hidden text counts, short source samples and sampled colors.
Open individual pages or scoped CSS only for unresolved details. Full HTML dumps,
a second inventory, converter experiments and QA implementation reads are not needed.

Type 3/scanned lettering may be painted into backgrounds with hidden glyph spans.
The report flags visibility; it cannot prove editable slots. Preserve these pages as
reference compositions and adapt only selected regions during generation.

Write `<work-dir>/source-notes.json` with these fields:

| Field | Source judgment |
| --- | --- |
| `name`, `title` | Template slug and display title |
| `designSystem` | Markdown: observed fonts/colors, backgrounds/artwork, spacing and reuse rules; label inferences |
| `qaConfig` | Source safe areas, chrome and approved fallbacks, per [qa-config.md](qa-config.md) |
| `pageRoles` | Page-number keys with roles, including the source cover/ending and distinct body families; e.g. `{"1":"cover","36":"ending"}` only if the source supports them |

## 3. Assemble and check in one command

```bash
python3 scripts/assemble-pdf.py --work-dir <work-dir> \
  --package <template-slug> --notes <work-dir>/source-notes.json
```

The helper preserves all pages/assets, creates `.slide > .pf.stage`, keeps original
`.pc` artwork outside an empty `.fit` content slot and sibling chrome slot, and writes
the index, shell and generation entrypoint. Paths resolve from `layouts/`. It installs
the shared black, centered viewer and runs the package verifier through absolute paths.
Source fragments stay explicitly reference-only until their selected content is adapted;
`PACKAGE_VALID` verifies structure, not editability or generated-deck visual quality.

`conversion.json`, `inspection.json` and `package-build.json` retain timings/evidence
outside the saved template. After `PACKAGE_VALID`, continue at **Save the Custom
Template** in [SKILL.md](../../SKILL.md), using the original PDF. A separate install,
second package check, reconstructed PDF or generated-deck QA pass is not needed.
