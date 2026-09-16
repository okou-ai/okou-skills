#!/usr/bin/env python3
"""Accept the reference.docx produced from a PDF.

Usage:  python3 verify_roundtrip.py reference.docx styles.json [--map 1=Heading1,2=Title]
        python3 verify_roundtrip.py reference.docx styles.json --structure-only

--structure-only drops the value reconciliation and keeps the dangling-reference
check. Use it after deliberately editing a style with set_style.py: the
reconciliation asks "did the builder write what was measured", which stops being
a meaningful question once a human has overridden a value on purpose.

Pass the same --map that build_reference.py was given. Without it the cluster to
style match is guessed from size and colour, which reports a false failure when
two clusters resolve to one style.

Two checks:
  1. Convert a probe document and look for dangling style references. A missing
     style raises no error: Pandoc still writes the pStyle but adds no
     definition, and Word quietly renders the text as Normal.
  2. Reconcile the font size, colour, spacing, indent and alignment actually
     present in the output against the values inferred from the PDF.

Exit code 0 means it passed.
"""
import sys, os, re, json, zipfile, subprocess, tempfile

PROBE = """---
title: Probe
---

# Heading one

First body paragraph.

Second body paragraph with `code`, **bold** and a [link](https://example.com).

## Heading two

- List item
> Block quote

```python
print(1)
```

| A | B |
|---|---|
| 1 | 2 |

### Heading three
"""

HALF2PT = lambda h: round(int(h) / 2, 1)
TWIP2PT = lambda t: round(int(t) / 20, 1)


def ids(z, part):
    try:
        x = z.read(part).decode("utf-8", "replace")
    except KeyError:
        return set()
    return (set(re.findall(r"<w:pStyle\s+w:val=\"([^\"]+)\"", x))
            | set(re.findall(r"<w:rStyle\s+w:val=\"([^\"]+)\"", x))
            | set(re.findall(r"<w:tblStyle\s+w:val=\"([^\"]+)\"", x)))


def style_props(xml, sid):
    m = re.search(rf'<w:style\b[^>]*?w:styleId="{sid}"[^>]*>(.*?)</w:style>', xml, re.S)
    if not m:
        return None
    inner = m.group(1)
    out = {}
    rpr = re.search(r"<w:rPr>.*?</w:rPr>", inner, re.S)
    if rpr:
        r = rpr.group(0)
        f = re.search(r'w:ascii="([^"]*)"', r)
        s = re.search(r'<w:sz w:val="(\d+)"', r)
        c = re.search(r'<w:color w:val="([0-9A-Fa-f]{6})"', r)
        out.update(font=f.group(1) if f else None,
                   size=HALF2PT(s.group(1)) if s else None,
                   color=c.group(1).upper() if c else None)
    ppr = re.search(r"<w:pPr>.*?</w:pPr>", inner, re.S)
    if ppr:
        p = ppr.group(0)
        # More than one means the merge was wrong; the later element wins.
        out["dup_spacing"] = p.count("<w:spacing") > 1
        for attr, name in (("before", "space_before_pt"), ("after", "space_after_pt"),
                           ("line", "line_advance_pt")):
            mm = re.search(rf'<w:spacing[^>]*w:{attr}="(\d+)"', p)
            out[name] = TWIP2PT(mm.group(1)) if mm else None
        mm = re.search(r'<w:ind[^>]*w:firstLine="(\d+)"', p)
        out["first_line_indent_pt"] = TWIP2PT(mm.group(1)) if mm else None
        mm = re.search(r'<w:jc w:val="([a-z]+)"', p)
        out["align"] = "center" if (mm and mm.group(1) == "center") else "left"
    return out


def main(ref, jpath, mapping=None, structure_only=False):
    mapping = mapping or {}
    d = json.load(open(jpath))
    tmp = tempfile.mkdtemp()
    md, out = os.path.join(tmp, "p.md"), os.path.join(tmp, "p.docx")
    open(md, "w").write(PROBE)
    r = subprocess.run(["pandoc", md, f"--reference-doc={ref}", "-o", out],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print("FAIL  pandoc conversion failed:\n" + r.stderr)
        return 1

    with zipfile.ZipFile(out) as z:
        sxml = z.read("word/styles.xml").decode("utf-8", "replace")
        defined = set(re.findall(r'<w:style\b[^>]*?w:styleId="([^"]+)"', sxml))
        used = ids(z, "word/document.xml") | ids(z, "word/footnotes.xml")
    dangling = sorted(used - defined)

    print(f"===== verifying {os.path.basename(ref)} =====\n")
    print(f"[style references] {len(used)} used, {len(defined)} defined")
    print("  OK  no dangling references" if not dangling
          else f"  FAIL  {len(dangling)} dangling: {', '.join(dangling)}")

    if structure_only:
        print("\n[reconciliation] skipped (--structure-only)")
        print(f"\nResult: " + ("PASS" if not dangling else "FAIL"))
        return 0 if not dangling else 1

    print(f"\n[reconciliation] output docx vs values inferred from the PDF")
    print(f"{'style':<14}{'field':<10}{'from PDF':<24}{'in docx':<24}")
    bad = 0
    targets = [("BodyText", d["body"])]
    with zipfile.ZipFile(ref) as rz:
        rxml = rz.read("word/styles.xml").decode("utf-8", "replace")
    for h in d["headings"]:
        if mapping:
            sid = mapping.get(str(h["level"]), f"Heading{h['level']}")
            if sid.lower() in ("skip", "none", "-"):
                continue            # deliberately dropped, nothing was written
            targets.append((sid, h))
            continue
        for sid in ("Title", f"Heading{h['level']}", "Heading1", "Heading2", "Heading3"):
            p = style_props(rxml, sid)
            if p and p.get("size") == h["size"] and (p.get("color") or "").upper() == h["color"]:
                targets.append((sid, h))
                break
    for sid, want in targets:
        got = style_props(sxml, sid)
        if got is None:
            print(f"{sid:<14}{'-':<10}{'':<24}FAIL  style absent from the output")
            bad += 1
            continue
        if got.get("dup_spacing"):
            print(f"{sid:<14}{'structure':<10}"
                  f"{'multiple w:spacing in w:pPr; the later one wins':<48}FAIL")
            bad += 1
        checks = [("size", "size"), ("color", "colour"),
                  ("space_before_pt", "before"), ("space_after_pt", "after"),
                  ("line_advance_pt", "line"), ("first_line_indent_pt", "indent"),
                  ("align", "align")]
        for k, label in checks:
            if k not in want or want[k] is None:
                continue        # None means it was never measured, not zero
            w, g = want[k], got.get(k)
            norm = lambda v: None if v in (0, 0.0, None, "") else v
            ok = str(norm(w)).upper() == str(norm(g)).upper()
            if not ok:
                bad += 1
            print(f"{sid:<14}{label:<10}{str(w):<24}{str(g):<24}{'' if ok else 'FAIL'}")

    with zipfile.ZipFile(out) as z:
        doc = z.read("word/document.xml").decode("utf-8", "replace")
    mar = dict(re.findall(r'w:(top|right|bottom|left)="(-?\d+)"', doc))
    cm = lambda t: round(int(t) / 1440 * 2.54, 2)
    if mar:
        print(f"\n[page] margins " + "  ".join(f"{k} {cm(v)}cm" for k, v in mar.items()))
    print(f"       paper {'pgSz present' if 'pgSz' in doc else 'pgSz MISSING'}")

    ok = not dangling and bad == 0
    print(f"\nResult: " + ("PASS" if ok else
                           f"FAIL — {len(dangling)} dangling, {bad} mismatches"))
    print("\nNote: whether a font name actually renders depends on it being installed "
          "on the\n      target machine. The script restores the system name from the "
          "embedded subset\n      name, but confirm it once in Word.")
    return 0 if ok else 1


if __name__ == "__main__":
    a = sys.argv
    if len(a) < 3:
        print(__doc__); sys.exit(2)
    mapping = {}
    if "--map" in a:
        for kv in a[a.index("--map") + 1].split(","):
            k, v = kv.split("=")
            mapping[k.strip()] = v.strip()
    sys.exit(main(a[1], a[2], mapping, "--structure-only" in a))
