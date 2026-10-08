#!/usr/bin/env python3
"""Inspect final PDF pages and record explicit, artifact-bound visual review.

The measurements below are deliberately conservative. They cannot judge design,
prove that somebody opened the PNGs, or validate Word's pagination. Acceptance is
a local review record, not an attestation: run ``accept`` again before delivery.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import unicodedata
import xml.etree.ElementTree as ET
import zipfile

import pymupdf


CRITERIA = (
    "legibility_and_density",
    "hierarchy",
    "composition_and_rhythm",
    "pagination_and_grouping",
    "tables_and_figures",
)
LIMITATIONS = [
    "Measurements are heuristics, not visual acceptance. Open every page PNG.",
    "Text extraction cannot detect every missing glyph, clipping path, or overlap.",
    "Expectations check text presence, not semantic equality: matching ignores "
    "whitespace and soft hyphens and normalizes Unicode compatibility forms "
    "(including ligatures). required_text may span pages; same_page may not.",
    "A paired DOCX is hash-bound and structurally checked; its Word pagination "
    "is not verified. Supply a PDF exported from that exact DOCX.",
    "When --render is supplied, its successful render snapshot, source, "
    "reference and declared resources must remain unchanged. This is local "
    "reproducibility evidence, not authentication of the renderer.",
    "Acceptance is a local snapshot, not tamper-proof evidence or proof of image "
    "viewing. Rerun accept immediately before delivering these exact files.",
    "When content review is required, acceptance checks its declared status and "
    "observation against this exact inspection. It does not prove factual "
    "correctness or that the reviewer was independent.",
]


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fingerprint(path):
    path = Path(path).resolve(strict=True)
    return {"path": str(path), "sha256": sha256(path), "bytes": path.stat().st_size}


def write_json(path, data):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def normalize(text):
    return "".join(unicodedata.normalize("NFKC", text).replace("\u00ad", "").split())


def read_expectations(path):
    if path is None:
        return {"required_text": [], "same_page": [], "not_applicable": {}}
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or set(data) - {"required_text", "same_page", "not_applicable"}:
        raise ValueError("Expectations must contain only required_text, same_page and not_applicable.")
    required = data.get("required_text", [])
    pairs = data.get("same_page", [])
    if not isinstance(required, list) or any(not isinstance(t, str) or not normalize(t) for t in required):
        raise ValueError("required_text must be a list of nonempty strings.")
    if not isinstance(pairs, list):
        raise ValueError("same_page must be a list.")
    for pair in pairs:
        if not isinstance(pair, dict) or set(pair) != {"first", "second", "reason"}:
            raise ValueError("Each same_page item needs first, second, and reason.")
        if any(not isinstance(pair[k], str) or not normalize(pair[k]) for k in pair):
            raise ValueError("same_page fields must be nonempty strings.")
    exemptions = data.get("not_applicable", {})
    if (not isinstance(exemptions, dict) or set(exemptions) - {"required_text", "same_page"} or
            any(not isinstance(reason, str) or not normalize(reason) for reason in exemptions.values())):
        raise ValueError("not_applicable must give a nonempty reason for required_text or same_page.")
    if any(data.get(key) for key in exemptions):
        raise ValueError("An expectation cannot have both entries and a not_applicable reason.")
    return {"required_text": required, "same_page": pairs, "not_applicable": exemptions}


def add_finding(report, severity, code, message, page=None, evidence=None):
    finding = {
        "id": f"finding-{len(report['findings']) + 1:03d}",
        "severity": severity,
        "code": code,
        "page": page,
        "message": message,
    }
    if evidence is not None:
        finding["evidence"] = evidence
    report["findings"].append(finding)


def inspect_expectations(report, texts, expectations):
    for key in ("required_text", "same_page"):
        if not expectations[key] and not expectations["not_applicable"].get(key):
            add_finding(report, "blocker", "empty_" + key,
                        f"Add task-specific {key} expectations, or explain why they do not apply.")
    normalized_pages = [normalize(text) for text in texts]

    def occurrences(phrase):
        needle = normalize(phrase)
        return [i + 1 for i, text in enumerate(normalized_pages) for _ in range(text.count(needle))]

    for phrase in expectations["required_text"]:
        if normalize(phrase) not in "".join(normalized_pages):
            add_finding(report, "blocker", "required_text_missing", "Required text was not found in the PDF's extracted text.", evidence={"text": phrase})
    for pair in expectations["same_page"]:
        first, second = occurrences(pair["first"]), occurrences(pair["second"])
        evidence = {**pair, "first_pages": first, "second_pages": second}
        if not first or not second:
            add_finding(report, "blocker", "relationship_text_missing", "A same-page relationship cannot be checked because its text is missing.", evidence=evidence)
        elif len(first) != 1 or len(second) != 1:
            add_finding(report, "warning", "ambiguous_relationship", "Repeated text makes this same-page relationship ambiguous. Check its intended occurrences visually or use more specific snippets.", evidence=evidence)
        elif first != second:
            add_finding(report, "blocker", "split_relationship", "Text explicitly required to stay together is on different pages.", evidence=evidence)


def visible_spans(page):
    """Trace boxes are tighter than text-dictionary ascender/descender boxes."""
    spans = []
    seen = set()
    for trace in page.get_texttrace():
        if trace["type"] == 3 or trace.get("opacity", 1) <= 0:
            continue  # Ignore explicitly invisible text, e.g. an OCR layer.
        text = "".join(chr(char[0]) for char in trace["chars"])
        if not text.strip():
            continue
        box = pymupdf.Rect(trace["bbox"])
        if box.is_empty:
            continue  # Zero-advance marks / ActualText placeholders have no box.
        key = (text, tuple(round(value, 2) for value in box))
        if key in seen:
            continue  # Fill-and-stroke text is not two overlapping text runs.
        seen.add(key)
        spans.append({"text": text, "box": box, "size": trace["size"], "direction": trace["dir"], "chars": trace["chars"]})
    return spans


def extracted_page_text(page):
    """Preserve logical RTL order and multi-character glyph mappings.

    MuPDF's geometric text sorting reverses RTL words. Its default extraction
    also reverses the characters *within* expanded RTL ligatures. A glyph ID of
    -1 explicitly identifies continuation characters in such a mapping. Keep
    those characters together when reversing a purely RTL trace, and apply the
    correction only inside the text span that contains that trace's geometry.
    Mixed-direction runs keep MuPDF's extraction; no words are guessed.
    """
    corrections = []
    for trace in page.get_texttrace():
        chars = trace["chars"]
        text = "".join(chr(char[0]) for char in chars)
        directions = {unicodedata.bidirectional(char) for char in text}
        if not ({"R", "AL"} & directions) or {"L", "EN", "AN"} & directions:
            continue
        if not any(char[1] == -1 for char in chars):
            continue
        clusters = []
        for codepoint, glyph, *_ in chars:
            if glyph == -1 and clusters:
                clusters[-1] += chr(codepoint)
            else:
                clusters.append(chr(codepoint))
        original, corrected = text[::-1], "".join(reversed(clusters))
        if original != corrected:
            corrections.append((pymupdf.Rect(trace["bbox"]), original, corrected))
    lines = []
    flags = pymupdf.TEXTFLAGS_DICT & ~pymupdf.TEXT_PRESERVE_IMAGES
    for block in page.get_text("dict", flags=flags, sort=False)["blocks"]:
        for line in block.get("lines", []):
            parts = []
            for span in line["spans"]:
                text = span["text"]
                box = pymupdf.Rect(span["bbox"]) + (-0.5, -0.5, 0.5, 0.5)
                for trace_box, original, corrected in corrections:
                    if box.contains(trace_box) and original in text:
                        text = text.replace(original, corrected, 1)
                parts.append(text)
            lines.append("".join(parts))
    return "\n".join(lines).strip()


def inspect_page(report, page, out):
    number = page.number + 1
    bounds = page.rect * page.derotation_matrix
    spans = visible_spans(page)
    # Expectations use page-bounded extraction: entirely off-page text must not
    # satisfy a required phrase. The traces above still expose edge clipping.
    text = extracted_page_text(page)
    pixmap = page.get_pixmap(matrix=pymupdf.Matrix(2, 2), alpha=False)
    image_name = f"page-{number:03d}.png"
    pixmap.save(out / image_name)
    dominant_ratio, dominant_color = pixmap.color_topusage()
    # Warm paper backgrounds are intentionally below RGB 250. A nearly uniform
    # page with no visible text is still blank regardless of paper colour.
    blank = dominant_ratio > 0.99999 and not spans
    clipped = []
    off_page = []
    for span in spans:
        if not span["box"].intersects(bounds):
            off_page.append(span["text"][:100])
            continue
        for codepoint, _, _, coordinates in span["chars"]:
            if chr(codepoint).isspace():
                continue
            box = pymupdf.Rect(coordinates)
            if box.is_empty:
                continue
            # Font metrics are not exact ink outlines. Require both a material
            # distance and a large lost fraction before treating it as clipping.
            outside = 1 - (box & bounds).get_area() / box.get_area()
            distance = max(bounds.x0 - box.x0, bounds.y0 - box.y0, box.x1 - bounds.x1, box.y1 - bounds.y1)
            if outside > 0.25 and distance > 1:
                clipped.append({"text": span["text"][:100], "bbox": list(span["box"])})
                break
    if clipped:
        add_finding(report, "blocker", "clipped_text", "Visible text geometry extends materially outside the page boundary.", number, clipped[:5])
    if off_page:
        add_finding(report, "warning", "off_page_text", "Text runs lie wholly outside the page; verify that this is intentional and no content is lost.", number, off_page[:5])
    if "\ufffd" in text or "\x00" in text:
        add_finding(report, "warning", "replacement_glyph", "Extracted text contains replacement or null characters; check for missing glyphs in the rendered page.", number)

    small = [span for span in spans if span["size"] < 8]
    if sum(len(span["text"].strip()) for span in small) >= 40 or any(len(span["text"].strip()) >= 20 for span in small):
        add_finding(report, "warning", "small_text", "Substantial text is smaller than 8 pt; check readability at normal viewing size.", number, {"min_font_pt": round(min(s["size"] for s in small), 2)})
    overlaps = []
    horizontal = sorted((s for s in spans if s["direction"] == (1, 0)), key=lambda s: s["box"].y0)
    for index, first in enumerate(horizontal):
        if len(overlaps) >= 5:
            break
        for second in horizontal[index + 1:]:
            if len(overlaps) >= 5 or second["box"].y0 >= first["box"].y1:
                break
            if min(first["size"], second["size"]) <= 0 or max(first["size"], second["size"]) / min(first["size"], second["size"]) > 1.25:
                continue  # Superscripts and subscripts commonly share a box.
            intersection = first["box"] & second["box"]
            minimum_area = min(first["box"].get_area(), second["box"].get_area())
            if minimum_area > 0 and intersection.get_area() / minimum_area > 0.35:
                overlaps.append([first["text"][:80], second["text"][:80]])
    if overlaps:
        add_finding(report, "warning", "possible_text_overlap", "Text boxes overlap substantially. Check whether this is intentional typography or unreadable content.", number, overlaps)

    coverage = min(1, sum((s["box"] & bounds).get_area() for s in spans) / max(1, bounds.get_area()))
    has_graphics = bool(page.get_images() or page.get_drawings())
    if blank:
        add_finding(report, "warning", "blank_page", "This page appears blank; verify that the blank page is intentional.", number)
    elif not text:
        add_finding(report, "warning", "no_extractable_text", "This page has no extractable text. Inspect all text and diagrams visually; text expectations cannot validate it.", number)
    elif coverage < 0.06 and len(text) < 350 and not has_graphics:
        add_finding(report, "warning", "sparse_page", "This page contains little text; check for an accidental page break or an intentional short page.", number)
    if coverage > 0.5 or len(text) / max(1, bounds.get_area()) > 0.01:
        add_finding(report, "warning", "dense_page", "High text density may impair reading; inspect spacing and hierarchy.", number)
    report["pages"].append({
        "number": number,
        "image": {"path": image_name, "sha256": sha256(out / image_name)},
        "width_pt": round(page.rect.width, 2),
        "height_pt": round(page.rect.height, 2),
        "text_characters": len(text),
        "min_font_pt": round(min((s["size"] for s in spans), default=0), 2),
        "text_box_area_ratio": round(coverage, 4),
        "appears_blank": blank,
    })
    return text


def validate_docx(path):
    with zipfile.ZipFile(path) as archive:
        ET.fromstring(archive.read("[Content_Types].xml"))
        document = ET.fromstring(archive.read("word/document.xml"))
        if document.tag != "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}document":
            raise ValueError("Missing Word document root.")


def bind_render_manifest(report, path):
    """Bind the renderer's complete success snapshot, including editable input.

    Bad snapshots become findings so the actual PDF pages remain available for
    diagnosis. Both Word exports and native PDF candidates can have a manifest.
    """
    inputs = report["inputs"]
    try:
        inputs["render_manifest"] = fingerprint(path)
        manifest = json.loads(Path(path).read_text(encoding="utf-8"))
        require(isinstance(manifest, dict), "The render manifest must be an object.")
        if manifest.get("status") != "needs-inspection":
            add_finding(report, "blocker", "render_not_ready", "The current render manifest does not describe a completed render.", evidence={"status": manifest.get("status")})
            return

        def bind(name, item, output=False):
            require(isinstance(item, dict), f"Manifest {name} must contain a path and sha256.")
            require(isinstance(item.get("path"), str) and bool(item["path"]), f"Manifest {name} has no valid path.")
            digest = item.get("sha256")
            require(isinstance(digest, str) and len(digest) == 64 and all(c in "0123456789abcdefABCDEF" for c in digest), f"Manifest {name} has no valid SHA-256.")
            declared_path = Path(item["path"])
            if not declared_path.is_absolute():
                declared_path = Path(path).resolve().parent / declared_path
            actual = fingerprint(declared_path)
            if output and name in inputs:
                require(actual["path"] == inputs[name]["path"], f"Manifest {name} is not the inspected {name} path.")
                require(actual["sha256"] == inputs[name]["sha256"], f"The inspected {name} changed while binding its manifest.")
            inputs[name] = actual
            require(actual["sha256"] == digest.lower(), f"Manifest {name} does not match the current file; render again.")

        outputs = manifest.get("outputs")
        require(isinstance(outputs, dict) and "pdf" in outputs and
                set(outputs).issubset({"pdf", "docx"}),
                "The render manifest must declare a PDF and, when present, its paired DOCX.")
        require("docx" not in inputs or "docx" in outputs,
                "The paired DOCX is absent from the render manifest.")
        bind("pdf", outputs["pdf"], output=True)
        if "docx" in outputs:
            bind("docx", outputs["docx"], output=True)
        bind("source", manifest.get("source"))
        if manifest.get("reference") is not None:
            bind("reference", manifest["reference"])
        resources = manifest.get("resources", [])
        require(isinstance(resources, list), "Manifest resources must be a list.")
        for number, resource in enumerate(resources, start=1):
            bind(f"resource_{number:03d}", resource)
    except (OSError, ValueError, KeyError, TypeError) as error:
        add_finding(report, "blocker", "invalid_render_manifest", f"The render snapshot cannot be verified: {error}")


def bind_docx_comparison(report, path):
    """Require a successful comparison of the exact edited Word package."""
    try:
        from compare_docx import validate_binding

        report["inputs"]["docx_comparison"] = fingerprint(path)
        comparison = json.loads(Path(path).read_text(encoding="utf-8"))
        validate_binding(comparison)
        require("docx" in report["inputs"], "A Word comparison needs the paired --docx.")
        bound = comparison["inputs"]
        require(isinstance(bound, dict) and {"original", "edited"} <= set(bound),
                "Word comparison must bind the original and edited documents.")
        for name, item in bound.items():
            if item is None:
                continue
            require(isinstance(item, dict) and isinstance(item.get("path"), str), "Invalid Word comparison input.")
            current = fingerprint(item["path"])
            require(current["sha256"] == item["sha256"],
                    f"The comparison's {name} changed; compare and inspect again.")
            report["inputs"]["comparison_" + name] = current
        require(bound["edited"]["sha256"] == report["inputs"]["docx"]["sha256"],
                "The compared Word document is not the inspected Word document.")
    except (OSError, ValueError, KeyError, TypeError) as error:
        add_finding(report, "blocker", "invalid_docx_comparison", str(error))


def quick(pdf, expectations, docx=None, render=None, docx_comparison=None):
    """Check text/relationships and input bindings without producing page images."""
    inputs = {"pdf": fingerprint(pdf), "expectations": fingerprint(expectations)}
    if docx:
        inputs["docx"] = fingerprint(docx)
    expected = read_expectations(expectations)
    report = {"status": "QUICK_CHECK_ONLY", "inputs": inputs,
              "expectations": expected, "page_count": 0, "findings": []}
    if render:
        bind_render_manifest(report, render)
    if docx_comparison:
        bind_docx_comparison(report, docx_comparison)
    if "docx" in inputs:
        validate_docx(inputs["docx"]["path"])
    with pymupdf.open(pdf) as document:
        require(document.is_pdf and not document.needs_pass and len(document) > 0,
                "Expected a nonempty, unencrypted PDF.")
        report["page_count"] = len(document)
        inspect_expectations(report, [extracted_page_text(page) for page in document], expected)
    for name, item in inputs.items():
        require(sha256(item["path"]) == item["sha256"], f"Input {name} changed during the quick check.")
    report["passed"] = not any(f["severity"] == "blocker" for f in report["findings"])
    report["next"] = "Run inspect and review every final page before accept. This command does not approve delivery."
    return report


def inspect(pdf, out, docx=None, expectations=None, render=None, docx_comparison=None,
            review_format="verbose", content_review=None):
    require(review_format in {"verbose", "compact"}, "Review format must be verbose or compact.")
    require(content_review in {None, "author", "independent"},
            "Content review must be author or independent when requested.")
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    (out / "acceptance.json").unlink(missing_ok=True)
    for old_page in out.glob("page-*.png"):
        if old_page.stem[5:].isdigit():
            old_page.unlink()
    inputs = {"pdf": fingerprint(pdf)}
    if docx:
        inputs["docx"] = fingerprint(docx)
    if expectations:
        inputs["expectations"] = fingerprint(expectations)
    expected = read_expectations(expectations)
    report = {"schema_version": 2, "created_at": datetime.now(timezone.utc).isoformat(), "inputs": inputs, "expectations": expected, "page_count": 0, "pages": [], "findings": [], "limitations": LIMITATIONS}
    if content_review:
        report["content_review"] = content_review
    if not expectations:
        add_finding(report, "blocker", "missing_expectations", "Supply --expectations with task-specific checks or explicit not-applicable reasons.")
    if render:
        bind_render_manifest(report, render)
    if docx_comparison:
        bind_docx_comparison(report, docx_comparison)
    if "docx" in inputs:
        try:
            validate_docx(inputs["docx"]["path"])
        except (OSError, ValueError, KeyError, zipfile.BadZipFile, ET.ParseError) as error:
            add_finding(report, "blocker", "invalid_docx", f"The paired DOCX is unreadable or structurally invalid: {error}")
    try:
        with pymupdf.open(pdf) as document:
            if not document.is_pdf or document.needs_pass:
                raise ValueError("Expected an unencrypted, readable PDF.")
            report["page_count"] = len(document)
            texts = [inspect_page(report, page, out) for page in document]
            if not texts or all(page["appears_blank"] for page in report["pages"]):
                add_finding(report, "blocker", "empty_pdf", "The PDF has no visible page content.")
            inspect_expectations(report, texts, expected)
    except (RuntimeError, ValueError, OSError) as error:
        add_finding(report, "blocker", "unreadable_pdf", f"The PDF could not be completely inspected: {error}")
    for name, item in inputs.items():
        try:
            require(sha256(item["path"]) == item["sha256"], "The file changed.")
        except (OSError, ValueError) as error:
            add_finding(report, "blocker", "input_changed_during_inspection", f"Input {name} changed while inspection was running; inspect again. {error}")
    write_json(out / "inspection.json", report)
    review = {
        "schema_version": 2,
        "inspection_sha256": sha256(out / "inspection.json"),
        "instructions": "Open every PNG. Check all five criteria on every page; set each to pass only after checking it (fail or pending cannot pass acceptance). Record a concise page observation covering the checks, including absent tables/figures, or use separate observations per criterion. Explain each warning. If you repair a file, run inspect again and review the new images.",
        "pages": [{"number": page["number"], "image_sha256": page["image"]["sha256"],
                   "criteria": {name: "pending" if review_format == "compact" else
                                {"status": "pending", "observations": ""} for name in CRITERIA},
                   **({"observations": ""} if review_format == "compact" else {})}
                  for page in report["pages"]],
        "warning_acknowledgements": [{"finding_id": finding["id"], "observations": ""} for finding in report["findings"] if finding["severity"] == "warning"],
    }
    if content_review:
        review["content"] = {"status": "pending", "reviewer": content_review,
                             "observations": ""}
        review["instructions"] += (
            " Complete the content check against the request and supplied material "
            "using the required reviewer mode. Record a concrete observation about "
            "coverage, consistency or corrected issues; a bare pass is insufficient. "
            "Set content.status to pass only after checking the final content.")
    write_json(out / "review.json", review)
    if report["pages"] and len(report["pages"]) == report["page_count"]:
        from page_gallery import build_gallery

        build_gallery(out)
    return report


def require(condition, message):
    if not condition:
        raise ValueError(message)


def validate_content_review(report, review):
    """Check a declared review bound by inspection_sha256, not its truthfulness."""
    if "content_review" not in report:
        return None  # Older/native inspections keep their opt-in behavior.
    mode = report["content_review"]
    require(mode in {"author", "independent"},
            "The inspection has an invalid content review mode; inspect again.")
    content = review.get("content")
    require(isinstance(content, dict), "Complete the required content review.")
    require(content.get("reviewer") == mode,
            f"Content review must use the inspection's required {mode} reviewer mode.")
    require(content.get("status") == "pass", "Content review is not passed.")
    observations = content.get("observations")
    # Reject empty/punctuation-only text and bare acknowledgements. Specificity
    # and correctness still require the reviewer; this is not semantic scoring.
    words = "".join(char for char in observations.casefold() if char.isalnum()) if isinstance(observations, str) else ""
    require(bool(words) and words not in {
        "pass", "passed", "ok", "okay", "done", "checked", "complete",
        "completed", "good", "none", "na", "noissues", "allgood",
        "通过", "已通过", "已检查", "检查通过", "完成", "已完成", "无问题",
    }, "Content review needs a concrete observation, not a blank or bare acknowledgement.")
    return content


def accept(out):
    out = Path(out).resolve()
    # A failed recheck must not leave an earlier success record behind.
    (out / "acceptance.json").unlink(missing_ok=True)
    inspection_path, review_path = out / "inspection.json", out / "review.json"
    report = json.loads(inspection_path.read_text(encoding="utf-8"))
    review = json.loads(review_path.read_text(encoding="utf-8"))
    require(report["schema_version"] == review["schema_version"] == 2, "Inspect again with the current verifier; older reviews do not cover required expectations.")
    require(review["inspection_sha256"] == sha256(inspection_path), "The inspection changed after the review was created. Inspect and review again.")
    require("pdf" in report["inputs"], "The inspection has no bound PDF.")
    require("expectations" in report["inputs"], "The inspection has no bound expectations.")
    for name, item in report["inputs"].items():
        require(sha256(item["path"]) == item["sha256"], f"The {name} changed after inspection. Inspect and review again.")
    blockers = [finding["code"] for finding in report["findings"] if finding["severity"] == "blocker"]
    require(not blockers, f"Unresolved machine blockers: {', '.join(blockers)}")
    content = validate_content_review(report, review)
    pages = report["pages"]
    require(len(pages) == report["page_count"] > 0, "Inspection did not cover every page.")
    require([page["number"] for page in pages] == list(range(1, len(pages) + 1)), "Inspection page order is invalid.")
    require(len(review["pages"]) == len(pages), "Visual review must cover every page exactly once.")
    by_number = {page["number"]: page for page in review["pages"]}
    require(set(by_number) == set(range(1, len(pages) + 1)), "Visual review has missing or duplicate page numbers.")
    image_hashes = {}
    for page in pages:
        number = page["number"]
        name = f"page-{number:03d}.png"
        require(page["image"]["path"] == name, f"Unexpected image path for page {number}.")
        digest = sha256(out / name)
        require(digest == page["image"]["sha256"] == by_number[number]["image_sha256"], f"Page {number}'s image changed; inspect and review again.")
        image_hashes[name] = digest
        criteria = by_number[number]["criteria"]
        require(set(criteria) == set(CRITERIA), f"Page {number} must address all five visual criteria.")
        for criterion, result in criteria.items():
            # Compact records share a page observation but still require an
            # explicit status for every criterion. No omitted/default passes.
            status = result if isinstance(result, str) else result.get("status")
            observations = by_number[number].get("observations") if isinstance(result, str) else result.get("observations")
            require(status == "pass" and isinstance(observations, str) and bool(observations.strip()), f"Page {number}: {criterion} needs a passed review with observations.")
    warnings = {finding["id"] for finding in report["findings"] if finding["severity"] == "warning"}
    acknowledgements = review["warning_acknowledgements"]
    require(len(acknowledgements) == len(warnings) and {item["finding_id"] for item in acknowledgements} == warnings, "Acknowledge each warning exactly once.")
    require(all(isinstance(item["observations"], str) and item["observations"].strip() for item in acknowledgements), "Every warning needs an explanation based on the rendered pages.")
    acceptance = {
        "schema_version": 2,
        "status": "READY_TO_DELIVER",
        "accepted_at": datetime.now(timezone.utc).isoformat(),
        "inputs": report["inputs"],
        "inspection_sha256": sha256(inspection_path),
        "review_sha256": sha256(review_path),
        "page_image_sha256": image_hashes,
        "limitations": LIMITATIONS,
    }
    if content is not None:
        acceptance["content"] = content
        acceptance["content_review"] = report["content_review"]
    write_json(out / "acceptance.json", acceptance)
    return acceptance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    preflight = commands.add_parser("quick", help="Check text and same-page expectations without rendering PNGs; not delivery acceptance.")
    preflight.add_argument("pdf", type=Path)
    preflight.add_argument("--expectations", type=Path, required=True)
    preflight.add_argument("--docx", type=Path)
    preflight.add_argument("--render", type=Path)
    preflight.add_argument("--docx-comparison", type=Path)
    inspection = commands.add_parser("inspect", help="Render the actual PDF and create measurement/review files.")
    inspection.add_argument("pdf", type=Path)
    inspection.add_argument("--out", type=Path, required=True)
    inspection.add_argument("--docx", type=Path)
    inspection.add_argument("--expectations", type=Path)
    inspection.add_argument("--render", type=Path, help="Bind a completed render.json, its outputs and all declared inputs.")
    inspection.add_argument("--docx-comparison", type=Path, help="Bind a passed original/edited Word preservation comparison (required for edits).")
    inspection.add_argument("--review-format", choices=("verbose", "compact"), default="verbose",
                            help="Compact: five explicit criterion statuses plus one concise observation per page; warnings remain separate.")
    inspection.add_argument("--content-review", choices=("author", "independent"),
                            help="Require an explicit content check in review.json; existing native/edit workflows remain opt-in.")
    acceptance = commands.add_parser("accept", help="Check all current hashes and completed visual review.")
    acceptance.add_argument("out", type=Path)
    args = parser.parse_args()
    try:
        if args.command == "quick":
            report = quick(args.pdf, args.expectations, args.docx, args.render, args.docx_comparison)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            return 0 if report["passed"] else 2
        if args.command == "inspect":
            report = inspect(args.pdf, args.out, args.docx, args.expectations, args.render, args.docx_comparison,
                             args.review_format, args.content_review)
            blockers = sum(f["severity"] == "blocker" for f in report["findings"])
            warnings = sum(f["severity"] == "warning" for f in report["findings"])
            print(f"Inspected {report['page_count']} pages: {blockers} blockers, {warnings} warnings. Browse {args.out / 'gallery/index.html'} and full page PNGs, then complete {args.out / 'review.json'}.")
            return 2 if blockers else 0
        accept(args.out)
        print("READY_TO_DELIVER — current files match the inspected pages and completed review.")
        return 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RuntimeError,
            zipfile.BadZipFile, ET.ParseError) as error:
        print(f"Document QA failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
