#!/usr/bin/env python3
"""Write the inferred PDF styles into a Pandoc reference.docx.

Usage:
  python3 build_reference.py styles.json out.docx
  python3 build_reference.py styles.json out.docx --map 1=Title,2=Heading1,3=Heading2
  python3 build_reference.py styles.json out.docx --bottom 3.0
  python3 build_reference.py styles.json out.docx --top 2.4 --left 1.8 --right 1.8

--map corrects the level assignment. analyze_pdf orders heading groups by
size, but a document title and an H1 are both just large text in a PDF, so the
mapping has to be stated explicitly. The left side is the group number from
the analysis report; the right side is a Word style name.

--bottom overrides the bottom margin. By default the analyzer's own suggestion
is used, which mirrors the top margin only when the layout measures as
vertically symmetric.

--top, --left and --right override the other three the same way. A measured
margin is the distance to the first glyph box, which sits a little inside the
text block, so a layout whose real margin is not in the analyzer's table of
common values can land on the wrong side of it. Pass the value you measured.

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


def build(json_path, out_path, mapping, overrides):
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
    # 0 is a measured value ("no extra space"), not a missing one. Skipping it
    # would leave pandoc's default spacing in place and contradict the report.
    if b.get("space_after_pt") is not None:
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
        if h.get("space_before_pt") is not None:
            hsp.append(f'w:before="{PT2TWIP(h["space_before_pt"])}"')
        if h.get("space_after_pt") is not None:
            hsp.append(f'w:after="{PT2TWIP(h["space_after_pt"])}"')
        if hsp:
            hp += f'<w:spacing {" ".join(hsp)}/>'
        # "left" is a measured value too. Pandoc's default Title is centered, so
        # leaving alignment unwritten silently overrides the measurement.
        if h.get("align"):
            hp += f'<w:jc w:val="{h["align"]}"/>'
        styles, ok = patch_style(styles, target,
                                 rpr(h["font"], h["size"], h["color"], bold), hp)
        applied.append((target + ("" if ok else " NOT FOUND"),
                        clean_font(h["font"]), h["size"], h["color"],
                        fmt_sp(h.get("space_after_pt"), None, None,
                               h.get("space_before_pt"), h.get("align"))))

    # --- heading levels the source never used ---
    # Only the levels named in --map get written, so the rest keep pandoc's
    # defaults. Those can be larger than a mapped level below them and in a
    # colour that appears nowhere in the source, so a ### would render bigger
    # than a ## and off-brand. Extend the mapped levels into a descending
    # ladder instead. These sizes are derived, not measured.
    written = {}
    for h in d["headings"]:
        t = mapping.get(str(h["level"]), f"Heading{h['level']}")
        m = re.fullmatch(r"Heading(\d)", t)
        if m:
            written[int(m.group(1))] = h
    derived = []
    if written:
        deepest = max(written)
        ref_h = written[deepest]
        bold = bool(re.search(r"bold|black|heavy|semibold", ref_h["font"], re.I))
        for lvl in range(deepest + 1, 10):
            size = max(round(ref_h["size"] * (0.92 ** (lvl - deepest)) * 2) / 2,
                       d["body"]["size"])
            styles, ok = patch_style(styles, f"Heading{lvl}",
                                     rpr(ref_h["font"], size, ref_h["color"], bold), "")
            if ok:
                derived.append((f"Heading{lvl}", size))
                applied.append((f"Heading{lvl}", clean_font(ref_h["font"]), size,
                                ref_h["color"], "derived"))

    # --- page ---
    p, mg = d["page"], d["margins_suggested_cm"]
    # Take the analyzer's own bottom suggestion. Mirroring the top margin is
    # wrong whenever the layout is not vertically symmetric, and the report
    # prints a warning in exactly that case.
    mg = dict(mg)
    if mg.get("bottom") is None:
        mg["bottom"] = mg.get("top")
    mg.update({k: v for k, v in overrides.items() if v is not None})
    bottom = mg["bottom"]
    overridden = sorted(k for k, v in overrides.items() if v is not None)
    # w:cols comes after w:pgMar in CT_SectPr
    cols = d.get("columns") or 1
    cols_xml, gap_note = "", ""
    if cols > 1:
        gap_pt = d.get("column_gap_pt")
        if gap_pt is None:
            gap_pt, gap_note = 24, "  gutter 24pt (DEFAULT — none could be measured)"
        else:
            gap_note = (f"  gutter {gap_pt}pt, column width "
                        f"{d.get('column_width_pt')}pt (both measured)")
        cols_xml = f'<w:cols w:num="{cols}" w:space="{PT2TWIP(gap_pt)}" w:equalWidth="1"/>'
    sect = (f'<w:sectPr><w:pgSz w:w="{CM2TWIP(p["w_cm"])}" w:h="{CM2TWIP(p["h_cm"])}"/>'
            f'<w:pgMar w:top="{CM2TWIP(mg["top"])}" w:right="{CM2TWIP(mg["right"])}" '
            f'w:bottom="{CM2TWIP(bottom)}" w:left="{CM2TWIP(mg["left"])}" '
            f'w:header="708" w:footer="708" w:gutter="0"/>{cols_xml}</w:sectPr>')
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
          + ("  (bottom from the analyzer's suggestion)" if "bottom" not in overridden
             else "")
          + (f"  ({', '.join(overridden)} overridden on the command line)"
             if overridden else "")
          + (f"  columns {cols}{gap_note}" if cols > 1 else ""))
    if derived:
        print(f"\nNOTE  the source used {max(written)} heading level(s). Levels "
              f"{derived[0][0][-1]}-9 were extended from it as a descending ladder "
              f"({', '.join(f'{n} {s}pt' for n, s in derived[:3])}...).")
        print("      These sizes are derived, not measured. Without this they would keep")
        print("      pandoc's defaults, which can be larger than the level above them.")
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
    mapping = {}
    overrides = {k: None for k in ("top", "right", "bottom", "left")}
    if "--map" in a:
        for kv in a[a.index("--map") + 1].split(","):
            k, v = kv.split("=")
            mapping[k.strip()] = v.strip()
    for k in overrides:
        if f"--{k}" in a:
            overrides[k] = float(a[a.index(f"--{k}") + 1])
    build(a[1], a[2], mapping, overrides)
