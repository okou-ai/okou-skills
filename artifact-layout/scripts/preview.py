#!/usr/bin/env python3
"""Build a browsable preview from the production renderer and maintained assets."""

import argparse
import html
import json
import tempfile
from pathlib import Path

from render import ASSETS, load_asset, render_report
from specimens import build_specimens


def build_preview(output):
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    themes, recipes = load_asset("themes.json"), load_asset("recipes.json")
    for recipe in recipes:
        source = ASSETS / "examples" / (recipe + ".json")
        report = json.loads(source.read_text(encoding="utf-8"))
        for theme in themes:
            # Asset paths keep their original resolution while the theme changes.
            for section in report["sections"]:
                for block in section["blocks"]:
                    if "image" in block:
                        block["image"] = str((source.parent / block["image"]).resolve())
            report["theme"] = theme
            with tempfile.TemporaryDirectory() as temporary:
                model = Path(temporary) / "report.json"
                model.write_text(
                    json.dumps(report, ensure_ascii=False), encoding="utf-8"
                )
                render_report(model, output / "reports" / f"{recipe}-{theme}")

    labels = {
        "editorial-research": (
            "杂志式研究报告",
            "双栏正文 · 大数字 · 跨栏图表 · 图文并置",
        ),
        "executive-brief": ("经营分析简报", "指标条 · 趋势图 · 模块化组合 · 宽表格"),
        "comparison-review": (
            "对比评估报告",
            "比较矩阵 · 主栏与侧栏 · 统一尺度 · 重点说明",
        ),
    }
    cards = []
    for recipe in recipes:
        name, description = labels[recipe]
        link = f"reports/{recipe}-warm-editorial/index.html"
        cards.append(
            f'<article class="card" data-recipe="{recipe}"><div class="frame"><iframe src="{link}" title="{name}的实际版式预览" tabindex="-1" loading="lazy"></iframe></div><div class="card-body"><h2>{name}</h2><p>{description}</p><a href="{link}" target="_blank" rel="noopener">查看完整报告 ↗</a></div></article>'
        )
    theme_buttons = "".join(
        f'<button type="button" data-theme="{key}" aria-pressed="{"true" if key == "warm-editorial" else "false"}">{html.escape(theme["name"])}</button>'
        for key, theme in themes.items()
    )
    vocabulary = load_asset("catalog.json")
    specimens, specimen_links = build_specimens(output)
    term_rows = []
    for entry in vocabulary["entries"]:
        coverage = (
            "已实现" if entry["rendering"]["coverage"] == "built-in" else "表达参考"
        )
        term_rows.append(
            f"<tr><td>{entry['id']}</td><td><strong>{html.escape(entry['zh'])}</strong><br /><span>{html.escape(entry['en'])}</span></td><td>{html.escape(entry['use'])}</td><td>{coverage}</td></tr>"
        )
    document = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8" /><meta name="viewport" content="width=device-width, initial-scale=1" /><title>Okou · Artifact 版式库</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f5f5f1;color:#202c30;font-family:system-ui,"Noto Sans CJK SC",sans-serif;font-size:16px;line-height:1.65}main{max-width:1320px;margin:auto;padding:48px 32px}header{padding-bottom:30px;border-bottom:1px solid #d8dedb}.eyebrow{font-size:12px;letter-spacing:.12em;color:#5b6969}h1{font-size:clamp(30px,4vw,54px);line-height:1.15;letter-spacing:-.03em;margin:18px 0}header p{max-width:760px;color:#5b6969;margin-bottom:0}.facts{display:flex;gap:40px;margin-top:24px}.facts strong{font-size:25px;color:#202c30}.facts span{color:#5b6969;font-size:14px;margin-left:7px}.toolbar{display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap;padding:28px 0}button{border:1px solid #cbd2ce;border-radius:4px;padding:10px 16px;background:transparent;color:#344548;font:inherit;font-size:14px;cursor:pointer}button[aria-pressed="true"]{background:#273a3d;color:white;border-color:#273a3d}button:focus-visible,a:focus-visible{outline:3px solid #995433;outline-offset:3px}.themes{display:flex;gap:8px;flex-wrap:wrap}.note{font-size:13px;color:#5b6969}.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:22px}.card{min-width:0;background:white;border:1px solid #d8dedb}.frame{height:410px;overflow:hidden;background:#e9ecee;position:relative}iframe{width:1100px;height:1700px;border:0;transform:scale(.35);transform-origin:top left;pointer-events:none}.card-body{padding:22px}h2{font-size:20px;margin:0 0 8px}.card-body p{font-size:14px;color:#5b6969;min-height:46px;margin:0 0 20px}a{color:#345f65;text-decoration-thickness:1px;text-underline-offset:4px}details{margin-top:42px;border-top:1px solid #d8dedb;padding-top:22px}summary{cursor:pointer;font-weight:600}.terms{overflow:auto;margin-top:20px}table{width:100%;border-collapse:collapse;font-size:14px}th,td{text-align:left;vertical-align:top;padding:12px;border-bottom:1px solid #d8dedb}td span{color:#5b6969}footer{margin-top:42px;border-top:1px solid #d8dedb;padding-top:20px;color:#5b6969;font-size:13px}@media(max-width:980px){.grid{grid-template-columns:1fr 1fr}.facts{gap:22px}}@media(max-width:660px){main{padding:28px 20px}.grid{grid-template-columns:1fr}.frame{height:400px}.facts{flex-wrap:wrap;gap:16px}.facts strong{font-size:21px}.toolbar{align-items:flex-start;flex-direction:column}}
</style></head><body><main><header><div class="eyebrow">OKOU / ARTIFACT LAYOUT</div><h1>让信息有清楚的版式。</h1><p>同一套表达组件，组合出不同阅读节奏。切换视觉主题，查看研究报告、经营简报与对比评估的实际排版。</p><div class="facts"><div><strong>3</strong><span>报告配方</span></div><div><strong>4</strong><span>视觉主题</span></div><div><strong>15</strong><span>内容组件</span></div><div><strong>121</strong><span>表达参考</span></div></div></header><div class="toolbar"><div class="themes">THEME_BUTTONS</div><span class="note">示例文字与数字仅用于版式展示。</span></div><div class="grid">CARDS</div><details><summary>查看完整表达分类 · 109 项核心＋12 项扩展</summary><p class="note">这是一份工作分类。已实现的组件与表达参考分别标注；图表、版式和视觉方向可以组合使用。</p><div class="terms"><table><thead><tr><th>ID</th><th>中英文名称</th><th>适用场景</th><th>支持方式</th></tr></thead><tbody>TERMS</tbody></table></div></details><footer>版式资源统一维护在 okou-skills / artifact-layout。Word 与 PDF 使用同一份内容和主题，分页会随格式调整。</footer></main>
<script>
document.querySelectorAll('[data-theme]').forEach(button=>button.addEventListener('click',()=>{const theme=button.dataset.theme;document.querySelectorAll('[data-theme]').forEach(item=>item.setAttribute('aria-pressed',String(item===button)));document.querySelectorAll('[data-recipe]').forEach(card=>{const url='reports/'+card.dataset.recipe+'-'+theme+'/index.html';card.querySelector('iframe').src=url;card.querySelector('a').href=url;});}));
function sizeFrames(){document.querySelectorAll('.frame').forEach(frame=>{const scale=frame.clientWidth/1100;frame.querySelector('iframe').style.transform='scale('+scale+')';});}addEventListener('resize',sizeFrames);sizeFrames();
</script></body></html>"""
    document = (
        document.replace("THEME_BUTTONS", theme_buttons)
        .replace("CARDS", "".join(cards))
        .replace("TERMS", "".join(term_rows))
        .replace("<strong>15</strong>", "<strong>27</strong>")
        .replace(
            '<div class="grid">',
            specimens + '<h2 class="recipe-title">3套报告配方</h2><div class="grid">',
            1,
        )
        .replace(
            "</style>",
            """
.top30{margin:10px 0 44px}.top30 h2{font-size:26px}.specimen-grid{display:grid;grid-template-columns:minmax(260px, .9fr) minmax(0, 1.8fr);gap:22px;margin-top:24px}.term-picker{min-width:0}.term-picker label{display:block;font-size:13px;margin-bottom:6px}.term-picker input{width:100%;font:inherit;font-size:14px;border:1px solid #cbd2ce;padding:12px;background:#fff}.term-list{max-height:620px;overflow:auto;border:1px solid #d8dedb;border-top:0;background:#fff}.term-option{display:flex;gap:14px;width:100%;text-align:left;padding:13px 15px;border:0;border-bottom:1px solid #e5e9e6;border-radius:0}.term-option[hidden]{display:none}.term-rank{font-variant-numeric:tabular-nums;color:#7b8782;font-size:18px}.term-option strong{font-size:14px;font-weight:600}.term-option small{display:block;font-size:12px;line-height:1.5;color:#68766f;margin-top:3px}.term-option[aria-pressed="true"]{background:#e7eeea;color:#203831}.term-option[aria-pressed="true"] .term-rank{color:#254939}.specimen-stage{border:1px solid #d8dedb;min-width:0;background:white}.specimen-info{padding:22px 24px;border-bottom:1px solid #d8dedb}.specimen-info h3{margin:0;font-size:20px}.specimen-info p{font-size:14px;line-height:1.65;color:#5b6969;margin:10px 0 14px}.specimen-links{display:flex;gap:22px;flex-wrap:wrap;font-size:13px}#specimen-view{width:100%;height:580px;transform:none;pointer-events:auto;display:block}.recipe-title{margin:0 0 22px}@media(max-width:760px){.specimen-grid{grid-template-columns:1fr}.term-list{max-height:250px}#specimen-view{height:510px}.specimen-info{padding:18px}}
</style>""",
            1,
        )
        .replace(
            "<script>",
            "<script>\nconst specimens="
            + json.dumps(specimen_links, ensure_ascii=False).replace("<", "\\u003c")
            + ";\n",
            1,
        )
        .replace(
            "const theme=button.dataset.theme;",
            "const theme=button.dataset.theme;activeTheme=theme;showTerm(activeTerm);",
        )
        .replace(
            "function sizeFrames()",
            """let activeTerm="N01",activeTheme="warm-editorial";
function showTerm(id){activeTerm=id;const item=specimens[id],links=item.themes[activeTheme];document.getElementById('specimen-name').textContent=id+' · '+item.name;document.getElementById('specimen-reason').textContent=item.reason;document.getElementById('specimen-view').src=links.page;document.getElementById('specimen-open').href=links.page;document.getElementById('specimen-model').href=links.bundle;document.querySelectorAll('[data-term]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.term===id)));}
document.querySelectorAll('[data-term]').forEach(button=>button.addEventListener('click',()=>showTerm(button.dataset.term)));
document.getElementById('term-search').addEventListener('input',event=>{const query=event.target.value.trim().toLocaleLowerCase();let count=0;document.querySelectorAll('[data-term]').forEach(button=>{button.hidden=!button.textContent.toLocaleLowerCase().includes(query);if(!button.hidden)count++;});document.getElementById('no-terms').hidden=count>0;});
document.getElementById('specimen-view').addEventListener('load',event=>{const frame=event.target,section=frame.contentDocument?.querySelector('section');if(section)frame.contentWindow.scrollTo(0,Math.max(0,section.offsetTop-24));});showTerm(activeTerm);
function sizeFrames()""",
            1,
        )
    )
    (output / "index.html").write_text(document, encoding="utf-8")
    return output / "index.html"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    print(build_preview(args.out))
