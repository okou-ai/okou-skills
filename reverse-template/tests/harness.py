"""Run each skill exactly as its SKILL.md says, on every corpus document, then
judge the delivered package: its own instructions must convert probe.md, the
render must pass the layout gate, and the render must match the source."""
import os, sys, json, subprocess, shutil, re, glob
SK = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); RUNS = "/tmp/runs"
ENV = dict(os.environ, PATH="/tmp/vendor/pandoc-3.11/bin:" + os.environ["PATH"])
def sh(cmd, cwd=None):
    r = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, env=ENV, timeout=600)
    return r.returncode, (r.stdout + r.stderr)

def render(pkg, tag):
    md = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "probe.md")).read()
    sk = open(f"{pkg}/SKILL.md").read()
    cmd = re.search(r"```bash\npandoc doc\.md (.*?)\n```", sk).group(1)
    # the package's own snippet, if it has one, otherwise plain probe
    snippet = re.search(r"````markdown\n(.*?)\n````", sk, re.S)
    if snippet:
        brks = re.findall(r"```\{=openxml\}\n.*?\n```", snippet.group(1), re.S)
        body = md.split("---\n", 2)[2]
        # title block | brk1 | sections; every H1 spans: brk(N) heading brk(1)
        parts = re.split(r"(?m)^(# .*)$", body)
        out = md.split("---\n", 2)[0] + "---\n" + md.split("---\n", 2)[1] + "---\n\n" + brks[0] + "\n" + parts[0]
        for i in range(1, len(parts), 2):
            out += "\n" + brks[1] + "\n\n" + parts[i] + "\n\n" + brks[2] + "\n" + parts[i + 1]
        out += "\n" + brks[3] + "\n"
        md = out
    open(f"{pkg}/doc.md", "w").write(md)
    rc, o = sh(f"pandoc doc.md {cmd} -f markdown-smart", cwd=pkg)
    if rc: return f"pandoc FAILED: {o[-300:]}"
    rc, o = sh(f"soffice --headless --convert-to pdf --outdir . out.docx", cwd=pkg)
    return None if os.path.exists(f"{pkg}/out.pdf") else f"render FAILED {o[-200:]}"

def docx_flow(src):
    name = os.path.splitext(os.path.basename(src))[0]
    out = f"{RUNS}/docx_{name}"; shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
    log = []
    S = f"{SK}/reverse-template/docx/scripts"
    rc, o = sh(f"python3 {S}/inspect_docx.py {src}", cwd=out); log.append(("inspect", rc, o))
    if "formatted by hand" in o:
        # the inspector says: render it and reverse the render
        rd = f"{RUNS}/render_{name}"; os.makedirs(rd, exist_ok=True)
        pdf = f"{rd}/{name}.pdf"
        for _ in range(3):
            sh(f"soffice --headless --convert-to pdf --outdir {rd} {src}", cwd=rd)
            if os.path.exists(pdf): break
            import time; time.sleep(2)
        log.append(("-> pdf-reverse-template on the render", 0, ""))
        nm, plog, pkg, srcpdf = pdf_flow(pdf, 1, tag=f"docx_{name}")
        return name, log + plog, pkg, f"/tmp/corpus/{name}.pdf"
    mp = re.search(r"--map '([^']+)'", o)
    mapflag = f" --map '{mp.group(1)}'" if mp else ""
    for step in (f"python3 {S}/build_reference.py {src} {out}/reference.docx{mapflag}",
                 f"python3 {S}/verify_reference.py {out}/reference.docx",
                 f"python3 {S}/make_package.py {src} {out}/reference.docx {out}/pkg --name {name}"):
        rc, o = sh(step, cwd=out); log.append((step.split("/")[-1].split()[0] + (mapflag and " (mapped)"), rc, o))
        if rc: return name, log, None, None
    return name, log, f"{out}/pkg", f"/tmp/corpus/{name}.pdf"


def auto_map(js):
    d = json.load(open(js))
    hs = sorted(d["headings"], key=lambda h: (-h["size"], not h["bold"]))
    ol = d.get("outline") or []
    title_lv = str(hs[0]["level"]) if hs else None
    sub_lv = None
    if len(ol) >= 2 and str(ol[0]["level"]) == title_lv:
        cand = next((h for h in hs if str(h["level"]) == str(ol[1]["level"])), None)
        if cand and not cand["bold"] and str(cand["level"]) != title_lv:
            sub_lv = str(cand["level"])
    roles = ["Title", "Heading1", "Heading2", "Heading3", "Heading4"]
    m = {}
    for h in hs:
        lv = str(h["level"])
        if lv == sub_lv:
            m[lv] = "Subtitle"; continue
        if roles: m[lv] = roles.pop(0)
    return ",".join(f"{k}={v}" for k, v in m.items())


def pdf_flow(src, columns, tag=None):
    name = os.path.splitext(os.path.basename(src))[0]
    out = f"{RUNS}/{tag or 'pdf_' + name}"; shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
    S = f"{SK}/reverse-template/pdf/scripts"; log = []
    cols = f" --columns {columns}" if columns > 1 else ""
    rc, o = sh(f"python3 {S}/analyze_pdf.py {src}{cols} --json {out}/styles.json", cwd=out); log.append(("analyze", rc, o))
    if rc: return name, log, None, None
    mp = auto_map(f"{out}/styles.json")
    for step in (f"python3 {S}/build_reference.py {out}/styles.json {out}/reference.docx --map {mp}",
                 f"python3 {S}/verify_roundtrip.py {out}/reference.docx {out}/styles.json --map {mp}",
                 f"python3 {S}/make_package.py {src} {out}/reference.docx {out}/styles.json {out}/pkg --map {mp} --name {name}"):
        rc, o = sh(step, cwd=out); log.append((step.split("/")[-1].split()[0], rc, o))
        if rc: return name, log, None, None
    return name, log, f"{out}/pkg", src

def judge(name, log, pkg, srcpdf):
    print(f"\n===== {name} =====")
    for step, rc, o in log:
        flag = "" if rc == 0 else f"  <-- rc={rc}"
        print(f"  {step:22} rc={rc}{flag}")
        if rc: print("    " + o.strip().replace("\n", "\n    ")[-600:])
    if not pkg: return
    err = render(pkg, name)
    if err: print("  RENDER:", err); return
    rc, o = sh("python3 " + os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_delivered.py") + f" {pkg}")
    print(f"  layout gate rc={rc}"); print("    " + o.strip().replace("\n", "\n    ")[-500:])
    rc, o = sh("python3 " + os.path.join(os.path.dirname(os.path.abspath(__file__)), "compare.py") + f" {srcpdf} {pkg}/out.pdf")
    print(f"  fidelity vs source rc={rc}"); print(o.rstrip())

if __name__ == "__main__":
    which = sys.argv[1:] or ["docx", "pdf"]
    COLS = {"c03_zh_newsletter_2col": 2, "c06_en_brochure_3col_landscape": 3, "twocol": 2}
    if "docx" in which:
        for f in sorted(glob.glob("/tmp/corpus/*.docx")):
            judge(*docx_flow(f))
    if "pdf" in which:
        for f in ["/tmp/twocol.pdf", "/tmp/onecol.pdf"] + sorted(glob.glob("/tmp/corpus/*.pdf")):
            nm = os.path.splitext(os.path.basename(f))[0]
            judge(*pdf_flow(f, COLS.get(nm, 1)))
