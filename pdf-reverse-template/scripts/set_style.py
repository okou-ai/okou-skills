#!/usr/bin/env python3
"""Edit a style definition inside reference.docx. No Word required.

Usage:
  python3 set_style.py <reference.docx> --list
  python3 set_style.py <reference.docx> "Block Text" --size 10.5 --color 6C757D --before 6 --after 6
  python3 set_style.py <reference.docx> "heading 2" --font "Arial" --bold --size 16 --align left

Styles are addressed by <w:name> ("heading 2", "Body Text"), not by styleId —
that is what Pandoc matches on. Names are case-insensitive.
Edits happen in place unless --out is given.

Options:
  --font NAME      font family (written to ascii/hAnsi/eastAsia/cs so CJK text
                   does not fall back to a default serif)
  --size PT        font size
  --color RRGGBB   text colour
  --bold/--no-bold, --italic/--no-italic
  --before PT      space before      --after PT   space after
  --line PT        line spacing (written as atLeast so tall glyphs are not clipped)
  --indent PT      first-line indent --left-indent PT  left indent
  --align left|center|right|both
  --keep-next/--no-keep-next   keep with next paragraph
  --create         create the style when the template does not define it
                   (the only way to add Source Code, which pandoc omits)
  --character      with --create, build a character style instead of a paragraph style
"""
import sys, os, re, shutil, zipfile

PT2HALF = lambda pt: int(round(float(pt) * 2))
PT2TWIP = lambda pt: int(round(float(pt) * 20))
TWIP2PT = lambda t: round(int(t) / 20, 1)
HALF2PT = lambda h: round(int(h) / 2, 1)

# CT_PPrBase child order. Word rejects the file when the order is wrong.
PPR_ORDER = ["pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr",
             "widowControl", "numPr", "suppressLineNumbers", "pBdr", "shd", "tabs",
             "suppressAutoHyphens", "kinsoku", "wordWrap", "overflowPunct",
             "topLinePunct", "autoSpaceDE", "autoSpaceDN", "bidi", "adjustRightInd",
             "snapToGrid", "spacing", "ind", "contextualSpacing", "mirrorIndents",
             "suppressOverlap", "jc", "textDirection", "textAlignment",
             "textboxTightWrap", "outlineLvl", "divId", "cnfStyle"]
# CT_RPr child order.
RPR_ORDER = ["rStyle", "rFonts", "b", "bCs", "i", "iCs", "caps", "smallCaps", "strike",
             "dstrike", "outline", "shadow", "emboss", "imprint", "noProof",
             "snapToGrid", "vanish", "webHidden", "color", "spacing", "w", "kern",
             "position", "sz", "szCs", "highlight", "u", "effect", "bdr", "shd",
             "fitText", "vertAlign", "rtl", "cs", "em", "lang", "eastAsianLayout",
             "specVanish", "oMath"]


def split_children(xml):
    """Return [(tag name, full element XML), ...]"""
    out = []
    for m in re.finditer(r"<w:([a-zA-Z]+)\b[^>]*?/>|<w:([a-zA-Z]+)\b[^>]*?>.*?</w:\2>",
                         xml or "", re.S):
        out.append(((m.group(1) or m.group(2)), m.group(0)))
    return out


def merge(existing, new_elems, order):
    """Replace same-named elements (never append), then sort into schema order.

    Appending would leave two <w:spacing> siblings; the later one wins, so the
    value being set here would be silently overridden by the existing one.
    """
    rank = {n: i for i, n in enumerate(order)}
    items = [kv for kv in split_children(existing) if kv[0] not in new_elems]
    items += list(new_elems.items())
    items.sort(key=lambda kv: rank.get(kv[0], len(order)))
    return "".join(x for _, x in items)


def styles_map(xml):
    """{lowercased w:name: (styleId, full style XML, span)}"""
    out = {}
    for m in re.finditer(r"<w:style\b[^>]*?w:styleId=\"([^\"]+)\"[^>]*>(.*?)</w:style>",
                         xml, re.S):
        n = re.search(r"<w:name\s+w:val=\"([^\"]*)\"", m.group(2))
        if n:
            out[n.group(1).lower()] = (m.group(1), m.group(0), m.span())
    return out


def describe(style_xml):
    rpr = re.search(r"<w:rPr>.*?</w:rPr>", style_xml, re.S)
    ppr = re.search(r"<w:pPr>.*?</w:pPr>", style_xml, re.S)
    r, p = (rpr.group(0) if rpr else ""), (ppr.group(0) if ppr else "")
    g = lambda pat, src: (lambda m: m.group(1) if m else None)(re.search(pat, src))
    sz = g(r'<w:sz w:val="(\d+)"', r)
    ind = g(r'<w:ind[^>]*w:firstLine="(\d+)"', p)
    left = g(r'<w:ind[^>]*w:left="(\d+)"', p)
    bits = []
    if g(r'w:ascii="([^"]*)"', r):
        bits.append(g(r'w:ascii="([^"]*)"', r))
    if sz:
        bits.append(f"{HALF2PT(sz)}pt")
    if g(r'<w:color w:val="([0-9A-Fa-f]{6})"', r):
        bits.append("#" + g(r'<w:color w:val="([0-9A-Fa-f]{6})"', r))
    if "<w:b/>" in r or "<w:b />" in r:
        bits.append("bold")
    for attr, label in (("before", "before"), ("after", "after"), ("line", "line")):
        v = g(rf'<w:spacing[^>]*w:{attr}="(\d+)"', p)
        if v:
            bits.append(f"{label} {TWIP2PT(v)}")
    if ind:
        bits.append(f"indent {TWIP2PT(ind)}")
    if left:
        bits.append(f"left {TWIP2PT(left)}")
    jc = g(r'<w:jc w:val="([a-z]+)"', p)
    if jc:
        bits.append(jc)
    return " ".join(bits) or "(everything inherited)"


def main():
    a = sys.argv[1:]
    if not a:
        print(__doc__)
        return 2
    path = a[0]
    with zipfile.ZipFile(path) as z:
        members = [(i.filename, z.read(i.filename)) for i in z.infolist()]
    styles = dict(members)["word/styles.xml"].decode("utf-8", "replace")
    smap = styles_map(styles)

    if "--list" in a:
        print(f"Styles in {os.path.basename(path)} (by w:name):\n")
        for name in sorted(smap):
            sid, xml, _ = smap[name]
            print(f"  {name:<24}[{sid}]  {describe(xml)}")
        return 0

    if len(a) < 2 or a[1].startswith("--"):
        print("Missing style name. Run --list to see what is available.")
        return 2
    target = a[1].lower()
    if target not in smap:
        if "--create" not in a:
            print(f"No style named {a[1]!r}. Run --list to see what is available, "
                  f"or pass --create to add it.")
            return 1
        sid = re.sub(r"[^A-Za-z0-9]", "", a[1]) or "CustomStyle"
        if any(v[0] == sid for v in smap.values()):
            sid += "X"
        kind = "character" if "--character" in a else "paragraph"
        based = "Normal" if kind == "paragraph" else "DefaultParagraphFont"
        block = (f'<w:style w:type="{kind}" w:customStyle="1" w:styleId="{sid}">'
                 f'<w:name w:val="{a[1]}"/><w:basedOn w:val="{based}"/>'
                 f'<w:qFormat/><w:rPr></w:rPr></w:style>')
        styles = styles.replace("</w:styles>", block + "</w:styles>")
        smap = styles_map(styles)
        print(f"created style {a[1]!r}  [{sid}]  type={kind}")

    opt = lambda k: a[a.index(k) + 1] if k in a else None
    rpr_new, ppr_new = {}, {}

    if opt("--font"):
        f = opt("--font")
        rpr_new["rFonts"] = (f'<w:rFonts w:ascii="{f}" w:hAnsi="{f}" '
                             f'w:eastAsia="{f}" w:cs="{f}"/>')
    if opt("--size"):
        s = PT2HALF(opt("--size"))
        rpr_new["sz"] = f'<w:sz w:val="{s}"/>'
        rpr_new["szCs"] = f'<w:szCs w:val="{s}"/>'
    if opt("--color"):
        rpr_new["color"] = f'<w:color w:val="{opt("--color").lstrip("#").upper()}"/>'
    if "--bold" in a:
        rpr_new["b"] = "<w:b/>"
    if "--no-bold" in a:
        rpr_new["b"] = ""
    if "--italic" in a:
        rpr_new["i"] = "<w:i/>"
    if "--no-italic" in a:
        rpr_new["i"] = ""

    sp = {}
    for k, attr in (("--before", "before"), ("--after", "after")):
        if opt(k):
            sp[attr] = PT2TWIP(opt(k))
    if opt("--line"):
        sp["line"] = PT2TWIP(opt("--line"))
        sp["lineRule"] = "atLeast"
    if sp:
        # keep any spacing attributes that are not being overridden
        old = re.search(r"<w:pPr>.*?</w:pPr>", smap[target][1], re.S)
        prev = re.search(r"<w:spacing\b[^>]*/>", old.group(0) if old else "")
        keep = dict(re.findall(r'w:(\w+)="([^"]*)"', prev.group(0))) if prev else {}
        keep.update({k: str(v) for k, v in sp.items()})
        ppr_new["spacing"] = "<w:spacing " + " ".join(
            f'w:{k}="{v}"' for k, v in keep.items()) + "/>"
    ind = {}
    if opt("--indent"):
        ind["firstLine"] = PT2TWIP(opt("--indent"))
    if opt("--left-indent"):
        ind["left"] = PT2TWIP(opt("--left-indent"))
    if ind:
        ppr_new["ind"] = "<w:ind " + " ".join(f'w:{k}="{v}"' for k, v in ind.items()) + "/>"
    if opt("--align"):
        ppr_new["jc"] = f'<w:jc w:val="{opt("--align")}"/>'
    if "--keep-next" in a:
        ppr_new["keepNext"] = "<w:keepNext/>"
    if "--no-keep-next" in a:
        ppr_new["keepNext"] = ""

    if not rpr_new and not ppr_new:
        print(f"{a[1]}  current: {describe(smap[target][1])}\n(no change requested)")
        return 0

    sid, xml, (s0, s1) = smap[target]
    before = describe(xml)

    def patch_block(block, tag, new, order):
        m = re.search(rf"<w:{tag}>.*?</w:{tag}>", block, re.S)
        inner = re.sub(rf"</?w:{tag}>", "", m.group(0)) if m else ""
        merged = merge(inner, {k: v for k, v in new.items() if v}, order)
        for k, v in new.items():                 # empty string means remove
            if not v:
                merged = re.sub(rf"<w:{k}\b[^>]*/>", "", merged)
        rebuilt = f"<w:{tag}>{merged}</w:{tag}>"
        return (block[:m.start()] + rebuilt + block[m.end():]) if m else \
               block.replace("</w:style>", rebuilt + "</w:style>")

    if ppr_new:
        xml = patch_block(xml, "pPr", ppr_new, PPR_ORDER)
    if rpr_new:
        xml = patch_block(xml, "rPr", rpr_new, RPR_ORDER)

    styles = styles[:s0] + xml + styles[s1:]
    out = a[a.index("--out") + 1] if "--out" in a else path
    tmp = out + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for fn, data in members:
            z.writestr(fn, styles.encode("utf-8") if fn == "word/styles.xml" else data)
    shutil.move(tmp, out)

    print(f"{a[1]}  [{sid}]")
    print(f"  before: {before}")
    print(f"  after:  {describe(xml)}")
    print(f"  -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
