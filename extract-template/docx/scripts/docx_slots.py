"""Address text across DOCX stories while preserving runs and placeholder links."""
from collections import Counter
import posixpath
import zipfile
from xml.etree import ElementTree as ET

from docx_layout import W, NS

REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"


def addresses(root):
    result, parents = {}, {}

    def walk(node, path):
        result[node] = path
        counts = Counter()
        for child in node:
            counts[child.tag] += 1
            parents[child] = node
            name = "w:" + child.tag[len(W):] if child.tag.startswith(W) else child.tag
            walk(child, f"{path}/{name}[{counts[child.tag]}]")

    walk(root, "w:" + root.tag[len(W):] + "[1]")
    return result, parents


def ancestor(node, tag, parents):
    while node in parents:
        node = parents[node]
        if node.tag == tag:
            return node
    return None


def story_parts(archive):
    parts = ["word/document.xml"]
    glossary = None
    try:
        rels = ET.fromstring(archive.read("word/_rels/document.xml.rels"))
    except KeyError:
        return parts, glossary
    for rel in rels.findall(REL + "Relationship"):
        kind = rel.get("Type", "").rsplit("/", 1)[-1]
        if rel.get("TargetMode") == "External":
            continue
        target = rel.get("Target", "")
        target = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join("word", target))
        if kind in ("header", "footer", "footnotes", "endnotes") and target not in parts:
            parts.append(target)
        elif kind == "glossaryDocument":
            glossary = target
    return parts, glossary


def read_slots(path):
    result = []
    with zipfile.ZipFile(path) as archive:
        parts, glossary = story_parts(archive)
        glossary_parts = {}
        if glossary:
            root = ET.fromstring(archive.read(glossary))
            paths, _ = addresses(root)
            for part in root.iter(W + "docPart"):
                name = part.find("w:docPartPr/w:name", NS)
                if name is not None:
                    glossary_parts[name.get(W + "val")] = {
                        "part": glossary, "path": paths[part],
                        "text": "".join(t.text or "" for t in part.iter(W + "t")),
                    }

        for part in parts:
            root = ET.fromstring(archive.read(part))
            paths, parents = addresses(root)
            fields, depth = {}, 0
            for run in root.iter(W + "r"):
                opened = depth
                for child in run:
                    if child.tag == W + "fldChar":
                        kind = child.get(W + "fldCharType")
                        if kind == "begin":
                            depth += 1
                        elif kind == "end":
                            depth = max(0, depth - 1)
                fields[run] = opened > 0 or depth > 0 or ancestor(run, W + "fldSimple", parents) is not None

            for number, paragraph in enumerate(root.iter(W + "p"), 1):
                runs = []
                for run in paragraph.iter(W + "r"):
                    if ancestor(run, W + "p", parents) is not paragraph:
                        continue
                    text_nodes = run.findall(W + "t")
                    if not text_nodes:
                        continue
                    item = {"path": paths[run], "text": "".join(t.text or "" for t in text_nodes),
                            "text_paths": [paths[t] for t in text_nodes], "field": fields[run]}
                    control = ancestor(run, W + "sdt", parents)
                    if control is not None:
                        props = control.find(W + "sdtPr")
                        if props is not None:
                            showing = props.find(W + "showingPlcHdr")
                            item["showing_placeholder"] = showing is not None and showing.get(W + "val", "true") not in ("0", "false", "off")
                            reference = props.find("w:placeholder/w:docPart", NS)
                            if reference is not None:
                                key = reference.get(W + "val")
                                item["placeholder_name"] = key
                                item["placeholder"] = glossary_parts.get(key)
                            binding = props.find(W + "dataBinding")
                            if binding is not None:
                                item["data_binding"] = {key.rsplit("}", 1)[-1]: value for key, value in binding.attrib.items()}
                    runs.append(item)
                style = paragraph.find("w:pPr/w:pStyle", NS)
                row = ancestor(paragraph, W + "tr", parents)
                result.append({"part": part, "paragraph": number, "path": paths[paragraph],
                               "style": style.get(W + "val") if style is not None else "(default)",
                               "row": paths[row] if row is not None else None,
                               "text": "".join(run["text"] for run in runs), "runs": runs})
    return result
