#!/usr/bin/env python3
"""Assemble a style-extraction package: SKILL.md, reference.docx and source.pdf.

Usage:
  python3 make_package.py <source.pdf> <reference.docx> <styles.json> <output dir> \
          [--map 1=Heading1,2=Title] [--body 2] [--name slug]
          [--top 2.4] [--right 1.8] [--bottom 2.2] [--left 1.8]

SKILL.md carries the usage, measured style values and extraction choices;
reference.docx is the artifact pandoc consumes. source.pdf is retained for
visual comparison and rebuilding the styles, not as a content model.
styles.json is not shipped because SKILL.md records the command that
re-derives it.

Pass --map, --body and every margin you overrode through verbatim: they are
every choice made along the way, and SKILL.md is the only place they are
written down. --name sets the skill name and defaults to the output
directory's name.
"""
import sys, os, re, json, shutil, zipfile, subprocess, datetime, textwrap

HALF2PT = lambda h: round(int(h) / 2, 1)
TWIP2PT = lambda t: round(int(t) / 20, 1)

MD_MAP = [
    ("`# Heading 1`", "heading 1"), ("`## Heading 2`", "heading 2"),
    ("`### Heading 3`", "heading 3"),
    ("Ordinary paragraph", "Body Text"), ("`> Block quote`", "Block Text"),
    ("Fenced code block", "Source Code"),
    ("Pipe table", "Table"),
    ("`title:` in the YAML header", "Title"),
]


def sect_parts(ref):
    """The template's own page setup, as XML fragments, for section breaks.

    A w:sectPr describes its whole section; nothing is inherited from a later
    one. A break that carries only w:cols therefore drops the page size,
    margins and header/footer references for everything before it.
    """
    with zipfile.ZipFile(ref) as z:
        d = z.read("word/document.xml").decode("utf-8", "replace")
    m = re.search(r"<w:sectPr\b.*?</w:sectPr>", d, re.S)
    sp = m.group(0) if m else ""
    g = lambda tag: "".join(re.findall(rf"<w:{tag}\b[^>]*/>", sp))
    refs = g("headerReference") + g("footerReference")
    cols = re.search(r"<w:cols\b[^>]*/>|<w:cols\b[^>]*>.*?</w:cols>", sp, re.S)
    return {"refs": refs, "pgSz": g("pgSz"), "pgMar": g("pgMar"),
            "cols": cols.group(0) if cols else ""}


def span_snippet(ref):
    """Markdown for a full-width heading inside a multi-column template."""
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


def hf_recipe(ref):
    """set_header_footer.py lines that recreate the template's header/footer.

    A PDF has none to inherit, so any part in the template was added by hand;
    the rebuild recipe must say so or a rebuild ships without it.
    """
    lines = []
    with zipfile.ZipFile(ref) as z:
        names = z.namelist()
        for kind in ("header", "footer"):
            parts = [n for n in names if re.match(rf"word/{kind}\d+\.xml", n)]
            if not parts:
                continue
            x = z.read(parts[0]).decode("utf-8", "replace")
            segs, cur, depth = [], [], 0
            for r in re.finditer(r"<w:r\b[^>]*>.*?</w:r>", x, re.S):
                run = r.group(0)
                if 'fldCharType="begin"' in run: depth += 1; continue
                if 'fldCharType="end"' in run: depth = max(0, depth - 1); continue
                if depth: continue
                if "<w:tab/>" in run:
                    segs.append("".join(cur)); cur = []
                cur += re.findall(r"<w:t[^>]*>([^<]*)</w:t>", run)
            segs.append("".join(cur))
            text = "\\t".join(seg.strip() for seg in segs)
            pn = " --page-number" if "PAGE" in x else ""
            sz = re.search(r'<w:sz w:val="(\d+)"', x); col = re.search(r'<w:color w:val="([0-9A-Fa-f]{6})"', x)
            extra = (f" --size {int(sz.group(1)) / 2:g}" if sz else "") + (f" --color {col.group(1)}" if col else "")
            lines.append(f"python3 set_header_footer.py reference.docx --{kind} '{text}'{pn}{extra}")
    return lines



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
        ind = re.search(r'<w:ind[^>]*w:firstLine="(\d+)"', p)
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

`reference.docx` carries the styles. `{src}` is the document they were taken from,
kept for visual comparison and rebuilding the styles. Write and organize the
content for the new task. Reuse the visual formatting; the source's section
order, body wording and writing conventions are not requirements.

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
python3 analyze_pdf.py {src}{repro} --json styles.json     # verify needs this
python3 verify_roundtrip.py reference.docx styles.json --structure-only
```

Scripts are in `reverse-template/pdf`. Change the style definition;
formatting applied to selected text does not change the template.

## Limits
{limits}

## Rebuild

```bash
python3 analyze_pdf.py {src}{repro} --json styles.json
{rebuild_block}
```
"""


def build(pdf, ref, jpath, outdir, mapping, margins, body=None, name=None):
    bottom = margins.get("bottom") if isinstance(margins, dict) else margins
    margins = margins if isinstance(margins, dict) else {}
    os.makedirs(outdir, exist_ok=True)
    name = name or os.path.basename(os.path.abspath(outdir))
    src = "source" + os.path.splitext(pdf)[1].lower()
    shutil.copy(ref, os.path.join(outdir, "reference.docx"))
    shutil.copy(pdf, os.path.join(outdir, src))

    d = json.load(open(jpath))
    st = styles_of(ref)
    # Every style the reader is told about, plus anything else the template
    # actually defines. A fixed list would omit a style created during the
    # optional step — Source Code is the usual one — while the FAQ still
    # explains how to create it.
    names = ["Title", "Subtitle", "heading 1", "heading 2", "heading 3",
             "Body Text", "First Paragraph", "Compact", "Block Text", "Source Code"]
    names += [n for _, n in MD_MAP if n not in names]
    rows = "\n".join(row(st, n) for n in names if n.lower() in st)
    md = "\n".join(f"| {a} | `{b}` |" for a, b in MD_MAP)

    p, mg = d["page"], d["margins_suggested_cm"]
    # Read the margins back out of the template rather than recomputing them.
    # Recomputing is how section 3 and section 4 came to disagree, and how a
    # value that is in neither the template nor the decision log got printed.
    with zipfile.ZipFile(ref) as z:
        rdoc = z.read("word/document.xml").decode("utf-8", "replace")
        rparts = z.namelist()
        rhf = []
        for part in sorted(x for x in rparts if re.match(r"word/(header|footer)\d+\.xml", x)):
            raw = z.read(part)
            t = literal_text(raw.decode("utf-8", "replace"))
            kind = "Header" if "header" in part else "Footer"
            extra = []
            if b"PAGE" in raw and "{PAGE}" not in t:
                extra.append("automatic page number")
            if b"<w:drawing" in raw or b"<v:imagedata" in raw:
                extra.append("image")
            rhf.append(f"{kind}: {t or '(no literal text)'}"
                       + (f" + {', '.join(extra)}" if extra else ""))
    cm = lambda t: round(int(t) / 1440 * 2.54, 2)
    mar = dict(re.findall(r'w:(top|right|bottom|left)="(-?\d+)"', rdoc))
    page = [f"- Paper: {p['w_cm']} x {p['h_cm']} cm"
            + (f" ({p['paper']})" if p.get("paper") else "")]
    if mar:
        page.append("- Margins: top {top} / bottom {bottom} / left {left} / "
                    "right {right} cm".format(**{k: cm(v) for k, v in mar.items()}))
    if (d.get("columns") or 1) > 1:
        page.append(f"- Columns: {d['columns']}, gap {d.get('column_gap_pt')}pt "
                    f"(column width {d.get('column_width_pt')}pt)")
    if rhf:
        page += [f"- {h}" for h in rhf]
    elif d.get("running_heads"):
        page.append("- Source header/footer, not carried over: "
                    + " / ".join(d["running_heads"]))

    # The flags that were chosen rather than measured, so the analysis can be
    # reproduced from source.pdf alone. The column count comes out of styles.json
    # rather than from a flag, where it cannot drift from the template.
    ncols = d.get("columns") or 1
    repro = (f" --body {body}" if body else "") + (f" --columns {ncols}" if ncols > 1 else "")
    # The build flags, so the rebuild line actually reproduces this template.
    # A margin corrected by hand is a measurement the analyzer got wrong; left
    # out here it is lost the moment anyone rebuilds.
    rebuild = ("" if not mapping else
               " \\\n        --map " + ",".join(f"{k}={v}" for k, v in mapping.items()))
    rebuild += "".join(f" --{k} {v}" for k, v in sorted(margins.items()))
    rebuild += "".join("\n" + l for l in hf_recipe(ref))
    logged = recipe_lines(ref, {os.path.basename(pdf): src, os.path.basename(ref): "reference.docx",
                                os.path.basename(jpath): "styles.json"})
    if logged:
        rebuild = ("\n" + "\n".join(logged)).replace(
            "\npython3 build_reference.py", "python3 build_reference.py", 1)

    # Limits that follow from this template rather than from the skill. A
    # multi-column layout has two that bite immediately and neither is
    # obvious from the style table.
    ncol = ncols

    # Only a multi-column template needs this, and the numbers have to be the
    # template's own or the section after the heading changes layout.
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
    limits.append("Heading levels and the bottom margin were judged, not read from the"
                  " PDF. If the layout looks wrong, check those first.")
    top = max((int(v[-1]) for v in mapping.values() if re.fullmatch(r"Heading\d", v)), default=0)
    if top:
        limits.append(f"`heading {top + 1}` and below were extrapolated from the levels the"
                      f" source used; set them with `set_style.py` before relying on them.")
    if "Subtitle" not in mapping.values():
        limits.append("The source has no subtitle. `Subtitle` is pandoc's default: the"
                      " Title's font and colour at 14pt. Set it with `set_style.py` before"
                      " using `subtitle:`.")
    if d.get("running_heads") and not hf_recipe(ref):
        limits.append("The source header and footer were not carried over. Add one with"
                      " `set_header_footer.py` if it matters.")
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

    open(os.path.join(outdir, "SKILL.md"), "w").write(SKILL.format(
        name=name, desc=desc, src=src, md_map=md, styles=rows,
        page="\n".join(page), repro=repro,
        rebuild_block=(rebuild.lstrip("\n") if logged else "python3 build_reference.py styles.json reference.docx" + rebuild),
        spanblock=spanblock, cols_flag=cols_flag,
        limits=limits,
        date=datetime.date.today().isoformat()))

    print(f"Package written to {outdir}/")
    for f in sorted(os.listdir(outdir)):
        print(f"  {f}")
    print("\nHand over the whole directory. SKILL.md is loadable as a skill: drop")
    print("the directory into a skills path and it triggers on its own description.")


if __name__ == "__main__":
    a = sys.argv
    if len(a) < 5:
        print(__doc__); sys.exit(2)
    mapping, bottom = {}, None
    if "--map" in a:
        for kv in a[a.index("--map") + 1].split(","):
            k, v = kv.split("=")
            mapping[k.strip()] = v.strip()
    margins = {k: float(a[a.index(f"--{k}") + 1])
               for k in ("top", "right", "bottom", "left") if f"--{k}" in a}
    bottom = margins.get("bottom")
    body = int(a[a.index("--body") + 1]) if "--body" in a else None
    nm = a[a.index("--name") + 1] if "--name" in a else None
    build(a[1], a[2], a[3], a[4], mapping, margins, body, nm)
