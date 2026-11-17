# PDF environment by operation and features

Set `SKILL_DIR` to the directory containing PDF `SKILL.md`. Use Python 3.10+
and reuse a working environment. Importing helpers, `--help`, argument validation and non-PDF parsing
never install packages. Runtime dependency errors are nonzero and include an
explicit setup hint; they must not trigger silent network access or pip.

Check input existence/type and content shape before expensive environment checks
where practical. Select only the required path:

| Operation/feature | Dependencies | Explicit check/setup when needed and authorized |
|---|---|---|
| Parse `.md` / `.markdown` / `.txt` / `.json` | Python standard library | No dependency setup |
| Inspect/fill forms, parse PDF text, merge PDFs | Python + `pypdf` | `make.sh check --only fill`; `make.sh fix --only fill` |
| Render body without math/chart/flowchart | Python + ReportLab | `make.sh check --only body --minimal`; `make.sh fix --only body --minimal` |
| Render body with math/chart/flowchart | Above + matplotlib | `make.sh check --only body`; `make.sh fix --only body` |
| Full cover/body, no plot features | Above core packages + Node/Playwright/Chromium | `make.sh check --minimal`; `make.sh fix --minimal` |
| Full cover/body with plot features | All of the above | `make.sh check`; `make.sh fix` |

Invoke the table's commands through the absolute script path, for example:

```bash
bash "$SKILL_DIR/scripts/make.sh" check --minimal
```

`fix` is the explicit installation route, only with authorization and preferably
an activated Python virtual environment. No-option `fix` retains full setup
including matplotlib; `--minimal` omits it. `--only fill` does not check or install
ReportLab, matplotlib, Node or Chromium. Body rendering no longer needs `pypdf`;
the final pipeline still needs it for merging. Plot imports are lazy per block.
No-option `check` now requires the full selected set, including matplotlib; use
`--minimal` when no math/chart/flowchart is used.

For this cover/body route, run the selected `check` once per unchanged session;
it includes an actual Chromium launch only for the pipeline scope. Recheck if
the environment/features change or a failure invalidates prior evidence. A named
manuscript or DOCX-to-PDF route uses its own setup/validation, not Chromium here.
On Linux, Chromium may additionally need authorized OS libraries (for example,
`npx playwright install-deps chromium`). Never send FILL through this setup.

CJK/mixed-script body text needs an embeddable TrueType font covering the actual
text. The renderer checks known Linux/macOS candidates and fails when glyphs
cannot be covered. When authorized, Debian/Ubuntu can install `fonts-wqy-zenhei`;
or set `PDF_CJK_FONT` to an absolute compatible TrueType path. Requested fonts and
Google cover fonts still need actual-output verification; do not hide fallbacks.

`demo` is sample material, not a finished deliverable. No new manuscript, APA/IEEE,
OCR, lossless-layout or font-selection CLI modes are introduced.
