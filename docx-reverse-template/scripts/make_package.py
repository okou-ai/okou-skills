#!/usr/bin/env python3
"""Assemble the deliverable: SKILL.md, reference.docx and source.docx.

Usage:  python3 make_package.py <source.docx> <reference.docx> <output dir> [--name slug]

Three files, no more. SKILL.md carries the usage, the measured style values and
the source's outline; reference.docx is the artifact pandoc consumes;
source.docx is the content reference. The style values are read back out of
reference.docx, not hardcoded. --name sets the skill name and defaults to the
output directory's name.
"""
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


def outline(path):
    """The source document's headings, in reading order.

    Matched on the style's w:name, not its styleId: a Word export localises the
    id but keeps the name, so "heading 1" is reliable where "1" is not.
    """
    with zipfile.ZipFile(path) as z:
        doc = z.read("word/document.xml").decode("utf-8", "replace")
        sty = z.read("word/styles.xml").decode("utf-8", "replace")
    name = {}
    for m in re.finditer(r'<w:style\b[^>]*w:styleId="([^"]+)".*?</w:style>', sty, re.S):
        n = re.search(r'<w:name w:val="([^"]+)"', m.group(0))
        if n:
            name[m.group(1)] = n.group(1)
    out = []
    for m in re.finditer(r"<w:p\b[^>]*>.*?</w:p>|<w:p\b[^>]*/>", doc, re.S):
        para = m.group(0)
        ps = re.search(r'<w:pStyle w:val="([^"]+)"', para)
        if not ps:
            continue
        n = name.get(ps.group(1), ps.group(1))
        lv = re.fullmatch(r"heading (\d)", n, re.I)
        if not (lv or n in ("Title", "Subtitle")):
            continue
        t = literal_text(para)
        if t:
            out.append((n, int(lv.group(1)) if lv else 0, t))
    return out


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
        out[n.group(1).lower()] = dict(
            id=sid,
            font=g(r'w:ascii="([^"]*)"', str, r),
            size=g(r'<w:sz w:val="(\d+)"', HALF2PT, r),
            color=g(r'<w:color w:val="([0-9A-Fa-f]{6})"', lambda v: v.upper(), r),
            before=g(r'<w:spacing[^>]*w:before="(\d+)"', TWIP2PT, p),
            after=g(r'<w:spacing[^>]*w:after="(\d+)"', TWIP2PT, p),
            line=g(r'<w:spacing[^>]*w:line="(\d+)"', TWIP2PT, p),
            indent=TWIP2PT(ind.group(1)) if ind else None,
            align=jc.group(1) if jc else None,
        )
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
            if b"PAGE" in raw:
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

Produce Word documents in this house style. `reference.docx` carries the
styles; `{src}` is the document they were taken from.

Two different jobs, and only the first one stops at the next section:

- **Converting Markdown you already have** — one command, below.
- **Writing the content as well** — read "Writing a new document in this
  style" first. The template holds no content at all, so the sections, the
  wording that has to stay fixed, and the terminology all come from `{src}`.

## Convert

```bash
pandoc your-document.md --reference-doc=reference.docx -o output.docx
```

That single command applies every style in the template. It does not supply
any content — see the section below for that.

No pandoc? `brew install pandoc`, `sudo apt install pandoc`, or
`winget install --id JohnMacFarlane.Pandoc`. Without administrator rights,
download the build matching your OS and CPU from
<https://github.com/jgm/pandoc/releases> and put its `bin` on PATH; it is a
single static binary.

## Markdown that picks up these styles

| Markdown construct | Style it maps to |
|---|---|
{md_map}

Put the document title in the YAML header, not in a `#` heading:

```markdown
---
title: Document title
author: Author
date: 2026-01-01
---

# Chapter one

Body text.
```

## What the template sets

| Style | Font / size / colour | Spacing | First-line indent | Alignment |
|---|---|---|---|---|
{styles}

{page}

## Writing a new document in this style

`--reference-doc` discards every piece of body content, so the template knows
the styles and nothing about what the source document said. When the task is
another document of this kind, or a revised version, read `{src}`.

Its section skeleton:

{outline}

Also take from it the text that belongs to the **document type** rather than
to that one instance — legal and confidentiality notices, defined terms,
standard table headers, metric definitions — along with its terminology and
level of detail.

What is fixed and what varies cannot be settled from a single sample: text
that looks like boilerplate may be specific to this instance, and a value that
looks specific may be required in every version. With one document, read it
and decide. With several, compare them first — what differs is variable, but
what matches is only *probably* fixed, since two samples can coincide.

The header and footer **are** in the template and carry the source's own
document number, version and owner. Replace them before reusing this template
more widely, or every document made from it inherits them.

## Adjusting it

Edit the style *definition*, not the text: formatting applied to a selection
does nothing to the template.

```bash
python3 set_style.py reference.docx --list
python3 set_style.py reference.docx "heading 2" --size 14 --color 1B4F72 --before 12
python3 set_style.py reference.docx "Source Code" --create --font Consolas --size 9
python3 set_header_footer.py reference.docx --replace 'OLD=NEW'
python3 verify_reference.py reference.docx
```

The scripts are in the `docx-reverse-template` skill.

## Known limits

- A font renders only if it is installed locally; otherwise Word substitutes
  one. Install the font rather than changing the template.
- Pandoc only writes the style names in the table above. A new name such as
  "Company Heading" is never referenced.
- Code blocks use `Source Code`, which pandoc generates on output. Customising
  it means creating a paragraph style with that exact name.
- Headings that come out looking like body text mean the template is missing
  that style. `verify_reference.py` says which one.{limits}

---

Built from `{src}` on {date}. Every value above was read out of that file,
not inferred. To rebuild:

```bash
python3 build_reference.py {src} reference.docx
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

    # The outline is the only record of the source's *content* that survives.
    # reference.docx carries no body text, so without it there is nothing to
    # work from when the task is "another document like this one".
    # Limits that follow from this template rather than from the skill. A
    # multi-column layout has two that bite immediately and neither is
    # obvious from the style table.
    limits = []
    if pg["cols"]:
        narrow = pg["narrowest_cm"]
        w = f"the narrowest column, {narrow} cm," if narrow else "a text column"
        limits += [
            f"A table wider than {w} overflows it. Set the column widths "
            f"explicitly rather than letting pandoc size them.",
            "Headings do not span the columns. Everything sits in one `sectPr`, "
            "and a full-width title needs a second section, which "
            "`--reference-doc` cannot add.",
        ]

    # An inverted hierarchy is the source's own value, reproduced rather than
    # corrected. Say so, or the next person silently "fixes" it.
    LADDER = ["Title", "heading 1", "heading 2", "heading 3",
              "heading 4", "heading 5", "heading 6"]
    sizes = [(n, st[n.lower()]["size"]) for n in LADDER
             if st.get(n.lower()) and st[n.lower()].get("size")]
    for (an, a), (bn, b) in zip(sizes, sizes[1:]):
        if b >= a:
            limits.append(
                f"`{bn}` is {b}pt against `{an}` at {a}pt — the source's own "
                f"value, copied as it is rather than corrected. Change it only "
                f"to depart from the source deliberately.")
            break
    limits = "\n".join("\n".join(textwrap.wrap(l, 76, initial_indent="- ",
                                              subsequent_indent="  "))
                       for l in limits)
    limits = "\n" + limits if limits else ""

    ol = outline(orig)
    ol_md = "\n".join(f"{'  ' * max(0, lv - 1)}- {t}  `{n}`" for n, lv, t in ol) \
        or "_The source has no headings to record._"

    # The description is what makes an agent reach for this package at all, so
    # it names the look rather than describing the file.
    look = st.get("heading 1") or st.get("title") or st.get("body text") or {}
    marks = ", ".join(v for v in (look.get("font"),
                                  f"#{look['color']}" if look.get("color") else "") if v)
    desc = (f"Produce Word documents in the {name} house style"
            + (f" ({marks})" if marks else "")
            + f". Use when asked to write, format, re-issue or restyle a document "
              f"in this style, or to produce another document like {src}.")
    # Quote it. The description carries hex colours, and " #" opens a comment
    # in an unquoted YAML scalar, so everything from the first colour onward -
    # including every trigger phrase - is dropped when the frontmatter is
    # parsed, and the published skill never matches anything.
    desc = '"' + desc.replace('\\', '\\\\').replace('"', '\\"') + '"' 

    open(os.path.join(outdir, "SKILL.md"), "w").write(SKILL.format(
        name=name, desc=desc, src=src, md_map=md, styles=rows,
        page="\n".join(page_lines), outline=ol_md, limits=limits,
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
