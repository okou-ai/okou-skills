#!/usr/bin/env python3
"""Infer the typographic style sheet of a PDF.

Usage:
  python3 analyze_pdf.py source.pdf                   # human-readable report
  python3 analyze_pdf.py source.pdf --json out.json   # input for build_reference.py
  python3 analyze_pdf.py source.pdf --body 2           # pick a different body group
  python3 analyze_pdf.py source.pdf --columns 2        # declare a multi-column layout

Requires: pip install pymupdf

A PDF has no style layer, only "draw this glyph at this coordinate in this font
and colour". Spans are therefore grouped on (size, colour, weight) by exact
equality — a group-by on values the file records, not a similarity grouping:
the group with the most characters is taken as body text, and anything larger
becomes a heading candidate, ordered by size.

Which group is prose, and what each larger group means, is not in the file.
That is what the samples in the report are for.

Fonts, sizes, colours and paragraph metrics come out of the coordinates and are
reliable. Heading levels and the bottom margin are not — neither is recorded,
so both have to be settled by reading the report rather than trusting it.
"""
import sys, json, math, re, collections, statistics
import os

try:
    import pymupdf
except ImportError:
    sys.exit("Requires pymupdf: pip install pymupdf")

CM = lambda pt: pt / 72 * 2.54
COMMON_CM = [1.0, 1.27, 1.5, 1.8, 2.0, 2.2, 2.5, 2.54, 3.0, 3.17, 3.5, 4.0]
PAPERS = {"A4": (595.3, 841.9), "A3": (841.9, 1190.6), "A5": (420.9, 595.3),
          "Letter": (612.0, 792.0), "Legal": (612.0, 1008.0)}
BOLD_NAME = re.compile(r"bold|black|heavy|semibold|demibold", re.I)
FILLER_CHARS = set(".·•‧…-_–—~*")


def is_filler(text):
    """True for a leader or rule run: the dot leaders in a table of contents,
    a row of dashes, and similar.

    These are the single biggest source of a wrong body group. A dotted ToC
    packs hundreds of characters into a handful of spans, so counting raw
    characters hands "body text" to the leader dots and every downstream
    metric — line advance, space after, the heading size threshold — is then
    computed against the wrong group.
    """
    t = re.sub(r"\s+", "", text)
    if len(t) < 6:
        return False
    common = collections.Counter(t).most_common(1)[0]
    return common[0] in FILLER_CHARS and common[1] / len(t) >= 0.9


def is_bold(span):
    # bit 4 of the span flags, with the font name as a fallback for fonts that
    # do not set it
    return bool(span.get("flags", 0) & 16) or bool(BOLD_NAME.search(span["font"]))


def collect(doc):
    spans = []
    for page in doc:
        for blk in page.get_text("dict")["blocks"]:
            for line in blk.get("lines", []):
                for s in line["spans"]:
                    if s["text"].strip():
                        spans.append(dict(font=s["font"], size=round(s["size"], 1),
                                          color="%06X" % s["color"], bbox=s["bbox"],
                                          base=round(s["origin"][1], 2),
                                          text=s["text"], page=page.number,
                                          bold=is_bold(s), filler=is_filler(s["text"])))
    return spans


def skey(s):
    """Merge key: size, colour and weight — deliberately not the font name.

    Exact tuple equality, not a distance: two spans group together only when all
    three values match. Size and colour come straight out of the PDF; weight is
    the span's own bold flag, falling back to the font name when it is unset.

    One heading is routinely split across two runs when it mixes scripts, e.g.
    "1.1" in a Latin face and the title text in a CJK face at the same size and
    colour. Keying on the font name would leave them as separate groups that
    both map to the same Word style, which no --map can reconcile.
    """
    return (s["size"], s["color"], s["bold"])


def paper_name(w, h):
    for name, (pw, ph) in PAPERS.items():
        if abs(w - pw) < 3 and abs(h - ph) < 3:
            return name
        if abs(w - ph) < 3 and abs(h - pw) < 3:
            return name + " landscape"
    return None


def snap(cm):
    """Round a measurement to a common layout value; leave it alone if far off."""
    best = min(COMMON_CM, key=lambda c: abs(c - cm))
    return (best, True) if abs(best - cm) < 0.25 else (round(cm, 2), False)


def running_heads(spans, npages, page_h, body_size=None, advance=None):
    """Indices of spans belonging to a running header or footer.

    Multi-page: same y position recurring across pages. Reliable.
    Single page: falls back to "isolated line at the top or bottom", a heuristic
    that the report flags as unreliable.
    """
    if npages >= 2:
        band = lambda s: s["bbox"][1] < page_h * 0.12 or s["bbox"][3] > page_h * 0.88
        by_y = collections.defaultdict(list)
        for i, s in enumerate(spans):
            if band(s):
                by_y[round(s["base"])].append(i)

        need = max(2, math.ceil(npages * 0.6))
        hits = set()
        for y, idx in by_y.items():
            pages = {spans[i]["page"] for i in idx}
            if len(pages) < need:
                continue
            texts = [spans[i]["text"].strip() for i in idx]
            # Chrome repeats itself; content does not. Two forms qualify:
            #   - the same words on most pages (a title, a confidentiality note)
            #   - a short token that counts up (a page number)
            # Position alone is not enough: a section heading printed at the top
            # of every page sits at the same y with different words each time,
            # and dropping it removes real headings from the style groups.
            # Chrome is never set larger than the body text. A section heading
            # printed at the top of every page repeats a position but not a
            # size: dropping it would delete real headings from the groups.
            if body_size is not None and \
                    max(spans[i]["size"] for i in idx) > body_size + 0.4:
                continue
            common = collections.Counter(texts).most_common(1)[0][1]
            repeats = common / len(texts) >= 0.6
            # Page numbers in any of the forms a footer uses: arabic, roman,
            # "3 / 12", and the CJK "page N of M" frame, whose three characters
            # are matched as data rather than written as prose.
            PAGE_TOKEN = r"[\divxlcIVXLC/第页共\-–—.]+"
            numeric = all(len(t) <= 6 and re.fullmatch(PAGE_TOKEN, t) for t in texts)
            # A header showing the current chapter changes its words every page,
            # so neither test above catches it. What it does have is a clear gap
            # to the text block; the first line of a paragraph does not.
            isolated = False
            if advance:
                gaps = []
                for i in idx:
                    pg, sy = spans[i]["page"], spans[i]["base"]
                    below = [s["base"] for s in spans
                             if s["page"] == pg and s["base"] > sy + 1]
                    above = [s["base"] for s in spans
                             if s["page"] == pg and s["base"] < sy - 1]
                    if sy < page_h / 2 and below:
                        gaps.append(min(below) - sy)
                    elif sy >= page_h / 2 and above:
                        gaps.append(sy - max(above))
                isolated = bool(gaps) and statistics.median(gaps) > advance * 1.8
            # Repetition alone is not enough at body size: two pages that
            # carry the same paragraph at the same height repeat a body line
            # too. Body-sized chrome must also stand clear of the text block.
            smaller = body_size is not None and max(spans[i]["size"] for i in idx) < body_size - 0.4
            if numeric or isolated or (repeats and smaller):
                hits |= set(idx)
        return hits, "recurring across pages"

    order = sorted(range(len(spans)), key=lambda i: spans[i]["bbox"][1])
    ys = [spans[i]["bbox"][1] for i in order]
    gaps = [b - a for a, b in zip(ys, ys[1:])]
    if not gaps:
        return set(), None
    typical = statistics.median([g for g in gaps if g > 0.5] or [0])
    hf = set()
    # Chrome is never larger than the body text; a title at the top of a
    # one-page document is isolated too, and must stay a heading.
    small = lambda i: body_size is None or spans[i]["size"] <= body_size + 0.4
    if typical and gaps and gaps[0] > typical * 2.5:
        hf |= {i for i in order if spans[i]["bbox"][1] <= ys[0] + 1 and small(i)}
    if body_size is not None:
        tiny = lambda i: spans[i]["size"] < body_size - 0.4
        hf |= {i for i in order if spans[i]["bbox"][1] < page_h * 0.08 and tiny(i)}
        hf |= {i for i in order if spans[i]["bbox"][3] > page_h * 0.92 and tiny(i)}
    if typical and gaps and gaps[-1] > typical * 2.5:
        hf |= {i for i in order if spans[i]["bbox"][1] >= ys[-1] - 1}
    return hf, "single-page heuristic (unreliable)" if hf else None


def to_lines(spans, columns=1, left=None, right=None):
    """Group spans into lines. PyMuPDF blocks are not paragraphs — in practice
    each block often holds a single line — so paragraphs are segmented here.

    Grouping is by baseline, not by the top of the bounding box. A heading that
    mixes scripts puts "1.1" and the CJK title on one baseline but at different
    box tops, because the two faces have different ascents; keying on the top
    splits one heading into two lines, halves the sample for its spacing, and
    turns the gaps that straddle the split into negative numbers.

    Multi-column layouts share one baseline grid, so side-by-side lines from
    different columns land in the same group and merge into one full-width
    line: a real line is lost, and the merged line's right edge is the *other*
    column's, which makes the measured gutter negative. A group is therefore
    split wherever the whitespace between two spans straddles a column
    boundary. Text that genuinely crosses a boundary — a title spanning the
    page — has no gap there and stays one line.
    """
    bounds = []
    if columns > 1 and left is not None and right is not None:
        w = (right - left) / columns
        bounds = [left + w * k for k in range(1, columns)]

    byline = collections.defaultdict(list)
    for s in spans:
        byline[(s["page"], s["base"])].append(s)
    out = []
    for (pg, y), ss in byline.items():
        ss.sort(key=lambda s: s["bbox"][0])
        runs, cur = [], [ss[0]]
        for prev, s in zip(ss, ss[1:]):
            if any(prev["bbox"][2] <= b <= s["bbox"][0] for b in bounds):
                runs.append(cur)
                cur = []
            cur.append(s)
        runs.append(cur)
        for run in runs:
            x0 = min(s["bbox"][0] for s in run)
            line = dict(page=pg, y=y, x0=round(x0, 1),
                        x1=round(max(s["bbox"][2] for s in run), 1),
                        key=skey(run[0]),
                        text="".join(s["text"] for s in run).strip(),
                        filler=all(s["filler"] for s in run))
            if bounds:
                line["col"] = sum(1 for b in bounds if x0 >= b)
            out.append(line)
    out.sort(key=lambda l: (l["page"], l["y"]))
    return out


def _sfnt_metrics(buf):
    import struct
    off = 0
    if buf[:4] == b"ttcf":
        off = struct.unpack(">I", buf[12:16])[0]
    if buf[off:off + 4] not in (b"\0\1\0\0", b"OTTO", b"true"):
        return None
    n = struct.unpack(">H", buf[off + 4:off + 6])[0]
    tables = {}
    for i in range(n):
        tag, _, toff, ln = struct.unpack(">4sIII", buf[off + 12 + 16 * i: off + 28 + 16 * i])
        tables[tag] = toff
    upm = struct.unpack(">H", buf[tables[b"head"] + 18: tables[b"head"] + 20])[0]
    asc, desc = struct.unpack(">hh", buf[tables[b"hhea"] + 4: tables[b"hhea"] + 8])
    return asc / upm, abs(desc) / upm


_METRICS_CACHE = {}


def font_metrics(doc, fontname):
    """(ascender, descender) in em from the font's hhea table, which is the
    box Word and LibreOffice lay a line out in. PyMuPDF's span bbox uses the
    OS/2 typo values instead, and for Noto Sans CJK the two differ by 0.28em.

    Read from the embedded font when it is an sfnt. Typst embeds CJK faces as
    bare CFF and LibreOffice as Type1, neither of which carries hhea, so fall
    back to the same face installed on this machine: that is the file Word
    will use to lay the output out anyway. None when neither is readable."""
    import subprocess
    want = fontname.split("+")[-1].split("-Identity")[0]
    if want in _METRICS_CACHE:
        return _METRICS_CACHE[want]
    res = None
    for pno in range(min(doc.page_count, 4)):
        for entry in doc[pno].get_fonts():
            if entry[3].split("+")[-1].split("-Identity")[0] != want:
                continue
            try:
                res = _sfnt_metrics(doc.extract_font(entry[0])[3])
            except Exception:
                res = None
            break
        if res:
            break
    if res is None:
        family = want.split("-")[0]
        style = want.split("-")[1] if "-" in want else "Regular"
        try:
            hit = subprocess.run(["fc-match", "-f", "%{file}|%{family}", f"{family}:style={style}"],
                                 capture_output=True, text=True, timeout=10).stdout
            path, fam = hit.split("|", 1)
            norm = lambda x: re.sub(r"[^a-z0-9]", "", x.lower())
            if any(norm(family).startswith(norm(f)[:8]) or norm(f).startswith(norm(family)[:8])
                   for f in fam.split(",")):
                res = _sfnt_metrics(open(path, "rb").read())
        except Exception:
            res = None
    _METRICS_CACHE[want] = res
    return res


def fit_top(spans, npages):
    """The text-block top, solved rather than measured.

    A glyph box starts below the text block by a fixed fraction of the font
    size, so the topmost line of a page reports a margin that is too small, and
    by a different amount for every font size. Two sizes are two equations:
        y0 = T + a * size
    Fitting y0 on size gives the intercept T, the real top margin, with the
    per-font offset a falling out as the slope.

    Returns None when every page starts at the same size, which leaves the two
    unknowns inseparable, or when the fit contradicts itself.
    """
    top = {}
    for sp in spans:
        cur = top.get(sp["page"])
        if cur is None or sp["bbox"][1] < cur[1]:
            top[sp["page"]] = (sp["size"], sp["bbox"][1])
    pts = list(top.values())
    if len({z for z, _ in pts}) < 2:
        return None
    n = len(pts)
    mx = sum(z for z, _ in pts) / n
    my = sum(y for _, y in pts) / n
    den = sum((z - mx) ** 2 for z, _ in pts)
    if not den:
        return None
    sl = sum((z - mx) * (y - my) for z, y in pts) / den
    T = my - sl * mx
    # y grows downward, and a glyph box reaches above the block top by its
    # ascent, so the solved top is below every box top by a fraction of one
    # em: the slope is a small negative number and T sits between the highest
    # box and one em under it. Anything else means the pages do not share a
    # block top and the fit is meaningless.
    hi, big = min(y for _, y in pts), max(z for z, _ in pts)
    if not (-0.5 < sl < 0) or not (hi <= T <= hi + big):
        return None
    return T


def measure_spacing(lines, body_key, col_left, col_right):
    """Line advance, space after, first-line indent, heading spacing, alignment."""
    B = [l for l in lines if l["key"] == body_key and not l["filler"]]
    if len(B) < 4:
        return {}, {}

    # Line advance = the mode of the y delta between consecutive body lines.
    # Paragraph gaps are the minority, so the mode excludes them for free.
    dl = [round(b["y"] - a["y"], 1) for a, b in zip(B, B[1:])
          if a["page"] == b["page"] and 0 < b["y"] - a["y"] < body_key[0] * 3]
    if not dl:
        return {}, {}
    adv = collections.Counter(dl).most_common(1)[0][0]

    # A y delta clearly larger than the line advance starts a new paragraph.
    # So does a column break: y jumps back to the top of the page there, which
    # is not a larger delta but a negative one.
    starts = {0}
    for i, (a, b) in enumerate(zip(B, B[1:]), start=1):
        if a["page"] != b["page"] or a.get("col") != b.get("col") \
                or (b["y"] - a["y"]) > adv * 1.25:
            starts.add(i)

    # Indent is measured from each line's own column edge. An absolute x mixes
    # the columns: the mode over paragraph starts can land in one column while
    # the mode over continuations lands in another, and subtracting them gives
    # a column offset rather than an indent. On the two-column fixture that
    # cancelled to exactly 0.0 and the real 2em indent was lost in silence.
    per_col = collections.defaultdict(collections.Counter)
    for l in B:
        per_col[l.get("col", 0)][l["x0"]] += 1
    # Most lines in a column are continuations, so the mode is its left edge.
    edge = {c: cc.most_common(1)[0][0] for c, cc in per_col.items()}
    relx = lambda l: round(l["x0"] - edge.get(l.get("col", 0), 0), 1)

    sx = collections.Counter(relx(B[i]) for i in starts)
    cx = collections.Counter(relx(B[i]) for i in range(len(B)) if i not in starts)
    indent = None
    if sx and cx:
        v = sx.most_common(1)[0][0] - cx.most_common(1)[0][0]
        indent = round(v, 1) if v > 2 else 0.0

    # A body line that follows a heading has its previous *body* line two or
    # three lines up; that distance is not a paragraph gap. Only pairs that
    # are adjacent in the page's line order count.
    pos = {id(l): j for j, l in enumerate(lines)}
    gaps = [round(B[i]["y"] - B[i - 1]["y"] - adv, 1) for i in sorted(starts)
            if i > 0 and B[i]["page"] == B[i - 1]["page"] and B[i]["y"] - B[i - 1]["y"] < adv * 4
            and pos[id(B[i])] - pos[id(B[i - 1])] == 1]
    # None, not 0.0: "no usable sample" and "measured as zero" are different
    # claims. Every paragraph here may be followed by a table, a list or a
    # heading, in which case nothing was measured and the builder must not
    # write a value it never obtained.
    # Justified or ragged right. A line that ends a paragraph stops wherever
    # the sentence does in either case, so only the lines that continue into
    # another line carry the evidence: under justification they all reach the
    # column edge, and under ragged right almost none do.
    inner = [B[i] for i in range(len(B) - 1) if (i + 1) not in starts
             and B[i]["page"] == B[i + 1]["page"]
             and B[i].get("col") == B[i + 1].get("col")]
    align = None
    if len(inner) >= 4:
        right = collections.Counter(l["x1"] for l in inner).most_common(1)[0]
        align = "both" if right[1] * 2 > len(inner) else "left"

    body = {"line_advance_pt": adv, "line_ratio": round(adv / body_key[0], 2),
            "align": align, "align_samples": len(inner),
            "space_after_pt": round(statistics.median(gaps), 1) if gaps else None,
            "space_after_samples": len(gaps),
            "first_line_indent_pt": indent,
            "first_line_indent_em": round(indent / body_key[0], 2) if indent else 0.0}

    col_mid = (col_left + col_right) / 2
    heads = {}

    # Baseline-to-baseline distance is what the PDF actually records. Turning it
    # into Word's before/after needs a model of the natural stacking, and there
    # is no exact one: the 15.9pt advance measured here is the generator's
    # leading setting, not a consequence of the font metrics (this document's
    # CJK face reports ascender - descender = 1.0, i.e. 10.5pt for a 15.9pt
    # advance). So state one model and use it in both directions.
    #
    # Natural gap between two lines = the mean of their line advances. A
    # group's own advance is measured when it wraps, and scaled from the body
    # otherwise, since a heading is rarely more than one line.
    def adv_of(key):
        L = [l for l in lines if l["key"] == key and not l["filler"]]
        dl = [round(b["y"] - a["y"], 1) for a, b in zip(L, L[1:])
              if a["page"] == b["page"] and 0 < b["y"] - a["y"] < key[0] * 3]
        if dl:
            c = collections.Counter(dl).most_common(1)[0]
            if c[1] >= 2:
                return c[0]
        return adv * key[0] / body_key[0]

    # A gap this large is not paragraph spacing, it is white space on a cover or
    # section-break page. Left in, the median lands in the hundreds of points.
    cap = adv * 6
    # A heading is larger than the body, or the body's size set apart by
    # weight or colour on lines that stop well short of the column edge:
    # a bold run-in inside a paragraph fills its line, a heading does not.
    colw = col_right - col_left
    def stands_apart(key):
        L = [l for l in lines if l["key"] == key and not l["filler"]]
        if not L or key == body_key:
            return False
        if key[0] > body_key[0] + 0.4:
            return True
        if key[0] < body_key[0] - 0.4 or (key[1] == body_key[1] and key[2] == body_key[2]):
            return False
        return statistics.median(l["x1"] - l["x0"] for l in L) < 0.7 * colw and len(L) * 4 < len(B)
    keys = {l["key"] for l in lines if stands_apart(l["key"])}
    natural = lambda a, b: (adv_of(a["key"]) + adv_of(b["key"])) / 2
    # Word adds space-after and space-before across a paragraph boundary
    # (LibreOffice takes the larger; Typst the larger). One gap must
    # therefore be written on one side only:
    #   heading -> body     : the heading's after
    #   anything -> heading : the heading's before, less whatever the
    #                         preceding paragraph already carries as after
    after_of = {body_key: body["space_after_pt"] or 0.0}
    for key in keys:
        idx = [i for i, l in enumerate(lines) if l["key"] == key]
        after, raw_a, to_head = [], [], False
        for i in idx:
            if i + 1 < len(lines) and lines[i + 1]["page"] == lines[i]["page"] \
                    and lines[i + 1]["key"] != key:
                g = lines[i + 1]["y"] - lines[i]["y"]
                if g > cap:
                    continue
                if lines[i + 1]["key"] == body_key:
                    raw_a.append(g)
                    after.append(g - natural(lines[i], lines[i + 1]))
                elif lines[i + 1]["key"] in keys:
                    to_head = True
        heads[key] = {
            "space_after_pt": (round(max(0, statistics.median(after)), 1) if after
                               else 0.0 if to_head else None),
            "baseline_gap_after_pt": round(statistics.median(raw_a), 1) if raw_a else None,
        }
        after_of[key] = heads[key]["space_after_pt"] or 0.0
    for key in keys:
        idx = [i for i, l in enumerate(lines) if l["key"] == key]
        mine = adv_of(key)
        before, raw_b = [], []
        for i in idx:
            if i > 0 and lines[i]["page"] == lines[i - 1]["page"] and lines[i - 1]["key"] != key:
                g = lines[i]["y"] - lines[i - 1]["y"]
                if g <= cap:
                    raw_b.append(g)
                    before.append(g - natural(lines[i - 1], lines[i])
                                  - after_of.get(lines[i - 1]["key"], 0.0))
        off = statistics.median([abs((lines[i]["x0"] + lines[i]["x1"]) / 2 - col_mid) for i in idx])
        left_off = statistics.median([abs(lines[i]["x0"] - col_left) for i in idx])
        # Never preceded by anything on its page: it sits at the top margin,
        # so the space before it is zero. Left unwritten, pandoc's own value
        # (24pt on Title) pushes the whole first page down.
        page_first = {}
        for i in idx:
            page_first.setdefault(lines[i]["page"], i)
        first_on_page = all(i == 0 or lines[i]["page"] != lines[i - 1]["page"]
                            for i in page_first.values())
        heads[key].update({
            "first_on_page_ys": ([[lines[i]["y"], key[0]] for i in page_first.values()]
                                 if first_on_page else None),
            "space_before_pt": (round(max(0, statistics.median(before)), 1) if before
                                else 0.0 if first_on_page else None),
            "baseline_gap_before_pt": round(statistics.median(raw_b), 1) if raw_b else None,
            "own_line_advance_pt": round(mine, 1),
            "align": "center" if off < 6 and left_off > 12 else "left",
        })
    return body, heads


def hf_distance(doc, spans, hf, H, which):
    """Distance from the page edge to the running head's line-box edge, which
    is what w:pgMar w:header / w:footer mean. Line box = baseline -/+ the
    font's hhea ascender/descender; the glyph box when the font is unreadable."""
    top = [spans[i] for i in hf if spans[i]["bbox"][1] < H / 2]
    bot = [spans[i] for i in hf if spans[i]["bbox"][3] >= H / 2]
    if which == "header":
        if not top:
            return None
        s = min(top, key=lambda x: x["base"])
        fm = font_metrics(doc, s["font"])
        return round(s["base"] - fm[0] * s["size"] if fm else s["bbox"][1], 1)
    if not bot:
        return None
    s = max(bot, key=lambda x: x["base"])
    fm = font_metrics(doc, s["font"])
    return round(H - (s["base"] + fm[1] * s["size"]) if fm else H - s["bbox"][3], 1)


def hf_spec(doc, spans, hf, H, col_left, col_right, which):
    """What set_header_footer.py needs to put the running head back: its text
    with tab stops between left / centre / right groups, {PAGE} where the page
    number goes, and its size and colour. Built from the first page that
    carries it; the page number is the token that differs on the next page."""
    band = [spans[i] for i in hf if (spans[i]["bbox"][1] < H / 2) == (which == "header")]
    if not band:
        return None
    pages = sorted({s["page"] for s in band})
    def compose(pg):
        row = sorted([s for s in band if s["page"] == pg], key=lambda s: s["bbox"][0])
        # Spans that nearly touch are one piece of text ("第 ", "1", " 页");
        # a piece is classified as a whole, by where it sits.
        pieces = []
        for s in row:
            if pieces and s["bbox"][0] - pieces[-1]["x1"] < s["size"] * 1.0:
                gap = s["bbox"][0] - pieces[-1]["x1"]
                pieces[-1]["text"] += (" " if gap > s["size"] * 0.2 and not pieces[-1]["text"].endswith(" ")
                                       and not s["text"].startswith(" ") else "") + s["text"]
                pieces[-1]["x1"] = s["bbox"][2]
            else:
                pieces.append({"text": s["text"], "x0": s["bbox"][0], "x1": s["bbox"][2]})
        mid = (col_left + col_right) / 2
        groups = {"l": [], "c": [], "r": []}
        for pc in pieces:
            if abs((pc["x0"] + pc["x1"]) / 2 - mid) < 0.08 * (col_right - col_left):
                groups["c"].append(pc)
            elif pc["x0"] - col_left < col_right - pc["x1"]:
                groups["l"].append(pc)
            else:
                groups["r"].append(pc)
        parts = [" ".join(x["text"].strip() for x in groups[k]).strip() for k in ("l", "c", "r")]
        return parts, row
    parts0, row0 = compose(pages[0])
    if len(pages) > 1:
        parts1, _ = compose(pages[1])
        parts0 = [re.sub(r"\d+", "{PAGE}", a, count=1) if a != b and re.search(r"\d", a) else a
                  for a, b in zip(parts0, parts1)]
    if parts0[1] and (parts0[0] or parts0[2]):
        text, align = "\t".join(parts0), "left"          # left / centre / right stops
    elif parts0[0] and parts0[2]:
        text, align = parts0[0] + "\t" + parts0[2], "left"   # left / right stops
    else:
        text, align = parts0[0], "left"
    if not parts0[0] and parts0[1] and not parts0[2]:
        text, align = parts0[1], "center"
    if not parts0[0] and not parts0[1] and parts0[2]:
        text, align = parts0[2], "right"
    lead = row0[0]
    return {"text": text, "align": align, "size": lead["size"], "color": lead["color"],
            "font": lead["font"].split("+")[-1], "page_number": "{PAGE}" in text}


def _hex(rgb):
    return "%02X%02X%02X" % tuple(int(round(c * 255)) for c in rgb[:3])


def measure_tables(doc):
    """Borders and shading of the first table found: outer and inside rules
    as (colour, width pt), the header row's fill and weight, and the fill
    of banded rows. LibreOffice and Word export rules as stroked lines and
    shading as filled rectangles; both are read from the page's drawings."""
    for page in doc:
        try:
            import io, contextlib
            with contextlib.redirect_stdout(io.StringIO()):   # PyMuPDF's upsell line
                found = page.find_tables()
        except Exception:
            return None
        tabs = [t for t in found.tables if t.row_count >= 2 and t.col_count >= 2]
        if not tabs:
            continue
        tb = tabs[0]
        bb = pymupdf.Rect(tb.bbox)
        outer = bb + (-3, -3, 3, 3)
        row0 = pymupdf.Rect(tb.rows[0].bbox)
        edges = {"top": [], "bottom": [], "left": [], "right": [], "insideH": [], "insideV": [], "header_bottom": []}
        fills_head, fills_body = collections.Counter(), collections.Counter()
        for dr in page.get_drawings():
            col = dr.get("color"); w = round(dr.get("width") or 0, 2)
            for it in dr["items"]:
                if it[0] == "l" and (outer.contains(it[1]) or outer.contains(it[2])) and col and w:
                    a, b = it[1], it[2]
                    if abs(a.y - b.y) < 0.5:
                        y = a.y
                        k = ("top" if abs(y - bb.y0) < 2 else "bottom" if abs(y - bb.y1) < 2
                             else "header_bottom" if abs(y - row0.y1) < 2 else "insideH")
                    else:
                        x = a.x
                        k = "left" if abs(x - bb.x0) < 2 else "right" if abs(x - bb.x1) < 2 else "insideV"
                    edges[k].append((_hex(col), w))
                elif it[0] == "re" and outer.intersects(it[1]) and min(it[1].width, it[1].height) >= 1.6:
                    f = dr.get("fill")
                    if f and _hex(f) != "FFFFFF":
                        (fills_head if it[1].intersects(row0) and it[1].y0 >= row0.y0 - 1 and it[1].y1 <= row0.y1 + 1
                         else fills_body)[_hex(f)] += 1
        rule = lambda k: (collections.Counter(edges[k]).most_common(1)[0][0] if edges[k] else None)
        head_bold = None
        spans = [sp for b in page.get_text("dict", clip=row0)["blocks"] for l in b.get("lines", []) for sp in l["spans"] if sp["text"].strip()]
        if spans:
            head_bold = all(is_bold(sp) for sp in spans)
        nrows = tb.row_count
        band = fills_body.most_common(1)[0] if fills_body else None
        return {
            "page": page.number + 1, "rows": nrows, "cols": tb.col_count,
            "top": rule("top"), "bottom": rule("bottom"), "left": rule("left"), "right": rule("right"),
            "insideH": rule("insideH"), "insideV": rule("insideV"),
            "header_bottom": rule("header_bottom"),
            "header_fill": fills_head.most_common(1)[0][0] if fills_head else None,
            "header_bold": head_bold,
            # shading on some but not all body rows is banding
            "band_fill": band[0] if band and band[1] < (nrows - 1) * tb.col_count else None,
            "body_fill": band[0] if band and band[1] >= (nrows - 1) * tb.col_count else None,
        }
    return None


def header_image(doc, H):
    """An image that sits in the header band on most pages: its xref, box and
    where it hangs (left / centre / right of the page)."""
    seen = collections.Counter(); boxes = {}
    for page in doc:
        for info in page.get_image_info(xrefs=True):
            r = pymupdf.Rect(info["bbox"])
            if r.y1 < H * 0.15 and info.get("xref"):
                key = (info["xref"], round(r.x0), round(r.y0))
                seen[key] += 1; boxes[key] = r
    if not seen:
        return None
    key, n = seen.most_common(1)[0]
    if n < max(1, math.ceil(doc.page_count * 0.6)):
        return None
    r = boxes[key]; W = doc[0].rect.width
    mid = (r.x0 + r.x1) / 2
    align = "center" if abs(mid - W / 2) < W * 0.08 else ("left" if r.x0 < W / 2 else "right")
    return {"xref": key[0], "x_pt": round(r.x0, 1), "y_pt": round(r.y0, 1),
            "w_pt": round(r.width, 1), "h_pt": round(r.height, 1), "align": align}


def analyze(path, body_pick=None, columns=1):
    doc = pymupdf.open(path)
    page = doc[0]
    W, H = page.rect.width, page.rect.height
    spans = collect(doc)
    if not spans:
        sys.exit("No text layer in this PDF — it is probably a scan. OCR it first.")

    tagged = doc.xref_get_key(doc.pdf_catalog(), "StructTreeRoot")[0] != "null"
    # Two passes: estimate the body size from every span first, so the running
    # head test can use "never larger than the body" as its size guard.
    prelim = collections.Counter()
    for s in spans:
        if not s["filler"]:
            prelim[s["size"]] += len(s["text"].strip())
    body_size = prelim.most_common(1)[0][0] if prelim else None
    pb = sorted((s["page"], s["base"]) for s in spans
                if s["size"] == body_size and not s["filler"])
    pdl = [round(b[1] - a[1], 1) for a, b in zip(pb, pb[1:])
           if a[0] == b[0] and 0 < b[1] - a[1] < (body_size or 12) * 3]
    advance = collections.Counter(pdl).most_common(1)[0][0] if pdl else None
    hf, hf_method = running_heads(spans, doc.page_count, H, body_size, advance)
    body_spans = [s for i, s in enumerate(spans) if i not in hf]
    content = [s for s in body_spans if not s["filler"]]
    filler_count = len(body_spans) - len(content)

    chars = collections.Counter()
    fonts = collections.defaultdict(collections.Counter)
    for s in content:
        chars[skey(s)] += len(s["text"].strip())
        fonts[skey(s)][s["font"]] += len(s["text"].strip())
    if not chars:
        sys.exit("Every span looks like a leader or rule. Nothing to infer.")

    # Ranked by character count, nothing more. Which group is body text is a
    # reading decision, not an arithmetic one: a dense table or an index can
    # hold more characters than the prose around it. The report prints every
    # candidate with its sample text so the caller can judge and pass --body.
    ranked = [k for k, _ in chars.most_common()]
    body = ranked[0]
    if body_pick is not None:
        if not 1 <= body_pick <= len(ranked):
            sys.exit(f"--body must be between 1 and {len(ranked)}")
        body = ranked[body_pick - 1]
    heads = sorted([k for k in chars if k[0] > body[0] + 0.4], key=lambda k: -k[0])

    font_of = lambda k: fonts[k].most_common(1)[0][0]

    def sample(key):
        return next((s["text"].strip() for s in content if skey(s) == key), "")

    # Left and right edges are both modes, per column. Taking the extreme
    # instead loses to a single outlier: a justified line reports a right edge
    # a few points past the column, because the span box carries the tracking
    # added to the last glyph. That one span moved the measured right margin
    # by 4.7pt on the fixture and, in a two-column layout, shrank the gutter
    # by the same amount.
    def far_edge(xs):
        """The right-hand text edge from the x where lines end.

        Justified text piles up on one x, and anything past it is overshoot.
        Ragged-right text has no pile-up at all, and then the longest line is
        the only estimate there is. Which case this is comes from the counts:
        a justified edge outnumbers everything to the right of it put together.
        """
        c = collections.Counter(xs)
        mode, n = c.most_common(1)[0]
        beyond = sum(v for k, v in c.items() if k > mode)
        return mode if n > beyond else max(c)

    def edges(ss):
        # A first-line indent on two-line paragraphs puts half the lines at the
        # indented x; the text edge is the leftmost x a substantial share of
        # lines start at, not the single most common one.
        c = collections.Counter(round(s["bbox"][0], 1) for s in ss)
        top = max(c.values())
        left = min(k for k, v in c.items() if v >= 0.3 * top)
        return (left, far_edge([round(s["bbox"][2], 1) for s in ss]))

    # Bootstrap the column bands from the extremes; a few points of overshoot
    # cannot move a band boundary, which sits half a column away.
    raw_l = min(s["bbox"][0] for s in body_spans)
    raw_r = max(s["bbox"][2] for s in body_spans)
    band_edges = None
    if columns > 1:
        # Column starts are the most common line-start x values that sit at
        # least 60pt apart; equal division would misfile the wide column's
        # lines when the columns are unequal.
        c = collections.Counter(round(s["bbox"][0]) for s in body_spans)
        starts = []
        for x, _ in c.most_common():
            if all(abs(x - y) >= 60 for y in starts):
                starts.append(x)
            if len(starts) == columns:
                break
        starts.sort()
        per_band = collections.defaultdict(list)
        for s in body_spans:
            k = max((i for i, x in enumerate(starts) if s["bbox"][0] >= x - 3), default=0)
            per_band[k].append(s)
        band_edges = [edges(per_band[k]) for k in sorted(per_band)]
        left_pt, right_edge = band_edges[0][0], band_edges[-1][1]
    else:
        left_pt, right_edge = edges(body_spans)
    right_pt = W - right_edge
    # Top: solve it from two font sizes where the document offers them, and
    # fall back to the highest glyph box otherwise. The fallback always reads
    # a little small, because a glyph box starts below the text block.
    not_first = [s for s in body_spans if s["page"] > 0]
    top_src = not_first or body_spans
    top_fit = fit_top(body_spans, doc.page_count)
    top_pt = top_fit if top_fit is not None else min(s["bbox"][1] for s in top_src)
    # Word puts the first baseline at top margin + the font's hhea ascender.
    # Solving the margin from the baselines with that ascender lands the
    # first line where the PDF has it; the glyph-box fit above reads it
    # 0.2-0.4em higher for every CJK face.
    fm = font_metrics(doc, body_spans[0]["font"]) if body_spans else None
    top_metric = None
    if fm:
        # First content line of each page, whatever its size: a page that
        # opens with a heading starts at the margin too. No page can start
        # above the margin, so the smallest value across pages is the margin;
        # a cover title pushed down the page is simply not the smallest.
        firsts = {}
        for i, sp in enumerate(spans):
            if i in hf or sp["filler"]:
                continue
            if sp["page"] not in firsts or sp["base"] < firsts[sp["page"]]["base"]:
                firsts[sp["page"]] = sp
        cand = []
        for f in firsts.values():
            m = font_metrics(doc, f["font"]) or fm
            cand.append(f["base"] - m[0] * f["size"])
        if cand:
            top_metric = min(cand)
            top_pt, top_fit = top_metric, top_metric
    # Bottom: page breaks rarely land exactly at the bottom of the text block,
    # so the measurement is always >= the real value. Take the minimum across
    # non-final pages as the tightest upper bound.
    last = doc.page_count - 1
    per_page = collections.defaultdict(float)
    for s in body_spans:
        if s["page"] != last:
            per_page[s["page"]] = max(per_page[s["page"]], s["bbox"][3])
    bottom_bound_pt = (H - max(per_page.values())) if per_page else None

    top_cm = round(CM(top_pt), 2) if top_fit is not None else snap(CM(top_pt))[0]
    bottom_suggested, geom_notes = None, []
    if filler_count:
        geom_notes.append(f"{filler_count} leader or rule spans were excluded from "
                          f"grouping; counting them would hand the body group to a "
                          f"dotted table of contents")
    if not not_first:
        geom_notes.append("single page: the top margin may include a title block "
                          "and read too large")
    if bottom_bound_pt is None:
        geom_notes.append("single page: the bottom margin cannot be measured at all")
    else:
        bound_cm = CM(bottom_bound_pt)
        if top_cm <= bound_cm:
            bottom_suggested = top_cm
            geom_notes.append(
                f"the bottom margin is an upper bound (real value <= {bound_cm:.2f}cm). "
                f"The top margin {top_cm}cm fits under it, so the layout is consistent "
                f"with being vertically symmetric — that value is the suggestion")
        else:
            bottom_suggested = snap(bound_cm)[0]
            geom_notes.append(
                f"the bottom margin is an upper bound (real value <= {bound_cm:.2f}cm), "
                f"and the top margin {top_cm}cm EXCEEDS it — this layout is NOT "
                f"vertically symmetric, so do not mirror the top margin. The suggestion "
                f"is the rounded bound; pass --bottom to override it")

    col_right = W - right_pt
    lines = to_lines(body_spans, columns, left_pt, col_right)
    # Same size as the body but set apart by weight or colour, on lines that
    # stop well short of the column: a heading, not a bold run-in.
    colw = col_right - left_pt
    nbody = sum(1 for l in lines if l["key"] == body)
    for k in chars:
        if k in heads or k == body or abs(k[0] - body[0]) > 0.4 or (k[1] == body[1] and k[2] == body[2]):
            continue
        L = [l for l in lines if l["key"] == k and not l["filler"]]
        if L and statistics.median(l["x1"] - l["x0"] for l in L) < 0.7 * colw and len(L) * 4 < nbody:
            heads.append(k)
    heads.sort(key=lambda k: (-k[0], not k[2]))

    # Evidence for the column decision, not a verdict. Bands of line-start x
    # separate for a multi-column layout and for a table alike, so the count
    # alone decides nothing — the report says to look at a rendered page.
    xs = sorted(l["x0"] for l in lines)
    bands = [[xs[0]]] if xs else []
    for a, b in zip(xs, xs[1:]):
        (bands[-1] if b - a < 30 else bands.append([b]) or bands[-1]).append(b)
    band_info = [{"x": round(sum(b) / len(b), 1), "lines": len(b)}
                 for b in bands if len(b) >= 3]

    # With the column count declared, order lines within a column instead of
    # straight down the page. Otherwise the line before a heading at the top of
    # column 2 is the last line of column 1, which sits lower on the page and
    # turns every heading gap into noise.
    if columns > 1:
        lines.sort(key=lambda l: (l["page"], l["col"], l["y"]))
        # Column edges come only from lines that stay inside one column. A
        # title or abstract set across the full width belongs to no column;
        # letting it set column 1's right edge puts that edge past where
        # column 2 starts, and the gutter comes out negative.
        span_w = (col_right - left_pt) / columns
        bounds = [left_pt + span_w * k for k in range(1, columns)]
        per_col = collections.defaultdict(list)
        for l in lines:
            if not any(l["x0"] < b < l["x1"] for b in bounds):
                per_col[l["col"]].append(l)
        box = [(collections.Counter(l["x0"] for l in v).most_common(1)[0][0],
                collections.Counter(l["x1"] for l in v).most_common(1)[0][0])
               for _, v in sorted(per_col.items())]
        col_gap = round(statistics.median(
            [b[0] - a[1] for a, b in zip(box, box[1:])]), 1) if len(box) > 1 else None
        col_width = round(statistics.median([e[1] - e[0] for e in box]), 1) if box else None
    else:
        col_gap = col_width = None
    if band_edges and len(band_edges) > 1:
        col_gap = round(statistics.median([b[0] - a[1] for a, b in zip(band_edges, band_edges[1:])]), 1)
        col_width = round(statistics.median([r - l for l, r in band_edges]), 1)
    body_sp, head_sp = measure_spacing(lines, body, left_pt, col_right)
    # A heading that opens its page sits where the top margin plus its own
    # ascender puts it; anything beyond that is space-before (a cover title
    # 200pt down the page), measured against the margin rather than a
    # preceding line.
    for _k, _h in head_sp.items():
        if _h.get("first_on_page_ys"):
            _asc = (fm[0] if fm else 0.88)
            _off = [y - top_pt - _asc * sz for y, sz in _h["first_on_page_ys"]]
            _h["space_before_pt"] = round(max(0.0, statistics.median(_off)), 1)
    leading = body_sp.get("line_advance_pt")

    result = {
        "file": path, "pages": doc.page_count,
        "page": {"w_pt": round(W, 1), "h_pt": round(H, 1),
                 "w_cm": round(CM(W), 2), "h_cm": round(CM(H), 2),
                 "paper": paper_name(W, H)},
        "tagged": tagged,
        "filler_spans_excluded": filler_count,
        "columns": columns,
        "column_gap_pt": col_gap,
        "column_width_pt": col_width,
        "column_evidence": band_info,
        "body_candidates": [{"rank": i, "font": font_of(k), "size": k[0], "color": k[1],
                             "bold": k[2], "chars": chars[k],
                             "lines": len({(s["page"], s["base"])
                                           for s in content if skey(s) == k}),
                             "pages": len({s["page"] for s in content if skey(s) == k}),
                             "sample": sample(k), "chosen": k == body}
                            for i, k in enumerate(ranked[:8], 1)],
        "body_pick": body_pick,
        "body": dict({"font": font_of(body), "size": body[0], "color": body[1],
                      "bold": body[2], "leading_pt": leading}, **body_sp),
        "headings": [dict({"level": i, "font": font_of(h), "size": h[0], "color": h[1],
                           "bold": h[2], "sample": sample(h)}, **head_sp.get(h, {}))
                     for i, h in enumerate(heads, 1)],
        "margins_measured_cm": {k: (round(CM(v), 2) if v is not None else None) for k, v in
                                (("left", left_pt), ("right", right_pt),
                                 ("top", top_pt), ("bottom", bottom_bound_pt))},
        "margins_suggested_cm": {"left": round(CM(left_pt), 2), "right": round(CM(right_pt), 2),
                                 "top": top_cm, "bottom": bottom_suggested},
        # Every heading line in reading order, not just one sample per group.
        # The template carries no body content at all, so this outline is the
        # only record of how the source document was actually organised — and
        # that is what a request to "write another one of these" needs.
        "outline": [{"level": lv, "text": l["text"], "page": l["page"] + 1}
                    for l in lines if l["text"] and not l["filler"]
                    for lv in [next((i for i, h in enumerate(heads, 1)
                                     if h == l["key"]), None)] if lv],
        "geometry_notes": geom_notes,
        "table": measure_tables(doc),
        "header_image": header_image(doc, H),
        "column_edges_pt": ([[round(l, 1), round(r, 1)] for l, r in band_edges]
                            if band_edges else None),
        "columns_unequal": (bool(band_edges) and
                            max(r - l for l, r in band_edges) > 1.05 * min(r - l for l, r in band_edges)),
        "running_heads": sorted({s["text"].strip() for i, s in enumerate(spans) if i in hf})[:6],
        # Where the running head and foot actually sit, so a header added later
        # lands where the source put it rather than at Word's default 708 twips.
        "header": hf_spec(doc, spans, hf, H, left_pt, W - right_pt, "header"),
        "footer": hf_spec(doc, spans, hf, H, left_pt, W - right_pt, "footer"),
        "header_pt": (lambda t, im: (min(v for v in (t, im and im["y_pt"]) if v is not None)
                                      if (t is not None or im) else None))(
            hf_distance(doc, spans, hf, H, "header"), header_image(doc, H)),
        "footer_pt": hf_distance(doc, spans, hf, H, "footer"),
        "font_metrics_hhea": ([round(v, 3) for v in fm] if fm else None),
        "running_heads_method": hf_method,
    }
    doc.close()
    return result, chars, body


def report(r, chars, body):
    p = r["page"]
    print(f"===== {r['file']} ({r['pages']} pages) =====\n")
    print(f"[page] {p['w_cm']} x {p['h_cm']} cm"
          + (f"  = {p['paper']}" if p["paper"] else "  (non-standard size)"))
    print(f"[structure tree] " + ("present — read heading levels from /StructTreeRoot "
                                  "instead of guessing from font size"
                                  if r["tagged"] else "absent — the PDF records no roles "
                                  "at all, so levels come from the sample text"))
    if r["running_heads"]:
        print(f"[running head/foot] {r['running_heads_method']}: "
              f"{' | '.join(r['running_heads'])}  -> excluded from margin measurement")
        for k in ("header", "footer"):
            if r.get(k):
                print(f"  {k}: {r[k]['text']!r}  {r[k]['size']}pt #{r[k]['color']} {r[k]['align']}"
                      f"  -> build_reference.py writes it into reference.docx")
    if r.get("header_image"):
        im = r["header_image"]
        print(f"  header image: {im['w_pt']}x{im['h_pt']}pt at x={im['x_pt']} y={im['y_pt']} ({im['align']})"
              f"  -> saved beside styles.json, written into the header")
    if r.get("table"):
        t = r["table"]
        fmt = lambda v: "none" if not v else f"#{v[0]} {v[1]}pt"
        print(f"\n[table] p{t['page']} {t['rows']}x{t['cols']}: outer {fmt(t['top'])}, inside H {fmt(t['insideH'])},"
              f" inside V {fmt(t['insideV'])}, header rule {fmt(t['header_bottom'])},"
              f" header fill {t['header_fill'] or 'none'}, header bold {t['header_bold']},"
              f" band fill {t['band_fill'] or 'none'}  -> pandoc's 'Table' style")
    elif r["pages"] < 2:
        print("[running head/foot] single page, cannot be determined by recurrence; "
              "any header or footer will distort the top and bottom margins")

    bands = r.get("column_evidence") or []
    print(f"\n[columns] declared: {r.get('columns', 1)}"
          + (f"   width {r['column_width_pt']}pt   gap {r['column_gap_pt']}pt"
             if r.get("column_width_pt") else ""))
    if bands:
        print("  lines start at: "
              + "   ".join(f"{b['x']}pt x{b['lines']}" for b in bands))
    print("  Bands appear for a table just as they do for columns, so this count")
    print("  settles nothing. Render a page and look at it, then pass --columns N.")

    cands = r.get("body_candidates") or []
    if len(cands) > 1:
        print(f"\n[body candidates]  ranked by character count only — READ THE SAMPLES.")
        print(f"  The default is simply the largest group, which is wrong whenever a")
        print(f"  table, an index or a caption block outweighs the prose. The choice")
        print(f"  drives every paragraph metric. Override with --body <rank>.")
        print(f"  {'rank':<5}{'size':>6}{'colour':>9}{'chars':>7}{'lines':>7}{'pages':>7}  sample")
        for c in cands:
            mark = "  <- chosen" if c["chosen"] else ""
            print(f"  {c['rank']:<5}{c['size']:>6}{'#'+c['color']:>9}{c['chars']:>7}"
                  f"{c['lines']:>7}{c['pages']:>7}  {c['sample'][:40]}{mark}")

    print(f"\n[inferred styles]  Spans are grouped on (size, colour, weight) by exact "
          f"equality —\n there is no similarity threshold, so a heading split across two "
          f"scripts stays\n one group. Size and colour are read from the PDF; weight is "
          f"read from the span\n flag, or from the font name when the flag is unset. "
          f"The role column is not\n recorded anywhere and is the one thing being "
          f"guessed — check it.")
    print(f"{'#':<4}{'role':<7}{'font':<26}{'size':>6}{'colour':>9}{'wt':>4}{'chars':>7}  sample")
    b = r["body"]
    print(f"{'':<4}{'body':<7}{b['font']:<26}{b['size']:>6}{'#'+b['color']:>9}"
          f"{('B' if b['bold'] else '-'):>4}{chars[(b['size'],b['color'],b['bold'])]:>7}")
    for h in r["headings"]:
        key = (h["size"], h["color"], h["bold"])
        print(f"{h['level']:<4}{'H'+str(h['level']):<7}{h['font']:<26}{h['size']:>6}{'#'+h['color']:>9}"
              f"{('B' if h['bold'] else '-'):>4}{chars[key]:>7}  {h['sample'][:18]}")
    print(" --map takes the # column: --map 1=Heading1,2=Title")

    if b.get("line_advance_pt"):
        print(f"\n[paragraph metrics]  computed from coordinates, same confidence as fonts")
        print(f"  body  line advance {b['line_advance_pt']}pt "
              f"= {b['line_ratio']}x the font size")
        sa = b.get("space_after_pt")
        print(f"        space after  " + (f"{sa}pt  ({b.get('space_after_samples', 0)} samples)"
              if sa is not None else
              "NOT MEASURED — every paragraph is followed by a table, list or\n"
              "                     heading, so no paragraph-to-paragraph gap exists.\n"
              "                     The template will keep pandoc's default."))
        fi = b.get("first_line_indent_pt") or 0
        print(f"        first indent {fi}pt"
              + (f" = {b['first_line_indent_em']} em" if fi else " (none)"))
        for h in r["headings"]:
            if "space_before_pt" in h:
                fmt = lambda v: "n/a" if v is None else f"{v}pt"
                print(f"  H{h['level']}    before {fmt(h['space_before_pt']):>7}  "
                      f"after {fmt(h['space_after_pt']):>7}  align {h['align']}"
                      f"   (baseline gaps {fmt(h.get('baseline_gap_before_pt'))} / "
                      f"{fmt(h.get('baseline_gap_after_pt'))}, own advance "
                      f"{fmt(h.get('own_line_advance_pt'))})")

    m, s = r["margins_measured_cm"], r["margins_suggested_cm"]
    print(f"\n[margins]  measured != defined; use the suggested row")
    print(f"{'':10}{'left':>8}{'right':>8}{'top':>8}{'bottom':>8}")
    fmt = lambda v: "-" if v is None else str(v)
    mb = "-" if m["bottom"] is None else f"<={m['bottom']}"
    print(f"{'measured':<10}" + "".join(f"{fmt(m[k]):>8}" for k in ("left", "right", "top"))
          + f"{mb:>8}")
    print(f"{'suggested':<10}" + "".join(f"{fmt(s[k]):>8}" for k in
                                         ("left", "right", "top", "bottom")))
    for n in r.get("geometry_notes", []):
        print(f"  .  {n}")

    print("\n[not recorded in the PDF — settle these before building]")
    print("  1. Levels: a document title and an H1 are both just large text in a PDF;")
    print("     grouping cannot separate them. Read the sample column.")
    print("  2. Margins: right/top/bottom measure where content reaches, not where the")
    print("     text block is defined. Feeding measurements back in accumulates drift.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    pick = int(sys.argv[sys.argv.index("--body") + 1]) if "--body" in sys.argv else None
    cols = int(sys.argv[sys.argv.index("--columns") + 1]) if "--columns" in sys.argv else 1
    r, chars, body = analyze(sys.argv[1], pick, cols)
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        if r.get("header_image"):
            # the picture itself, beside styles.json, for build_reference to place
            im = r["header_image"]
            try:
                d = pymupdf.open(sys.argv[1]); ex = d.extract_image(im["xref"]); d.close()
                fn = os.path.join(os.path.dirname(os.path.abspath(out)), "header-image." + ex["ext"])
                open(fn, "wb").write(ex["image"])
                r["header"] = r.get("header") or {"text": "", "align": im["align"], "size": 9.0,
                                                  "color": "808080", "font": "", "page_number": False}
                left_edge = r["margins_suggested_cm"]["left"] / 2.54 * 72
                r["header"]["image"] = {"file": fn, "h_pt": im["h_pt"], "w_pt": im["w_pt"], "align": im["align"],
                                        "indent_pt": round(im["x_pt"] - left_edge, 1) if im["align"] == "left" else 0.0}
            except Exception as e:
                print(f"header image not extracted: {e}")
        json.dump(r, open(out, "w"), ensure_ascii=False, indent=2)
        print(f"Wrote {out}\n")
    report(r, chars, body)
