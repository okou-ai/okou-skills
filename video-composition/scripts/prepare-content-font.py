#!/usr/bin/env python3
"""Prepare one licensed local font for the browser; retain full coverage by default."""
import argparse
import json
import os
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--face-index", type=int, help="Required for TTC collections; use the selected locale's face")
    parser.add_argument("--text-file", type=Path, help="Optional complete final visible copy for subsetting")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error("The input font does not exist.")
    if args.input.resolve() == args.output.resolve():
        parser.error("Keep the source font intact; choose a different output path.")
    if args.output.suffix.lower() != ".woff2":
        parser.error("The output must be a .woff2 file.")
    if args.output.exists() and not args.overwrite:
        parser.error("Output exists; reuse it or use --overwrite for an intentional update.")
    if args.input.suffix.lower() == ".ttc" and args.face_index is None:
        parser.error("Select the collection's locale with --face-index.")
    if args.face_index is not None and args.face_index < 0:
        parser.error("--face-index must be non-negative.")
    try:
        from fontTools import subset
        from fontTools.ttLib import TTFont
        import brotli  # noqa: F401 - WOFF2 encoding dependency
    except ImportError:
        parser.error("Install fonttools and brotli once in an isolated Python environment, then rerun this helper there.")

    with TTFont(args.input, fontNumber=args.face_index or 0) as font:
        if args.text_file:
            visible = args.text_file.read_text(encoding="utf-8")
            required = {ord(char) for char in visible if not char.isspace()}
            missing = sorted(required - set(font.getBestCmap() or {}))
            if missing:
                parser.error("The selected font lacks visible glyphs: " + ", ".join(f"U+{point:04X}" for point in missing))
            options = subset.Options()
            selected = subset.Subsetter(options=options)
            selected.populate(text=visible + "".join(chr(point) for point in range(32, 127)))
            selected.subset(font)
        font.flavor = "woff2"
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.output.with_name(f".{args.output.name}.{os.getpid()}.tmp")
        try:
            font.save(temporary)
            os.replace(temporary, args.output)
        finally:
            temporary.unlink(missing_ok=True)
        print(json.dumps({"output": str(args.output.resolve()), "bytes": args.output.stat().st_size,
                          "characters": len(font.getBestCmap() or {}), "subset": bool(args.text_file)}))


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Font preparation failed: {error}", file=sys.stderr)
        sys.exit(1)
