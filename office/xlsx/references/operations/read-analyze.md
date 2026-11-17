# Read and analyze spreadsheet data

Extract requested records/results directly; expand analysis only when needed.
Do not save, restyle, execute macros or recalculate the original. An output file
is a separate CREATE/EDIT operation, not a mandatory extra report.

## Choose the smallest read

```bash
# Standard library only; no pandas/openpyxl/Calc needed:
python3 "$SKILL_DIR/scripts/xlsx_reader.py" input.xlsx --inventory --json
python3 "$SKILL_DIR/scripts/xlsx_reader.py" input.xlsx
python3 "$SKILL_DIR/scripts/xlsx_reader.py" input.xlsm --sheet Sales --range B3:D8 --json
python3 "$SKILL_DIR/scripts/xlsx_reader.py" input.csv --preview 8 --columns 4 --encoding utf-8-sig
# Explicit full DataFrame work (optional pandas + appropriate Excel engine):
python3 "$SKILL_DIR/scripts/xlsx_reader.py" input.xlsx --analyze --sheet Sales --json
python3 "$SKILL_DIR/scripts/xlsx_reader.py" input.xlsx --quality --sheet Sales --json
```

- Default: inventory plus **A1:L5 of the first XML worksheet only**. `--sheet`
  selects a name, not an assumed part number. `--inventory` opens no worksheets,
  styles or shared strings and makes no claim about used dimensions/row counts.
- `--range A1:C8` (or one cell) uses actual Excel row/column addresses. Otherwise
  `--preview N --columns M` reads addresses A1 through column M/row N. Slices are
  capped at 10,000 cells. Sparse/absent cells are omitted, not fabricated zeros.
- Worksheet XML streams only through the requested final row; reaching a late
  range still scans preceding XML. Referenced shared strings stream until found;
  styles are read for number-format metadata. These reads do not render Excel,
  expand shared formulas, evaluate functions or access external links.
- Numeric values remain exact XML lexical strings with style/number-format IDs;
  date serials retain the workbook's 1900/1904 basis rather than guessed dates.
  Unknown formats/types remain explicitly undecoded. Cell-format metadata does
  not resolve inherited row/column styles, conditional formatting or locale display.
  Explicit text, long IDs,
  leading zeros and CJK strings are retained. A numeric `123` formatted `000000`
  is not silently turned into an identifier; confirm field meaning and locale.
- Formula text/attributes and cache status are separate: absent/blank caches are
  unknown, never zero. A stored cache can still be stale. Inline/shared rich-text
  content excludes phonetic annotations; unsupported annotations/features are not
  a promise of lossless rendered text extraction.
- CSV/TSV previews keep all fields as text. Encoding retries occur only on actual
  decode failures; parser/I/O errors are reported without changing encodings.
  Automatic UTF-8 BOM/GBK/Latin-1 fallback is ambiguous: confirm delimiter/encoding
  and text, or specify `--encoding`. Inventory does not count delimited records.
- `--analyze` restores the old full pandas structure + quality + statistics path;
  omitted `--sheet` loads all sheets. `--quality` retains full audit/skip-statistics
  meaning, and `--json` still selects machine-readable output. Lightweight JSON
  instead reports `sheets`/`previews`; do not treat its sample as an audit result.
  Full pandas inference is not an identifier/date preservation guarantee: provide
  an explicit source schema for substantive custom analysis when needed.

## Interpret and answer

Confirm relevant sheets, real headers/offsets, grain, units, periods and types.
Read only needed sheets/fields; do not run all-column profiling or extra financial
metrics for a simple extraction. Aggregate source columns, not rounded summaries.
For financial READ apply only the [finance semantics](../domains/finance.md#financial-semantics-read-and-authoring).

Preserve missing, invalid, unavailable and zero states; identify rejected
conversions. Values-only reads do not calculate formulas and must never overwrite
the formula source. Fresh results require an authorized disposable copy and the
[impact-driven validation plan](validate.md), not a save/recalc of the original.

Return requested findings/records with actual Excel cell/row locations and enough
calculation detail for material results. Account for real header/skip offsets,
not pandas indices or a universal index-to-row formula. Use requested display
precision/currency/locale without rounding intermediate arithmetic; disclose
relevant sampling, cache and quality limits. Do not invent causes or add
unrequested metrics, sections or files.
