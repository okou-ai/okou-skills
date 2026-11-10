#!/usr/bin/env python3
"""Compile curated prompts and export/check raster thumbnails; never calls a model."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MAX_BYTES = 2_000_000  # Conservative decimal limit, below 2 MiB.
SIZE = (1280, 720)
FIELDS = {
    "template_id", "video_title", "audience", "visual_hook", "subject",
    "scene_details", "overlay_lines", "language", "brand_colors",
    "reference_instruction",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def catalog() -> dict[str, dict[str, Any]]:
    data = read_json(ROOT / "templates" / "catalog.json")
    if data.get("schema_version") != 1:
        raise ValueError("unsupported catalog schema")
    result = {}
    for entry in data["templates"]:
        if entry["id"] in result:
            raise ValueError("duplicate template ID")
        result[entry["id"]] = entry
    return result


def validate_brief(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise ValueError("brief must be a JSON object")
    unknown = set(data) - FIELDS
    if unknown:
        raise ValueError("unknown brief fields: " + ", ".join(sorted(unknown)))
    result = dict(data)
    for field in ("template_id", "video_title", "audience", "visual_hook", "subject", "language"):
        value = result.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field} must be a nonempty string")
        if len(value) > 3000:
            raise ValueError(f"{field} is too long")
        result[field] = value.strip()
    if result["template_id"] not in catalog():
        raise ValueError("unknown template_id; run the list command")
    for field in ("scene_details", "reference_instruction"):
        value = result.get(field, "")
        if not isinstance(value, str) or len(value) > 3000:
            raise ValueError(f"{field} must be a string of at most 3000 characters")
        result[field] = value.strip()
    lines = result.get("overlay_lines", [])
    if not isinstance(lines, list) or len(lines) > 2:
        raise ValueError("overlay_lines must contain zero, one or two strings")
    for line in lines:
        if not isinstance(line, str) or not line.strip() or "\n" in line or "\r" in line:
            raise ValueError("each overlay line must be a nonempty single-line string")
        if len(line.strip()) > 40:
            raise ValueError("overlay line too long for a thumbnail")
    lines = [line.strip() for line in lines]
    text = " ".join(lines)
    if re.search(r"[\u3040-\u30ff\u3400-\u9fff\uac00-\ud7af]", text):
        if len(re.sub(r"\s", "", text)) > 20:
            raise ValueError("keep CJK/mixed overlay text within 20 visible characters")
    elif len(text.split()) > 6:
        raise ValueError("keep overlay text within six words; prefer four or fewer")
    result["overlay_lines"] = lines
    colors = result.get("brand_colors", [])
    if not isinstance(colors, list) or len(colors) > 3 or any(
        not isinstance(c, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", c) for c in colors
    ):
        raise ValueError("brand_colors must contain at most three #RRGGBB colors")
    result["brand_colors"] = colors
    return result


def compile_prompt(brief: Any) -> str:
    data = validate_brief(brief)
    template = catalog()[data["template_id"]]
    quote = lambda value: json.dumps(value, ensure_ascii=False)
    parts = [
        "Create ONE original raster YouTube video thumbnail, landscape 16:9. "
        "Compose for a 1280x720 delivery and immediate readability at 168x94 pixels.",
        f"Video title (context only, not extra text to render): {quote(data['video_title'])}. "
        f"Audience: {data['audience']}. Visual promise / question: {data['visual_hook']}.",
        "Template direction: " + template["direction"],
        "Main subject and action: " + data["subject"],
    ]
    if data["scene_details"]:
        parts.append("Scene details: " + data["scene_details"])
    if data["brand_colors"]:
        parts.append("Override the template's default palette with these brand colors: "
                     + ", ".join(data["brand_colors"]) + ". Use neutral white/black only as needed for legibility.")
    if data["reference_instruction"]:
        parts.append("Supplied-image instruction: " + data["reference_instruction"])
    lines = data["overlay_lines"]
    if lines:
        parts.append(
            f"Render ONLY the following {len(lines)} headline line(s), in this exact order, "
            f"in {data['language']}. Headline lines from top to bottom, encoded as a JSON array: "
            + json.dumps(lines, ensure_ascii=False) + ". "
            "The array punctuation is metadata, not artwork; preserve every character inside each "
            "string, including any literal slash. Use oversized bold clean sans-serif lettering with "
            "strong background contrast, precise spelling and comfortable spacing. Place it in the "
            "template's reserved text zone, clear of the subject. "
            "Do not render the video title, extra captions, UI text or a watermark."
        )
    else:
        parts.append("Create a visual-only thumbnail: no lettering, numbers, labels or watermark. "
                     "Keep the template's text zone as intentional breathing room.")
    parts.append(
        "Composition instruction, not visible artwork: keep the lower-right corner quiet, naturally "
        "continuous with the scene, and free of essential text or subject details. The finished image "
        "itself contains no added interface badges, corner placeholder boxes, safe-zone guides "
        "or layout-measurement annotations. Do not visualize layout instructions. Use one focal subject or one "
        "clearly grouped comparison, at most three main visual elements, clean margins and separation "
        "from both light and dark feed backgrounds. Avoid tiny decoration and unsupported metrics. "
        "Use original generic objects unless real reference assets are supplied; do not invent a "
        "real person's likeness or distort an existing product's shape or logo. Make the visual promise "
        "honest to the supplied context. A demonstration concept is not evidence of real-world results."
    )
    return "\n\n".join(parts) + "\n"


def ensure_new(path: Path) -> None:
    if path.exists():
        raise ValueError(f"refusing to overwrite: {path}; use a new versioned path")
    if not path.parent.is_dir():
        path.parent.mkdir(parents=True, exist_ok=True)


def image_modules():
    try:
        from PIL import Image, ImageOps
    except ImportError as exc:
        raise ValueError("image operations require Pillow; install requirements.txt in an isolated environment") from exc
    return Image, ImageOps


def image_info(path: Path) -> dict[str, Any]:
    Image, _ = image_modules()
    try:
        with Image.open(path) as image:
            if image.width * image.height > 40_000_000:
                raise ValueError("image exceeds 40 million pixels")
            image.verify()
        with Image.open(path) as image:
            width, height = image.size
            fmt = image.format
            image.load()
    except Image.DecompressionBombError as exc:
        raise ValueError("image exceeds Pillow's safe pixel limit") from exc
    size = path.stat().st_size
    return {
        "path": str(path), "width": width, "height": height, "format": fmt,
        "bytes": size, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "exact_1280x720": (width, height) == SIZE,
        "under_2mb": size < MAX_BYTES,
        "supported_format": fmt in ("JPEG", "PNG"), "final_jpeg": fmt == "JPEG",
    }


def check_image(path: Path) -> dict[str, Any]:
    result = image_info(path)
    result["technical_pass"] = all(result[key] for key in (
        "exact_1280x720", "under_2mb", "supported_format", "final_jpeg"
    ))
    result["visual_review"] = "required: text, focal point, references and duration safe zone"
    result["ctr_effectiveness"] = "not measured"
    return result


def export_image(source: Path, output: Path, qa_dir: Path, allow_crop: bool = False) -> dict[str, Any]:
    Image, ImageOps = image_modules()
    if output.suffix.lower() not in (".jpg", ".jpeg"):
        raise ValueError("export output must use .jpg or .jpeg")
    preview = qa_dir / (output.stem + "-168x94.jpg")
    ensure_new(output)
    ensure_new(preview)
    # Validate the encoded file before decoding and orienting it.
    image_info(source)
    with Image.open(source) as opened:
        image = ImageOps.exif_transpose(opened)
        width, height = image.size
        if width < SIZE[0] or height < SIZE[1]:
            raise ValueError("source smaller than 1280x720; regenerate rather than silently upscale")
        mismatch = abs((width / height) / (16 / 9) - 1)
        if mismatch > 0.03 and not allow_crop:
            raise ValueError("source is not near 16:9; review framing before explicitly using --allow-crop")
        if "A" in image.getbands() or "transparency" in image.info:
            rgba = image.convert("RGBA")
            canvas = Image.new("RGBA", rgba.size, "white")
            image = Image.alpha_composite(canvas, rgba).convert("RGB")
        else:
            image = image.convert("RGB")
        image = ImageOps.fit(image, SIZE, method=Image.Resampling.LANCZOS)
        for quality in (95, 90, 85, 80, 75):
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=quality, optimize=True)
            if buffer.tell() < MAX_BYTES:
                final_bytes = buffer.getvalue()
                break
        else:
            raise ValueError("could not meet the file-size cap without excessive compression")
        # Build the preview from the exact final JPEG before creating either file.
        with Image.open(io.BytesIO(final_bytes)) as delivered:
            mobile = delivered.resize((168, 94), Image.Resampling.LANCZOS)
            preview_buffer = io.BytesIO()
            mobile.save(preview_buffer, format="JPEG", quality=95)
        created = []
        try:
            for path, content in ((output, final_bytes), (preview, preview_buffer.getvalue())):
                with path.open("xb") as handle:
                    created.append(path)
                    handle.write(content)
        except OSError:
            # Preserve any pre-existing raced-in file; remove only files we created.
            for path in created:
                path.unlink(missing_ok=True)
            raise
    result = check_image(output)
    result.update({
        "source_size": [width, height], "near_ratio_crop": mismatch > 0,
        "large_crop_explicitly_allowed": bool(allow_crop), "mobile_preview": str(preview),
    })
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="list the curated templates")
    compile_cmd = commands.add_parser("compile", help="write a final prompt; does not generate an image")
    compile_cmd.add_argument("--brief", type=Path, required=True)
    compile_cmd.add_argument("--out", type=Path)
    export_cmd = commands.add_parser("export", help="export an actual model image to an exact-size JPEG")
    export_cmd.add_argument("--input", type=Path, required=True)
    export_cmd.add_argument("--out", type=Path, required=True)
    export_cmd.add_argument("--qa-dir", type=Path, required=True)
    export_cmd.add_argument("--allow-crop", action="store_true")
    check_cmd = commands.add_parser("check", help="check technical requirements, not visual quality or CTR")
    check_cmd.add_argument("image", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            result = [{key: value[key] for key in ("id", "name", "best_for", "source_ids")}
                      for value in catalog().values()]
        elif args.command == "compile":
            prompt = compile_prompt(read_json(args.brief))
            if args.out:
                ensure_new(args.out)
                with args.out.open("x", encoding="utf-8") as handle:
                    handle.write(prompt)
                result = {"prompt": str(args.out), "image_generated": False}
            else:
                print(prompt, end="")
                return 0
        elif args.command == "export":
            result = export_image(args.input, args.out, args.qa_dir, args.allow_crop)
        else:
            result = check_image(args.image)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1 if isinstance(result, dict) and result.get("technical_pass") is False else 0
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
