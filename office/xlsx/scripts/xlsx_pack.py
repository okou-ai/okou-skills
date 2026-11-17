#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Pack a directory, or replace only named XML parts in a source-preserving copy.

Legacy: xlsx_pack.py SOURCE_DIR OUTPUT.xlsx
Scoped: xlsx_pack.py --base INPUT.xlsx --part xl/worksheets/sales.xml=edited.xml OUTPUT.xlsx
Outputs must be new paths. XML well-formedness is not full OOXML validation.
"""

import argparse
import sys
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
from xlsx_package import pack_directory, replace_parts, source_files


def validate_xml_files(source_dir: str) -> list[str]:
    """Legacy helper: return XML parse failures, without changing any source."""
    bad = []
    for path, name in source_files(Path(source_dir)):
        if name.endswith((".xml", ".rels")):
            try:
                ET.parse(path)
            except ET.ParseError as exc:
                bad.append(f"{name}: {exc}")
    return bad


def pack(source_dir: str, xlsx_path: str) -> None:
    count = pack_directory(source_dir, xlsx_path)
    print(f"Packed {count} files → '{xlsx_path}'")
    print("XML is well-formed. Continue with the impact-driven checks in VALIDATE.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="SOURCE_DIR OUTPUT, or OUTPUT with --base")
    parser.add_argument("--base", help="Existing XLSX/XLSM; never modified")
    parser.add_argument("--part", action="append", default=[], metavar="MEMBER=FILE",
                        help="Existing XML/rels part to replace (repeat for coupled changes)")
    args = parser.parse_args()
    try:
        if args.base:
            if len(args.paths) != 1:
                parser.error("--base expects exactly one output path")
            replacements = {}
            for value in args.part:
                name, separator, filename = value.partition("=")
                if not separator or not filename or name in replacements:
                    raise ValueError("Each --part must be a distinct MEMBER=FILE")
                replacements[name] = filename
            replace_parts(args.base, replacements, args.paths[0])
            print(f"Replaced {len(replacements)} part(s) → '{args.paths[0]}'")
            print("Unchanged ZIP member records preserved. Review dependencies and VALIDATE checks.")
        else:
            if len(args.paths) != 2 or args.part:
                parser.error("Directory mode expects SOURCE_DIR OUTPUT and no --part")
            pack(*args.paths)
    except (OSError, ValueError, ET.ParseError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
