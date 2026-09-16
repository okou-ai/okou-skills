#!/usr/bin/env python3
"""Assemble the deliverable: template, source, report and usage notes in one directory.

Usage:  python3 make_package.py <source.docx> <reference.docx> <output dir>

The style values in README.md are read out of reference.docx, not hardcoded.
"""
import sys, os, re, shutil, zipfile, subprocess, datetime

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
            t = " ".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>",
                                    z.read(part).decode("utf-8", "replace"))).strip()
            kind = "Header" if "header" in part else "Footer"
            img = " (contains an image)" if b"<w:drawing" in z.read(part) else ""
            hf.append(f"{kind}: {t or '(no text)'}{img}")
    s = re.search(r"<w:sectPr\b.*?</w:sectPr>", d, re.S)
    s = s.group(0) if s else ""
    pg = re.search(r'<w:pgSz[^>]*w:w="(\d+)"[^>]*w:h="(\d+)"', s) or \
         re.search(r'<w:pgSz[^>]*w:h="(\d+)"[^>]*w:w="(\d+)"', s)
    mar = dict(re.findall(r'w:(top|right|bottom|left)="(-?\d+)"', s))
    return {"size": (TWIP2CM(pg.group(1)), TWIP2CM(pg.group(2))) if pg else None,
            "margin": {k: TWIP2CM(v) for k, v in mar.items()} or None,
            "hf": hf}


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

Convert Markdown into Word documents that match this template's layout.

## 1. Quick start

```bash
# Install pandoc
brew install pandoc                                  # macOS
sudo apt install pandoc                              # Debian / Ubuntu
winget install --id JohnMacFarlane.Pandoc            # Windows

# Convert
pandoc your-document.md --reference-doc=reference.docx -o output.docx
```

That single command applies the whole template to the output.

No administrator rights? Pandoc ships a portable build. Download the archive
matching **your OS and CPU architecture** from
<https://github.com/jgm/pandoc/releases> (Apple Silicon: `arm64-macOS.zip`,
Intel Mac: `x86_64-macOS.zip`, Windows: `windows-x86_64.zip`, Linux:
`linux-amd64` or `linux-arm64.tar.gz`), unpack it, and add its `bin` directory
to PATH. It is a single static binary with no runtime dependencies.

## 2. Writing Markdown that picks up these styles

| Markdown construct | Style it maps to |
|---|---|
{md_map}

Standard Markdown syntax is all that is needed. Put the document title in the
YAML header:

```markdown
---
title: Document title
author: Author
date: 2026-01-01
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

## 4. FAQ

**The fonts look wrong.**
A font named in the template only renders if it is installed locally; otherwise
Word substitutes one. Install the font — the template does not need changing.

**How do I adjust a style?**
Open `reference.docx` in Word and use **right-click the style in the Styles
pane -> Modify**. Editing the **style definition** is what matters; selecting
text and changing its font is direct formatting and does not affect the
template. Save when done.

Without Word, or for bulk edits, use `set_style.py` from the skill that
generated this package:
`python3 set_style.py reference.docx "heading 2" --size 14 --color 1B4F72 --before 12`

**I created my own style and nothing happens.**
Pandoc only uses a fixed set of style names — the ones in the table above.
A new name like "Company Heading" is never referenced. Modify the existing ones.

**I cannot change how code blocks look.**
Code blocks use `Source Code`, which Pandoc generates on output. To customise
it, create a paragraph style with that exact name — in Word via
**Styles -> New Style**, or with the script:
`python3 set_style.py reference.docx "Source Code" --create --font "Consolas" --size 9`

**Headings come out looking like body text.**
The template is missing that style. Run `verify_reference.py` from the skill to
find out which one.

**I need a header, footer, or different margins.**
Edit them directly in `reference.docx` with Word and save; all of it carries
into every output document. Or use `set_header_footer.py` from the skill.

## 5. Package contents

| File | Purpose |
|---|---|
| `reference.docx` | **The template.** Point `--reference-doc` at this |
| `{orig}` | The source document. Keep it for comparison |
| `report.txt` | Inspection and verification output from when this was built |
| `README.md` | This file |

---
Generated by the docx-reverse-template skill on {date}
"""


def build(orig, ref, outdir):
    os.makedirs(outdir, exist_ok=True)
    shutil.copy(ref, os.path.join(outdir, "reference.docx"))
    shutil.copy(orig, os.path.join(outdir, os.path.basename(orig)))

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
    page_lines += [f"- {h}" for h in pg["hf"]] or ["- No header or footer"]

    here = os.path.dirname(os.path.abspath(__file__))
    rep = []
    for script, arg in (("inspect_docx.py", orig), ("verify_reference.py", ref)):
        r = subprocess.run([sys.executable, os.path.join(here, script), arg],
                           capture_output=True, text=True)
        rep.append(f"$ python3 {script} {os.path.basename(arg)}\n"
                   f"(exit={r.returncode})\n{r.stdout}")
    open(os.path.join(outdir, "report.txt"), "w").write("\n\n".join(rep))

    open(os.path.join(outdir, "README.md"), "w").write(README.format(
        name=os.path.splitext(os.path.basename(orig))[0],
        md_map=md, styles=rows, page="\n".join(page_lines),
        orig=os.path.basename(orig),
        date=datetime.date.today().isoformat()))

    print(f"Package written to {outdir}/")
    for f in sorted(os.listdir(outdir)):
        print(f"  {f}")
    print("\nHand over the whole directory; README.md explains how to use it.")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(2)
    build(sys.argv[1], sys.argv[2], sys.argv[3])
