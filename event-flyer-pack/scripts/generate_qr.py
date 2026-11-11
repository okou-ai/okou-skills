#!/usr/bin/env python3
"""
Generate a QR code that encodes a URL. Export PNG and/or SVG.
Supports styled QR codes with custom module shapes, colors, gradients, and logo overlay.

Examples:
  # Basic QR code
  python generate_qr.py --url "https://example.com" --png qr.png

  # Rounded dots with custom colors
  python generate_qr.py --url "https://example.com" --png qr.png --style rounded --fg "#E5383B" --bg "#FFFFFF"

  # Circle dots with radial gradient and logo
  python generate_qr.py --url "https://example.com" --png qr.png --style circle --gradient radial --gradient-center "#E5383B" --gradient-edge "#1A1A2E" --logo logo.png

  # Vertical bars with horizontal gradient
  python generate_qr.py --url "https://example.com" --png qr.png --style vertical-bars --gradient horizontal --gradient-left "#FF6B6B" --gradient-right "#4ECDC4"

Notes:
- Requires: qrcode, pillow (PIL)
- Styled PNG uses StyledPilImage (module drawers, color masks, embedded images)
- SVG export does not support styled modules (use PNG for styled output)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from urllib.parse import urlparse, urlencode, parse_qsl, urlunparse

import qrcode
from qrcode.constants import ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q, ERROR_CORRECT_H


def validate_url(u: str) -> str:
    u = u.strip()
    parsed = urlparse(u)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("URL must start with http:// or https://")
    if not parsed.netloc:
        raise ValueError("URL must include a domain (netloc).")
    return u


def add_utm(url: str, utm: dict[str, str]) -> str:
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    for k, v in utm.items():
        if v:
            query[f"utm_{k}"] = v
    new_query = urlencode(query, doseq=True)
    return urlunparse(parsed._replace(query=new_query))


def err_level(level: str):
    return {
        "L": ERROR_CORRECT_L,
        "M": ERROR_CORRECT_M,
        "Q": ERROR_CORRECT_Q,
        "H": ERROR_CORRECT_H,
    }[level.upper()]


def parse_color(color_str: str) -> tuple[int, int, int]:
    """Parse hex color (#RRGGBB or #RGB) or named color to RGB tuple."""
    c = color_str.strip().lstrip("#")
    if len(c) == 3:
        c = c[0]*2 + c[1]*2 + c[2]*2
    if len(c) == 6:
        return (int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16))
    raise ValueError(f"Invalid color: {color_str}")


def get_module_drawer(style: str):
    """Return a module drawer instance for the given style name."""
    from qrcode.image.styledpil import StyledPilImage
    from qrcode.image.styles.moduledrawers.pil import (
        SquareModuleDrawer,
        RoundedModuleDrawer,
        CircleModuleDrawer,
        GappedSquareModuleDrawer,
        VerticalBarsDrawer,
        HorizontalBarsDrawer,
    )
    drawers = {
        "square": SquareModuleDrawer(),
        "rounded": RoundedModuleDrawer(),
        "circle": CircleModuleDrawer(),
        "gapped": GappedSquareModuleDrawer(),
        "vertical-bars": VerticalBarsDrawer(),
        "horizontal-bars": HorizontalBarsDrawer(),
    }
    if style not in drawers:
        raise ValueError(f"Unknown style: {style}. Choose from: {', '.join(drawers.keys())}")
    return drawers[style]


def get_color_mask(args):
    """Build a color mask from CLI args. Returns None if no color/gradient options set."""
    from qrcode.image.styles.colormasks import (
        SolidFillColorMask,
        RadialGradiantColorMask,
        SquareGradiantColorMask,
        HorizontalGradiantColorMask,
        VerticalGradiantColorMask,
    )

    bg = parse_color(args.bg) if args.bg else (255, 255, 255)

    if args.gradient:
        if args.gradient == "radial":
            center = parse_color(args.gradient_center) if args.gradient_center else (0, 0, 0)
            edge = parse_color(args.gradient_edge) if args.gradient_edge else (100, 100, 100)
            return RadialGradiantColorMask(back_color=bg, center_color=center, edge_color=edge)
        elif args.gradient == "square":
            center = parse_color(args.gradient_center) if args.gradient_center else (0, 0, 0)
            edge = parse_color(args.gradient_edge) if args.gradient_edge else (100, 100, 100)
            return SquareGradiantColorMask(back_color=bg, center_color=center, edge_color=edge)
        elif args.gradient == "horizontal":
            left = parse_color(args.gradient_left) if args.gradient_left else (0, 0, 0)
            right = parse_color(args.gradient_right) if args.gradient_right else (100, 100, 100)
            return HorizontalGradiantColorMask(back_color=bg, left_color=left, right_color=right)
        elif args.gradient == "vertical":
            top = parse_color(args.gradient_top) if args.gradient_top else (0, 0, 0)
            bottom = parse_color(args.gradient_bottom) if args.gradient_bottom else (100, 100, 100)
            return VerticalGradiantColorMask(back_color=bg, top_color=top, bottom_color=bottom)

    if args.fg:
        fg = parse_color(args.fg)
        return SolidFillColorMask(back_color=bg, front_color=fg)

    if args.bg:
        return SolidFillColorMask(back_color=bg, front_color=(0, 0, 0))

    return None


def make_qr(data: str, error: str, box_size: int, border: int):
    qr = qrcode.QRCode(
        version=None,
        error_correction=err_level(error),
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr


def draw_circular_finder(draw, cx, cy, outer_r, fg=(0, 0, 0), bg=(255, 255, 255)):
    """Draw a concentric-circle finder pattern (target style) to replace the square one."""
    # Three rings: outer filled, middle gap, inner filled
    # Standard QR finder is 7 modules: 1 border + 1 gap + 3 center + 1 gap + 1 border
    # Outer ring: full radius
    # Middle ring (white): ~5/7 of radius
    # Inner circle: ~3/7 of radius
    draw.ellipse([cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r], fill=fg)
    mid_r = int(outer_r * 5 / 7)
    draw.ellipse([cx - mid_r, cy - mid_r, cx + mid_r, cy + mid_r], fill=bg)
    inner_r = int(outer_r * 3 / 7)
    draw.ellipse([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r], fill=fg)


def replace_finder_patterns(img, qr, box_size, border, fg=(0, 0, 0), bg=(255, 255, 255)):
    """Replace the three square finder patterns with circular (target) ones."""
    from PIL import ImageDraw

    draw = ImageDraw.Draw(img)
    modules_count = qr.modules_count
    finder_size = 7  # finder pattern is always 7x7 modules

    # The three finder pattern positions (top-left corner of each, in module coords)
    positions = [
        (0, 0),                              # top-left
        (modules_count - finder_size, 0),     # top-right
        (0, modules_count - finder_size),     # bottom-left
    ]

    for (col, row) in positions:
        # Pixel coordinates of the finder pattern area
        x0 = (border + col) * box_size
        y0 = (border + row) * box_size
        size_px = finder_size * box_size

        # Clear the square finder area
        draw.rectangle([x0, y0, x0 + size_px, y0 + size_px], fill=bg)

        # Draw circular finder centered in that area
        cx = x0 + size_px // 2
        cy = y0 + size_px // 2
        outer_r = size_px // 2
        draw_circular_finder(draw, cx, cy, outer_r, fg=fg, bg=bg)

    return img


def embed_logo(img, logo_path: str, bg: tuple = (255, 255, 255)):
    """Clear a circular area in the center and paste the logo on a clean background."""
    from PIL import Image, ImageDraw

    logo = Image.open(logo_path).convert("RGBA")

    # Logo should be ~25% of QR width
    max_logo_size = int(img.width * 0.25)
    logo.thumbnail((max_logo_size, max_logo_size), Image.LANCZOS)

    # Clear a circular area slightly larger than the logo
    draw = ImageDraw.Draw(img)
    cx, cy = img.width // 2, img.height // 2
    clear_r = int(max(logo.width, logo.height) * 0.6)
    draw.ellipse([cx - clear_r, cy - clear_r, cx + clear_r, cy + clear_r], fill=bg)

    # Paste logo centered
    lx = cx - logo.width // 2
    ly = cy - logo.height // 2
    img.paste(logo, (lx, ly), logo)  # use alpha channel as mask

    return img


def export_png(qr, path: str, caption_label: str | None, show_url: bool, url: str | None,
               style: str | None, color_mask, logo_path: str | None,
               circular_finders: bool = False, box_size: int = 10, border: int = 4,
               fg_color: tuple = (0, 0, 0), bg_color: tuple = (255, 255, 255)):
    from PIL import Image, ImageDraw, ImageFont

    use_styled = style or color_mask or logo_path

    if use_styled:
        from qrcode.image.styledpil import StyledPilImage

        kwargs = {"image_factory": StyledPilImage}
        if style:
            kwargs["module_drawer"] = get_module_drawer(style)
        if color_mask:
            kwargs["color_mask"] = color_mask
        # Don't use lib's embeded_image_path — we handle logo manually to clear background

        img = qr.make_image(**kwargs).convert("RGB")
    else:
        img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    if circular_finders:
        img = replace_finder_patterns(img, qr, box_size, border, fg=fg_color, bg=bg_color)

    if logo_path:
        img = embed_logo(img, logo_path, bg=bg_color)

    if not (caption_label or (show_url and url)):
        img.save(path)
        return

    font = ImageFont.load_default()
    lines = []
    if caption_label:
        lines.append(caption_label.strip())
    if show_url and url:
        lines.append(url.strip())

    draw = ImageDraw.Draw(img)
    padding = 16
    line_h = 14
    text_h = len(lines) * (line_h + 6)

    new_w = img.width
    new_h = img.height + padding + text_h + padding
    out = Image.new("RGB", (new_w, new_h), "white")
    out.paste(img, (0, 0))

    draw2 = ImageDraw.Draw(out)
    y = img.height + padding
    for line in lines:
        bbox = draw2.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        x = max(0, (new_w - w) // 2)
        draw2.text((x, y), line, fill="black", font=font)
        y += line_h + 6

    out.save(path)


def export_svg(qr, path: str, caption_label: str | None, show_url: bool, url: str | None):
    """SVG export — basic only (no styled modules). Use PNG for styled output."""
    from qrcode.image.svg import SvgImage
    import re

    img = qr.make_image(image_factory=SvgImage)
    svg = img.to_string().decode("utf-8")

    if not (caption_label or (show_url and url)):
        PathWrite(path, svg)
        return

    caption_lines = []
    if caption_label:
        caption_lines.append(caption_label.strip())
    if show_url and url:
        caption_lines.append(url.strip())

    m = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg)
    if not m:
        PathWrite(path, svg)
        return
    w = int(m.group(1))
    h = int(m.group(2))

    extra = 70 + 20 * (len(caption_lines) - 1)
    new_h = h + extra

    svg2 = re.sub(r'viewBox="0 0 \d+ \d+"', f'viewBox="0 0 {w} {new_h}"', svg, count=1)
    text_y = h + 35
    text_elems = []
    for line in caption_lines:
        text_elems.append(
            f'<text x="{w/2:.1f}" y="{text_y}" text-anchor="middle" '
            f'font-family="Arial, sans-serif" font-size="18" fill="#000">'
            f'{EscapeXML(line)}</text>'
        )
        text_y += 24

    svg2 = svg2.replace("</svg>", "\n" + "\n".join(text_elems) + "\n</svg>")
    PathWrite(path, svg2)


def EscapeXML(s: str) -> str:
    return (s.replace("&", "&amp;")
             .replace("<", "&lt;")
             .replace(">", "&gt;")
             .replace('"', "&quot;")
             .replace("'", "&apos;"))


def PathWrite(path: str, content: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(content, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description="Generate styled QR codes with custom shapes, colors, gradients, and logos.")

    # Core
    ap.add_argument("--url", required=True, help="Destination URL to encode.")
    ap.add_argument("--png", default="", help="Output PNG path.")
    ap.add_argument("--svg", default="", help="Output SVG path (basic style only).")
    ap.add_argument("--error", default="M", choices=["L","M","Q","H"], help="Error correction level.")
    ap.add_argument("--box-size", type=int, default=10, help="QR pixel size per module.")
    ap.add_argument("--border", type=int, default=4, help="Quiet zone border (modules).")

    # Captions
    ap.add_argument("--caption-label", default="", help="Caption label (e.g., 'Scan to join').")
    ap.add_argument("--show-url", action="store_true", help="Show URL as caption line.")

    # Style — module shape
    ap.add_argument("--style", default="", choices=["", "square", "rounded", "circle", "gapped", "vertical-bars", "horizontal-bars"],
                    help="Module dot style (PNG only).")

    # Style — colors
    ap.add_argument("--fg", default="", help="Foreground color (hex, e.g. '#E5383B').")
    ap.add_argument("--bg", default="", help="Background color (hex, e.g. '#FFFFFF').")

    # Style — gradients
    ap.add_argument("--gradient", default="", choices=["", "radial", "square", "horizontal", "vertical"],
                    help="Gradient type (PNG only).")
    ap.add_argument("--gradient-center", default="", help="Center color for radial/square gradient.")
    ap.add_argument("--gradient-edge", default="", help="Edge color for radial/square gradient.")
    ap.add_argument("--gradient-left", default="", help="Left color for horizontal gradient.")
    ap.add_argument("--gradient-right", default="", help="Right color for horizontal gradient.")
    ap.add_argument("--gradient-top", default="", help="Top color for vertical gradient.")
    ap.add_argument("--gradient-bottom", default="", help="Bottom color for vertical gradient.")

    # Style — logo
    ap.add_argument("--logo", default="", help="Path to logo image to embed in center (PNG only).")

    # Style — finder patterns
    ap.add_argument("--circular-finders", action="store_true",
                    help="Replace square finder patterns with concentric circles (PNG only).")

    # UTM
    ap.add_argument("--utm-source", default="", dest="utm_source")
    ap.add_argument("--utm-medium", default="", dest="utm_medium")
    ap.add_argument("--utm-campaign", default="", dest="utm_campaign")
    ap.add_argument("--utm-content", default="", dest="utm_content")
    ap.add_argument("--utm-term", default="", dest="utm_term")

    args = ap.parse_args()

    url = validate_url(args.url)
    utm = {
        "source": args.utm_source,
        "medium": args.utm_medium,
        "campaign": args.utm_campaign,
        "content": args.utm_content,
        "term": args.utm_term,
    }
    final_url = add_utm(url, utm) if any(utm.values()) else url

    # Auto-upgrade error correction when logo is used
    error = args.error
    if args.logo and error != "H":
        error = "H"
        print("Note: Error correction upgraded to H (required for logo overlay).", file=sys.stderr)

    qr = make_qr(final_url, error, args.box_size, args.border)

    caption_label = args.caption_label.strip() or None
    style = args.style.strip() or None
    color_mask = get_color_mask(args)
    logo_path = args.logo.strip() or None

    if logo_path and not Path(logo_path).is_file():
        raise FileNotFoundError(f"Logo file not found: {logo_path}")

    if not args.png and not args.svg:
        args.png = "qr.png"

    # Resolve fg/bg colors for finder patterns
    fg_color = parse_color(args.fg) if args.fg else (0, 0, 0)
    bg_color = parse_color(args.bg) if args.bg else (255, 255, 255)

    if args.png:
        export_png(qr, args.png, caption_label, args.show_url, final_url, style, color_mask, logo_path,
                   circular_finders=args.circular_finders, box_size=args.box_size, border=args.border,
                   fg_color=fg_color, bg_color=bg_color)

    if args.svg:
        if style or color_mask or logo_path:
            print("Warning: SVG export does not support styled modules/colors/logos. Use PNG for styled output.", file=sys.stderr)
        export_svg(qr, args.svg, caption_label, args.show_url, final_url)

    print(final_url)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)
