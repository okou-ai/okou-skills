#!/usr/bin/env python3
"""Turn any .docx into a usable Pandoc --reference-doc template.

Usage:  python3 build_reference.py source.docx reference.docx

Three things happen:
  1. The source stylesheet, theme, header/footer, numbering and page setup are
     carried over byte for byte.
  2. The body is replaced with a style sampler: one paragraph per style, whose
     text is the style name.
  3. Missing Pandoc styles are added. Heading levels are derived from the
     neighbouring levels already in the document; anything else is taken from
     pandoc's default template and rebased onto the document's body font.

Requires pandoc on PATH.
"""
import sys, os, re, zipfile, shutil, subprocess, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandoc_styles as PS

HALF2PT = lambda h: int(h) / 2
PT2HALF = lambda pt: int(round(pt * 2))
TWIP2PT = lambda t: int(t) / 20
PT2TWIP = lambda pt: int(round(pt * 20))


def style_map(xml):
    """{lowercased w:name: (styleId, full XML)}. Keyed by name; Pandoc matches on it."""
    out = {}
    for m in re.finditer(r"<w:style\b[^>]*?w:styleId=\"([^\"]+)\"[^>]*>(.*?)</w:style>", xml, re.S):
        n = re.search(r"<w:name\s+w:val=\"([^\"]*)\"", m.group(2))
        if n:
            out[n.group(1).lower()] = (m.group(1), m.group(0))
    return out


def default_reference():
    tmp = tempfile.mkdtemp()
    p = os.path.join(tmp, "ref.docx")
    subprocess.run(["pandoc", "-o", p, "--print-default-data-file", "reference.docx"],
                   check=True, capture_output=True)
    return p, tmp


def normal_rfonts(styles_xml, smap):
    """The source document's Normal <w:rFonts>, applied to injected styles."""
    entry = smap.get("normal")
    if not entry:
        return None
    f = re.search(r"<w:rFonts\b[^>]*/>", entry[1])
    return f.group(0) if f else None


def sample_body(smap, sect_xml, paragraph_names):
    """One paragraph per style, with the style name as its text."""
    ps = []
    for n in paragraph_names:
        hit = smap.get(n.lower())
        if not hit:
            continue
        ps.append(f'<w:p><w:pPr><w:pStyle w:val="{hit[0]}"/></w:pPr>'
                  f'<w:r><w:t xml:space="preserve">{n}</w:t></w:r></w:p>')
    return "".join(ps) + sect_xml


def look_of(xml):
    """Read the visual parameters out of a style definition."""
    rpr = re.search(r"<w:rPr>.*?</w:rPr>", xml, re.S)
    r = rpr.group(0) if rpr else ""
    ppr = re.search(r"<w:pPr>.*?</w:pPr>", xml, re.S)
    p = ppr.group(0) if ppr else ""
    grab = lambda pat, src: (lambda m: m.group(1) if m else None)(re.search(pat, src))
    sz = grab(r'<w:sz w:val="(\d+)"', r)
    return {
        "fonts": grab(r"(<w:rFonts\b[^>]*/>)", r),
        "bold": "<w:b/>" in r or "<w:b />" in r,
        "color": grab(r'<w:color w:val="([0-9A-Fa-f]{6})"', r),
        "size": HALF2PT(sz) if sz else None,
        "before": (lambda v: TWIP2PT(v) if v else None)(
            grab(r'<w:spacing[^>]*w:before="(\d+)"', p)),
        "after": (lambda v: TWIP2PT(v) if v else None)(
            grab(r'<w:spacing[^>]*w:after="(\d+)"', p)),
    }


def derive_heading(level, have):
    """Derive a missing heading level from the neighbouring levels in the document.

    Better than copying pandoc's default, which brings its own theme font and
    colour and would then need adjusting by hand.
    """
    known = {}
    for i in range(1, 10):
        hit = have.get(f"heading {i}")
        if hit:
            known[i] = look_of(hit[1])
    known = {k: v for k, v in known.items() if v["size"]}
    if not known:
        return None
    lower = max((k for k in known if k < level), default=None)   # lower number = larger text
    upper = min((k for k in known if k > level), default=None)

    if lower and upper:      # bracketed: interpolate the size across the levels
        a, b = known[lower], known[upper]
        t = (level - lower) / (upper - lower)
        size = a["size"] + (b["size"] - a["size"]) * t
        src = ref = a
    elif lower:              # only a larger level: shrink 15% per level
        src = ref = known[lower]
        size = src["size"] * (0.85 ** (level - lower))
    else:                    # only a smaller level: grow
        src = ref = known[upper]
        size = src["size"] / (0.85 ** (upper - level))

    size = max(round(size * 2) / 2, 8.0)     # round to 0.5pt, floor at 8pt
    rpr = (ref["fonts"] or "") + ("<w:b/>" if ref["bold"] else "")
    if ref["color"]:
        rpr += f'<w:color w:val="{ref["color"]}"/>'
    rpr += f'<w:sz w:val="{PT2HALF(size)}"/><w:szCs w:val="{PT2HALF(size)}"/>'
    spacing = ""
    if src["before"] or src["after"]:
        bits = []
        if src["before"]:
            bits.append(f'w:before="{PT2TWIP(src["before"])}"')
        if src["after"]:
            bits.append(f'w:after="{PT2TWIP(src["after"])}"')
        spacing = f'<w:spacing {" ".join(bits)}/>'
    basis = f"heading {lower}" if lower else f"heading {upper}"
    return rpr, spacing, size, basis


def _spacing_of(styles_xml, sid):
    """before / after / first-line indent in pt, for the report."""
    m = re.search(rf'<w:style\b[^>]*?w:styleId="{re.escape(sid)}"[^>]*>(.*?)</w:style>',
                  styles_xml, re.S)
    if not m:
        return ("-", "-", "-")
    p = re.search(r"<w:pPr>.*?</w:pPr>", m.group(1), re.S)
    p = p.group(0) if p else ""
    g = lambda a: (lambda mm: str(round(int(mm.group(1)) / 20, 1)) if mm else "-")(
        re.search(rf'<w:spacing[^>]*w:{a}="(\d+)"', p))
    ind = re.search(r'<w:ind[^>]*w:(?:firstLine|left)="(\d+)"', p)
    return (g("before"), g("after"), str(round(int(ind.group(1)) / 20, 1)) if ind else "-")


def build(src_path, out_path):
    with zipfile.ZipFile(src_path) as src:
        members = [(i.filename, src.read(i.filename)) for i in src.infolist()]
        names = [f for f, _ in members]
    blob = dict(members)
    styles = blob["word/styles.xml"].decode("utf-8", "replace")
    doc = blob["word/document.xml"].decode("utf-8", "replace")

    have = style_map(styles)
    missing = [n for n in PS.MUST_EXIST + PS.AUTO_INJECTED if n.lower() not in have]

    injected, unavailable, derived = [], [], []
    if missing:
        dref, tmp = default_reference()
        with zipfile.ZipFile(dref) as dz:
            dmap = style_map(dz.read("word/styles.xml").decode("utf-8", "replace"))
        shutil.rmtree(tmp, ignore_errors=True)
        rf = normal_rfonts(styles, have)
        used_ids = {v[0] for v in have.values()}
        blocks = []
        for n in missing:
            hit = dmap.get(n.lower())
            if not hit:
                unavailable.append(n)
                continue
            sid, xml = hit
            if sid in used_ids:                       # styleId collision, rename
                new = sid + "P"
                xml = xml.replace(f'w:styleId="{sid}"', f'w:styleId="{new}"', 1)
                sid = new
            m = re.fullmatch(r"heading (\d)", n)
            d = derive_heading(int(m.group(1)), have) if m else None
            if d:
                drpr, dspacing, dsize, basis = d
                xml = re.sub(r"<w:rPr>.*?</w:rPr>", f"<w:rPr>{drpr}</w:rPr>", xml, flags=re.S)
                if dspacing:
                    xml = re.sub(r'<w:spacing\b[^>]*/>', dspacing, xml, count=1)
                derived.append((n, dsize, basis))
            elif rf:
                xml = re.sub(r"<w:rFonts\b[^>]*/>", rf, xml)
            blocks.append(xml)
            used_ids.add(sid)
            have[n.lower()] = (sid, xml)
            injected.append(n)
        styles = styles.replace("</w:styles>", "".join(blocks) + "</w:styles>")

    # body -> style sampler; sectPr kept as is (header/footer refs, paper, margins)
    sect = re.search(r"<w:sectPr\b.*?</w:sectPr>|<w:sectPr\b[^>]*/>", doc, re.S)
    sect_xml = sect.group(0) if sect else "<w:sectPr/>"
    doc = re.sub(r"(<w:body>).*?(</w:body>)",
                 lambda m: m.group(1) + sample_body(have, sect_xml, PS.PARAGRAPH) + m.group(2),
                 doc, flags=re.S)

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as out:
        for fn, data in members:
            if fn == "word/styles.xml":
                data = styles.encode("utf-8")
            elif fn == "word/document.xml":
                data = doc.encode("utf-8")
            out.writestr(fn, data)

    hf = [n for n in names if re.match(r"word/(header|footer)\d+\.xml", n)]
    kept = [os.path.basename(n) for n in ("word/theme/theme1.xml", "word/numbering.xml")
            if n in names]
    print(f"{src_path}  ->  {out_path}")
    print(f"  {len(have) - len(injected)} existing styles, {len(injected)} added"
          + (f": {', '.join(injected)}" if injected else ""))
    print(f"  kept: {', '.join(kept) or '(no theme or numbering)'}"
          + (f", {len(hf)} header/footer parts" if hf else ", no header/footer"))
    print(f"  body replaced with a style sampler")
    if unavailable:
        print(f"  .   {', '.join(unavailable)}: absent from pandoc's default template "
              f"too; the writer generates them, nothing to add")

    print("\n  Paragraph settings of existing styles carry over unchanged — styles.xml "
          "is copied\n  wholesale and only appended to. Run inspect_docx.py to see the values.")

    if derived:
        print(f"\n  OK  {len(derived)} heading levels derived from neighbouring levels "
              f"in this document:")
        for n, size, basis in derived:
            print(f"     {n:<14}{size:>6}pt   (font/colour/spacing from {basis}, "
                  f"size interpolated)")

    plain = [n for n in injected if n not in {d[0] for d in derived}]
    if plain:
        print(f"\n  NOTE  {len(plain)} styles use pandoc's default spacing, which may not "
              f"match this document:")
        print(f"     {'style':<18}{'before':>7}{'after':>7}{'indent':>8}")
        for n in ["Body Text"] + plain:
            sid = have.get(n.lower(), ("", ""))[0]
            row = _spacing_of(styles, sid)
            tag = "  <- this document's body text, match against it" if n == "Body Text" else ""
            print(f"     {n:<18}{row[0]:>7}{row[1]:>7}{row[2]:>8}{tag}")
        print("     Adjust with set_style.py if needed; the template is deliverable "
              "either way.")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    build(sys.argv[1], sys.argv[2])
