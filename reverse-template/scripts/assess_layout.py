#!/usr/bin/env python3
"""Say whether a document's look survives a style-only template.

The docx and pdf branches produce a `reference.docx`: a style sheet. It carries
paper size, margins, columns, per-style fonts and spacing, and a header and
footer. It carries no composition — no sidebar, no panel behind a block of
text, no floating photo, no grid of coloured cards. A source whose identity
lives in its composition has to go to the source-style branch instead.
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


def assess_pdf(path):
    try:
        import pymupdf
    except ImportError:
        fail("pymupdf is required for a PDF. pip install pymupdf")

    doc = pymupdf.open(path)
    pages = len(doc)
    shapes_per_page, repeats = [], collections.Counter()

    for page in doc:
        width, height = page.rect.width, page.rect.height
        shapes = []
        for drawing in page.get_drawings():
            fill = drawing.get("fill")
            if fill is None or min(fill) > 0.95:  # unfilled or near-white: not ink
                continue
            rect = drawing["rect"]
            if rect.width * rect.height > 0.98 * width * height:  # page background
                continue
            shapes.append(rect)
        for image in page.get_images(full=True):
            shapes.extend(page.get_image_rects(image[0]))
        for rect in shapes:
            repeats[rect_key(rect)] += 1
        shapes_per_page.append((width, height, shapes))

    # A shape at the same place on most pages is a header band, a footer rule or
    # a logo. set_header_footer.py reproduces those, so they are not evidence.
    chrome_threshold = max(2, pages * 0.6)
    raw_cov, net_cov = [], []
    for width, height, shapes in shapes_per_page:
        raw, net = set(), set()
        for rect in shapes:
            covered = cells_of(rect, width, height)
            raw |= covered
            if pages > 1 and repeats[rect_key(rect)] >= chrome_threshold:
                continue
            net |= covered
        raw_cov.append(len(raw) / CELLS)
        net_cov.append(len(net) / CELLS)

    ink_raw = statistics.median(raw_cov)
    ink_net = statistics.median(net_cov)

    report = [
        "[ink]",
        f"  pages                {pages}",
        f"  covered, all fills   {ink_raw:.3f} of the median page",
        f"  covered, minus chrome {ink_net:.3f} of the median page",
    ]

    if pages == 1:
        report.append("  single page: chrome cannot be told from composition")
        if ink_net >= COMPOSED_INK:
            return COMPOSED, report, f"{ink_net:.3f} of the page is fill or image"
        return CHECK, report, "one page carries no repetition to measure"

    if ink_net >= COMPOSED_INK:
        return COMPOSED, report, f"{ink_net:.3f} of the page is fill or image that is not chrome"
    if ink_net <= FLOW_INK:
        return FLOW, report, f"only {ink_net:.3f} of the page is fill or image beyond its chrome"
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
    # has many rows and a short value in each cell. Borders say nothing here —
    # they usually come from the table style, not from the table itself.
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
    print("  Panels, sidebars or cards behind the text: source-style. Otherwise stay here.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
