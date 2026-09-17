#!/usr/bin/env python3
"""Accept a reference.docx by converting a probe document and catching silent failures.

Usage:  python3 verify_reference.py reference.docx [probe_out.docx]

The failure this catches: when a style is missing, Pandoc still writes
<w:pStyle w:val="Heading1"> but adds no definition. The document opens fine and
the heading quietly renders as Normal, which is easy to miss by eye.

Exit code 0 means it passed; 1 means dangling style references, a lost
header/footer, or a missing paper size.
"""
import shutil
import sys, os, re, zipfile, subprocess, tempfile

PROBE = """---
title: Probe document
subtitle: Subtitle
author: Verification
date: 2026-01-01
abstract: Abstract paragraph.
---

# Heading one

First body paragraph, followed by a second so First Paragraph and Body Text
can be told apart.

Second body paragraph with `inline code`, **bold**, a [link](https://example.com)
and a footnote[^1].

## Heading two

- List item one
- List item two

1. Ordered one
2. Ordered two

> Block quote, styled as Block Text.

```python
print("Source Code")
```

| Column A | Column B |
|----------|----------|
| 1        | 2        |

: Table caption

Term
:   Definition body

### Heading three

#### Heading four

##### Heading five

###### Heading six

####### Heading seven

######## Heading eight

######### Heading nine

[^1]: Footnote body.
"""


def defined_styles(z):
    x = z.read("word/styles.xml").decode("utf-8", "replace")
    return set(re.findall(r"<w:style\b[^>]*?w:styleId=\"([^\"]+)\"", x))


def used_styles(z):
    used = set()
    parts = ["word/document.xml", "word/footnotes.xml", "word/endnotes.xml"]
    parts += [n for n in z.namelist() if re.match(r"word/(header|footer)\d+\.xml", n)]
    for part in parts:
        try:
            x = z.read(part).decode("utf-8", "replace")
        except KeyError:
            continue
        used |= set(re.findall(r"<w:pStyle\s+w:val=\"([^\"]+)\"", x))
        used |= set(re.findall(r"<w:rStyle\s+w:val=\"([^\"]+)\"", x))
        used |= set(re.findall(r"<w:tblStyle\s+w:val=\"([^\"]+)\"", x))
    return used


def main(ref, keep=None):
    tmp = tempfile.mkdtemp()
    md = os.path.join(tmp, "probe.md")
    out = keep or os.path.join(tmp, "probe.docx")
    open(md, "w").write(PROBE)

    if not shutil.which("pandoc"):

        sys.exit("pandoc is not on PATH. Run: python3 ensure_pandoc.py")

    r = subprocess.run(["pandoc", md, f"--reference-doc={ref}", "-o", out],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL  pandoc conversion failed:\n" + r.stderr)
        return 1

    z = zipfile.ZipFile(out)
    defined, used = defined_styles(z), used_styles(z)
    dangling = sorted(used - defined)

    print(f"===== verifying {os.path.basename(ref)} =====\n")
    # Count what the template defines, not what the converted probe ended up
    # with: pandoc adds its code-highlight styles whenever the probe contains a
    # fenced block, so the output number moves with the probe, not the template.
    with zipfile.ZipFile(ref) as zt:
        tmpl_defined = defined_styles(zt)
    print(f"[style references] probe uses {len(used)} styles; "
          f"template defines {len(tmpl_defined)}")
    if dangling:
        print(f"  FAIL  {len(dangling)} dangling references (Word renders these as Normal):")
        for d in dangling:
            print(f"     {d}")
    else:
        print("  OK  no dangling references")

    names = z.namelist()
    hdr = [n for n in names if re.match(r"word/header\d+\.xml", n)]
    ftr = [n for n in names if re.match(r"word/footer\d+\.xml", n)]
    doc = z.read("word/document.xml").decode("utf-8", "replace")
    sect = re.search(r"<w:sectPr\b.*?</w:sectPr>", doc, re.S)
    s = sect.group(0) if sect else ""

    print(f"\n[header/footer] output has {len(hdr)} header(s) / {len(ftr)} footer(s); "
          f"sectPr references: header {'yes' if 'headerReference' in s else 'no'}, "
          f"footer {'yes' if 'footerReference' in s else 'no'}")
    no_paper = "pgSz" not in s
    print(f"[page setup] pgSz {'yes' if not no_paper else 'MISSING'}, "
          f"pgMar {'yes' if 'pgMar' in s else 'MISSING'}")
    if no_paper:
        # Without a paper size Word falls back to the reader's locale default:
        # A4 in most of the world, Letter in the US. The text block then changes
        # width and height, so line breaks, page breaks and the total page count
        # differ per machine from the same Markdown.
        print("  FAIL  no paper size, so output depends on the reader's locale default")
        print("        (A4 vs Letter changes the text block and therefore the page count)")
        print(f"        set_header_footer.py {os.path.basename(ref)} --paper A4")

    rz = zipfile.ZipFile(ref)
    ref_hf = [n for n in rz.namelist() if re.match(r"word/(header|footer)\d+\.xml", n)]
    lost = bool(ref_hf) and not (hdr or ftr)
    rz.close(); z.close()
    if lost:
        print("  FAIL  the template has a header/footer but the output does not")

    if keep:
        print(f"\nProbe output kept at: {out}")
    print()
    ok = not dangling and not lost and not no_paper
    print("Result: " + ("PASS — ready to ship" if ok else "FAIL — see the markers above"))
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3) or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else None))
