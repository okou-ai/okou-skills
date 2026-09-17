#!/usr/bin/env python3
"""Check a generated piece against the references it claims to match.

Usage:  python3 check_piece.py --refs <ref> [<ref> ...] --piece <image> [<image> ...]

Passes when every measurable axis of the piece falls inside the range the
references set. Covers canvas, background, palette structure, line colour and
weight, fill flatness, edge softness, grain and subject geometry. It cannot
see subject conventions, motif vocabulary or medium; check those by eye.
Exit code 0 when every piece passes.
"""
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from measure_style import HEX, dist, measure  # noqa: E402


def band(values, rel=0.25, floor=0.0):
    lo, hi = min(values), max(values)
    pad = max(floor, lo * rel)
    return lo - pad, hi + pad


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def check(refs, piece):
    out, bad = [], 0
    # A reference smaller than MIN_SIDE cannot speak for colour or stroke: its
    # own downscaling produced those values. Those axes are reported and not
    # counted.
    coarse = all(m.get("low_res") for m in refs)
    soft = {"line colour", "line width", "fill flatness", "grain"} if coarse else set()

    def row(name, want, got, ok):
        nonlocal bad
        excused = name in soft or (coarse and name.startswith("locked colour"))
        bad += 0 if (ok or excused) else 1
        mark = "ok" if ok else ("not counted" if excused else "DIFF")
        out.append(f"  {name:20} {str(want):>26} {str(got):>26}  {mark}")

    rc = {(m["canvas"]["w"], m["canvas"]["h"]) for m in refs}
    pc = (piece["canvas"]["w"], piece["canvas"]["h"])
    ra = [m["canvas"]["aspect"] for m in refs]
    row("canvas", "/".join(f"{w}x{h}" for w, h in rc), f"{pc[0]}x{pc[1]}",
        abs(piece["canvas"]["aspect"] - min(ra, key=lambda a: abs(a - piece["canvas"]["aspect"]))) <= 0.02)

    rbg = [rgb(m["background"]["color"]) for m in refs]
    pbg = rgb(piece["background"]["color"])
    row("background colour", "#" + refs[0]["background"]["color"], "#" + piece["background"]["color"],
        min(dist(pbg, c) for c in rbg) <= 20)
    row("background kind", "/".join({m["background"]["kind"] for m in refs}), piece["background"]["kind"],
        piece["background"]["kind"] in {m["background"]["kind"] for m in refs})

    rl = [m["lines"] for m in refs if m["lines"]["present"]]
    if rl and piece["lines"]["present"]:
        want = {bool(l.get("contour")) for l in rl}
        got = bool(piece["lines"].get("contour"))
        row("drawn contour", "/".join("yes" if v else "no" for v in want),
            "yes" if got else "no", got in want)
        row("line colour", "#" + rl[0]["color"], "#" + piece["lines"]["color"],
            min(dist(rgb(piece["lines"]["color"]), rgb(l["color"])) for l in rl) <= 40)
        lo, hi = band([l["width_pct_of_canvas"] for l in rl], 0.35)
        w = piece["lines"]["width_pct_of_canvas"]
        row("line width", f"{lo:.2f}-{hi:.2f}% of canvas", f"{w}%", lo <= w <= hi)
    elif rl or piece["lines"]["present"]:
        row("line structure", "present" if rl else "none",
            "present" if piece["lines"]["present"] else "none", False)

    for key, name, rel, floor in (("flat_pct", "fill flatness", 0.12, 4),
                                  ("edge_px", "edge softness", 0.5, 1),
                                  ("grain", "grain", 1.0, 0.3)):
        vals = [m["surface"][key] for m in refs if m["surface"][key] is not None]
        got = piece["surface"][key]
        if not vals or got is None:
            continue
        lo, hi = band(vals, rel, floor)
        row(name, f"{lo:.2f}-{hi:.2f}", got, lo <= got <= hi)

    if piece["subject"] and all(m["subject"] for m in refs):
        lo, hi = band([m["subject"]["ink_pct"] for m in refs], 0.5, 5)
        row("ink coverage", f"{lo:.1f}-{hi:.1f}%", f"{piece['subject']['ink_pct']}%",
            lo <= piece["subject"]["ink_pct"] <= hi)
        want = {m["subject"]["centred"] for m in refs}
        row("subject centred", "/".join(str(v) for v in want), str(piece["subject"]["centred"]),
            piece["subject"]["centred"] in want)

    # A locked palette colour is one every reference carries. The piece must
    # carry it too; its own accent is expected to be new and is not checked.
    def solid(m):
        return [p for p in m["palette"] if not p["blend"] and p["share_pct"] >= 1.5]
    shared = []
    for p in solid(refs[0]):
        c = rgb(p["color"])
        if all(any(dist(c, rgb(q["color"])) <= 28 for q in solid(m)) for m in refs[1:]):
            shared.append(p["color"])
    for c in shared:
        got = min((dist(rgb(c), rgb(q["color"])), q["color"]) for q in solid(piece))
        row(f"locked colour #{c}", "present", "#" + got[1], got[0] <= 34)
    if not shared:
        out.append(f"  {'locked colours':20} {'none shared by all refs':>26} {'-':>26}  n/a")
    if coarse:
        out.append("  every reference is under 400px: colour and stroke axes are reported"
                   " but not counted")
    return out, bad


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or "--refs" not in a or "--piece" not in a:
        print(__doc__)
        sys.exit(2)
    i, j = a.index("--refs"), a.index("--piece")
    ref_paths = a[i + 1:j] if i < j else a[i + 1:]
    piece_paths = a[j + 1:] if j > i else a[j + 1:i]
    refs = [measure(p) for p in ref_paths]
    failed = 0
    for pp in piece_paths:
        piece = measure(pp)
        rows, bad = check(refs, piece)
        print(f"\n=== {piece['file']} against {len(refs)} reference(s)")
        print(f"  {'':20} {'references':>26} {'piece':>26}")
        print("\n".join(rows))
        print(f"  {'FAIL' if bad else 'PASS'}: {bad} axis/axes outside the reference range")
        failed += bad
    print("\nAxes this cannot see: medium, line quality, shape language, subject "
          "conventions,\nmotif vocabulary, composition meaning. Look at the piece for those.")
    sys.exit(1 if failed else 0)
