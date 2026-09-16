#!/usr/bin/env python3
"""Write the inferred PDF styles into a Pandoc reference.docx.

Usage:
  python3 build_reference.py styles.json out.docx
  python3 build_reference.py styles.json out.docx --map 1=Title,2=Heading1,3=Heading2
  python3 build_reference.py styles.json out.docx --bottom 3.0

--map corrects the level assignment. analyze_pdf orders heading clusters by
size, but a document title and an H1 are both just large text in a PDF, so the
mapping has to be stated explicitly. The left side is the cluster number from
the analysis report; the right side is a Word style name.

--bottom overrides the bottom margin (analyze_pdf can only bound it; the
default is to reuse the top margin).

Requires pandoc on PATH.
"""
import sys, os, re, json, zipfile, shutil, subprocess, tempfile

CM2TWIP = lambda cm: int(round(cm / 2.54 * 1440))   # cm -> twips
PT2TWIP = lambda pt: int(round(pt * 20))            # pt -> twips (spacing, indent)
PT2HALF = lambda pt: int(round(pt * 2))             # pt -> half-points (font size)


def fmt_sp(after, line, indent, before, align=None):
    """One-line paragraph summary for the report."""
    bits = []
    if before:            bits.append(f"before {before}")
    if after:             bits.append(f"after {after}")
    if line:              bits.append(f"line {line}")
    if indent:            bits.append(f"indent {indent}")
    if align == "center": bits.append("centered")
    return " ".join(bits) or "-"


# analyze_pdf reports the embedded PDF font name; map it back to a system name
SUFFIX = re.compile(r"[-,_](Bold|Regular|Italic|Oblique|Light|Medium|Semibold|Black|"
                    r"BoldItalic|Thin|ExtraBold|Heavy)$", re.I)


def clean_font(f):
    """ABCDEF+NotoSansCJKsc-Bold -> Noto Sans CJK SC"""
    f = re.sub(r"^[A-Z]{6}\+", "", f)             # drop the subset prefix
    f = SUFFIX.sub("", f)                          # drop the weight suffix
    f = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", f)     # split camel case
    # CJK region codes: CJKsc -> CJK SC
    f = re.sub(r"\bCJK(sc|tc|jp|kr|hk)\b", lambda m: "CJK " + m.group(1).upper(), f)
    return re.sub(r"\s+", " ", f).strip()


def default_reference():
    tmp = tempfile.mkdtemp()
    p = os.path.join(tmp, "ref.docx")
    subprocess.run(["pandoc", "-o", p, "--print-default-data-file", "reference.docx"],
                   check=True, capture_output=True)
    return p, tmp


def rpr(font, size, color, bold):
    f = clean_font(font)
    return (f'<w:rFonts w:ascii="{f}" w:hAnsi="{f}" w:eastAsia="{f}" w:cs="{f}"/>'
            + ("<w:b/>" if bold else "")
            + f'<w:color w:val="{color}"/>'
            + f'<w:sz w:val="{PT2HALF(size)}"/><w:szCs w:val="{PT2HALF(size)}"/>')


# CT_PPrBase child order. w:pPr accepts at most one of each element.
PPR_ORDER = [
    "pStyle", "keepNext", "keepLines", "pageBreakBefore", "framePr", "widowControl",
    "numPr", "suppressLineNumbers", "pBdr", "shd", "tabs", "suppressAutoHyphens",
    "kinsoku", "wordWrap", "overflowPunct", "topLinePunct", "autoSpaceDE",
    "autoSpaceDN", "bidi", "adjustRightInd", "snapToGrid", "spacing", "ind",
    "contextualSpacing", "mirrorIndents", "suppressOverlap", "jc", "textDirection",
    "textAlignment", "textboxTightWrap", "outlineLvl", "divId", "cnfStyle",
]
PPR_RANK = {n: i for i, n in enumerate(PPR_ORDER)}


def merge_ppr(existing, new_elems):
    """Merge into an existing pPr: replace same-named elements, then sort.

    Replacing matters: w:pPr allows only one w:spacing. Appending leaves two
    siblings and the later one wins, so the measured value would be silently
    overridden by the template's default.
    """
    items = []
    for m in re.finditer(r"<w:([a-zA-Z]+)\b[^>]*?/>|<w:([a-zA-Z]+)\b[^>]*?>.*?</w:\2>",
                         existing or "", re.S):
        items.append(((m.group(1) or m.group(2)), m.group(0)))
    override = {}
    for m in re.finditer(r"<w:([a-zA-Z]+)\b[^>]*?/>", new_elems or ""):
        override[m.group(1)] = m.group(0)
    items = [(n, x) for n, x in items if n not in override]
    items += list(override.items())
    items.sort(key=lambda kv: PPR_RANK.get(kv[0], len(PPR_ORDER)))
    return "".join(x for _, x in items)


def patch_style(xml, style_id, body_rpr, ppr_extra=""):
    """Replace the <w:rPr> of a styleId and merge ppr_extra into its <w:pPr>."""
    pat = rf'(<w:style\b[^>]*?w:styleId="{style_id}"[^>]*>)(.*?)(</w:style>)'
    m = re.search(pat, xml, re.S)
    if not m:
        return xml, False
    head, inner, tail = m.groups()
    if "<w:rPr>" in inner:
        inner = re.sub(r"<w:rPr>.*?</w:rPr>", f"<w:rPr>{body_rpr}</w:rPr>", inner, flags=re.S)
    else:
        inner += f"<w:rPr>{body_rpr}</w:rPr>"
    if ppr_extra:
        old = re.search(r"<w:pPr>(.*?)</w:pPr>", inner, re.S)
        merged = merge_ppr(old.group(1) if old else "", ppr_extra)
        if old:
            inner = inner[:old.start()] + f"<w:pPr>{merged}</w:pPr>" + inner[old.end():]
        else:
            inner = f"<w:pPr>{merged}</w:pPr>" + inner
    return xml[:m.start()] + head + inner + tail + xml[m.end():], True


def build(json_path, out_path, mapping, bottom_override):
    d = json.load(open(json_path))
    ref, tmp = default_reference()
    with zipfile.ZipFile(ref) as z:
        members = [(i.filename, z.read(i.filename)) for i in z.infolist()]
    shutil.rmtree(tmp, ignore_errors=True)
    blob = dict(members)
    styles = blob["word/styles.xml"].decode()
    doc = blob["word/document.xml"].decode()

    applied = []

    # --- body: font, line spacing, space after, first-line indent ---
    b = d["body"]
    ppr = ""
    sp = []
    if b.get("space_after_pt"):
        sp.append(f'w:after="{PT2TWIP(b["space_after_pt"])}"')
    if b.get("line_advance_pt"):
        # atLeast rather than exact; exact clips tall glyphs
        sp.append(f'w:line="{PT2TWIP(b["line_advance_pt"])}" w:lineRule="atLeast"')
    if sp:
        ppr += f'<w:spacing {" ".join(sp)}/>'
    fi = b.get("first_line_indent_pt") or 0
    indent_xml = f'<w:ind w:firstLine="{PT2TWIP(fi)}"/>' if fi else ""
    ppr += indent_xml
    for sid in ("BodyText", "FirstParagraph", "Compact", "Normal"):
        # Indent only Body Text: First Paragraph follows a heading and is not
        # indented by convention, and Compact is used for tight list items.
        p = ppr if sid == "BodyText" else ppr.replace(indent_xml, "")
        styles, ok = patch_style(styles, sid,
                                 rpr(b["font"], b["size"], b["color"], False), p)
        if ok:
            applied.append((sid, clean_font(b["font"]), b["size"], b["color"],
                            fmt_sp(b.get("space_after_pt"), b.get("line_advance_pt"),
                                   fi if sid == "BodyText" else 0, None)))

    # --- headings: font, space before/after, alignment ---
    for h in d["headings"]:
        target = mapping.get(str(h["level"]), f"Heading{h['level']}")
        if target.lower() in ("skip", "none", "-"):
            continue
        bold = bool(re.search(r"bold|black|heavy|semibold", h["font"], re.I))
        hp = ""
        hsp = []
        if h.get("space_before_pt"):
            hsp.append(f'w:before="{PT2TWIP(h["space_before_pt"])}"')
        if h.get("space_after_pt"):
            hsp.append(f'w:after="{PT2TWIP(h["space_after_pt"])}"')
        if hsp:
            hp += f'<w:spacing {" ".join(hsp)}/>'
        if h.get("align") == "center":
            hp += '<w:jc w:val="center"/>'
        styles, ok = patch_style(styles, target,
                                 rpr(h["font"], h["size"], h["color"], bold), hp)
        applied.append((target + ("" if ok else " NOT FOUND"),
                        clean_font(h["font"]), h["size"], h["color"],
                        fmt_sp(h.get("space_after_pt"), None, None,
                               h.get("space_before_pt"), h.get("align"))))

    # --- page ---
    p, mg = d["page"], d["margins_suggested_cm"]
    bottom = bottom_override if bottom_override is not None else mg.get("top")
    sect = (f'<w:sectPr><w:pgSz w:w="{CM2TWIP(p["w_cm"])}" w:h="{CM2TWIP(p["h_cm"])}"/>'
            f'<w:pgMar w:top="{CM2TWIP(mg["top"])}" w:right="{CM2TWIP(mg["right"])}" '
            f'w:bottom="{CM2TWIP(bottom)}" w:left="{CM2TWIP(mg["left"])}" '
            f'w:header="708" w:footer="708" w:gutter="0"/></w:sectPr>')
    doc = re.sub(r"<w:sectPr\b.*?</w:sectPr>|<w:sectPr\b[^>]*/>", sect, doc, flags=re.S)

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as out:
        for fn, data in members:
            if fn == "word/styles.xml":
                data = styles.encode()
            elif fn == "word/document.xml":
                data = doc.encode()
            out.writestr(fn, data)

    print(f"{json_path}  ->  {out_path}\n")
    print(f"{'style':<20}{'font':<22}{'size':>6}{'colour':>9}  paragraph (pt)")
    for sid, f, s, c, spm in applied:
        print(f"{sid:<20}{f:<22}{s:>6}{'#'+c:>9}  {spm}")
    print(f"\npage {p['w_cm']}x{p['h_cm']}cm  margins left {mg['left']} right {mg['right']} "
          f"top {mg['top']} bottom {bottom}cm"
          + ("  (bottom = top, no --bottom given)" if bottom_override is None else ""))
    if not mapping:
        print("\nNOTE  no --map given; headings were assigned Heading1/2/3... by size.")
        print("  If the PDF has a separate document title it takes Heading1 and shifts")
        print("  every level by one. Check the sample text in the analysis report, then")
        print("  re-run with --map 1=Title,2=Heading1,...")
    print("\nNext: python3 verify_roundtrip.py " + out_path + " " + json_path)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(2)
    a = sys.argv
    mapping, bottom = {}, None
    if "--map" in a:
        for kv in a[a.index("--map") + 1].split(","):
            k, v = kv.split("=")
            mapping[k.strip()] = v.strip()
    if "--bottom" in a:
        bottom = float(a[a.index("--bottom") + 1])
    build(a[1], a[2], mapping, bottom)
