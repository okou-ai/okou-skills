#!/usr/bin/env python3
"""Build numbered contact sheets and an offline gallery from inspected PNGs.

This is a review aid, not visual approval. Full pages remain available at their
original resolution; no review statuses are changed by generating or browsing it.
"""

import argparse
import hashlib
from html import escape
import json
from pathlib import Path
import shutil
import sys
import tempfile

import pymupdf


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build_gallery(qa, output=None, *, columns=2, per_sheet=6, thumb_width=420):
    qa = Path(qa).resolve()
    output = Path(output).resolve() if output else qa / "gallery"
    if output == qa or output in qa.parents:
        raise ValueError("Gallery output must be separate from the inspection directory and its parents.")
    if not (1 <= columns <= 4 and columns <= per_sheet <= 16 and 200 <= thumb_width <= 1000):
        raise ValueError("Use 1–4 columns, columns–16 pages per sheet, and 200–1000 px thumbnails.")
    inspection = qa / "inspection.json"
    inspection_hash = digest(inspection)
    report = json.loads(inspection.read_text(encoding="utf-8"))
    pages = report["pages"]
    if not pages or [p["number"] for p in pages] != list(range(1, report["page_count"] + 1)):
        raise ValueError("Inspection must contain every page exactly once and in order.")
    for page in pages:
        expected = f"page-{page['number']:03d}.png"
        if page["image"]["path"] != expected or digest(qa / expected) != page["image"]["sha256"]:
            raise ValueError(f"Page {page['number']} changed after inspection; inspect again.")
    output.parent.mkdir(parents=True, exist_ok=True)
    # Only replace directories created by this helper, never arbitrary user data.
    if output.exists():
        marker = output / "manifest.json"
        if not marker.is_file() or json.loads(marker.read_text()).get("kind") != "office-page-gallery":
            raise ValueError("Existing output is not an office page gallery. Choose a new directory.")
    with tempfile.TemporaryDirectory(prefix=".page-gallery-", dir=output.parent) as temporary:
        stage = Path(temporary) / "gallery"
        stage.mkdir()
        entries = []
        for page in pages:
            name = page["image"]["path"]
            shutil.copyfile(qa / name, stage / name)
            if digest(stage / name) != page["image"]["sha256"]:
                raise ValueError("A page changed while the gallery was being built; inspect again.")
            entries.append({"number": page["number"], "path": name, "sha256": page["image"]["sha256"]})
        sheets = []
        gutter, label_height = 18, 30
        thumb_height = round(thumb_width * 1.42)
        for start in range(0, len(entries), per_sheet):
            batch = entries[start:start + per_sheet]
            rows = (len(batch) + columns - 1) // columns
            with pymupdf.open() as contact:
                canvas = contact.new_page(
                    width=gutter + columns * (thumb_width + gutter),
                    height=gutter + rows * (thumb_height + label_height + gutter))
                canvas.draw_rect(canvas.rect, color=None, fill=(0.92, 0.94, 0.96))
                for index, entry in enumerate(batch):
                    x = gutter + (index % columns) * (thumb_width + gutter)
                    y = gutter + (index // columns) * (thumb_height + label_height + gutter)
                    canvas.insert_text((x, y + 17), f"Page {entry['number']}", fontsize=13)
                    box = pymupdf.Rect(x, y + label_height, x + thumb_width, y + label_height + thumb_height)
                    canvas.insert_image(box, filename=str(stage / entry["path"]), keep_proportion=True)
                name = f"overview-{len(sheets) + 1:03d}.png"
                canvas.get_pixmap(alpha=False).save(stage / name)
            sheets.append({"path": name, "first_page": batch[0]["number"], "last_page": batch[-1]["number"]})
        links = "\n".join(
            f'<a class="card" href="{entry["path"]}" data-index="{index}">'
            f'<span>Page {entry["number"]}</span><img src="{entry["path"]}" '
            f'alt="Page {entry["number"]}" loading="lazy"></a>'
            for index, entry in enumerate(entries))
        sheet_links = " · ".join(
            f'<a href="{sheet["path"]}">Pages {sheet["first_page"]}–{sheet["last_page"]}</a>'
            for sheet in sheets)
        title = escape(f"Page review · {len(entries)} pages")
        html = '''<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>__TITLE__</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#eef1f5;color:#192331;font:16px/1.5 system-ui,sans-serif}
header{padding:24px;max-width:1200px;margin:auto}h1{font-size:26px;margin:0 0 8px}p{margin:8px 0}
a{color:#164d93}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:20px;padding:0 24px 32px;max-width:1600px;margin:auto}
.card{display:block;text-decoration:none;background:white;border-radius:8px;padding:12px;box-shadow:0 2px 8px #0001}
.card span{display:block;margin-bottom:8px;font-weight:600}.card img{display:block;width:100%;height:auto}
dialog{border:0;padding:0;width:98vw;max-width:none;height:96vh;max-height:none;background:#e4e8ee}
dialog::backdrop{background:#000a}.toolbar{display:flex;gap:12px;align-items:center;flex-wrap:wrap;padding:12px;background:white}
button{font:inherit;padding:6px 12px;cursor:pointer}#counter{margin-right:auto}#viewport{height:calc(100% - 70px);overflow:auto;padding:16px}
#full{display:block;width:100%;height:auto;margin:auto}#full.actual{width:auto;max-width:none}
</style>
<header><h1>__TITLE__</h1><p>Click a page to enlarge. Use ← / → to move between pages, Home / End to jump, Esc to close.</p>
<p>Contact sheets: __SHEETS__</p><p>Use the overview for layout, then inspect every page at readable size. Browsing does not mark a page as passed.</p></header>
<main>__PAGES__</main>
<dialog id="viewer" aria-label="Full page review"><div class="toolbar"><strong id="counter"></strong>
<button id="previous" aria-label="Previous page">← Previous</button><button id="next" aria-label="Next page">Next →</button>
<button id="size">Original pixels</button><button id="close">Close</button></div>
<div id="viewport"><img id="full" alt=""></div></dialog>
<script>
const cards=[...document.querySelectorAll('.card')], viewer=document.querySelector('#viewer'), full=document.querySelector('#full');
let current=0;
function show(index){current=Math.max(0,Math.min(cards.length-1,index));full.src=cards[current].getAttribute('href');full.alt=`Page ${current+1}`;
document.querySelector('#counter').textContent=`Page ${current+1} of ${cards.length}`;document.querySelector('#previous').disabled=current===0;
document.querySelector('#next').disabled=current===cards.length-1;document.querySelector('#viewport').scrollTo(0,0);if(!viewer.open)viewer.showModal();}
cards.forEach((card,index)=>card.addEventListener('click',event=>{event.preventDefault();show(index)}));
document.querySelector('#previous').onclick=()=>show(current-1);document.querySelector('#next').onclick=()=>show(current+1);
document.querySelector('#close').onclick=()=>viewer.close();document.querySelector('#size').onclick=event=>{full.classList.toggle('actual');event.target.textContent=full.classList.contains('actual')?'Fit width':'Original pixels'};
document.addEventListener('keydown',event=>{if(!viewer.open)return;const moves={ArrowLeft:current-1,ArrowRight:current+1,Home:0,End:cards.length-1};
if(event.key in moves){event.preventDefault();show(moves[event.key]);}});
</script></html>'''
        (stage / "index.html").write_text(html.replace("__TITLE__", title).replace("__SHEETS__", sheet_links).replace("__PAGES__", links), encoding="utf-8")
        manifest = {"kind": "office-page-gallery", "status": "review-aid", "inspection_sha256": inspection_hash,
                    "page_count": len(entries), "pages": entries, "contact_sheets": sheets}
        (stage / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if digest(inspection) != inspection_hash:
            raise ValueError("Inspection changed during gallery creation; regenerate the gallery.")
        if output.exists():
            shutil.rmtree(output)
        stage.replace(output)
    return output / "index.html"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("qa", type=Path, help="Directory containing inspection.json and page-NNN.png")
    parser.add_argument("--out", type=Path, help="Separate gallery directory; default: QA/gallery")
    parser.add_argument("--columns", type=int, default=2)
    parser.add_argument("--pages-per-sheet", type=int, default=6)
    parser.add_argument("--thumb-width", type=int, default=420)
    args = parser.parse_args()
    try:
        print(build_gallery(args.qa, args.out, columns=args.columns, per_sheet=args.pages_per_sheet, thumb_width=args.thumb_width))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f"Gallery failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
