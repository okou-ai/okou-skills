"""Inventory literal PPTX style evidence without inventing roles or effective styles."""
import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
PART = re.compile(r"^ppt/(?:slides/slide\d+|slideLayouts/slideLayout\d+|slideMasters/slideMaster\d+|theme/theme\d+)\.xml$")


def walk(node, path):
    yield node, path
    counts = {}
    for child in node:
        tag = child.tag.split("}")[-1]
        counts[tag] = counts.get(tag, 0) + 1
        yield from walk(child, f"{path}/{tag}[{counts[tag]}]")


def parse_xml(data):
    if len(data) > 5 * 1024 * 1024 or b"<!DOCTYPE" in data.upper():
        raise ValueError("Unsupported XML size or document type")
    return ET.fromstring(data)


def canvas_transform(canvas, width, height):
    if width <= 0 or height <= 0:
        raise ValueError("Invalid target canvas")
    scale = min(width / canvas["widthPt"], height / canvas["heightPt"])
    return {"targetWidthPx": width, "targetHeightPx": height, "scalePxPerPt": scale, "offsetXPx": (width - canvas["widthPt"] * scale) / 2, "offsetYPx": (height - canvas["heightPt"] * scale) / 2, "mode": "uniform-contain"}


def inspect(source, width=1600, height=900):
    source = Path(source)
    if source.stat().st_size > 100 * 1024 * 1024:
        raise ValueError("PPTX exceeds the 100MB input bound")
    observations = []
    with ZipFile(source) as archive:
        if sum(info.file_size for info in archive.infolist()) > 200 * 1024 * 1024:
            raise ValueError("PPTX exceeds the uncompressed input bound")
        presentation = parse_xml(archive.read("ppt/presentation.xml"))
        size = presentation.find(f"{{{P}}}sldSz")
        if size is None:
            raise ValueError("Missing source canvas")
        canvas = {"widthEmu": int(size.attrib["cx"]), "heightEmu": int(size.attrib["cy"])}
        canvas.update({"widthPt": canvas["widthEmu"] / 12700, "heightPt": canvas["heightEmu"] / 12700})
        if canvas["widthPt"] <= 0 or canvas["heightPt"] <= 0:
            raise ValueError("Invalid source canvas")
        transform = canvas_transform(canvas, width, height)
        parts = sorted(name for name in archive.namelist() if PART.fullmatch(name))
        for part in parts:
            root = parse_xml(archive.read(part))
            for node, location in walk(root, root.tag.split("}")[-1]):
                if not node.tag.startswith("{" + A + "}"):
                    continue
                tag = node.tag.split("}")[-1]
                base = {"part": part, "location": location, "origin": "extracted", "scope": "literal-xml", "effective": False}
                if tag in ("rPr", "defRPr", "endParaRPr") and "sz" in node.attrib:
                    value = int(node.attrib["sz"]) / 100
                    if value > 0: observations.append({**base, "property": "font-size", "value": value, "unit": "pt", "normalized": {"value": value * transform["scalePxPerPt"], "unit": "px"}})
                if tag in ("latin", "ea", "cs") and node.get("typeface"):
                    value = node.get("typeface")
                    observations.append({**base, "property": "font-reference" if value.startswith("+") else "font-family", "value": value})
                if tag == "srgbClr" and re.fullmatch(r"[0-9A-Fa-f]{6}", node.get("val", "")):
                    transforms = [{"kind": child.tag.split("}")[-1], "value": child.get("val")} for child in node]
                    observations.append({**base, "property": "color", "value": "#" + node.attrib["val"].lower(), "transforms": transforms})
                if tag == "schemeClr":
                    observations.append({**base, "property": "color-reference", "value": node.get("val"), "transforms": [{"kind": child.tag.split("}")[-1], "value": child.get("val")} for child in node]})
                if tag == "normAutofit":
                    observations.append({**base, "property": "source-autofit", "attributes": dict(node.attrib)})
    return {
        "sourceFilename": source.name,
        "sourceSha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "canvas": canvas,
        "canvasTransform": transform,
        "slideCount": sum(bool(re.fullmatch(r"ppt/slides/slide\d+\.xml", name)) for name in parts),
        "observations": observations,
        "counts": {prop: sum(record["property"] == prop for record in observations) for prop in sorted({record["property"] for record in observations})},
        "unknown": ["Semantic text and color roles", "Effective run/placeholder/layout/master/theme inheritance", "Effective font after source autofit and transforms", "Readability limits and content capacity", "Final rendering when source fonts are unavailable"],
        "limitations": "Literal evidence inventory only. Do not convert all observations to theme defaults or mark inferred semantic mapping as extracted. Rendering and role selection remain required."
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--height", type=int, default=900)
    args = parser.parse_args()
    report = inspect(args.input, args.width, args.height)
    target = Path(args.out)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"out": str(target), "slideCount": report["slideCount"], "counts": report["counts"], "effectiveStylesResolved": False}))


if __name__ == "__main__":
    main()
