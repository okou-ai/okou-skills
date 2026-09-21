#!/usr/bin/env python3
"""Edit the page-level settings of reference.docx: header, footer, paper size.

Usage:
  python3 set_header_footer.py <reference.docx> --header "Company" --footer "Confidential"
  python3 set_header_footer.py <reference.docx> --footer "Page " --page-number --align center
  python3 set_header_footer.py <reference.docx> --show
  python3 set_header_footer.py <reference.docx> --clear

Options:
  --replace OLD=NEW  replace literal text inside the existing header and footer
                     parts, leaving their layout untouched. Repeatable. Use this
                     to swap a document number or owner out of a branded footer:
                     rebuilding it with --footer would flatten the tab columns,
                     border rules, first-page variant and any table it contains.
  --header TEXT      header text (omit to leave the header untouched). A tab
                     splits the line into columns against the right margin:
                     "Title\tv2.3" puts the title left and the version right,
                     "left\tcentre\tright" gives three. Write it as \t.
  --footer TEXT      footer text, same tab handling
  --page-number      append an automatic PAGE field after the footer text;
                     or write {PAGE} inside the text where the number goes
  --align L          left | center | right (default: header right, footer center)
  --size PT          font size (default 9)
  --color RRGGBB     colour (default 808080)
  --paper NAME       paper size: A4 | A5 | A3 | Letter | Legal
  --header-image FILE   picture at the start of the header (png/jpeg); with
                        --header-image-height PT, --header-image-align left|center|right
                        and --header-image-indent PT (picture offset from the left margin)
  --header-distance PT  distance from the page top to the header (pgMar w:header)
  --footer-distance PT  distance from the page bottom to the footer (pgMar w:footer)
  --columns N        number of text columns (1 restores a single column). The
                     gutter and any per-column widths come from the document;
                     they are only replaced when the count actually changes.
  --column-gap PT    override the gutter. Without it the document's own gutter
                     is kept, and 24pt is used only when the document sets none.
  --out PATH         write elsewhere; default is in place

Pandoc carries the header and footer into every document produced with
--reference-doc. Image logos are out of scope: they need extra media parts and
relationships that this script does not write.
"""
import sys, os, re, shutil, zipfile, collections

NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"')
CT_HDR = ("application/vnd.openxmlformats-officedocument."
          "wordprocessingml.header+xml")
CT_FTR = ("application/vnd.openxmlformats-officedocument."
          "wordprocessingml.footer+xml")
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/"
# twips
PAPER = {"A4": (11906, 16838), "A5": (8391, 11906), "A3": (16838, 23811),
         "LETTER": (12240, 15840), "LEGAL": (12240, 20160)}
# CT_SectPr is an ordered sequence. Inserting pgSz at the head of sectPr puts it
# before the header/footer references and breaks that order.
SECTPR_ORDER = ["headerReference", "footerReference", "footnotePr", "endnotePr",
                "type", "pgSz", "pgMar", "paperSrc", "pgBorders", "lnNumType",
                "pgNumType", "cols", "formProt", "vAlign", "noEndnote", "titlePg",
                "textDirection", "bidi", "rtlGutter", "docGrid", "printerSettings",
                "sectPrChange"]


def literal_text(xml):
    """Text a reader sees typed in, with field results dropped.

    A PAGE field caches its last result in an ordinary <w:t>, so a plain sweep
    of <w:t> reports a footer that only holds a page number as literally
    reading "1". Runs between fldChar begin and end carry the instruction and
    that cached result; both are skipped.
    """
    xml = re.sub(r"<w:fldSimple\b.*?</w:fldSimple>", "", xml, flags=re.S)
    out, depth = [], 0
    for m in re.finditer(r"<w:r\b[^>]*>.*?</w:r>", xml, re.S):
        r = m.group(0)
        if 'fldCharType="begin"' in r:
            depth += 1
        elif 'fldCharType="end"' in r:
            depth = max(0, depth - 1)
        elif depth == 0:
            out += re.findall(r"<w:t[^>]*>([^<]*)</w:t>", r)
    return " ".join(out).strip()


def merge_sectpr(inner, new_elems):
    """Replace same-named children and re-sort into CT_SectPr order."""
    rank = {n: i for i, n in enumerate(SECTPR_ORDER)}
    items = []
    for m in re.finditer(r"<w:([a-zA-Z]+)\b[^>]*?/>|<w:([a-zA-Z]+)\b[^>]*?>.*?</w:\2>",
                         inner or "", re.S):
        items.append(((m.group(1) or m.group(2)), m.group(0)))
    single = {k: v for k, v in new_elems.items() if k != "headerReference"
              and k != "footerReference"}
    items = [(n, v) for n, v in items if n not in single]
    items += list(single.items())
    for k in ("headerReference", "footerReference"):
        if k in new_elems:
            items.insert(0, (k, new_elems[k]))
    items.sort(key=lambda kv: rank.get(kv[0], len(SECTPR_ORDER)))
    return "".join(v for _, v in items)


def put_in_sectpr(doc, elems):
    """Merge elements into the body sectPr, creating one when absent."""
    m = re.search(r"<w:sectPr\b[^>]*>(.*?)</w:sectPr>", doc, re.S)
    if m:
        return doc[:m.start()] + f"<w:sectPr>{merge_sectpr(m.group(1), elems)}</w:sectPr>" \
               + doc[m.end():]
    m = re.search(r"<w:sectPr\b[^>]*/>", doc)
    body = merge_sectpr("", elems)
    if m:
        return doc[:m.start()] + f"<w:sectPr>{body}</w:sectPr>" + doc[m.end():]
    return doc.replace("</w:body>", f"<w:sectPr>{body}</w:sectPr></w:body>")


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def image_run(rid, w_emu, h_emu):
    """An inline picture: the run any header paragraph can hold."""
    return (f'<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0" '
            f'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">'
            f'<wp:extent cx="{w_emu}" cy="{h_emu}"/><wp:docPr id="1001" name="header image"/>'
            f'<a:graphic xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
            f'<a:graphicData uri="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:pic xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture">'
            f'<pic:nvPicPr><pic:cNvPr id="0" name="header image"/><pic:cNvPicPr/></pic:nvPicPr>'
            f'<pic:blipFill><a:blip r:embed="{rid}" '
            f'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/>'
            f'<a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
            f'<pic:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{w_emu}" cy="{h_emu}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr></pic:pic>'
            f'</a:graphicData></a:graphic></wp:inline></w:drawing></w:r>')


def part_xml(tag, text, align, size, color, page_number, width=None, image=None):
    """One header or footer paragraph.

    A tab in the text splits the line into columns: "left\tright" for a
    two-part running head, "left\tcentre\tright" for three. The tab stops are
    positioned from the document's own text width, so the last column ends
    exactly on the right margin. Without a tab the whole line takes --align.
    """
    # CT_RPr is an ordered sequence and w:color precedes w:sz. Emitting them the
    # other way round makes the part invalid, and Word may refuse the file.
    rpr = (f'<w:rPr><w:color w:val="{color}"/>'
           f'<w:sz w:val="{int(round(size*2))}"/>'
           f'<w:szCs w:val="{int(round(size*2))}"/></w:rPr>')

    def t(s):
        return f'<w:r>{rpr}<w:t xml:space="preserve">{esc(s)}</w:t></w:r>'

    cols = (text or "").split("\t")
    tabs = ""
    if len(cols) > 1:
        if width is None:
            print(f"  NOTE  {tag}: the document declares no page size, so the tab "
                  f"stops fall back to Word's defaults and the columns will not "
                  f"reach the margins. Run --paper first.")
        else:
            stops = ([("center", width // 2)] if len(cols) > 2 else []) \
                    + [("right", width)]
            tabs = "<w:tabs>" + "".join(
                f'<w:tab w:val="{v}" w:pos="{p}"/>' for v, p in stops) + "</w:tabs>"
        align = "left"

    # PAGE field: Word computes the current page number when the file opens
    field = (f'<w:r>{rpr}<w:fldChar w:fldCharType="begin"/></w:r>'
             f'<w:r>{rpr}<w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
             f'<w:r>{rpr}<w:fldChar w:fldCharType="separate"/></w:r>'
             f'<w:r>{rpr}<w:t>1</w:t></w:r>'
             f'<w:r>{rpr}<w:fldChar w:fldCharType="end"/></w:r>')
    runs = ""
    # image = (rid, w_emu, h_emu, align): left goes before the text, centre
    # after the first tab, right after the last tab
    img_at = {"left": 0, "center": 1, "right": len(cols) - 1}.get(image[3], 0) if image else None
    if image and not any(cols) and len(cols) == 1:
        align = image[3]
    for i, c in enumerate(cols):
        if i:
            runs += f'<w:r>{rpr}<w:tab/></w:r>'
        if image and i == img_at:
            runs += image_run(*image[:3])
        # {PAGE} anywhere in the text puts the field there: "第 {PAGE} 页"
        for j, piece in enumerate(c.split("{PAGE}")):
            if j:
                runs += field
            if piece:
                runs += t(piece)
    if page_number and "{PAGE}" not in (text or ""):
        runs += field
    # Explicit spacing: the part paragraph otherwise inherits Normal, including
    # a body atLeast line height and space-after sized for body text, which
    # pushes a header down and a footer up. CT_PPrBase order: tabs, spacing, jc.
    spacing = '<w:spacing w:before="0" w:after="0" w:line="240" w:lineRule="auto"/>'
    ind = (f'<w:ind w:left="{int(round(image[4] * 20))}"/>'
           if image and len(image) > 4 and image[4] and image[4] > 1 else "")
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<w:{tag} {NS}><w:p><w:pPr>{tabs}{spacing}{ind}<w:jc w:val="{align}"/></w:pPr>'
            f'{runs}</w:p></w:{tag}>')


def set_pgmar(doc, **attrs):
    """Set attributes on the existing pgMar without disturbing the others."""
    m = re.search(r"<w:pgMar\b[^>]*/>", doc)
    if not m:
        return doc, False
    tag = m.group(0)
    for k, v in attrs.items():
        if re.search(rf'w:{k}="[^"]*"', tag):
            tag = re.sub(rf'w:{k}="[^"]*"', f'w:{k}="{v}"', tag)
        else:
            tag = tag[:-2] + f' w:{k}="{v}"/>'
    return doc[:m.start()] + tag + doc[m.end():], True


def text_width(doc):
    """Text width in twips from the document's own sectPr, or None."""
    w = re.search(r'<w:pgSz\b[^>]*w:w="(\d+)"', doc)
    m = re.search(r'<w:pgMar\b[^>]*?w:left="(\d+)"[^>]*?w:right="(\d+)"', doc) \
        or re.search(r'<w:pgMar\b[^>]*?w:right="(\d+)"[^>]*?w:left="(\d+)"', doc)
    if not (w and m):
        return None
    return int(w.group(1)) - int(m.group(1)) - int(m.group(2))


def show(members):
    blob = dict(members)
    found = False
    for fn in sorted(blob):
        m = re.match(r"word/(header|footer)(\d+)\.xml", fn)
        if not m:
            continue
        found = True
        x = blob[fn].decode("utf-8", "replace")
        txt = literal_text(x)
        extra = []
        if "PAGE" in x:
            extra.append("+page field")
        if b"<w:drawing" in blob[fn] or b"<v:imagedata" in blob[fn]:
            extra.append("+image")
        jc = re.search(r'<w:jc w:val="([a-z]+)"', x)
        kind = "header" if m.group(1) == "header" else "footer"
        print(f"  {kind} {fn.split('/')[-1]}: {txt or '(no text)'} "
              f"[{jc.group(1) if jc else 'left'}] {' '.join(extra)}")
    if not found:
        print("  no header or footer")


def _log_recipe(target, argv):
    """Append this invocation beside the template so make_package can replay
    it. Inferring the recipe from the result was never complete."""
    import json, os
    try:
        with open(os.path.abspath(target) + ".recipe", "a") as f:
            f.write(json.dumps({"cmd": [os.path.basename(argv[0])] + argv[1:]}, ensure_ascii=False) + "\n")
    except OSError:
        pass


def apply_running_heads(path, header=None, footer=None, header_distance=None,
                        footer_distance=None):
    """Write a header and/or footer from analyzer specs
    {"text","align","size","color","page_number"} into an existing docx."""
    argv = [path]
    for kind, spec in (("--header", header), ("--footer", footer)):
        if not spec:
            continue
        args = argv + [kind, spec["text"].replace("\t", "\\t"), "--align", spec["align"],
                       "--size", str(spec["size"]), "--color", spec["color"]]
        if kind == "--header" and spec.get("image"):
            im = spec["image"]
            args += ["--header-image", im["file"], "--header-image-height", str(im["h_pt"]),
                     "--header-image-align", im["align"]]
            if im.get("indent_pt"):
                args += ["--header-image-indent", str(im["indent_pt"])]
        if spec.get("page_number") and "{PAGE}" not in spec["text"]:
            args.append("--page-number")
        if header_distance is not None:
            args += ["--header-distance", str(header_distance)]
        if footer_distance is not None:
            args += ["--footer-distance", str(footer_distance)]
        saved = sys.argv
        sys.argv = ["set_header_footer.py"] + args
        try:
            rc = main()
        finally:
            sys.argv = saved
        if rc:
            return rc
    return 0


def main():
    a = sys.argv[1:]
    if not a or a[0] in ('-h', '--help'):
        print(__doc__)
        return 2
    path = a[0]
    with zipfile.ZipFile(path) as z:
        members = [(i.filename, z.read(i.filename)) for i in z.infolist()]
    blob = dict(members)

    if "--show" in a:
        print(f"Header and footer in {os.path.basename(path)}:")
        show(members)
        return 0

    opt = lambda k: a[a.index(k) + 1] if k in a else None

    # --replace edits the existing parts in place. It runs as a pass over
    # members rather than its own exit path, so it composes with --paper and
    # the rest in one invocation.
    pairs = [a[i + 1] for i, v in enumerate(a) if v == "--replace" and i + 1 < len(a)]
    subs, hits, missed = [], collections.Counter(), []
    for pr in pairs:
        if "=" not in pr:
            print(f"--replace needs OLD=NEW, got {pr!r}")
            return 2
        subs.append(tuple(pr.split("=", 1)))
    if subs:
        patched = []
        for fn, data in members:
            if re.match(r"word/(header|footer)\d+\.xml", fn):
                t = data.decode("utf-8", "replace")
                for old, new in subs:
                    # only inside <w:t>, so element names and attributes are safe
                    def sub(m, old=old, new=new):
                        if old not in m.group(2):
                            return m.group(0)
                        hits[old] += m.group(2).count(old)
                        return m.group(1) + m.group(2).replace(old, esc(new)) + m.group(3)
                    t = re.sub(r"(<w:t[^>]*>)([^<]*)(</w:t>)", sub, t)
                data = t.encode("utf-8")
            patched.append((fn, data))
        members = patched
        for old, new in subs:
            n = hits[old]
            print(f"  {'replaced' if n else 'NOT FOUND'}  {old!r} -> {new!r}"
                  + (f"  ({n}x)" if n else ""))
            if not n:
                missed.append(old)

    clear = "--clear" in a
    # A literal tab is awkward to type in a shell argument, so \t is accepted
    # as the column separator for a split running head.
    unesc = lambda s: None if s is None else s.replace("\\t", "\t")
    header, footer = unesc(opt("--header")), unesc(opt("--footer"))
    paper = (opt("--paper") or "").upper() or None
    himg = opt("--header-image")
    himg_h = float(opt("--header-image-height")) if opt("--header-image-height") else None
    himg_align = opt("--header-image-align") or "left"
    himg_indent = float(opt("--header-image-indent")) if opt("--header-image-indent") else 0.0
    if himg and header is None:
        header = ""
    # picture on one side, text on the other: give the text its own tab column
    if himg and header and "\t" not in header:
        want = (opt("--align") or "right")
        if himg_align == "left" and want == "right":
            header = "\t" + header
        elif himg_align == "left" and want == "center":
            header = "\t" + header + "\t"
        elif himg_align == "right" and want in ("left", "center"):
            header = (header + "\t") if want == "left" else ("\t" + header + "\t")
    hdist = float(opt("--header-distance")) if opt("--header-distance") else None
    fdist = float(opt("--footer-distance")) if opt("--footer-distance") else None
    ncols = int(opt("--columns")) if opt("--columns") else None
    cgap = float(opt("--column-gap")) if opt("--column-gap") else None
    if paper and paper not in PAPER:
        print(f"Unknown paper size {paper!r}. Choose from: {', '.join(PAPER)}")
        return 2
    if not clear and header is None and footer is None and not paper \
            and not subs and ncols is None and hdist is None and fdist is None:
        print("Nothing to do: pass --replace / --header / --footer / --paper / "
              "--columns / --clear / --show.")
        return 2

    size = float(opt("--size") or 9)
    color = (opt("--color") or "808080").lstrip("#").upper()
    align = opt("--align")
    pagenum = "--page-number" in a

    ct = blob["[Content_Types].xml"].decode()
    rels = blob["word/_rels/document.xml.rels"].decode()
    doc = blob["word/document.xml"].decode()

    # Replace only the kind being set. Wiping both would delete a brand logo
    # sitting in the header just because a footer was requested.
    kinds = ["header", "footer"] if clear else \
            ([] + (["header"] if header is not None else [])
                + (["footer"] if footer is not None else []))
    drop = set()
    for kind in kinds:
        existing = [fn for fn in blob if re.match(rf"word/{kind}\d+\.xml", fn)]
        if len(existing) > 1 or "<w:titlePg" in doc:
            print(f"  NOTE  replacing {len(existing)} {kind} part(s) with one; a distinct "
                  f"first page or odd/even variant is collapsed")
        drop |= set(existing)
        ct = re.sub(rf'<Override PartName="/word/{kind}\d+\.xml"[^>]*/>', "", ct)
        rels = re.sub(rf'<Relationship[^>]*Target="{kind}\d+\.xml"[^>]*/>', "", rels)
        doc = re.sub(rf"<w:{kind}Reference\b[^>]*/>", "", doc)

    tw = text_width(doc)
    if paper and tw is not None:
        cur = int(re.search(r'<w:pgSz\b[^>]*w:w="(\d+)"', doc).group(1))
        tw += PAPER[paper][0] - cur

    new_parts, added = {}, []
    if not clear:
        for kind, text, default_align, ctype in (
                ("hdr", header, "right", CT_HDR), ("ftr", footer, "center", CT_FTR)):
            if text is None:
                continue
            part = "header1.xml" if kind == "hdr" else "footer1.xml"
            rid = "rIdHdrX" if kind == "hdr" else "rIdFtrX"
            image = None
            if kind == "hdr" and himg:
                data = open(himg, "rb").read()
                ext = os.path.splitext(himg)[1].lower().lstrip(".") or "png"
                ext = {"jpg": "jpeg"}.get(ext, ext)
                # pixel size -> aspect; height in points from the flag or 0.7cm
                import struct as _st
                if data[:8] == b"\x89PNG\r\n\x1a\n":
                    pw, ph = _st.unpack(">II", data[16:24])
                else:
                    pw, ph = 3, 1
                    i = 2
                    while i < len(data) - 9:          # JPEG SOF marker
                        if data[i] == 0xFF and data[i + 1] in (0xC0, 0xC1, 0xC2):
                            ph, pw = _st.unpack(">HH", data[i + 5:i + 9]); break
                        i += 2 + _st.unpack(">H", data[i + 2:i + 4])[0]
                h_pt = himg_h or 20.0
                w_pt = h_pt * pw / ph
                new_parts[f"word/media/hdrimg1.{ext}"] = data
                new_parts[f"word/_rels/{part}.rels"] = (
                    '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                    '<Relationship Id="rIdImg1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/image" '
                    f'Target="media/hdrimg1.{ext}"/></Relationships>').encode()
                if f'Extension="{ext}"' not in ct:
                    ct = ct.replace("<Default ", f'<Default Extension="{ext}" ContentType="image/{ext}"/><Default ', 1)
                image = ("rIdImg1", int(w_pt * 12700), int(h_pt * 12700), himg_align, himg_indent)
            new_parts[f"word/{part}"] = part_xml(
                kind, text, align or default_align, size, color,
                pagenum and kind == "ftr", width=tw, image=image).encode()
            ct = ct.replace("</Types>",
                            f'<Override PartName="/word/{part}" ContentType="{ctype}"/></Types>')
            reltype = REL + ("header" if kind == "hdr" else "footer")
            rels = rels.replace("</Relationships>",
                                f'<Relationship Id="{rid}" Type="{reltype}" '
                                f'Target="{part}"/></Relationships>')
            tag = "header" if kind == "hdr" else "footer"
            doc = put_in_sectpr(doc, {f"{tag}Reference":
                                      f'<w:{tag}Reference w:type="default" r:id="{rid}"/>'})
            added.append(f"{tag} {text!r}"
                         f"{' +page number' if pagenum and kind == 'ftr' else ''}")

    if ncols is not None:
        if ncols < 1:
            print("--columns must be 1 or more")
            return 2
        # Read what the document already declares. Replacing the whole element
        # with defaults would discard a gutter and per-column widths that the
        # source chose deliberately.
        cur = re.search(r"<w:cols\b[^>]*/>|<w:cols\b[^>]*>.*?</w:cols>", doc, re.S)
        cur_xml = cur.group(0) if cur else ""
        cur_num = int((re.search(r'w:num="(\d+)"', cur_xml) or [0, "1"])[1]) if cur_xml else 1
        cur_space = re.search(r'w:space="(\d+)"', cur_xml)
        has_children = "<w:col " in cur_xml
        unequal = 'w:equalWidth="0"' in cur_xml or has_children

        if ncols == cur_num and cgap is None:
            print(f"  columns already {ncols}; left untouched"
                  + (" (per-column widths preserved)" if has_children else ""))
        else:
            if cgap is not None:
                space, origin = int(round(cgap * 20)), "from --column-gap"
            elif cur_space:
                space, origin = int(cur_space.group(1)), "kept from the document"
            else:
                space, origin = 480, "default, the document sets none"
            if unequal and ncols != cur_num:
                print(f"  NOTE  the document defines {cur_num} columns of unequal width; "
                      f"changing the count to {ncols} cannot keep those widths and they "
                      f"are dropped")
            doc = put_in_sectpr(doc, {"cols": f'<w:cols w:num="{ncols}" '
                                              f'w:space="{space}" w:equalWidth="1"/>'})
            added.append(f"{ncols} column(s)"
                         + (f", gap {space / 20:g}pt ({origin})" if ncols > 1 else ""))

    if hdist is not None or fdist is not None:
        kw = {}
        if hdist is not None: kw["header"] = int(round(hdist * 20))
        if fdist is not None: kw["footer"] = int(round(fdist * 20))
        doc, ok = set_pgmar(doc, **kw)
        added.append("header/footer distance " + ", ".join(f"{k} {v / 20:g}pt" for k, v in kw.items())
                     + ("" if ok else "  (no pgMar in the document; run --paper first)"))
    if paper:
        w, h = PAPER[paper]
        doc = put_in_sectpr(doc, {"pgSz": f'<w:pgSz w:w="{w}" w:h="{h}"/>'})
        added.append(f"paper {paper}")

    out = opt("--out") or path
    tmp = out + ".tmp"
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as z:
        for fn, data in members:
            if fn in drop:
                continue
            if fn == "[Content_Types].xml":
                data = ct.encode()
            elif fn == "word/_rels/document.xml.rels":
                data = rels.encode()
            elif fn == "word/document.xml":
                data = doc.encode()
            z.writestr(fn, data)
        for fn, data in new_parts.items():
            z.writestr(fn, data)
    shutil.move(tmp, out)

    if added:
        print("Set: " + ", ".join(added))
    elif clear:
        print("Cleared header and footer.")
    print(f"  -> {out}")
    with zipfile.ZipFile(out) as z:
        show([(i.filename, z.read(i.filename)) for i in z.infolist()])
    return 1 if missed else 0


if __name__ == "__main__":
    _rc = main()
    if not _rc and len(sys.argv) > 1 and sys.argv[1] not in ("-h", "--help") and "--show" not in sys.argv and "--list" not in sys.argv:
        _out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else sys.argv[1]
        _log_recipe(_out, sys.argv)
    sys.exit(_rc or 0)
