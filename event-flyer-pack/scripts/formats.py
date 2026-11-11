#!/usr/bin/env python3
"""Deterministic event-pack formats; no image generation or invented bleed.

Normalize bases BEFORE QR overlay. Export four-up/tent/story AFTER QR overlay;
verify each printed panel from the exported PDF, not just its source image.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import tempfile

import pymupdf as fitz
from PIL import Image, ImageOps
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from overlay_qr import decode

A6_PIXELS = (1240, 1748)
A4_MM = (210, 297)
A6_MM = (105, 148)


def load(path: Path) -> Image.Image:
    with Image.open(path) as image:
        return image.convert("RGB")


def assert_code(image: Image.Image, expected: str, label: str) -> dict:
    actual = decode(image)
    if not expected or actual != expected:
        raise ValueError(f"{label}: expected URL not decoded ({actual or 'NO DECODE'}).")
    return {"panel": label, "expected_url": expected, "decoded_url": actual, "qr_pass": True}


def assert_a6(path: Path, expected: str) -> Image.Image:
    image = load(path)
    if image.size != A6_PIXELS:
        raise ValueError(f"{path}: require A6 master {A6_PIXELS}, got {image.size}.")
    assert_code(image, expected, path.name)
    return image


def verify_pdf(path: Path, boxes: list[tuple[float, float, float, float]],
               expected: str, rotate_first: bool = False) -> list[dict]:
    checks = []
    with fitz.open(path) as document:
        if len(document) != 1:
            raise ValueError("Expected a single-page PDF.")
        page = document[0]
        # Boxes are mm, with a top-left origin. Decode at final 300-dpi pixels.
        for index, box in enumerate(boxes):
            rect = fitz.Rect(*(value * mm for value in box))
            pixels = page.get_pixmap(clip=rect, dpi=300, alpha=False)
            image = Image.frombytes("RGB", (pixels.width, pixels.height), pixels.samples)
            if rotate_first and index == 0:
                image = image.transpose(Image.Transpose.ROTATE_180)
            checks.append(assert_code(image, expected, f"PDF panel {index + 1}"))
    return checks


def normalize(source: Path, target: Path, width: int, height: int, matte: str) -> dict:
    if width <= 0 or height <= 0:
        raise ValueError("Canvas dimensions must be positive.")
    image = load(source)
    contained = ImageOps.contain(image, (width, height), Image.Resampling.LANCZOS)
    output = Image.new("RGB", (width, height), matte)
    output.paste(contained, ((width - contained.width) // 2, (height - contained.height) // 2))
    target.parent.mkdir(parents=True, exist_ok=True)
    output.save(target, dpi=(300, 300))
    return {"output": str(target), "input_pixels": list(image.size),
            "output_pixels": [width, height], "content_pixels": list(contained.size),
            "upscaled": contained.width > image.width or contained.height > image.height,
            "qr_verified": False, "note": "Base only: inspect padding, then overlay QR."}


def four_up(front: Path, back: Path, out: Path, slug: str, expected: str) -> dict:
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
        raise ValueError("Use a lowercase alphanumeric filename slug with hyphens.")
    images = [("front", assert_a6(front, expected)), ("back", assert_a6(back, expected))]
    out.mkdir(parents=True, exist_ok=True)
    scale = 0.95
    tile_w, tile_h = (dimension * scale for dimension in A6_MM)
    left, bottom = (A4_MM[0] - 2 * tile_w) / 2, (A4_MM[1] - 2 * tile_h) / 2
    results = []
    # Build and verify both before exposing either final file.
    with tempfile.TemporaryDirectory(dir=out) as scratch:
        staged = []
        for side, image in images:
            destination = out / f"{slug}-a4-4up-{side}.pdf"
            temp = Path(scratch) / destination.name
            pdf = canvas.Canvas(str(temp), pagesize=tuple(value * mm for value in A4_MM))
            pdf.setTitle(f"{slug} — {side} — 95% A6 home-print sheet")
            boxes = []
            for row in range(2):
                for col in range(2):
                    x, y = left + col * tile_w, bottom + row * tile_h
                    pdf.drawImage(ImageReader(image), x * mm, y * mm,
                                  tile_w * mm, tile_h * mm)
                    top = A4_MM[1] - y - tile_h
                    boxes.append((x, top, x + tile_w, top + tile_h))
            # Crop marks ONLY in outside margins; do not cross panel artwork.
            pdf.setLineWidth(0.25)
            for x in (left, left + tile_w, left + 2 * tile_w):
                for y in (bottom, bottom + 2 * tile_h):
                    sign = -1 if y == bottom else 1
                    pdf.line(x * mm, (y + sign) * mm, x * mm, (y + sign * 3.5) * mm)
            for y in (bottom, bottom + tile_h, bottom + 2 * tile_h):
                for x in (left, left + 2 * tile_w):
                    sign = -1 if x == left else 1
                    pdf.line((x + sign) * mm, y * mm, (x + sign * 3.5) * mm, y * mm)
            pdf.showPage()
            pdf.save()
            checks = verify_pdf(temp, boxes, expected)
            staged.append((temp, destination))
            results.append({"output": str(destination), "pages": 1, "qr_checks": checks})
        for temp, destination in staged:
            temp.replace(destination)
    return {"outputs": results, "page_mm": list(A4_MM),
            "tile_mm": [tile_w, tile_h], "a6_scale": scale,
            "bleed_mm": 0, "note": "Print at Actual size / 100%; tiles are 95% A6, not true A6."}


def tent(top: Path, bottom: Path, out_png: Path, expected: str) -> dict:
    upper, lower = assert_a6(top, expected), assert_a6(bottom, expected)
    if out_png.suffix.lower() != ".png":
        raise ValueError("Tent image output must be .png.")
    out_pdf = out_png.with_suffix(".pdf")
    out_png.parent.mkdir(parents=True, exist_ok=True)
    width, height = A6_PIXELS
    image = Image.new("RGB", (width, height * 2), "white")
    image.paste(upper.transpose(Image.Transpose.ROTATE_180), (0, 0))
    image.paste(lower, (0, height))
    with tempfile.TemporaryDirectory(dir=out_png.parent) as scratch:
        temp_png, temp_pdf = Path(scratch) / "tent.png", Path(scratch) / "tent.pdf"
        image.save(temp_png, dpi=(300, 300))
        exported = load(temp_png)
        png_checks = [
            assert_code(exported.crop((0, 0, width, height)).transpose(Image.Transpose.ROTATE_180),
                        expected, "PNG top, rotated upright"),
            assert_code(exported.crop((0, height, width, height * 2)), expected, "PNG bottom")
        ]
        pdf = canvas.Canvas(str(temp_pdf), pagesize=(105 * mm, 296 * mm))
        pdf.setTitle("Tent card — 105 x 296 mm — fold at 148 mm")
        pdf.drawImage(ImageReader(exported), 0, 0, 105 * mm, 296 * mm)
        pdf.showPage()
        pdf.save()
        pdf_checks = verify_pdf(temp_pdf, [(0, 0, 105, 148), (0, 148, 105, 296)],
                                expected, rotate_first=True)
        temp_png.replace(out_png)
        temp_pdf.replace(out_pdf)
    return {"output_png": str(out_png), "output_pdf": str(out_pdf),
            "pixels": [width, height * 2], "page_mm": [105, 296], "fold_mm": 148,
            "bleed_mm": 0, "png_qr_checks": png_checks, "pdf_qr_checks": pdf_checks}


def story(source: Path, target: Path, expected: str) -> dict:
    image = load(source)
    if image.size != (1080, 1920):
        raise ValueError("Story must be 1080x1920 before overlay and JPEG export.")
    if target.suffix.lower() not in (".jpg", ".jpeg"):
        raise ValueError("Story export requires .jpg or .jpeg.")
    assert_code(image, expected, "Story source")
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=target.parent) as scratch:
        temp = Path(scratch) / "story.jpg"
        image.save(temp, quality=95, subsampling=0)
        check = assert_code(load(temp), expected, "Final JPEG")
        temp.replace(target)
    return {"output": str(target), "pixels": [1080, 1920], "qr_checks": [check]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    normal = commands.add_parser("normalize", help="Prepare a base BEFORE QR overlay")
    normal.add_argument("source", type=Path)
    normal.add_argument("target", type=Path)
    normal.add_argument("--width", required=True, type=int)
    normal.add_argument("--height", required=True, type=int)
    normal.add_argument("--matte", default="#181818")
    four = commands.add_parser("four-up")
    four.add_argument("front", type=Path)
    four.add_argument("back", type=Path)
    four.add_argument("--out", type=Path, required=True)
    four.add_argument("--slug", required=True)
    four.add_argument("--verify", required=True)
    card = commands.add_parser("tent")
    card.add_argument("top", type=Path)
    card.add_argument("bottom", type=Path)
    card.add_argument("target", type=Path)
    card.add_argument("--verify", required=True)
    social = commands.add_parser("story")
    social.add_argument("source", type=Path)
    social.add_argument("target", type=Path)
    social.add_argument("--verify", required=True)
    args = parser.parse_args()
    try:
        if args.command == "normalize":
            if args.source.resolve() == args.target.resolve():
                raise ValueError("Preserve the original base; use a different output path.")
            result = normalize(args.source, args.target, args.width, args.height, args.matte)
        elif args.command == "four-up":
            result = four_up(args.front, args.back, args.out, args.slug, args.verify)
        elif args.command == "tent":
            if args.target.resolve() in (args.top.resolve(), args.bottom.resolve()):
                raise ValueError("Output must not overwrite either source panel.")
            result = tent(args.top, args.bottom, args.target, args.verify)
        else:
            if args.source.resolve() == args.target.resolve():
                raise ValueError("Preserve the source PNG; use a different output path.")
            result = story(args.source, args.target, args.verify)
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(1, f"Format failed: {exc}\n")
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
