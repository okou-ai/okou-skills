#!/usr/bin/env python3
"""Measure one reference image, or report what a set of them holds constant.

Usage:  python3 measure_style.py <image> [<image> ...] [--json out.json]

One image: canvas, background, palette with area shares, subject extent,
line system, fill flatness, edge softness and grain.
Several: the same table per image plus a CONSTANT / VARIES verdict per
dimension, which is what separates a locked axis from a dial.
"""
import collections
import json
import os
import statistics
import sys

import pymupdf

HEX = lambda c: "%02X%02X%02X" % c


def load(path):
    """RGB rows at full size, plus a small copy for area work.

    Read through stride and channel count, never width*3: shrink() returns a
    four-channel pixmap even from a three-channel source, and reading that as
    RGB rotates every colour one channel to the left."""
    pix = pymupdf.Pixmap(path)
    if pix.colorspace is None or pix.colorspace.n != 3:
        pix = pymupdf.Pixmap(pymupdf.csRGB, pix)

    def rows_of(p, step=1):
        s, n, st = p.samples, p.n, p.stride
        return [[(s[y * st + x * n], s[y * st + x * n + 1], s[y * st + x * n + 2])
                 for x in range(0, p.width, step)] for y in range(0, p.height, step)]

    small = pymupdf.Pixmap(pix)
    while small.width > 320:
        small.shrink(1)
    return rows_of(pix), rows_of(small), pix.width, pix.height


def dist(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]), abs(a[2] - b[2]))


def luma(c):
    return 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]


def background(rows, w, h, box=None):
    """The field the art sits on, and whether it is flat, a gradient or
    textured.

    Read from the border strips the art leaves empty. Sampling the whole
    border ring reports the painting itself whenever a piece bleeds off one
    edge, which is why the strips come from the subject box."""
    strips = []
    if box:
        x0, y0, x1, y1 = box
        if y0 > 0.015 * h:
            strips += [rows[y][x] for y in range(0, int(y0 * 0.8), max(1, h // 120)) for x in range(0, w, 3)]
        if h - y1 > 0.015 * h:
            strips += [rows[y][x] for y in range(int(y1 + (h - y1) * 0.2), h, max(1, h // 120)) for x in range(0, w, 3)]
        if x0 > 0.015 * w:
            strips += [rows[y][x] for x in range(0, int(x0 * 0.8), max(1, w // 120)) for y in range(0, h, 3)]
        if w - x1 > 0.015 * w:
            strips += [rows[y][x] for x in range(int(x1 + (w - x1) * 0.2), w, max(1, w // 120)) for y in range(0, h, 3)]
    ring = strips or ([rows[y][x] for y in (0, 1, h - 2, h - 1) for x in range(0, w, 3)]
                      + [rows[y][x] for x in (0, 1, w - 2, w - 1) for y in range(0, h, 3)])
    mode = collections.Counter(ring).most_common(1)[0][0]
    spread = statistics.median(dist(c, mode) for c in ring)
    corners = [rows[0][0], rows[0][w - 1], rows[h - 1][0], rows[h - 1][w - 1]]
    corner_spread = max(dist(a, b) for a in corners for b in corners)
    kind = "flat" if spread <= 4 and corner_spread <= 10 else (
        "gradient" if corner_spread > 24 and spread <= 24 else "textured")
    return {"color": HEX(mode), "kind": kind, "edge_spread": round(spread, 1),
            "corner_spread": corner_spread, "from_strips": bool(strips)}


def palette(quarter, top=8):
    """Colours by share of area. Near-identical colours merge, so a hue laid
    down with anti-aliasing counts once."""
    n = 0
    buckets = collections.Counter()
    for row in quarter:
        for c in row:
            buckets[(c[0] >> 3 << 3, c[1] >> 3 << 3, c[2] >> 3 << 3)] += 1
            n += 1
    merged = []
    for c, k in buckets.most_common():
        for m in merged:
            if dist(c, m[0]) <= 24:
                m[1] += k
                break
        else:
            merged.append([c, k])
    merged.sort(key=lambda m: -m[1])
    out = [{"color": HEX(c), "share_pct": round(100 * k / n, 1), "rgb": c} for c, k in merged[:top]]
    # A colour sitting on the line between two larger ones is anti-aliasing
    # between them, not a colour the artwork uses.
    big = [e for e in out if e["share_pct"] >= 2.0]
    for e in out:
        e["blend"] = False
        if e in big:
            continue
        for a in big:
            for b in big:
                if a is b:
                    continue
                for t in (0.25, 0.4, 0.5, 0.6, 0.75):
                    mix = tuple(round(a["rgb"][i] * t + b["rgb"][i] * (1 - t)) for i in range(3))
                    if dist(mix, e["rgb"]) <= 16:
                        e["blend"] = True
                        break
                if e["blend"]:
                    break
            if e["blend"]:
                break
    for e in out:
        e.pop("rgb")
    return out


def subject(rows, w, h, bg):
    """Where the art actually sits: its box, its share of the canvas, and the
    margin on each side as a fraction of the canvas."""
    bgc = tuple(int(bg["color"][i:i + 2], 16) for i in (0, 2, 4))
    step = max(1, w // 400)
    x0, y0, x1, y1 = w, h, -1, -1
    hit = 0
    for y in range(0, h, step):
        row = rows[y]
        for x in range(0, w, step):
            if dist(row[x], bgc) > 18:
                hit += 1
                x0, y0 = min(x0, x), min(y0, y)
                x1, y1 = max(x1, x), max(y1, y)
    if x1 < 0:
        return None
    box_w, box_h = (x1 - x0) / w, (y1 - y0) / h
    cols = max(1, len(range(0, w, step)))
    rowsn = max(1, len(range(0, h, step)))
    return {"box": (x0, y0, x1, y1),
            "box_pct": [round(100 * box_w, 1), round(100 * box_h, 1)],
            "ink_pct": round(100 * hit / (cols * rowsn), 1),
            "margins_pct": {"left": round(100 * x0 / w, 1), "right": round(100 * (w - x1) / w, 1),
                            "top": round(100 * y0 / h, 1), "bottom": round(100 * (h - y1) / h, 1)},
            "centred": abs((x0 + x1) / 2 - w / 2) < 0.04 * w and abs((y0 + y1) / 2 - h / 2) < 0.06 * h}


def lines(rows, w, h):
    """The drawn line: its colour and how wide it is laid down.

    Both come from short dark runs along a scanline. A run as long as a shape
    is that shape's fill, so taking the modal dark colour over the whole image
    reports dark paint as the ink."""
    thin = max(2, int(w * 0.015))
    runs, ink_px, drawn = [], [], 0
    for y in range(0, h, max(1, h // 400)):
        row = rows[y]
        run, start = [], 0
        for x in range(w):
            c = row[x]
            if luma(c) < 110:
                if not run:
                    start = x
                run.append(c)
            else:
                if 0 < len(run) <= thin:
                    runs.append(len(run))
                    ink_px.extend(run)
                    # A drawn contour carries lighter paint on both sides. The
                    # edge of a dark shape carries the shape on one side, so
                    # counting every thin dark run reports an outline on a
                    # style that never draws one.
                    left = row[start - 1] if start > 0 else None
                    core = min(luma(v) for v in run)
                    if left is not None and luma(left) > core + 40 and luma(row[x]) > core + 40:
                        drawn += 1
                run = []
    if len(runs) < 20 or not ink_px:
        return {"present": False}
    drawn_share = round(drawn / len(runs), 2)
    ink = collections.Counter((c[0] >> 3 << 3, c[1] >> 3 << 3, c[2] >> 3 << 3)
                              for c in ink_px).most_common(1)[0][0]
    c = collections.Counter(runs)
    # The modal run is the stroke. A median would be pulled up by the filled
    # shapes the strokes enclose, and a width read off a downscaled preview
    # comes out several times too fine.
    width = c.most_common(1)[0][0]
    band = [r for r, k in c.items() if abs(r - width) <= max(1, width * 0.3) for _ in range(k)]
    return {"present": True, "contour": drawn_share >= 0.3, "contour_share": drawn_share,
            "color": HEX(ink), "width_px": width,
            "width_pct_of_canvas": round(100 * width / w, 2),
            "width_range_px": [min(band), max(band)], "samples": len(runs)}


def surface(rows, w, h, bg):
    """Flat fill or modelled, hard edges or soft, clean or grainy.

    flat_pct  — pixels with no structural edge under them. The threshold rides
                on the measured grain: a flat shape under a heavy paper texture
                has neighbours that differ everywhere, and a fixed threshold
                reports it as modelled.
    edge_px   — how many pixels a colour boundary takes to cross over; a
                vector edge is 1-2, a watercolour bleed is far wider.
    grain     — mean neighbour difference where no edge runs.
    """
    step = max(1, w // 320)
    deltas = []
    for y in range(step, h - step, step):
        for x in range(step, w - step, step):
            c = rows[y][x]
            nb = (rows[y][x - step], rows[y][x + step], rows[y - step][x], rows[y + step][x])
            deltas.append((max(dist(c, n) for n in nb),
                           statistics.mean(dist(c, n) for n in nb)))
    if not deltas:
        return {"flat_pct": 0.0, "grain": 0.0, "edge_px": None, "edge_samples": 0}
    quiet = [m for d, m in deltas if d <= 6]
    grain = statistics.mean(quiet) if quiet else 0.0
    if not quiet or len(quiet) * 4 < len(deltas):
        # A textured sheet: re-read the grain from the calmest tenth, then let
        # the flatness threshold ride on it.
        calm = sorted(m for _, m in deltas)[: max(1, len(deltas) // 10)]
        grain = statistics.mean(calm)
    thresh = max(6.0, grain * 3.0)
    same = sum(1 for d, _ in deltas if d <= thresh)
    ramps = []
    for y in range(0, h, max(1, h // 120)):
        row = rows[y]
        x = 1
        while x < w - 1:
            if dist(row[x], row[x - 1]) > 20:
                start, x2 = x, x
                while x2 < w - 1 and dist(row[x2], row[x2 + 1]) > 6 and x2 - start < 40:
                    x2 += 1
                ramps.append(x2 - start + 1)
                x = x2 + 1
            x += 1
    return {"flat_pct": round(100 * same / len(deltas), 1),
            "grain": round(grain, 2),
            "flat_threshold": round(thresh, 1),
            "edge_px": round(statistics.median(ramps), 1) if ramps else None,
            "edge_samples": len(ramps)}


# Below this, a reference describes its own downscaling: the palette fills up
# with anti-alias blends, the modal dark colour is one of those blends rather
# than the ink, and one pixel of stroke is a large share of the canvas.
MIN_SIDE = 400


def measure(path):
    rows, quarter, w, h = load(path)
    bg = background(rows, w, h)
    probe = subject(rows, w, h, bg)
    if probe:                      # second pass: field read outside the art
        bg = background(rows, w, h, probe["box"])
        probe = subject(rows, w, h, bg)
    # Art that runs to the edges leaves no field to read: the border ring is
    # painting, and its colour and flatness describe the painting, not a
    # background.
    if probe and not bg["from_strips"] and probe["ink_pct"] >= 45:
        bg = {"color": bg["color"], "kind": "none (art covers the canvas)",
              "edge_spread": bg["edge_spread"], "corner_spread": bg["corner_spread"]}
    return {"file": os.path.basename(path), "low_res": min(w, h) < MIN_SIDE,
            "canvas": {"w": w, "h": h,
            "aspect": round(w / h, 3), "shape": "square" if abs(w - h) <= 2 else
            ("portrait" if h > w else "landscape")},
            "background": bg, "palette": palette(quarter),
            "subject": ({k: v for k, v in probe.items() if k != "box"} if probe else None),
            "lines": lines(rows, w, h), "surface": surface(rows, w, h, bg)}


def report(ms):
    for m in ms:
        c, b, s, l, f = m["canvas"], m["background"], m["subject"], m["lines"], m["surface"]
        print(f"\n=== {m['file']}")
        print(f"  canvas      {c['w']}x{c['h']}  {c['shape']}  aspect {c['aspect']}")
        print(f"  background  #{b['color']}  {b['kind']}  (edge spread {b['edge_spread']}, corner spread {b['corner_spread']})")
        print("  palette     " + "  ".join(f"#{p['color']} {p['share_pct']}%" for p in m["palette"][:6] if not p["blend"]))
        blends = [p for p in m["palette"][:8] if p["blend"]]
        if blends:
            print("              (anti-alias blends, not style colours: "
                  + " ".join("#" + p["color"] for p in blends) + ")")
        if s:
            mg = s["margins_pct"]
            print(f"  subject     box {s['box_pct'][0]}x{s['box_pct'][1]}% of canvas, ink {s['ink_pct']}%, "
                  f"{'centred' if s['centred'] else 'off-centre'}")
            print(f"              margins L{mg['left']} R{mg['right']} T{mg['top']} B{mg['bottom']} %")
        if not l["present"]:
            print("  lines       no dark line structure")
        else:
            print(f"  lines       #{l['color']}  width {l.get('width_px')}px "
                  f"({l.get('width_pct_of_canvas')}% of canvas, range {l.get('width_range_px')},"
                  f" {l.get('samples')} runs)")
            if l.get("contour"):
                print(f"              drawn contour: {l.get('contour_share')} of dark runs have"
                      f" lighter paint on both sides")
            else:
                print(f"              NO drawn contour: only {l.get('contour_share')} of dark runs"
                      f" have lighter paint on both\n              sides. Shapes meet at their"
                      f" colour edges; the value above is the darkest\n              paint, not an"
                      f" outline. Do not put an outline in the package.")
        print(f"  surface     flat {f['flat_pct']}%  grain {f['grain']}  edge ramp {f['edge_px']}px")
        if m["low_res"]:
            print(f"  LOW RES     {c['w']}x{c['h']} is under {MIN_SIDE}px. Palette, line colour and"
                  f" line width\n              describe the downscaling, not the style. Ask for a"
                  f" larger file.\n              Still usable: aspect, ground colour, ink coverage,"
                  f" centring.")

    if len(ms) < 2:
        print("\nOne reference cannot separate a locked axis from a dial. Every value above"
              "\nis a fact about this piece only. Ask for more references, or mark the axes"
              "\nthis one cannot settle in the package.")
        return

    print(f"\n=== across {len(ms)} references")
    print("  CONSTANT = write the value into the locked frame")
    print("  RANGE    = still locked, but write it as a range")
    print("  VARIES   = a dial; the package must let it change per piece\n")

    def num(name, values, unit="", rel=0.25):
        vals = [v for v in values if v is not None]
        if not vals:
            print(f"  VARIES    {name:22} not measurable")
            return
        lo, hi = min(vals), max(vals)
        if hi - lo <= 1e-9 or (lo > 0 and hi / lo <= 1 + rel):
            print(f"  CONSTANT  {name:22} {round(statistics.median(vals), 2)}{unit}")
        else:
            print(f"  RANGE     {name:22} {lo}{unit} - {hi}{unit}")

    def cat(name, values):
        uniq = list(dict.fromkeys(values))
        if len(uniq) == 1:
            print(f"  CONSTANT  {name:22} {uniq[0]}")
        else:
            print(f"  VARIES    {name:22} " + "  ".join(str(u) for u in uniq[:4]))

    cat("canvas", [f"{m['canvas']['w']}x{m['canvas']['h']}" for m in ms])
    bgs = [tuple(int(m["background"]["color"][i:i + 2], 16) for i in (0, 2, 4)) for m in ms]
    bg_spread = max(dist(bgs[0], c) for c in bgs)
    print(f"  {'CONSTANT' if bg_spread <= 12 else 'VARIES  '}  {'background colour':22} "
          f"#{ms[0]['background']['color']}" + (f"  (spread {bg_spread})" if bg_spread else ""))
    cat("background kind", [m["background"]["kind"] for m in ms])
    lc = [m["lines"].get("color") for m in ms]
    if all(lc):
        rgbs = [tuple(int(c[i:i + 2], 16) for i in (0, 2, 4)) for c in lc]
        sp = max(dist(rgbs[0], c) for c in rgbs)
        print(f"  {'CONSTANT' if sp <= 24 else 'VARIES  '}  {'line colour':22} #{lc[0]}"
              + (f"  (spread {sp})" if sp else ""))
    else:
        cat("line colour", ["#" + (c or "none") for c in lc])
    num("line width", [m["lines"].get("width_pct_of_canvas") for m in ms], "% of canvas", 0.5)
    num("fill flatness", [m["surface"]["flat_pct"] for m in ms], "%", 0.15)
    num("edge softness", [m["surface"]["edge_px"] for m in ms], "px", 0.5)
    num("grain", [m["surface"]["grain"] for m in ms], "", 1.0)
    num("ink coverage", [m["subject"]["ink_pct"] if m["subject"] else None for m in ms], "%", 0.3)
    cat("subject centred", [str(m["subject"]["centred"]) if m["subject"] else "-" for m in ms])

    shared = []
    for p in [x for x in ms[0]["palette"] if not x["blend"]]:
        c0 = tuple(int(p["color"][i:i + 2], 16) for i in (0, 2, 4))
        if all(any(dist(c0, tuple(int(q["color"][i:i + 2], 16) for i in (0, 2, 4))) <= 28
                   for q in m["palette"] if not q["blend"]) for m in ms[1:]):
            shared.append(p["color"])
    print(f"  shared colours (in every reference): " + ("  ".join("#" + c for c in shared) if shared else "none"))
    print("  Colours outside that list belong to a palette dial, not to the locked frame.")


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    if not a or "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__)
        sys.exit(2)
    if "--json" in sys.argv:
        a = [x for x in a if x != sys.argv[sys.argv.index("--json") + 1]]
    ms = [measure(p) for p in a]
    report(ms)
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        json.dump(ms, open(out, "w"), ensure_ascii=False, indent=2)
        print(f"\nWrote {out}")
