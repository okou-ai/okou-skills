#!/usr/bin/env python3
"""Render common document charts; see references/chart-spec.md.

For other types, use Matplotlib with chart_style.chart_theme and save_chart.
"""

import argparse
import json
import math
from pathlib import Path

from chart_style import chart_theme, plt, save_chart, text_width


STYLE_FIELDS = {"title", "font", "accent", "palette", "width_inches", "height_inches"}
AXIS_FIELDS = {"x_label", "y_label"}
TYPE_FIELDS = {
    "bar": {"categories", "x", "series", "orientation", "stacked"},
    "line": {"categories", "x", "series"},
    "scatter": {"series"},
    "pie": {"categories", "series"},
    "donut": {"categories", "series"},
    "histogram": {"series", "bins"},
    "waterfall": {"categories", "series", "totals"},
}


def numbers(values, where):
    if not isinstance(values, list) or not values or any(
        isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value)
        for value in values
    ):
        raise ValueError(f"{where} must be a nonempty array of finite numbers")
    return values


def categories(values):
    if not isinstance(values, list) or not values or any(not isinstance(value, str) for value in values):
        raise ValueError("categories must be a nonempty array of strings")
    return values


def validate(spec):
    if not isinstance(spec, dict):
        raise ValueError("Chart specification must be an object")
    kind = spec.get("type", "bar")
    if not isinstance(kind, str) or kind not in TYPE_FIELDS:
        raise ValueError(f"Unsupported chart type {kind!r}. Presets: {', '.join(TYPE_FIELDS)}. For other types use Matplotlib with chart_style; see references/document-charts.md.")
    allowed = {"type"} | STYLE_FIELDS | TYPE_FIELDS[kind]
    if kind not in ("pie", "donut"):
        allowed |= AXIS_FIELDS
    unknown = set(spec) - allowed
    if unknown:
        raise ValueError(f"Fields not supported for {kind}: {', '.join(sorted(unknown))}")
    for field in ("title", "x_label", "y_label", "font"):
        if field in spec and not isinstance(spec[field], str):
            raise ValueError(f"{field} must be a string")
    series = spec.get("series")
    if not isinstance(series, list) or not series:
        raise ValueError("Supply a nonempty series array")
    expected = {"name", "x", "y"} if kind == "scatter" else {"name", "values"}
    for item in series:
        if not isinstance(item, dict) or set(item) != expected or not isinstance(item.get("name"), str) or not item["name"].strip():
            raise ValueError(f"Each {kind} series needs exactly {', '.join(sorted(expected))}, with a nonempty name")
        if kind == "scatter":
            if len(numbers(item["x"], "series.x")) != len(numbers(item["y"], "series.y")):
                raise ValueError("Each scatter series needs one y value per x value")
        else:
            numbers(item["values"], "series.values")

    positions = None
    if kind in ("bar", "line"):
        if ("categories" in spec) == ("x" in spec):
            raise ValueError("Supply exactly one of categories or numeric x")
        if "categories" in spec:
            positions = list(range(len(categories(spec["categories"]))))
        else:
            positions = numbers(spec["x"], "x")
            if any(a >= b for a, b in zip(positions, positions[1:])):
                raise ValueError("Numeric x values must be distinct and ascending; use scatter for unordered observations")
    elif kind in ("pie", "donut", "waterfall"):
        positions = list(range(len(categories(spec.get("categories")))))
        if len(series) != 1:
            raise ValueError(f"{kind} takes exactly one series")
    if positions is not None and any(len(item["values"]) != len(positions) for item in series):
        raise ValueError("Every series must have one value per category/x coordinate")

    if kind == "bar":
        if spec.get("orientation", "vertical") not in ("vertical", "horizontal"):
            raise ValueError("orientation must be vertical or horizontal")
        if not isinstance(spec.get("stacked", False), bool):
            raise ValueError("stacked must be a boolean")
        if spec.get("stacked", False):
            for values in zip(*(item["values"] for item in series)):
                if not all(math.isfinite(sum(value for value in values if (value >= 0) == sign)) for sign in (True, False)):
                    raise ValueError("Stacked totals must be finite")
    elif kind in ("pie", "donut"):
        values = series[0]["values"]
        if any(value < 0 for value in values) or not math.isfinite(sum(values)) or sum(values) <= 0:
            raise ValueError("Pie/donut values must be nonnegative with a finite positive total")
    elif kind == "histogram":
        bins = spec.get("bins", 10)
        if isinstance(bins, bool) or not isinstance(bins, (int, list)):
            raise ValueError("bins must be a positive integer or increasing numeric edges")
        if isinstance(bins, int):
            if bins < 1:
                raise ValueError("bins must be positive")
        else:
            numbers(bins, "bins")
            if len(bins) < 2 or any(a >= b for a, b in zip(bins, bins[1:])):
                raise ValueError("Histogram edges must be strictly increasing")
            if any(value < bins[0] or value > bins[-1] for item in series for value in item["values"]):
                raise ValueError("Histogram edges must cover all supplied samples; filter intentionally in the source first")
    elif kind == "waterfall":
        totals = spec.get("totals", [])
        if not isinstance(totals, list) or any(isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < len(positions) for index in totals) or len(set(totals)) != len(totals):
            raise ValueError("totals must contain distinct zero-based category indices")
        running = 0
        for index, value in enumerate(series[0]["values"]):
            if index in totals:
                if index and not math.isclose(value, running, rel_tol=1e-9, abs_tol=1e-9):
                    raise ValueError(f"Waterfall total at index {index} is {value}, but preceding values accumulate to {running}")
                running = value
            else:
                running += value
            if not math.isfinite(running):
                raise ValueError("Waterfall accumulated levels must be finite")
    return kind, positions


def _legend(fig, handles, labels, title=None):
    columns = min(len(labels), max(1, int(60 / max(8, max(text_width(label) for label in labels)))))
    legend = fig.legend(handles, labels, title=title, loc="outside lower center", ncols=columns)
    for label in [*legend.get_texts(), legend.get_title()]:
        label.set_parse_math(False)


def _bars(ax, spec, positions):
    horizontal = spec.get("orientation") == "horizontal"
    stacked = spec.get("stacked", False)
    gap = min((b - a for a, b in zip(positions, positions[1:])), default=1)
    size = 0.8 * gap / (1 if stacked else len(spec["series"]))
    positive, negative = [0] * len(positions), [0] * len(positions)
    for index, item in enumerate(spec["series"]):
        offsets = positions if stacked else [x + (index - (len(spec["series"]) - 1) / 2) * size for x in positions]
        bases = [positive[i] if value >= 0 else negative[i] for i, value in enumerate(item["values"])] if stacked else [0] * len(positions)
        if horizontal:
            ax.barh(offsets, item["values"], height=size, left=bases, label=item["name"])
        else:
            ax.bar(offsets, item["values"], width=size, bottom=bases, label=item["name"])
        if stacked:
            for i, value in enumerate(item["values"]):
                (positive if value >= 0 else negative)[i] += value
    if horizontal:
        ax.axvline(0, color="#7B8794", linewidth=0.7)
    else:
        ax.axhline(0, color="#7B8794", linewidth=0.7)


def _waterfall(ax, spec, colors):
    running = 0
    for index, value in enumerate(spec["series"][0]["values"]):
        if index:
            ax.plot([index - 0.65, index - 0.35], [running, running], color="#7B8794", linewidth=0.8)
        total = index in spec.get("totals", [])
        base = 0 if total else running
        color = colors[(2 if total else (0 if value >= 0 else 1)) % len(colors)]
        bars = ax.bar(index, value, bottom=base, width=0.7, color=color)
        ax.bar_label(bars, labels=[f"{value:g}" if total else f"{value:+g}"], padding=3)
        running = value if total else running + value
    ax.axhline(0, color="#7B8794", linewidth=0.7)
    # Bar sticky edges otherwise pin negative totals to the lower axis edge,
    # leaving their value labels on top of the category labels.
    ax.use_sticky_edges = False
    ax.margins(y=0.15)


def render(spec, output):
    kind, positions = validate(spec)
    appearance = {key: spec[key] for key in ("width_inches", "height_inches", "palette", "accent") if key in spec}
    with chart_theme(**appearance) as colors:
        fig, ax = plt.subplots()
        try:
            if kind == "bar":
                _bars(ax, spec, positions)
            elif kind == "line":
                for item in spec["series"]:
                    ax.plot(positions, item["values"], label=item["name"], linewidth=2.2, marker="o", markersize=4)
            elif kind == "scatter":
                for item in spec["series"]:
                    ax.scatter(item["x"], item["y"], label=item["name"], s=32, alpha=0.85)
            elif kind in ("pie", "donut"):
                values = spec["series"][0]["values"]
                total = sum(values)
                # Axes.pie casts to float32; normalize finite doubles first
                # so very large/small source units retain their proportions.
                shares = [value / total for value in values]
                wedges, _ = ax.pie(shares, startangle=90, colors=colors,
                                  wedgeprops={"width": 0.4} if kind == "donut" else None)
                labels = [f"{label} ({share:.1%})" for label, share in zip(spec["categories"], shares)]
                _legend(fig, wedges, labels, title=spec["series"][0]["name"])
                ax.set_aspect("equal")
            elif kind == "histogram":
                ax.hist([item["values"] for item in spec["series"]], bins=spec.get("bins", 10),
                        label=[item["name"] for item in spec["series"]], edgecolor="white", linewidth=0.5)
            else:
                _waterfall(ax, spec, colors)
            horizontal = kind == "bar" and spec.get("orientation") == "horizontal"
            if "categories" in spec and kind not in ("pie", "donut"):
                if horizontal:
                    ax.set_yticks(positions, spec["categories"], parse_math=False)
                    ax.invert_yaxis()
                else:
                    rotate = 30 if max(map(text_width, spec["categories"])) > 10 else 0
                    ax.set_xticks(positions, spec["categories"], rotation=rotate, ha="right" if rotate else "center", parse_math=False)
            if kind not in ("pie", "donut"):
                ax.set_xlabel(spec.get("x_label", ""), parse_math=False)
                ax.set_ylabel(spec.get("y_label", ""), parse_math=False)
                ax.grid(axis="x" if horizontal else "y")
                ax.ticklabel_format(axis="x" if horizontal else "y", style="plain", useOffset=False)
                handles, labels = ax.get_legend_handles_labels()
                if labels:
                    _legend(fig, handles, labels)
            if spec.get("title"):
                ax.set_title(spec["title"], wrap=True, parse_math=False)
            return save_chart(fig, output, font=spec.get("font"))
        finally:
            plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(render(json.loads(Path(args.spec).read_text(encoding="utf-8")), args.output), ensure_ascii=False))
    except (ValueError, OSError, TypeError, OverflowError) as error:
        parser.exit(1, f"render_chart: {error}\n")


if __name__ == "__main__":
    main()
