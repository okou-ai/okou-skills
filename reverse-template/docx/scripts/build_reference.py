#!/usr/bin/env python3
"""Turn any .docx into a usable Pandoc --reference-doc template.

Usage:  python3 build_reference.py source.docx reference.docx [--map 'Memo Title=Title,Section Head=Heading1,Body Copy=BodyText']

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


def _log_recipe(target, argv):
    """Append this invocation beside the template so make_package can replay
    it. Inferring the recipe from the result was never complete."""
    import json, os
    try:
        with open(os.path.abspath(target) + ".recipe", "a") as f:
            f.write(json.dumps({"cmd": [os.path.basename(argv[0])] + argv[1:]}, ensure_ascii=False) + "\n")
    except OSError:
        pass


def build(src_path, out_path, mapping=None):
    with zipfile.ZipFile(src_path) as src:
        members = [(i.filename, src.read(i.filename)) for i in src.infolist()]
        names = [f for f, _ in members]
    blob = dict(members)
    styles = blob["word/styles.xml"].decode("utf-8", "replace")
    doc = blob["word/document.xml"].decode("utf-8", "replace")
    src_doc = doc          # the document as written, before the body becomes a sampler

    have = style_map(styles)
    # Every style pandoc's own reference.docx defines is one pandoc may emit;
    # the source must end up with all of them. Read the list from pandoc
    # itself rather than from a table here, which is how Abstract Title went
    # missing for a whole pandoc release.
    dref, tmp = default_reference()
    with zipfile.ZipFile(dref) as dz:
        dmap = style_map(dz.read("word/styles.xml").decode("utf-8", "replace"))
    shutil.rmtree(tmp, ignore_errors=True)
    dnames = {k: (re.search(r'<w:name w:val="([^"]+)"', v[1]) or [None, k])[1] for k, v in dmap.items()}
    known = [n for n in PS.MUST_EXIST + PS.AUTO_INJECTED if n.lower() not in have]
    missing = known + [dnames[k] for k in dmap if k not in have and dnames[k] not in known]

    injected, unavailable, derived = [], [], []
    if missing:
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
            if n.lower() in ("body text", "first paragraph", "compact"):
                # Body paragraphs must look like the source's Normal: pandoc's
                # own spacing and indent on these would replace it.
                xml = re.sub(r"<w:spacing\b[^>]*/>|<w:ind\b[^>]*/>", "", xml)
                xml = re.sub(r"<w:pPr>\s*</w:pPr>", "", xml)
            blocks.append(xml)
            used_ids.add(sid)
            have[n.lower()] = (sid, xml)
            injected.append(n)
        styles = styles.replace("</w:styles>", "".join(blocks) + "</w:styles>")

    # body -> style sampler; sectPr kept as is (header/footer refs, paper, margins)
    sect = re.search(r"<w:sectPr\b.*?</w:sectPr>|<w:sectPr\b[^>]*/>", doc, re.S)
    sect_xml = sect.group(0) if sect else "<w:sectPr/>"
    # Make the closing section continuous. A single-section source never says,
    # and the default (nextPage) makes any section break inserted later start
    # a new page. CT_SectPr order: header/footer refs, footnotePr, endnotePr,
    # then type, then pgSz.
    if "<w:type " not in sect_xml and not sect_xml.endswith("/>"):
        m_ = re.search(r"<w:(?:pgSz|pgMar|paperSrc|pgBorders|lnNumType|pgNumType|cols)\b", sect_xml)
        at = m_.start() if m_ else sect_xml.index("</w:sectPr>")
        sect_xml = sect_xml[:at] + '<w:type w:val="continuous"/>' + sect_xml[at:]
    elif sect_xml.endswith("/>"):
        sect_xml = '<w:sectPr><w:type w:val="continuous"/></w:sectPr>'
    doc = re.sub(r"(<w:body>).*?(</w:body>)",
                 lambda m: m.group(1) + sample_body(have, sect_xml, PS.PARAGRAPH) + m.group(2),
                 doc, flags=re.S)



    # --- body paragraphs look like the paragraphs the document is set in ---
    # pandoc writes ordinary paragraphs as Body Text / First Paragraph /
    # Compact. In most documents those styles exist but are never used: the
    # text is Normal, and Word's built-in Body Text carries a 6pt space-after
    # of its own. Rebase them on the style the document actually uses and
    # clear their own paragraph and run overrides.
    import collections as _c
    _use = _c.Counter()
    for _para in re.findall(r"<w:p\b.*?</w:p>", src_doc, re.S):
        if re.search(r"<w:t\b[^>]*>[^<]*\S", _para):
            _ps = re.search(r'<w:pStyle w:val="([^"]+)"', _para)
            _use[_ps.group(1) if _ps else "Normal"] += 1
    _body_sid = _use.most_common(1)[0][0] if _use else "Normal"
    _body_targets = ("body text", "first paragraph", "compact")
    _body_ids = {have[n][0] for n in _body_targets if n in have}
    if (mapping or {}).get("__body__"):
        _body_sid = have[mapping["__body__"].lower()][0]
    if _body_sid not in _body_ids:
        for n in _body_targets:
            if n not in have:
                continue
            sid, xml = have[n]
            new = re.sub(r"<w:rPr>.*?</w:rPr>|<w:rPr/>", "", xml, flags=re.S)
            new = re.sub(r"<w:spacing\b[^>]*/>|<w:ind\b[^>]*/>|<w:jc\b[^>]*/>|<w:contextualSpacing\b[^>]*/>", "", new)
            new = re.sub(r"<w:pPr>\s*</w:pPr>", "", new)
            new = (re.sub(r'<w:basedOn w:val="[^"]+"/>', f'<w:basedOn w:val="{_body_sid}"/>', new, count=1)
                   if "<w:basedOn" in new else
                   re.sub(r'(<w:name w:val="[^"]+"/>)', lambda m: m.group(1) + f'<w:basedOn w:val="{_body_sid}"/>', new, count=1))
            if xml in styles:
                styles = styles.replace(xml, new, 1)
            else:
                styles = re.sub(rf'<w:style\b[^>]*w:styleId="{re.escape(sid)}".*?</w:style>', lambda m: new, styles, count=1, flags=re.S)
            have[n] = (sid, new)
        print(f"  body paragraphs: Body Text, First Paragraph and Compact now follow {_body_sid!r},"
              f" the style {_use[_body_sid]} of {sum(_use.values())} paragraphs use")


    # --- tables look like the document's tables ---
    # pandoc writes every table with style "Table" (its own: one rule under
    # the header row). The document's tables use a table style of their own
    # or direct borders; either becomes "Table".
    import collections as _c2
    _tstyles = _c2.Counter(re.findall(r'<w:tblStyle w:val="([^"]+)"', src_doc))
    _tbl_hit = have.get("table")
    if _tbl_hit:
        _tsid, _txml = _tbl_hit
        _src_tbl = None
        if _tstyles:
            _tid = _tstyles.most_common(1)[0][0]
            _m = re.search(rf'<w:style\b[^>]*w:type="table"[^>]*w:styleId="{re.escape(_tid)}".*?</w:style>', styles, re.S)
            _src_tbl = _m.group(0) if _m else None
        if _src_tbl:
            # everything after the naming elements: pPr, rPr, tblPr, trPr, tcPr, tblStylePr*
            _props = "".join(m.group(0) for m in re.finditer(
                r"<w:pPr>.*?</w:pPr>|<w:rPr>.*?</w:rPr>|<w:tblPr>.*?</w:tblPr>|<w:trPr>.*?</w:trPr>|<w:tcPr>.*?</w:tcPr>|<w:tblStylePr\b.*?</w:tblStylePr>",
                _src_tbl, re.S))
            _new = re.sub(r"<w:pPr>.*?</w:pPr>|<w:rPr>.*?</w:rPr>|<w:tblPr>.*?</w:tblPr>|<w:trPr>.*?</w:trPr>|<w:tcPr>.*?</w:tcPr>|<w:tblStylePr\b.*?</w:tblStylePr>",
                          "", _txml, flags=re.S)
            _new = _new.replace("</w:style>", _props + "</w:style>")
            _how = f"table style {_tid!r} ({_tstyles[_tid]} tables)"
        else:
            _tp = re.search(r"<w:tblPr>.*?</w:tblPr>", src_doc, re.S)
            _borders = re.search(r"<w:tblBorders>.*?</w:tblBorders>", _tp.group(0), re.S) if _tp else None
            _new = None
            if _borders:
                _new = re.sub(r"<w:tblPr>.*?</w:tblPr>", lambda m: re.sub(r"(<w:tblPr>)", r"\1" + _borders.group(0), m.group(0), count=1)
                              if "<w:tblBorders>" not in m.group(0) else m.group(0), _txml, flags=re.S)
                _how = "the first table's own borders"
        if _src_tbl or (_borders if not _src_tbl else False):
            styles = styles.replace(_txml, _new, 1) if _txml in styles else re.sub(
                rf'<w:style\b[^>]*w:styleId="{re.escape(_tsid)}".*?</w:style>', lambda m: _new, styles, count=1, flags=re.S)
            have["table"] = (_tsid, _new)
            print(f"  tables: 'Table' takes {_how}")

    # --- custom style names onto the ones pandoc writes to ---
    # A document set in "Memo Title" and "Section Head" never touches Title
    # and heading 1; the mapped style's own look is copied into the target.
    TARGET = {"title": "title", "subtitle": "subtitle", "bodytext": "body text",
              "heading1": "heading 1", "heading2": "heading 2", "heading3": "heading 3",
              "heading4": "heading 4", "heading5": "heading 5", "heading6": "heading 6"}
    NAMING = r"(?:name|aliases|basedOn|next|link|autoRedefine|hidden|uiPriority|semiHidden|unhideWhenUsed|qFormat|locked|personal\w*|rsid)"
    for src_name, target in (mapping or {}).items():
        tkey = TARGET.get(target.lower().replace(" ", ""), target.lower())
        src_hit, tgt_hit = have.get(src_name.lower()), have.get(tkey)
        if not src_hit or not tgt_hit:
            print(f"  --map: {src_name!r} -> {target}: "
                  f"{'source style not found' if not src_hit else 'target not found'}")
            continue
        sxml, (tsid, txml) = src_hit[1], tgt_hit
        new = re.sub(r"<w:pPr>.*?</w:pPr>|<w:pPr/>|<w:rPr>.*?</w:rPr>|<w:rPr/>", "", txml, flags=re.S)
        props = "".join(m.group(0) for m in re.finditer(r"<w:pPr>.*?</w:pPr>|<w:rPr>.*?</w:rPr>", sxml, re.S))
        last = None
        for m in re.finditer(rf"<w:{NAMING}\b[^>]*/>", new):
            last = m
        new = (new[:last.end()] + props + new[last.end():]) if last else new.replace("</w:style>", props + "</w:style>")
        sb = re.search(r'<w:basedOn w:val="[^"]+"/>', sxml)
        if sb:
            new = (re.sub(r'<w:basedOn w:val="[^"]+"/>', sb.group(0), new, count=1) if "<w:basedOn" in new
                   else re.sub(r'(<w:name w:val="[^"]+"/>)', lambda m: m.group(1) + sb.group(0), new, count=1))
        if txml in styles:
            styles = styles.replace(txml, new, 1)
        else:
            styles = re.sub(rf'<w:style\b[^>]*w:styleId="{re.escape(tsid)}".*?</w:style>', lambda m: new, styles, count=1, flags=re.S)
        have[tkey] = (tsid, new)
        print(f"  mapped {src_name!r} -> {target}")

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
    if "<w:pgSz" not in sect_xml:
        # Pandoc's own default reference.docx has none either, so this is common.
        # Verification treats it as a failure because without a paper size the
        # layout follows the reader's locale and the page count varies per machine.
        print("  ACTION REQUIRED  the source sets no paper size, so neither does this "
              "template.\n                   Verification will fail until you set one:")
        print(f"                   set_header_footer.py {os.path.basename(out_path)} --paper A4")
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
    a = sys.argv[1:]
    mp = None
    if "--map" in a:
        i = a.index("--map")
        mp = dict(kv.split("=", 1) for kv in a[i + 1].split(",") if "=" in kv)
        a = a[:i] + a[i + 2:]
    if len(a) != 2 or a[0] in ("-h", "--help"):
        print(__doc__)
        sys.exit(2)
    build(a[0], a[1], mp)
    _log_recipe(a[1], sys.argv)
