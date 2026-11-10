#!/usr/bin/env python3
"""Okou adaptation of Folio: trusted local HTML -> PDF and QA page images.

No automatic editable/Canva export or publishing. Output must be a fresh directory
inside the document project. --png-only retains only PNGs and the contact sheet.
"""
import argparse
import json
from pathlib import Path
import tempfile
import sys
sys.dont_write_bytecode = True

from document import add_style, open_document, output_path

MM_PER_PX = 25.4 / 96


def contact_sheet(pngs, dest, single=False, thumb_h=400):
    """Reader spreads: cover on the right, then 2–3, 4–5; single sheets in a grid."""
    from PIL import Image, ImageDraw
    gap = 24
    with Image.open(pngs[0]) as first:
        tw = round(first.width * thumb_h / first.height)
    groups = [[0]] + [list(range(i, min(i + 2, len(pngs)))) for i in range(1, len(pngs), 2)]
    if single:
        groups = [[i] for i in range(len(pngs))]
    cols = min(3 if not single else 4, len(groups))
    sw = tw if single else 2 * tw
    rows = (len(groups) + cols - 1) // cols
    sheet = Image.new("RGB", (gap + cols * (sw + gap), gap + rows * (thumb_h + 44)), "#d8d9db")
    draw = ImageDraw.Draw(sheet)
    for k, group in enumerate(groups):
        x, y = gap + k % cols * (sw + gap), gap + k // cols * (thumb_h + 44)
        for i in group:
            offset = 0 if single or i % 2 else tw
            with Image.open(pngs[i]) as image:
                sheet.paste(image.resize((tw, thumb_h), Image.Resampling.LANCZOS), (x + offset, y))
            draw.text((x + offset + 5, y + thumb_h + 6), str(i + 1), fill="#474b50")
    sheet.save(dest)
    return dest


def render(args):
    import pypdfium2 as pdfium
    html = Path(args.html).resolve()
    out = output_path(args.out or html.parent / "out", html.parent)
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        raise ValueError("Output exists and is not empty; choose a new --out directory")
    if not 72 <= args.dpi <= 300 or not 0 <= args.bleed <= 10:
        raise ValueError("DPI must be 72–300 and bleed must be 0–10 mm")
    out.parent.mkdir(parents=True, exist_ok=True)
    # Do not leave apparently valid partial deliverables on failure.
    with tempfile.TemporaryDirectory(prefix=".folio-render-", dir=html.parent) as temp:
        stage = Path(temp)
        (stage / "pages").mkdir()
        pdf_path = stage / (html.stem + ".pdf")
        with open_document(html) as page:
            page.emulate_media(media="print")
            add_style(page, f":root{{--bleed:{args.bleed}mm !important}}")
            boxes = page.evaluate("""() => [...document.querySelectorAll('.page')].map(p => {
                const r=p.getBoundingClientRect(), t=(p.querySelector('.trim')||p).getBoundingClientRect();
                return {w:r.width,h:r.height,tw:t.width,th:t.height,b:t.left-r.left};
            })""")
            geo = boxes[0]
            if any(abs(b[k] - geo[k]) > .6 for b in boxes for k in ("w", "h", "tw", "th", "b")):
                raise ValueError("All document pages must share the same paper size and bleed")
            w_mm, h_mm, bleed_mm = (geo[k] * MM_PER_PX for k in ("w", "h", "b"))
            pixels = w_mm / 25.4 * h_mm / 25.4 * args.dpi ** 2
            if min(geo["tw"], geo["th"]) <= 0 or pixels > 40_000_000 or pixels * len(boxes) > 160_000_000:
                raise ValueError("Invalid geometry or excessive raster size; reduce DPI/page count")
            add_style(page, f"@page{{size:{w_mm:.3f}mm {h_mm:.3f}mm;margin:0}} "
                                      "@media print{html,body{margin:0!important;padding:0!important}"
                                      ".page{margin:0!important;box-shadow:none!important}"
                                      ".page:last-child{break-after:auto!important}}")
            page.pdf(path=str(pdf_path), prefer_css_page_size=True, print_background=True)
        pngs = []
        with pdfium.PdfDocument(str(pdf_path)) as pdf:
            count = len(pdf)
            if count != len(boxes):
                raise ValueError(f"PDF/HTML page mismatch: {count} versus {len(boxes)}; fix pagination")
            for i in range(count):
                pdf_page = pdf[i]
                try:
                    bitmap = pdf_page.render(scale=args.dpi / 72)
                    try:
                        image = bitmap.to_pil().convert("RGB")
                    finally:
                        bitmap.close()
                finally:
                    pdf_page.close()
                crop = round(bleed_mm / 25.4 * args.dpi)
                if crop > 0:
                    image = image.crop((crop, crop, image.width - crop, image.height - crop))
                dest = stage / "pages" / f"page-{i + 1:03d}.png"
                image.save(dest, dpi=(args.dpi, args.dpi))
                image.close()
                pngs.append(dest)
        contact_sheet(pngs, stage / "contact.png", single=args.single or args.png_only)
        if args.png_only:
            pdf_path.unlink()
        if out.exists():
            out.rmdir()  # only the previously checked empty directory
        stage.rename(out)
        result = {"pages": count, "trim_mm": [round(geo["tw"] * MM_PER_PX, 2), round(geo["th"] * MM_PER_PX, 2)],
                  "bleed_mm": round(bleed_mm, 2), "preview_dpi": args.dpi,
                  "previews": str(out / "pages"), "contact": str(out / "contact.png")}
        if not args.png_only:
            result["pdf"] = str(out / (html.stem + ".pdf"))
        print(json.dumps(result, indent=2))
        return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("html")
    ap.add_argument("--out")
    ap.add_argument("--bleed", type=float, default=0)
    ap.add_argument("--dpi", type=int, default=110)
    ap.add_argument("--single", action="store_true")
    ap.add_argument("--png-only", action="store_true")
    args = ap.parse_args()
    try:
        render(args)
    except (ValueError, FileNotFoundError) as exc:
        ap.exit(1, f"folio render: {exc}\n")


if __name__ == "__main__":
    main()
