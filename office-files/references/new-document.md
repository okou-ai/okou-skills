# New Word/PDF report

Use this starter for new prose without a supplied template. For native Word
features or existing files, use [Word](word-authoring.md) or [PDF](pdf-authoring.md).

## Prepare and write

Set the skill path once per shell, with assignment on its own line. Run setup
once; it checks pinned Python dependencies and the actual Writer module,
installs only missing/mismatched requirements, and records setup time:

```bash
export OFFICE_FILES_DIR=/absolute/path/to/office-files
python3 "$OFFICE_FILES_DIR/scripts/setup_office.py" document \
  --out generated/setup-document.json
```

Add `--charts` to this setup command when chart images are needed. Installation
supports Debian/Ubuntu; other platforms receive concrete missing requirements.

Copy the runnable source and optional style settings:

```bash
mkdir -p generated/report
cp "$OFFICE_FILES_DIR/assets/document.md" generated/report/report.md
cp "$OFFICE_FILES_DIR/assets/document-style.json" generated/report/style.json
```

Replace the sample with the requested content. Set the actual language in YAML,
for example `lang: zh-CN`. Use ordinary Markdown headings, lists and tables.
Keep calculations in a data/model file; label assumptions and fictional inputs.
Use the requested sections and only the supporting analysis needed for their
decisions. Do not add manual chapter breaks or a page cap to shorten execution.
Compute the metrics needed to explain the supplied data. Forecasts, counterfactual
scenarios, payback models and numeric operating thresholds belong only in tasks
that request them; missing causal evidence calls for a stated uncertainty and a
validation action. Keep toolchain names and local file paths in QA/chat, not in
the business report, unless the user asks for implementation details.

State a finding once where it supports a requested decision; do not repeatedly
narrate the same table. Keep metric names and meanings identical to the model.
An average is not a marginal contribution, an observed change is not its cause,
and a required volume is not proof of achievable capacity. When the requested
problem analysis cannot establish a cause from the supplied data, identify what
to check next instead of inventing a diagnosis. Use assumptions only to complete
an explicitly needed calculation; label both the assumption and its consequence.

Use installed fonts covering the content. Optional style keys are `body_font`,
`heading_font`, `east_asia_font`, `body_size_pt`, `accent` (six hex digits),
`page_size` (`A4` or `Letter`), and `margins_mm` with `top`, `right`, `bottom`,
`left`. The defaults include table sizing and page numbers. Read
[editorial components](pandoc-authoring.md#optional-editorial-components) only
when needed; ordinary prose does not require custom CSS or layout experiments.

### When a chart is needed

Copy [the chart spec](../assets/chart.json) to `generated/report/chart.json` and
fill its data. Use `type: "bar"` or `"line"`, `categories` or numeric `x`, and
`series` entries with `name` and `values`. Set meaningful `x_label` and `y_label`;
optional keys are `font` (installed family/path), `accent` or `palette`.
The default image is 6 × 3.6 inches to fit the document. Override with
`width_inches` and `height_inches` only when needed. Put the figure caption in
Markdown; add an internal `title` only if it contributes distinct information.

```bash
python3 "$OFFICE_FILES_DIR/scripts/render_chart.py" \
  --spec generated/report/chart.json --output generated/report/chart.png
```

Insert `![Caption](chart.png)` into Markdown and bind the chart spec with
`--resource` below. Reuse this renderer before writing custom drawing code.

## Prepare the candidate and review

Before rendering, write `generated/report/expectations.json` from the request
and raw data. Include the key wording and independently calculated results;
text presence alone does not establish correct reasoning. For example:

```json
{
  "required_text": ["Decision summary", "40 completed tasks"],
  "same_page": [],
  "not_applicable": {}
}
```

Replace these example checks with actual requirements. Use `same_page` only
for a necessary grouping, with distinctive body text rather than repeated table
headers. Each item is an object, for example
`{"first": "Required group heading", "second": "Unique opening body text", "reason": "Heading must remain with its introduction"}`;
replace these strings with actual source text, or leave the array empty.
Do not invent a requirement that an entire table and chart share a page
when each is readable on adjacent pages. Headings and their opening prose are
added automatically from the Markdown source. Captions and tables use the
renderer’s grouping defaults and still need page review.

### Check content in parallel

Before the first preparation command, start a content check once the complete
draft and calculation model are ready. If agent tools are available, delegate
one bounded review to an independent reviewer using the same default model,
without a model override. Give it fresh context containing the original user
request, raw data, complete final draft and calculation model; exclude the
author's own passing QA conclusions. Use a background/asynchronous task when
supported so preparation and the overview inspection can continue. Collect
content and visible layout fixes together before the full-page review of the
final candidate; do not write a full acceptance record for a draft still under
content review. Without agent tools, perform the same content check yourself
and state that it was not independent.

Check requirement coverage; recompute all key calculations and reconcile
repeated targets and assumptions throughout the draft. Distinguish evidence
from causal, efficiency or feasibility claims: a change in cost or effort alone
does not establish its cause. Verify that each recommended action is sufficient
to resolve the problem it claims to address, including any numerical shortfall.
Check every quantitative explanation against the model's dependency structure:
which inputs actually change the named result, and which do not? Do not let a
correct number conceal a wrong explanation. Distinguish totals from averages,
observed differences from marginal effects, and cash results from accounting
results. For each asserted inability, sufficiency or capacity constraint, require
the missing size, duration or operating evidence; try a simple counterexample
under the stated assumptions. If the assertion does not follow, report it as an
error rather than a stylistic preference. Remove unsupported certainty or narrow
the conclusion to what the data establishes; adding "probably" is not evidence.
Return only specific errors with their locations and evidence, or `pass`;
do not add analysis, sections or cosmetic changes to the report.

Resolve actual errors before acceptance. Recheck changed conclusions and their
dependent calculations when needed; do not repeat an unchanged passing content
review. No additional schema or lengthy review record is needed. A time target
never permits skipping this check or the five visual criteria below, or imposing
a word or page limit.

### Prepare and inspect pages

Run generation, quick checks and page-preview preparation in one command:

```bash
python3 "$OFFICE_FILES_DIR/scripts/prepare_document.py" generated/report/report.md \
  --out generated/report/output --expectations generated/report/expectations.json \
  --style generated/report/style.json
```

Bind calculation scripts, input data and chart specs with repeated `--resource`
arguments. Keep all authored inputs outside `--out`. Use `--reference template.docx`
instead of `--style` when a supplied style reference governs the new document.
For deliberate Pandoc column proportions, add `--table-widths source`; otherwise
retain automatic widths, which reserve space for short labels and numbers.

The output contains editable `report.docx`, its exported `report.pdf`, timing in
`prepare.json`, and `qa/`. Original expectations are preserved; the current
Markdown checks are merged into `expectations.prepared.json`. Quick blockers
stop page-preview preparation. Fix missing text or split required groups in the
source and rerun. Repeated text is an ambiguity warning: verify the intended
occurrences visually or use a distinctive check, without rewriting sound prose.

Open `qa/gallery/overview-*.png`, then **every full page** at readable size in
small batches. In `qa/review.json`, check all five criteria on each page and set
each status explicitly to `pass` or `fail`. Write one concise page-specific
observation covering the checks, including absent tables/figures when relevant.
Explain every warning from the rendered pages. The compact record reduces
duplicate prose; it does not skip criteria or approve pages automatically.
Repair actual defects together where possible, then prepare and review the
changed candidate. Finish the content check above before `accept`. A passing
candidate needs no additional layout experiments.

```bash
python3 "$OFFICE_FILES_DIR/scripts/check_document.py" accept generated/report/output/qa
okou web upload-file -f generated/report/output/report.docx
```

Upload only after `READY_TO_DELIVER`. For a final PDF, upload `report.pdf` and
its editable DOCX source. Immediately send a short assistant message containing
the returned download URL(s), before any retrospective. Keep source and QA files.

For custom pipelines, the separate `render_document.py`, `quick`, `inspect` and
`accept` interfaces remain available in [document layout](document-layout.md).
