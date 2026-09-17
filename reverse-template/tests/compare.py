"""Fidelity: does a document produced with the package look like the source?
Measures both PDFs the same way and reports each dimension as ok / DIFF."""
import sys, collections, statistics, pymupdf, re

def profile(path):
    d = pymupdf.open(path)
    W, H = d[0].rect.width, d[0].rect.height
    spans, lines = [], []
    for page in d:
        for b in page.get_text("dict")["blocks"]:
            for l in b.get("lines", []):
                ss = [s for s in l["spans"] if s["text"].strip()]
                if not ss: continue
                s0 = ss[0]
                lines.append(dict(page=page.number, x0=l["bbox"][0], x1=l["bbox"][2], y=s0["origin"][1],
                                  size=round(s0["size"], 1), color="%06X" % s0["color"], font=s0["font"].split("+")[-1],
                                  bold=bool(s0["flags"] & 16) or "Bold" in s0["font"], text="".join(s["text"] for s in ss)))
    n = len(lines)
    body_key = collections.Counter((l["size"], l["color"]) for l in lines).most_common(1)[0][0]
    body = [l for l in lines if (l["size"], l["color"]) == body_key]
    # header/footer band: lines repeated on >1 page at same y within 3% of the edge
    band = [l for l in lines if l["y"] < H * 0.08 or l["y"] > H * 0.93]
    hf_texts = collections.Counter(re.sub(r"\d+", "#", l["text"]) for l in band)
    hf = {t for t, c in hf_texts.items() if c >= 2 or d.page_count == 1}
    head_y = [l["y"] for l in band if re.sub(r"\d+", "#", l["text"]) in hf and l["y"] < H / 2]
    foot_y = [l["y"] for l in band if re.sub(r"\d+", "#", l["text"]) in hf and l["y"] > H / 2]
    core = [l for l in lines if re.sub(r"\d+", "#", l["text"]) not in hf]
    bodyc = [l for l in body if re.sub(r"\d+", "#", l["text"]) not in hf]
    longb = [l for l in bodyc if l["x1"] - l["x0"] > 100] or bodyc
    left = min(l["x0"] for l in longb)
    # columns: x0 clusters of long body lines (table cells and list items are short or indented)
    x0s = collections.Counter(round(l["x0"]) for l in longb)
    starts = sorted(x for x, c in x0s.items() if c >= max(3, len(longb) * 0.08))
    cols = 1 + sum(1 for a, b in zip(starts, starts[1:]) if b - a > 60)
    # the right margin is set by the rightmost column's lines
    lastcol = [l for l in longb if l["x0"] >= (starts[-1] - 3 if starts else 0)] or longb
    x1m = collections.Counter(round(l["x1"]) for l in lastcol).most_common(1)[0]
    right = W - (x1m[0] if x1m[1] * 3 >= len(lastcol) else max(l["x1"] for l in lastcol))
    steps = [round(b["y"] - a["y"], 1) for a, b in zip(bodyc, bodyc[1:])
             if a["page"] == b["page"] and 0 < b["y"] - a["y"] < body_key[0] * 4]
    adv = collections.Counter(v for v in steps if v < body_key[0] * 3).most_common(1)
    # paragraph gap: the modal step larger than the line advance
    pgap = collections.Counter(v for v in steps if adv and v > adv[0][0] + 1.5).most_common(1)
    firsts = collections.defaultdict(list)
    for l in core: firsts[l["page"]].append(l)
    top1 = min(x["y"] for x in firsts[0]) if 0 in firsts else None
    big = max(firsts[0], key=lambda x: x["size"]) if 0 in firsts else None
    title1 = (round(big["y"], 1), big["size"]) if big else None
    rest = [min(x["y"] for x in ls) for pg, ls in firsts.items() if pg > 0]
    top = statistics.median(rest) if rest else None
    heads = {}
    for l in core:
        k = (l["size"], l["color"], l["bold"])
        if l["size"] > body_key[0] + 0.4 or (l["bold"] and not (l["size"], l["color"]) == body_key):
            heads.setdefault(k, []).append(l)
    heads = {k: v for k, v in heads.items() if len(v) >= 1}
    cjk = lambda t: re.search(r"[\u4e00-\u9fff]", t) is not None
    lat = [l for l in body if not cjk(l["text"]) and re.search(r"[A-Za-z]{3}", l["text"])]
    cj = [l for l in body if cjk(l["text"])]
    imgs = [pymupdf.Rect(i["bbox"]) for i in d[0].get_image_info() if pymupdf.Rect(i["bbox"]).y1 < H * 0.15]
    himg = tuple(round(v, 1) for v in (imgs[0].x0, imgs[0].y0, imgs[0].width, imgs[0].height)) if imgs else None
    return dict(W=W, H=H, pages=d.page_count, header_image=himg, body_size=body_key[0], body_color=body_key[1],
                body_font_latin=collections.Counter(l["font"] for l in lat).most_common(1)[0][0] if len(lat) >= 3 else None,
                body_font_cjk=collections.Counter(l["font"] for l in cj).most_common(1)[0][0] if len(cj) >= 5 else None, adv=adv[0][0] if adv else None, pgap=pgap[0][0] if pgap and pgap[0][1] >= 2 else None,
                left=round(left, 1), right=round(right, 1), first_baseline=round(top, 1) if top else None, first_baseline_p1=round(top1, 1) if top1 else None, title_p1=title1,
                cols=cols, header_y=round(statistics.median(head_y), 1) if head_y else None,
                footer_y=round(statistics.median(foot_y), 1) if foot_y else None,
                heads=sorted(heads, key=lambda k: -k[0]))

def table_look(path):
    """Border lines and shading of the first table: {(kind, colour, width)} and {fill}."""
    d = pymupdf.open(path)
    for p in d:
        import io, contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            t = p.find_tables()
        if not t.tables:
            continue
        tb = t.tables[0]
        bb = pymupdf.Rect(tb.bbox) + (-3, -3, 3, 3)
        lines, fills = set(), set()
        for dr in p.get_drawings():
            for it in dr["items"]:
                if it[0] == "l" and (bb.contains(it[1]) or bb.contains(it[2])):
                    lines.add(("h" if abs(it[1].y - it[2].y) < 0.5 else "v",
                               tuple(round(c, 1) for c in (dr.get("color") or ())), round(dr.get("width") or 0, 1)))
                elif it[0] == "re" and bb.intersects(it[1]) and min(it[1].width, it[1].height) >= 1.6:
                    f = dr.get("fill")
                    if f and tuple(round(c, 2) for c in f) != (1.0, 1.0, 1.0):
                        fills.add(tuple(round(c, 1) for c in f))
        return {"lines": lines, "fills": fills}
    return None

def main(src, out):
    a, b = profile(src), profile(out)
    rows, bad = [], 0
    def cmp(name, x, y, tol=None):
        nonlocal bad
        ok = (x == y) if tol is None else (x is not None and y is not None and abs(x - y) <= tol) or (x is None and y is None)
        if not ok: bad += 1
        rows.append(f"  {name:16} {str(x):>28} {str(y):>28}  {'ok' if ok else 'DIFF'}")
    cmp("paper", (round(a['W']), round(a['H'])), (round(b['W']), round(b['H'])))
    cmp("columns", a["cols"], b["cols"])
    cmp("left margin", a["left"], b["left"], 3)
    cmp("right margin", a["right"], b["right"], max(3, a["body_size"]))
    ta, tb = a["title_p1"], b["title_p1"]
    if ta and tb and ta[1] == tb[1]:
        cmp("title baseline p1", ta[0], tb[0], 4)
    else:
        cmp("1st baseline p1", a["first_baseline_p1"], b["first_baseline_p1"], 4)
    if a["first_baseline"] is None or b["first_baseline"] is None:
        rows.append(f"  {'1st baseline p2+':16} {str(a['first_baseline']):>28} {str(b['first_baseline']):>28}  n/a")
    else:
        cmp("1st baseline p2+", a["first_baseline"], b["first_baseline"], 4)
    for k in ("latin", "cjk"):
        x, y = a[f"body_font_{k}"], b[f"body_font_{k}"]
        if x is None or y is None:
            rows.append(f"  {'body font ' + k:16} {str(x):>28} {str(y):>28}  n/a")
        else:
            cmp("body font " + k, x, y)
    cmp("body size", a["body_size"], b["body_size"], 0.3)
    cmp("body colour", a["body_color"], b["body_color"])
    cmp("line advance", a["adv"], b["adv"], 0.8)
    if a["pgap"] is None or b["pgap"] is None:
        rows.append(f"  {'paragraph gap':16} {str(a['pgap']):>28} {str(b['pgap']):>28}  n/a")
    else:
        cmp("paragraph gap", a["pgap"], b["pgap"], 1.5)
    cmp("header y", a["header_y"], b["header_y"], 3)
    cmp("footer y", a["footer_y"], b["footer_y"], 3)
    if a["header_image"] is None and b["header_image"] is None:
        rows.append(f"  {'header image':16} {'none':>28} {'none':>28}  n/a")
    elif a["header_image"] and b["header_image"]:
        ok = all(abs(x - y) <= 3 for x, y in zip(a["header_image"], b["header_image"]))
        bad += 0 if ok else 1
        rows.append(f"  {'header image':16} {str(a['header_image']):>28} {str(b['header_image']):>28}  {'ok' if ok else 'DIFF'}")
    else:
        cmp("header image", a["header_image"], b["header_image"])
    ha = [(k[0], k[1], k[2]) for k in a["heads"]][:5]; hb = [(k[0], k[1], k[2]) for k in b["heads"]][:5]
    ta_, tb_ = table_look(src), table_look(out)
    if ta_ is None or tb_ is None:
        rows.append(f"  {'table look':16} {str(ta_ and 'table'):>28} {str(tb_ and 'table'):>28}  n/a")
    else:
        cmp("table borders", sorted(ta_["lines"]), sorted(tb_["lines"]))
        cmp("table shading", sorted(ta_["fills"]), sorted(tb_["fills"]))
    missing = [h for h in ha if h not in hb]
    cmp("source headings", "all present", "all present" if not missing else f"MISSING {missing}")
    print(f"  {'':16} {'source':>28} {'output':>28}")
    print("\n".join(rows))
    return bad

if __name__ == "__main__":
    sys.exit(min(1, main(sys.argv[1], sys.argv[2])))
