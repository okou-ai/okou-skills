#!/usr/bin/env python3
"""Restore the packaged style reference and verify its checksum."""
from __future__ import annotations

import argparse
import base64
import hashlib
from pathlib import Path

REFERENCE_SHA256 = "b75d5c270427f16bcff3b8616dd514dd7d9a0445b8f9a28f7221272e882db930"


def restore(encoded: Path, destination: Path) -> Path:
    if destination.suffix.lower() != ".png" or encoded.resolve() == destination.resolve():
        raise ValueError("Write the restored visual reference to a separate .png file.")
    text = "".join(encoded.read_text(encoding="ascii").split())
    data = base64.b64decode(text, validate=True)
    if hashlib.sha256(data).hexdigest() != REFERENCE_SHA256:
        raise ValueError("Visual reference checksum mismatch; do not use a corrupted image.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    return destination


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_png", type=Path, help="Path under this task's scratch/output directory")
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1] / "assets/style-reference.png.b64"
    try:
        result = restore(source, args.output_png)
    except (OSError, ValueError, UnicodeError) as exc:
        parser.exit(1, f"Reference restore failed: {exc}\n")
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
