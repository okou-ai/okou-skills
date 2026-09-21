"""List the blanks a form's pages leave for a new document to fill.

    python3 find_blanks.py source.pdf

Read-only. Output is one line per blank in reading order:

    p<page>  <kind>  <the line it sits in, blank marked [...]>

Four kinds, because a PDF writes a blank three ways and only one of them is
a character:

    underscores   a run of _ in the text layer
    ruled         a rule drawn under spaces, on a line that carries text
    rule-alone    a rule on a line of its own, labelled from below or above —
                  a signature line
    parenthetical an instruction to the filler, e.g. (NAME) or (DATE)

A rule is a thin filled rectangle (Word) or a stroked line of any thickness
(LibreOffice, Typst, LaTeX); both are read, and a rule a PDF writes in pieces
is joined back into one. A ruled blank is told from an underlined phrase by
what sits above the rule: spaces mean a blank, glyphs mean emphasis. Nothing
else distinguishes them — rule thickness tracks the font size, not the purpose.

Left out on purpose: a parenthetical whose letters are the initials of the
words before it defines a term rather than asking for one — "combined single
limit (CSL)" is not a blank, "take effect on (DATE)" is; a roman numeral in
brackets is an enumerator; a rule wider than half the page is a separator.

Still reported, and for the reader to strike: an acronym used without being
defined nearby, and any other upper-case bracket such as (US) or (INC.). A
rule in a table cell's bottom border with no label near it is not found at
all. Check the list against the rendered pages; this narrows the reading, it
does not finish it.
"""

import re
import sys

import pymupdf

# A parenthetical instruction is upper-case: (NAME), (DATE), (ADDRESS). Mixed
# case is ordinary prose — "(services/project name)" is a note to the reader,
# not a slot, and is left out.
PARENTHETICAL = re.compile(r"\([A-Z][A-Z0-9 ./&'-]{1,40}\)")
ROMAN = re.compile(r"[IVXLC]+")
UNDERSCORES = re.compile(r"_{2,}")
WORD = re.compile(r"[A-Za-z]+")

# A rule sits within this band around the baseline of the line it marks: up
# to RULE_DROP below it, or RULE_RISE above it when it is a box's bottom edge.
RULE_DROP = 5.0
RULE_RISE = 1.0
# Anything taller is a filled box or a table shade, not a rule.
RULE_MAX_HEIGHT = 2.5
# A rule on its own line is a blank only when its label sits this close.
LABEL_REACH = 20.0
# A rule wider than this share of the page is a separator, not a blank.
SEPARATOR_SHARE = 0.5
# Pieces of one rule: same height within this, touching within this.
JOIN_Y = 0.6
JOIN_X = 1.5


def lines_of(page):
    """Visual lines with their characters, in reading order."""
    out = []
    for block in page.get_text("rawdict")["blocks"]:
        if block["type"] != 0:
            continue
        for line in block["lines"]:
            chars = [c for span in line["spans"] for c in span["chars"]]
            if not chars:
                continue
            out.append(
                {
                    "baseline": line["spans"][0]["origin"][1],
                    "chars": chars,
                    "text": "".join(c["c"] for c in chars).rstrip(),
                    "x0": min(c["bbox"][0] for c in chars),
                    "x1": max(c["bbox"][2] for c in chars),
                }
            )
    out.sort(key=lambda l: (round(l["baseline"], 1), l["x0"]))
    return out


def rules_of(page):
    """Horizontal rules: thin filled rectangles or stroked lines, joined."""
    pieces = []
    for drawing in page.get_drawings():
        rect = drawing["rect"]
        height = rect.y1 - rect.y0
        if drawing["type"] == "f":
            if not 0 < height <= RULE_MAX_HEIGHT:
                continue
        else:
            # A stroked path's rect has no thickness; the pen width is it.
            height = max(height, drawing.get("width") or 0)
            if height > RULE_MAX_HEIGHT:
                continue
        if rect.x1 - rect.x0 <= 2:
            continue
        pieces.append(pymupdf.Rect(rect))
    pieces.sort(key=lambda r: (round(r.y0, 1), r.x0))

    out = []
    for rect in pieces:
        last = out[-1] if out else None
        if last and abs(last.y0 - rect.y0) < JOIN_Y and rect.x0 - last.x1 < JOIN_X:
            last.x1 = max(last.x1, rect.x1)
            continue
        out.append(rect)
    return out


def covered_text(line, x0, x1):
    """The characters of `line` that sit within a rule's horizontal span."""
    return "".join(
        c["c"]
        for c in line["chars"]
        if c["bbox"][0] < x1 and c["bbox"][2] > x0
    )


def label_of(candidates, rect):
    """The line that labels a rule: the nearest one ending to its left,
    else the nearest one vertically."""
    left = [l for l in candidates if l["x1"] <= rect.x0 + 2]
    if left:
        return min(left, key=lambda l: rect.x0 - l["x1"])
    return min(candidates, key=lambda l: abs(rect.y0 - l["baseline"]))


def mark(text, start, end):
    return f"{text[:start]}[{text[start:end]}]{text[end:]}".strip()


def defines_acronym(text, start, end, preceding=""):
    """True when the parenthetical spells out the initials just before it.

    "combined single limit (CSL)" defines a term; "take effect on (DATE)" asks
    for one. Both are upper-case in brackets, and this is what separates them.

    `preceding` carries the line above, because a defining phrase is often
    split by the line break that precedes its acronym.
    """
    letters = [c for c in text[start + 1 : end - 1] if c.isalpha()]
    if not letters:
        return False
    before = WORD.findall(f"{preceding} {text[:start]}")[-len(letters) :]
    if len(before) != len(letters):
        return False
    return [w[0].upper() for w in before] == [c.upper() for c in letters]


def find(path):
    doc = pymupdf.open(path)
    found = []

    for number, page in enumerate(doc, 1):
        lines = lines_of(page)
        rules = rules_of(page)
        separator = page.rect.width * SEPARATOR_SHARE

        for index, line in enumerate(lines):
            previous = lines[index - 1]["text"] if index else ""
            for m in UNDERSCORES.finditer(line["text"]):
                found.append((number, line["baseline"], "underscores", mark(line["text"], m.start(), m.end())))
            for m in PARENTHETICAL.finditer(line["text"]):
                inner = line["text"][m.start() + 1 : m.end() - 1]
                if ROMAN.fullmatch(inner):
                    continue
                if defines_acronym(line["text"], m.start(), m.end(), previous):
                    continue
                found.append((number, line["baseline"], "parenthetical", mark(line["text"], m.start(), m.end())))

        for rect in rules:
            if rect.x1 - rect.x0 > separator:
                continue
            where = f"<- rule at x={rect.x0:.0f}..{rect.x1:.0f}"
            above = [l for l in lines if -RULE_RISE <= rect.y0 - l["baseline"] <= RULE_DROP]
            if above:
                # Any glyph under the rule means an underlined phrase, or a
                # run of underscores already reported. Several lines can share
                # a baseline band, so every one of them has to be clear.
                if any(covered_text(l, rect.x0, rect.x1).strip() for l in above):
                    continue
                line = label_of(above, rect)
                found.append((number, line["baseline"], "ruled", f"{line['text'].strip()}   {where}"))
                continue
            # No text on the rule's own line: a signature line, labelled by
            # the nearest line below (or above) it.
            near = [l for l in lines if abs(l["baseline"] - rect.y0) <= LABEL_REACH]
            if not near:
                continue
            label = min(near, key=lambda l: (abs(l["baseline"] - rect.y0), abs(l["x0"] - rect.x0)))
            found.append((number, rect.y0, "rule-alone", f"{label['text'].strip()}   {where}"))

    found.sort(key=lambda f: (f[0], round(f[1], 1)))
    for number, _, kind, context in found:
        print(f"p{number:<3} {kind:<14} {context[:110]}")
    print(f"\n{len(found)} blanks on {doc.page_count} pages", file=sys.stderr)
    doc.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    find(sys.argv[1])
