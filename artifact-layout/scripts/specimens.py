"""Render the ranked expression specimens with the production content model."""

import copy
import hashlib
import html
import io
import json
import tempfile
import zipfile
from pathlib import Path

from render import ASSETS, bundle_image, load_asset, render_report


def ranked_reports():
    ranking = load_asset("top30.json")
    examples = load_asset("examples/top30.json")
    return [
        (entry, copy.deepcopy(examples[entry["id"]])) for entry in ranking["entries"]
    ]


def resolve_images(report):
    for section in report["sections"]:
        for block in section["blocks"]:
            if "image" in block:
                block["image"] = str(ASSETS / "examples" / block["image"])


def build_specimens(output):
    catalog = {entry["id"]: entry for entry in load_asset("catalog.json")["entries"]}
    rows, links = [], {}
    for entry, example in ranked_reports():
        identity = entry["id"]
        term = catalog[identity]
        links[identity] = {"reason": entry["reason"], "name": term["zh"], "themes": {}}
        for theme in load_asset("themes.json"):
            report = copy.deepcopy(example)
            report["theme"] = theme
            resolve_images(report)
            relative = Path("expressions") / f"{identity}-{theme}"
            destination = output / relative
            with tempfile.TemporaryDirectory() as temporary:
                model = Path(temporary) / "report.json"
                model.write_text(
                    json.dumps(report, ensure_ascii=False), encoding="utf-8"
                )
                render_report(model, destination)
            # Downloadable models use bundle-relative assets, never local paths.
            for section in report["sections"]:
                for block in section["blocks"]:
                    if "image" in block:
                        block["image"] = bundle_image(block["image"], destination)
            data = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
            filename = (
                "model-" + hashlib.sha256(data.encode()).hexdigest()[:20] + ".json"
            )
            (destination / filename).write_text(data, encoding="utf-8")
            archive = io.BytesIO()
            with zipfile.ZipFile(
                archive, "w", compression=zipfile.ZIP_DEFLATED
            ) as bundle:
                files = {"report.json": data.encode()}
                files.update(
                    {
                        asset.relative_to(destination).as_posix(): asset.read_bytes()
                        for asset in (destination / "assets").glob("*")
                    }
                )
                for name, contents in sorted(files.items()):
                    info = zipfile.ZipInfo(name, date_time=(2000, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    bundle.writestr(info, contents)
            archive_name = (
                "example-"
                + hashlib.sha256(archive.getvalue()).hexdigest()[:20]
                + ".zip"
            )
            (destination / archive_name).write_bytes(archive.getvalue())
            links[identity]["themes"][theme] = {
                "page": (relative / "index.html").as_posix(),
                "model": (relative / filename).as_posix(),
                "bundle": (relative / archive_name).as_posix(),
            }
        rows.append(
            f'<button type="button" class="term-option" data-term="{identity}" aria-pressed="false"><span class="term-rank">{entry["rank"]:02d}</span><span><strong>{html.escape(term["zh"])}</strong><small>{identity} · {html.escape(term["en"])}</small></span></button>'
        )
    markup = (
        '<section class="top30" aria-labelledby="top30-title"><h2 id="top30-title">Top 30 · 逐项查看表达</h2><p class="note">按商务报告、调研和数据分析的使用广度、表达价值与组合能力排序；这是维护优先级，不是实际使用量统计。30项均支持HTML、Word与PDF。</p><div class="specimen-grid"><div class="term-picker"><label for="term-search">搜索名称或ID</label><input id="term-search" type="search" placeholder="例如：趋势、N01、table" /><div class="term-list">'
        + "".join(rows)
        + '</div><p id="no-terms" hidden>没有匹配项。</p></div><div class="specimen-stage"><div class="specimen-info"><h3 id="specimen-name"></h3><p id="specimen-reason"></p><div class="specimen-links"><a id="specimen-open" target="_blank" rel="noopener">查看完整示例 ↗</a><a id="specimen-model" download>下载示例包</a></div></div><iframe id="specimen-view" title="选中的表达示例"></iframe></div></div></section>'
    )
    return markup, links
