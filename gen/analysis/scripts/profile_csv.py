"""Profile explicitly selected CSV columns without silently coercing missing data."""

import argparse
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import re
import statistics
import sys


NUMBER = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")
MAX_BYTES = 32 * 1024 * 1024


def profile_csv(path, numeric=(), key=(), missing=(), delimiter=",", max_rows=100_000):
    if max_rows < 1:
        raise ValueError("max_rows must be positive")
    if len(delimiter) != 1:
        raise ValueError("delimiter must be one character")
    with Path(path).open("rb") as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError("CSV exceeds 32 MiB; use a streaming dataframe or database")
    reader = csv.reader(
        io.StringIO(raw.decode("utf-8-sig"), newline=""),
        delimiter=delimiter,
        strict=True,
    )
    columns = next(reader, None)
    if not columns or any(not name.strip() or name != name.strip() for name in columns):
        raise ValueError("CSV requires nonblank headers without surrounding whitespace")
    if len(set(columns)) != len(columns):
        raise ValueError("CSV has duplicate headers")
    for group in (numeric, key):
        if len(set(group)) != len(group):
            raise ValueError("Selected columns must not repeat")
        unknown = set(group) - set(columns)
        if unknown:
            raise ValueError(f"Unknown columns: {', '.join(sorted(unknown))}")

    missing_tokens = {"", *missing}
    missing_counts = dict.fromkeys(columns, 0)
    invalid_counts = dict.fromkeys(numeric, 0)
    numbers = {name: [] for name in numeric}
    seen_keys = set()
    row_count = duplicate_keys = missing_keys = 0
    for row in reader:
        if len(row) != len(columns):
            raise ValueError(f"Malformed CSV record ending on line {reader.line_num}")
        row_count += 1
        if row_count > max_rows:
            raise ValueError(
                f"CSV exceeds {max_rows} rows; raise --max-rows or use a database"
            )
        record = dict(zip(columns, row))
        absent = {
            name for name, value in record.items() if value.strip() in missing_tokens
        }
        for name in absent:
            missing_counts[name] += 1
        for name in numeric:
            if name in absent:
                continue
            value = record[name].strip()
            parsed = float(value) if NUMBER.fullmatch(value) else math.nan
            if not math.isfinite(parsed):
                invalid_counts[name] += 1
            else:
                numbers[name].append(parsed)
        if key:
            if absent.intersection(key):
                missing_keys += 1
            else:
                identity = tuple(record[name] for name in key)
                if identity in seen_keys:
                    duplicate_keys += 1
                seen_keys.add(identity)

    summaries = {}
    for name, values in numbers.items():
        stats = {
            "valid_numeric_count": len(values),
            "missing_count": missing_counts[name],
            "invalid_numeric_count": invalid_counts[name],
            "sum": math.fsum(values) if values else None,
            "mean": statistics.mean(values) if values else None,
            "median": statistics.median(values) if values else None,
            "minimum": min(values) if values else None,
            "maximum": max(values) if values else None,
            "sample_stddev": statistics.stdev(values) if len(values) > 1 else None,
        }
        if any(isinstance(v, float) and not math.isfinite(v) for v in stats.values()):
            raise ValueError(
                f"Numeric summary overflow in {name}; use decimal arithmetic"
            )
        summaries[name] = stats
    return {
        "source": str(path),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "row_count": row_count,
        "columns": columns,
        "missing_counts": missing_counts,
        "numeric": summaries,
        "key": {
            "columns": list(key),
            "duplicate_rows_after_first": duplicate_keys,
            "rows_with_missing_key": missing_keys,
        }
        if key
        else None,
        "limitations": "Numeric summaries use finite, valid cells only and binary floating-point. "
        "Check missing/invalid counts; this profile does not establish data validity.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--numeric", nargs="+", default=[])
    parser.add_argument("--key", nargs="+", default=[])
    parser.add_argument("--missing", nargs="+", default=[])
    parser.add_argument("--delimiter", default=",")
    parser.add_argument("--max-rows", type=int, default=100_000)
    args = parser.parse_args()
    try:
        result = profile_csv(
            args.input,
            args.numeric,
            args.key,
            args.missing,
            args.delimiter,
            args.max_rows,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))
    except (OSError, UnicodeError, csv.Error, ValueError, OverflowError) as error:
        print(f"CSV profile failed: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
