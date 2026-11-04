#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Explicit openpyxl primitives for NEW financial report layouts, not a model generator.

Call only after selecting the finance defaults; supplied styles take precedence.
Roles and ranges come from the author's plan, not guessed cell coordinates.
Requires the optional requirements-authoring.txt dependencies.
"""
from copy import copy

from openpyxl.styles import Alignment, Border, PatternFill, Side
from openpyxl.utils.cell import range_boundaries
from openpyxl.worksheet.page import PageMargins
from openpyxl.worksheet.properties import PageSetupProperties

ROLE_COLORS = {
    "input": "0000FF", "same_sheet": "000000", "cross_sheet": "008000",
    "external": "FF0000", "label": "404040", "source": "404040",
}
FORMULA_ROLES = {"same_sheet", "cross_sheet", "external"}
NUMBER_FORMATS = {
    "amount": '#,##0;(#,##0);"–"',
    "percent": "0.0%;(0.0%);0.0%",
    "integer": "0", "year": "0", "date": "yyyy-mm-dd", "text": "General",
}
BANDS = {"title": ("135B44", "FFFFFF", 26), "section": ("CFE9E0", "0B3D2C", 20)}


def _bounded_range(cell_range):
    bounds = range_boundaries(cell_range)
    if (None in bounds or not (1 <= bounds[0] <= bounds[2] <= 16384)
            or not (1 <= bounds[1] <= bounds[3] <= 1048576)):
        raise ValueError("Use a bounded, ordered Excel cell range")
    return bounds


def style_value(cell, *, role, kind):
    """Assign font role and number format together, retaining other font attributes.

    Populate the cell first. Explicit roles avoid treating retained source numbers
    as editable assumptions; resolve named-range dependencies before calling.
    """
    if role not in ROLE_COLORS or kind not in NUMBER_FORMATS:
        raise ValueError("Unknown financial cell role or number kind")
    if (cell.data_type == "f") != (role in FORMULA_ROLES):
        raise ValueError("Formula state does not match the supplied cell role")
    font = copy(cell.font)
    font.color = "FF" + ROLE_COLORS[role]
    cell.font = font
    cell.number_format = NUMBER_FORMATS[kind]
    return cell


def report_band(ws, cell_range, text, *, level="section"):
    """Create one planned, full-width title/section row without deleting data."""
    if level not in BANDS:
        raise ValueError("Band level must be title or section")
    left, top, right, bottom = _bounded_range(cell_range)
    if top != bottom:
        raise ValueError("A report band must span exactly one row")
    for merged in ws.merged_cells.ranges:
        ml, mt, mr, mb = merged.bounds
        if not (right < ml or left > mr or bottom < mt or top > mb):
            raise ValueError("Band would overlap an existing merged range")
    for row in ws.iter_rows(min_row=top, max_row=bottom, min_col=left, max_col=right):
        for cell in row:
            if cell.value is not None:
                raise ValueError("Band range must be empty; do not merge over existing content")
    fill, color, height = BANDS[level]
    if left != right:
        ws.merge_cells(cell_range)
    for row in ws.iter_rows(min_row=top, max_row=bottom, min_col=left, max_col=right):
        for cell in row:
            cell.fill = PatternFill("solid", fgColor="FF" + fill)
    anchor = ws.cell(top, left, text)
    font = copy(anchor.font)
    font.color, font.bold = "FF" + color, True
    font.sz = 16 if level == "title" else 11
    anchor.font = font
    anchor.alignment = Alignment(horizontal="left", vertical="center", wrap_text=False)
    ws.row_dimensions[top].height = height
    return anchor


def table_header(ws, cell_range):
    """Style literal column labels, not editable header inputs or formula outputs."""
    left, top, right, bottom = _bounded_range(cell_range)
    if top != bottom:
        raise ValueError("A column-header range must span exactly one row")
    cells = list(ws.iter_rows(min_row=top, max_row=top, min_col=left, max_col=right))[0]
    if any(cell.data_type == "f" for cell in cells):
        raise ValueError("Use style_value for formula outputs, including header formulas")
    for cell in cells:
        font = copy(cell.font)
        font.color, font.bold = "FF404040", True
        cell.font = font
        cell.fill = PatternFill("solid", fgColor="FFF2F2F2")
        cell.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True)
        cell.border = Border(bottom=Side(style="thin", color="FFD0D0D0"))
    ws.row_dimensions[top].height = 28


def report_page(ws, cell_range, *, orientation="landscape", paper_size=None):
    """Set a real report area one page wide, leaving height unrestricted.

    Set widths, explanation heights, page breaks and chart bounds separately,
    then inspect the actual export. These settings do not guarantee readability.
    """
    if orientation not in {"portrait", "landscape"}:
        raise ValueError("Invalid page orientation")
    _bounded_range(cell_range)
    ws.print_area = cell_range
    ws.sheet_view.showGridLines = False
    ws.page_setup.orientation = orientation
    if paper_size is not None:
        ws.page_setup.paperSize = paper_size
    ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
    if ws.sheet_properties.pageSetUpPr is None:
        ws.sheet_properties.pageSetUpPr = PageSetupProperties()
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_margins = PageMargins(left=.35, right=.35, top=.45, bottom=.45,
                                 header=.2, footer=.25)
