# New Word/PDF report

Use this starter for new prose without a supplied template. For native Word
features or existing files, use [Word](word-authoring.md) or [PDF](pdf-authoring.md).

## Prepare and write

Set the skill path once per shell, with assignment on its own line:

```bash
export OFFICE_FILES_DIR=/absolute/path/to/office-files
python3 -m pip install --break-system-packages --quiet pypandoc_binary==1.17 python-docx==1.2.0 PyMuPDF==1.28.2
```

If LibreOffice Writer is absent, install it before writing:

```bash
sudo apt-get update -qq
sudo apt-get install -y -qq libreoffice-writer
```

Copy the runnable source and optional style settings:

```bash
mkdir -p generated/report
cp "$OFFICE_FILES_DIR/assets/document.md" generated/report/report.md
cp "$OFFICE_FILES_DIR/assets/document-style.json" generated/report/style.json
```

Replace the sample with the requested content. Set the actual language in YAML,
for example `lang: zh-CN`. Use ordinary Markdown headings, lists and tables;
insert existing chart images with `![Caption](chart.png)`. Keep calculations in
a data/model file and derive the key expected results independently of the
rendered candidate.

Use installed fonts covering the content. Optional style keys are `body_font`,
`heading_font`, `east_asia_font`, `body_size_pt`, `accent` (six hex digits), `page_size` (`A4` or
`Letter`), and `margins_mm` with `top`, `right`, `bottom`, `left`.
Do not add manual chapter breaks just to give each section its own page.
Read [editorial components](pandoc-authoring.md#optional-editorial-components)
only when the document needs them.

### When a chart is needed

Copy [the chart spec](../assets/chart.json) to `generated/report/chart.json` and
fill its data. Use `type: "bar"` or `"line"`, `categories` or numeric `x`, and
`series` entries with `name` and `values`. Set `title`, `x_label`, `y_label` and
optionally `font` (installed family or path), `accent` or `palette`.

```bash
python3 -m pip install --break-system-packages --quiet matplotlib==3.10.8
python3 "$OFFICE_FILES_DIR/scripts/render_chart.py" \
  --spec generated/report/chart.json --output generated/report/chart.png
```

Insert the image in the Markdown and bind its spec with `--resource` below.
Use the existing chart defaults before implementing custom drawing code.

## Render and check

```bash
python3 "$OFFICE_FILES_DIR/scripts/render_document.py" generated/report/report.md \
  --out generated/report/output --style generated/report/style.json
```

The output contains editable `report.docx` and its `report.pdf`. For deliberately
chosen Pandoc column proportions, add `--table-widths source`; otherwise retain
automatic content-based widths. Use `--reference template.docx` instead of
`--style` when a supplied style reference governs a new document.
Bind calculation scripts, data and other dependencies with repeated `--resource`.

Add key wording/numbers and required grouping to
`generated/report/output/expectations.json` using the request and source data.
Use unique text from the first body row for a table grouping check, not a repeated
table header. A rerender preserves this file; reconcile changed headings with
the refreshed `expectations.seed.json`.

```bash
python3 "$OFFICE_FILES_DIR/scripts/check_document.py" quick \
  generated/report/output/report.pdf --docx generated/report/output/report.docx \
  --render generated/report/output/render.json \
  --expectations generated/report/output/expectations.json
```

Fix missing text or split required groups before producing page images. Repeated
text is an ambiguity warning: choose a distinctive snippet or verify the intended
occurrences during page review; do not rewrite sound prose merely to remove it.
A quick check does not validate numbers semantically or approve delivery.

Once the content is stable:

```bash
python3 "$OFFICE_FILES_DIR/scripts/check_document.py" inspect \
  generated/report/output/report.pdf --docx generated/report/output/report.docx \
  --render generated/report/output/render.json \
  --expectations generated/report/output/expectations.json --out generated/report/qa
```

Open `qa/gallery/overview-*.png`, then every full page in small batches. Check
readability, hierarchy, spacing, grouping, tables/figures and visible glyphs.
Complete the existing five fields for each page in `qa/review.json`; explain
warnings based on the pages. Repair actual defects, then render and inspect the
changed candidate again. Do not rerender solely to collect another copy of a
passing check.

```bash
python3 "$OFFICE_FILES_DIR/scripts/check_document.py" accept generated/report/qa
okou web upload-file -f generated/report/output/report.docx
```

Upload the requested file after `READY_TO_DELIVER`. For a final PDF, upload
`report.pdf` and include its editable DOCX source. Keep source and QA files.
