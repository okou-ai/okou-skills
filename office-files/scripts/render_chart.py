#!/usr/bin/env python3
"""Render a bar/line chart from JSON to PNG; see assets/chart.json."""

import argparse
import json
import math
from pathlib import Path
import re
import subprocess
import unicodedata

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.font_manager import FontProperties
    from matplotlib.ft2font import FT2Font
except ImportError:
    raise SystemExit("Install optional chart support: python3 -m pip install matplotlib==3.10.8")


def select_font(requested, text):
    required = {ord(c) for c in text if not c.isspace()}
    if requested and Path(requested).is_file():
        candidates = [str(Path(requested).resolve())]
    else:
        try:
            if requested:
                listing = subprocess.run(["fc-list", "--format=%{family}\t%{file}\n"], check=True, text=True, capture_output=True).stdout
                candidates = [line.split("\t", 1)[1] for line in listing.splitlines() if "\t" in line and requested.casefold() in [name.strip().casefold() for name in line.split("\t", 1)[0].split(",")]]
            else:
                candidates = subprocess.run(["fc-match", "--sort", "--format=%{file}\n", "sans-serif:lang=zh"], check=True, text=True, capture_output=True).stdout.splitlines()
        except (OSError, subprocess.CalledProcessError) as error:
            raise ValueError("Font discovery needs fontconfig; alternatively set font to an installed font file path.") from error
    for candidate in dict.fromkeys(candidates):
        try:
            if required <= set(FT2Font(candidate).get_charmap()):
                return FontProperties(fname=candidate), candidate
        except (OSError, RuntimeError):
            continue
    raise ValueError("No selected installed font covers all chart text. Set font to a covering font file path or installed family; no fonts were downloaded.")


def numbers(values, where):
    if not isinstance(values, list) or not values or any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v) for v in values):
        raise ValueError(f"{where} must be a nonempty array of finite numbers")
    return values


def width(text):
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in text)


def render(spec, output):
    allowed = {"type", "title", "categories", "x", "x_label", "y_label", "series", "font", "accent", "palette", "width_inches", "height_inches"}
    if not isinstance(spec, dict) or set(spec) - allowed:
        raise ValueError(f"Chart fields: {', '.join(sorted(allowed))}")
    kind = spec.get("type", "bar")
    if kind not in ("bar", "line") or not isinstance(spec.get("series"), list) or not spec["series"]:
        raise ValueError("Use type bar or line and a nonempty series array")
    if ("categories" in spec) == ("x" in spec):
        raise ValueError("Supply exactly one of categories or x")
    categories = spec.get("categories")
    if "categories" in spec and (not isinstance(categories, list) or not categories or any(not isinstance(v, str) for v in categories)):
        raise ValueError("categories must be a nonempty array of strings")
    x = list(range(len(categories))) if categories is not None else numbers(spec["x"], "x")
    if len(x) != len(set(x)) or categories is None and any(a >= b for a, b in zip(x, x[1:])):
        raise ValueError("Numeric x values must be distinct and ascending")
    labels = [spec.get(key, "") for key in ("title", "x_label", "y_label")]
    if any(not isinstance(v, str) for v in labels) or "font" in spec and not isinstance(spec["font"], str):
        raise ValueError("Titles, axis labels and font must be strings")
    # A report figure should fit the text column at its intrinsic size. Growing
    # the canvas with category count makes Pandoc shrink all labels when it fits
    # the image to the page. Authors can request a different physical size.
    dimensions = [spec.get("width_inches", 6.0), spec.get("height_inches", 3.6)]
    for key, value in zip(("width_inches", "height_inches"), dimensions):
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value) or not 1 <= value <= 30):
            raise ValueError(f"{key} must be a finite number from 1 to 30")
    for series in spec["series"]:
        if not isinstance(series, dict) or set(series) != {"name", "values"} or not isinstance(series["name"], str) or not series["name"].strip():
            raise ValueError("Each series needs a string name and a values array")
        if len(numbers(series["values"], "series.values")) != len(x):
            raise ValueError("Every series must have one value per category/x coordinate")
        labels.append(series["name"])
    palette = spec.get("palette", [spec.get("accent", "245C7B"), "D19A45", "3C8D7B", "94689A", "7B8794"])
    if not isinstance(palette, list) or not palette or any(not isinstance(c, str) or not re.fullmatch(r"#?[0-9a-fA-F]{6}", c) for c in palette):
        raise ValueError("palette/accent must contain RGB hex colors, with or without #")
    font, font_path = select_font(spec.get("font"), " ".join(labels + (categories or []) + ["0123456789.,-%"]))
    plt.rcParams.update({"text.parse_math": False, "axes.unicode_minus": False, "font.size": 11})
    fig, ax = plt.subplots(figsize=dimensions, layout="constrained")
    gap = min((b - a for a, b in zip(x, x[1:])), default=1)
    bar_width = 0.8 * gap / len(spec["series"])
    for i, series in enumerate(spec["series"]):
        hue = "#" + palette[i % len(palette)].lstrip("#")
        if kind == "bar":
            positions = [value + (i - (len(spec["series"]) - 1) / 2) * bar_width for value in x]
            ax.bar(positions, series["values"], width=bar_width, label=series["name"], color=hue)
        else:
            ax.plot(x, series["values"], label=series["name"], color=hue, linewidth=2.2, marker="o", markersize=4)
    if categories is not None:
        rotate = 30 if max(map(width, categories)) > 10 else 0
        ax.set_xticks(x, categories, rotation=rotate, ha="right" if rotate else "center")
    if labels[0]:
        ax.set_title(labels[0], fontproperties=font, fontsize=15, pad=14, wrap=True)
    ax.set_xlabel(labels[1], fontproperties=font, labelpad=8)
    ax.set_ylabel(labels[2], fontproperties=font, labelpad=8)
    ax.ticklabel_format(axis="y", style="plain", useOffset=False)
    ax.set_axisbelow(True)
    ax.grid(axis="y", color="#E3E8ED", linewidth=0.8)
    ax.spines[["top", "right"]].set_visible(False)
    for side in ("bottom", "left"):
        ax.spines[side].set_color("#AAB5C0")
    for tick in ax.get_xticklabels() + ax.get_yticklabels():
        tick.set_fontproperties(font)
        tick.set_fontsize(10)
    columns = min(len(spec["series"]), max(1, int(60 / max(8, max(width(s["name"]) for s in spec["series"])))))
    fig.legend(loc="outside lower center", ncols=columns, frameon=False, prop=font)
    destination = Path(output).resolve()
    if destination.suffix.lower() != ".png":
        raise ValueError("Output must have the .png extension")
    destination.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(destination, dpi=180, facecolor="white")
    plt.close(fig)
    return {"status": "RENDERED_NEEDS_VISUAL_REVIEW", "output": str(destination), "font": font_path}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(render(json.loads(Path(args.spec).read_text(encoding="utf-8")), args.output), ensure_ascii=False))
    except (ValueError, OSError, TypeError) as error:
        parser.exit(1, f"render_chart: {error}\n")


if __name__ == "__main__":
    main()
