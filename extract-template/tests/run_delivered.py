#!/usr/bin/env python3
"""Run a delivered package's instructions verbatim, render, and measure.
   python3 run_delivered.py <pkg> [--balance]"""
import re, subprocess, zipfile, pathlib, sys, pymupdf
pkg = sys.argv[1].rstrip("/"); balance = "--balance" in sys.argv
import os; os.chdir(os.path.dirname(os.path.abspath(pkg)) or "."); pkg = os.path.basename(pkg)
sk = pathlib.Path(f"{pkg}/SKILL.md").read_text()
cmd = re.search(r'```bash\n(pandoc [^\n]+)', sk).group(1)
m = re.search(r'````markdown\n(.*?)\n````', sk, re.S)
LONG = "# A heading long enough to run well past the width of a single column on this page"
BODY = " ".join(["Body text in columns, long enough to wrap several times so the columns are visible."] * 5)
TABLE = ("\n\n+------------------+------------------+------------------+------------------+\n"
         "| Metric           | Definition       | Source           | Note             |\n"
         "+==================+==================+==================+==================+\n"
         "| Pass rate        | No manual fix    | Run log          | Weekly           |\n"
         "+------------------+------------------+------------------+------------------+\n")
if m:
    md = m.group(1).replace("# Heading across all columns", LONG)
    md = md.replace("Body text, in columns.", BODY, 1).replace("Body text, in columns.", BODY + TABLE + "\n\n" + BODY)
    if balance and not re.search(r'w:num="[2-9]"[^`]*```\s*$', md.rstrip() + "```"):
        blocks = re.findall(r'(```\{=openxml\}\n.*?\n```)', md, re.S)
        first_brk = next(b for b in blocks if re.search(r'w:num="[2-9]"', b))
        md += "\n\n" + first_brk
else:
    md = "---\ntitle: T\n---\n\n" + BODY + TABLE
tag = pkg + ("_bal" if balance else "")
pathlib.Path(f"{tag}.md").write_text(md)
subprocess.run(cmd.replace("doc.md", f"{tag}.md").replace("reference.docx", f"{pkg}/reference.docx").replace("out.docx", f"{tag}.docx"), shell=True, check=True)
subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", ".", f"{tag}.docx"], capture_output=True, timeout=180)
doc = pymupdf.open(f"{tag}.pdf"); p0 = doc[0]; W = p0.rect.width
tdoc = zipfile.ZipFile(f"{pkg}/reference.docx").read("word/document.xml").decode()
has_hf = 'headerReference w:type="default"' in tdoc and "<w:titlePg" not in tdoc
pg = re.search(r"<w:pgSz\b[^>]*/>", tdoc).group(0); PW = int(re.search(r'w:w="(\d+)"', pg).group(1)) / 20
mar = dict(re.findall(r'w:(left|right)="(\d+)"', re.search(r"<w:pgMar[^>]*/>", tdoc).group(0)))
L, R = int(mar["left"]) / 20, W - int(mar["right"]) / 20
cols = re.search(r"<w:cols\b[^>]*/>|<w:cols\b[^>]*>.*?</w:cols>", tdoc, re.S)
cols = cols.group(0) if cols else ""
ncol = int((re.search(r'w:num="(\d+)"', cols) or re.search(r"(1)", "1")).group(1))
widths = [int(x) / 20 for x in re.findall(r'<w:col\b[^>]*w:w="(\d+)"', cols)]
space = int((re.search(r'w:space="(\d+)"', cols) or re.search(r"(0)", "0")).group(1)) / 20
c1r = (L + widths[0]) if widths else (L + ((R - L) - space * (ncol - 1)) / ncol)
c2l = c1r + space
lines = []
for pg in doc:
    for b in pg.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            t = "".join(s["text"] for s in l["spans"]).strip()
            if t: lines.append(dict(page=pg.number, x0=l["bbox"][0], x1=l["bbox"][2], y=l["bbox"][1], t=t))
H = p0.rect.height
p1 = [l for l in lines if l["page"] == 0 and 60 < l["y"] < H - 70]     # drop header/footer bands
head = next((l for l in p1 if l["t"].startswith("A heading long enough")), None)
hy_end = head["y"] + 2 if head else 0
if head:  # a wrapped heading continues on the next line(s); skip those too
    for l in sorted(p1, key=lambda l: l["y"]):
        if l["y"] > hy_end and l["y"] < hy_end + 24 and l["x0"] < L + 6 and l["x1"] < L + 200 and not l["t"].startswith("Body"):
            hy_end = l["y"] + 2
after = [l for l in p1 if head and l["y"] > hy_end]
# derive the rendered column geometry from the lines themselves, not the twips:
# renderers stretch columns that do not fill the text width differently.
if ncol > 1:
    mid = (L + R) / 2
    xs = sorted(set(round(l["x0"]) for l in after if l["x1"] - l["x0"] > 120))
    clusters = []
    for x in xs:
        if clusters and x - clusters[-1][-1] < 60:
            clusters[-1].append(x)
        else:
            clusters.append([x])
    c2l = clusters[1][0] if len(clusters) > 1 else R
    c1r = max((l["x1"] for l in after if l["x0"] < mid and l["x1"] < c2l - 4), default=(L + R) / 2)
col2 = [l for l in after if abs(l["x0"] - c2l) < 6]
tb = [l for l in p1 if l["t"] in ("Metric", "Weekly", "Note", "Pass rate")]
ty0, ty1 = (min(l["y"] for l in tb) - 2, max(l["y"] for l in tb) + 14) if tb else (0, 0)
side = (tb[0]["x0"] < c2l - 4) if (tb and ncol > 1) else True
trows = [l for l in p1 if ty0 <= l["y"] <= ty1 and (ncol == 1 or (l["x0"] < c2l - 4) == side)]
tx0, tx1 = (min(l["x0"] for l in trows), max(l["x1"] for l in trows)) if trows else (0, 0)
tedge = c1r if (ncol > 1 and side) else R
hdr = [l for l in lines if l["page"] == 0 and l["y"] < 60]
checks = {
  "paper matches template": abs(W - PW) < 1,
  "header on page 1": bool(hdr) if has_hf else True,
  "heading spans (x1 past column 1)": bool(head) and head["x1"] > c1r + 5 if ncol > 1 else True,
  "no full-width line after heading": all(l["x1"] <= c1r + 8 or l["x0"] >= c2l - 8 for l in after) if ncol > 1 else True,
  "column 2 used after heading": bool(col2) if ncol > 1 else True,
  "table inside its column": bool(trows) and tx1 <= tedge + 4,
}
last = doc[doc.page_count - 1]
if ncol > 1:
    lp = [l for l in lines if l["page"] == doc.page_count - 1 and 60 < l["y"] < H - 70]
    lc1 = [l for l in lp if l["x0"] < c2l - 4]; lc2 = [l for l in lp if abs(l["x0"] - c2l) < 6]
    y1 = max((l["y"] for l in lc1), default=0); y2 = max((l["y"] for l in lc2), default=0)
    checks["last page columns balanced (bottoms within 50pt)"] = abs(y1 - y2) < 50
print(f"===== {tag}: {cmd}   pages={doc.page_count}")
for k, v in checks.items(): print(f"  {'PASS' if v else 'FAIL'}  {k}")
if head: print(f"        heading x1={head['x1']:.1f} vs col1 edge {c1r:.1f};  table x={tx0:.1f}..{tx1:.1f} vs edge {tedge:.1f}")
p0.get_pixmap(dpi=60).save(f"{tag}_p1.png")
sys.exit(0 if all(checks.values()) else 1)
