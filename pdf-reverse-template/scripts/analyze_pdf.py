#!/usr/bin/env python3
"""Infer the typographic style sheet of a PDF.

Usage:
  python3 analyze_pdf.py source.pdf                   # human-readable report
  python3 analyze_pdf.py source.pdf --json out.json   # input for build_reference.py
  python3 analyze_pdf.py source.pdf --body 2           # pick a different body cluster

Requires: pip install pymupdf

A PDF has no style layer, only "draw this glyph at this coordinate in this font
and colour". So this clusters every text span by (size, colour, weight): the
cluster with the most characters is body text, and anything larger becomes a
heading candidate, ordered by size.

Fonts, sizes, colours and paragraph metrics come out of the coordinates and are
reliable. Heading levels and the bottom margin are not — both need a human.
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

    These are the single biggest source of a wrong body cluster. A dotted ToC
    packs hundreds of characters into a handful of spans, so counting raw
    characters hands "body text" to the leader dots and every downstream
    metric — line advance, space after, the heading size threshold — is then
    computed against the wrong cluster.
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
                                          text=s["text"], page=page.number,
                                          bold=is_bold(s), filler=is_filler(s["text"])))
    return spans


def skey(s):
    """Merge key: size, colour and weight — deliberately not the font name.

    One heading is routinely split across two runs when it mixes scripts, e.g.
    "1.1" in a Latin face and the title text in a CJK face at the same size and
    colour. Keying on the font name would leave them as separate clusters that
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


def running_heads(spans, npages, page_h):
    """Indices of spans belonging to a running header or footer.

    Multi-page: same y position recurring across pages. Reliable.
    Single page: falls back to "isolated line at the top or bottom", a heuristic
    that the report flags as unreliable.
    """
    if npages >= 2:
        # Conditions: inside the top/bottom 12% band, and the same y appears on
        # >= 60% of pages. Text equality is deliberately not required — page
        # numbers differ on every page but are still a footer. The band is what
        # keeps ordinary body lines out: equal-length paragraphs land on the
        # same baseline across pages.
        band = lambda s: s["bbox"][1] < page_h * 0.12 or s["bbox"][3] > page_h * 0.88
        pages_of = collections.defaultdict(set)
        for s in spans:
            if band(s):
                pages_of[round(s["bbox"][1])].add(s["page"])
        # ceil, not int: with int(4 * 0.6) == 2, two chapter headings that happen
        # to share a y would be mistaken for a running head.
        need = max(2, math.ceil(npages * 0.6))
        rep = {y for y, pgs in pages_of.items() if len(pgs) >= need}
        return {i for i, s in enumerate(spans)
                if band(s) and round(s["bbox"][1]) in rep}, "recurring across pages"

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


def to_lines(spans):
    """Group spans into lines. PyMuPDF blocks are not paragraphs — in practice
    each block often holds a single line — so paragraphs are segmented here."""
    byline = collections.defaultdict(list)
    for s in spans:
        byline[(s["page"], round(s["bbox"][1], 1))].append(s)
    out = []
    for (pg, y), ss in byline.items():
        first = min(ss, key=lambda s: s["bbox"][0])
        out.append(dict(page=pg, y=y,
                        x0=round(min(s["bbox"][0] for s in ss), 1),
                        x1=round(max(s["bbox"][2] for s in ss), 1),
                        key=skey(first),
                        filler=all(s["filler"] for s in ss)))
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
    starts = {0}
    for i, (a, b) in enumerate(zip(B, B[1:]), start=1):
        if a["page"] != b["page"] or (b["y"] - a["y"]) > adv * 1.25:
            starts.add(i)
    sx = collections.Counter(B[i]["x0"] for i in starts)
    cx = collections.Counter(B[i]["x0"] for i in range(len(B)) if i not in starts)
    indent = None
    if sx and cx:
        v = sx.most_common(1)[0][0] - cx.most_common(1)[0][0]
        indent = round(v, 1) if v > 2 else 0.0

    gaps = [round(B[i]["y"] - B[i - 1]["y"] - adv, 1) for i in sorted(starts)
            if i > 0 and B[i]["page"] == B[i - 1]["page"] and B[i]["y"] - B[i - 1]["y"] < adv * 4]
    body = {"line_advance_pt": adv, "line_ratio": round(adv / body_key[0], 2),
            "space_after_pt": round(statistics.median(gaps), 1) if gaps else 0.0,
            "first_line_indent_pt": indent,
            "first_line_indent_em": round(indent / body_key[0], 2) if indent else 0.0}

    col_mid = (col_left + col_right) / 2
    heads = {}
    # A gap this large is not paragraph spacing, it is white space on a cover or
    # section-break page. Left in, the median lands in the hundreds of points.
    cap = adv * 6
    for key in {l["key"] for l in lines if l["key"][0] > body_key[0] + 0.4}:
        idx = [i for i, l in enumerate(lines) if l["key"] == key]
        before = [g for g in (lines[i]["y"] - lines[i - 1]["y"] - adv for i in idx
                              if i > 0 and lines[i]["page"] == lines[i - 1]["page"])
                  if g <= cap]
        after = [g for g in (lines[i + 1]["y"] - lines[i]["y"] - key[0] * 1.2 for i in idx
                             if i + 1 < len(lines) and lines[i + 1]["page"] == lines[i]["page"])
                 if g <= cap]
        off = statistics.median([abs((lines[i]["x0"] + lines[i]["x1"]) / 2 - col_mid) for i in idx])
        left_off = statistics.median([abs(lines[i]["x0"] - col_left) for i in idx])
        heads[key] = {
            "space_before_pt": round(max(0, statistics.median(before)), 1) if before else 0.0,
            "space_after_pt": round(max(0, statistics.median(after)), 1) if after else 0.0,
            "align": "center" if off < 6 and left_off > 12 else "left",
        }
    return body, heads


def analyze(path, body_pick=None):
    doc = pymupdf.open(path)
    page = doc[0]
    W, H = page.rect.width, page.rect.height
    spans = collect(doc)
    if not spans:
        sys.exit("No text layer in this PDF — it is probably a scan. OCR it first.")

    tagged = doc.xref_get_key(doc.pdf_catalog(), "StructTreeRoot")[0] != "null"
    hf, hf_method = running_heads(spans, doc.page_count, H)
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

    # Spans per distinct line, which separates prose from table cells: a table
    # row puts one span in every column, prose puts one or two on a line. Raw
    # character count alone hands "body text" to a dense table, and every
    # paragraph metric is then measured against table geometry.
    tabular = {}
    for k in chars:
        S = [s for s in content if skey(s) == k]
        rows = len({(s["page"], round(s["bbox"][1], 1)) for s in S})
        tabular[k] = (len(S) / rows) >= 2.0 if rows else False

    ranked = [k for k, _ in chars.most_common()]
    prose = [k for k in ranked if not tabular[k]]
    body = (prose or ranked)[0]
    if body_pick is not None:
        if not 1 <= body_pick <= len(ranked):
            sys.exit(f"--body must be between 1 and {len(ranked)}")
        body = ranked[body_pick - 1]
    heads = sorted([k for k in chars if k[0] > body[0] + 0.4], key=lambda k: -k[0])

    font_of = lambda k: fonts[k].most_common(1)[0][0]

    def sample(key):
        return next((s["text"].strip() for s in content if skey(s) == key), "")

    # Left: the mode of line start x, steadier than taking the minimum.
    lefts = collections.Counter(round(s["bbox"][0]) for s in body_spans)
    left_pt = lefts.most_common(1)[0][0]
    # Right: where the longest line ends, assuming some line fills the column.
    right_pt = W - max(s["bbox"][2] for s in body_spans)
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
                          f"clustering; counting them would hand the body cluster to a "
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

    lines = to_lines(body_spans)
    col_right = W - right_pt
    body_sp, head_sp = measure_spacing(lines, body, left_pt, col_right)
    leading = body_sp.get("line_advance_pt")

    result = {
        "file": path, "pages": doc.page_count,
        "page": {"w_pt": round(W, 1), "h_pt": round(H, 1),
                 "w_cm": round(CM(W), 2), "h_cm": round(CM(H), 2),
                 "paper": paper_name(W, H)},
        "tagged": tagged,
        "filler_spans_excluded": filler_count,
        "body_candidates": [{"rank": i, "font": font_of(k), "size": k[0], "color": k[1],
                             "bold": k[2], "chars": chars[k], "tabular": tabular[k],
                             "sample": sample(k), "chosen": k == body}
                            for i, k in enumerate(ranked[:6], 1)],
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
                                  if r["tagged"] else "absent — levels are inferred by "
                                  "clustering and must be reviewed by a human"))
    if r["running_heads"]:
        print(f"[running head/foot] {r['running_heads_method']}: "
              f"{' | '.join(r['running_heads'])}  -> excluded from margin measurement")
    elif r["pages"] < 2:
        print("[running head/foot] single page, cannot be determined by recurrence; "
              "any header or footer will distort the top and bottom margins")

    cands = r.get("body_candidates") or []
    if len(cands) > 1:
        print(f"\n[body candidates]  the chosen one drives every paragraph metric; "
              f"override with --body <rank>")
        print(f"{'rank':<6}{'font':<26}{'size':>6}{'colour':>9}{'chars':>7}{'table?':>8}  sample")
        for c in cands:
            mark = " <- chosen" if c["chosen"] else ""
            print(f"{c['rank']:<6}{c['font']:<26}{c['size']:>6}{'#'+c['color']:>9}"
                  f"{c['chars']:>7}{('yes' if c['tabular'] else '-'):>8}  "
                  f"{c['sample'][:22]}{mark}")

    print(f"\n[inferred styles]  clustered by size + colour + weight, so one heading "
          f"split\n across scripts stays a single cluster. Exact: size/colour/weight. "
          f"Inferred: level.")
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
        print(f"        space after  {b['space_after_pt']}pt")
        fi = b.get("first_line_indent_pt") or 0
        print(f"        first indent {fi}pt"
              + (f" = {b['first_line_indent_em']} em" if fi else " (none)"))
        for h in r["headings"]:
            if "space_before_pt" in h:
                print(f"  H{h['level']}    before {h['space_before_pt']}pt  "
                      f"after {h['space_after_pt']}pt  align {h['align']}")

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

    print("\n[needs a human]")
    print("  1. Levels: a document title and an H1 are both just large text in a PDF;")
    print("     clustering cannot separate them. Read the sample column.")
    print("  2. Margins: right/top/bottom measure where content reaches, not where the")
    print("     text block is defined. Feeding measurements back in accumulates drift.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    pick = int(sys.argv[sys.argv.index("--body") + 1]) if "--body" in sys.argv else None
    r, chars, body = analyze(sys.argv[1], pick)
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        json.dump(r, open(out, "w"), ensure_ascii=False, indent=2)
        print(f"Wrote {out}\n")
    report(r, chars, body)
