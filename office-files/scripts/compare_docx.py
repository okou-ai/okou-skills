#!/usr/bin/env python3
"""Compare an original and edited DOCX, including features hidden by PDF export.

Uses only the Python standard library. This is a conservative change inventory,
not OOXML schema validation or proof that an edit matches a user's request.
Intentional changes require individually scoped, hash-bound explanations.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import posixpath
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
from zipfile import BadZipFile, ZipFile


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
STRICT_W = "http://purl.oclc.org/ooxml/wordprocessingml/main"
STRICT_R = "http://purl.oclc.org/ooxml/officeDocument/relationships"
WORD_NAMESPACES = {W, STRICT_W}
REL_NAMESPACES = {R, STRICT_R}
CHANGE_KEYS = {"code", "part", "scope", "before_sha256", "after_sha256"}
REVISION_TAGS = {
    "ins", "del", "moveFrom", "moveTo", "moveFromRangeStart", "moveFromRangeEnd",
    "moveToRangeStart", "moveToRangeEnd", "customXmlInsRangeStart", "customXmlInsRangeEnd",
    "customXmlDelRangeStart", "customXmlDelRangeEnd", "customXmlMoveFromRangeStart",
    "customXmlMoveFromRangeEnd", "customXmlMoveToRangeStart", "customXmlMoveToRangeEnd",
    "rPrChange", "pPrChange", "sectPrChange", "tblPrChange", "tblGridChange",
    "trPrChange", "tcPrChange", "tblPrExChange", "cellIns", "cellDel", "cellMerge",
    "numberingChange",
}
FEATURE_TAGS = {
    "hyperlinks": {"hyperlink"},
    "comment_anchors": {"commentRangeStart", "commentRangeEnd", "commentReference"},
    "revisions": REVISION_TAGS,
    "fields": {"fldSimple", "fldChar", "instrText"},
    "header_footer_references": {"headerReference", "footerReference"},
    "drawings": {"drawing", "pict", "object"},
    "bookmarks": {"bookmarkStart", "bookmarkEnd"},
}


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fingerprint(path):
    path = Path(path).resolve(strict=True)
    return {"path": str(path), "sha256": sha256(path), "bytes": path.stat().st_size}


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, separators=(",", ":"),
                                    sort_keys=True).encode("utf-8")).hexdigest()


def split_tag(tag):
    if tag.startswith("{"):
        namespace, local = tag[1:].split("}", 1)
        return namespace, local
    return "", tag


def word_attribute(node, local):
    return next((node.get(f"{{{ns}}}{local}") for ns in WORD_NAMESPACES
                 if node.get(f"{{{ns}}}{local}") is not None), None)


def relationship_owner(part):
    if part == "_rels/.rels":
        return ""
    parent, filename = posixpath.split(part)
    if not parent.endswith("/_rels") or not filename.endswith(".rels"):
        raise ValueError(f"Invalid relationship part name: {part}")
    return posixpath.join(parent[:-6], filename[:-5])


def resolved_target(owner, target, mode):
    if mode == "External":
        return target
    url = urlsplit(target)
    if url.scheme or url.netloc:
        raise ValueError(f"Internal relationship has a non-package target: {target}")
    path = unquote(url.path)
    path = owner if not path else (path.lstrip("/") if path.startswith("/")
                                   else posixpath.join(posixpath.dirname(owner), path))
    path = posixpath.normpath(path)
    if path in (".", "..") or path.startswith("../"):
        raise ValueError(f"Relationship target escapes the package: {target}")
    return path + ("#" + url.fragment if url.fragment else "")


def canonical(node, relationships, *, omit_text=False):
    """Ignore XML serialization and relationship ID renumbering, not formatting."""
    attributes = []
    for name, value in sorted(node.attrib.items()):
        namespace, local = split_tag(name)
        if namespace in REL_NAMESPACES and local in {"id", "embed", "link"}:
            value = relationships.get(value, ("MISSING_RELATIONSHIP", value))
        attributes.append((name, value))
    text = None if omit_text else node.text
    if text is not None and not text.strip() and len(node):
        text = None  # Pretty-print indentation between child elements.
    tail = None if omit_text or not (node.tail or "").strip() else node.tail
    return [node.tag, attributes, text, tail,
            [canonical(child, relationships, omit_text=omit_text) for child in node]]


def text_payload(root):
    values = []

    def visit(node):
        if node.text is not None and (node.text.strip() or not len(node)):
            values.append(node.text)
        for child in node:
            visit(child)
        if node.tail is not None and node.tail.strip():
            values.append(node.tail)

    visit(root)
    return values


def read_package(path):
    with ZipFile(path) as archive:
        names = [name for name in archive.namelist() if not name.endswith("/")]
        if len(names) != len(set(names)):
            raise ValueError("Duplicate ZIP member names")
        if any(name.startswith("/") or posixpath.normpath(name) != name
               or name.startswith("../") or "\\" in name for name in names):
            raise ValueError("Non-canonical ZIP member path")
        parts = {name: archive.read(name) for name in names}
    for required in ("[Content_Types].xml", "_rels/.rels"):
        if required not in parts:
            raise ValueError(f"Missing package part: {required}")
    xml = {name: ET.fromstring(data) for name, data in parts.items()
           if name.endswith((".xml", ".rels"))}
    relationships, by_owner = {}, {}
    errors = []
    for name, root in xml.items():
        if not name.endswith(".rels"):
            continue
        owner = relationship_owner(name)
        if root.tag != f"{{{REL}}}Relationships":
            raise ValueError(f"Invalid relationships root: {name}")
        if owner and owner not in parts:
            errors.append((name, f"Relationship owner is missing: {owner}"))
        entries = {}
        for item in root:
            rel_id, rel_type, target = (item.get(key) for key in ("Id", "Type", "Target"))
            mode = item.get("TargetMode", "Internal")
            if (item.tag != f"{{{REL}}}Relationship" or not rel_id or not rel_type
                    or target is None or mode not in {"Internal", "External"}):
                raise ValueError(f"Invalid relationship record: {name}")
            if rel_id in entries:
                raise ValueError(f"Duplicate relationship ID {rel_id} in {name}")
            resolved = resolved_target(owner, target, mode)
            entries[rel_id] = (rel_type, resolved, mode)
            if mode == "Internal" and resolved.split("#", 1)[0] not in parts:
                errors.append((name, f"Missing relationship target: {resolved}"))
        relationships[name] = entries
        by_owner[owner] = entries
    document_targets = [target for kind, target, mode in by_owner.get("", {}).values()
                        if kind.endswith("/officeDocument") and mode == "Internal"]
    if len(document_targets) != 1 or document_targets[0] not in xml:
        errors.append(("_rels/.rels", "Package must reference one XML officeDocument part"))
    elif split_tag(xml[document_targets[0]].tag) not in {(ns, "document") for ns in WORD_NAMESPACES}:
        errors.append((document_targets[0], "The officeDocument part is not a Word document"))
    for name, root in xml.items():
        if name.endswith(".rels"):
            continue
        for node in root.iter():
            for attribute, value in node.attrib.items():
                namespace, local = split_tag(attribute)
                if (namespace in REL_NAMESPACES and local in {"id", "embed", "link"}
                        and value not in by_owner.get(name, {})):
                    errors.append((name, f"Referenced relationship ID is missing: {value}"))
    content_types = xml["[Content_Types].xml"]
    if content_types.tag != "{http://schemas.openxmlformats.org/package/2006/content-types}Types":
        errors.append(("[Content_Types].xml", "Invalid content-types root"))
    defaults = {node.get("Extension"): node.get("ContentType") for node in content_types
                if split_tag(node.tag)[1] == "Default"}
    overrides = {unquote(node.get("PartName", "")).lstrip("/"): node.get("ContentType")
                 for node in content_types if split_tag(node.tag)[1] == "Override"}
    for name in parts:
        if name != "[Content_Types].xml" and not (overrides.get(name) or defaults.get(name.rsplit(".", 1)[-1])):
            errors.append((name, "Package part has no content type"))
    for name in overrides:
        if name not in parts:
            errors.append(("[Content_Types].xml", f"Content type refers to missing part: {name}"))
    # Relationship and content-type element order has no meaning in OPC.
    content_types[:] = sorted(content_types, key=lambda node: (node.tag, sorted(node.attrib.items())))
    return {"parts": parts, "xml": xml, "relationships": relationships,
            "by_owner": by_owner, "errors": errors}


def features(package):
    result = {}
    for part, root in package["xml"].items():
        relationships = package["by_owner"].get(part, {})
        namespace, local = split_tag(root.tag)
        if namespace in WORD_NAMESPACES and local in {"hdr", "ftr", "comments"}:
            result[(part, {"hdr": "header", "ftr": "footer", "comments": "comments"}[local])] = canonical(root, relationships)
        for feature, tags in FEATURE_TAGS.items():
            matches = [canonical(node, relationships) for node in root.iter()
                       if split_tag(node.tag)[0] in WORD_NAMESPACES and split_tag(node.tag)[1] in tags]
            if matches:
                result[(part, feature)] = matches
    for part, data in package["parts"].items():
        if part.startswith("word/media/"):
            result[(part, "media")] = hashlib.sha256(data).hexdigest()
    return result


def feature_errors(package):
    """Check referenced comments and complex field boundaries in each story."""
    errors = []
    for part, root in package["xml"].items():
        comments = set()
        for kind, target, mode in package["by_owner"].get(part, {}).values():
            if kind.endswith("/comments") and mode == "Internal" and target in package["xml"]:
                comments.update(word_attribute(node, "id") for node in package["xml"][target].iter()
                                if split_tag(node.tag)[0] in WORD_NAMESPACES and split_tag(node.tag)[1] == "comment")
        field_stack = []
        starts, ends = Counter(), Counter()
        for node in root.iter():
            namespace, local = split_tag(node.tag)
            if namespace not in WORD_NAMESPACES:
                continue
            if local in {"commentRangeStart", "commentRangeEnd", "commentReference"}:
                comment_id = word_attribute(node, "id")
                if comment_id not in comments:
                    errors.append((part, f"Comment anchor has no related comment: {comment_id}"))
                if local == "commentRangeStart":
                    starts[comment_id] += 1
                elif local == "commentRangeEnd":
                    ends[comment_id] += 1
            if local == "fldChar":
                kind = word_attribute(node, "fldCharType")
                if kind == "begin":
                    field_stack.append(False)
                elif kind == "separate" and field_stack and not field_stack[-1]:
                    field_stack[-1] = True
                elif kind == "end" and field_stack:
                    field_stack.pop()
                else:
                    errors.append((part, f"Unmatched or invalid complex-field boundary: {kind}"))
        if starts != ends:
            errors.append((part, "Comment range starts and ends do not match"))
        if field_stack:
            errors.append((part, "Unclosed complex field"))
    return errors


def read_policy(path):
    if path is None:
        return []
    policy = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(policy, dict) or set(policy) != {"schema_version", "changes"} or policy["schema_version"] != 1:
        raise ValueError("Changes policy needs schema_version: 1 and a changes list only")
    if not isinstance(policy["changes"], list):
        raise ValueError("Policy changes must be a list")
    seen = set()
    for change in policy["changes"]:
        if not isinstance(change, dict) or set(change) != CHANGE_KEYS | {"reason"}:
            raise ValueError("Each change needs code, part, scope, before_sha256, after_sha256 and reason")
        for key in ("code", "part", "scope"):
            if not isinstance(change[key], str) or not change[key].strip() or any(c in change[key] for c in "*?[]"):
                # [Content_Types].xml is an exact OPC filename, not a glob.
                if key != "part" or change[key] != "[Content_Types].xml":
                    raise ValueError(f"Policy {key} must identify one exact change; wildcards are not allowed")
        for key in ("before_sha256", "after_sha256"):
            value = change[key]
            if value is not None and (not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value)):
                raise ValueError(f"Policy {key} must be a lowercase SHA-256 or null")
        reason = change["reason"]
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError("Each intentional change needs a concrete, task-specific reason")
        if reason.strip().lower().rstrip(".。") in {"all changes approved", "approve all changes", "expected changes", "intentional change", "approved", "全部批准", "所有修改已批准"}:
            raise ValueError("Blanket approval reasons are not allowed")
        key = tuple(change[field] for field in sorted(CHANGE_KEYS))
        if key in seen:
            raise ValueError("Duplicate policy change")
        seen.add(key)
    return policy["changes"]


def validate_binding(report):
    """Raise if any compared input or its policy changed after comparison."""
    if report.get("schema_version") != 1 or report.get("status") != "PASS":
        raise ValueError("DOCX comparison must have schema_version 1 and status PASS")
    inputs = report.get("inputs", {})
    for required in ("original", "edited"):
        if not isinstance(inputs.get(required), dict):
            raise ValueError(f"Comparison lacks its {required} fingerprint")
    for name, expected in inputs.items():
        if expected is not None:
            actual = fingerprint(expected["path"])
            if actual["sha256"] != expected["sha256"] or actual["bytes"] != expected["bytes"]:
                raise ValueError(f"The comparison {name} changed; compare again")
    if any(item.get("severity") == "blocker" for item in report.get("findings", [])):
        raise ValueError("DOCX comparison still has blocking findings")
    return True


def compare(original, edited, changes=None, strict_bytes=False):
    if Path(original).resolve() == Path(edited).resolve():
        raise ValueError("Keep the original unchanged and compare it with a separate edited file")
    inputs = {"original": fingerprint(original), "edited": fingerprint(edited),
              "changes": fingerprint(changes) if changes else None}
    policy = read_policy(changes)
    used = set()
    report = {"schema_version": 1, "status": "BLOCKED", "compared_at": datetime.now(timezone.utc).isoformat(),
              "inputs": inputs, "strict_bytes": bool(strict_bytes), "parts": [], "features": [], "findings": [],
              "limitations": ["This inventories changes and checks references; it is not full OOXML schema validation.",
                              "Approval reasons require human or agent judgment against the request.",
                              "Compare renderings and inspect every page; a PDF does not show all comments or revisions."]}

    def finding(code, part, scope, before=None, after=None, *, severity="blocker", evidence=None, approvable=True):
        item = {"code": code, "part": part, "scope": scope,
                "before_sha256": digest(before) if before is not None else None,
                "after_sha256": digest(after) if after is not None else None}
        item["id"] = "change-" + digest(item)[:16]
        item["severity"] = severity
        if evidence is not None:
            item["evidence"] = evidence
        if severity == "blocker" and approvable:
            for index, change in enumerate(policy):
                if all(item[key] == change[key] for key in CHANGE_KEYS):
                    item["severity"] = "info"
                    item["approval_reason"] = change["reason"].strip()
                    used.add(index)
                    break
        report["findings"].append(item)

    try:
        before, after = read_package(original), read_package(edited)
    except (ValueError, BadZipFile, ET.ParseError, KeyError) as error:
        finding("invalid_package", "package", "integrity", evidence=str(error), approvable=False)
        before = after = None
    if before is not None:
        for side, package in (("original", before), ("edited", after)):
            for part, error in package["errors"] + feature_errors(package):
                finding("invalid_reference", part, side, evidence=error, approvable=False)
        for part in sorted(before["parts"].keys() | after["parts"].keys()):
            left, right = before["parts"].get(part), after["parts"].get(part)
            left_hash = hashlib.sha256(left).hexdigest() if left is not None else None
            right_hash = hashlib.sha256(right).hexdigest() if right is not None else None
            report["parts"].append({"part": part, "before_sha256": left_hash, "after_sha256": right_hash})
            if left == right:
                continue
            old_rel, new_rel = before["relationships"].get(part), after["relationships"].get(part)
            empty_rel_delta = part.endswith(".rels") and ((old_rel == {} and right is None) or (new_rel == {} and left is None))
            if empty_rel_delta:
                finding("empty_relationship_part", part, "package", left_hash, right_hash, severity="info")
            elif left is None or right is None:
                finding("part_added" if left is None else "part_removed", part, "package", left_hash, right_hash)
            if strict_bytes and not empty_rel_delta and left is not None and right is not None:
                finding("part_bytes_changed", part, "bytes", left_hash, right_hash)
            if part.endswith(".rels"):
                old_items = Counter(tuple(value) for value in (old_rel or {}).values())
                new_items = Counter(tuple(value) for value in (new_rel or {}).values())
                for relationship in sorted(old_items.keys() | new_items.keys()):
                    if old_items[relationship] != new_items[relationship]:
                        finding("relationship_changed", part, "relationship:" + digest(relationship),
                                {"relationship": relationship, "count": old_items[relationship]} if old_items[relationship] else None,
                                {"relationship": relationship, "count": new_items[relationship]} if new_items[relationship] else None,
                                evidence={"type": relationship[0], "target": relationship[1], "mode": relationship[2]})
                if old_items == new_items and not empty_rel_delta and left is not None and right is not None:
                    finding("xml_serialization_only", part, "serialization", left_hash, right_hash, severity="info")
                continue
            if left is None or right is None:
                continue
            if part in before["xml"] and part in after["xml"]:
                old_xml, new_xml = before["xml"][part], after["xml"][part]
                old_rels, new_rels = before["by_owner"].get(part, {}), after["by_owner"].get(part, {})
                old_tree, new_tree = canonical(old_xml, old_rels), canonical(new_xml, new_rels)
                if old_tree == new_tree:
                    finding("xml_serialization_only", part, "serialization", left_hash, right_hash, severity="info")
                    continue
                old_text, new_text = text_payload(old_xml), text_payload(new_xml)
                if old_text != new_text:
                    finding("text_changed", part, "text", old_text, new_text,
                            evidence={"before": old_text, "after": new_text})
                old_structure = canonical(old_xml, old_rels, omit_text=True)
                new_structure = canonical(new_xml, new_rels, omit_text=True)
                if old_structure != new_structure:
                    finding("xml_structure_changed", part, "structure", old_structure, new_structure)
            else:
                finding("part_content_changed", part, "content", left_hash, right_hash)
        old_features, new_features = features(before), features(after)
        for key in sorted(old_features.keys() | new_features.keys()):
            old_value, new_value = old_features.get(key), new_features.get(key)
            report["features"].append({"part": key[0], "scope": key[1],
                                       "before_sha256": digest(old_value) if old_value is not None else None,
                                       "after_sha256": digest(new_value) if new_value is not None else None})
            if old_value != new_value:
                finding("feature_changed", *key, old_value, new_value)
    for index in set(range(len(policy))) - used:
        finding("unused_policy_change", policy[index]["part"], policy[index]["scope"],
                evidence={"policy_index": index, "reason": "No current blocking change matches this approval"}, approvable=False)
    for name, expected in inputs.items():
        if expected is not None and fingerprint(expected["path"]) != expected:
            finding("input_changed_during_comparison", "package", name, approvable=False)
    report["summary"] = {"parts": len(report["parts"]),
                         "blockers": sum(item["severity"] == "blocker" for item in report["findings"]),
                         "approved_changes": len(used),
                         "informational": sum(item["severity"] == "info" for item in report["findings"])}
    if not report["summary"]["blockers"]:
        report["status"] = "PASS"
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path)
    parser.add_argument("edited", type=Path)
    parser.add_argument("--out", required=True, type=Path, help="Write the hash-bound comparison JSON")
    parser.add_argument("--changes", type=Path, help="Exact intentional changes and task-specific reasons")
    parser.add_argument("--strict-bytes", action="store_true", help="For focused OOXML edits, also require approval of each changed part's bytes")
    args = parser.parse_args()
    try:
        if args.out.resolve() in {path.resolve() for path in (args.original, args.edited, args.changes) if path}:
            raise ValueError("Comparison output must not overwrite an input")
        args.out.unlink(missing_ok=True)
        report = compare(args.original, args.edited, args.changes, args.strict_bytes)
        args.out.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.out.with_suffix(args.out.suffix + ".tmp")
        temporary.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        temporary.replace(args.out)
        print(json.dumps({"status": report["status"], "report": str(args.out.resolve()), **report["summary"]}))
        return 0 if report["status"] == "PASS" else 1
    except (OSError, ValueError) as error:
        print(f"DOCX comparison failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
