#!/usr/bin/env python3
"""Create source previews and an upload PDF in fixed sibling directories."""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--contact-sheet", action="store_true")
    parser.add_argument("--pdf", action="store_true")
    args = parser.parse_args()
    if not (args.contact_sheet or args.pdf):
        parser.error("Choose --contact-sheet, --pdf, or both")

    work = args.work_dir.resolve()
    source = work / "source-pages"
    pages = sorted(
        (p for p in source.iterdir() if p.is_file() and re.fullmatch(r"page-\d{3,}\.png", p.name)),
        key=lambda p: int(p.stem.split("-")[1]),
    )
    expected = [f"page-{number:03}.png" for number in range(1, len(pages) + 1)]
    if not pages or [p.name for p in pages] != expected:
        parser.error("source-pages needs consecutive original page-001.png, page-002.png, ...")

    # A cached install keeps subsequent preview/PDF calls to one command.
    try:
        from PIL import Image, ImageDraw, ImageOps
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--quiet", "--disable-pip-version-check",
             "--break-system-packages", "Pillow"], check=True, stdout=sys.stderr,
        )
        from PIL import Image, ImageDraw, ImageOps

    result = {"pageCount": len(pages), "pages": str(source), "previews": [], "pdf": None}
    images = []
    try:
        for page in pages:
            with Image.open(page) as image:
                rgba = image.convert("RGBA")
                rgb = Image.new("RGB", image.size, "white")
                rgb.paste(rgba, mask=rgba.getchannel("A"))
                if not args.pdf:
                    rgb.thumbnail((320, 180))
                images.append(rgb)

        if args.contact_sheet:
            previews = work / "previews"
            previews.mkdir(parents=True, exist_ok=True)
            if previews.resolve() == source.resolve():
                parser.error("previews must be separate from source-pages")
            for start in range(0, len(images), 20):
                group = images[start:start + 20]
                rows = (len(group) + 3) // 4
                sheet = Image.new("RGB", (4 * 336, rows * 212), "#eeeeee")
                draw = ImageDraw.Draw(sheet)
                for offset, image in enumerate(group):
                    x, y = (offset % 4) * 336, (offset // 4) * 212
                    thumb = ImageOps.contain(image, (320, 180))
                    sheet.paste(thumb, (x + 8, y + 24))
                    draw.text((x + 8, y + 6), str(start + offset + 1), fill="black")
                target = previews / f"contact-sheet-{start // 20 + 1:03}.png"
                sheet.save(target)
                sheet.close()
                result["previews"].append(str(target))

        if args.pdf:
            upload = work / "upload"
            upload.mkdir(parents=True, exist_ok=True)
            if upload.resolve() == source.resolve():
                parser.error("upload must be separate from source-pages")
            target = upload / "source.pdf"
            images[0].save(target, "PDF", save_all=True, append_images=images[1:], resolution=96, quality=95)
            result["pdf"] = str(target)
    finally:
        for image in images:
            image.close()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
