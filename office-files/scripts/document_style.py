"""General document typography for the default (unbranded) DOCX route.

These functions are deliberately opt-in: the renderer must never call them on a
user's existing document or supplied reference document. Content stays in Pandoc;
this module changes styles and page-layout properties, never paragraph text.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from io import BytesIO
import json
import math
from pathlib import Path
import re
import subprocess
import unicodedata

from docx import Document
from docx.document import Document as DocumentObject
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Mm, Pt, RGBColor
from docx.table import Table, _Cell
from docx.text.paragraph import Paragraph
from docx.text.run import Run


TABLE_TEXT_STYLE = "Okou Table Text"
TABLE_HEADER_STYLE = "Okou Table Header"
METRIC_VALUE_STYLE = "Metric Value"
METRIC_LABEL_STYLE = "Metric Label"
METRIC_GRID_STYLE_ID = "MetricGrid"

# Editorial-paper palette. It is deliberately restrained: one ink-blue accent,
# warm neutrals, and no decorative gradients or hard shadows. These defaults
# are used only for new, untemplated prose.
INK = "1B365D"
PAPER = "F5F4ED"
IVORY = "FAF9F5"
WARM_SAND = "E8E6DC"
BORDER_SOFT = "E5E3D8"
NEAR_BLACK = "141413"
DARK_WARM = "3D3D3A"
OLIVE = "504E49"
STONE = "6B6A64"


@dataclass(frozen=True)
class _Theme:
    body_font: str = "Noto Sans"
    east_asia_font: str | None = None
    heading_font: str = "Noto Serif"
    body_size_pt: float = 10.5
    accent: str = INK
    page_size: str = "A4"
    margins_mm: tuple[float, float, float, float] = (20, 22, 22, 22)

    @property
    def scale(self) -> float:
        return self.body_size_pt / 10.5

    @property
    def page_mm(self) -> tuple[float, float]:
        return (210, 297) if self.page_size == "A4" else (215.9, 279.4)


def _validate_style(value) -> dict:
    """Validate the small, optional house-theme JSON schema without coercion."""
    if not isinstance(value, dict):
        raise ValueError("Style must be a JSON object.")
    allowed = {"body_font", "east_asia_font", "heading_font", "body_size_pt",
               "accent", "page_size", "margins_mm"}
    unknown = set(value) - allowed
    if unknown:
        raise ValueError(f"Unknown style field(s): {', '.join(sorted(unknown))}.")
    result = {}
    for name in ("body_font", "east_asia_font", "heading_font"):
        if name not in value:
            continue
        font = value[name]
        if (not isinstance(font, str) or not font.strip() or len(font) > 120
                or any(unicodedata.category(char).startswith("C") for char in font)):
            raise ValueError(f"{name} must be a nonempty font-family name.")
        result[name] = font.strip()
    if "body_size_pt" in value:
        size = value["body_size_pt"]
        if (isinstance(size, bool) or not isinstance(size, (int, float))
                or not math.isfinite(size) or not 8 <= size <= 18):
            raise ValueError("body_size_pt must be a number from 8 to 18.")
        result["body_size_pt"] = float(size)
    if "accent" in value:
        accent = value["accent"]
        if not isinstance(accent, str) or not re.fullmatch(r"#?[0-9A-Fa-f]{6}", accent):
            raise ValueError("accent must be a six-digit RGB hex colour, optionally prefixed with #.")
        result["accent"] = accent.removeprefix("#").upper()
    if "page_size" in value:
        if value["page_size"] not in ("A4", "Letter"):
            raise ValueError("page_size must be A4 or Letter.")
        result["page_size"] = value["page_size"]
    if "margins_mm" in value:
        margins = value["margins_mm"]
        if not isinstance(margins, dict) or set(margins) - {"top", "right", "bottom", "left"}:
            raise ValueError("margins_mm must be an object with only top, right, bottom and left.")
        for side, margin in margins.items():
            if (isinstance(margin, bool) or not isinstance(margin, (int, float))
                    or not math.isfinite(margin) or not 0 <= margin <= 70):
                raise ValueError(f"margins_mm.{side} must be a number from 0 to 70.")
        result["margins_mm"] = {side: float(margin) for side, margin in margins.items()}
    return result


def load_style(path: Path) -> dict:
    """Read optional house-theme overrides, rejecting unknown/duplicate keys.

    Supported keys: body_font, east_asia_font, heading_font, body_size_pt (8–18),
    accent (RGB hex), page_size (A4 or Letter), and margins_mm (any of top, right,
    bottom, left, in 0–70 mm). Unspecified values retain the house defaults.
    """
    def unique_keys(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate style field: {key}.")
            result[key] = value
        return result

    with Path(path).open(encoding="utf-8") as stream:
        return _validate_style(json.load(stream, object_pairs_hook=unique_keys))


def _theme(style: dict | None) -> _Theme:
    overrides = _validate_style(style) if style is not None else {}
    margins = dict(zip(("top", "right", "bottom", "left"), _Theme().margins_mm))
    margins.update(overrides.pop("margins_mm", {}))
    return _Theme(**overrides, margins_mm=tuple(margins.values()))

# python-docx supplies setters for most properties. These schema orders cover
# the few properties it does not expose, including bidi, language and row flags.
_PPR_ORDER = (
    "pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr",
    "widowControl", "numPr", "suppressLineNumbers", "pBdr", "shd", "tabs",
    "suppressAutoHyphens", "kinsoku", "wordWrap", "overflowPunct",
    "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd",
    "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents",
    "suppressOverlap", "jc", "textDirection", "textAlignment",
    "textboxTightWrap", "outlineLvl", "divId", "cnfStyle", "rPr", "sectPr",
    "pPrChange",
)
_RPR_ORDER = (
    "rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps",
    "strike", "dstrike", "outline", "shadow", "emboss", "imprint", "noProof",
    "snapToGrid", "vanish", "webHidden", "color", "spacing", "w", "kern",
    "position", "sz", "szCs", "highlight", "u", "effect", "bdr", "shd",
    "fitText", "vertAlign", "rtl", "cs", "em", "lang", "eastAsianLayout",
    "specVanish", "oMath", "rPrChange",
)
_TBLPR_ORDER = (
    "tblStyle", "tblpPr", "tblOverlap", "bidiVisual", "tblStyleRowBandSize",
    "tblStyleColBandSize", "tblW", "jc", "tblCellSpacing", "tblInd",
    "tblBorders", "shd", "tblLayout", "tblCellMar", "tblLook", "tblCaption",
    "tblDescription", "tblPrChange",
)
_TRPR_ORDER = (
    "cnfStyle", "divId", "gridBefore", "gridAfter", "wBefore", "wAfter",
    "cantSplit", "trHeight", "tblHeader", "tblCellSpacing", "jc", "hidden",
    "ins", "del", "trPrChange",
)
_TCPR_ORDER = (
    "cnfStyle", "tcW", "gridSpan", "hMerge", "vMerge", "tcBorders", "shd",
    "noWrap", "tcMar", "textDirection", "tcFitText", "vAlign", "hideMark",
    "headers", "cellIns", "cellDel", "cellMerge", "tcPrChange",
)


def _ordered_property(parent, name: str, order: tuple[str, ...]):
    """Get/create a property at its schema position, without rewriting XML."""
    tag = qn(f"w:{name}")
    existing = parent.find(tag)
    if existing is not None:
        return existing
    element = OxmlElement(f"w:{name}")
    successors = {qn(f"w:{item}") for item in order[order.index(name) + 1:]}
    for index, child in enumerate(parent):
        if child.tag in successors:
            parent.insert(index, element)
            break
    else:
        parent.append(element)
    return element


def _flag(parent, name: str, value: bool, order: tuple[str, ...]) -> None:
    _ordered_property(parent, name, order).set(qn("w:val"), "1" if value else "0")


def _paragraph_decoration(style, *, fill: str | None = None,
                          left_border: str | None = None,
                          bottom_border: str | None = None) -> None:
    """Apply print-safe paragraph decoration at the style level."""
    properties = style.element.get_or_add_pPr()
    if fill:
        shading = _ordered_property(properties, "shd", _PPR_ORDER)
        shading.set(qn("w:val"), "clear")
        shading.set(qn("w:fill"), fill)
    if left_border or bottom_border:
        borders = _ordered_property(properties, "pBdr", _PPR_ORDER)
        if left_border:
            border = _ordered_property(borders, "left", ("top", "left", "bottom", "right", "between", "bar"))
            border.set(qn("w:val"), "single")
            border.set(qn("w:sz"), "14")
            border.set(qn("w:space"), "8")
            border.set(qn("w:color"), left_border)
        if bottom_border:
            border = _ordered_property(borders, "bottom", ("top", "left", "bottom", "right", "between", "bar"))
            border.set(qn("w:val"), "single")
            border.set(qn("w:sz"), "4")
            border.set(qn("w:space"), "5")
            border.set(qn("w:color"), bottom_border)


@dataclass(frozen=True)
class _Language:
    tag: str
    east_asia: str
    east_asia_tag: str
    complex_font: str
    rtl: bool


def _language(lang: str) -> _Language:
    tag = (lang or "en").replace("_", "-")
    parts = tag.lower().split("-")
    base = parts[0]
    east_asia, east_asia_tag = "Noto Sans CJK SC", "zh-CN"
    if base == "ja":
        east_asia, east_asia_tag = "Noto Sans CJK JP", "ja-JP"
    elif base == "ko":
        east_asia, east_asia_tag = "Noto Sans CJK KR", "ko-KR"
    elif base == "zh" and ("hant" in parts or any(p in parts for p in ("tw", "hk", "mo"))):
        east_asia, east_asia_tag = "Noto Sans CJK TC", "zh-TW"
    arabic = "arab" in parts or base in {"ar", "fa", "ur", "ps", "sd", "ug"}
    hebrew = "hebr" in parts or base in {"he", "yi"}
    # An explicit script takes precedence (for example, az-Arab or sd-Deva).
    if "latn" in parts or "deva" in parts:
        arabic = hebrew = False
    scripts = {
        "hi": "Devanagari", "mr": "Devanagari", "ne": "Devanagari",
        "bn": "Bengali", "as": "Bengali", "gu": "Gujarati", "pa": "Gurmukhi",
        "ta": "Tamil", "te": "Telugu", "kn": "Kannada", "ml": "Malayalam",
        "th": "Thai", "lo": "Lao", "km": "Khmer", "my": "Myanmar",
        "si": "Sinhala",
    }
    script_overrides = {
        "deva": "Devanagari", "beng": "Bengali", "gujr": "Gujarati",
        "guru": "Gurmukhi", "taml": "Tamil", "telu": "Telugu",
        "knda": "Kannada", "mlym": "Malayalam", "thai": "Thai",
        "laoo": "Lao", "khmr": "Khmer", "mymr": "Myanmar", "sinh": "Sinhala",
    }
    script = next((script_overrides[p] for p in parts if p in script_overrides), scripts.get(base))
    complex_font = (
        "Noto Sans Arabic" if arabic else "Noto Sans Hebrew" if hebrew
        else f"Noto Sans {script}" if script else "Noto Sans"
    )
    return _Language(tag, east_asia, east_asia_tag, complex_font, arabic or hebrew)


def _font_properties(rpr, language: _Language, *, code: bool = False,
                     serif: bool = False, size: float | None = None,
                     theme: _Theme = _Theme()) -> None:
    fonts = _ordered_property(rpr, "rFonts", _RPR_ORDER)
    cjk_font = theme.east_asia_font or language.east_asia
    if code:
        latin, east_asia, complex_font = "Noto Sans Mono", cjk_font, language.complex_font
    elif serif:
        latin = theme.heading_font
        east_asia = theme.east_asia_font or language.east_asia.replace("Noto Sans CJK", "Noto Serif CJK")
        complex_font = ("Noto Naskh Arabic" if language.complex_font == "Noto Sans Arabic"
                        else language.complex_font.replace("Noto Sans", "Noto Serif"))
    else:
        latin, east_asia, complex_font = theme.body_font, cjk_font, language.complex_font
    fonts.set(qn("w:ascii"), latin)
    fonts.set(qn("w:hAnsi"), latin)
    fonts.set(qn("w:eastAsia"), east_asia)
    fonts.set(qn("w:cs"), complex_font)
    for theme in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme", "csTheme"):
        fonts.attrib.pop(qn(f"w:{theme}"), None)
    language_property = _ordered_property(rpr, "lang", _RPR_ORDER)
    # w:val selects the Latin text language; w:eastAsia selects CJK. Giving the
    # Latin slot zh/ja/ko makes LibreOffice apply character-level CJK breaking
    # inside ordinary English words (for example, "ch/ecklist").
    latin_language = "en-US" if language.tag.lower().split("-")[0] in {"zh", "ja", "ko"} else language.tag
    language_property.set(qn("w:val"), latin_language)
    language_property.set(qn("w:eastAsia"), language.east_asia_tag)
    language_property.set(qn("w:bidi"), language.tag)
    if size is not None:
        _ordered_property(rpr, "sz", _RPR_ORDER).set(qn("w:val"), str(round(size * 2)))
        _ordered_property(rpr, "szCs", _RPR_ORDER).set(qn("w:val"), str(round(size * 2)))
    _flag(rpr, "rtl", language.rtl and not code, _RPR_ORDER)


def _style(document, name: str, base: str = "Normal"):
    # python-docx maps built-in UI names (Caption -> caption) before membership
    # lookup, while Pandoc may retain the capitalized XML name. Compare exposed
    # names instead, otherwise add_style creates a duplicate style ID and Word /
    # LibreOffice can continue using the unmodified first definition.
    for existing in document.styles:
        if existing.name == name:
            return existing
    style = document.styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
    style.base_style = document.styles[base]
    return style


def _paragraph_style(document, name: str, language: _Language, *, size: float = 11,
                     before: float = 0, after: float = 6, spacing: float = 1.45,
                     bold: bool = False, color: str = DARK_WARM, keep_next: bool = False,
                     keep_lines: bool = False, code: bool = False, serif: bool = False,
                     theme: _Theme = _Theme()):
    size *= theme.scale
    style = _style(document, name)
    style.font.size = Pt(size)
    style.font.bold = bold
    style.font.cs_bold = bold
    style.font.color.rgb = RGBColor.from_string(color)
    _font_properties(style.element.get_or_add_rPr(), language, code=code, serif=serif,
                     size=size, theme=theme)
    fmt = style.paragraph_format
    fmt.space_before, fmt.space_after = Pt(before), Pt(after)
    fmt.line_spacing = spacing
    if language.rtl:
        # Arabic fonts have tall natural metrics. Multiplying those metrics by
        # the usual line-spacing factor produces excessive gaps. A minimum
        # physical line height preserves full glyphs/diacritics without doing
        # that multiplication (unlike an exact height, it cannot clip them).
        fmt.line_spacing = Pt(size * max(spacing, 1.5))
        fmt.line_spacing_rule = WD_LINE_SPACING.AT_LEAST
    fmt.keep_with_next = keep_next
    fmt.keep_together = keep_lines
    fmt.widow_control = True
    fmt.page_break_before = False
    fmt.first_line_indent = Pt(0)
    fmt.alignment = WD_ALIGN_PARAGRAPH.LEFT
    _flag(style.element.get_or_add_pPr(), "bidi", language.rtl and not code, _PPR_ORDER)
    # Prevent Latin words and numeric tokens being split character-by-character
    # in a CJK paragraph. This does not disable normal CJK line breaking.
    if not code:
        _flag(style.element.get_or_add_pPr(), "wordWrap", False, _PPR_ORDER)
    if language.rtl and not code:
        # Logical start is right for RTL text. python-docx's older alignment
        # enum omits start/end, so use the valid OOXML value explicitly.
        _ordered_property(style.element.get_or_add_pPr(), "jc", _PPR_ORDER).set(qn("w:val"), "start")
    return style


def _configure_styles(document: DocumentObject, language: _Language,
                      theme: _Theme = _Theme()) -> None:
    paragraph_style = partial(_paragraph_style, theme=theme)
    defaults = document.styles.element.find(qn("w:docDefaults"))
    if defaults is None:
        defaults = OxmlElement("w:docDefaults")
        document.styles.element.insert(0, defaults)
    run_defaults = defaults.find(qn("w:rPrDefault"))
    if run_defaults is None:
        run_defaults = OxmlElement("w:rPrDefault")
        defaults.insert(0, run_defaults)
    rpr = run_defaults.find(qn("w:rPr"))
    if rpr is None:
        rpr = OxmlElement("w:rPr")
        run_defaults.append(rpr)
    _font_properties(rpr, language, size=theme.body_size_pt, theme=theme)

    for name in ("Normal", "Body Text", "First Paragraph", "Abstract", "Definition", "Bibliography"):
        paragraph_style(document, name, language, size=10.5, after=7, spacing=1.5,
                         color=DARK_WARM)
    # Pandoc uses Compact for both lists and table text. Keep lists at body size;
    # only actual table paragraphs receive the separate styles during polishing.
    paragraph_style(document, "Compact", language, size=10.5, after=3, spacing=1.45)
    paragraph_style(document, "Keep with Next", language, size=10.5, after=7,
                     spacing=1.5, keep_next=True)
    paragraph_style(document, "Definition Term", language, size=10.5, after=3,
                     bold=True, keep_next=True)

    # Editorial hierarchy: serif carries display hierarchy while the sans body
    # stays neutral and robust across scripts. Size and spacing do more work than
    # repeated bold/color treatments.
    paragraph_style(document, "Title", language, size=30, before=36, after=8,
                     spacing=1.08, color=NEAR_BLACK, keep_next=True, keep_lines=True,
                     serif=True)
    paragraph_style(document, "Subtitle", language, size=15, after=13, spacing=1.3,
                     color=OLIVE, keep_next=True, serif=True)
    for name in ("Author", "Date"):
        paragraph_style(document, name, language, size=8.5, after=5, spacing=1.25,
                         color=STONE)
    for level, size in enumerate((20, 15, 12.5, 11.5, 10.5, 10.5, 10.5, 10.5, 10.5), 1):
        style = paragraph_style(document, f"Heading {level}", language, size=size,
                                 before=22 if level == 1 else 14, after=7, spacing=1.2,
                                 bold=False, color=theme.accent if level == 1 else NEAR_BLACK,
                                 keep_next=True, keep_lines=True, serif=True)
        if level == 1:
            _paragraph_decoration(style, bottom_border=WARM_SAND)
    paragraph_style(document, "Abstract Title", language, size=12.5, before=12,
                     color=NEAR_BLACK, keep_next=True, serif=True)
    paragraph_style(document, "TOC Heading", language, size=20, before=18, after=7,
                     color=theme.accent, keep_next=True, serif=True)
    for name in ("Caption", "Table Caption", "Image Caption"):
        caption = paragraph_style(document, name, language, size=9, before=5, after=7,
                                  spacing=1.35, color=OLIVE, keep_lines=True,
                                  keep_next=name == "Table Caption")
        # Pandoc's default Caption inherits italic. CJK faces generally have no
        # italic face, so that inheritance produces synthetic slanted glyphs.
        # Authors' explicit run-level emphasis remains intact.
        caption.font.italic = False
        caption.font.cs_italic = False
    for name in ("Footnote Text", "Footnote Block Text"):
        paragraph_style(document, name, language, size=8.5, after=4, spacing=1.3,
                         color=STONE)

    # Reusable composition components. Authors opt into only the components that
    # fit the content; these are not a mandatory report skeleton.
    eyebrow = paragraph_style(document, "Eyebrow", language, size=8.5, before=0,
                               after=7, spacing=1.15, bold=True, color=theme.accent,
                               keep_next=True)
    eyebrow.font.all_caps = True
    paragraph_style(document, "Deck", language, size=14, before=2, after=14,
                     spacing=1.45, color=OLIVE, keep_next=True, serif=True)
    takeaway = paragraph_style(document, "Key Takeaway", language, size=11.5,
                                before=8, after=13, spacing=1.45, color=DARK_WARM,
                                keep_lines=True, serif=True)
    takeaway.paragraph_format.left_indent = Pt(12)
    takeaway.paragraph_format.right_indent = Pt(12)
    _paragraph_decoration(takeaway, fill=IVORY, left_border=theme.accent)
    quote = paragraph_style(document, "Pull Quote", language, size=15, before=10,
                             after=12, spacing=1.5, color=theme.accent, keep_lines=True,
                             serif=True)
    quote.paragraph_format.left_indent = Pt(11)
    _paragraph_decoration(quote, left_border=theme.accent)
    paragraph_style(document, "Section Lead", language, size=12, before=0,
                     after=10, spacing=1.45, color=OLIVE, keep_next=True,
                     serif=True)
    paragraph_style(document, "Source Note", language, size=8.5, before=3,
                     after=8, spacing=1.3, color=STONE, keep_lines=True)
    paragraph_style(document, METRIC_VALUE_STYLE, language, size=20, before=2,
                     after=2, spacing=1.05, color=theme.accent, keep_next=True,
                     keep_lines=True, serif=True)
    paragraph_style(document, METRIC_LABEL_STYLE, language, size=8.5, before=0,
                     after=4, spacing=1.25, color=OLIVE, keep_lines=True)

    # python-docx assigns these built-in style IDs when it creates a header or
    # footer, but Pandoc's reference does not include their definitions.
    for name in ("Header", "Footer"):
        style = paragraph_style(document, name, language, size=8.5, after=0,
                                 spacing=1.2, color=STONE)
        # add_style normalizes their names to lowercase, while newly created
        # header/footer parts reference the capitalized built-in IDs.
        style.style_id = name
    paragraph_style(document, "Block Text", language, size=10.5, before=5,
                     after=8, spacing=1.45, color=OLIVE, serif=True)
    for name in ("Figure", "Captioned Figure"):
        style = paragraph_style(document, name, language, size=10.5, after=6,
                                 spacing=1.0, keep_next=name == "Captioned Figure",
                                 keep_lines=True)
        style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph_style(document, "Source Code", language, size=9, before=5, after=7,
                     spacing=1.25, code=True)
    code = document.styles["Verbatim Char"]
    _font_properties(code.element.get_or_add_rPr(), language, code=True, theme=theme)
    if "Hyperlink" in document.styles:
        document.styles["Hyperlink"].font.color.rgb = RGBColor.from_string(theme.accent)
    for name, bold in ((TABLE_TEXT_STYLE, False), (TABLE_HEADER_STYLE, True)):
        paragraph_style(document, name, language, size=9.5, before=0, after=3,
                         spacing=1.3, bold=bold, keep_next=bold,
                         color=DARK_WARM)
    # Pandoc uses a layout table for figures containing multiple blocks. Its
    # shipped reference omits this style, despite emitting the style reference.
    if "FigureTable" not in document.styles:
        figure_table = document.styles.add_style("FigureTable", WD_STYLE_TYPE.TABLE)
        figure_table.base_style = document.styles["Table"]
    if METRIC_GRID_STYLE_ID not in {style.style_id for style in document.styles}:
        metric_grid = document.styles.add_style("Metric Grid", WD_STYLE_TYPE.TABLE)
        metric_grid.base_style = document.styles["Table"]
        metric_grid.style_id = METRIC_GRID_STYLE_ID


def _set_page_background(document: DocumentObject, color: str) -> None:
    for existing in document._element.findall(qn("w:background")):
        document._element.remove(existing)
    background = OxmlElement("w:background")
    background.set(qn("w:color"), color)
    document._element.insert(0, background)
    settings = document.settings.element
    if settings.find(qn("w:displayBackgroundShape")) is None:
        settings.append(OxmlElement("w:displayBackgroundShape"))


def build_reference(pandoc_binary: str, output: Path, lang: str,
                    style: dict | None = None) -> None:
    """Write an unbranded reference DOCX containing Pandoc's complete styles."""
    result = subprocess.run(
        [str(pandoc_binary), "--print-default-data-file", "reference.docx"],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    document = Document(BytesIO(result.stdout))
    language = _language(lang)
    theme = _theme(style)
    _configure_styles(document, language, theme)
    _set_page_background(document, PAPER)
    page_width, page_height = theme.page_mm
    top, right, bottom, left = theme.margins_mm
    for section in document.sections:
        section.page_width, section.page_height = Mm(page_width), Mm(page_height)
        section.left_margin, section.right_margin = Mm(left), Mm(right)
        section.top_margin, section.bottom_margin = Mm(top), Mm(bottom)
        section.header_distance, section.footer_distance = Mm(min(10, top / 2)), Mm(min(11, bottom / 2))
        paragraph = section.footer.paragraphs[0]
        paragraph.clear()
        paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        paragraph.paragraph_format.space_before = Pt(0)
        paragraph.paragraph_format.space_after = Pt(0)
        paragraph.paragraph_format.keep_with_next = False
        field = OxmlElement("w:fldSimple")
        field.set(qn("w:instr"), "PAGE")
        run = OxmlElement("w:r")
        rpr = OxmlElement("w:rPr")
        _font_properties(rpr, language, size=9 * theme.scale, theme=theme)
        run.append(rpr)
        text = OxmlElement("w:t")
        text.text = "1"
        run.append(text)
        field.append(run)
        paragraph._p.append(field)
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    document.save(output)


def _display_width(text: str) -> float:
    """Approximate em width for layout hints; rendering remains the QA authority."""
    return sum(
        0 if unicodedata.combining(char) else
        1 if unicodedata.east_asian_width(char) in {"W", "F"} else
        .3 if char.isspace() else .58
        for char in text
    )


def _physical_cells(row, table):
    column = row.grid_cols_before
    for tc in row._tr.tc_lst:
        cell = _Cell(tc, table)
        span = tc.grid_span
        yield column, span, cell
        column += span


def _is_header(row) -> bool:
    trpr = row._tr.trPr
    header = trpr.find(qn("w:tblHeader")) if trpr is not None else None
    return header is not None and header.get(qn("w:val"), "1") not in {"0", "false", "off"}


def _has_explicit_widths(table: Table) -> bool:
    properties = table._tbl.tblPr
    width = properties.find(qn("w:tblW"))
    if width is not None and width.get(qn("w:type")) not in {None, "auto", "nil"}:
        return True
    if table.autofit is False:
        return True
    grid = [column.width for column in table.columns]
    return bool(grid) and len(set(grid)) > 1


def _minimum_cell_ems(text: str) -> float:
    """Protect short labels and ordinary tokens without making prose unwrappable."""
    minimum = 1.5
    for line in text.splitlines():
        width = _display_width(line)
        # A short CJK label should read horizontally. Longer prose may wrap,
        # but still needs several characters per line, not a one-glyph strip.
        minimum = max(minimum, width if width <= 6 else 4)
        latin = "".join(" " if unicodedata.east_asian_width(char) in {"W", "F"}
                        else char for char in line)
        for token in re.split(r"[\s/]+", latin):
            minimum = max(minimum, min(12, _display_width(token)))
        # Do not break ordinary amounts/percentages after a comma or decimal.
        # Numeric tokens retain their full minimum even in descriptive cells.
        for number in re.findall(r"[+\-−]?\d[\d,]*(?:\.\d+)?%?", line):
            minimum = max(minimum, _display_width(number))
    return minimum


def _size_default_columns(table: Table, usable_width: int, *, automatic: bool = False,
                          font_size: float = 9.5) -> None:
    count = len(table.columns)
    if not count or (not automatic and _has_explicit_widths(table)):
        return
    samples: list[list[float]] = [[] for _ in range(count)]
    headers = [0.0] * count
    minimum_ems = [1.5] * count
    for row in table.rows:
        for column, span, cell in _physical_cells(row, table):
            if span != 1 or column >= count:
                continue
            width = max((_display_width(line) for line in cell.text.splitlines()), default=0)
            minimum_ems[column] = max(minimum_ems[column], _minimum_cell_ems(cell.text))
            if _is_header(row):
                headers[column] = max(headers[column], width)
            else:
                samples[column].append(width)
    weights = []
    for header, values in zip(headers, samples):
        values.sort()
        typical = values[min(len(values) - 1, math.floor(len(values) * .8))] if values else 0
        # Sublinear growth makes room for numeric columns without allowing a
        # single verbose label or URL to consume almost the whole table.
        weights.append(max(1.5, min(40, max(header, typical))) ** .75)
    total = sum(weights)
    shares = [weight / total for weight in weights]
    if count > 1:
        maximum = .75 if count == 2 else .7
        largest = max(range(count), key=shares.__getitem__)
        if shares[largest] > maximum:
            others = 1 - shares[largest]
            shares = [maximum if index == largest else share * (1 - maximum) / others
                      for index, share in enumerate(shares)]
    # The old relative weights could give a three-character heading only one
    # character of actual room once Word subtracts the 5 pt side margins. Use
    # physical lower bounds, including those margins and a font-metric buffer,
    # then redistribute the remaining space with the existing content weights.
    minimums = [(ems * font_size * 1.1 + 10) * 12700 for ems in minimum_ems]
    if sum(minimums) >= usable_width:
        # An intrinsically overfull table must still fit the page; leave the
        # content/font intact for page review rather than silently shrinking it.
        widths = [round(usable_width * minimum / sum(minimums)) for minimum in minimums]
    else:
        assigned = {}
        pending = set(range(count))
        while pending:
            remaining = usable_width - sum(assigned.values())
            total_share = sum(shares[index] for index in pending)
            proposed = {index: remaining * shares[index] / total_share for index in pending}
            constrained = {index for index in pending if proposed[index] < minimums[index]}
            if not constrained:
                assigned.update(proposed)
                break
            assigned.update({index: minimums[index] for index in constrained})
            pending -= constrained
        widths = [round(assigned[index]) for index in range(count)]
    widths[-1] += usable_width - sum(widths)
    table.autofit = False
    table_width = _ordered_property(table._tbl.tblPr, "tblW", _TBLPR_ORDER)
    table_width.set(qn("w:type"), "dxa")
    table_width.set(qn("w:w"), str(round(usable_width / 635)))
    for column, width in zip(table.columns, widths):
        column.width = width
    for row in table.rows:
        for column, span, cell in _physical_cells(row, table):
            if column + span <= count:
                cell.width = sum(widths[column:column + span])


def _paragraph_height(paragraph: Paragraph, width_points: float, font_size: float = 10) -> float:
    width_ems = max(1, (width_points - 12) / font_size)
    lines = sum(max(1, math.ceil(_display_width(line) / width_ems))
                for line in paragraph.text.split("\n"))
    drawing_height = sum(int(extent.get("cy", "0")) / 12700
                         for extent in paragraph._p.xpath(".//wp:extent"))
    return lines * font_size * 1.3 + 3 + drawing_height


def _row_height(row, table: Table, fallback_width: int, font_size: float = 10) -> float:
    heights = []
    column_widths = [column.width for column in table.columns]
    for column, span, cell in _physical_cells(row, table):
        grid_width = sum(int(width or 0) for width in column_widths[column:column + span])
        width = int(cell.width or grid_width or fallback_width) / 12700
        height = sum(_paragraph_height(paragraph, width, font_size) for paragraph in cell.paragraphs) + 8
        # Nested tables may contain arbitrarily tall content. Let those rows
        # break, instead of locking a potentially multi-page cell to one page.
        if cell.tables:
            return math.inf
        heights.append(height)
    return max(heights, default=0)


def _paragraph_direction(paragraph: Paragraph, language: _Language) -> None:
    if not language.rtl:
        return
    code_paragraph = paragraph.style.name == "Source Code"
    _flag(paragraph._p.get_or_add_pPr(), "bidi", not code_paragraph, _PPR_ORDER)
    for element in paragraph._p.iter(qn("w:r")):
        run = Run(element, paragraph)
        code = code_paragraph or run.style.name in {"Verbatim Char", "Source Code"}
        strong = next((unicodedata.bidirectional(char) for char in run.text
                       if unicodedata.bidirectional(char) in {"R", "AL", "L"}), None)
        run.font.rtl = not code and strong in {"R", "AL"}
        run.font.complex_script = not code and strong in {"R", "AL"}


def _polish_metric_grid(table: Table, language: _Language, usable_width: int,
                        theme: _Theme = _Theme()) -> None:
    """Turn a semantic metric-grid table into an editorial KPI strip."""
    count = len(table.columns)
    if not count:
        return
    properties = table._tbl.tblPr
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    width = _ordered_property(properties, "tblW", _TBLPR_ORDER)
    width.set(qn("w:type"), "dxa")
    width.set(qn("w:w"), str(round(usable_width / 635)))
    column_widths = [usable_width // count] * count
    column_widths[-1] += usable_width - sum(column_widths)
    for column, column_width in zip(table.columns, column_widths):
        column.width = column_width
    margins = _ordered_property(properties, "tblCellMar", _TBLPR_ORDER)
    for side, value in (("top", 150), ("left", 140), ("bottom", 120), ("right", 140)):
        item = _ordered_property(margins, side, ("top", "left", "bottom", "right"))
        item.set(qn("w:type"), "dxa")
        item.set(qn("w:w"), str(value))
    borders = _ordered_property(properties, "tblBorders", _TBLPR_ORDER)
    order = ("top", "left", "bottom", "right", "insideH", "insideV")
    for side in order:
        border = _ordered_property(borders, side, order)
        border.set(qn("w:val"), "single" if side in {"top", "bottom", "insideV"} else "nil")
        border.set(qn("w:sz"), "5" if side in {"top", "bottom"} else "3")
        border.set(qn("w:color"), theme.accent if side in {"top", "bottom"} else BORDER_SOFT)
    for row_index, row in enumerate(table.rows):
        trpr = row._tr.get_or_add_trPr()
        _flag(trpr, "tblHeader", False, _TRPR_ORDER)
        _flag(trpr, "cantSplit", True, _TRPR_ORDER)
        for column, span, cell in _physical_cells(row, table):
            if column + span <= count:
                cell.width = sum(column_widths[column:column + span])
            shading = _ordered_property(cell._tc.get_or_add_tcPr(), "shd", _TCPR_ORDER)
            shading.set(qn("w:val"), "clear")
            shading.set(qn("w:fill"), IVORY)
            for paragraph in cell.paragraphs:
                paragraph.style = METRIC_VALUE_STYLE if row_index == 0 else METRIC_LABEL_STYLE
                paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                paragraph.paragraph_format.keep_with_next = row_index == 0
                paragraph.paragraph_format.keep_together = True
                _paragraph_direction(paragraph, language)


def _polish_table(table: Table, language: _Language, usable_width: int, usable_height: int,
                  *, automatic_table_widths: bool = False, theme: _Theme = _Theme()) -> None:
    # A FigureTable is a layout container, not a data grid. Keep its widths,
    # borderless appearance and paragraph styles, while pairing its content.
    style = table._tbl.tblPr.tblStyle
    if style is not None and style.val == METRIC_GRID_STYLE_ID:
        _polish_metric_grid(table, language, usable_width, theme)
        return
    if style is not None and style.val == "FigureTable":
        for row in table.rows:
            _flag(row._tr.get_or_add_trPr(), "cantSplit",
                  _row_height(row, table, usable_width) < usable_height / 12700 * .65, _TRPR_ORDER)
            for _, _, cell in _physical_cells(row, table):
                _polish_blocks(cell, language, int(cell.width or usable_width), usable_height,
                               automatic_table_widths=automatic_table_widths, theme=theme)
        return
    _size_default_columns(table, usable_width, automatic=automatic_table_widths,
                          font_size=9.5 * theme.scale)
    properties = table._tbl.tblPr
    margins = _ordered_property(properties, "tblCellMar", _TBLPR_ORDER)
    for side, width in (("top", 80), ("left", 100), ("bottom", 80), ("right", 100)):
        item = _ordered_property(margins, side, ("top", "left", "bottom", "right"))
        item.set(qn("w:type"), "dxa")
        item.set(qn("w:w"), str(width))
    borders = _ordered_property(properties, "tblBorders", _TBLPR_ORDER)
    border_order = ("top", "left", "bottom", "right", "insideH", "insideV")
    for side in border_order:
        border = _ordered_property(borders, side, border_order)
        border.set(qn("w:val"), "nil" if side in {"left", "right", "insideV"} else "single")
        border.set(qn("w:sz"), "4")
        border.set(qn("w:color"), BORDER_SOFT)
    if language.rtl:
        properties.get_or_add_bidiVisual().val = True
        table.alignment = WD_TABLE_ALIGNMENT.RIGHT
    for row_index, row in enumerate(table.rows):
        header = _is_header(row)
        trpr = row._tr.get_or_add_trPr()
        if header:
            _flag(trpr, "tblHeader", True, _TRPR_ORDER)
        _flag(trpr, "cantSplit", _row_height(row, table, usable_width, 9.5 * theme.scale)
              < usable_height / 12700 * .65,
              _TRPR_ORDER)
        for _, _, cell in _physical_cells(row, table):
            if header or row_index % 2 == 0:
                shading = _ordered_property(cell._tc.get_or_add_tcPr(), "shd", _TCPR_ORDER)
                shading.set(qn("w:val"), "clear")
                shading.set(qn("w:fill"), WARM_SAND if header else IVORY)
            for paragraph in cell.paragraphs:
                if paragraph.style.name in {"Compact", "Normal", "Body Text", "First Paragraph",
                                            TABLE_TEXT_STYLE, TABLE_HEADER_STYLE}:
                    paragraph.style = TABLE_HEADER_STYLE if header else TABLE_TEXT_STYLE
                paragraph.paragraph_format.widow_control = True
                if header:
                    paragraph.paragraph_format.keep_with_next = True
                _paragraph_direction(paragraph, language)
            for nested in cell.tables:
                _polish_table(nested, language, max(1, int(cell.width or usable_width) - int(Mm(4))),
                              usable_height, automatic_table_widths=automatic_table_widths, theme=theme)


def _has_drawing(paragraph: Paragraph) -> bool:
    return bool(paragraph._p.xpath(".//w:drawing | .//w:pict"))


def _is_caption(paragraph: Paragraph) -> bool:
    return paragraph.style.name in {"Caption", "Image Caption", "Table Caption"}


def _polish_blocks(document: DocumentObject, language: _Language, usable_width: int, usable_height: int,
                   *, automatic_table_widths: bool = False, theme: _Theme = _Theme()) -> None:
    blocks = list(document.iter_inner_content())
    for index, block in enumerate(blocks):
        if isinstance(block, Table):
            _polish_table(block, language, usable_width, usable_height,
                          automatic_table_widths=automatic_table_widths, theme=theme)
            continue
        paragraph = block
        if paragraph.paragraph_format.widow_control is None:
            paragraph.paragraph_format.widow_control = True
        _paragraph_direction(paragraph, language)
        following = blocks[index + 1] if index + 1 < len(blocks) else None
        if (language.rtl and paragraph.style.name == "Title" and isinstance(following, Paragraph)
                and following.style.name.startswith("Heading ")):
            paragraph.paragraph_format.space_after = Pt(6)
        if paragraph.style.name.startswith("Heading "):
            paragraph.paragraph_format.keep_with_next = True
            paragraph.paragraph_format.keep_together = True
            if (language.rtl and index > 0 and isinstance(blocks[index - 1], Paragraph)
                    and blocks[index - 1].style.name == "Title"):
                paragraph.paragraph_format.space_before = Pt(0)
        if _has_drawing(paragraph) and isinstance(following, Paragraph) and _is_caption(following):
            paragraph.paragraph_format.keep_with_next = True
            following.paragraph_format.keep_together = True
            following.paragraph_format.keep_with_next = False
        if paragraph.style.name in {"Caption", "Table Caption"} and isinstance(following, Table):
            paragraph.paragraph_format.keep_with_next = True
        if paragraph.style.name not in {"Normal", "Body Text", "First Paragraph"}:
            continue
        if not paragraph.text.strip() or paragraph._p.xpath("./w:pPr/w:numPr"):
            continue
        intro_height = _paragraph_height(paragraph, usable_width / 12700, theme.body_size_pt)
        if intro_height > 3 * theme.body_size_pt * 1.45:
            continue
        if isinstance(following, Table) and following.rows:
            component_height = _row_height(following.rows[0], following, usable_width, 9.5 * theme.scale)
            if _is_header(following.rows[0]) and len(following.rows) > 1:
                component_height += _row_height(following.rows[1], following, usable_width, 9.5 * theme.scale)
        elif isinstance(following, Paragraph) and _has_drawing(following):
            component_height = _paragraph_height(following, usable_width / 12700)
        else:
            continue
        if component_height + intro_height < usable_height / 12700 * .6:
            paragraph.paragraph_format.keep_with_next = True


def polish_document(path: Path, lang: str, *, automatic_table_widths: bool = False,
                    style: dict | None = None) -> None:
    """Polish a newly generated house DOCX; never pass a custom/user document.

    ``automatic_table_widths`` ignores Pandoc's delimiter-derived column sizes.
    Leave it false to retain intentionally authored widths. Pass the same style
    overrides used by ``build_reference`` to keep typography and layout aligned.
    """
    document = Document(path)
    language = _language(lang)
    theme = _theme(style)
    if style is not None:
        _configure_styles(document, language, theme)
    # Pandoc does not carry the document-level w:background element from a
    # reference document, so restore the default paper colour after conversion.
    _set_page_background(document, PAPER)
    # Pandoc can reapply document metadata to docDefaults after reading the
    # reference. Keep that fallback consistent with the script-specific styles.
    if language.tag.lower().split("-")[0] in {"zh", "ja", "ko"}:
        for setting in document.styles.element.xpath("./w:docDefaults/w:rPrDefault/w:rPr/w:lang"):
            setting.set(qn("w:val"), "en-US")
    # Build-reference normally supplies these styles. Keeping this idempotent
    # also supports callers that generated a fresh DOCX with Pandoc defaults.
    for name, bold in ((TABLE_TEXT_STYLE, False), (TABLE_HEADER_STYLE, True)):
        if name not in document.styles:
            _paragraph_style(document, name, language, size=9.5, after=3,
                             spacing=1.3, bold=bold, keep_next=bold,
                             color=DARK_WARM, theme=theme)
    for name, size, serif, color in (
        (METRIC_VALUE_STYLE, 20, True, theme.accent),
        (METRIC_LABEL_STYLE, 8.5, False, OLIVE),
    ):
        if name not in document.styles:
            _paragraph_style(document, name, language, size=size, after=3,
                             spacing=1.2, serif=serif, color=color,
                             keep_lines=True, theme=theme)
    section = document.sections[0]
    usable_width = int(section.page_width - section.left_margin - section.right_margin)
    usable_height = int(section.page_height - section.top_margin - section.bottom_margin)
    _polish_blocks(document, language, usable_width, usable_height,
                   automatic_table_widths=automatic_table_widths, theme=theme)
    document.save(path)
