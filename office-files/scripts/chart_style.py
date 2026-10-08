#!/usr/bin/env python3
"""Shared Matplotlib theme and PNG export for preset or custom document charts."""

from contextlib import contextmanager
from functools import lru_cache
from io import BytesIO
import math
from pathlib import Path
import re
import subprocess
import tempfile
import unicodedata
import warnings

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from cycler import cycler
    from matplotlib.font_manager import FontProperties, findfont
    from matplotlib.ft2font import FT2Font
    from matplotlib.text import Text
except ImportError:
    raise SystemExit("Install optional chart support: python3 -m pip install matplotlib==3.10.8")


DEFAULT_PALETTE = ("245C7B", "D19A45", "3C8D7B", "94689A", "7B8794")


@lru_cache(maxsize=32)
def _font_candidates(requested):
    if requested and Path(requested).is_file():
        return (str(Path(requested).resolve()),)
    try:
        if requested:
            listing = subprocess.run(
                ["fc-list", "--format=%{family}\t%{file}\n"],
                check=True, text=True, capture_output=True,
            ).stdout
            return tuple(dict.fromkeys(
                line.split("\t", 1)[1] for line in listing.splitlines()
                if "\t" in line and requested.casefold() in
                [name.strip().casefold() for name in line.split("\t", 1)[0].split(",")]
            ))
        listing = subprocess.run(
            ["fc-match", "--sort", "--format=%{file}\n", "sans-serif:lang=zh"],
            check=True, text=True, capture_output=True,
        ).stdout
        return tuple(dict.fromkeys(listing.splitlines()))
    except (OSError, subprocess.CalledProcessError) as error:
        raise ValueError("Font discovery needs fontconfig; alternatively pass an installed font file path.") from error


@lru_cache(maxsize=128)
def _font_characters(path):
    return frozenset(FT2Font(path).get_charmap())


def select_font(requested, text):
    if requested is not None and not isinstance(requested, str):
        raise ValueError("font must be an installed font family or file path")
    required = {ord(char) for char in text if not char.isspace()}
    for candidate in _font_candidates(requested):
        try:
            if required <= _font_characters(candidate):
                return FontProperties(fname=candidate), candidate
        except (OSError, RuntimeError):
            continue
    raise ValueError("No selected installed font covers all chart text. Choose a covering font family or file; no fonts were downloaded.")


def text_width(text):
    return sum(2 if unicodedata.east_asian_width(char) in "WF" else 1 for char in text)


def _dimension(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 1 <= value <= 30:
        raise ValueError(f"{name} must be a finite number from 1 to 30 inches")
    return value


@contextmanager
def chart_theme(*, width_inches=6.0, height_inches=3.6, palette=None, accent=None):
    """Set temporary defaults for any Matplotlib figure; yield resolved colors."""
    colors = list(DEFAULT_PALETTE) if palette is None else palette
    if palette is None and accent is not None:
        colors[0] = accent
    if not isinstance(colors, (list, tuple)) or not colors or any(
        not isinstance(color, str) or not re.fullmatch(r"#?[0-9a-fA-F]{6}", color)
        for color in colors
    ):
        raise ValueError("palette/accent must contain RGB hex colors, with or without #")
    if accent is not None and (not isinstance(accent, str) or not re.fullmatch(r"#?[0-9a-fA-F]{6}", accent)):
        raise ValueError("accent must be an RGB hex color")
    colors = tuple("#" + color.lstrip("#") for color in colors)
    size = (_dimension(width_inches, "width_inches"), _dimension(height_inches, "height_inches"))
    with matplotlib.rc_context({
        "figure.figsize": size, "figure.constrained_layout.use": True,
        "figure.facecolor": "white", "axes.facecolor": "white",
        "axes.prop_cycle": cycler(color=colors), "axes.axisbelow": True,
        "axes.spines.top": False, "axes.spines.right": False,
        "axes.edgecolor": "#AAB5C0", "axes.labelpad": 8,
        "axes.titlesize": 15, "axes.titlepad": 14,
        "axes.unicode_minus": False, "axes.formatter.useoffset": False,
        "grid.color": "#E3E8ED", "grid.linewidth": 0.8,
        "font.size": 11, "xtick.labelsize": 10, "ytick.labelsize": 10,
        "legend.frameon": False,
    }):
        yield colors


def _visible_text(fig):
    # Locators keep extra ticks outside the view; Axis.draw omits them even
    # though the Text artists report visible=True. Do not flag undrawn labels.
    excluded = set()
    for ax in fig.axes:
        if not ax.get_visible():
            excluded.update(ax.findobj(Text))
            continue
        for axis in (ax.xaxis, ax.yaxis):
            axis.get_ticklabels(minor=False)
            axis.get_ticklabels(minor=True)
            if not ax.axison or not axis.get_visible():
                excluded.update(axis.findobj(Text))
                continue
            transform = axis.get_transform()
            lower, upper = sorted(transform.transform(axis.get_view_interval()))
            tolerance = abs(upper - lower) * 1e-10
            for tick in axis.get_major_ticks() + axis.get_minor_ticks():
                location = transform.transform([tick.get_loc()])[0]
                if not lower - tolerance <= location <= upper + tolerance:
                    excluded.update((tick.label1, tick.label2))
    return [item for item in fig.findobj(Text)
            if item not in excluded and item.get_visible() and item.get_text().strip()]


def _apply_font(fig, requested):
    labels = _visible_text(fig)
    required_text = "0123456789.,-%" + " ".join(label.get_text() for label in labels)
    if any(label.get_parse_math() and "$" in label.get_text() for label in labels):
        # MathText replaces ASCII minus with U+2212, including log exponents.
        required_text += "−"
    _, path = select_font(requested, required_text)
    family = FT2Font(path).family_name
    required = {ord(char) for char in required_text if not char.isspace()}
    for label in labels:
        properties = label.get_fontproperties().copy()
        selected = path
        if not (requested and Path(requested).is_file()):
            # A fixed regular fname suppresses the caller's bold/italic face.
            # Resolve installed variants of the covering family when possible.
            variant = FontProperties(family=family, weight=properties.get_weight(),
                                     style=properties.get_style(), stretch=properties.get_stretch())
            try:
                candidate = findfont(variant, fallback_to_default=False)
                if required <= _font_characters(candidate):
                    selected = candidate
            except (ValueError, OSError, RuntimeError):
                # fontconfig can see a newly installed family before
                # Matplotlib's registry does; the covering file still works.
                pass
        properties.set_file(selected)
        label.set_fontproperties(properties)
    return path


def save_chart(fig, output, *, font=None):
    """Apply fonts to actual artists, check canvas bounds, save PNG, close fig.

    This leaves chart geometry and meaning to the caller. Bounds warnings are
    hints for visual review, not proof of legibility, accuracy or no overlap.
    """
    temporary = None
    try:
        destination = Path(output).resolve()
        if destination.suffix.lower() != ".png":
            raise ValueError("Output must have the .png extension")
        fig.set_dpi(180)
        with warnings.catch_warnings(record=True) as captured:
            warnings.simplefilter("always", UserWarning)
            font_path = _apply_font(fig, font)
            fig.canvas.draw()
            # Layout may create new ticks/offset labels. Include their text too.
            font_path = _apply_font(fig, font)
            fig.canvas.draw()
            canvas = fig.bbox
            renderer = fig.canvas.get_renderer()
            findings = []
            for label in _visible_text(fig):
                bbox = label.get_window_extent(renderer)
                if bbox.x0 < canvas.x0 - 1 or bbox.y0 < canvas.y0 - 1 or bbox.x1 > canvas.x1 + 1 or bbox.y1 > canvas.y1 + 1:
                    findings.append({"code": "text_outside_canvas", "text": label.get_text()})
            data = BytesIO()
            # A caller's savefig.bbox='tight' would silently change physical
            # size and bypass the canvas-bound checks used by documents.
            with matplotlib.rc_context({"savefig.bbox": None}):
                fig.savefig(data, format="png", dpi=180, facecolor=fig.get_facecolor())
        for message in dict.fromkeys(str(item.message) for item in captured):
            findings.append({"code": "matplotlib_warning", "message": message})
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(dir=destination.parent, suffix=".png", delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data.getvalue())
        temporary.replace(destination)
        return {
            "status": "RENDERED_NEEDS_VISUAL_REVIEW", "output": str(destination),
            "font": font_path, "dpi": 180,
            "width_inches": float(fig.get_figwidth()), "height_inches": float(fig.get_figheight()),
            "warnings": findings,
        }
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        plt.close(fig)
