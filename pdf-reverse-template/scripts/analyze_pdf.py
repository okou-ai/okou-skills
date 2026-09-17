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
            if repeats or numeric or isolated:
                hits |= set(idx)
        return hits, "recurring across pages"

    order = sorted(range(len(spans)), key=lambda i: spans[i]["bbox"][1])
    ys = [spans[i]["bbox"][1] for i in order]
    gaps = [b - a for a, b in zip(ys, ys[1:])]
    if not gaps:
        return set(), None
    typical = statistics.median([g for g in gaps if g > 0.5] or [0])
    hf = set()
    if typical and gaps and gaps[0] > typical * 2.5:
        hf |= {i for i in order if spans[i]["bbox"][1] <= ys[0] + 1}
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

    gaps = [round(B[i]["y"] - B[i - 1]["y"] - adv, 1) for i in sorted(starts)
            if i > 0 and B[i]["page"] == B[i - 1]["page"] and B[i]["y"] - B[i - 1]["y"] < adv * 4]
    # None, not 0.0: "no usable sample" and "measured as zero" are different
    # claims. Every paragraph here may be followed by a table, a list or a
    # heading, in which case nothing was measured and the builder must not
    # write a value it never obtained.
    body = {"line_advance_pt": adv, "line_ratio": round(adv / body_key[0], 2),
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
    for key in {l["key"] for l in lines if l["key"][0] > body_key[0] + 0.4}:
        idx = [i for i, l in enumerate(lines) if l["key"] == key]
        mine = adv_of(key)
        before, after, raw_b, raw_a = [], [], [], []
        for i in idx:
            if i > 0 and lines[i]["page"] == lines[i - 1]["page"]:
                g = lines[i]["y"] - lines[i - 1]["y"]
                if g <= cap:
                    raw_b.append(g)
                    before.append(g - (adv_of(lines[i - 1]["key"]) + mine) / 2)
            if i + 1 < len(lines) and lines[i + 1]["page"] == lines[i]["page"]:
                g = lines[i + 1]["y"] - lines[i]["y"]
                if g <= cap:
                    raw_a.append(g)
                    after.append(g - (mine + adv_of(lines[i + 1]["key"])) / 2)
        off = statistics.median([abs((lines[i]["x0"] + lines[i]["x1"]) / 2 - col_mid) for i in idx])
        left_off = statistics.median([abs(lines[i]["x0"] - col_left) for i in idx])
        heads[key] = {
            "space_before_pt": round(max(0, statistics.median(before)), 1) if before else None,
            "space_after_pt": round(max(0, statistics.median(after)), 1) if after else None,
            "baseline_gap_before_pt": round(statistics.median(raw_b), 1) if raw_b else None,
            "baseline_gap_after_pt": round(statistics.median(raw_a), 1) if raw_a else None,
            "own_line_advance_pt": round(mine, 1),
            "align": "center" if off < 6 and left_off > 12 else "left",
        }
    return body, heads


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
        return (collections.Counter(round(s["bbox"][0], 1) for s in ss).most_common(1)[0][0],
                far_edge([round(s["bbox"][2], 1) for s in ss]))

    # Bootstrap the column bands from the extremes; a few points of overshoot
    # cannot move a band boundary, which sits half a column away.
    raw_l = min(s["bbox"][0] for s in body_spans)
    raw_r = max(s["bbox"][2] for s in body_spans)
    if columns > 1:
        w = (raw_r - raw_l) / columns
        per_band = collections.defaultdict(list)
        for s in body_spans:
            per_band[min(columns - 1, int((s["bbox"][0] - raw_l) / w))].append(s)
        band_edges = [edges(per_band[k]) for k in sorted(per_band)]
        left_pt, right_edge = band_edges[0][0], band_edges[-1][1]
    else:
        left_pt, right_edge = edges(body_spans)
    right_pt = W - right_edge
    # Top: prefer page 2 onward; a title block inflates the first page.
    not_first = [s for s in body_spans if s["page"] > 0]
    top_src = not_first or body_spans
    top_pt = min(s["bbox"][1] for s in top_src)
    # Bottom: page breaks rarely land exactly at the bottom of the text block,
    # so the measurement is always >= the real value. Take the minimum across
    # non-final pages as the tightest upper bound.
    last = doc.page_count - 1
    per_page = collections.defaultdict(float)
    for s in body_spans:
        if s["page"] != last:
            per_page[s["page"]] = max(per_page[s["page"]], s["bbox"][3])
    bottom_bound_pt = (H - max(per_page.values())) if per_page else None

    top_cm = snap(CM(top_pt))[0]
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
    body_sp, head_sp = measure_spacing(lines, body, left_pt, col_right)
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
        "margins_suggested_cm": {"left": snap(CM(left_pt))[0], "right": snap(CM(right_pt))[0],
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
        "running_heads": sorted({s["text"].strip() for i, s in enumerate(spans) if i in hf})[:6],
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
    print(f"{'role':<7}{'font':<26}{'size':>6}{'colour':>9}{'wt':>4}{'chars':>7}  sample")
    b = r["body"]
    print(f"{'body':<7}{b['font']:<26}{b['size']:>6}{'#'+b['color']:>9}"
          f"{('B' if b['bold'] else '-'):>4}{chars[(b['size'],b['color'],b['bold'])]:>7}")
    for h in r["headings"]:
        key = (h["size"], h["color"], h["bold"])
        print(f"{'H'+str(h['level']):<7}{h['font']:<26}{h['size']:>6}{'#'+h['color']:>9}"
              f"{('B' if h['bold'] else '-'):>4}{chars[key]:>7}  {h['sample'][:18]}")

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
        json.dump(r, open(out, "w"), ensure_ascii=False, indent=2)
        print(f"Wrote {out}\n")
    report(r, chars, body)
