"""Shared contracts and drawing geometry for the Top 30 additions."""

import math

SERIES_CHARTS = {"grouped-bar-chart", "stacked-bar-chart", "percent-stacked-bar-chart"}
GRAPHICS = SERIES_CHARTS | {"target-comparison", "metric-sparkline", "progress"}
EXTRA_TYPES = GRAPHICS | {
    "heading",
    "standfirst",
    "change-indicator",
    "heatmap-table",
    "process-steps",
    "numbered-list",
}
DIRECTIONS = {"up": "↑", "down": "↓", "flat": "→"}


def finite(value):
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(value)
    )


def validate_extra(block):
    kind = block["type"]

    def text(key, obj=block):
        if not isinstance(obj.get(key), str) or not obj[key].strip():
            raise ValueError(f"{key} must be a nonempty string")

    def number(key, obj=block):
        if not finite(obj.get(key)):
            raise ValueError(f"{key} must be a finite number")

    def sequence(key, obj=block):
        if not isinstance(obj.get(key), list) or not obj[key]:
            raise ValueError(f"{key} must be a nonempty list")
        return obj[key]

    if kind in {"heading", "standfirst"}:
        text("text")
    if kind == "heading" and (
        type(block.get("level", 2)) is not int or block.get("level", 2) not in {2, 3, 4}
    ):
        raise ValueError("Heading level must be 2, 3, or 4")
    if kind in {
        "change-indicator",
        "metric-sparkline",
        "target-comparison",
        "progress",
    }:
        text("label")
    if kind == "change-indicator":
        text("value")
        text("comparison")
        if block.get("direction") not in DIRECTIONS:
            raise ValueError("Change direction must be supplied as up, down, or flat")
    if kind == "target-comparison":
        for key in ["actual", "target", "maximum"]:
            number(key)
        if (
            not 0 <= block["actual"] <= block["maximum"]
            or not 0 <= block["target"] <= block["maximum"]
            or block["maximum"] <= 0
        ):
            raise ValueError(
                "Target comparison requires nonnegative values within a positive maximum"
            )
    if kind == "progress":
        for key in ["value", "total"]:
            number(key)
        if block["total"] <= 0 or not 0 <= block["value"] <= block["total"]:
            raise ValueError("Progress requires a positive total and a value within it")
    if kind == "metric-sparkline":
        text("value")
        text("period")
        values = sequence("values")
        if len(values) < 2 or not all(finite(value) for value in values):
            raise ValueError("Sparkline requires at least two finite values")
    if kind in SERIES_CHARTS:
        labels, series = sequence("labels"), sequence("series")
        if not all(isinstance(label, str) for label in labels):
            raise ValueError("Chart labels must contain strings")
        names = []
        for item in series:
            if not isinstance(item, dict):
                raise ValueError("Chart series must be objects")
            text("name", item)
            values = sequence("values", item)
            if len(values) != len(labels) or not all(finite(value) for value in values):
                raise ValueError(
                    "Each series requires finite values matching the labels"
                )
            if kind != "grouped-bar-chart" and any(value < 0 for value in values):
                raise ValueError("Stacked charts require nonnegative values")
            names.append(item["name"])
        if len(set(names)) != len(names):
            raise ValueError("Series names must be distinct")
        if kind == "percent-stacked-bar-chart" and any(
            sum(item["values"][index] for item in series) == 0
            for index in range(len(labels))
        ):
            raise ValueError(
                "Percentage stacks require a positive total for every category"
            )
    if kind == "heatmap-table":
        domain = sequence("domain")
        if (
            len(domain) != 2
            or not all(finite(value) for value in domain)
            or domain[0] >= domain[1]
        ):
            raise ValueError("Heatmap domain must contain two increasing finite values")
        columns = sequence("heatColumns")
        for column in columns:
            if type(column) is not int or not 0 <= column < len(block["headers"]):
                raise ValueError("Heat column is outside the headers")
            if any(not finite(row[column]) for row in block["rows"]):
                raise ValueError("Heatmap cells must be finite numbers")
    if kind == "numbered-list":
        if not all(isinstance(item, str) for item in sequence("items")):
            raise ValueError("Numbered list items must be strings")
    if kind == "process-steps":
        for item in sequence("items"):
            if not isinstance(item, dict):
                raise ValueError("Process steps must be objects")
            text("label", item)
            text("text", item)


def blend(first, second, amount):
    channels = [
        round(
            int(first[i : i + 2], 16) * (1 - amount)
            + int(second[i : i + 2], 16) * amount
        )
        for i in (1, 3, 5)
    ]
    return "#" + "".join(f"{channel:02x}" for channel in channels)


def heat_color(block, column, value, theme):
    if column not in block["heatColumns"]:
        return theme["background"]
    low, high = block["domain"]
    strength = max(0, min(1, (value - low) / (high - low)))
    return blend(theme["background"], theme["accent"], strength * 0.36)


def extra_geometry(block, theme, wrap_label, font):
    """Visible values and series names accompany every graphical mark."""
    kind = block["type"]
    lines, rects, texts, points = [], [], [], []
    width, height = 640, 160

    def label(x, y, value, anchor="start", color=None):
        texts.append((x, y, str(value), anchor, color or theme["ink"], font))

    if kind == "metric-sparkline":
        values = block["values"]
        low, high = min(values), max(values)
        extent = high - low or 1
        points = [
            (20 + index / (len(values) - 1) * 600, 112 - (value - low) / extent * 76)
            for index, value in enumerate(values)
        ]
        label(20, 150, values[0])
        label(620, 150, values[-1], "end")
    elif kind in {"progress", "target-comparison"}:
        maximum = block["total"] if kind == "progress" else block["maximum"]
        value = block["value"] if kind == "progress" else block["actual"]
        rects.extend(
            [
                (10, 38, 620, 24, theme["tint"]),
                (10, 38, 620 * value / maximum, 24, theme["accent"]),
            ]
        )
        label(10, 106, f"{value:g} / {maximum:g}")
        if kind == "progress":
            label(630, 106, f"{value / maximum * 100:.1f}%", "end")
        else:
            target_x = 10 + 620 * block["target"] / maximum
            lines.append((target_x, 25, target_x, 78, theme["ink"]))
            label(
                630,
                106,
                f"{block.get('targetLabel', 'Target')} {block['target']:g}",
                "end",
            )
    else:
        series = block["series"]
        colors = [
            blend(theme["background"], theme["accent"], 0.3 + 0.6 * (index % 5) / 4)
            for index in range(len(series))
        ]
        all_values = [value for item in series for value in item["values"]]
        if kind == "grouped-bar-chart":
            low, high = min(0, min(all_values)), max(0, max(all_values))
        else:
            low, high = (
                0,
                100
                if kind == "percent-stacked-bar-chart"
                else max(
                    sum(item["values"][index] for item in series)
                    for index in range(len(block["labels"]))
                ),
            )
        high = high if high > low else low + 1
        start, end = 240, 530

        def scale(value):
            return start + (value - low) / (high - low) * (end - start)

        zero, y = scale(0), 32
        for index, category in enumerate(block["labels"]):
            if kind == "grouped-bar-chart":
                for number, item in enumerate(series):
                    wrapped = wrap_label(f"{category} / {item['name']}", 214, font)
                    row_height = max(48, len(wrapped) * (font + 4) + 12)
                    center = y + row_height / 2
                    value = item["values"][index]
                    endpoint = scale(value)
                    rects.append(
                        (
                            min(zero, endpoint),
                            center - 10,
                            abs(endpoint - zero),
                            20,
                            colors[number],
                        )
                    )
                    for offset, text in enumerate(wrapped):
                        label(
                            0,
                            center
                            - (len(wrapped) - 1) * (font + 4) / 2
                            + offset * (font + 4)
                            + font * 0.32,
                            text,
                        )
                    label(638, center + font * 0.32, value, "end")
                    y += row_height
                y += 22
            else:
                wrapped = wrap_label(category, 214, font)
                row_height = max(48, len(wrapped) * (font + 4) + 12)
                total = sum(item["values"][index] for item in series)
                cursor = start
                for number, item in enumerate(series):
                    raw = item["values"][index]
                    value = (
                        raw / total * 100
                        if kind == "percent-stacked-bar-chart"
                        else raw
                    )
                    size = (value / (high - low)) * (end - start)
                    rects.append(
                        (cursor, y + row_height / 2 - 12, size, 24, colors[number])
                    )
                    cursor += size
                for offset, text in enumerate(wrapped):
                    label(0, y + font + offset * (font + 4), text)
                label(
                    638,
                    y + row_height / 2 + font * 0.32,
                    "100%" if kind == "percent-stacked-bar-chart" else total,
                    "end",
                )
                y += row_height + 8
                for number, item in enumerate(series):
                    raw = item["values"][index]
                    value = (
                        f"{raw:g} ({raw / total * 100:.1f}%)"
                        if kind == "percent-stacked-bar-chart"
                        else f"{raw:g}"
                    )
                    wrapped = wrap_label(
                        f"{number + 1}. {item['name']}: {value}", 610, font
                    )
                    rects.append((0, y - font * 0.7, 8, 8, colors[number]))
                    for text in wrapped:
                        label(16, y, text)
                        y += font + 4
                y += 26
        height = max(160, y + 54)
        lines.append((zero, 15, zero, height - 45, theme["rule"]))
        label(start, height - 8, format(low, ".5g"))
        label(
            end,
            height - 8,
            format(high, ".5g") + ("%" if kind == "percent-stacked-bar-chart" else ""),
            "end",
        )
    return {
        "width": width,
        "height": height,
        "lines": lines,
        "rects": rects,
        "texts": texts,
        "points": points,
    }
