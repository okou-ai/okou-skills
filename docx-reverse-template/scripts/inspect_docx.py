#!/usr/bin/env python3
"""Report what a .docx offers as a Pandoc --reference-doc.

Usage:  python3 inspect_docx.py source.docx

Read-only. Exit code 0 means it is usable as is; 1 means build_reference.py
needs to fill gaps first.
"""
import sys, zipfile, re, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pandoc_styles as PS

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
        print("          set_header_footer.py <ref> --replace 'OKOU-2026-001=PLACEHOLDER'")
        print("          Swap the values in place. Rebuilding with --footer would flatten")
        print("          tab columns, border rules, a first-page variant and any table.")

    # --- page setup ---
    doc = z.read("word/document.xml").decode("utf-8", "replace")
    sect = re.search(r"<w:sectPr\b.*?</w:sectPr>|<w:sectPr\b[^>]*/>", doc, re.S)
    print("\n[page setup]")
    if sect:
        s = sect.group(0)
        pg = re.search(r"<w:pgSz[^>]*w:w=\"(\d+)\"[^>]*w:h=\"(\d+)\"", s) or \
             re.search(r"<w:pgSz[^>]*w:h=\"(\d+)\"[^>]*w:w=\"(\d+)\"", s)
        mar = dict(re.findall(r"w:(top|right|bottom|left)=\"(-?\d+)\"", s))
        if pg:
            print(f"  paper: {TWIP(pg.group(1)):.1f} x {TWIP(pg.group(2)):.1f} cm")
        if mar:
            print("  margins: " + "  ".join(f"{k} {TWIP(v):.2f}cm" for k, v in mar.items()))
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
            print(f"  columns: {n}"
                  + (f"   gutter {TWIP(sp.group(1)):.2f}cm" if sp and n > 1 else "")
                  + ("   (inherited as is; use set_header_footer.py --columns to change it)"
                     if n > 1 else ""))
        else:
            print("  columns: 1 (none set)")
    else:
        print("  no sectPr — output falls back to Word defaults")

    # --- theme fonts ---
    if "word/theme/theme1.xml" in names:
        t = z.read("word/theme/theme1.xml").decode("utf-8", "replace")
        major = re.search(r"<a:majorFont>.*?typeface=\"([^\"]*)\"", t, re.S)
        minor = re.search(r"<a:minorFont>.*?typeface=\"([^\"]*)\"", t, re.S)
        print(f"\n[theme fonts] headings {major.group(1) if major else '?'} / "
              f"body {minor.group(1) if minor else '?'}")

    # --- required style coverage ---
    crit = [n for n in PS.MUST_EXIST if n.lower() not in have]
    soft = [n for n in PS.AUTO_INJECTED if n.lower() not in have]
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
        print(f"\n[paragraph settings] pt. All of these carry over: build_reference.py "
              f"copies styles.xml wholesale")
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
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
