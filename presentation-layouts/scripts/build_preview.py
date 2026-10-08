"""Build a self-contained synthetic acceptance deck. Not a source template extractor."""
import argparse
import copy
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import quote
from bind_tokens import compile_theme

ROOT = Path(__file__).resolve().parents[1]


def token(type_, value):
    return {"$type": type_, "$value": value, "$extensions": {"origin": {"kind": "inferred", "reason": "Synthetic acceptance fixture, not real source extraction."}}}


def materialize(node, context):
    placeholder = re.compile(r"\{\{([^{}]+)\}\}")
    replace = lambda text: placeholder.sub(lambda match: str(context[match.group(1)]), text or "")
    node.text, node.tail = replace(node.text), replace(node.tail)
    for name, value in list(node.attrib.items()): node.set(name, replace(value))
    for index, child in reversed(list(enumerate(list(node)))):
        repeat = child.get("data-repeat")
        if repeat:
            node.remove(child)
            for offset, item in enumerate(context[repeat]):
                clone = copy.deepcopy(child)
                clone.attrib.pop("data-repeat")
                materialize(clone, {**context, **item})
                node.insert(index + offset, clone)
        else:
            materialize(child, context)
    return node


def build(out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    minimal = json.loads((ROOT / "examples/minimal.tokens.json").read_text())
    image = 'data:image/svg+xml,' + quote('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400"><rect width="600" height="400" fill="#dededb"/><rect x="60" y="60" width="480" height="280" rx="16" fill="#f8f8f5"/><path d="M120 260L240 170L330 210L480 120" fill="none" stroke="#566166" stroke-width="12"/><text x="300" y="310" text-anchor="middle" font-family="sans-serif" font-size="20" fill="#333333">Synthetic illustration / not source data</text></svg>')
    payload = {
        "kpi-grid": {"title": "关键指标 / KPI overview", "metrics": [{"value": value, "label": label, "note": "合成数据 · Synthetic fixture"} for value, label in [("24", "客户 / Clients"), ("18%", "增长 / Growth"), ("7.2", "评分 / Score"), ("4", "团队 / Teams")]]},
        "table": {"title": "数据表格 / Structured evidence", "columns": [{"column": c} for c in ["项目 / Item", "当前 / Current", "状态 / Status"]], "rows": [{"cells": [{"cell": c} for c in row]} for row in [("方案 A / Option A", "24", "进行中 / Active"), ("方案 B / Option B", "18", "待确认 / Pending"), ("方案 C / Option C", "7", "已完成 / Complete")]], "source-note": "全部为合成数据 / All values are synthetic"},
        "two-column": {"title": "双栏叙述 / Two narratives", "left-heading": "背景 / Context", "left-body": "优先保留用户的源布局。只有缺少合适结构时，才读取共享布局。Prefer the source layout; borrow a neutral structure only when needed.", "right-heading": "行动 / Action", "right-body": "字体、颜色和组件属于用户模板。不要把共享结构当成新的主题。Typography, colors and components remain the user's design system."},
        "comparison": {"title": "并列对比 / Compare options", "option-a": "方案 A / Option A", "evidence-a": "保留相同的区域与内容，只切换样式绑定。Same regions and content, with an independent skin binding.", "option-b": "方案 B / Option B", "evidence-b": "无需重写结构，也不依赖任何专属 shell。The structure stays unchanged and has no theme-shell dependency."},
        "process": {"title": "四步流程 / Four-step process", **{f"step-{i}": s for i, s in enumerate(["1 · 观察 / Observe", "2 · 映射 / Map", "3 · 绑定 / Bind", "4 · 检查 / Check"], 1)}, **{f"detail-{i}": s for i, s in enumerate(["记录可靠来源 / Record evidence", "未知明确标注 / Mark unknowns", "由程序解析 / Resolve mechanically", "真实测量溢出 / Measure overflow"], 1)}},
        "image-text": {"title": "图文布局 / Image and narrative", "image-description": "Synthetic illustration; not a source chart", "heading": "有意义的图像 / Meaningful image", "body": "图像是内容而非背景装饰。保留独立资产、可读说明和源字体基线。Keep the image as a local asset and the narrative as editable text.", "source-note": "示意图，不代表真实数据 / Illustration only"}
    }
    palette = {"light": ("#f7f7f4", "#20252a", "#e9e9e5", "#4b5255", "#b6bdbe"), "dark": ("#172833", "#e6f2ed", "#253e4a", "#c4d9d2", "#739a99")}
    pages, styles, reports = [], [], {}
    for skin, (background, foreground, panel, secondary, border) in palette.items():
        theme = copy.deepcopy(minimal)
        tokens = theme["$tokens"]
        tokens["color.surface.canvas"] = token("color", background)
        tokens["color.on-surface.canvas.primary"] = token("color", foreground)
        for name, value in {"color.on-surface.canvas.secondary": secondary, "color.border.canvas": border, "color.surface.panel": panel, "color.on-surface.panel.primary": foreground, "color.on-surface.panel.secondary": secondary, "color.border.panel": border}.items(): tokens[name] = token("color", value)
        for role in ("title", "body"):
            tokens[f"type.{role}.font-weight"] = token("number", 600 if role == "title" else 400)
            tokens[f"type.{role}.line-height"] = token("number", 1.15 if role == "title" else 1.3)
        tokens["type.body.font-size"] = token("dimension", {"value": 32 if skin == "light" else 30, "unit": "px"})
        tokens["component.card.surface-role"] = token("string", "panel")
        tokens["component.card.padding"] = token("dimension", {"value": 30, "unit": "px"})
        tokens["component.card.radius"] = token("dimension", {"value": 16 if skin == "light" else 0, "unit": "px"})
        tokens["component.table.cell-padding"] = token("dimension", {"value": 18, "unit": "px"})
        tokens["component.table.rule-width"] = token("dimension", {"value": 1, "unit": "px"})
        css, report = compile_theme(theme)
        reports[skin] = report
        styles.append(css.replace(".okp-theme", f'.okp-theme[data-skin="{skin}"]'))
        for layout, data in payload.items():
            node = materialize(ET.fromstring((ROOT / "layouts" / f"{layout}.html").read_text()), data)
            for image_node in node.iter("img"): image_node.set("src", image)
            fragment = ET.tostring(node, encoding="unicode", method="html")
            pages.append(f'<section class="slide" data-slide="{skin}-{layout}"><div class="stage okp-theme" data-skin="{skin}">{fragment}<footer>{skin} · {layout} · SYNTHETIC FIXTURE / 非真实提取</footer></div></section>')
    geometry = (ROOT / "styles/geometry.css").read_text()
    fitter = (ROOT / "scripts/fit-text.js").read_text()
    policies = {skin: {"roleMap": report["roleMap"], "roleBounds": {"title": {"minScale": 0.75}, "body": {"minScale": 0.75}}} for skin, report in reports.items()}
    html = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Shared layouts — synthetic acceptance</title><style>' + geometry + '\n'.join(styles) + '''
html,body { margin:0; background:#121a20; scrollbar-width:none; }
::-webkit-scrollbar { display:none; }
.slide,.stage { width:1600px; height:900px; }
.stage { box-sizing:border-box; padding:64px; position:relative; }
.stage footer { position:absolute; bottom:18px; left:64px; font:16px sans-serif; color:inherit; }
.slide { margin:auto; }
</style></head><body><main class="deck">''' + ''.join(pages) + f'</main><script>{fitter}</script><script>const policies={json.dumps(policies)}; window.fixtureReady=(async()=>{{ window.fixtureReports=[]; for(const stage of document.querySelectorAll(".stage")) window.fixtureReports.push(await OkpFit.fit(stage,policies[stage.dataset.skin])); document.documentElement.dataset.fitReady="true"; }})();</script></body></html>'
    (out / "deck.html").write_text(html)
    (out / "bindings.json").write_text(json.dumps(reports, ensure_ascii=False, indent=2) + "\n")
    # The view scales the fixed intrinsic canvas, not its source font-size tokens.
    viewer = '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>共享布局 · 验收预览</title><style>body{margin:0;padding:24px;background:#121a20;color:#eff4f3;font:16px system-ui}h1{font-size:24px}p{color:#c1ccca;line-height:1.6}button{padding:10px 18px;margin:0 8px 16px 0;background:#d5e7e0;color:#172833;border:0;border-radius:6px;cursor:pointer}.viewport{width:100%;aspect-ratio:16/9;overflow:hidden}iframe{border:0;width:1600px;height:900px;transform-origin:top left}</style><h1>共享布局 · v1 验收预览</h1><p>六类中性结构 × 两套合成皮肤。此页不是实际模板提取结果，也不代表首稿通过率或速度提升。</p><button id="prev">上一页</button><button id="next">下一页</button><span id="counter"></span><div class="viewport"><iframe src="deck.html" title="合成布局验证"></iframe></div><p><a href="deck.html" style="color:#c7e5db">打开完整测试页</a> · 字号基线由绑定器输出；fit 只在真实溢出时执行。</p><script>const f=document.querySelector("iframe"),v=document.querySelector(".viewport");let n=0;function show(){f.style.transform=`scale(${v.clientWidth/1600})`;f.contentWindow.scrollTo(0,n*900);document.querySelector("#counter").textContent=`${n+1} / 12`}f.onload=show;window.onresize=show;document.querySelector("#prev").onclick=()=>{n=(n+11)%12;show()};document.querySelector("#next").onclick=()=>{n=(n+1)%12;show()};document.onkeydown=e=>{if(["ArrowRight","ArrowDown"].includes(e.key)){e.preventDefault();n=(n+1)%12;show()}if(["ArrowLeft","ArrowUp"].includes(e.key)){e.preventDefault();n=(n+11)%12;show()}};</script></html>'
    (out / "index.html").write_text(viewer)
    print(json.dumps({"out": str(out), "pages": len(pages), "synthetic": True}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    build(parser.parse_args().out)
