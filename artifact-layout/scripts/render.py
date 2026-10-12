#!/usr/bin/env python3
"""Compose literal report content with the maintained Okou layout assets."""

import argparse
import hashlib
import html
import json
import math
import re
import unicodedata
from pathlib import Path

from primitives import (
    DIRECTIONS,
    EXTRA_TYPES,
    GRAPHICS,
    heat_color,
    extra_geometry,
    validate_extra,
)

ASSETS = Path(__file__).resolve().parent.parent / "assets"
LAYOUTS = {"single", "two-column", "sidebar", "modular"}
TYPES = {
    "prose",
    "big-number",
    "metric-strip",
    "callout",
    "takeaways",
    "pull-quote",
    "image-text",
    "figure",
    "bar-chart",
    "line-chart",
    "small-multiples",
    "data-table",
    "comparison-table",
    "timeline",
    "source-note",
} | EXTRA_TYPES


def escape(value):
    return html.escape(str(value), quote=True)


def load_asset(name):
    return json.loads((ASSETS / name).read_text(encoding="utf-8"))


def validate_report(report, source_dir):
    """Validate renderable shapes before creating output; not a factual audit."""

    def text(obj, key):
        if not isinstance(obj.get(key), str) or not obj[key].strip():
            raise ValueError(f"{key} must be a nonempty string")

    def items(obj, key):
        value = obj.get(key)
        if not isinstance(value, list) or not value:
            raise ValueError(f"{key} must be a nonempty list")
        return value

    def strings(obj, key):
        for value in items(obj, key):
            if not isinstance(value, str):
                raise TypeError(f"{key} must contain strings")

    def chart(block):
        strings(block, "labels")
        values = items(block, "values")
        if len(values) != len(block["labels"]):
            raise ValueError("Chart labels and values must have the same length")
        if any(
            isinstance(v, bool)
            or not isinstance(v, (int, float))
            or not math.isfinite(v)
            for v in values
        ):
            raise ValueError("Chart values must be finite numbers")

    def block_shape(block):
        if not isinstance(block, dict) or block.get("type") not in TYPES:
            raise ValueError("Unknown or missing component type")
        if block.get("span", "column") not in {"column", "all"}:
            raise ValueError("Block span must be column or all")
        if block.get("placement", "main") not in {"main", "aside"}:
            raise ValueError("Block placement must be main or aside")
        kind = block["type"]
        if kind in {"prose", "image-text"}:
            strings(block, "paragraphs")
        if kind in {"callout", "pull-quote", "source-note"}:
            text(block, "text")
        if kind == "big-number":
            text(block, "label")
            if not isinstance(block.get("value"), (str, int, float)):
                raise ValueError("Metric value must be supplied text or a number")
        if kind == "metric-strip":
            for item in items(block, "items"):
                block_shape({**item, "type": "big-number"})
        if kind == "takeaways":
            strings(block, "items")
        if kind == "timeline":
            for item in items(block, "items"):
                text(item, "label")
                text(item, "text")
        if kind in {"figure", "image-text"}:
            text(block, "image")
            text(block, "alt")
            path = (source_dir / block["image"]).resolve()
            if (
                path.suffix.lower() not in {".png", ".jpg", ".jpeg", ".svg"}
                or not path.is_file()
            ):
                raise ValueError(
                    f"Figure must name an existing PNG, JPEG, or SVG: {block['image']}"
                )
        if kind in {"bar-chart", "line-chart"}:
            chart(block)
        if kind == "small-multiples":
            for item in items(block, "charts"):
                if item.get("type") not in {"bar-chart", "line-chart"}:
                    raise ValueError(
                        "Small multiples support bar-chart and line-chart panels"
                    )
                chart(item)
        if kind in {"data-table", "comparison-table", "heatmap-table"}:
            strings(block, "headers")
            rows = block.get("rows")
            if not isinstance(rows, list) or any(
                not isinstance(row, list) or len(row) != len(block["headers"])
                for row in rows
            ):
                raise ValueError("Every table row must match the headers")
            for column in block.get("numericColumns", []):
                if (
                    isinstance(column, bool)
                    or not isinstance(column, int)
                    or not 0 <= column < len(block["headers"])
                ):
                    raise ValueError("Numeric table column is outside the headers")
        if kind in EXTRA_TYPES:
            validate_extra(block)

    if not isinstance(report, dict) or report.get("version") != 1:
        raise ValueError("Report model version must be 1")
    text(report, "title")
    text(report, "language")
    if report.get("theme") not in load_asset("themes.json"):
        raise ValueError("Unknown layout theme")
    recipes = load_asset("recipes.json")
    if report.get("recipe") not in recipes:
        raise ValueError("Unknown visual recipe")
    for section in items(report, "sections"):
        layout = section.get("layout", recipes[report["recipe"]]["defaultLayout"])
        if layout not in LAYOUTS:
            raise ValueError("Unknown section layout")
        for block in items(section, "blocks"):
            block_shape(block)
            if block.get("placement") == "aside" and layout != "sidebar":
                raise ValueError("Aside placement requires a sidebar section")


def numeric_cell(block, column, value):
    return column in block.get("numericColumns", []) or bool(
        re.fullmatch(r"[+−\-]?[¥￥$€£]?\s*\d[\d,. ]*(?:\s*%)?", str(value).strip())
    )


def bundle_image(path, output):
    path = Path(path)
    data = path.read_bytes()
    name = "assets/image-" + hashlib.sha256(data).hexdigest()[:20] + path.suffix.lower()
    target = output / name
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(data)
    return name


def chart_domain(block):
    values = [v for panel in block.get("charts", [block]) for v in panel["values"]]
    low, high = min(0, min(values)), max(0, max(values))
    if low == high:
        high = low + 1
    return low, high


def wrap_label(value, width, size=30):
    """Wrap labels without discarding text or shrinking their type."""
    lines, line, used = [], "", 0
    for char in str(value):
        factor = 1 if unicodedata.east_asian_width(char) in {"W", "F"} else 0.6
        if char in "WM@":
            factor = 1
        if line and used + factor * size > width:
            lines.append(line)
            line, used = "", 0
        line += char
        used += factor * size
    if line:
        lines.append(line)
    return lines or [""]


def chart_geometry(block, theme, domain=None, label_size=30):
    """The same coordinates drive HTML SVG and native Word chart images."""
    if block["type"] in GRAPHICS:
        return extra_geometry(block, theme, wrap_label, label_size)
    low, high = domain or chart_domain(block)
    width = 640
    height = 350
    lines, rects, texts, points = [], [], [], []
    font = label_size
    if block["type"] == "bar-chart":
        start, end = 215, 530

        def scale(value):
            return start + (value - low) / (high - low) * (end - start)

        zero = scale(0)
        y = 36
        for label, value in zip(block["labels"], block["values"]):
            wrapped = wrap_label(label, 190, size=font)
            line_height = font + 4
            row_height = max(58, len(wrapped) * line_height + 14)
            bar_y = y + (row_height - 26) / 2
            endpoint = scale(value)
            rects.append(
                (
                    min(zero, endpoint),
                    bar_y,
                    max(1, abs(endpoint - zero)),
                    26,
                    theme["accent"],
                )
            )
            texts.extend(
                (
                    0,
                    bar_y
                    + 13
                    + font * 0.32
                    - (len(wrapped) - 1) * line_height / 2
                    + offset * line_height,
                    line,
                    "start",
                    theme["ink"],
                    font,
                )
                for offset, line in enumerate(wrapped)
            )
            texts.append(
                (635, bar_y + 13 + font * 0.32, str(value), "end", theme["ink"], font)
            )
            y += row_height
        height = max(240, y + 52)
        lines.append((zero, 28, zero, height - 40, theme["rule"]))
        texts.extend(
            [
                (start, height - 5, format(low, ".6g"), "start", theme["muted"], font),
                (end, height - 5, format(high, ".6g"), "end", theme["muted"], font),
            ]
        )
    else:
        start, end, top, bottom = 76, 580, 30, 276
        for step in range(3):
            value = low + step * (high - low) / 2
            y = bottom - step * (bottom - top) / 2
            lines.append((start, y, end, y, theme["rule"]))
            texts.append(
                (62, y + font * 0.3, format(value, ".5g"), "end", theme["muted"], font)
            )
        count = len(block["values"])
        label_width = max(48, (end - start) / max(1, count - 1) * 0.85)
        label_lines = 1
        for index, (label, value) in enumerate(zip(block["labels"], block["values"])):
            x = start + index / max(1, count - 1) * (end - start)
            y = bottom - (value - low) / (high - low) * (bottom - top)
            points.append((x, y))
            wrapped = wrap_label(label, label_width, size=font)
            label_lines = max(label_lines, len(wrapped))
            texts.extend(
                (x, 322 + offset * 34, line, "middle", theme["ink"], font)
                for offset, line in enumerate(wrapped)
            )
        height = max(350, 334 + (label_lines - 1) * 34)
    return {
        "width": width,
        "height": height,
        "lines": lines,
        "rects": rects,
        "texts": texts,
        "points": points,
    }


def chart_svg(block, theme, domain=None, label_size=30):
    geometry = chart_geometry(block, theme, domain, label_size)
    name = block.get("title") or block.get("label") or "Supplied chart"
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {geometry["width"]} {geometry["height"]}" role="img" aria-label="{escape(name)}">',
        f"<title>{escape(name)}</title>",
    ]
    for x1, y1, x2, y2, color in geometry["lines"]:
        parts.append(
            f'<line x1="{x1:g}" y1="{y1:g}" x2="{x2:g}" y2="{y2:g}" stroke="{color}" stroke-width="1" />'
        )
    for x, y, width, height, color in geometry["rects"]:
        parts.append(
            f'<rect x="{x:g}" y="{y:g}" width="{width:g}" height="{height:g}" fill="{color}" />'
        )
    if geometry["points"]:
        coords = " ".join(f"{x:g},{y:g}" for x, y in geometry["points"])
        parts.append(
            f'<polyline points="{coords}" fill="none" stroke="{theme["accent"]}" stroke-width="4" />'
        )
        for x, y in geometry["points"]:
            parts.append(
                f'<circle cx="{x:g}" cy="{y:g}" r="5" fill="{theme["accent"]}" />'
            )
    for x, y, value, anchor, color, size in geometry["texts"]:
        parts.append(
            f'<text x="{x:g}" y="{y:g}" text-anchor="{anchor}" fill="{color}" font-size="{size}" font-family="{escape(theme["body"] + ", " + theme["cjk"])}">{escape(value)}</text>'
        )
    parts.append("</svg>")
    return "".join(parts)


def theme_css(theme):
    body = f'"{theme["body"]}", "{theme["cjk"]}", serif'
    display = f'"{theme["display"]}", "{theme["cjk"]}", serif'
    return (
        ":root {"
        + ";".join(
            [
                f"--paper:{theme['background']}",
                f"--ink:{theme['ink']}",
                f"--muted:{theme['muted']}",
                f"--accent:{theme['accent']}",
                f"--tint:{theme['tint']}",
                f"--rule:{theme['rule']}",
                f"--radius:{theme['radius']}px",
                f"--body-font:{body}",
                f"--display-font:{display}",
            ]
        )
        + "}"
    )


def render_html(report, output, source_dir):
    theme = load_asset("themes.json")[report["theme"]]
    recipe = load_asset("recipes.json")[report["recipe"]]

    def paragraphs(values):
        return "".join(f"<p>{escape(value)}</p>" for value in values)

    def notes(block):
        return "".join(
            f'<div class="{name}">{escape(block[key])}</div>'
            for key, name in [("caption", "caption"), ("source", "source-note")]
            if block.get(key)
        )

    def heading(block):
        return f"<h3>{escape(block['title'])}</h3>" if block.get("title") else ""

    def metric(item):
        unit = (
            f'<span class="number-unit"> {escape(item["unit"])}</span>'
            if item.get("unit")
            else ""
        )
        context = "".join(
            f'<div class="metric-context">{escape(item[key])}</div>'
            for key in ["period", "note"]
            if item.get(key)
        )
        delta = (
            f'<div class="delta">{escape(item["delta"])}</div>'
            if item.get("delta")
            else ""
        )
        return f'<span class="number">{escape(item["value"])}{unit}</span><div class="metric-label">{escape(item["label"])}</div>{delta}{context}{notes(item)}'

    def image_figure(block):
        image = bundle_image((source_dir / block["image"]).resolve(), output)
        return f'<figure><img src="{image}" alt="{escape(block["alt"])}" />{notes(block)}</figure>'

    def draw_chart(block, domain=None):
        unit = " · ".join(
            str(block[key]) for key in ["unit", "period"] if block.get(key)
        )
        label = f'<div class="chart-unit">{escape(unit)}</div>' if unit else ""
        return heading(block) + label + chart_svg(block, theme, domain) + notes(block)

    def draw_block(block):
        kind = block["type"]
        title = heading(block)
        if kind == "heading":
            level = block.get("level", 2)
            content = f"<h{level}>{escape(block['text'])}</h{level}>"
        elif kind == "standfirst":
            content = f'<p class="standfirst">{escape(block["text"])}</p>'
        elif kind == "change-indicator":
            content = f'<div class="change-value">{DIRECTIONS[block["direction"]]} {escape(block["value"])}</div><strong>{escape(block["label"])}</strong><p class="metric-context">{escape(block["comparison"])}</p>{notes(block)}'
        elif kind in {"target-comparison", "progress"}:
            content = (
                title
                + f"<strong>{escape(block['label'])}</strong>"
                + draw_chart({**block, "title": None})
            )
        elif kind == "metric-sparkline":
            content = metric(block) + chart_svg(block, theme)
        elif kind == "prose":
            content = title + paragraphs(block["paragraphs"])
        elif kind == "big-number":
            content = metric(block)
        elif kind == "metric-strip":
            content = "".join(f"<div>{metric(item)}</div>" for item in block["items"])
        elif kind in {"callout", "source-note"}:
            content = title + paragraphs([block["text"]]) + notes(block)
        elif kind in {"takeaways", "numbered-list"}:
            tag = "ol" if kind == "numbered-list" else "ul"
            content = (
                title
                + f"<{tag}>"
                + "".join(f"<li>{escape(item)}</li>" for item in block["items"])
                + f"</{tag}>"
                + notes(block)
            )
        elif kind == "pull-quote":
            attribution = (
                f'<div class="attribution">{escape(block["attribution"])}</div>'
                if block.get("attribution")
                else ""
            )
            content = f'<blockquote class="quote">{escape(block["text"])}</blockquote>{attribution}{notes(block)}'
        elif kind == "figure":
            content = title + image_figure(block)
        elif kind == "image-text":
            content = f'<div class="image-text-inner">{image_figure(block)}<div>{title}{paragraphs(block["paragraphs"])}</div></div>'
        elif kind in {"bar-chart", "line-chart"} | GRAPHICS:
            content = draw_chart(block)
        elif kind == "small-multiples":
            domain = chart_domain(block)
            content = (
                title
                + '<div class="small-multiples">'
                + "".join(
                    f'<div class="chart">{draw_chart(panel, domain)}</div>'
                    for panel in block["charts"]
                )
                + "</div>"
                + notes(block)
            )
        elif kind in {"data-table", "comparison-table", "heatmap-table"}:
            headers = "".join(
                f'<th scope="col">{escape(value)}</th>' for value in block["headers"]
            )
            rows = "".join(
                "<tr>"
                + "".join(
                    f'<td class="{"numeric" if numeric_cell(block, index, value) else ""}"'
                    + (
                        f' style="background:{heat_color(block, index, value, theme)}"'
                        if kind == "heatmap-table"
                        else ""
                    )
                    + f">{escape(value)}</td>"
                    for index, value in enumerate(row)
                )
                + "</tr>"
                for row in block["rows"]
            )
            content = (
                title
                + f'<div class="table-scroll"><table><thead><tr>{headers}</tr></thead><tbody>{rows}</tbody></table></div>'
                + notes(block)
            )
            if kind == "heatmap-table":
                content += f'<p class="caption">{escape(block.get("scaleLabel", "Color scale"))}: {escape(block["domain"][0])} → {escape(block["domain"][1])}</p>'
        elif kind in {"timeline", "process-steps"}:
            content = (
                title
                + "<ol>"
                + "".join(
                    f"<li><strong>{escape(item['label'])}</strong><p>{escape(item['text'])}</p></li>"
                    for item in block["items"]
                )
                + "</ol>"
                + notes(block)
            )
        else:
            raise ValueError(f"Unknown component: {kind}")
        classes = ["block", kind]
        if kind in {"bar-chart", "line-chart"} | GRAPHICS:
            classes.append("chart")
        if block.get("span") == "all":
            classes.append("span-all")
        style = (
            f' style="--metric-count:{len(block["items"])}"'
            if kind == "metric-strip"
            else ""
        )
        return f'<div class="{" ".join(classes)}"{style}>{content}</div>'

    def section_html(section):
        layout = section.get("layout", recipe["defaultLayout"])
        title = (
            f'<h2 class="section-heading">{escape(section["title"])}</h2>'
            if section.get("title")
            else ""
        )
        blocks = section["blocks"]
        if layout == "sidebar":
            # Full-width blocks interrupt the pair, then resume it in source order.
            chunks, group = [], []

            def flush():
                if not group:
                    return
                main = "".join(
                    draw_block(b) for b in group if b.get("placement") != "aside"
                )
                aside = "".join(
                    draw_block(b) for b in group if b.get("placement") == "aside"
                )
                chunks.append(
                    f'<div class="sidebar-grid"><div>{main}</div><aside class="aside">{aside}</aside></div>'
                )
                group.clear()

            for block in blocks:
                if block.get("span") == "all":
                    flush()
                    chunks.append(draw_block(block))
                else:
                    group.append(block)
            flush()
            content = "".join(chunks)
        else:
            content = (
                f'<div class="content {layout}">'
                + "".join(draw_block(b) for b in blocks)
                + "</div>"
            )
        return f"<section>{title}{content}</section>"

    meta = (
        f'<div class="meta">{escape(report["meta"])}</div>'
        if report.get("meta")
        else ""
    )
    subtitle = (
        f'<p class="standfirst">{escape(report["subtitle"])}</p>'
        if report.get("subtitle")
        else ""
    )
    footer = (
        f'<footer class="footer">{escape(report["footer"])}</footer>'
        if report.get("footer")
        else ""
    )
    css = theme_css(theme) + (ASSETS / "layout.css").read_text(encoding="utf-8")
    content = "".join(section_html(section) for section in report["sections"])
    document = f'<!doctype html>\n<html lang="{escape(report["language"])}"><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" /><title>{escape(report["title"])}</title><style>{css}</style></head><body><main class="report"><header class="masthead">{meta}<h1>{escape(report["title"])}</h1>{subtitle}</header>{content}{footer}</main></body></html>\n'
    target = output / "index.html"
    target.write_text(document, encoding="utf-8")
    return target


def render_report(input_path, output, formats=("html",), office_dir=None):
    input_path, output = Path(input_path).resolve(), Path(output).resolve()
    report = json.loads(input_path.read_text(encoding="utf-8"))
    validate_report(report, input_path.parent)
    if not formats or set(formats) - {"html", "docx", "pdf"}:
        raise ValueError("Choose html, docx, or pdf")
    if set(formats) & {"docx", "pdf"}:
        import native

        office_dir = (
            Path(office_dir).resolve()
            if office_dir
            else Path(__file__).resolve().parents[2] / "office-files"
        )
        native.prepare(report, office_dir, formats)
    output.mkdir(parents=True, exist_ok=True)
    results = {}
    if "html" in formats:
        results["html"] = str(render_html(report, output, input_path.parent))
    if set(formats) & {"docx", "pdf"}:
        results.update(
            native.render_native(report, output, input_path.parent, office_dir, formats)
        )
    return results


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument(
        "--format", nargs="+", choices=["html", "docx", "pdf"], default=["html"]
    )
    parser.add_argument("--office-dir", type=Path)
    args = parser.parse_args()
    try:
        result = render_report(args.input, args.out, args.format, args.office_dir)
    except (ValueError, TypeError, OSError, ImportError) as error:
        parser.error(str(error))
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
