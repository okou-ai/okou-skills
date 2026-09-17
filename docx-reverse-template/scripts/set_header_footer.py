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
  --header TEXT      header text (omit to leave the header untouched)
  --footer TEXT      footer text
  --page-number      append an automatic PAGE field after the footer text
  --align L          left | center | right (default: header right, footer center)
  --size PT          font size (default 9)
  --color RRGGBB     colour (default 808080)
  --paper NAME       paper size: A4 | A5 | A3 | Letter | Legal
  --columns N        number of text columns (1 restores a single column). The
                     gutter and any per-column widths come from the document;
                     they are only replaced when the count actually changes.
  --column-gap PT    override the gutter. Without it the document's own gutter
                     is kept, and 24pt is used only when the document sets none.
  --out PATH         write elsewhere; default is in place

Pandoc carries the header and footer into every document produced with
--reference-doc. Image logos are out of scope here: they need extra media parts
and relationships, which is easier to do in Word.
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


def part_xml(tag, text, align, size, color, page_number):
    runs = ""
    rpr = f'<w:rPr><w:sz w:val="{int(round(size*2))}"/><w:color w:val="{color}"/></w:rPr>'
    if text:
        runs += f'<w:r>{rpr}<w:t xml:space="preserve">{esc(text)}</w:t></w:r>'
    if page_number:
        # PAGE field: Word computes the current page number when the file opens
        runs += (f'<w:r>{rpr}<w:fldChar w:fldCharType="begin"/></w:r>'
                 f'<w:r>{rpr}<w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>'
                 f'<w:r>{rpr}<w:fldChar w:fldCharType="separate"/></w:r>'
                 f'<w:r>{rpr}<w:t>1</w:t></w:r>'
                 f'<w:r>{rpr}<w:fldChar w:fldCharType="end"/></w:r>')
    return (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            f'<w:{tag} {NS}><w:p><w:pPr><w:jc w:val="{align}"/></w:pPr>{runs}</w:p></w:{tag}>')


def show(members):
    blob = dict(members)
    found = False
    for fn in sorted(blob):
        m = re.match(r"word/(header|footer)(\d+)\.xml", fn)
        if not m:
            continue
        found = True
        x = blob[fn].decode("utf-8", "replace")
        txt = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", x)).strip()
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


def main():
    a = sys.argv[1:]
    if not a:
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
    header, footer = opt("--header"), opt("--footer")
    paper = (opt("--paper") or "").upper() or None
    ncols = int(opt("--columns")) if opt("--columns") else None
    cgap = float(opt("--column-gap")) if opt("--column-gap") else None
    if paper and paper not in PAPER:
        print(f"Unknown paper size {paper!r}. Choose from: {', '.join(PAPER)}")
        return 2
    if not clear and header is None and footer is None and not paper \
            and not subs and ncols is None:
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

    new_parts, added = {}, []
    if not clear:
        for kind, text, default_align, ctype in (
                ("hdr", header, "right", CT_HDR), ("ftr", footer, "center", CT_FTR)):
            if text is None:
                continue
            part = "header1.xml" if kind == "hdr" else "footer1.xml"
            rid = "rIdHdrX" if kind == "hdr" else "rIdFtrX"
            new_parts[f"word/{part}"] = part_xml(
                kind, text, align or default_align, size, color,
                pagenum and kind == "ftr").encode()
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
    sys.exit(main())
