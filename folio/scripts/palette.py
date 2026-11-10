#!/usr/bin/env python3
# Modified by Okou: remove inherited personal-taste reference; palette algorithms
# and catalogue retained from the pinned Folio source under Apache-2.0.
"""
folio palette — turn a brand colour (or an industry) into print-ready role palettes, check them,
suggest better alternatives, and draw a swatch sheet the user can choose from.

Usage
  python palette.py --brand "#8B1E3F"                         # client colour → 3 options
  python palette.py --brand "#8B1E3F" --brand2 "#D4A017"      # two brand colours (second becomes accent)
  python palette.py --brand "#EE2C27" --accent "#0D0D0D" --check   # just audit a proposed palette
  python palette.py --industry "school annual report"         # no brand yet → curated picks by industry
  python palette.py --from-image logo.png --industry "school"  # read brand colours from the logo
  python palette.py ... --out palette                          # palette/swatches.png, options.json, tokens-<id>.css

Roles (see folio.css): paper, ink, ink-2, rule, brand, brand-ink, brand-deep, tint, accent.
Checks: WCAG contrast for every text role on the surfaces it will sit on; brand usable as text?;
CMYK risk for very saturated RGB colours; the "AI default" hues and cream-paper band; accent too
close to the brand. Every problem comes with the concrete fix.
"""
import argparse, csv, json, math, re, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data" / "palettes.csv"


# ---------- colour maths (sRGB <-> OKLab/OKLCH) ----------
def hex2rgb(h):
    h = h.strip().lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def rgb2hex(c):
    return "#" + "".join(f"{round(max(0, min(1, v)) * 255):02x}" for v in c)


def _lin(v): return v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4
def _gam(v): return 12.92 * v if v <= 0.0031308 else 1.055 * v ** (1 / 2.4) - 0.055


def rgb2oklch(c):
    r, g, b = (_lin(v) for v in c)
    l = 0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b
    m = 0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b
    s = 0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b
    l, m, s = (math.copysign(abs(v) ** (1 / 3), v) for v in (l, m, s))
    L = 0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s
    a = 1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s
    bb = 0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s
    return L, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360


def oklch2rgb(L, C, H):
    a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    r = 4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s
    g = -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s
    bl = -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s
    return tuple(_gam(max(0, v)) if v > 0 else 0 for v in (r, g, bl))


def in_gamut(L, C, H):
    a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    vals = (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)
    return all(-0.001 <= v <= 1.001 for v in vals)


def lch(L, C, H):
    """closest in-gamut colour at this L/H (reduce chroma until it fits)"""
    while C > 0 and not in_gamut(L, C, H):
        C -= 0.002
    return rgb2hex(oklch2rgb(L, max(C, 0), H))


def lum(hx):
    return sum(k * _lin(v) for k, v in zip((0.2126, 0.7152, 0.0722), hex2rgb(hx)))


def contrast(a, b):
    A, B = lum(a), lum(b)
    return (max(A, B) + 0.05) / (min(A, B) + 0.05)


def on_colour(bg, hue):
    """best text colour on a field: white, or a deep shade of the field's own hue"""
    deep = lch(0.2, 0.05, hue)
    return "#ffffff" if contrast("#ffffff", bg) >= contrast(deep, bg) else deep


# ---------- roles ----------
def roles(brand, accent=None, paper="#ffffff"):
    L, C, H = rgb2oklch(hex2rgb(brand))
    r = {"paper": paper, "brand": brand}
    r["ink"] = lch(0.19, min(0.012, C * 0.15), H)
    r["ink-2"] = lch(0.42, min(0.02, C * 0.2), H)
    while contrast(r["ink-2"], paper) < 4.8:
        L2 = rgb2oklch(hex2rgb(r["ink-2"]))[0] - 0.03
        r["ink-2"] = lch(L2, 0.015, H)
    r["rule"] = lch(0.88, min(0.015, C * 0.2), H)
    r["tint"] = lch(0.965, min(0.025, C * 0.25 + 0.005), H)
    r["brand-ink"] = on_colour(brand, H)
    # a text-safe shade of the brand for headings on paper
    deepL = min(L, 0.5)
    deep = lch(deepL, C, H)
    while contrast(deep, paper) < 4.5 and deepL > 0.15:
        deepL -= 0.02; deep = lch(deepL, C, H)
    r["brand-deep"] = deep
    r["accent"] = accent or pick_accents(brand)[0][1]
    return r


def pick_accents(brand):
    """candidate accents: complementary, split, analogous-warm, gold, ink — ranked"""
    L, C, H = rgb2oklch(hex2rgb(brand))
    cands = []
    # muted rather than neon: alternatives should look art-directed, not like UI states
    for name, dh, Lx, Cx in (("brass", None, 0.74, 0.12), ("complement", 180, 0.72, 0.085), ("split-warm", 150, 0.76, 0.09),
                             ("split-cool", 210, 0.70, 0.08), ("analogous", 40, 0.70, 0.11), ("signal", None, 0.88, 0.17)):
        h = (H + dh) % 360 if dh is not None else (80 if name == "brass" else 108)
        hx = lch(Lx, Cx, h)
        dist = min(abs(h - H), 360 - abs(h - H))
        score = (min(dist, 120) / 120) + min(contrast(hx, brand), 4.5) / 4.5 - (0.6 if 265 <= h <= 305 else 0) \
                + (0.6 if name == "brass" and L < 0.55 else 0) - (0.3 if name == "signal" and L > 0.5 else 0)
        cands.append((round(score, 3), hx, name))
    cands.sort(reverse=True)
    return [(s, hx, n) for s, hx, n in cands]


# ---------- checks ----------
def audit(r):
    out = []
    def need(fg, bg, lvl, what, fix):
        c = contrast(r[fg], r[bg])
        if c < lvl:
            out.append({"level": "fix", "issue": f"{what}: {r[fg]} on {r[bg]} is {c:.2f}:1 (needs {lvl})", "fix": fix})
    need("ink", "paper", 7, "body text", "darken ink toward L 0.2")
    need("ink-2", "paper", 4.5, "secondary text", f"use {lch(0.4, 0.015, rgb2oklch(hex2rgb(r['brand']))[2])}")
    need("ink", "tint", 7, "text on tint panels", "lighten the tint")
    need("brand-ink", "brand", 4.5, "text on brand fields", "use white or a deep shade of the brand hue for text on brand")
    Lb, Cb, Hb = rgb2oklch(hex2rgb(r["brand"]))
    if contrast(r["brand"], r["paper"]) < 3:
        out.append({"level": "note", "issue": f"brand {r['brand']} is too light to use as text on paper",
                    "fix": f"keep it for fields, stripes and big shapes; set brand-coloured headings in brand-deep {r['brand-deep']}"})
    ca = contrast(r["accent"], r["paper"]); cb = contrast(r["accent"], r["brand"])
    if ca < 3 and cb < 3:
        out.append({"level": "fix", "issue": f"accent {r['accent']} is weak on both paper ({ca:.1f}:1) and brand ({cb:.1f}:1)",
                    "fix": f"try {pick_accents(r['brand'])[0][1]}"})
    elif ca < 3:
        out.append({"level": "note", "issue": f"accent reads on brand fields ({cb:.1f}:1) but not as text on paper ({ca:.1f}:1)",
                    "fix": "use it for numerals/marks on brand or dark pages; on paper use it only as shapes"})
    La, Ca, Ha = rgb2oklch(hex2rgb(r["accent"]))
    if min(abs(Ha - Hb), 360 - abs(Ha - Hb)) < 20 and abs(La - Lb) < 0.15:
        out.append({"level": "fix", "issue": "accent is almost the same colour as the brand", "fix": f"try {pick_accents(r['brand'])[0][1]}"})
    for role in ("brand", "accent"):
        L, C, H = rgb2oklch(hex2rgb(r[role]))
        if C > 0.2 or (C > 0.16 and (140 <= H <= 175 or 255 <= H <= 300)):
            out.append({"level": "note", "issue": f"{role} {r[role]} is a vivid RGB colour that will print duller in CMYK",
                        "fix": "ask for the brand's CMYK/Pantone values; request a hard proof" })
    # the user's taste: no raw yellow, green or purple; their aesthetic versions are welcome
    RAW = (((75, 115), "yellow", "mustard #D4A22C or butter #F1D98A"),
           ((125, 165), "green", "olive #5E6B3A, sage #9DB39A or emerald #0F4D3A"),
           ((285, 335), "purple", "lavender #A796C9, lilac #C4B3DD or aubergine #3A1638"))
    for role in ("brand", "accent"):
        L, C, H = rgb2oklch(hex2rgb(r[role]))
        for (lo, hi), name, alt in RAW:
            if lo <= H <= hi and C > 0.15:
                out.append({"level": "fix", "issue": f"{role} {r[role]} is a raw {name}", "fix": f"use its aesthetic version: {alt}"})
    Lp, Cp, Hp = rgb2oklch(hex2rgb(r["paper"]))
    if 0.84 <= Lp <= 0.97 and Cp < 0.06 and 40 <= Hp <= 100 and Cp > 0.008:
        out.append({"level": "note", "issue": "cream paper is also a generated-design default",
                    "fix": "keep it when the style asks for it (Editorial Minimalist, Heritage, pastels) and pair it with a decisive ink; otherwise white"})
    return out


# ---------- industry data ----------
def search(query, n=3):
    rows = list(csv.DictReader(open(DATA, encoding="utf-8")))
    q = set(re.findall(r"[a-z]+", query.lower()))
    scored = []
    for r in rows:
        words = set(re.findall(r"[a-z]+", (r["industries"] + " " + r["name"] + " " + r["register"]).lower()))
        exact = q & words   # partial matches only for query words with no exact hit ("school" must not pull in "preschool")
        s = len(exact) + 0.3 * sum(1 for w in q - exact for x in words if len(w) > 3 and (w in x or x in w))
        reg = ("corporate" if re.search(r"report|annual|profile|prospectus|society|trust", query, re.I) else
               "catalog" if re.search(r"catalog|product|quotation|price|spec", query, re.I) else
               "magazine" if re.search(r"magazine|zine|lookbook|sport|fitness", query, re.I) else None)
        if reg and r["register"] == reg:
            s += 0.5
        if re.search(r"preschool|kindergarten|children", r["industries"]) and not re.search(r"kid|child|pre-?school|kinder|play", query, re.I):
            s -= 1.0   # audience-specific palettes only when the brief is about that audience
        scored.append((s, r))
    scored.sort(key=lambda t: -t[0])
    picks, lanes = [], set()
    for s, r in scored:              # spread across different directions ("schools")
        if r["direction"] in lanes:
            continue
        picks.append(r); lanes.add(r["direction"])
        if len(picks) == n:
            break
    return picks


# ---------- swatch sheet ----------
def swatches(options, dest):
    from PIL import Image, ImageDraw, ImageFont
    def font(sz, bold=False):
        for f in ("DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", "Arial.ttf"):
            try: return ImageFont.truetype(f, sz)
            except Exception: pass
        return ImageFont.load_default()
    W, H, pad = 420, 560, 28
    sheet = Image.new("RGB", (pad + len(options) * (W + pad), H + 150), "#e9eaec")
    d = ImageDraw.Draw(sheet)
    for i, o in enumerate(options):
        r = o["roles"]; x = pad + i * (W + pad); y = pad
        # mini spread: brand field page + paper page
        d.rectangle([x, y, x + W, y + H], fill=r["paper"])
        d.rectangle([x, y, x + W * 0.52, y + H], fill=r["brand"])
        d.text((x + 18, y + 26), o["label"], font=font(15, True), fill=r["brand-ink"])
        d.text((x + 18, y + 90), "24", font=font(74, True), fill=r["accent"])
        d.text((x + 18, y + 180), "Annual", font=font(34, True), fill=r["brand-ink"])
        d.text((x + 18, y + 220), "Report", font=font(34, True), fill=r["brand-ink"])
        d.rectangle([x + W * 0.52 + 16, y + 30, x + W - 16, y + 150], fill=r["tint"])
        d.text((x + W * 0.52 + 26, y + 42), "Heading", font=font(18, True), fill=r["brand-deep"])
        for k in range(5):
            d.rectangle([x + W * 0.52 + 26, y + 76 + k * 13, x + W - 30 - (k == 4) * 50, y + 81 + k * 13], fill=r["ink"])
        for k in range(9):
            d.rectangle([x + W * 0.52 + 16, y + 180 + k * 14, x + W - 16 - (k % 4 == 3) * 40, y + 185 + k * 14], fill=r["ink-2"] if k > 5 else r["ink"])
        d.line([x + W * 0.52 + 16, y + 320, x + W - 16, y + 320], fill=r["rule"], width=2)
        d.ellipse([x + W - 110, y + 350, x + W - 20, y + 440], fill=r["accent"])
        d.text((x + W * 0.52 + 16, y + 460), "42%", font=font(38, True), fill=r["brand-deep"])
        # chips
        cy = y + H + 14
        for j, k in enumerate(("paper", "ink", "ink-2", "brand", "brand-deep", "tint", "accent")):
            cx = x + j * 60
            d.rectangle([cx, cy, cx + 52, cy + 40], fill=r[k], outline="#9a9ca3")
            d.text((cx, cy + 44), k, font=font(10), fill="#333")
            d.text((cx, cy + 58), r[k], font=font(10), fill="#555")
        flags = [p for p in o["audit"] if p["level"] == "fix"]
        d.text((x, cy + 82), ("⚠ " + flags[0]["issue"][:62]) if flags else "✓ contrast checks pass", font=font(11), fill="#a0291e" if flags else "#1d6b35")
    sheet.save(dest)
    return dest


def from_image(path, n=2):
    """dominant chromatic colours of a logo / brand image (ignores white, black and greys)"""
    from PIL import Image
    im = Image.open(path).convert("RGBA")
    bg = Image.new("RGBA", im.size, (255, 255, 255, 255)); bg.alpha_composite(im)
    q = bg.convert("RGB").quantize(colors=12, method=Image.Quantize.MEDIANCUT)
    pal = q.getpalette(); counts = sorted(q.getcolors(), reverse=True)
    out = []
    for cnt, idx in counts:
        hx = rgb2hex(tuple(v / 255 for v in pal[idx * 3: idx * 3 + 3]))
        L, C, H = rgb2oklch(hex2rgb(hx))
        if C < 0.04 or L > 0.95 or L < 0.12:
            continue
        if all(abs(H - rgb2oklch(hex2rgb(o))[2]) % 360 > 18 for o in out):
            out.append(hx)
        if len(out) == n:
            break
    return out


def css(r, label):
    body = "\n".join(f"  --{k}: {v};" for k, v in r.items())
    return f"/* folio palette · {label} */\n:root{{\n{body}\n}}\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--brand"); ap.add_argument("--brand2"); ap.add_argument("--accent"); ap.add_argument("--paper", default="#ffffff")
    ap.add_argument("--industry"); ap.add_argument("--check", action="store_true")
    ap.add_argument("--from-image", help="logo or brand image to read the brand colours from")
    ap.add_argument("--out")
    a = ap.parse_args()
    options = []
    if a.from_image and not a.brand:
        found = from_image(a.from_image)
        if found:
            a.brand = found[0]; a.brand2 = a.brand2 or (found[1] if len(found) > 1 else None)
            print(json.dumps({"from_image": a.from_image, "colours": found}), file=sys.stderr)
    if a.brand:
        acc = a.accent or a.brand2
        base = roles(a.brand, acc, a.paper)
        options.append({"id": "A", "label": "Your brand", "strategy": "Committed", "roles": base})
        if not a.check:
            used = {base["accent"].lower()}
            for s, hx, name in pick_accents(a.brand):
                if hx.lower() in used: continue
                used.add(hx.lower())
                options.append({"id": chr(65 + len(options)), "label": f"+ {name} accent", "strategy": "Committed", "roles": roles(a.brand, hx, a.paper)})
                if len(options) == 3: break
    if a.industry or not a.brand:
        for row in search(a.industry or "corporate brochure", n=3 if not a.brand else 1):
            r = {"paper": row["paper"], "ink": row["ink"], "ink-2": row["ink2"], "rule": lch(0.88, 0.01, rgb2oklch(hex2rgb(row["brand"]))[2]),
                 "tint": row["tint"], "brand": row["brand"], "brand-ink": row["brand_ink"], "accent": row["accent"]}
            if row.get("support"):
                r["support"] = row["support"]   # an optional supporting colour, not a user-preference rule
            r["brand-deep"] = roles(row["brand"], row["accent"], row["paper"])["brand-deep"]
            options.append({"id": chr(65 + len(options)), "label": row["name"], "strategy": row["strategy"], "direction": row["direction"],
                            "note": row["note"], "roles": r})
    for o in options:
        o["audit"] = audit(o["roles"])
    res = {"options": [{k: v for k, v in o.items()} for o in options]}
    if a.out:
        out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
        res["swatches"] = str(swatches(options, out / "swatches.png"))
        for o in options:
            (out / f"tokens-{o['id']}.css").write_text(css(o["roles"], o["label"]))
        (out / "options.json").write_text(json.dumps(res, indent=2))
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # Windows consoles default to cp1252 and crash on ■ — “
    main()
