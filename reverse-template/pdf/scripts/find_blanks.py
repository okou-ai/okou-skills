"""List the blanks a form's pages leave for a new document to fill.

    python3 find_blanks.py source.pdf

Read-only, always exits 0. Output is one line per blank in reading order:

    p<page>  <kind>  <the line it sits in, blank marked [...]>

Three kinds, because a PDF writes a blank three ways and only one of them is
a character:

    underscores   a run of _ in the text layer
    ruled         a drawn rule under spaces, which carries no character at all
    parenthetical an instruction to the filler, e.g. (NAME) or (DATE)

A ruled blank is told from an underlined phrase by what sits above the rule:
spaces mean a blank, glyphs mean emphasis. Nothing else distinguishes them —
rule thickness tracks the font size, not the purpose.

A parenthetical whose letters are the initials of the words before it defines a
term rather than asking for one, and is dropped: "combined single limit (CSL)"
is not a blank, "take effect on (DATE)" is. An acronym used without being
defined nearby still reads as a blank here. Check the list against the rendered
pages; this narrows the reading, it does not finish it.
"""

import re
import sys

import pymupdf

# A parenthetical instruction is upper-case: (NAME), (DATE), (ADDRESS). Mixed
# case is ordinary prose — "(services/project name)" is a note to the reader,
# not a slot, and is left out.
PARENTHETICAL = re.compile(r"\([A-Z][A-Z0-9 ./&'-]{1,40}\)")
UNDERSCORES = re.compile(r"_{2,}")
WORD = re.compile(r"[A-Za-z]+")

# A rule sits within this many points below the baseline of the line it marks.
RULE_DROP = 5.0
# Anything taller is a filled box or a table shade, not a rule.
RULE_MAX_HEIGHT = 2.5


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
                }
            )
    out.sort(key=lambda l: (round(l["baseline"], 1), l["chars"][0]["bbox"][0]))
    return out


def rules_of(page):
    """Thin filled rectangles, which is how a PDF draws any underline."""
    out = []
    for drawing in page.get_drawings():
        rect = drawing["rect"]
        if 0 < rect.y1 - rect.y0 <= RULE_MAX_HEIGHT and rect.x1 - rect.x0 > 2:
            out.append(rect)
    return out


def covered_text(line, x0, x1):
    """The characters of `line` that sit within a rule's horizontal span."""
    return "".join(
        c["c"]
        for c in line["chars"]
        if c["bbox"][0] < x1 and c["bbox"][2] > x0
    )


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

        for index, line in enumerate(lines):
            previous = lines[index - 1]["text"] if index else ""
            for m in UNDERSCORES.finditer(line["text"]):
                found.append((number, line["baseline"], "underscores", mark(line["text"], m.start(), m.end())))
            for m in PARENTHETICAL.finditer(line["text"]):
                if defines_acronym(line["text"], m.start(), m.end(), previous):
                    continue
                found.append((number, line["baseline"], "parenthetical", mark(line["text"], m.start(), m.end())))

        for rect in rules:
            above = [l for l in lines if 0 <= rect.y0 - l["baseline"] <= RULE_DROP]
            if not above:
                continue
            # Any glyph under the rule means an underlined phrase, or a run of
            # underscores already reported. Several lines can share a baseline
            # band, so every one of them has to be clear before this is a blank.
            if any(covered_text(l, rect.x0, rect.x1).strip() for l in above):
                continue
            line = min(above, key=lambda l: rect.y0 - l["baseline"])
            found.append(
                (
                    number,
                    line["baseline"],
                    "ruled",
                    f"{line['text'].strip()}   <- rule at x={rect.x0:.0f}..{rect.x1:.0f}",
                )
            )

    found.sort(key=lambda f: (f[0], f[1]))
    for number, _, kind, context in found:
        print(f"p{number:<3} {kind:<14} {context[:110]}")
    print(f"\n{len(found)} blanks on {doc.page_count} pages", file=sys.stderr)
    doc.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    find(sys.argv[1])
