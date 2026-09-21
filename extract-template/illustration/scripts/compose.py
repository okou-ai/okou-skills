#!/usr/bin/env python3
"""Place a generated piece at the reference's scale and position.

Usage:  python3 compose.py --ref <reference> --piece <image> --out <image>

Some models will not honour how large the drawing should sit in the frame,
however the prompt says it. On a plain ground the drawing can be placed after
the fact: its ink box is scaled and positioned to the fractions the reference
measures. Nothing inside the drawing changes.
"""
import sys

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from measure_style import background, dist, load, subject  # noqa: E402

import pymupdf  # noqa: E402


def ink_box(rows, w, h, bgc):
    x0, y0, x1, y1 = w, h, -1, -1
    for y in range(h):
        row = rows[y]
        for x in range(w):
            if dist(row[x], bgc) > 18:
                if x < x0: x0 = x
                if x > x1: x1 = x
                if y < y0: y0 = y
                if y > y1: y1 = y
    return x0, y0, x1, y1


def main(ref_path, piece_path, out_path):
    rrows, _, rw, rh = load(ref_path)
    rbg = background(rrows, rw, rh)
    rprobe = subject(rrows, rw, rh, rbg)
    tw_frac = rprobe["box_pct"][0] / 100
    th_frac = rprobe["box_pct"][1] / 100
    lx = rprobe["margins_pct"]["left"] / 100
    ty = rprobe["margins_pct"]["top"] / 100

    prows, _, pw, ph = load(piece_path)
    pbg = background(prows, pw, ph)
    bgc = tuple(int(pbg["color"][i:i + 2], 16) for i in (0, 2, 4))
    x0, y0, x1, y1 = ink_box(prows, pw, ph, bgc)
    bw, bh = x1 - x0 + 1, y1 - y0 + 1

    # one scale for both axes, so nothing is stretched
    k = min(tw_frac * pw / bw, th_frac * ph / bh)
    nw, nh = max(1, round(bw * k)), max(1, round(bh * k))
    ox, oy = round(lx * pw), round(ty * ph)
    ox = min(ox, pw - nw)
    oy = min(oy, ph - nh)

    white = (255, 255, 255)
    out = bytearray()
    for y in range(ph):
        sy = y0 + int((y - oy) * bh / nh) if oy <= y < oy + nh else -1
        for x in range(pw):
            if sy < 0 or not (ox <= x < ox + nw):
                out += bytes(white)
                continue
            sx = x0 + int((x - ox) * bw / nw)
            out += bytes(prows[min(sy, ph - 1)][min(sx, pw - 1)])
    pix = pymupdf.Pixmap(pymupdf.csRGB, pw, ph, bytes(out), 0)
    pix.save(out_path)
    print(f"{out_path}: ink box {bw}x{bh} -> {nw}x{nh} at ({ox},{oy}) on {pw}x{ph}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not {"--ref", "--piece", "--out"} <= set(a):
        print(__doc__)
        sys.exit(2)
    g = lambda k: a[a.index(k) + 1]
    main(g("--ref"), g("--piece"), g("--out"))
