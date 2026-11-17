#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Unpack XLSX/XLSM without rewriting XML. Pretty-print only with --pretty.

Usage: xlsx_unpack.py INPUT.xlsx NEW_OUTPUT_DIR [--pretty]
Use xlsx_pack.py --base/--part for small edits without unpacking every member.
"""

import argparse
import os
from pathlib import Path
import shutil
import sys
import tempfile
import xml.dom.minidom
import zipfile
from xlsx_package import checked_members


def pretty_print_xml(content: bytes) -> bytes:
    """Explicit readability transform; malformed XML is never silently repaired."""
    dom = xml.dom.minidom.parseString(content)
    return dom.toprettyxml(indent="  ", encoding="utf-8")


def unpack(xlsx_path: str, output_dir: str, pretty: bool = False) -> None:
    source, target = Path(xlsx_path).resolve(), Path(output_dir).absolute()
    if not source.is_file():
        raise FileNotFoundError(f"File not found: {xlsx_path}")
    if os.path.lexists(target) or source.is_relative_to(target.resolve()):
        raise ValueError("Output must be a new directory, not the source or its ancestor")
    with zipfile.ZipFile(source) as package:
        infos = checked_members(package)
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = Path(tempfile.mkdtemp(prefix=".xlsx-unpack-", dir=target.parent))
        try:
            for info in infos:
                path = temporary / info.filename
                if info.is_dir():
                    path.mkdir(parents=True, exist_ok=True)
                else:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    with package.open(info) as incoming, path.open("xb") as outgoing:
                        shutil.copyfileobj(incoming, outgoing)
                    if pretty and info.filename.endswith((".xml", ".rels")):
                        path.write_bytes(pretty_print_xml(path.read_bytes()))
            if os.path.lexists(target):
                raise ValueError("Output directory appeared during extraction; refusing overwrite")
            temporary.rename(target)
        finally:
            if temporary.exists():
                shutil.rmtree(temporary)
    print(f"Unpacked '{xlsx_path}' → '{output_dir}' ({len(infos)} members)")
    print("XML pretty-print enabled: all XML may change." if pretty else "Original part bytes retained (no XML reserialization).")
    print("Resolve tab names through workbook relationships; review high-risk parts and structural dependencies.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input")
    parser.add_argument("output_dir")
    parser.add_argument("--pretty", action="store_true", help="Opt-in XML readability transform (not preservation mode)")
    args = parser.parse_args()
    try:
        unpack(args.input, args.output_dir, pretty=args.pretty)
    except (OSError, ValueError, zipfile.BadZipFile, xml.parsers.expat.ExpatError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
