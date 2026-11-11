#!/usr/bin/env python3
"""Exact ordered revenue and weighted-rate bridges using only the standard library.

Input: {"baseline": [...], "actual": [...]} with matching unique segment IDs.
Revenue rows: segment, quantity (common units), price. Weighted-rate rows:
segment, weight (denominator amount), rate (fractional units).
Numbers may be integers or decimal strings. CLI JSON decimals are parsed exactly.
Output amounts are rational strings (e.g. "320" or "20/3"), never rounded.
"""

import argparse
from decimal import Decimal
from fractions import Fraction
import json
from pathlib import Path


def _unique_keys(pairs):
    """Reject ambiguous JSON objects before any source value can be overwritten."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _records(rows, fields):
    if not isinstance(rows, list) or not rows:
        raise ValueError("Each period must be a nonempty array")
    records = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Each row must be an object")
        segment = row.get("segment")
        if not isinstance(segment, str) or not segment.strip() or segment in records:
            raise ValueError("Segment IDs must be nonempty, unique strings")
        values = {}
        for field in fields:
            value = row.get(field)
            if value is None or isinstance(value, (bool, float)):
                raise ValueError(f"{segment}: {field} needs an exact number or decimal string")
            try:
                values[field] = Fraction(value)
            except (TypeError, ValueError, ZeroDivisionError, OverflowError) as exc:
                raise ValueError(f"{segment}: invalid finite number for {field}") from exc
        records[segment] = values
    return records


def _periods(baseline, actual, fields, weight):
    base = _records(baseline, fields)
    end = _records(actual, fields)
    if base.keys() != end.keys():
        raise ValueError("Periods need matching segment IDs and explicit counterpart values")
    for period in (base, end):
        if any(row[weight] < 0 for row in period.values()):
            raise ValueError(f"{weight} must be nonnegative")
        if sum(row[weight] for row in period.values()) <= 0:
            raise ValueError(f"Total {weight} must be positive in both periods")
    return base, end


def revenue_bridge(baseline, actual):
    """Substitute total quantity, segment mix, then prices; return exact amounts."""
    base, end = _periods(baseline, actual, ("quantity", "price"), "quantity")
    q0 = sum(row["quantity"] for row in base.values())
    q1 = sum(row["quantity"] for row in end.values())
    r0 = sum(row["quantity"] * row["price"] for row in base.values())
    r1 = sum(row["quantity"] * row["price"] for row in end.values())
    quantity = (q1 - q0) * r0 / q0
    mix = sum((end[s]["quantity"] - q1 * base[s]["quantity"] / q0)
              * base[s]["price"] for s in base)
    price = sum(end[s]["quantity"] * (end[s]["price"] - base[s]["price"])
                for s in base)
    return {"baseline": r0, "actual": r1, "quantity": quantity, "mix": mix,
            "price": price, "change": r1 - r0}


def weighted_rate_bridge(baseline, actual):
    """Normalize denominator weights, substitute mix then rates; return rates."""
    base, end = _periods(baseline, actual, ("weight", "rate"), "weight")
    t0 = sum(row["weight"] for row in base.values())
    t1 = sum(row["weight"] for row in end.values())
    r0 = sum(row["weight"] * row["rate"] for row in base.values()) / t0
    r1 = sum(row["weight"] * row["rate"] for row in end.values()) / t1
    mix = sum((end[s]["weight"] / t1 - base[s]["weight"] / t0)
              * base[s]["rate"] for s in base)
    rate = sum(end[s]["weight"] / t1 * (end[s]["rate"] - base[s]["rate"])
               for s in base)
    return {"baseline": r0, "actual": r1, "mix": mix, "rate": rate,
            "change": r1 - r0}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("revenue", "weighted-rate"), required=True)
    parser.add_argument("--input", type=Path, required=True,
                        help="JSON file with baseline and actual arrays")
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"), parse_float=Decimal,
                          object_pairs_hook=_unique_keys)
        if not isinstance(data, dict) or "baseline" not in data or "actual" not in data:
            raise ValueError("Input needs baseline and actual arrays")
        bridge = revenue_bridge if args.mode == "revenue" else weighted_rate_bridge
        result = bridge(data["baseline"], data["actual"])
        parts = ("quantity", "mix", "price") if args.mode == "revenue" else ("mix", "rate")
        if sum(result[key] for key in parts) != result["change"]:
            raise ValueError("Bridge does not reconcile")
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps({key: str(value) for key, value in result.items()}, indent=2))


if __name__ == "__main__":
    main()
