# Tabular summaries from supplied data

Use this route for a **new** workbook with category or calendar-month summaries
of supplied CSV/JSON records. It replaces per-report data mapping, formula-range
code, derived calculations, chart coordinates and expectation scripts with one
small configuration. For editing an existing file, arbitrary formulas, pivots
or a custom layout, use [the Excel workflow](excel-authoring.md) instead.

Install the dependencies from that workflow once. Set `OFFICE_FILES_DIR` to this
package. Copy [summary-spec.json](../assets/summary-spec.json), replace its
columns, sheet names and requested summaries, and point it at actual source
data. The accompanying [summary-data.csv](../assets/summary-data.csv) is a
deterministic **simulated** service-booking example, not factual business data.
Do not add sections, KPIs or charts the request does not need.
Localize every visible label, including each summary's `total_label` (the
default is English `Total`), notes headers and chart titles. For a currency,
set e.g. `"theme": {"currency": "¥"}` and reuse `"format": "money"` /
`"number_format": "money"`; ordinary currency formatting needs no manually
escaped Excel format string.

```bash
python3 "$OFFICE_FILES_DIR/scripts/summarize_workbook.py" \
  --data generated/source.csv --spec generated/summary-spec.json \
  --out generated/summary --prepare-review
```

This single command writes an editable XLSX, `workbook-spec.json`,
`expectations.json`, and a provenance/timing `manifest.json`; then runs the
fixed quick check, fresh Calc verification and preview. It stops on a failed
stage and records the failure. Omit `--prepare-review` while drafting if only
the workbook and expectations are needed. Output directories must be new so
earlier inputs and QA are retained.

It does **not** approve the pages or permit delivery. Inspect every page in the
returned gallery, record observations in the returned `review.json`, then run:

```bash
python3 "$OFFICE_FILES_DIR/scripts/check_workbook.py" accept \
  --qa generated/summary/qa
```

Deliver only the exact `candidate.path` from a successful acceptance, which is
the recalculated XLSX. Calc preview does not establish native Excel rendering.
The script binds the raw data, high-level spec, builder, lower-level author and
generated workbook spec; changing any bound file requires fresh QA.

## Supported configuration

`version` is `1`. `filename` is an optional `.xlsx` basename (default
`summary.xlsx`). Optional `theme` uses the lower-level author's theme fields.
Only these fields and the objects below are supported; unknown fields and
arbitrary expressions fail rather than being silently ignored.

| Object | Fields |
| --- | --- |
| `source` | `columns` plus optional `sheet` (default `Data`) and `title` (default `Source data`) |
| Source column | `key`, `header`, `type`: `date`, `text` or `number`; optional `format` and `width` |
| `summaries[]` | Unique `id`, `sheet`, `title`, `group_by`, `metrics`; optional `totals` (default true) and `total_label` (default `Total`) |
| `group_by` | `column` and `kind`: `category` for a text column, or `month` for a date column; optional `header` |
| Metric | Unique `id`, `label`, `op` and operands below; optional `format` and `width` |
| Optional `dashboard` | `sheet`, `title`, and explicitly configured `kpis` and/or `charts` |
| Optional `notes` | `sheet`, `title`, `rows`: pairs of literal strings, with the first row used as column headers; optional `column_widths` for `A` and/or `B` |
| KPI | `summary`, `metric`, `label`; refers to that summary's total; `change` is not a total KPI |
| Chart | `summary`, `metrics` (array of ids), `title`; optional `type`: `column`, `bar`, `line`; `labels` boolean; `number_format` |

Summary ids and metric ids are simple ASCII identifiers; source keys can be
the actual CSV/JSON field names. Sheet names and labels can use other languages,
spaces and internal apostrophes. Reusing the exact same summary `sheet` name
stacks sections on that sheet. Source, dashboard and notes sheets must be distinct.
There is no fixed number of summaries, sheets or printed pages.

The builder freezes raw data at `A4` (title/header rows stay visible) and
summaries at `B4` (also retaining the group-label column). Raw data uses a
structured table with filter controls. Number formats come from the source
columns and metrics; wrapped text, header styling, column widths and chart
slots have working defaults. These defaults require no lower-level spec or
script-source inspection. Use the custom route only for a requested feature
outside this interface.

Notes are supplied text only: the builder adds no definitions, conclusions or
source claims on its own. Formula-like note text stays literal.

Column widths are finite numbers greater than 0 and at most 255. Metrics
default to 20; notes default to `{"A": 26, "B": 80}`. Stacked summaries share
physical sheet columns: an explicit metric width applies to every section in
that column, and conflicting explicit widths are rejected. Notes already wrap
and get estimated row heights; adjust widths for actual readability problems
and check the preview rather than requiring every note to fit on one line.

| `op` | Operands | Calculation |
| --- | --- | --- |
| `count` | None | Number of source records in the group |
| `sum` | `column` | Sum of a declared numeric source column |
| `difference` | `left`, `right` | Earlier metric ids: left minus right |
| `ratio` | `numerator`, `denominator` | Earlier metric ids: numerator divided by denominator |
| `change` | `metric` | Earlier metric id: `(current − previous) / previous`, month grouping only |

Derived metrics refer to **earlier** metrics, never source-column expressions.
There is no expression parser. Count defaults to integer format; sums and
differences to decimal; ratios and changes to percent. Use `money`, `integer`,
`decimal`, `percent`, `date`, `text` or an Excel number-format string to override.
Plan metric order with the desired chart series in mind: a chart's selected
metrics must be adjacent and in that same order.

Month summaries include every calendar month from the earliest to latest input
date, including missing months with zero counts/sums. The first month's change,
any ratio/change with a zero or undefined denominator, and the change total are
blank. Derived calculations propagate a blank operand. Total counts and sums
cover all input rows; total ratios divide the total operands, so they are
weighted correctly rather than averaging group percentages. A change uses the
signed prior value as denominator, including when it is negative.

Charts get stable two-column grid slots on the optional dashboard. Metric ids
must be adjacent **and in summary-column order**; reorder metrics or use the
lower-level author for noncontiguous series/custom geometry. Categories and
data ranges are computed from the selected summary, excluding its total.
The dashboard title repeats on printed continuation pages. Charts do not
create additional analysis or inferred narrative.
Data labels default to false. Keep that default for line charts unless labels
add necessary information; labels can collide with the lines in Calc previews.

## Source and verification contract

CSV must be UTF-8 (BOM accepted) with one header row; JSON must be an array of
objects. Field names must match the declared source keys exactly. Dates must be
valid `YYYY-MM-DD` strings from 1900-01-01 through 9999-11-30. Numeric values
must be finite, without currency symbols, thousands separators, blanks or
surrounding whitespace. Missing values and invalid types fail with the record
and field name. Zero and negative numbers are valid. Text is written literally,
including a leading `=`; it is never interpreted as a formula.

Category labels must be nonempty without surrounding whitespace. Labels that
differ only by case are rejected because Excel's `SUMIFS` is case-insensitive.
Literal `*`, `?` and `~` characters are escaped in criteria. Empty input and
undefined/duplicate names, unsupported expressions and ambiguous groupings
are rejected.

Expectations come from a separate Python `Decimal` aggregation path over raw
records, never from workbook caches or evaluation of the emitted Excel
formulas. They cover every summary metric, derived value, total and KPI, plus
raw numeric/text cells. Raw date literals are strictly parsed and typed; the
numeric checker does not compare date literals individually. The manifest
records expected/formula/date-literal counts for each sheet and SHA-256 input
and output fingerprints; verified formula counts appear only after successful
fresh verification. Inspect key results against domain knowledge as part
of review; generated expectations do not establish business assumptions.

The workbook is a snapshot: formulas remain editable, but adding new raw rows
or categories does not automatically rebuild grouping lists or ranges. Re-run
the builder and QA for changed inputs. The emitted lower-level spec is a
readable escape point for features outside this schema; once edited, regenerate
independent expectations for affected results and follow the lower-level QA.

The manifest's stage durations measure local code and QA execution only. They
exclude model composition, tool-dispatch time, review and upload; use observed
end-to-end run timings to evaluate overall speed, not these script durations.
