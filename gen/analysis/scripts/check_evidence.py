"""Check evidence-record structure; do not certify factual or analytical validity."""

import argparse
from datetime import date
import json
from pathlib import Path
import sys


KINDS = {
    "fact",
    "calculation",
    "estimate",
    "forecast",
    "interpretation",
    "recommendation",
}
STATUSES = {"supported", "conditional", "unverified"}


def nonblank(value):
    return isinstance(value, str) and bool(value.strip())


def string_list(value):
    return isinstance(value, list) and all(nonblank(item) for item in value)


def check_evidence(document):
    errors = []
    review_required = []
    if not isinstance(document, dict):
        return {
            "structure_valid": False,
            "errors": ["Expected a JSON object"],
            "review_required": [],
        }
    sources, claims = document.get("sources"), document.get("claims")
    if not isinstance(sources, list):
        errors.append("sources must be a list")
        sources = []
    if not isinstance(claims, list) or not claims:
        errors.append("claims must be a nonempty list")
        claims = []

    source_ids = set()
    for index, source in enumerate(sources):
        where = f"sources[{index}]"
        if not isinstance(source, dict):
            errors.append(f"{where} must be an object")
            continue
        for field in ("id", "locator", "accessed_on"):
            if not nonblank(source.get(field)):
                errors.append(f"{where}.{field} must be a nonblank string")
        identifier = source.get("id")
        if nonblank(identifier):
            if identifier in source_ids:
                errors.append(f"Duplicate source id: {identifier}")
            source_ids.add(identifier)
        retrieved = source.get("accessed_on")
        if nonblank(retrieved):
            try:
                if date.fromisoformat(retrieved).isoformat() != retrieved:
                    raise ValueError("noncanonical date")
            except ValueError:
                errors.append(f"{where}.accessed_on must be YYYY-MM-DD")

    claim_ids = set()
    for index, claim in enumerate(claims):
        where = f"claims[{index}]"
        if not isinstance(claim, dict):
            errors.append(f"{where} must be an object")
            continue
        for field in ("id", "text"):
            if not nonblank(claim.get(field)):
                errors.append(f"{where}.{field} must be a nonblank string")
        identifier = claim.get("id")
        if nonblank(identifier):
            if identifier in claim_ids:
                errors.append(f"Duplicate claim id: {identifier}")
            claim_ids.add(identifier)
        kind, status = claim.get("kind"), claim.get("status")
        if not isinstance(kind, str) or kind not in KINDS:
            errors.append(f"{where}.kind is not a supported statement type")
        if not isinstance(status, str) or status not in STATUSES:
            errors.append(
                f"{where}.status must be supported, conditional, or unverified"
            )
        references = claim.get("source_ids")
        if not string_list(references):
            errors.append(f"{where}.source_ids must be a list of nonblank source IDs")
        else:
            if len(references) != len(set(references)):
                errors.append(f"{where}.source_ids contains duplicate references")
            for reference in references:
                if reference not in source_ids:
                    errors.append(f"{where} references unknown source: {reference}")
            if status in ("supported", "conditional") and not references:
                errors.append(f"{where} needs sources for its declared status")
        if kind != "fact" and not nonblank(claim.get("basis")):
            errors.append(f"{where}.basis must identify the calculation or inference")
        if kind in ("estimate", "forecast") and status == "supported":
            errors.append(
                f"{where}: estimates and forecasts must declare conditionality"
            )
        assumptions = claim.get("assumptions", [])
        if not string_list(assumptions):
            errors.append(f"{where}.assumptions must be a list of nonblank strings")
        elif (
            kind in ("estimate", "forecast") or status == "conditional"
        ) and not assumptions:
            errors.append(f"{where} needs explicit assumptions")
        if status in ("conditional", "unverified"):
            if not nonblank(claim.get("limitations")):
                errors.append(f"{where}.limitations must explain uncertainty")
            review_required.append(identifier if nonblank(identifier) else where)

    return {
        "structure_valid": not errors,
        "errors": errors,
        "review_required": review_required,
        "limitations": "Structural checks only. Verify source support, independence, "
        "calculations and method assumptions separately. Statuses are analyst declarations.",
    }


def unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"Non-finite JSON value: {value}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    args = parser.parse_args()
    try:
        document = json.loads(
            args.ledger.read_text(encoding="utf-8"),
            object_pairs_hook=unique_keys,
            parse_constant=reject_constant,
        )
        result = check_evidence(document)
    except (OSError, UnicodeError, ValueError) as error:
        print(
            json.dumps(
                {
                    "structure_valid": False,
                    "errors": [str(error)],
                    "review_required": [],
                },
                indent=2,
            )
        )
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["structure_valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
