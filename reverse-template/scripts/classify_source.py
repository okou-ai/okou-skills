#!/usr/bin/env python3
"""Name the branch of reverse-template that a source file belongs to."""

import argparse
import os
import shutil
import statistics
import subprocess
import sys

PRESENTATION = "presentation"
DOCX = "docx"
PDF = "pdf"
AMBIGUOUS = "ambiguous"

GUIDE = {
    PRESENTATION: "reverse-template/presentation/SKILL.md",
    DOCX: "reverse-template/docx/SKILL.md",
    PDF: "reverse-template/pdf/SKILL.md",
}

DECK_EXT = {".pptx", ".ppt", ".key", ".odp"}
IMAGE_EXT = {".png", ".jpg", ".jpeg", ".webp", ".heic", ".tif", ".tiff", ".bmp"}
DOC_EXT = {".docx"}
LEGACY_DOC_EXT = {".doc", ".rtf", ".odt"}

# Paper sizes in points, portrait. A page that matches one of these in either
# orientation was laid out for paper, which decks are not.
PAPER = {
    "A3": (841.9, 1190.6),
    "A4": (595.3, 841.9),
    "A5": (419.5, 595.3),
    "B5": (498.9, 708.7),
    "Letter": (612.0, 792.0),
    "Legal": (612.0, 1008.0),
    "Tabloid": (792.0, 1224.0),
}
PAPER_TOLERANCE_PT = 6.0

# Ratios decks are authored at, as width / height.
DECK_RATIOS = {"16:9": 16 / 9, "16:10": 16 / 10, "4:3": 4 / 3, "3:2": 3 / 2}
RATIO_TOLERANCE = 0.02

# Characters on the median page. Measured on real files: a sparse deck lands
# near 170, a text-heavy deck near 1100, an A4 report near 3700.
DECK_CHARS_MAX = 700
DOC_CHARS_MIN = 1800


def fail(message):
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(2)


def require(binary):
    if shutil.which(binary) is None:
        fail(f"{binary} not found. Install poppler-utils.")


def pdf_geometry(path):
    require("pdfinfo")
    out = subprocess.run(
        ["pdfinfo", path], capture_output=True, text=True, check=False
    ).stdout
    pages, width, height = None, None, None
    for line in out.splitlines():
        if line.startswith("Pages:"):
            pages = int(line.split(":", 1)[1].strip())
        elif line.startswith("Page size:"):
            value = line.split(":", 1)[1].strip().split(" pts")[0]
            width, height = (float(n) for n in value.split(" x "))
    if width is None or height is None:
        fail(f"pdfinfo reported no page size for {path}")
    return pages, width, height


def pdf_chars_per_page(path):
    require("pdftotext")
    out = subprocess.run(
        ["pdftotext", "-q", path, "-"], capture_output=True, text=True, check=False
    ).stdout
    pages = [len(page.strip()) for page in out.split("\f")]
    if pages and pages[-1] == 0:
        pages.pop()
    return pages or [0]


def paper_match(width, height):
    short, long_ = sorted((width, height))
    for name, (pw, ph) in PAPER.items():
        if (
            abs(short - pw) <= PAPER_TOLERANCE_PT
            and abs(long_ - ph) <= PAPER_TOLERANCE_PT
        ):
            return name
    return None


def deck_ratio(width, height):
    ratio = width / height
    for name, value in DECK_RATIOS.items():
        if abs(ratio - value) <= RATIO_TOLERANCE:
            return name
    return None


def classify_pdf(path):
    pages, width, height = pdf_geometry(path)
    chars = pdf_chars_per_page(path)
    median = statistics.median(chars)
    paper = paper_match(width, height)
    ratio = deck_ratio(width, height)
    orientation = "portrait" if height > width else "landscape"

    if paper:
        geometry_vote, geometry_why = PDF, f"{paper} {orientation} is a paper size"
    elif ratio:
        geometry_vote, geometry_why = PRESENTATION, f"{ratio} is a slide ratio"
    elif orientation == "portrait":
        geometry_vote, geometry_why = PDF, "portrait pages are not authored as slides"
    else:
        geometry_vote, geometry_why = None, "page size matches neither paper nor a slide ratio"

    with_text = sum(1 for n in chars if n > 0)
    if with_text == 0:
        density_vote, density_why = None, "no text layer"
    elif median <= DECK_CHARS_MAX:
        density_vote, density_why = PRESENTATION, f"{median:.0f} chars on the median page"
    elif median >= DOC_CHARS_MIN:
        density_vote, density_why = PDF, f"{median:.0f} chars on the median page"
    else:
        density_vote, density_why = None, f"{median:.0f} chars on the median page is between a deck and a document"

    report = [
        "[geometry]",
        f"  pages      {pages}",
        f"  page size  {width:.1f} x {height:.1f} pt  "
        f"({paper or ratio or 'non-standard'} {orientation})",
        f"  aspect     {width / height:.3f}",
        "",
        "[text]",
        f"  median chars/page  {median:.0f}  (min {min(chars)}, max {max(chars)})",
        f"  pages with text    {with_text}/{len(chars)}",
        "",
        "[votes]",
        f"  geometry   {geometry_vote or 'undecided'}  — {geometry_why}",
        f"  density    {density_vote or 'undecided'}  — {density_why}",
    ]

    # A deck runs to many pages. One or two pages at a paper size is a document
    # however little text it carries — a resume, a certificate, an invoice —
    # and sparse text there is a form, which the router's question 2 answers.
    if paper and pages <= 2:
        return PDF, report, f"{pages} page(s) at {paper}: a document, not a deck"

    if geometry_vote and density_vote and geometry_vote != density_vote:
        return AMBIGUOUS, report, "the two signals disagree"
    route = geometry_vote or density_vote
    if route is None:
        return AMBIGUOUS, report, "neither signal decided"
    return route, report, f"{geometry_why}; {density_why}"


def classify(path):
    if os.path.isdir(path):
        images = [
            n for n in os.listdir(path) if os.path.splitext(n)[1].lower() in IMAGE_EXT
        ]
        if images:
            return PRESENTATION, [], f"a directory of {len(images)} page images"
        fail(f"{path} holds no page images")

    ext = os.path.splitext(path)[1].lower()
    if ext in DECK_EXT:
        return PRESENTATION, [], f"{ext} is a deck"
    if ext in IMAGE_EXT:
        return PRESENTATION, [], f"{ext} is a page image"
    if ext in DOC_EXT:
        return DOCX, [], f"{ext} is a Word document"
    if ext in LEGACY_DOC_EXT:
        return DOCX, [], f"{ext}: re-save it as .docx from Word first, then follow the docx guide"
    if ext == ".pdf":
        return classify_pdf(path)
    fail(f"unsupported source {ext or path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="deck, document, or directory of page images")
    args = parser.parse_args()

    if not os.path.exists(args.source):
        fail(f"{args.source} does not exist")

    route, report, why = classify(args.source)

    print(f"[source]\n  {args.source}\n")
    if report:
        print("\n".join(report))
        print()

    if route == AMBIGUOUS:
        print(f"[route]  ambiguous — {why}")
        print(
            "  Render page 1 and look at it, then pick the branch yourself:\n"
            f"    okou presentation screenshot --input {args.source} --out shots"
        )
        return 1

    print(f"[route]  {route}  ->  {GUIDE[route]}")
    print(f"  {why}")
    if route in (DOCX, PDF):
        print(
            "  That branch builds a style sheet. Look at the pages first: a form,\n"
            "  or an article whose body is not one stream, takes source-style."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
