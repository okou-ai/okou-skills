#!/usr/bin/env python3
"""Read-only, stdlib DOCX text and package inventory. No setup, conversion or writes.

Text is stored OOXML text in document order, not rendered pagination or lossless
content extraction. Field results may be stale; drawings, equations, automatic
numbering and alternate-content semantics require specialized inspection.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import posixpath
import re
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
from zipfile import BadZipFile, ZipFile


WORD = {"http://schemas.openxmlformats.org/wordprocessingml/2006/main",
        "http://purl.oclc.org/ooxml/wordprocessingml/main"}
RELS = {"http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        "http://purl.oclc.org/ooxml/officeDocument/relationships"}
LIMITS = ("Stored OOXML text, not rendered pages or lossless extraction; excludes "
          "deleted/moved-from text and field instructions. Cached field results may "
          "be stale. Drawings, equations, automatic numbering and alternate content "
          "need specialized inspection. This is not full revision/render semantics. "
          "Non-body parts are separate, not in page order.")
BODY_LIMIT = 50
TEXT_LIMIT = 160


def split_tag(tag):
    if tag.startswith("{"):
        return tag[1:].split("}", 1)
    return "", tag


def word(element, name):
    namespace, local = split_tag(element.tag)
    return namespace in WORD and local == name


def attribute(element, name):
    return next((value for key, value in element.attrib.items()
                 if split_tag(key)[0] in WORD and split_tag(key)[1] == name), None)


def children(element, name):
    return [child for child in element if word(child, name)]


def descendants(element, name):
    return [child for child in element.iter() if word(child, name)]


def first(element, name):
    return next(iter(children(element, name)), None)


def value(element, name):
    child = first(element, name)
    return attribute(child, "val") if child is not None else None


def inline_text(element):
    """Join run fragments, preserving stored spaces, tabs and explicit breaks."""
    if word(element, "del") or word(element, "moveFrom"):
        return ""
    if word(element, "t"):
        return element.text or ""
    if word(element, "tab"):
        return "\t"
    if word(element, "br"):
        kind = attribute(element, "type")
        return {"page": "\n[PAGE BREAK]\n", "column": "\n[COLUMN BREAK]\n"}.get(kind, "\n")
    if word(element, "cr"):
        return "\n"
    for name, label in (("footnoteReference", "FOOTNOTE"), ("endnoteReference", "ENDNOTE"),
                        ("commentReference", "COMMENT")):
        if word(element, name):
            return f"[{label}:{attribute(element, 'id')}]"
    return "".join(inline_text(child) for child in element)


def inline_chunks(element):
    if word(element, "del") or word(element, "moveFrom"):
        return
    if len(element) == 0:
        yield inline_text(element)
    else:
        for child in element:
            yield from inline_chunks(child)


def separated_chunks(elements, separator, reader):
    for index, element in enumerate(elements):
        if index:
            yield separator
        yield from reader(element)


def block_chunks(element):
    # Revision wrappers can contain entire paragraphs/tables, not just runs.
    if word(element, "del") or word(element, "moveFrom") or word(element, "sectPr"):
        return
    if word(element, "p"):
        yield from inline_chunks(element)
    elif word(element, "tbl"):
        def cell_chunks(cell):
            yield from separated_chunks((child for child in cell if not word(child, "tcPr")),
                                        "\n", block_chunks)

        def row_chunks(row):
            yield from separated_chunks(children(row, "tc"), "\t", cell_chunks)

        yield "[TABLE]\n"
        yield from separated_chunks(children(element, "tr"), "\n", row_chunks)
        yield "\n[END TABLE]"
    else:
        # SDTs/custom XML wrappers may contain paragraphs and tables.
        yield from separated_chunks((child for child in element
                                     if not word(child, "sdtPr") and not word(child, "sdtEndPr")),
                                    "\n", block_chunks)


def block_text(element):
    return "".join(block_chunks(element))


def text_summary(element, full=False):
    if full:
        return block_text(element), False
    chunks, length = [], 0
    for chunk in block_chunks(element):
        chunks.append(chunk[:TEXT_LIMIT + 1 - length])
        length += len(chunks[-1])
        if length > TEXT_LIMIT:
            break
    text = "".join(chunks)
    return text[:TEXT_LIMIT], len(text) > TEXT_LIMIT


def metadata(element):
    """Section properties without serialized XML; preserve nested attributes."""
    def qualified(name):
        namespace, local = split_tag(name)
        return ("w:" + local if namespace in WORD else
                "r:" + local if namespace in RELS else name)
    result = {"kind": qualified(element.tag)}
    if element.attrib:
        result["attributes"] = {qualified(k): v for k, v in element.attrib.items()}
    if len(element):
        result["children"] = [metadata(child) for child in element]
    return result


class Package:
    def __init__(self, path):
        self.zip = ZipFile(path, "r")
        names = self.zip.namelist()
        if len(names) != len(set(names)):
            self.zip.close()
            raise ValueError("Duplicate ZIP member names make part selection ambiguous")
        self.names = set(names)
        self.xml = {}

    def close(self):
        self.zip.close()

    def parse(self, name, data=None):
        if name not in self.xml:
            data = self.zip.read(name) if data is None else data
            if b"<!DOCTYPE" in data.upper():
                raise ValueError(f"DTD declarations are not supported: {name}")
            self.xml[name] = ET.fromstring(data)
        return self.xml[name]

    def text_parts(self, selection):
        result = []
        groups = {"body": ["word/document.xml"],
                  "headers": sorted(n for n in self.names if n.startswith("word/header") and n.endswith(".xml")),
                  "footers": sorted(n for n in self.names if n.startswith("word/footer") and n.endswith(".xml")),
                  "footnotes": ["word/footnotes.xml"], "endnotes": ["word/endnotes.xml"],
                  "comments": ["word/comments.xml"]}
        for item in selection:
            candidates = (sum(groups.values(), []) if item == "all"
                          else groups.get(item, [item]))
            for name in candidates:
                if name not in self.names:
                    if item not in groups and item != "all":
                        raise ValueError(f"Missing package part: {name}")
                    if name == "word/document.xml":
                        raise ValueError("Missing main body part: word/document.xml")
                    continue
                if name not in result:
                    result.append(name)
        return result


def text_output(package, selection, start=0, end=None):
    for name in package.text_parts(selection):
        root = package.parse(name)
        is_body = name == "word/document.xml"
        content = first(root, "body") if is_body else root
        if content is None:
            raise ValueError(f"Missing body in {name}")
        label = "BODY" if is_body else "PART"
        print(f"[{label}: {name}]")
        elements = list(content)
        if is_body and (start or end is not None):
            print(f"[BODY ELEMENT RANGE: {start}:{end if end is not None else len(elements)}; zero-based, end exclusive]")
            elements = elements[start:end]
        for element in elements:
            kind = split_tag(element.tag)[1]
            if kind in ("footnote", "endnote", "comment"):
                print(f"[{kind.upper()} id={attribute(element, 'id')}]")
                print(block_text(element))
                print(f"[END {kind.upper()}]")
            elif not word(element, "sectPr"):
                print(block_text(element))
        print(f"[END {label}: {name}]")


def relationship_source(name):
    if name == "_rels/.rels":
        return ""
    directory, filename = posixpath.split(name)
    return posixpath.join(posixpath.dirname(directory), filename[:-5])


def internal_target(source, target):
    """Conservative package presence check, not a general OPC URI resolver."""
    try:
        if (not target or re.search(r"[\s\\\\\x00-\x1f\x7f]", target)
                or re.search(r"%(?![0-9a-fA-F]{2})", target)):
            return None
        uri = urlsplit(target)
        path = unquote(uri.path, errors="strict")
        if (uri.scheme or uri.netloc or uri.query or not path or path.startswith("//")
                or re.search(r"[\\\\\x00-\x1f\x7f]", path)):
            return None
        resolved = posixpath.normpath(path.lstrip("/") if path.startswith("/") else
                                     posixpath.join(posixpath.dirname(source), path))
        return None if resolved in (".", "..") or resolved.startswith("../") else resolved
    except (ValueError, UnicodeError):
        return None


def inventory(package, start=0, end=None, full=False, xml=False, hash_parts=False):
    """Bounded body summaries; XML and all-member hashing are opt-in."""
    manifest = []
    text_parts = set(package.text_parts(["all"]))
    for info in package.zip.infolist():
        entry = {"part": info.filename, "size": info.file_size,
                 "compressed_size": info.compress_size}
        if hash_parts:
            data = package.zip.read(info)
            entry["sha256"] = hashlib.sha256(data).hexdigest()
            if (info.filename.endswith(".rels") or info.filename == "word/styles.xml"
                    or info.filename in text_parts):
                package.parse(info.filename, data)
        manifest.append(entry)
    document = package.parse("word/document.xml")
    body = first(document, "body")
    if body is None:
        raise ValueError("Missing main document body")
    total = len(body)
    start = min(start, total)
    end = total if full else min(end if end is not None else start + BODY_LIMIT, total)
    elements = []
    for index in range(start, end):
        element = body[index]
        text, truncated = text_summary(element, full)
        entry = {"index": index, "kind": split_tag(element.tag)[1], "text": text,
                 "text_truncated": truncated,
                 "paragraph_count": len(descendants(element, "p")),
                 "table_count": len(descendants(element, "tbl"))}
        if xml:
            entry["xml"] = ET.tostring(element, encoding="unicode")
        elements.append(entry)
    styles = []
    if "word/styles.xml" in package.names:
        for style in children(package.parse("word/styles.xml"), "style"):
            styles.append({"styleId": attribute(style, "styleId"), "type": attribute(style, "type"),
                           "name": value(style, "name"), "basedOn": value(style, "basedOn"),
                           "default": attribute(style, "default")})
            if xml:
                styles[-1]["xml"] = ET.tostring(style, encoding="unicode")
    used = {}
    references = []
    sections = []
    for name in package.text_parts(["all"]):
        root = package.parse(name)
        used[name] = {kind: dict(Counter(attribute(e, "val") for e in descendants(root, kind)))
                      for kind in ("pStyle", "rStyle", "tblStyle")}
        for index, element in enumerate(root.iter()):
            for key, val in element.attrib.items():
                namespace, local = split_tag(key)
                if namespace in RELS and local in ("id", "embed", "link"):
                    references.append({"part": name, "element_index": index,
                                       "attribute": local, "id": val})
        for index, section in enumerate(descendants(root, "sectPr")):
            entry = {"part": name, "index": index, "properties": metadata(section)}
            if xml:
                entry["xml"] = ET.tostring(section, encoding="unicode")
            sections.append(entry)
    relationships = []
    for name in sorted(n for n in package.names if n.endswith(".rels")):
        source = relationship_source(name)
        for relationship in package.parse(name):
            entry = {"rels_part": name, "source_part": source, **relationship.attrib}
            target = entry.get("Target", "")
            if entry.get("TargetMode") == "External":
                entry["status"] = "external (not fetched)"
            else:
                resolved = internal_target(source, target)
                if entry.get("TargetMode", "Internal") != "Internal":
                    resolved = None
                entry["resolved_target"] = resolved
                entry["status"] = ("invalid internal target" if resolved is None else
                                   "present" if resolved in package.names else "missing")
            relationships.append(entry)
    by_source = {(entry["source_part"], entry.get("Id")) for entry in relationships}
    for reference in references:
        reference["relationship_present"] = (reference["part"], reference["id"]) in by_source
    return {"schema": "docx-inventory-v2", "limits": LIMITS,
            "detail": {"xml": xml, "hash_parts": hash_parts},
            "body_coverage": {"total": total, "start": start, "end": end,
                              "returned": len(elements), "complete": start == 0 and end == total,
                              "text_mode": "full" if full else "preview",
                              "text_limit": None if full else TEXT_LIMIT,
                              "expand": "--start N --end M for a range; --full for all elements/full text; --xml for XML"},
            "body_elements": elements, "sections": sections, "styles": styles,
            "used_styles": used, "relationships": relationships,
            "relationship_reference_scope": {"parts": sorted(used), "attributes": ["r:id", "r:embed", "r:link"]},
            "relationship_references": references, "parts": manifest}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest="mode", required=True)
    text = modes.add_parser("text", help="Whole stored body text by default, without .NET")
    text.add_argument("input", type=Path)
    text.add_argument("--part", action="append", help="body (default), headers, footers, footnotes, endnotes, comments, all, or exact XML part; repeatable")
    text.add_argument("--start", type=int, default=0, help="Body element start index (zero-based)")
    text.add_argument("--end", type=int, help="Body element end index (exclusive)")
    inspect = modes.add_parser("inventory", help="Concise JSON: bounded body, all styles/sections/relationships, cheap part sizes")
    inspect.add_argument("input", type=Path)
    inspect.add_argument("--start", type=int, default=0, help="Body start index (zero-based; default 0)")
    inspect.add_argument("--end", type=int, help="Body end index (exclusive; default start + 50)")
    inspect.add_argument("--full", action="store_true", help="All body elements and complete text; no implicit XML/hashes")
    inspect.add_argument("--xml", action="store_true", help="Include XML for selected body elements, all styles and sections")
    inspect.add_argument("--hash-parts", action="store_true", help="Read/hash every ZIP member once, including binary/media, for preservation")
    part = modes.add_parser("part", help="Print one serialized XML/rels part for inspection, not byte-preserving editing")
    part.add_argument("input", type=Path)
    part.add_argument("name", help="Exact member path, e.g. word/numbering.xml")
    args = parser.parse_args()
    if args.mode in ("text", "inventory"):
        if args.start < 0 or (args.end is not None and args.end < args.start):
            parser.error("range requires 0 <= --start <= --end")
        if args.mode == "text":
            if (args.start or args.end is not None) and args.part not in (None, ["body"]):
                parser.error("element ranges apply only to --part body")
        elif args.full and (args.start or args.end is not None):
            parser.error("--full cannot be combined with a body range")
    package = None
    try:
        package = Package(args.input)
        if args.mode == "text":
            print(LIMITS, file=sys.stderr)
            text_output(package, args.part or ["body"], args.start, args.end)
        elif args.mode == "inventory":
            print(json.dumps(inventory(package, args.start, args.end, args.full,
                                       args.xml, args.hash_parts), ensure_ascii=False, indent=2))
        else:
            print(ET.tostring(package.parse(args.name), encoding="unicode"))
    except (OSError, BadZipFile, KeyError, ValueError, ET.ParseError) as error:
        print(f"DOCX inspection failed: {error}", file=sys.stderr)
        return 1
    finally:
        if package is not None:
            package.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
