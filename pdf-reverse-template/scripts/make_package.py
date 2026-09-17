#!/usr/bin/env python3
"""Assemble the deliverable: template, source PDF, report and usage notes.

Usage:
  python3 make_package.py <source.pdf> <reference.docx> <styles.json> <output dir> \
          [--map 1=Heading1,2=Title] [--bottom 3.0] [--body 2]

Pass --map, --bottom and --body through verbatim. They are recorded in the
"Human decisions" section of the README, and --body is also replayed when the
report is regenerated — otherwise report.txt would re-analyse with the default
cluster and contradict the template it ships beside.
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


README = """# {name} document template

A Word template reverse-engineered from a PDF. Use it to convert Markdown into
documents that match the original layout.

## 1. Quick start

```bash
# Install pandoc
brew install pandoc                                  # macOS
sudo apt install pandoc                              # Debian / Ubuntu
winget install --id JohnMacFarlane.Pandoc            # Windows

# Convert
pandoc your-document.md --reference-doc=reference.docx -o output.docx
```

For a PDF, open the resulting .docx in Word and export from there.

No administrator rights? Pandoc ships a portable build. Download the archive
matching **your OS and CPU architecture** from
<https://github.com/jgm/pandoc/releases> (Apple Silicon: `arm64-macOS.zip`,
Intel Mac: `x86_64-macOS.zip`, Windows: `windows-x86_64.zip`, Linux:
`linux-amd64` or `linux-arm64.tar.gz`), unpack it, and add its `bin` directory
to PATH.

## 2. Writing Markdown that picks up these styles

| Markdown construct | Style it maps to |
|---|---|
{md_map}

Put the document title in the YAML header:

```markdown
---
title: Document title
author: Author
---

# Chapter one

Body text.
```

## 3. What this template contains

### Fonts and spacing (pt)

| Style | Font / size / colour | Spacing | First-line indent | Alignment |
|---|---|---|---|---|
{styles}

### Page

{page}

## 4. Human decisions

A PDF has no style layer, so this template was **measured and inferred**. Two
choices were made by hand when it was built; start here if any value looks off:

{review}

Confidence by field:

| Field | Source | Confidence |
|---|---|---|
| Font / size / colour | Recorded exactly in the PDF | High |
| Spacing / line height / indent / alignment | Computed from coordinates | High |
| Heading levels | Assigned by hand (above) | Depends on the review |
| Top / left / right margins | Measured, then rounded | Medium |
| Bottom margin | Only bounded, never measured | Low |

## 5. FAQ

**The fonts look wrong.**
The PDF stores embedded subset names; the script restores the system name, but
the font still has to be installed locally. Install it — the template does not
need changing.

**How do I adjust a style?**
Open `reference.docx` in Word and use **right-click the style in the Styles
pane -> Modify**. Editing the **style definition** is what matters; selecting
text and changing its font is direct formatting and does not affect the
template.

Without Word, or for bulk edits, use `set_style.py` from the skill that
generated this package:
`python3 set_style.py reference.docx "heading 2" --size 14 --color 1B4F72 --before 12`

**I created my own style and nothing happens.**
Pandoc only uses a fixed set of style names — the ones in the table above.
Modify the existing ones.

**I cannot change how code blocks look.**
`Source Code` is generated by Pandoc on output. Create a paragraph style with
that exact name — in Word via **Styles -> New Style**, or with the script:
`python3 set_style.py reference.docx "Source Code" --create --font "Consolas" --size 9`

**The layout does not match the original PDF.**
Check the heading level mapping in section 4 first. Levels are the one thing a
PDF does not record.

**I need a header or footer.**
Section 3 lists what this template carries. A PDF stores its running content as
ordinary text, so nothing is carried over automatically — whatever is listed was
added deliberately when the template was built. Add or change one in Word, or
with `set_header_footer.py` from the skill; either way it flows into every
output document.

## 6. Package contents

| File | Purpose |
|---|---|
| `reference.docx` | **The template.** Point `--reference-doc` at this |
| `{orig}` | The source PDF. Keep it for comparison |
| `styles.json` | The raw inferred values, useful when editing the template |
| `report.txt` | Analysis and verification output from when this was built |
| `README.md` | This file |

---
Generated by the pdf-reverse-template skill on {date}
"""


def build(pdf, ref, jpath, outdir, mapping, bottom, body=None):
    os.makedirs(outdir, exist_ok=True)
    shutil.copy(ref, os.path.join(outdir, "reference.docx"))
    shutil.copy(pdf, os.path.join(outdir, os.path.basename(pdf)))
    shutil.copy(jpath, os.path.join(outdir, "styles.json"))

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
        rev.append("**Heading levels**: no `--map` was given, so clusters were assigned "
                   "Heading1/2/3... by size.\n")
        rev.append("> If the source PDF has a separate document title it took Heading1 "
                   "and shifted every level by one. Check the sample text for each "
                   "cluster in `report.txt`.")
    rev.append("")
    rev.append(f"**Columns**: {d.get('columns', 1)}"
               + (f", gap {d.get('column_gap_pt')}pt" if (d.get("columns") or 1) > 1 else "")
               + ". A PDF does not record whether a layout is multi-column; this was "
                 "declared by looking at a rendered page.")

    cands = d.get("body_candidates") or []
    chosen = next((c for c in cands if c.get("chosen")), None)
    if chosen and len(cands) > 1:
        rev.append("")
        rev.append(f"**Body cluster**: rank {chosen['rank']} "
                   f"({chosen['font']} {chosen['size']}pt #{chosen['color']}, "
                   f"{chosen['chars']} characters)"
                   + (f", chosen explicitly with --body {d['body_pick']}"
                      if d.get("body_pick")
                      else ". It was the largest cluster, accepted as the default."))
        rev.append("")
        rev.append("| Rank | Font | Size | Chars | Lines | Sample |")
        rev.append("|---|---|---|---|---|---|")
        for c in cands:
            mark = " **<- chosen**" if c["chosen"] else ""
            rev.append(f"| {c['rank']} | {c['font']} | {c['size']}pt | {c['chars']} "
                       f"| {c.get('lines', '-')} | {c['sample'][:28]}{mark} |")
    rev.append("")
    if bottom is not None:
        rev.append(f"**Bottom margin**: set by hand to {bottom} cm.")
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

    here = os.path.dirname(os.path.abspath(__file__))
    rep = []
    map_args = ["--map", ",".join(f"{k}={v}" for k, v in mapping.items())] if mapping else []
    body_args = ["--body", str(body)] if body else []
    # The column count is read back out of styles.json rather than taken as a
    # flag. Re-running the analysis without it regenerates report.txt as a
    # single-column document, which then contradicts the template beside it.
    ncols = d.get("columns") or 1
    col_args = ["--columns", str(ncols)] if ncols > 1 else []
    for script, args in (("analyze_pdf.py", [pdf] + body_args + col_args),
                         ("verify_roundtrip.py", [ref, jpath] + map_args)):
        r = subprocess.run([sys.executable, os.path.join(here, script)] + args,
                           capture_output=True, text=True)
        rep.append(f"$ python3 {script} ...\n(exit={r.returncode})\n{r.stdout}")
    open(os.path.join(outdir, "report.txt"), "w").write("\n\n".join(rep))

    open(os.path.join(outdir, "README.md"), "w").write(README.format(
        name=os.path.splitext(os.path.basename(pdf))[0],
        md_map=md, styles=rows, page="\n".join(page),
        review="\n".join(rev), orig=os.path.basename(pdf),
        date=datetime.date.today().isoformat()))

    print(f"Package written to {outdir}/")
    for f in sorted(os.listdir(outdir)):
        print(f"  {f}")
    print("\nHand over the whole directory; README.md explains how to use it.")


if __name__ == "__main__":
    a = sys.argv
    if len(a) < 5:
        print(__doc__); sys.exit(2)
    mapping, bottom = {}, None
    if "--map" in a:
        for kv in a[a.index("--map") + 1].split(","):
            k, v = kv.split("=")
            mapping[k.strip()] = v.strip()
    if "--bottom" in a:
        bottom = float(a[a.index("--bottom") + 1])
    body = int(a[a.index("--body") + 1]) if "--body" in a else None
    build(a[1], a[2], a[3], a[4], mapping, bottom, body)
