#!/usr/bin/env python3
"""Read only the relevant slice of the maintained layout vocabulary."""

import argparse
import json
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"


def lookup(*, query=None, group=None, ids=None):
    catalog = json.loads((ASSETS / "catalog.json").read_text(encoding="utf-8"))
    entries = catalog["entries"]
    if ids is not None:
        selected = set(ids)
        known = {entry["id"] for entry in entries}
        if selected - known:
            raise ValueError(
                "Unknown vocabulary IDs: " + ", ".join(sorted(selected - known))
            )
        entries = [entry for entry in entries if entry["id"] in selected]
    if group:
        if group not in {item["id"] for item in catalog["groups"]}:
            raise ValueError(f"Unknown vocabulary group: {group}")
        entries = [entry for entry in entries if entry["group"] == group]
    if query:
        needle = query.casefold()
        entries = [
            entry
            for entry in entries
            if needle in json.dumps(entry, ensure_ascii=False).casefold()
        ]
    source_ids = {source for entry in entries for source in entry["sources"]}
    return {
        "entries": entries,
        "sources": [
            source for source in catalog["sources"] if source["id"] in source_ids
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--query")
    selection.add_argument("--group")
    selection.add_argument("--ids", nargs="+")
    args = parser.parse_args()
    try:
        result = lookup(query=args.query, group=args.group, ids=args.ids)
    except ValueError as error:
        parser.error(str(error))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
