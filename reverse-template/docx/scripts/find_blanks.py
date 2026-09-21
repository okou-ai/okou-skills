"""List the blanks a Word document leaves for a new document to fill.

    python3 find_blanks.py source.docx

Read-only. Output is one line per blank in document order:

    p<paragraph>  r<run>  <kind>  <the paragraph's text, blank marked [...]>

Paragraph and run numbers are the ones `inspect_docx.py --slots` prints, so a
blank matches its row there. Four kinds, because Word writes a blank four ways
and only two of them are text:

    underscores     a run of _ in a <w:t>
    underlined-tab  an underlined run holding only tabs or spaces. It has no
                    <w:t>, so --slots does not list it and it prints as r-
    bordered        an empty paragraph with a bottom border — a signature
                    line, labelled by the paragraph below it
    parenthetical   an instruction to the filler, e.g. (NAME) or (DATE)

Left out on purpose: a parenthetical whose letters are the initials of the
words before it defines a term rather than asking for one — "combined single
limit (CSL)" is not a blank, "take effect on (DATE)" is; a roman numeral in
brackets is an enumerator.

Still reported, and for the reader to strike: an acronym used without being
defined nearby, and any other upper-case bracket such as (US) or (INC.). A
blank drawn as a table cell's bottom border is not found at all. Check the
list against the rendered pages; this narrows the reading, it does not finish
it.
"""

import re
import sys
import zipfile
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

PARENTHETICAL = re.compile(r"\([A-Z][A-Z0-9 ./&'-]{1,40}\)")
ROMAN = re.compile(r"[IVXLC]+")
UNDERSCORES = re.compile(r"_{2,}")
WORD = re.compile(r"[A-Za-z]+")


def run_text(r):
    """A run's text, with tabs shown as <tab> so a blank has a width."""
    out = []
    for child in r:
        if child.tag == W + "t":
            out.append(child.text or "")
        elif child.tag in (W + "tab", W + "ptab"):
            out.append("<tab>")
    return "".join(out)


def underlined(r):
    u = r.find(f"{W}rPr/{W}u")
    return u is not None and u.get(W + "val", "single") != "none"


def bordered_below(p):
    return p.find(f"{W}pPr/{W}pBdr/{W}bottom") is not None


def mark(text, start, end):
    return f"{text[:start]}[{text[start:end]}]{text[end:]}".strip()


def defines_acronym(text, start, end, preceding=""):
    """True when the parenthetical spells out the initials just before it."""
    letters = [c for c in text[start + 1 : end - 1] if c.isalpha()]
    if not letters:
        return False
    before = WORD.findall(f"{preceding} {text[:start]}")[-len(letters) :]
    if len(before) != len(letters):
        return False
    return [w[0].upper() for w in before] == [c.upper() for c in letters]


def find(path):
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    paragraphs = list(root.iter(W + "p"))
    plain = ["".join(t.text or "" for t in p.iter(W + "t")) for p in paragraphs]
    found = []

    for p_index, p in enumerate(paragraphs, 1):
        previous = plain[p_index - 2] if p_index > 1 else ""
        runs = list(p.iter(W + "r"))
        # Offsets into the paragraph's text, and --slots row numbers, per run.
        text, spans, slot = "", [], 0
        for r in runs:
            piece = run_text(r)
            has_text = any((t.text or "") for t in r.iter(W + "t"))
            slot += 1 if has_text else 0
            spans.append((len(text), len(text) + len(piece), slot if has_text else None))
            text += piece

        def row_of(offset):
            for start, end, s in spans:
                if start <= offset < end:
                    return f"r{s}" if s else "r-"
            return "r-"

        for m in UNDERSCORES.finditer(text):
            found.append((p_index, row_of(m.start()), "underscores", mark(text, m.start(), m.end())))
        for m in PARENTHETICAL.finditer(text):
            inner = text[m.start() + 1 : m.end() - 1]
            if ROMAN.fullmatch(inner) or defines_acronym(text, m.start(), m.end(), previous):
                continue
            found.append((p_index, row_of(m.start()), "parenthetical", mark(text, m.start(), m.end())))
        for r, (start, end, _) in zip(runs, spans):
            piece = text[start:end]
            if piece and underlined(r) and not piece.replace("<tab>", "").strip():
                found.append((p_index, "r-", "underlined-tab", mark(text, start, end)))

        if bordered_below(p) and not text.strip():
            label = next((plain[i] for i in range(p_index, len(plain)) if plain[i].strip()), "")
            found.append((p_index, "r-", "bordered", f"{label.strip()}   <- rule under p{p_index}"))

    for p_index, row, kind, context in found:
        print(f"p{p_index:<4} {row:<4} {kind:<15} {context[:110]}")
    print(f"\n{len(found)} blanks in {len(paragraphs)} paragraphs", file=sys.stderr)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    find(sys.argv[1])
