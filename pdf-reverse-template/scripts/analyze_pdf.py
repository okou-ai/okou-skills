#!/usr/bin/env python3
"""Infer the typographic style sheet of a PDF.

Usage:
  python3 analyze_pdf.py source.pdf                   # human-readable report
  python3 analyze_pdf.py source.pdf --json out.json   # input for build_reference.py

Requires: pip install pymupdf

A PDF has no style layer, only "draw this glyph at this coordinate in this font
and colour". So this clusters every text span by (font, size, colour): the
cluster with the most characters is body text, and anything larger becomes a
heading candidate, ordered by size.

Fonts, sizes, colours and paragraph metrics come out of the coordinates and are
reliable. Heading levels and the bottom margin are not — both need a human.
"""
import sys, json, math, collections, statistics

try:
    import pymupdf
except ImportError:
    sys.exit("Requires pymupdf: pip install pymupdf")

CM = lambda pt: pt / 72 * 2.54
COMMON_CM = [1.0, 1.27, 1.5, 1.8, 2.0, 2.2, 2.5, 2.54, 3.0, 3.17, 3.5, 4.0]
PAPERS = {"A4": (595.3, 841.9), "A3": (841.9, 1190.6), "A5": (420.9, 595.3),
          "Letter": (612.0, 792.0), "Legal": (612.0, 1008.0)}


def collect(doc):
    spans = []
    for page in doc:
        for blk in page.get_text("dict")["blocks"]:
            for line in blk.get("lines", []):
                for s in line["spans"]:
                    if s["text"].strip():
                        spans.append(dict(font=s["font"], size=round(s["size"], 1),
                                          color="%06X" % s["color"], bbox=s["bbox"],
                                          text=s["text"], page=page.number))
    return spans


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
                        key=(first["font"], first["size"], first["color"])))
    out.sort(key=lambda l: (l["page"], l["y"]))
    return out


def measure_spacing(lines, body_key, col_left, col_right):
    """Line advance, space after, first-line indent, heading spacing, alignment."""
    B = [l for l in lines if l["key"] == body_key]
    if len(B) < 4:
        return {}, {}

    # Line advance = the mode of the y delta between consecutive body lines.
    # Paragraph gaps are the minority, so the mode excludes them for free.
    dl = [round(b["y"] - a["y"], 1) for a, b in zip(B, B[1:])
          if a["page"] == b["page"] and 0 < b["y"] - a["y"] < body_key[1] * 3]
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
    body = {"line_advance_pt": adv, "line_ratio": round(adv / body_key[1], 2),
            "space_after_pt": round(statistics.median(gaps), 1) if gaps else 0.0,
            "first_line_indent_pt": indent,
            "first_line_indent_em": round(indent / body_key[1], 2) if indent else 0.0}

    col_mid = (col_left + col_right) / 2
    heads = {}
    for key in {l["key"] for l in lines if l["key"][1] > body_key[1] + 0.4}:
        idx = [i for i, l in enumerate(lines) if l["key"] == key]
        before = [lines[i]["y"] - lines[i - 1]["y"] - adv for i in idx
                  if i > 0 and lines[i]["page"] == lines[i - 1]["page"]]
        after = [lines[i + 1]["y"] - lines[i]["y"] - key[1] * 1.2 for i in idx
                 if i + 1 < len(lines) and lines[i + 1]["page"] == lines[i]["page"]]
        off = statistics.median([abs((lines[i]["x0"] + lines[i]["x1"]) / 2 - col_mid) for i in idx])
        left_off = statistics.median([abs(lines[i]["x0"] - col_left) for i in idx])
        heads[key] = {
            "space_before_pt": round(max(0, statistics.median(before)), 1) if before else 0.0,
            "space_after_pt": round(max(0, statistics.median(after)), 1) if after else 0.0,
            "align": "center" if off < 6 and left_off > 12 else "left",
        }
    return body, heads


def analyze(path):
    doc = pymupdf.open(path)
    page = doc[0]
    W, H = page.rect.width, page.rect.height
    spans = collect(doc)
    if not spans:
        sys.exit("No text layer in this PDF — it is probably a scan. OCR it first.")

    tagged = doc.xref_get_key(doc.pdf_catalog(), "StructTreeRoot")[0] != "null"
    hf, hf_method = running_heads(spans, doc.page_count, H)
    body_spans = [s for i, s in enumerate(spans) if i not in hf]

    chars = collections.Counter()
    for s in body_spans:
        chars[(s["font"], s["size"], s["color"])] += len(s["text"].strip())
    body = chars.most_common(1)[0][0]
    heads = sorted([k for k in chars if k[1] > body[1] + 0.4], key=lambda k: -k[1])

    def sample(key):
        return next(s["text"].strip() for s in body_spans
                    if (s["font"], s["size"], s["color"]) == key)

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

    geom_notes = []
    if not not_first:
        geom_notes.append("single page: the top margin may include a title block "
                          "and read too large")
    if bottom_bound_pt is None:
        geom_notes.append("single page: the bottom margin cannot be measured at all")
    else:
        geom_notes.append(
            f"the bottom margin is an upper bound (real value <= "
            f"{CM(bottom_bound_pt):.2f}cm) because page breaks rarely land at the "
            f"bottom of the text block. Use the top margin value "
            f"{snap(CM(top_pt))[0]}cm — layouts are almost always vertically "
            f"symmetric — after confirming it is below the bound")

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
        "body": dict({"font": body[0], "size": body[1], "color": body[2],
                      "leading_pt": leading}, **body_sp),
        "headings": [dict({"level": i, "font": h[0], "size": h[1], "color": h[2],
                           "sample": sample(h)}, **head_sp.get(h, {}))
                     for i, h in enumerate(heads, 1)],
        "margins_measured_cm": {k: (round(CM(v), 2) if v is not None else None) for k, v in
                                (("left", left_pt), ("right", right_pt),
                                 ("top", top_pt), ("bottom", bottom_bound_pt))},
        "margins_suggested_cm": {k: (snap(CM(v))[0] if v is not None else None) for k, v in
                                 (("left", left_pt), ("right", right_pt),
                                  ("top", top_pt), ("bottom", None))},
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

    print(f"\n[inferred styles]  exact: font/size/colour | inferred: level")
    print(f"{'role':<7}{'font':<30}{'size':>6}{'colour':>9}{'chars':>7}  sample")
    b = r["body"]
    print(f"{'body':<7}{b['font']:<30}{b['size']:>6}{'#'+b['color']:>9}"
          f"{chars[(b['font'],b['size'],b['color'])]:>7}")
    for h in r["headings"]:
        key = (h["font"], h["size"], h["color"])
        print(f"{'H'+str(h['level']):<7}{h['font']:<30}{h['size']:>6}{'#'+h['color']:>9}"
              f"{chars[key]:>7}  {h['sample'][:18]}")

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
    sb = "-" if s["top"] is None else f"={s['top']}"
    print(f"{'suggested':<10}" + "".join(f"{fmt(s[k]):>8}" for k in ("left", "right", "top"))
          + f"{sb:>8}")
    for n in r.get("geometry_notes", []):
        print(f"  .  {n}")

    print("\n[needs a human]")
    print("  1. Levels: a document title and an H1 are both just large text in a PDF;")
    print("     clustering cannot separate them.")
    print("  2. Margins: right/top/bottom measure where content reaches, not where the")
    print("     text block is defined. Feeding measurements back in accumulates drift.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(2)
    r, chars, body = analyze(sys.argv[1])
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        json.dump(r, open(out, "w"), ensure_ascii=False, indent=2)
        print(f"Wrote {out}\n")
    report(r, chars, body)
