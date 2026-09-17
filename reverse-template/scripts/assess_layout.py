#!/usr/bin/env python3
"""Let a source onto the docx or pdf branch only when every gate passes.

Those branches produce a `reference.docx`: a style sheet that pandoc pours one
stream of paragraphs into, in one column or in equal columns. The gates below
are the list of what that reproduces. Anything outside the list goes to the
source-style branch, which keeps the source file itself — a template that is
less editable, but that loses nothing.

The gates are a whitelist on purpose. A wrong `flow` is silent: the template
comes out looking plausible with the sidebar gone. A wrong `composed` only
costs editability.
"""

import argparse
import collections
import os
import re
import statistics
import sys
import zipfile

GRID_X, GRID_Y = 60, 84
CELLS = GRID_X * GRID_Y

BIN_PT = 2.0            # x and y resolution when looking for a gutter
CORRIDOR_PT = 8.0       # narrower than this is letter spacing, not a gutter
CORRIDOR_NOISE = 0.03   # a gutter may be crossed by a spanning title or figure
TALL_REGION = 0.5       # a region this much of the body height runs down the page
CHAR_SHARE = 0.08       # a column of right-aligned dates is a tab stop, not a
                        # region; it holds almost none of the page's text
WIDTH_RATIO = 1.25      # wider a gap than this and two regions are not columns
RUNNING_BAND = 0.12     # a running head or foot lives this far into the page
PAGE_ART = 0.25         # a fill or image this large is decoration, not a table
                        # row: nothing is beside it, so the test above lets it by
LONG_RULE = 0.4         # a vertical rule this much of the page height divides
                        # the page; a table's cell borders are far shorter
RULE_TO_TEXT = 12.0     # a rule this close to a line of text is its border
LATTICE_PT = 20.0       # a horizontal rule with a vertical one this close is
                        # part of a table, which pandoc does reproduce
BESIDE_OVERLAP = 0.5    # text level with a block over this much of its height
                        # is beside it, not above or below it


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(2)


class Gate:
    def __init__(self, name, ok, detail, hint=None):
        self.name = name
        self.ok = ok
        self.detail = detail
        self.hint = hint


def cells_of(rect, width, height):
    x0 = max(0, int(rect.x0 / width * GRID_X))
    x1 = min(GRID_X, int(rect.x1 / width * GRID_X) + 1)
    y0 = max(0, int(rect.y0 / height * GRID_Y))
    y1 = min(GRID_Y, int(rect.y1 / height * GRID_Y) + 1)
    return {(i, j) for i in range(x0, x1) for j in range(y0, y1)}


def rect_key(rect):
    return (round(rect.x0), round(rect.y0), round(rect.x1), round(rect.y1))


def page_fills(page):
    """Filled drawings and images, minus the page background."""
    width, height = page.rect.width, page.rect.height
    fills, images = [], []
    for drawing in page.get_drawings():
        colour = drawing.get("fill")
        if colour is None or min(colour) > 0.95:
            continue
        rect = drawing["rect"]
        if rect.width * rect.height > 0.98 * width * height:
            continue
        fills.append(rect)
    for image in page.get_images(full=True):
        images.extend(page.get_image_rects(image[0]))
    return fills, images


def page_rules(page):
    """Horizontal and vertical strokes, as (x0, y0, x1, y1)."""
    horizontal, vertical = [], []
    for drawing in page.get_drawings():
        if drawing.get("color") is None:
            continue
        for item in drawing["items"]:
            if item[0] == "l":
                (ax, ay), (bx, by) = (item[1].x, item[1].y), (item[2].x, item[2].y)
            elif item[0] == "re":
                rect = item[1]
                ax, ay, bx, by = rect.x0, rect.y0, rect.x1, rect.y1
            else:
                continue
            dx, dy = abs(bx - ax), abs(by - ay)
            if dy <= 1 < dx:
                horizontal.append((min(ax, bx), (ay + by) / 2, max(ax, bx), (ay + by) / 2))
            elif dx <= 1 < dy:
                vertical.append(((ax + bx) / 2, min(ay, by), (ax + bx) / 2, max(ay, by)))
    return horizontal, vertical


def page_lines(page):
    out = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            text = "".join(span["text"] for span in line["spans"]).strip()
            if text:
                out.append((line["bbox"], text))
    return out


def regions_of(lines):
    """Split one page's lines at the vertical corridors that run its height."""
    if len(lines) < 8:
        return None

    x0 = min(b[0] for b, _ in lines)
    x1 = max(b[2] for b, _ in lines)
    y0 = min(b[1] for b, _ in lines)
    y1 = max(b[3] for b, _ in lines)
    body_width, body_height = x1 - x0, y1 - y0
    if body_width <= 0 or body_height <= 0:
        return None

    nx = max(1, int(body_width / BIN_PT))
    ny = max(1, int(body_height / BIN_PT))
    occupied = [set() for _ in range(nx)]
    for (bx0, by0, bx1, by1), _ in lines:
        i0 = max(0, int((bx0 - x0) / BIN_PT))
        i1 = min(nx, int((bx1 - x0) / BIN_PT) + 1)
        rows = range(max(0, int((by0 - y0) / BIN_PT)), min(ny, int((by1 - y0) / BIN_PT) + 1))
        for i in range(i0, i1):
            occupied[i].update(rows)

    limit = CORRIDOR_NOISE * ny
    clear = [len(rows) <= limit for rows in occupied]

    spans, start = [], None
    for i, empty in enumerate(clear + [True]):
        if not empty and start is None:
            start = i
        elif empty and start is not None:
            gap_end = i
            while gap_end < nx and clear[gap_end]:
                gap_end += 1
            if gap_end == nx or (gap_end - i) * BIN_PT >= CORRIDOR_PT:
                spans.append((start, i))
                start = None
    if start is not None:
        spans.append((start, nx))

    total_chars = sum(len(text) for _, text in lines) or 1
    measured = []
    for a, b in spans:
        left, right = x0 + a * BIN_PT, x0 + b * BIN_PT
        inside = [
            (bbox, text)
            for bbox, text in lines
            if left - 1 <= (bbox[0] + bbox[2]) / 2 <= right + 1
        ]
        if not inside:
            continue
        measured.append(
            {
                "left": left,
                "width": right - left,
                "span": max(b[3] for b, _ in inside) - min(b[1] for b, _ in inside),
                "share": sum(len(t) for _, t in inside) / total_chars,
            }
        )

    tall = [
        r
        for r in measured
        if r["span"] >= TALL_REGION * body_height and r["share"] >= CHAR_SHARE
    ]
    return {"body_height": body_height, "tall": tall}


def assess_pdf(path):
    try:
        import pymupdf
    except ImportError:
        fail("pymupdf is required for a PDF. pip install pymupdf")

    doc = pymupdf.open(path)
    pages = len(doc)
    chrome_at = max(2, pages * 0.6)

    shape_repeats, rule_repeats, line_repeats = (
        collections.Counter(),
        collections.Counter(),
        collections.Counter(),
    )
    per_page = []
    for page in doc:
        fills, images = page_fills(page)
        horizontal, vertical = page_rules(page)
        lines = page_lines(page)
        for rect in fills + images:
            shape_repeats[rect_key(rect)] += 1
        for rule in horizontal + vertical:
            rule_repeats[tuple(round(v) for v in rule)] += 1
        band = RUNNING_BAND * page.rect.height
        for bbox, text in lines:
            # Only a line near an edge can be a running head or foot. Body text
            # that happens to repeat is still body text.
            if bbox[1] <= band or bbox[3] >= page.rect.height - band:
                line_repeats[(round(bbox[1]), text)] += 1
        per_page.append(
            {
                "size": (page.rect.width, page.rect.height),
                "fills": fills,
                "images": images,
                "horizontal": horizontal,
                "vertical": vertical,
                "lines": lines,
            }
        )

    def is_chrome_shape(rect):
        return pages > 1 and shape_repeats[rect_key(rect)] >= chrome_at

    def is_chrome_rule(rule):
        return pages > 1 and rule_repeats[tuple(round(v) for v in rule)] >= chrome_at

    # ── gate: columns ────────────────────────────────────────────────────────
    column_counts, ratios, unequal_pages, measured_pages = [], [], 0, 0
    for page in per_page:
        body = [
            (bbox, text)
            for bbox, text in page["lines"]
            if not (pages > 1 and line_repeats[(round(bbox[1]), text)] >= chrome_at)
        ]
        found = regions_of(body)
        if found is None:
            continue
        measured_pages += 1
        tall = found["tall"]
        column_counts.append(len(tall))
        if len(tall) >= 2:
            widths = [r["width"] for r in tall]
            ratio = max(widths) / min(widths)
            ratios.append(ratio)
            if ratio > WIDTH_RATIO or len(tall) > 2:
                unequal_pages += 1

    if measured_pages == 0:
        gates = [
            Gate(
                "columns",
                False,
                "too few lines to tell a gutter from a margin",
                "A scan or an image-only export has no text to measure.",
            )
        ]
        columns = 0
    else:
        columns = statistics.median(column_counts)
        widest = max(ratios, default=1.0)
        if unequal_pages * 2 >= measured_pages:
            detail = f"{columns:.0f} regions, widths differ by {widest:.2f}x"
        elif columns >= 2:
            detail = f"{columns:.0f} equal columns, widths differ by {widest:.2f}x"
        else:
            detail = "one column"
        gates = [Gate("columns", unequal_pages * 2 < measured_pages, detail)]

    # ── gate: blocks side by side ────────────────────────────────────────────
    # A fill or an image with text beside it at the same height is one block
    # among several: a sidebar panel, a card in a grid, a wrapped photo. One
    # that spans the flow — a shaded table row, a full-width figure — is not.
    beside = 0
    for page in per_page:
        for rect in page["fills"] + page["images"]:
            if is_chrome_shape(rect):
                continue
            height = rect.y1 - rect.y0
            if height <= 0:
                continue
            for bbox, _ in page["lines"]:
                overlap = min(bbox[3], rect.y1) - max(bbox[1], rect.y0)
                outside = bbox[2] < rect.x0 - 2 or bbox[0] > rect.x1 + 2
                if outside and overlap >= BESIDE_OVERLAP * min(height, bbox[3] - bbox[1]):
                    beside += 1
                    break
    gates.append(
        Gate(
            "blocks side by side",
            beside == 0,
            "none" if not beside else f"{beside} fills or images with text beside them",
        )
    )

    # ── gate: page art ───────────────────────────────────────────────────────
    # Full-bleed decoration passes the test above, because nothing is beside it.
    coverage = []
    for page in per_page:
        width, height = page["size"]
        net = set()
        for rect in page["fills"] + page["images"]:
            if not is_chrome_shape(rect):
                net |= cells_of(rect, width, height)
        coverage.append(len(net) / CELLS)
    ink = statistics.median(coverage)
    gates.append(
        Gate("page art", ink <= PAGE_ART, f"{ink:.3f} of the median page, chrome excluded")
    )

    # ── gate: dividing rules ─────────────────────────────────────────────────
    dividers = 0
    longest = 0.0
    for page in per_page:
        height = page["size"][1]
        for rule in page["vertical"]:
            if is_chrome_rule(rule):
                continue
            length = rule[3] - rule[1]
            longest = max(longest, length / height)
            if length >= LONG_RULE * height:
                dividers += 1
    gates.append(
        Gate(
            "dividing rules",
            dividers == 0,
            "none" if not dividers else f"{dividers} vertical, longest {longest:.0%} of the page",
        )
    )

    # ── gate: paragraph rules ────────────────────────────────────────────────
    borders = 0
    for page in per_page:
        for rule in page["horizontal"]:
            if is_chrome_rule(rule):
                continue
            x0, y, x1, _ = rule
            in_table = any(
                v[1] - LATTICE_PT <= y <= v[3] + LATTICE_PT and x0 - 2 <= v[0] <= x1 + 2
                for v in page["vertical"]
            )
            if in_table:
                continue
            near_text = any(
                abs(bbox[3] - y) <= RULE_TO_TEXT or abs(bbox[1] - y) <= RULE_TO_TEXT
                for bbox, _ in page["lines"]
            )
            if near_text:
                borders += 1
    gates.append(
        Gate(
            "paragraph rules",
            borders == 0,
            "none" if not borders else f"{borders} rules under or over a line of text",
            "set_style.py cannot write w:pBdr yet; a --border-bottom flag would "
            "move these inside the list.",
        )
    )

    return gates


DOCX_MARKS = [
    ("floating image or shape", re.compile(rb"<wp:anchor[ >]")),
    ("text box", re.compile(rb"<w:txbxContent[ >]|<mc:AlternateContent[ >]")),
    ("positioned frame", re.compile(rb"<w:framePr[ >]")),
]


def assess_docx(path):
    """A docx needs fewer gates than a PDF.

    build_reference.py copies styles.xml across whole, so a rule carried on a
    style as w:pBdr survives — which is why there is no paragraph-rule gate
    here. Only what pandoc's single paragraph stream cannot express is gated.
    """
    try:
        with zipfile.ZipFile(path) as zf:
            body = zf.read("word/document.xml")
    except (KeyError, zipfile.BadZipFile):
        fail(f"{path} is not a readable .docx")

    gates = []
    for name, pattern in DOCX_MARKS:
        found = len(pattern.findall(body))
        gates.append(Gate(name, found == 0, "none" if not found else str(found)))

    # A table of two or three rows whose cells hold prose is page scaffolding,
    # not data: a resume's sidebar, a two-up block, a header card. A data table
    # has many rows and a short value in each cell, and so does the two-column
    # table a resume uses to push a date to the right margin. Borders say
    # nothing here — they usually come from the table style, not the table.
    layout_tables = 0
    for table in re.findall(rb"<w:tbl>.*?</w:tbl>", body, re.S):
        columns = len(re.findall(rb"<w:gridCol[ /]", table))
        rows = len(re.findall(rb"<w:tr[ >]", table))
        prose_cells = 0
        for cell in re.findall(rb"<w:tc>.*?</w:tc>", table, re.S):
            text = b"".join(re.findall(rb"<w:t[^>]*>(.*?)</w:t>", cell, re.S))
            if len(re.findall(rb"<w:p[ >]", cell)) >= 2 or len(text) >= 80:
                prose_cells += 1
        if columns >= 2 and rows <= 2 and prose_cells:
            layout_tables += 1
    gates.append(
        Gate("layout table", layout_tables == 0, "none" if not layout_tables else str(layout_tables))
    )

    # Unequal columns come from one w:cols with explicit widths, which the
    # branch keeps, but only one section may define them.
    widths = re.findall(rb'<w:col [^>]*w:w="(\d+)"', body)
    if len(widths) >= 2:
        values = [int(w) for w in widths]
        equal = max(values) / min(values) <= WIDTH_RATIO
        gates.append(
            Gate("columns", equal, f"{len(values)} columns, widths differ by "
                 f"{max(values) / min(values):.2f}x")
        )
    else:
        gates.append(Gate("columns", True, "one column"))

    return gates


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="the .pdf or .docx already routed to the pdf or docx branch")
    args = parser.parse_args()

    if not os.path.exists(args.source):
        fail(f"{args.source} does not exist")

    ext = os.path.splitext(args.source)[1].lower()
    if ext == ".pdf":
        gates = assess_pdf(args.source)
    elif ext == ".docx":
        gates = assess_docx(args.source)
    else:
        fail(f"{ext or args.source}: run this on the .pdf or .docx only")

    print(f"[source]\n  {args.source}\n")
    print("[gates]")
    for gate in gates:
        print(f"  {'pass' if gate.ok else 'FAIL'}  {gate.name:22s} {gate.detail}")
    print()

    failed = [gate for gate in gates if not gate.ok]
    if not failed:
        print("[verdict]  flow  ->  stay on this branch")
        print("  every gate passed, so a reference.docx reproduces this page")
        return 0

    print("[verdict]  composed  ->  reverse-template/source-style/SKILL.md")
    print(f"  outside the list: {', '.join(gate.name for gate in failed)}")
    for gate in failed:
        if gate.hint:
            print(f"  note: {gate.hint}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
