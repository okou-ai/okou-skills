#!/usr/bin/env python3
"""Say whether a document's look survives a style-only template.

The docx and pdf branches produce a `reference.docx`: a style sheet. Pandoc
pours one stream of paragraphs into it, top to bottom, in one column or in
equal columns. That reproduces paper size, margins, per-style type, a header
and a footer — and nothing that depends on where a block sits. A sidebar, a
panel behind text, a floating photo, a grid of cards: a source whose identity
lives in those goes to the source-style branch instead.
"""

import argparse
import collections
import os
import re
import statistics
import sys
import zipfile

FLOW = "flow"
COMPOSED = "composed"
CHECK = "check"

GRID_X, GRID_Y = 60, 84
CELLS = GRID_X * GRID_Y

# Share of the page covered by fills and images that are not page chrome.
# Measured: an A4 report with a brand band, a logo and a shaded table lands at
# 0.045 once its chrome is subtracted; a sidebar resume at 0.333.
COMPOSED_INK = 0.12
FLOW_INK = 0.06

BIN_PT = 2.0            # x and y resolution when looking for a gutter
CORRIDOR_PT = 8.0       # narrower than this is letter spacing, not a gutter
CORRIDOR_NOISE = 0.03   # a gutter may be crossed by a spanning title or figure
TALL_REGION = 0.5       # a region this much of the body height runs down the page
WIDTH_RATIO = 1.25      # wider a gap than this between two regions and they are
                        # not columns of one grid
CHAR_SHARE = 0.08       # a column of right-aligned dates is a tab stop, not a
                        # region; it holds almost none of the page's text
RUNNING_BAND = 0.12     # a running head or foot lives this far into the page


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(2)


def cells_of(rect, width, height):
    x0 = max(0, int(rect.x0 / width * GRID_X))
    x1 = min(GRID_X, int(rect.x1 / width * GRID_X) + 1)
    y0 = max(0, int(rect.y0 / height * GRID_Y))
    y1 = min(GRID_Y, int(rect.y1 / height * GRID_Y) + 1)
    return {(i, j) for i in range(x0, x1) for j in range(y0, y1)}


def rect_key(rect):
    return (round(rect.x0), round(rect.y0), round(rect.x1), round(rect.y1))


def page_shapes(page):
    """Filled drawings and images, minus the page background."""
    width, height = page.rect.width, page.rect.height
    shapes = []
    for drawing in page.get_drawings():
        fill = drawing.get("fill")
        if fill is None or min(fill) > 0.95:  # unfilled or near-white: not ink
            continue
        rect = drawing["rect"]
        if rect.width * rect.height > 0.98 * width * height:
            continue
        shapes.append(rect)
    for image in page.get_images(full=True):
        shapes.extend(page.get_image_rects(image[0]))
    return shapes


def page_lines(page):
    out = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            text = "".join(span["text"] for span in line["spans"]).strip()
            if text:
                out.append((line["bbox"], text))
    return out


def side_by_side(lines):
    """Split one page's lines at vertical corridors and keep the tall regions.

    A sidebar and a column look the same here; what separates them is width.
    Pandoc writes equal columns from one `w:cols`, so equal regions stay
    reproducible and unequal ones do not.
    """
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
        j0 = max(0, int((by0 - y0) / BIN_PT))
        j1 = min(ny, int((by1 - y0) / BIN_PT) + 1)
        rows = range(j0, j1)
        for i in range(i0, i1):
            occupied[i].update(rows)

    limit = CORRIDOR_NOISE * ny
    clear = [len(rows) <= limit for rows in occupied]

    regions, start = [], None
    for i, empty in enumerate(clear + [True]):
        if not empty and start is None:
            start = i
        elif empty and start is not None:
            gap_end = i
            while gap_end < nx and clear[gap_end]:
                gap_end += 1
            if gap_end == nx or (gap_end - i) * BIN_PT >= CORRIDOR_PT:
                regions.append((start, i))
                start = None
    if start is not None:
        regions.append((start, nx))

    total_chars = sum(len(text) for _, text in lines) or 1
    measured = []
    for a, b in regions:
        left, right = x0 + a * BIN_PT, x0 + b * BIN_PT
        inside = [
            (bbox, text)
            for bbox, text in lines
            if left - 1 <= (bbox[0] + bbox[2]) / 2 <= right + 1
        ]
        if not inside:
            continue
        span = max(bbox[3] for bbox, _ in inside) - min(bbox[1] for bbox, _ in inside)
        chars = sum(len(text) for _, text in inside)
        measured.append(
            {
                "left": left,
                "width": right - left,
                "span": span,
                "share": chars / total_chars,
            }
        )

    tall = [
        r
        for r in measured
        if r["span"] >= TALL_REGION * body_height and r["share"] >= CHAR_SHARE
    ]
    return {"body_height": body_height, "regions": measured, "tall": tall}


def assess_pdf(path):
    try:
        import pymupdf
    except ImportError:
        fail("pymupdf is required for a PDF. pip install pymupdf")

    doc = pymupdf.open(path)
    pages = len(doc)
    shapes_per_page, repeats = [], collections.Counter()
    line_repeats = collections.Counter()
    lines_per_page = []

    for page in doc:
        shapes = page_shapes(page)
        for rect in shapes:
            repeats[rect_key(rect)] += 1
        shapes_per_page.append((page.rect.width, page.rect.height, shapes))
        lines = page_lines(page)
        band = RUNNING_BAND * page.rect.height
        for bbox, text in lines:
            # Only a line near the top or bottom edge can be a running head or
            # foot. Body text that happens to repeat is still body text.
            if bbox[1] <= band or bbox[3] >= page.rect.height - band:
                line_repeats[(round(bbox[1]), text)] += 1
        lines_per_page.append(lines)

    # A shape or a line at the same place on most pages is a header band, a
    # footer rule, a logo or a running head. set_header_footer.py reproduces
    # those, so they are not evidence of composition.
    chrome_at = max(2, pages * 0.6)

    raw_cov, net_cov = [], []
    for width, height, shapes in shapes_per_page:
        raw, net = set(), set()
        for rect in shapes:
            covered = cells_of(rect, width, height)
            raw |= covered
            if pages > 1 and repeats[rect_key(rect)] >= chrome_at:
                continue
            net |= covered
        raw_cov.append(len(raw) / CELLS)
        net_cov.append(len(net) / CELLS)

    ink_raw = statistics.median(raw_cov)
    ink_net = statistics.median(net_cov)

    verdicts, shapes_seen = [], None
    for lines in lines_per_page:
        body = [
            (bbox, text)
            for bbox, text in lines
            if not (pages > 1 and line_repeats[(round(bbox[1]), text)] >= chrome_at)
        ]
        result = side_by_side(body)
        if result is None:
            continue
        shapes_seen = shapes_seen or result
        tall = result["tall"]
        if len(tall) < 2:
            verdicts.append((FLOW, len(tall)))
        else:
            widths = [r["width"] for r in tall]
            ratio = max(widths) / min(widths)
            verdicts.append((COMPOSED if ratio > WIDTH_RATIO else FLOW, len(tall), ratio))

    report = [
        "[layout]",
        f"  pages                 {pages}",
    ]
    if verdicts:
        composed_pages = sum(1 for v in verdicts if v[0] == COMPOSED)
        widest = max((v[2] for v in verdicts if len(v) > 2), default=1.0)
        columns = statistics.median([v[1] for v in verdicts])
        report.append(f"  full-height regions   {columns:.0f} on the median page")
        if widest > 1.0:
            report.append(f"  widest width ratio    {widest:.2f} (columns are 1.00)")
        report.append(f"  pages side by side    {composed_pages}/{len(verdicts)}")
        region_verdict = COMPOSED if composed_pages * 2 >= len(verdicts) else FLOW
    else:
        report.append("  full-height regions   not measurable (too few lines)")
        region_verdict = None

    report += [
        "",
        "[ink]",
        f"  covered, all fills    {ink_raw:.3f} of the median page",
        f"  covered, minus chrome {ink_net:.3f} of the median page",
    ]

    if region_verdict == COMPOSED:
        return COMPOSED, report, "the page splits into side-by-side regions of unequal width"
    if ink_net >= COMPOSED_INK:
        if pages == 1:
            return COMPOSED, report, f"{ink_net:.3f} of the page is fill or image"
        return COMPOSED, report, f"{ink_net:.3f} of the page is fill or image that is not chrome"
    if region_verdict == FLOW and ink_net <= FLOW_INK:
        return FLOW, report, "one stream of text, and no fill beyond the page chrome"
    if region_verdict is None:
        return CHECK, report, "too few lines to tell a gutter from a margin"
    return CHECK, report, f"{ink_net:.3f} sits between a report's chrome and a composed page"


DOCX_MARKS = [
    ("floating image or shape", re.compile(rb"<wp:anchor[ >]")),
    ("text box", re.compile(rb"<w:txbxContent[ >]|<mc:AlternateContent[ >]")),
    ("positioned frame", re.compile(rb"<w:framePr[ >]")),
]


def assess_docx(path):
    try:
        with zipfile.ZipFile(path) as zf:
            body = zf.read("word/document.xml")
    except (KeyError, zipfile.BadZipFile):
        fail(f"{path} is not a readable .docx")

    found = [(name, len(pattern.findall(body))) for name, pattern in DOCX_MARKS]
    found = [(name, n) for name, n in found if n]

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

    marks = found + ([("layout table", layout_tables)] if layout_tables else [])
    report = ["[composition marks]"]
    for name, n in marks:
        report.append(f"  {name:24s} {n}")
    if not marks:
        report.append("  none — the body is a linear flow of paragraphs")

    if marks:
        return COMPOSED, report, ", ".join(f"{n} {name}" for name, n in marks)
    return FLOW, report, "the body is a linear flow of paragraphs"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="the .pdf or .docx already routed to the pdf or docx branch")
    args = parser.parse_args()

    if not os.path.exists(args.source):
        fail(f"{args.source} does not exist")

    ext = os.path.splitext(args.source)[1].lower()
    if ext == ".pdf":
        verdict, report, why = assess_pdf(args.source)
    elif ext == ".docx":
        verdict, report, why = assess_docx(args.source)
    else:
        fail(f"{ext or args.source}: run this on the .pdf or .docx only")

    print(f"[source]\n  {args.source}\n")
    print("\n".join(report))
    print()

    if verdict == FLOW:
        print("[verdict]  flow  ->  stay on this branch")
        print(f"  {why}")
        return 0
    if verdict == COMPOSED:
        print("[verdict]  composed  ->  reverse-template/source-style/SKILL.md")
        print(f"  {why}: a reference.docx cannot hold this.")
        return 1
    print("[verdict]  check — look at a rendered page")
    print(f"  {why}")
    print(f"    okou presentation screenshot --input {args.source} --out shots")
    print(
        "  Blocks placed side by side with different widths, or text over a fill:\n"
        "  source-style. One stream of text down the page: stay here."
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
