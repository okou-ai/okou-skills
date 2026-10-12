#!/usr/bin/env python3
"""Inventory an HTML deck once and preserve its editable slide fragments (stdlib only)."""
import argparse
from dataclasses import dataclass, field
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import time
from urllib.parse import urljoin


VOID = set("area base br col embed hr img input link meta param source track wbr".split())


@dataclass
class Element:
    tag: str
    attrs: dict
    start: int
    opening_end: int
    parent: object
    closing_start: int = 0
    end: int = 0
    text: list = field(default_factory=list)

    def has_class(self, name):
        return name in self.attrs.get("class", "").split()

    def inside(self, ancestor):
        node = self.parent
        while node:
            if node is ancestor:
                return True
            node = node.parent
        return False


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.source = source
        self.lines = [0] + [m.end() for m in re.finditer("\n", source)]
        self.elements, self.stack, self.errors = [], [], []
        self.feed(source)
        self.close()
        self.errors.extend(f"Unclosed <{node.tag}> at offset {node.start}" for node in self.stack)

    def source_offset(self):
        line, column = self.getpos()
        return self.lines[line - 1] + column

    def handle_starttag(self, tag, attrs):
        start = self.source_offset()
        node = Element(tag, dict((key, value or "") for key, value in attrs), start,
                       start + len(self.get_starttag_text()), self.stack[-1] if self.stack else None)
        self.elements.append(node)
        if tag in VOID:
            node.closing_start = node.end = node.opening_end
        else:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        node = self.elements[-1]
        if self.stack and self.stack[-1] is node:
            self.stack.pop()
        node.closing_start = node.end = node.opening_end

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack or self.stack[-1].tag != tag:
            self.errors.append(f"Unbalanced </{tag}> at offset {self.source_offset()}")
            return
        node = self.stack.pop()
        node.closing_start = self.source_offset()
        node.end = self.source.find(">", node.closing_start) + 1

    def handle_data(self, data):
        if any(node.tag in ("script", "style") for node in self.stack):
            return
        for node in self.stack:
            node.text.append(data)


def inventory(source, source_name, slide_class="slide", stage_class="stage", base=""):
    document = Document(source)
    if document.errors:
        raise ValueError("Use a browser-serialized DOM for HTML with omitted/unbalanced tags: "
                         + "; ".join(document.errors[:3]))
    slides = [node for node in document.elements if node.has_class(slide_class)]
    if not slides:
        raise ValueError("No static slide elements found; inspect the rendered DOM or set --slide-class")
    if any(node.inside(other) for node in slides for other in slides if node is not other):
        raise ValueError("Nested slide elements need an explicit source adaptation")
    base_node = next((node for node in document.elements if node.tag == "base" and node.attrs.get("href")), None)
    if base_node:
        base = urljoin(base, base_node.attrs["href"])
    resources, scripts = [], []
    for node in document.elements:
        attrs = node.attrs
        if node.tag in ("img", "source", "video", "audio", "link", "image", "use", "object", "embed", "iframe", "script"):
            for key in ("src", "href", "xlink:href", "poster", "data", "srcset", "imagesrcset"):
                if attrs.get(key):
                    resources.append({"tag": node.tag, "attribute": key, "value": attrs[key],
                                      "resolved": urljoin(base, attrs[key]) if key not in ("srcset", "imagesrcset") else None})
        if node.tag == "script":
            scripts.append({"src": attrs.get("src"), "type": attrs.get("type", "text/javascript"),
                            "bytes": len(source[node.start:node.end].encode())})
    layouts, fragments, used_ids = [], {}, set()
    for number, slide in enumerate(slides, 1):
        descendants = [node for node in document.elements if node.inside(slide)]
        stages = [node for node in descendants if node.has_class(stage_class)]
        stage = stages[0] if len(stages) == 1 else None
        name = stage.attrs.get("data-layout") or stage.attrs.get("data-source-profile") if stage else None
        layout_id = re.sub(r"[^a-z0-9-]+", "-", (name or f"page-{number:03}").lower()).strip("-") or f"page-{number:03}"
        candidate, suffix = layout_id, 2
        while candidate in used_ids:
            candidate = f"{layout_id}-{suffix}"
            suffix += 1
        layout_id = candidate
        used_ids.add(layout_id)
        file = f"source/{layout_id}.html"
        fragments[file] = source[slide.start:slide.end]
        regions = []
        for node in descendants:
            role = node.attrs.get("data-text-role") or node.attrs.get("data-region")
            if role or re.fullmatch("h[1-6]", node.tag):
                text = " ".join("".join(node.text).split())
                regions.append({"role": role or node.tag, "characters": len(text), "sample": text[:100]})
        issues = []
        if len(stages) != 1:
            issues.append(f"Expected one stage; found {len(stages)}")
        fits = [node for node in descendants if node.has_class("fit") and stage and node.inside(stage)]
        if len(fits) != 1:
            issues.append(f"Expected one .fit inside stage; found {len(fits)}")
        layouts.append({"id": layout_id, "file": file, "sourcePages": [number],
                        "sourceRole": stage.attrs.get("data-slot") if stage else None,
                        "regions": regions, "issues": issues})
    # Keep every source composition; repeated names alone do not prove equivalent layouts.
    unique_resources = list({json.dumps(item, sort_keys=True): item for item in resources}.values())
    return {"sourceFilename": source_name, "pageCount": len(slides), "layouts": layouts,
            "resources": unique_resources, "scripts": scripts,
            "notes": ["Character counts describe source content, not tested maximum capacity.",
                      "Fragments retain original markup and paths. Localize resources before packaging.",
                      "Inspect CSS imports, url() and inline styles as well as the HTML resource list."]}, fragments


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Downloaded HTML or browser-serialized DOM")
    parser.add_argument("--out", type=Path, required=True, help="Extraction work directory, outside the saved package")
    parser.add_argument("--base-url", default="", help="Original URL for resolving HTML resource references")
    parser.add_argument("--slide-class", default="slide")
    parser.add_argument("--stage-class", default="stage")
    args = parser.parse_args()
    started = time.monotonic()
    if args.out.exists() and any(args.out.iterdir()):
        parser.error("Choose a new or empty --out directory to preserve earlier extraction evidence")
    try:
        report, fragments = inventory(args.input.read_text(encoding="utf-8"), args.base_url or args.input.name,
                                      args.slide_class, args.stage_class,
                                      args.base_url or args.input.resolve().as_uri())
    except ValueError as error:
        parser.error(str(error))
    for file, html in fragments.items():
        target = args.out / file
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding="utf-8")
    report["elapsedMs"] = round((time.monotonic() - started) * 1000)
    output = args.out / "inventory.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"inventory": str(output), "fragments": str(args.out / "source"),
                      "pageCount": report["pageCount"], "elapsedMs": report["elapsedMs"],
                      "pagesNeedingHooks": [entry["sourcePages"][0] for entry in report["layouts"] if entry["issues"]]}))


if __name__ == "__main__":
    main()
