#!/usr/bin/env python3
"""Add or replace the header and footer in reference.docx. No Word required.

Usage:
  python3 set_header_footer.py <reference.docx> --header "Company" --footer "Confidential"
  python3 set_header_footer.py <reference.docx> --footer "Page " --page-number --align center
  python3 set_header_footer.py <reference.docx> --show
  python3 set_header_footer.py <reference.docx> --clear

Options:
  --header TEXT      header text (omit to leave the header untouched)
  --footer TEXT      footer text
  --page-number      append an automatic PAGE field after the footer text
  --align L          left | center | right (default: header right, footer center)
  --size PT          font size (default 9)
  --color RRGGBB     colour (default 808080)
  --out PATH         write elsewhere; default is in place

Pandoc carries the header and footer into every document produced with
--reference-doc. Image logos are out of scope here: they need extra media parts
and relationships, which is easier to do in Word.
"""
import sys, os, re, shutil, zipfile

NS = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"')
CT_HDR = ("application/vnd.openxmlformats-officedocument."
          "wordprocessingml.header+xml")
CT_FTR = ("application/vnd.openxmlformats-officedocument."
          "wordprocessingml.footer+xml")
REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/"


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
    clear = "--clear" in a
    header, footer = opt("--header"), opt("--footer")
    if not clear and header is None and footer is None:
        print("Nothing to do: pass --header / --footer / --clear / --show.")
        return 2

    size = float(opt("--size") or 9)
    color = (opt("--color") or "808080").lstrip("#").upper()
    align = opt("--align")
    pagenum = "--page-number" in a

    ct = blob["[Content_Types].xml"].decode()
    rels = blob["word/_rels/document.xml.rels"].decode()
    doc = blob["word/document.xml"].decode()

    # drop existing header/footer parts, relationships and references
    drop = {fn for fn in blob if re.match(r"word/(header|footer)\d+\.xml", fn)}
    ct = re.sub(r'<Override PartName="/word/(header|footer)\d+\.xml"[^>]*/>', "", ct)
    rels = re.sub(r'<Relationship[^>]*Target="(header|footer)\d+\.xml"[^>]*/>', "", rels)
    doc = re.sub(r"<w:(header|footer)Reference\b[^>]*/>", "", doc)

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
            ref = f'<w:{tag}Reference w:type="default" r:id="{rid}"/>'
            if "<w:sectPr>" in doc:
                doc = doc.replace("<w:sectPr>", "<w:sectPr>" + ref, 1)
            elif re.search(r"<w:sectPr\b[^>]*/>", doc):
                doc = re.sub(r"<w:sectPr\b[^>]*/>", f"<w:sectPr>{ref}</w:sectPr>", doc, 1)
            else:
                doc = doc.replace("</w:body>", f"<w:sectPr>{ref}</w:sectPr></w:body>")
            added.append(f"{tag} {text!r}"
                         f"{' +page number' if pagenum and kind == 'ftr' else ''}")

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

    print("Cleared header and footer." if clear else "Set: " + ", ".join(added))
    print(f"  -> {out}")
    with zipfile.ZipFile(out) as z:
        show([(i.filename, z.read(i.filename)) for i in z.infolist()])
    return 0


if __name__ == "__main__":
    sys.exit(main())
