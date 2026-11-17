# Read and analyze spreadsheet data

Use for extraction or analysis without changing the source. Do not save,
restyle or recalculate the original. A request for an output file is a separate
CREATE/EDIT operation; return the requested format, not a mandatory report.

## Discover the data

```bash
python3 "$SKILL_DIR/scripts/xlsx_reader.py" input.xlsx
python3 "$SKILL_DIR/scripts/xlsx_reader.py" input.xlsx --sheet Sales --json
```

The reader handles XLSX/XLSM/CSV/TSV through pandas and supports `--quality`.
Check actual sheet names, headers, extent, units, periods and data types before
analysis. CSV encoding detection can be ambiguous; confirm text and delimiters
rather than silently accepting garbled data. Read macros as data, never execute
them as part of inspection.

For custom analysis, use pandas or another appropriate deterministic tool.
Read only needed sheets/columns for large files. Account for header offsets,
merged or multi-row headers, and whether identifiers are text rather than
quantities. Aggregate actual source columns rather than inferring totals from
rounded summaries.

## Interpret values carefully

- Missing formula caches are uncalculated/unknown values, not zeros. Reading
  with `data_only=True` can inspect existing caches but does not calculate
  formulas; never save that values-only workbook over the formula source.
- When results require recalculation, use an authorized disposable copy and
  the VALIDATE workflow. Do not silently alter the original during analysis.
- Preserve missing, invalid and unavailable states. If coercing mixed types,
  identify rejected values rather than silently deleting them.
- Distinguish source records from calculated findings, estimates and proposals.
  Explain material limits instead of inventing causes or unsupported facts.
- Report Excel cell/row locations, not pandas indices. Account for the actual
  header/skip offset rather than assuming a universal index-to-row formula.
- Match requested decimal precision, currency, units and locale in displayed
  results. Numeric display is not permission to round intermediate arithmetic.

## Answer the actual request

Present the requested findings or extracted records with enough source
locations and calculation detail to make material results checkable. Include
relevant quality issues and missing-evidence caveats; do not impose unrelated
financial metrics, a fixed section template, or an extra file on every task.
