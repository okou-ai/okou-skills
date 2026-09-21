#!/usr/bin/env python3
"""Assemble a style-extraction package: SKILL.md, reference.docx and source.docx.

Usage:  python3 make_package.py <source.docx> <reference.docx> <output dir> [--name slug]

SKILL.md carries the usage and measured style values; reference.docx is the
artifact pandoc consumes. source.docx is retained for visual comparison and
rebuilding the styles, not as a content model. The style values are read back
out of reference.docx, not hardcoded. --name sets the skill name and defaults
to the output directory's name.
"""
import json
import sys, os, re, shutil, zipfile, subprocess, datetime, textwrap

HALF2PT = lambda h: round(int(h) / 2, 1)
TWIP2PT = lambda t: round(int(t) / 20, 1)
TWIP2CM = lambda t: round(int(t) / 1440 * 2.54, 2)

# Markdown construct -> Word style name, for the reader of the package
MD_MAP = [
    ("`# Heading 1`", "heading 1"), ("`## Heading 2`", "heading 2"),
    ("`### Heading 3`", "heading 3"),
    ("Ordinary paragraph", "Body Text"), ("`> Block quote`", "Block Text"),
    ("Fenced code block", "Source Code"),
    ("Pipe table", "Table"),
    ("`title:` in the YAML header", "Title"),
]


def header_substitutions(orig, ref):
    """--replace pairs inferred by diffing the header and footer text.

    They are applied in a separate step, so the packager is never told about
    them. Left out of the rebuild recipe, a rebuild silently restores the
    source's own document number and owner.
    """
    def texts(path):
        out = {}
        with zipfile.ZipFile(path) as z:
            for n in sorted(z.namelist()):
                if re.match(r"word/(header|footer)\d+\.xml", n):
                    out[n] = literal_text(z.read(n).decode("utf-8", "replace"))
        return out
    a, b = texts(orig), texts(ref)
    pairs = []
    for n in a:
        if n not in b or a[n] == b[n]:
            continue
        import difflib
        sm = difflib.SequenceMatcher(None, a[n].split(), b[n].split(), autojunk=False)
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag == "replace":
                old, new = " ".join(a[n].split()[i1:i2]), " ".join(b[n].split()[j1:j2])
                if old and new and (old, new) not in pairs:
                    pairs.append((old, new))
    return pairs


def norm(x):
    return re.sub(r"\s+/>", "/>", re.sub(r"\s+", " ", x))


def docdefault_size(path):
    """Body size in points from docDefaults, where a style that inherits
    everything gets it from. No other script in the toolchain reads it, so a
    heading smaller than the body went unnoticed."""
    with zipfile.ZipFile(path) as z:
        x = norm(z.read("word/styles.xml").decode("utf-8", "replace"))
    m = re.search(r"<w:docDefaults>.*?</w:docDefaults>", x, re.S)
    if not m:
        return None
    sz = re.search(r'<w:sz w:val="(\d+)"', m.group(0))
    return HALF2PT(sz.group(1)) if sz else None


def sect_parts(ref):
    """The template's own page setup, as XML fragments, for section breaks.
    A w:sectPr describes its whole section; nothing is inherited from a later
    one, so a break carrying only w:cols drops page size, margins and the
    header/footer references for everything before it."""
    with zipfile.ZipFile(ref) as z:
        d = z.read("word/document.xml").decode("utf-8", "replace")
    m = re.search(r"<w:sectPr\b.*?</w:sectPr>", d, re.S)
    sp = m.group(0) if m else ""
    g = lambda tag: "".join(re.findall(rf"<w:{tag}\b[^>]*/>", sp))
    cols = re.search(r"<w:cols\b[^>]*/>|<w:cols\b[^>]*>.*?</w:cols>", sp, re.S)
    return {"refs": g("headerReference") + g("footerReference"), "pgSz": g("pgSz"),
            "pgMar": g("pgMar"), "cols": cols.group(0) if cols else ""}


def span_snippet(ref):
    sp = sect_parts(ref)
    n = re.search(r'w:num="(\d+)"', sp["cols"])
    if not n or int(n.group(1)) < 2:
        return ""
    fixed = sp["refs"] + '<w:type w:val="continuous"/>' + sp["pgSz"] + sp["pgMar"]
    brk = lambda cols: f"```{{=openxml}}\n<w:p><w:pPr><w:sectPr>{fixed}{cols}</w:sectPr></w:pPr></w:p>\n```"
    return ("\n## Full-width heading\n\n"
            "A block that spans every column ends a 1-column section; the columns"
            " resume after it. The numbers are this template's; do not shorten them.\n\n"
            "````markdown\n---\ntitle: Document title\nsubtitle: Subtitle\n---\n\n"
            + brk('<w:cols w:num="1"/>') + "\n\n"
            "Body text, in columns.\n\n" + brk(sp["cols"]) + "\n\n"
            "# Heading across all columns\n\n" + brk('<w:cols w:num="1"/>') + "\n\n"
            "Body text, in columns.\n\n" + brk(sp["cols"]) + "\n````\n\n"
            "The break after the title block closes a 1-column section holding the"
            " title and subtitle. The break at the very end makes the last"
            " section balance its columns; without it column 1 fills first."
            " The title block is full width; to keep the title inside the"
            " columns, delete the first break.\n")


def layout_recipe(orig, ref):
    """set_header_footer.py --columns line when the template's columns differ
    from the source's; nothing otherwise."""
    def cols(path):
        with zipfile.ZipFile(path) as z:
            d = z.read("word/document.xml").decode("utf-8", "replace")
        m = re.search(r"<w:cols\b[^>]*/>|<w:cols\b[^>]*>.*?</w:cols>", d, re.S)
        if not m:
            return 1, None
        n = re.search(r'w:num="(\d+)"', m.group(0)); g = re.search(r'w:space="(\d+)"', m.group(0))
        return (int(n.group(1)) if n else 1), (int(g.group(1)) if g else None)
    a, b = cols(orig), cols(ref)
    if a == b:
        return []
    line = f"python3 set_header_footer.py reference.docx --columns {b[0]}"
    if b[1] is not None and b[1] != a[1]:
        line += f" --column-gap {b[1] / 20:g}"
    return [line]


def style_recipe(orig, ref):
    """set_style.py lines for every style whose values differ from the source."""
    a, b = styles_of(orig), styles_of(ref)
    flags = [("font", "--font", lambda v: f'"{v}"'), ("size", "--size", str),
             ("color", "--color", str), ("before", "--before", str),
             ("after", "--after", str), ("line", "--line", str),
             ("indent", "--indent", str), ("align", "--align", str)]
    out = []
    for name, tv in b.items():
        sv = a.get(name)
        if not sv:
            continue                      # created by build_reference, not by hand
        diff = [f"{fl} {fmt(tv[k])}" for k, fl, fmt in flags
                if tv.get(k) is not None and tv.get(k) != sv.get(k)]
        if diff:
            out.append(f'python3 set_style.py reference.docx "{name}" ' + " ".join(diff))
    return out



def recipe_lines(ref, renames):
    """The commands that produced this template, replayed from the log the
    scripts append to beside reference.docx. Only the commands from the last
    build onward are live; earlier ones were overwritten by that build."""
    import shlex
    log = os.path.abspath(ref) + ".recipe"
    if not os.path.exists(log):
        return None
    cmds = []
    for line in open(log, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        try:
            cmds.append(json.loads(line)["cmd"])
        except (ValueError, KeyError):
            continue
    last = max((i for i, c in enumerate(cmds) if c and c[0] == "build_reference.py"), default=None)
    if last is None:
        return None
    out = []
    for c in cmds[last:]:
        toks = [renames.get(os.path.basename(t), t) if ("/" in t or t in renames) else t for t in c]
        toks = [renames.get(os.path.basename(t), t) for t in toks]
        out.append("python3 " + shlex.join(toks))
    return out


def literal_text(xml):
    """Text a reader sees typed in, with field results dropped.

    A PAGE field caches its last result in an ordinary <w:t>, so a plain sweep
    of <w:t> reports a footer that only holds a page number as literally
    reading "1". Runs between fldChar begin and end carry the instruction and
    that cached result; both are skipped.
    """
    xml = re.sub(r"<w:fldSimple\b[^>]*w:instr=\"[^\"]*PAGE[^\"]*\".*?</w:fldSimple>",
                 "<w:r><w:t>{PAGE}</w:t></w:r>", xml, flags=re.S)
    xml = re.sub(r"<w:fldSimple\b.*?</w:fldSimple>", "", xml, flags=re.S)
    xml = xml.replace("<w:tab/>", "<w:t>\\t</w:t>")
    runs = [m.group(0) for m in re.finditer(r"<w:r\b[^>]*>.*?</w:r>", xml, re.S)]
    out, depth = [], 0
    for i, r in enumerate(runs):
        if 'fldCharType="begin"' in r:
            depth += 1
            rest = "".join(runs[i:])
            end = rest.find('fldCharType="end"')
            if re.search(r"<w:instrText[^>]*>[^<]*\bPAGE\b", rest[:end if end > 0 else None]):
                out.append("{PAGE}")
        elif 'fldCharType="end"' in r:
            depth = max(0, depth - 1)
        elif depth == 0:
            out += re.findall(r"<w:t[^>]*>([^<]*)</w:t>", r)
    text = re.sub(r" {2,}", " ", " ".join(out))
    return text.replace(" \\t ", "\\t").replace(" \\t", "\\t").replace("\\t ", "\\t").strip()


def styles_of(path):
    with zipfile.ZipFile(path) as z:
        x = z.read("word/styles.xml").decode("utf-8", "replace")
    out = {}
    for m in re.finditer(r"<w:style\b[^>]*?w:styleId=\"([^\"]+)\"[^>]*>(.*?)</w:style>", x, re.S):
        sid, inner = m.group(1), m.group(2)
        n = re.search(r"<w:name\s+w:val=\"([^\"]*)\"", inner)
        if not n:
            continue
        rpr = re.search(r"<w:rPr>.*?</w:rPr>", inner, re.S)
        r = rpr.group(0) if rpr else ""
        ppr = re.search(r"<w:pPr>.*?</w:pPr>", inner, re.S)
        p = ppr.group(0) if ppr else ""
        g = lambda pat, conv, src: (lambda mm: conv(mm.group(1)) if mm else None)(
            re.search(pat, src))
        ind = re.search(r'<w:ind[^>]*w:(?:firstLine)="(\d+)"', p)
        jc = re.search(r'<w:jc w:val="([a-z]+)"', p)
        based = re.search(r'<w:basedOn w:val="([^"]+)"', inner)
        out[n.group(1).lower()] = dict(
            id=sid, based_on=based.group(1) if based else None,
            font=g(r'w:ascii="([^"]*)"', str, r),
            size=g(r'<w:sz w:val="(\d+)"', HALF2PT, r),
            color=g(r'<w:color w:val="([0-9A-Fa-f]{6})"', lambda v: v.upper(), r),
            before=g(r'<w:spacing[^>]*w:before="(\d+)"', TWIP2PT, p),
            after=g(r'<w:spacing[^>]*w:after="(\d+)"', TWIP2PT, p),
            line=g(r'<w:spacing[^>]*w:line="(\d+)"', TWIP2PT, p),
            indent=TWIP2PT(ind.group(1)) if ind else None,
            align=jc.group(1) if jc else None,
        )
    # A style that sets nothing gets everything from basedOn, and past the root
    # from docDefaults - which is where the body size normally lives. Fill in
    # the effective font, size and colour so the table shows real values.
    by_id = {v["id"]: v for v in out.values()}
    dd = re.search(r"<w:docDefaults>.*?</w:docDefaults>", x, re.S)
    ddv = {}
    if dd:
        f = re.search(r'w:ascii="([^"]*)"', dd.group(0))
        z_ = re.search(r'<w:sz w:val="(\d+)"', dd.group(0))
        ddv = {"font": f.group(1) if f else None, "size": HALF2PT(z_.group(1)) if z_ else None}
    for v in out.values():
        cur, seen = v, 0
        while cur and seen < 8 and (v["font"] is None or v["size"] is None or v["color"] is None):
            parent = by_id.get(cur["based_on"]) if cur["based_on"] else None
            if not parent:
                break
            for k in ("font", "size", "color"):
                if v[k] is None and parent[k] is not None:
                    v[k] = parent[k]
            cur, seen = parent, seen + 1
        for k in ("font", "size"):
            if v[k] is None and ddv.get(k) is not None:
                v[k] = ddv[k]
    return out


def page_of(path):
    with zipfile.ZipFile(path) as z:
        d = z.read("word/document.xml").decode("utf-8", "replace")
        names = z.namelist()
        hf = []
        for part in [n for n in names if re.match(r"word/(header|footer)\d+\.xml", n)]:
            raw = z.read(part)
            t = literal_text(raw.decode("utf-8", "replace"))
            kind = "Header" if "header" in part else "Footer"
            extra = []
            if b"PAGE" in raw and "{PAGE}" not in t:
                extra.append("automatic page number")
            if b"<w:drawing" in raw or b"<v:imagedata" in raw:
                extra.append("image")
            hf.append(f"{kind}: {t or '(no literal text)'}"
                      + (f" + {', '.join(extra)}" if extra else ""))
    s = re.search(r"<w:sectPr\b.*?</w:sectPr>", d, re.S)
    s = s.group(0) if s else ""
    pg = re.search(r'<w:pgSz[^>]*w:w="(\d+)"[^>]*w:h="(\d+)"', s) or \
         re.search(r'<w:pgSz[^>]*w:h="(\d+)"[^>]*w:w="(\d+)"', s)
    mar = dict(re.findall(r'w:(top|right|bottom|left)="(-?\d+)"', s))
    # Columns are inherited from the source sectPr without anyone asking for
    # them, so a template can be two-column while its README says nothing.
    cols = re.search(r"<w:cols\b[^>]*/>|<w:cols\b[^>]*>.*?</w:cols>", s, re.S)
    col, narrow = None, None
    if cols:
        c = cols.group(0)
        n = re.search(r'w:num="(\d+)"', c)
        n = int(n.group(1)) if n else (len(re.findall(r"<w:col\b", c)) or 1)
        if n > 1:
            gap = re.search(r'w:space="(\d+)"', c)
            widths = re.findall(r'<w:col\b[^>]*w:w="(\d+)"', c)
            # Unequal columns are common; a table has to fit the narrowest.
            if widths:
                narrow = min(TWIP2CM(w) for w in widths)
            elif pg and mar:
                text = int(pg.group(1)) - int(mar.get("left", 0)) - int(mar.get("right", 0))
                spc = int(gap.group(1)) if gap else 0
                narrow = TWIP2CM((text - spc * (n - 1)) // n)
            col = f"- Columns: {n}"
            if gap:
                col += f", gutter {TWIP2CM(gap.group(1))} cm"
            if widths:
                col += (" (per-column widths "
                        + ", ".join(f"{TWIP2CM(w)} cm" for w in widths)
                        + ", inherited as they are)")
    return {"size": (TWIP2CM(pg.group(1)), TWIP2CM(pg.group(2))) if pg else None,
            "margin": {k: TWIP2CM(v) for k, v in mar.items()} or None,
            "cols": col, "narrowest_cm": narrow, "hf": hf}


def row(st, name):
    s = st.get(name.lower())
    if not s:
        return f"| {name} | not defined | - | - | - |"
    look = " ".join(v for v in (s["font"],
                                f"{s['size']}pt" if s["size"] else "",
                                f"#{s['color']}" if s["color"] else "") if v)
    sp = " ".join(v for v in (f"before {s['before']}" if s["before"] else "",
                              f"after {s['after']}" if s["after"] else "",
                              f"line {s['line']}" if s["line"] else "") if v)
    indent = f"{s['indent']}pt" if s["indent"] else "-"
    return (f"| {name} | {look or 'inherited from Normal'} | {sp or '-'} | "
            f"{indent} | {s['align'] or '-'} |")


SKILL = """---
name: {name}
description: {desc}
---

# {name}

`reference.docx` carries the styles, header and footer. `{src}` is the document
they were taken from, kept for visual comparison and rebuilding the styles.
Write and organize the content for the new task. Reuse the visual formatting;
the source's section order, body wording and writing conventions are not requirements.

## Convert

```bash
pandoc doc.md --reference-doc=reference.docx -o out.docx{cols_flag}
```

- Put the title in the YAML header as `title:`, not as a `#` heading.
- For a PDF, convert to docx and export from Word. Pandoc's direct PDF output ignores the template.
- For CJK text add `-f markdown-smart`, or straight quotes become curly.
- No pandoc: `brew install pandoc`, `sudo apt install pandoc`, `winget install --id JohnMacFarlane.Pandoc`, or a static build from <https://github.com/jgm/pandoc/releases>.
{spanblock}
## Markdown → style

| Write | Gets |
|---|---|
{md_map}
| `subtitle:` in the YAML header | `Subtitle` |

The first paragraph after a heading gets `First Paragraph`; the rest get
`Body Text`.

## Styles

| Style | Font / size / colour | Spacing | Indent | Align |
|---|---|---|---|---|
{styles}

{page}

## Adjust

```bash
python3 set_style.py reference.docx --list
python3 set_style.py reference.docx "heading 2" --size 14 --color 1B4F72 --before 12
python3 set_style.py reference.docx "Source Code" --create --font Consolas --size 9
python3 set_header_footer.py reference.docx --replace 'OLD=NEW'
python3 verify_reference.py reference.docx
```

Scripts are in `reverse-template/docx`. Change the style definition;
formatting applied to selected text does not change the template.

## Limits
{limits}

## Rebuild

```bash
{rebuild_block}
python3 verify_reference.py reference.docx
```
"""


def build(orig, ref, outdir, name=None):
    os.makedirs(outdir, exist_ok=True)
    name = name or os.path.basename(os.path.abspath(outdir))
    src = "source" + os.path.splitext(orig)[1].lower()
    shutil.copy(ref, os.path.join(outdir, "reference.docx"))
    shutil.copy(orig, os.path.join(outdir, src))

    st, pg = styles_of(ref), page_of(ref)
    names = ["Title", "heading 1", "heading 2", "heading 3",
             "Body Text", "First Paragraph", "Compact", "Block Text"]
    rows = "\n".join(row(st, n) for n in names)
    md = "\n".join(f"| {a} | `{b}` |" for a, b in MD_MAP)

    page_lines = []
    if pg["size"]:
        page_lines.append(f"- Paper: {pg['size'][0]} x {pg['size'][1]} cm")
    if pg["margin"]:
        m = pg["margin"]
        page_lines.append("- Margins: top {top} / bottom {bottom} / left {left} / "
                          "right {right} cm".format(**m))
    if pg["cols"]:
        page_lines.append(pg["cols"])
    page_lines += [f"- {h}" for h in pg["hf"]] or ["- No header or footer"]

    # Limits that follow from this template rather than from the skill. A
    # multi-column layout has two that bite immediately and neither is
    # obvious from the style table.
    spanblock = span_snippet(ref)

    limits = []
    cols_flag = " --columns=20"
    limits.append("Tables fill the column they sit in; `--columns=20` on the"
                  " convert command does that for both table syntaxes."
                  " Do not raise it.")
    limits.append("Install the fonts named above on the machine that renders the output.")
    limits.append("Only the style names in the table are ever used. Do not add new ones.")
    limits.append("Pandoc creates `Source Code` itself. To restyle code blocks, create a"
                  " style with exactly that name.")
    limits.append("`Compact` sets both table cells and tight lists; its spacing cannot"
                  " be changed for one without the other.")
    limits.append("A heading that renders as body text means that style is missing;"
                  " `verify_reference.py` names it.")
    if any("[" in h for h in pg["hf"]):
        limits.append("The header carries placeholders in square brackets. Before"
                      " converting, unzip reference.docx, replace the bracketed text in"
                      " `word/header*.xml` and `word/footer*.xml`, and zip it back; or run"
                      " `set_header_footer.py --replace 'OLD=NEW'` from"
                      " `reverse-template/docx`.")
    elif pg["hf"]:
        limits.append("The header and footer still carry the source's own title, document"
                      " number, version or owner. Replace that text in `word/header*.xml`"
                      " and `word/footer*.xml` before converting, or run"
                      " `set_header_footer.py --replace 'OLD=NEW'` from"
                      " `reverse-template/docx`.")

    # An inverted hierarchy is the source's own value, reproduced rather than
    # corrected. Say so, or the next person silently "fixes" it.
    LADDER = ["Title", "heading 1", "heading 2", "heading 3",
              "heading 4", "heading 5", "heading 6"]
    sizes = [(n, st[n.lower()]["size"]) for n in LADDER
             if st.get(n.lower()) and st[n.lower()].get("size")]
    for (an, a), (bn, b) in zip(sizes, sizes[1:]):
        if b >= a:
            limits.append(
                f"`{bn}` is {b}pt against `{an}` at {a}pt. This is the source's own"
                f" value; change it only to depart from the source on purpose.")
            break

    # A heading smaller than the body is the more glaring inversion and the
    # ladder above cannot see it, because the body size usually lives in
    # docDefaults rather than on Body Text.
    body_pt = (st.get("body text") or {}).get("size") or docdefault_size(ref)
    if body_pt:
        small = [(n, v) for n, v in sizes if n != "Title" and v <= body_pt]
        if small:
            limits.append(
                ", ".join(f"`{n}` at {v}pt" for n, v in small)
                + f" {'is' if len(small) == 1 else 'are'} no larger than body text"
                  f" at {body_pt}pt. This is the source's own value; change it only"
                  f" to depart from the source on purpose.")
    limits = "\n".join("\n".join(textwrap.wrap(l, 76, initial_indent="- ",
                                              subsequent_indent="  "))
                       for l in limits)
    limits = "\n" + limits if limits else ""

    # The description is what makes an agent reach for this package at all, so
    # it names the look rather than describing the file.
    look = st.get("heading 1") or st.get("title") or st.get("body text") or {}
    marks = ", ".join(v for v in (look.get("font"),
                                  f"#{look['color']}" if look.get("color") else "") if v)
    desc = (f"Produce Word documents in the {name} house style"
            + (f" ({marks})" if marks else "")
            + ". Use when asked to apply this visual style to new content "
              "or restyle a document with its formatting.")
    # Quote it. The description carries hex colours, and " #" opens a comment
    # in an unquoted YAML scalar, so everything from the first colour onward -
    # including every trigger phrase - is dropped when the frontmatter is
    # parsed, and the published skill never matches anything.
    desc = '"' + desc.replace('\\', '\\\\').replace('"', '\\"') + '"' 

    subs = header_substitutions(orig, ref)
    replaces = ""
    if subs:
        replaces = ("\npython3 set_header_footer.py reference.docx \\\n        "
                    + " \\\n        ".join(f"--replace '{o}={n}'" for o, n in subs))
    replaces += "".join("\n" + l for l in layout_recipe(orig, ref))
    logged = recipe_lines(ref, {os.path.basename(orig): src, os.path.basename(ref): "reference.docx"})
    rebuild_block = ("\n".join(logged) if logged
                     else "python3 build_reference.py " + src + " reference.docx" + replaces)

    open(os.path.join(outdir, "SKILL.md"), "w").write(SKILL.format(
        name=name, desc=desc, src=src, md_map=md, styles=rows,
        page="\n".join(page_lines), limits=limits,
        spanblock=spanblock, cols_flag=cols_flag,
        rebuild_block=rebuild_block,
        date=datetime.date.today().isoformat()))

    print(f"Package written to {outdir}/")
    for f in sorted(os.listdir(outdir)):
        print(f"  {f}")
    print("\nHand over the whole directory. SKILL.md is loadable as a skill: drop")
    print("the directory into a skills path and it triggers on its own description.")


if __name__ == "__main__":
    a = sys.argv
    if len(a) < 4:
        print(__doc__)
        sys.exit(2)
    nm = a[a.index("--name") + 1] if "--name" in a else None
    build(a[1], a[2], a[3], nm)
