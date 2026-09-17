#!/usr/bin/env python3
"""Assemble the deliverable: SKILL.md, reference.docx and source.pdf.

Usage:
  python3 make_package.py <source.pdf> <reference.docx> <styles.json> <output dir> \
          [--map 1=Heading1,2=Title] [--body 2] [--name slug]
          [--top 2.4] [--right 1.8] [--bottom 2.2] [--left 1.8]

Three files, no more. SKILL.md carries the usage, the measured style values,
the choices made and the source's outline; reference.docx is the artifact
pandoc consumes; source.pdf is the content reference. styles.json is not
shipped because SKILL.md records the exact command that re-derives it, and the
analysis is reproducible byte for byte.

Pass --map, --body and every margin you overrode through verbatim: they are
every choice made along the way, and SKILL.md is the only place they are
written down. --name sets the skill name and defaults to the output
directory's name.
"""
import sys, os, re, json, shutil, zipfile, subprocess, datetime

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

Produce Word documents in this house style. `reference.docx` carries the
styles; `{src}` is the document they were reverse-engineered from.

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

For a PDF, convert to docx first and export from Word. Going straight to PDF
with pandoc bypasses `--reference-doc` entirely and loses every style here.

## Markdown that picks up these styles

| Markdown construct | Style it maps to |
|---|---|
{md_map}

## What the template sets

| Style | Font / size / colour | Spacing | First-line indent | Alignment |
|---|---|---|---|---|
{styles}

{page}

## What was inferred rather than read

A PDF has no style layer, so these values were measured from glyph
coordinates. Start here if something looks off.

{review}

| Field | Source | Confidence |
|---|---|---|
| Font / size / colour | Recorded exactly in the PDF | High |
| Spacing / line height / indent / alignment | Computed from coordinates | High |
| Heading levels | Assigned from the sample text (above) | Depends on the review |
| Top / left / right margins | Measured, then rounded | Medium |
| Bottom margin | Only bounded, never measured | Low |

To re-derive every measured value, run this against `{src}` with the
`pdf-reverse-template` skill; the output is reproducible byte for byte:

```bash
python3 analyze_pdf.py {src}{repro} --json styles.json
```

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

## Adjusting it

Open `reference.docx` in Word and **right-click the style in the Styles pane ->
Modify**. Editing the style *definition* is what matters; selecting text and
changing its font is direct formatting and does nothing to the template.

Without Word, use the scripts from the `pdf-reverse-template` skill:

```bash
python3 set_style.py reference.docx "heading 2" --size 14 --color 1B4F72 --before 12
python3 set_style.py reference.docx "Source Code" --create --font Consolas --size 9
python3 set_header_footer.py reference.docx --header 'Title\tv2.3'
python3 verify_roundtrip.py reference.docx styles.json --structure-only
```

## Known limits

- The PDF stores embedded subset names. The system name is restored, but the
  font still has to be installed locally or Word substitutes one.
- Pandoc only writes the style names in the table above. A new name such as
  "Company Heading" is never referenced.
- Code blocks use `Source Code`, which pandoc generates on output. Customising
  it means creating a paragraph style with that exact name.
- A layout that does not match the original is almost always the heading level
  mapping. Levels are the one thing a PDF does not record.
- A PDF stores its running head as ordinary text, so nothing was carried over
  automatically. Whatever the page section lists was added deliberately.

Built from `{src}` by the pdf-reverse-template skill on {date}.
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
            if b"PAGE" in raw:
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
        page.append(f"- Recurring content in the source PDF (header/footer/page number): "
                    f"{' / '.join(d['running_heads'])}\n"
                    f"  This was **not** carried into the template — in a PDF it is "
                    f"ordinary text. Add one with `set_header_footer.py` or in Word.")

    rev = []
    if mapping:
        rev.append("**Heading level mapping** (`--map " +
                   ",".join(f"{k}={v}" for k, v in mapping.items()) + "`):\n")
        rev.append("| Cluster in the analysis | Sample text | Assigned to |")
        rev.append("|---|---|---|")
        for h in d["headings"]:
            tgt = mapping.get(str(h["level"]), f"Heading{h['level']}")
            rev.append(f"| #{h['level']} - {h['size']}pt - #{h['color']} "
                       f"| {h.get('sample', '')[:20]} | `{tgt}` |")
    else:
        rev.append("**Heading levels**: no `--map` was given, so groups were assigned "
                   "Heading1/2/3... by size.\n")
        rev.append("> If the source PDF has a separate document title it took Heading1 "
                   "and shifted every level by one. Check the sample text for each "
                   "group in `report.txt`.")
    rev.append("")
    rev.append(f"**Columns**: {d.get('columns', 1)}"
               + (f", gap {d.get('column_gap_pt')}pt" if (d.get("columns") or 1) > 1 else "")
               + ". A PDF does not record whether a layout is multi-column; this was "
                 "declared by looking at a rendered page.")

    cands = d.get("body_candidates") or []
    chosen = next((c for c in cands if c.get("chosen")), None)
    if chosen and len(cands) > 1:
        rev.append("")
        rev.append(f"**Body group**: rank {chosen['rank']} "
                   f"({chosen['font']} {chosen['size']}pt #{chosen['color']}, "
                   f"{chosen['chars']} characters)"
                   + (f", chosen explicitly with --body {d['body_pick']}"
                      if d.get("body_pick")
                      else ". It was the largest group, accepted as the default."))
        rev.append("")
        rev.append("| Rank | Font | Size | Chars | Lines | Sample |")
        rev.append("|---|---|---|---|---|---|")
        for c in cands:
            mark = " **<- chosen**" if c["chosen"] else ""
            rev.append(f"| {c['rank']} | {c['font']} | {c['size']}pt | {c['chars']} "
                       f"| {c.get('lines', '-')} | {c['sample'][:28]}{mark} |")
    rev.append("")
    if bottom is not None:
        rev.append(f"**Bottom margin**: overridden to {bottom} cm.")
    else:
        mb = d["margins_measured_cm"].get("bottom")
        sug = mg.get("bottom")
        rev.append(f"**Bottom margin**: {sug} cm, taken from the analyzer's suggestion"
                   + (f" (it mirrors the top margin of {mg['top']} cm, which fits under "
                      f"the measured upper bound of <={mb} cm)"
                      if sug == mg.get("top") and mb else
                      f" (the top margin of {mg['top']} cm exceeds the measured upper "
                      f"bound of <={mb} cm, so this layout is not vertically symmetric "
                      f"and the bound was rounded instead)" if mb else "")
                   + ".")

    # The flags that were chosen rather than measured, so the analysis can be
    # reproduced from source.pdf alone. The column count comes out of styles.json
    # rather than from a flag, where it cannot drift from the template.
    ncols = d.get("columns") or 1
    repro = (f" --body {body}" if body else "") + (f" --columns {ncols}" if ncols > 1 else "")
    # Every margin overridden on the command line. These are measurements the
    # analyzer got wrong and somebody corrected; if SKILL.md does not carry
    # them, the correction is lost the moment the template is rebuilt.
    if margins:
        rev.append("")
        rev.append("**Margins set by hand**: "
                   + ", ".join(f"`--{k} {v}`" for k, v in sorted(margins.items()))
                   + ". The rest came from the analysis.")

    # The outline is the only record of the source's *content* that survives.
    # reference.docx carries no body text, so without it there is nothing to
    # work from when the task is "another document like this one".
    ol_lines = []
    for o in d.get("outline") or []:
        n = mapping.get(str(o["level"]), f"Heading{o['level']}")
        lv = re.fullmatch(r"Heading(\d)", n)
        depth = max(0, int(lv.group(1)) - 1) if lv else 0
        ol_lines.append(f"{'  ' * depth}- {o['text']}  `{n}`  (p{o['page']})")
    ol_md = "\n".join(ol_lines) or "_No headings were detected in the source._"

    # The description is what makes an agent reach for this package at all, so
    # it names the look rather than describing the file.
    look = st.get("heading 1") or st.get("title") or st.get("body text") or {}
    marks = ", ".join(v for v in (look.get("font"),
                                  f"#{look['color']}" if look.get("color") else "") if v)
    desc = (f"Produce Word documents in the {name} house style"
            + (f" ({marks})" if marks else "")
            + f". Use when asked to write, format, re-issue or restyle a document "
              f"in this style, or to produce another document like {src}.")

    open(os.path.join(outdir, "SKILL.md"), "w").write(SKILL.format(
        name=name, desc=desc, src=src, md_map=md, styles=rows,
        page="\n".join(page), review="\n".join(rev), repro=repro,
        outline=ol_md, date=datetime.date.today().isoformat()))

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
