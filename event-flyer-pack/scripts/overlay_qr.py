#!/usr/bin/env python3
"""Overlay a real QR on any generated design and verify the exported pixels.

Adapted from razbakov/skills event-flyer-pack/scripts/overlay_qr.py at
b82463bb6d1e74f1776cf27591ee68b9547b0120. See NOTICE.md / LICENSE.upstream.md.
Keeps the original thin-compositor approach; adds fail-closed bounds, explicit
white clearing, ambiguity checks, and mandatory expected-URL verification.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import tempfile

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageOps


def decode(image: Image.Image) -> str:
    """Decode at original pixel scale; do not rescale failed proofs to pass."""
    pixels = cv2.cvtColor(np.asarray(image.convert("RGB")), cv2.COLOR_RGB2BGR)
    value, _, _ = cv2.QRCodeDetector().detectAndDecode(pixels)
    return value


def find_white_square(path: Path) -> tuple[int, int, int]:
    with Image.open(path) as source:
        image = np.asarray(source.convert("RGB"))
    height, width = image.shape[:2]
    mask = cv2.inRange(image, (245, 245, 245), (255, 255, 255))
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    candidates = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if min(w, h) < 80 or max(w, h) > min(width, height) * 0.5:
            continue
        if not 0.9 <= w / h <= 1.1:
            continue
        if cv2.contourArea(contour) < w * h * 0.85:
            continue
        candidates.append((x, y, min(w, h), w * h))
    if len(candidates) != 1:
        raise ValueError(
            f"Expected one white QR placeholder, found {len(candidates)}. "
            "Inspect the image and use --x/--y/--size; do not guess."
        )
    x, y, size, _ = candidates[0]
    return x, y, size


def composite(base_path: Path, qr_path: Path, out_path: Path,
              x: int, y: int, size: int, expected: str) -> dict:
    if out_path.suffix.lower() != ".png":
        raise ValueError("Use PNG for overlay output; verify lossy exports separately.")
    if out_path.resolve() in (base_path.resolve(), qr_path.resolve()):
        raise ValueError("Output must not overwrite a source image.")
    with Image.open(base_path) as source:
        dpi = source.info.get("dpi")
        base = source.convert("RGB")
    with Image.open(qr_path) as source:
        qr = source.convert("RGB")
    if size < 80 or x < 0 or y < 0 or x + size > base.width or y + size > base.height:
        raise ValueError("QR rectangle is too small or outside the canvas.")
    if qr.width != qr.height:
        raise ValueError("QR source must be square without captions.")
    qr_pixels = cv2.cvtColor(np.asarray(qr), cv2.COLOR_RGB2BGR)
    actual_source, _, matrix = cv2.QRCodeDetector().detectAndDecode(qr_pixels)
    if not expected or actual_source != expected or matrix is None:
        raise ValueError("QR source does not decode to the exact expected URL.")
    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise ValueError("QR source did not yield a square module grid.")
    # Re-render the verified matrix at an INTEGER pixel pitch. Preserve four
    # whole modules of quiet zone instead of unevenly scaling arbitrary pixels.
    module_count = matrix.shape[0]
    pitch = size // (module_count + 8)
    if pitch < 3:
        raise ValueError("QR placeholder too small: require at least 3 pixels per module.")
    clean = ImageOps.expand(Image.fromarray(matrix).convert("RGB"), border=4, fill="white")
    qr_side = (module_count + 8) * pitch
    clean = clean.resize((qr_side, qr_side), Image.Resampling.NEAREST)
    pad = (size - qr_side) // 2
    # Erase every fake module/shadow, not just the area covered by the new QR.
    ImageDraw.Draw(base).rectangle((x, y, x + size - 1, y + size - 1), fill="white")
    base.paste(clean, (x + pad, y + pad))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temp_name = tempfile.mkstemp(suffix=".png", dir=out_path.parent)
    os.close(descriptor)
    temp_path = Path(temp_name)
    try:
        base.save(temp_path, **({"dpi": dpi} if dpi else {}))
        with Image.open(temp_path) as exported:
            region = exported.crop((x, y, x + size, y + size))
            actual = decode(region)
        if actual != expected:
            raise ValueError(f"Exported QR verification failed: {actual or 'NO DECODE'}")
        temp_path.replace(out_path)
    finally:
        temp_path.unlink(missing_ok=True)
    return {"output": str(out_path), "canvas": list(base.size),
            "qr_region": [x, y, size, size], "expected_url": expected,
            "decoded_url": actual, "qr_pass": True, "module_pixels": pitch,
            "quiet_zone_modules": 4}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_png")
    parser.add_argument("qr_png")
    parser.add_argument("output_png")
    parser.add_argument("--x", type=int)
    parser.add_argument("--y", type=int)
    parser.add_argument("--size", type=int)
    parser.add_argument("--auto-detect", action="store_true")
    parser.add_argument("--verify", required=True, help="Exact expected URL")
    args = parser.parse_args()
    manual = (args.x, args.y, args.size)
    if args.auto_detect and any(value is not None for value in manual):
        parser.error("Choose auto-detect OR all three manual coordinates.")
    if not args.auto_detect and not all(value is not None for value in manual):
        parser.error("Pass --auto-detect or all of --x, --y, --size.")
    try:
        x, y, size = (find_white_square(Path(args.base_png)) if args.auto_detect else manual)
        result = composite(Path(args.base_png), Path(args.qr_png), Path(args.output_png),
                           x, y, size, args.verify)
    except (OSError, ValueError, cv2.error) as exc:
        parser.exit(1, f"Overlay failed: {exc}\n")
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
