#!/usr/bin/env python3
"""Report what a .docx offers as a Pandoc --reference-doc.

Usage:  python3 inspect_docx.py source.docx
        python3 inspect_docx.py source.docx --slots [--json]

Read-only. Exit code 0 means it is usable as is; 1 means build_reference.py
needs to fill gaps first. --slots lists text locations across document parts
after the reuse scope is chosen; it does not classify the document or decide
which runs may change. A successful listing exits 0.
"""
import collections
import sys, zipfile, re, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandoc_styles as PS
from docx_layout import Styles, body_candidates, choose_body, choose_section, sections, section_xml
PS_LOWER = {n.lower() for n in PS.ALL}

TWIP = lambda t: int(t) / 1440 * 2.54          # twips -> cm
TWIP2PT = lambda t: round(int(t) / 20, 1)      # twips -> pt


SIMPLE_FIELD = re.compile(r"<w:fldSimple\b[^>]*?w:instr=\"([^\"]*)\".*?</w:fldSimple>", re.S)
INSTR_TEXT = re.compile(r"<w:instrText[^>]*>([^<]*)</w:instrText>")


def split_hf(xml):
    """Separate literal text from field results in a header or footer.

    A field result is whatever Word recomputes on open (PAGE, NUMPAGES,
    STYLEREF). What matters for review is the literal text, because that is
    copied verbatim into every document made from the template.

    Both encodings occur: <w:fldSimple w:instr="PAGE"> wrapping its cached
    result, and the fldChar begin/separate/end run sequence with <w:instrText>.
    """
    fields = [f.strip().split()[0] for f in SIMPLE_FIELD.findall(xml) if f.strip()]
    fields += [f.strip().split()[0] for f in INSTR_TEXT.findall(xml) if f.strip()]
    xml = SIMPLE_FIELD.sub("", xml)          # drop cached fldSimple results

    literal, depth = [], 0
    for m in re.finditer(r"<w:fldChar[^>]*w:fldCharType=\"(\w+)\"[^>]*/>"
                         r"|<w:t[^>]*>([^<]*)</w:t>", xml):
        if m.group(1):
            if m.group(1) == "separate":
                depth += 1
            elif m.group(1) == "end":
                depth = max(0, depth - 1)
        elif depth == 0 and m.group(2).strip():
            literal.append(m.group(2))
    return " ".join(literal).strip(), sorted(set(fields))


def styles_in(z):
    """{lowercased w:name: styleId}. Keyed by name because Pandoc matches on it."""
    try:
        x = z.read("word/styles.xml").decode("utf-8", "replace")
    except KeyError:
        return {}
    out = {}
    for m in re.finditer(r"<w:style\b[^>]*?w:styleId=\"([^\"]+)\"[^>]*>(.*?)</w:style>", x, re.S):
        sid, body = m.group(1), m.group(2)
        n = re.search(r"<w:name\s+w:val=\"([^\"]*)\"", body)
        if n:
            out[n.group(1).lower()] = sid
    return out


def para_props(z, name_to_id, names):
    """Paragraph-level settings for the key styles. build_reference.py copies
    styles.xml wholesale, so these all carry over; this just surfaces them."""
    x = z.read("word/styles.xml").decode("utf-8", "replace")
    rows = []
    for n in names:
        sid = name_to_id.get(n.lower())
        if not sid:
            continue
        m = re.search(rf"<w:style\b[^>]*?w:styleId=\"{re.escape(sid)}\"[^>]*>(.*?)</w:style>",
                      x, re.S)
        if not m:
            continue
        ppr = re.search(r"<w:pPr>.*?</w:pPr>", m.group(1), re.S)
        p = ppr.group(0) if ppr else ""
        g = lambda a: (lambda mm: TWIP2PT(mm.group(1)) if mm else None)(
            re.search(rf'<w:spacing[^>]*w:{a}="(\d+)"', p))
        ind = re.search(r'<w:ind[^>]*w:(firstLine|left)="(\d+)"', p)
        jc = re.search(r'<w:jc w:val="([a-z]+)"', p)
        line = re.search(r'<w:spacing[^>]*w:line="(\d+)"[^>]*w:lineRule="([a-z]+)"', p)
        rows.append((n, sid, g("before"), g("after"),
                     f"{TWIP2PT(line.group(1))}/{line.group(2)}" if line else None,
                     f"{ind.group(1)}={TWIP2PT(ind.group(2))}" if ind else None,
                     jc.group(1) if jc else None,
                     "keepNext" if "<w:keepNext" in p else None))
    return rows


def slots(path, as_json=False):
    from docx_slots import read_slots
    records = read_slots(path)
    if as_json:
        import json
        print(json.dumps(records, ensure_ascii=False, indent=2))
        return 0
    print(f"===== {os.path.basename(path)} =====\n")
    print("[text locations] Addresses identify nodes; text alone is not a unique key.")
    for paragraph in records:
        print(f"\n{paragraph['part']}  p{paragraph['paragraph']}  style={paragraph['style']}")
        print(f"  paragraph: {paragraph['text']!r}")
        if paragraph['row']:
            print(f"  table row: {paragraph['row']}")
        if not paragraph['runs']:
            print(f"  {paragraph['path']}  (no text; inspect spacing/artwork before cloning)")
        for run in paragraph['runs']:
            mark = " [field result: not editable]" if run['field'] else ""
            print(f"  {run['path']}  {run['text']!r}{mark}")
            if run.get('placeholder_name'):
                linked = run.get('placeholder')
                print(f"    placeholder {run['placeholder_name']!r}; showing={run.get('showing_placeholder', False)}")
                print(f"    linked: {linked!r}")
            if run.get('data_binding'):
                print(f"    data binding: {run['data_binding']!r}; update the bound value when filling")
    return 0


def main(path):
    z = zipfile.ZipFile(path)
    names = z.namelist()
    have = styles_in(z)

    print(f"===== {os.path.basename(path)} =====\n")

    # --- header / footer ---
    hdrs = [n for n in names if re.match(r"word/header\d+\.xml", n)]
    ftrs = [n for n in names if re.match(r"word/footer\d+\.xml", n)]
    print("[header/footer]  carried into every output document by --reference-doc")
    literals = []
    for tag, parts in (("header", hdrs), ("footer", ftrs)):
        if not parts:
            print(f"  {tag}: none")
            continue
        for p in parts:
            raw = z.read(p)
            txt, fields = split_hf(raw.decode("utf-8", "replace"))
            img = " +image" if b"<w:drawing" in raw or b"<v:imagedata" in raw else ""
            fl = f"  [fields: {', '.join(fields)}]" if fields else ""
            print(f"  {tag} {p.split('/')[-1]}: {txt[:70] or '(no literal text)'}{img}{fl}")
            if txt:
                literals.append(txt)
    if literals:
        print("  REVIEW: the literal text above is copied verbatim into every document")
        print("          generated from this template. Document numbers, versions, owners")
        print("          and dates belonging to the source must be replaced:")
        print("          set_header_footer.py <ref> --replace 'OLD=PLACEHOLDER'")
        print("          using values from the literal text above, not this example.")
        print("          Swap the values in place. Rebuilding with --footer would flatten")
        print("          tab columns, border rules, a first-page variant and any table.")

    # --- page setup ---
    doc = z.read("word/document.xml").decode("utf-8", "replace")
    source_styles = Styles(z.read("word/styles.xml"))
    print("\n[body candidates] flowing prose, ranked by non-whitespace characters")
    for sid, count in body_candidates(doc, source_styles).most_common():
        print(f"  {sid}: {count} characters")
    print("\n[sections]")
    for number, (section, paragraphs) in enumerate(sections(doc), 1):
        margin = section.find("w:pgMar", {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"})
        margins = {key.rsplit("}", 1)[-1]: value for key, value in margin.attrib.items()} if margin is not None else "(defaults)"
        print(f"  {number}: {len(paragraphs)} main-flow paragraphs; margins {margins}")
    body_sid = None
    try:
        body_sid = choose_body(doc, source_styles)
        selected = choose_section(doc, source_styles, body_sid)
        print(f"  selected: --section {selected}; body style {body_sid!r}")
    except ValueError as error:
        print(f"  REVIEW: {error}")
        selected = None
    print("\n[page setup]")
    if selected is not None:
        s = section_xml(doc, selected)
        pg = re.search(r"<w:pgSz[^>]*w:w=\"(\d+)\"[^>]*w:h=\"(\d+)\"", s) or \
             re.search(r"<w:pgSz[^>]*w:h=\"(\d+)\"[^>]*w:w=\"(\d+)\"", s)
        mar = dict(re.findall(r"w:(top|right|bottom|left)=\"(-?\d+)\"", s))
        if pg:
            print(f"  paper: {TWIP(pg.group(1)):.1f} x {TWIP(pg.group(2)):.1f} cm")
        if mar:
            print("  margins: " + "  ".join(f"{k} {TWIP(v):.2f}cm" for k, v in mar.items()))
        # A tab stop past the text width puts that part of the header outside
        # the text area on every page. One subtraction catches it, and nothing
        # else in the toolchain looks at w:tab.
        if pg and mar.get("left") and mar.get("right"):
            tw = int(pg.group(1)) - int(mar["left"]) - int(mar["right"])
            for part in [n for n in names if re.match(r"word/(header|footer)\d+\.xml", n)]:
                x = z.read(part).decode("utf-8", "replace")
                for val, pos in re.findall(r'<w:tab w:val="(\w+)" w:pos="(\d+)"', x):
                    if int(pos) > tw:
                        over = int(pos) - tw
                        print(f"  REVIEW: {os.path.basename(part)} has a {val} tab at "
                              f"{pos} twips, {over} past the {tw}-twip text width "
                              f"({over / 1440 * 2.54:.2f}cm outside it). Rebuild the part with "
                              f"set_header_footer.py --{part.split('/')[-1][:6]} 'left\\tright', "
                              f"which places the stop at {tw}.")
        print(f"  references a header: {'yes' if 'headerReference' in s else 'no'}"
              f"   footer: {'yes' if 'footerReference' in s else 'no'}")
        # Columns ride along in sectPr like paper and margins do, so a
        # multi-column source produces a multi-column template with nothing
        # asked of the caller. Say so rather than letting it pass unseen.
        c = re.search(r"<w:cols\b[^>]*/>|<w:cols\b[^>]*>.*?</w:cols>", s, re.S)
        if c:
            num = re.search(r'w:num="(\d+)"', c.group(0))
            sp = re.search(r'w:space="(\d+)"', c.group(0))
            n = int(num.group(1)) if num else 1
            widths = re.findall(r'<w:col\b[^>]*w:w="(\d+)"', c.group(0))
            print(f"  columns: {n}"
                  + (f"   gutter {TWIP(sp.group(1)):.2f}cm" if sp and n > 1 else "")
                  + (f"   unequal widths: {', '.join(f'{TWIP(w):.2f}cm' for w in widths)}"
                     if widths else ""))
            if n > 1:
                print("           inherited as is. set_header_footer.py --columns changes"
                      " the count,")
                print("           and changing it drops per-column widths.")
            if widths and n > 1:
                spaces = re.findall(r'<w:col\b[^>]*w:space="(\d+)"', c.group(0))
                span = sum(int(w) for w in widths) + sum(int(x) for x in spaces[:-1])
                pw = re.search(r'<w:pgSz\b[^>]*w:w="(\d+)"', s)
                mg = dict(re.findall(r'w:(left|right)="(-?\d+)"', re.search(r"<w:pgMar\b[^>]*/>", s).group(0))) if re.search(r"<w:pgMar\b[^>]*/>", s) else {}
                if pw and mg:
                    tw = int(pw.group(1)) - int(mg.get("left", 0)) - int(mg.get("right", 0))
                    if abs(tw - span) > 40:
                        print(f"  REVIEW: the columns span {TWIP(span):.2f}cm of a {TWIP(tw):.2f}cm text width."
                              " Word leaves the rest empty; LibreOffice stretches the columns.")
        else:
            print("  columns: 1 (none set)")
    else:
        print("  select a body style and section before building")

    # --- theme fonts ---
    if "word/theme/theme1.xml" in names:
        t = z.read("word/theme/theme1.xml").decode("utf-8", "replace")
        # Each font group has its own latin, East Asian and complex-script
        # slot. A single non-greedy search always returns the latin one, so an
        # empty <a:ea> reads as if the fonts were fine while every CJK glyph
        # falls back to whatever the reader picks.
        def slots(group):
            m = re.search(rf"<a:{group}>(.*?)</a:{group}>", t, re.S)
            if not m:
                return "?", "?"
            g = lambda tag: (re.search(rf'<a:{tag} typeface="([^"]*)"', m.group(1))
                             or re.search(r"(?!)", "")) 
            lat = re.search(r'<a:latin typeface="([^"]*)"', m.group(1))
            ea = re.search(r'<a:ea typeface="([^"]*)"', m.group(1))
            return (lat.group(1) if lat else "?"), (ea.group(1) if ea else "")
        maj_l, maj_e = slots("majorFont")
        min_l, min_e = slots("minorFont")
        print(f"\n[theme fonts] headings {maj_l or '(none)'} / body {min_l or '(none)'}")
        print(f"              east asian: headings {maj_e or 'EMPTY'} / "
              f"body {min_e or 'EMPTY'}")
        if not (maj_e and min_e):
            print("  REVIEW: the theme sets no East Asian font, so CJK text falls back to")
            print("          whatever the reader substitutes. Set it per style with")
            print("          set_style.py --font, which writes w:eastAsia.")

    # --- required style coverage ---
    crit = [n for n in PS.MUST_EXIST if n.lower() not in have]
    soft = [n for n in PS.AUTO_INJECTED if n.lower() not in have]
    # What the document actually uses. The styles pandoc writes to may be the
    # ones the author never touched: a document set in "Memo Title" and
    # "Section Head" leaves Title and heading 1 at their defaults, and a
    # document formatted by hand leaves every style empty.
    docxml = z.read("word/document.xml").decode("utf-8", "replace")
    id_to_name = {(v[0] if isinstance(v, tuple) else v): k for k, v in have.items()}
    paras = re.findall(r"<w:p\b.*?</w:p>", docxml, re.S)
    use, direct = collections.Counter(), collections.Counter()
    for para in paras:
        if not re.search(r"<w:t\b[^>]*>[^<]*\S", para):
            continue
        ps = re.search(r'<w:pStyle w:val="([^"]+)"', para)
        sid = ps.group(1) if ps else "Normal"
        use[sid] += 1
        runs = re.findall(r"<w:r\b.*?</w:r>", para, re.S)
        if any(re.search(r"<w:rPr>.*?<w:(sz|b|color|rFonts)\b", r, re.S) for r in runs):
            direct[sid] += 1
    ntbl = docxml.count("<w:tbl>")
    tstyles = collections.Counter(re.findall(r'<w:tblStyle w:val="([^"]+)"', docxml))
    if ntbl:
        print(f"\n[tables] {ntbl}; table style: "
              + (", ".join(f"{id_to_name.get(k, k)} x{v}" for k, v in tstyles.most_common(3)) if tstyles else "none (direct borders)")
              + " -> build_reference.py copies it onto pandoc's 'Table'")
    print(f"\n[styles in use] {sum(use.values())} paragraphs with text")
    print(f"  {'style':24}{'paragraphs':>11}{'direct formatting':>19}")
    for sid, n in use.most_common():
        nm = id_to_name.get(sid, sid)
        print(f"  {nm:24}{n:>11}{direct[sid]:>19}")
    total = sum(use.values()) or 1
    if direct["Normal"] * 100 >= 60 * total:
        print("  REVIEW: the document is formatted by hand; its styles carry nothing.")
        print("          Render it and extract styles from the render instead:")
        print(f"            node ../scripts/render-document.mjs --input {os.path.basename(path)} --out source-render")
        print("          then follow extract-template/pdf/SKILL.md on that PDF.")
    else:
        targets = {"title": "Title", "heading 1": "Heading1", "heading 2": "Heading2",
                   "heading 3": "Heading3", "body text": "BodyText"}
        sid_of = lambda n: have[n][0] if isinstance(have[n], tuple) else have[n]
        unused = [n for n in targets if n in have and sid_of(n) not in use]
        custom = [(id_to_name.get(sid, sid), n) for sid, n in use.most_common()
                  if id_to_name.get(sid, sid).lower() not in PS_LOWER]
        top_unused = any(n in unused for n in ("title", "heading 1"))
        if top_unused and custom:
            styles_xml = z.read("word/styles.xml").decode("utf-8", "replace")
            def look(name):
                sid = sid_of(name.lower()) if name.lower() in have else name
                m = re.search(rf'<w:style\b[^>]*w:styleId="{re.escape(sid)}".*?</w:style>', styles_xml, re.S)
                x = m.group(0) if m else ""
                sz = re.search(r'<w:sz w:val="(\d+)"', x)
                return (int(sz.group(1)) / 2 if sz else None, bool(re.search(r"<w:b\s*/>|<w:b w:val=\"(1|true)\"", x)))
            print(f"  REVIEW: pandoc writes to {', '.join(unused)}, which this document never uses.")
            print("          It uses:")
            for name, n in custom:
                sz, b = look(name)
                print(f"            {name:24}{n:>4} paragraphs  {sz if sz else '-':>5}pt  {'bold' if b else ''}")
            ranked = sorted(custom, key=lambda c: -(look(c[0])[0] or 0))
            body_guess = id_to_name.get(body_sid) if body_sid else None
            heads = [c[0] for c in ranked if c[0] != body_guess]
            guess = ([f"__body__={body_guess}"] if body_guess else []) + \
                    [f"{h}={t}" for h, t in zip(heads, ("Title", "Heading1", "Heading2", "Heading3"))]
            print("          Map each onto the pandoc style whose part it plays (the size order")
            print("          below is a guess; check it against the document):")
            print("            python3 build_reference.py <source.docx> reference.docx --map '" + ",".join(guess) + "'")
    print(f"\n[style coverage] {len(have)} styles defined; Pandoc references {len(PS.ALL)}")
    if crit:
        print(f"  MISSING {len(crit)} required — a dangling reference renders as Normal:")
        print(f"     {', '.join(crit)}")
    else:
        print(f"  OK  all {len(PS.MUST_EXIST)} required styles present")
    if soft:
        print(f"  .   {len(soft)} recreated by pandoc automatically: {', '.join(soft)}")
    wg = [n for n in PS.WRITER_GENERATED if n.lower() not in have]
    if wg:
        print(f"  .   {len(wg)} generated by the writer: {', '.join(wg)} "
              f"(create a style with the same name to customise)")

    # --- paragraph-level settings ---
    key_styles = ["Normal", "Body Text", "First Paragraph", "Compact",
                  "Title", "heading 1", "heading 2", "heading 3", "Block Text"]
    rows = para_props(z, have, key_styles)
    if rows:
        print("\n[paragraph settings] pt. Check these against the builder's reported rebasing and mappings.")
        print(f"  {'style':<18}{'id':<16}{'before':>7}{'after':>7}{'line':>12}"
              f"{'indent':>14}{'align':>8}  other")
        for n, sid, bf, af, ln, ind, jc, kn in rows:
            f = lambda v: "-" if v in (None, "") else str(v)
            print(f"  {n:<18}{sid:<16}{f(bf):>7}{f(af):>7}{f(ln):>12}"
                  f"{f(ind):>14}{f(jc):>8}  {kn or ''}")

    # styleIds that differ from the canonical name indicate a localised Word export
    odd = {n: have[n.lower()] for n in PS.PARAGRAPH
           if n.lower() in have and have[n.lower()].lower() != n.replace(" ", "").lower()}
    if odd:
        print(f"\n[non-standard styleIds] {len(odd)} — harmless, Pandoc matches on w:name")
        for n, sid in list(odd.items())[:6]:
            print(f"  \"{n}\"  ->  styleId=\"{sid}\"")

    z.close()
    print()
    if crit:
        print("Result: not usable as is. Run build_reference.py to fill the gaps.")
        return 1
    print("Result: usable as --reference-doc (still run build_reference.py to strip "
          "the body content).")
    return 0


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) in (2, 3) and args[1] == "--slots" and (len(args) == 2 or args[2] == "--json"):
        sys.exit(slots(args[0], "--json" in args))
    if len(args) != 1:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(args[0]))
