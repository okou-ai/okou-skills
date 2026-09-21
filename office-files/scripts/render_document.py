#!/usr/bin/env python3
"""Prepare native DOCX/PDF or render Markdown for shared page verification.

No document-type classification. A supplied DOCX is copied without rewriting;
a supplied reference controls styles. Only new, untemplated Markdown gets the
house theme. A native PDF is preserved without a Word intermediate. Output is
a candidate until check_document.py accepts it.
"""

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlparse

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                     prefix=".document-", suffix=".json", delete=False) as stream:
        temporary = Path(stream.name)
        json.dump(value, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    temporary.replace(path)


def run(command, *, input_text=None, timeout=120):
    result = subprocess.run(command, input=input_text, text=True,
                            capture_output=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f"{Path(command[0]).name} failed:\n{result.stderr or result.stdout}")
    return result.stdout


def find_pandoc():
    try:
        import pypandoc
        # Prefer the pinned wheel even when the host has another Pandoc on PATH.
        bundled = Path(pypandoc.__file__).parent / "files" / "pandoc"
        if bundled.is_file():
            return str(bundled)
    except ImportError:
        pass
    binary = shutil.which("pandoc")
    if binary:
        return binary
    raise RuntimeError("Install the skill's requirements.txt before rendering.")


def inline_text(value):
    """Extract visible text, excluding footnotes and link targets."""
    if isinstance(value, list):
        return "".join(inline_text(item) for item in value)
    if not isinstance(value, dict):
        return ""
    kind, content = value.get("t"), value.get("c")
    if kind == "Str":
        return content
    if kind in ("Space", "SoftBreak", "LineBreak"):
        return " "
    if kind in ("Code", "Math"):
        return content[1]
    if kind in ("Link", "Image", "Span"):
        return inline_text(content[1])
    if kind == "Cite":
        return inline_text(content[1])
    if kind in ("Note", "RawInline", "RawBlock"):
        return ""
    if kind == "Quoted":
        return inline_text(content[1])
    if kind == "MetaString":
        return content
    return inline_text(content)


def language_of(ast, override):
    if override:
        return override
    declared = inline_text(ast.get("meta", {}).get("lang", {})).strip()
    if declared:
        return declared
    # Only a fallback. Authors should set lang for regional glyphs/direction.
    text = inline_text(ast.get("blocks", []))
    for pattern, language in ((r"[\u3040-\u30ff]", "ja-JP"),
                              (r"[\uac00-\ud7af]", "ko-KR"),
                              (r"[\u4e00-\u9fff]", "zh-CN"),
                              (r"[\u0600-\u06ff]", "ar"),
                              (r"[\u0590-\u05ff]", "he")):
        if re.search(pattern, text):
            return language
    return "en-US"


def prose_text(block):
    if block.get("t") in ("Para", "Plain"):
        return inline_text(block["c"])
    return ""


def validate_source(value):
    """Pandoc's Word writer drops raw HTML/Typst instead of reporting an error."""
    if isinstance(value, list):
        for child in value:
            validate_source(child)
    elif isinstance(value, dict):
        if value.get("t") in ("RawBlock", "RawInline") and value["c"][0] != "openxml":
            raise ValueError("Raw " + value["c"][0] + " would be lost in Word. "
                             "Use Markdown elements or the selected template's native renderer.")
        for child in value.values():
            if isinstance(child, (list, dict)):
                validate_source(child)


def apply_design_components(ast):
    """Map semantic Markdown classes to renderer-native document components.

    The source stays portable Markdown. This small translation layer exists
    because Pandoc preserves paragraph custom styles but does not map table
    classes to Word table styles or heading classes to page-break properties.
    """
    for block in ast.get("blocks", []):
        if block.get("t") == "Table":
            attributes = block["c"][0]
            if "metric-grid" in attributes[1]:
                attributes[2] = [item for item in attributes[2] if item[0] != "custom-style"]
                attributes[2].append(["custom-style", "MetricGrid"])
    transformed = []
    for block in ast.get("blocks", []):
        if block.get("t") == "Header" and "chapter" in block["c"][1][1]:
            transformed.append({
                "t": "RawBlock",
                "c": ["openxml", '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'],
            })
        transformed.append(block)
    ast["blocks"] = transformed


def source_expectations(ast):
    """Bind semantic headings to the opening text they introduce, not a page quota.

    This supplements, rather than replaces, a visual check: math, positioned
    content, large tables and figures still need inspection of rendered pages.
    """
    def nonliteral(value):
        if isinstance(value, list):
            return any(nonliteral(item) for item in value)
        if isinstance(value, dict):
            return value.get("t") in {"Math", "RawInline", "RawBlock", "Note", "Cite", "Image"} or any(
                nonliteral(item) for item in value.values() if isinstance(item, (dict, list)))
        return False

    required, relationships = [], []
    blocks = ast.get("blocks", [])
    for index, block in enumerate(blocks):
        if block.get("t") != "Header" or nonliteral(block):
            continue
        heading = inline_text(block["c"][2]).strip()
        if not heading:
            continue
        required.append(heading)
        if index + 1 < len(blocks) and not nonliteral(blocks[index + 1]):
            following = prose_text(blocks[index + 1]).strip()
            if following:
                relationships.append({"first": heading, "second": following[:60],
                                      "reason": "Heading and opening text stay together"})
    return {"required_text": required, "same_page": relationships}


def validate_docx(path):
    """Reject dangling Word style references, which otherwise fail silently."""
    with zipfile.ZipFile(path) as archive:
        ET.fromstring(archive.read("[Content_Types].xml"))
        document = ET.fromstring(archive.read("word/document.xml"))
        if document.tag != W + "document":
            raise ValueError("Not a Word document.")
        defined = set()
        if "word/styles.xml" in archive.namelist():
            styles = ET.fromstring(archive.read("word/styles.xml"))
            defined = {item.get(W + "styleId") for item in styles.findall(W + "style")}
        missing = set()
        for name in archive.namelist():
            if not re.fullmatch(r"word/(document|header\d+|footer\d+|footnotes|endnotes)\.xml", name):
                continue
            root = ET.fromstring(archive.read(name))
            for item in root.iter():
                if item.tag in {W + "pStyle", W + "rStyle", W + "tblStyle"}:
                    style = item.get(W + "val")
                    if style and style not in defined:
                        missing.add(style)
        if missing:
            raise RuntimeError("DOCX references undefined styles: " + ", ".join(sorted(missing)) +
                               ". Repair the reference document before exporting.")


def export_pdf(docx_path, output_dir):
    binary = shutil.which("soffice") or shutil.which("libreoffice")
    if not binary:
        raise RuntimeError("PDF export and Word preview require LibreOffice Writer. "
                           "See references/document-layout.md for installation.")
    with tempfile.TemporaryDirectory(prefix="office-profile-") as profile:
        output = run([binary, "-env:UserInstallation=" + Path(profile).as_uri(),
                      "--headless", "--convert-to",
                      'pdf:writer_pdf_Export:{"UseTaggedPDF":{"type":"boolean","value":"true"}}',
                      "--outdir", str(output_dir), str(docx_path)], timeout=180)
    pdf_path = output_dir / (docx_path.stem + ".pdf")
    if not pdf_path.is_file() or not pdf_path.stat().st_size:
        raise RuntimeError("LibreOffice did not produce a PDF. Install libreoffice-writer "
                           "(the Draw/Impress packages are insufficient).\n" + output)
    return pdf_path, run([binary, "--version"]).strip()


def render(source, output_dir, output_format=None, lang=None, reference=None, resources=()):
    source, output_dir = Path(source).resolve(), Path(output_dir).resolve()
    native_pdf = source.suffix.lower() == ".pdf"
    if source.suffix.lower() not in (".md", ".markdown", ".docx", ".pdf"):
        raise ValueError("Input must be Markdown, a finished DOCX, or a finished PDF.")
    if not source.is_file():
        raise ValueError(f"Source file does not exist: {source}")
    output_format = output_format or ("pdf" if native_pdf else "both")
    if output_format not in ("pdf", "docx", "both"):
        raise ValueError("Output format must be pdf, docx, or both.")
    if native_pdf and output_format != "pdf":
        raise ValueError("A PDF input cannot produce editable Word. Author DOCX separately or supply its native source.")
    reference = Path(reference).resolve() if reference else None
    if reference and (source.suffix.lower() not in (".md", ".markdown") or not reference.is_file()):
        raise ValueError("--reference requires a Markdown input and an existing reference DOCX.")
    resource_paths = sorted({Path(path).resolve() for path in resources})
    for path in resource_paths:
        if not path.is_file():
            raise ValueError(f"Resource file does not exist: {path}")
    output_dir.mkdir(parents=True, exist_ok=True)
    extensions = (".pdf",) if native_pdf else (".docx", ".pdf")
    targets = [output_dir / (source.stem + ext) for ext in extensions]
    targets += [output_dir / name for name in ("expectations.json", "render.json")]
    for target in targets:
        for original in (source, reference, *resource_paths):
            if original and (target.resolve() == original or
                             (target.exists() and target.samefile(original))):
                raise ValueError("Output would overwrite an input. Choose a separate output directory.")
    write_json(output_dir / "render.json", {"status": "rendering", "source": str(source)})
    try:
        return render_candidate(source, output_dir, output_format, lang, reference, resource_paths)
    except Exception as error:
        write_json(output_dir / "render.json", {"status": "failed", "source": str(source),
                                                "error": str(error)})
        raise


def local_resources(value, parent):
    paths = set()
    if isinstance(value, list):
        for child in value:
            paths.update(local_resources(child, parent))
    elif isinstance(value, dict):
        if value.get("t") == "Image":
            target = urlparse(value["c"][2][0])
            if not target.scheme and target.path:
                path = (parent / unquote(target.path)).resolve()
                if path.is_file():
                    paths.add(path)
        for child in value.values():
            if isinstance(child, (list, dict)):
                paths.update(local_resources(child, parent))
    return paths


def render_candidate(source, output_dir, output_format, lang, reference, resource_paths=()):
    # Everything is built in isolation. A failed export cannot reuse an old PDF.
    with tempfile.TemporaryDirectory(prefix=".document-", dir=output_dir) as staging:
        stage = Path(staging)
        docx_path = stage / (source.stem + ".docx")
        pdf_path = stage / (source.stem + ".pdf")
        versions = {}
        resources = [{"path": str(path), "sha256": sha256(path)} for path in resource_paths]
        warnings = []
        expectations = {"required_text": [], "same_page": []}
        source_hash = sha256(source)
        reference_hash = sha256(reference) if reference else None
        if source.suffix.lower() == ".pdf":
            import pymupdf

            shutil.copyfile(source, pdf_path)
            with pymupdf.open(pdf_path) as document:
                if not document.is_pdf or document.needs_pass or len(document) == 0:
                    raise ValueError("Expected a readable, unencrypted PDF with pages.")
            versions["pymupdf"] = pymupdf.VersionBind
            theme = "source-preserved"
            artifacts = (pdf_path,)
        elif source.suffix.lower() == ".docx":
            shutil.copyfile(source, docx_path)
            theme = "source-preserved"
        else:
            # Native files do not need the Markdown author's dependencies.
            from document_style import build_reference, polish_document

            pandoc = find_pandoc()
            versions["pandoc"] = run([pandoc, "--version"]).splitlines()[0]
            ast = json.loads(run([pandoc, str(source), "-f", "markdown-smart", "-t", "json"]))
            validate_source(ast)
            apply_design_components(ast)
            existing = {item["path"] for item in resources}
            resources.extend({"path": str(path), "sha256": sha256(path)}
                             for path in sorted(local_resources(ast, source.parent))
                             if str(path) not in existing)
            lang = language_of(ast, lang)
            ast.setdefault("meta", {})["lang"] = {"t": "MetaString", "c": lang}
            if not reference:
                (stage / "style").mkdir()
                active_reference = stage / "style" / "reference.docx"
                build_reference(pandoc, active_reference, lang)
            else:
                active_reference = reference
            run([pandoc, "-f", "json", "-t", "docx", "--standalone",
                 "--resource-path", str(source.parent),
                 "--log", str(stage / "pandoc.json"),
                 "--reference-doc", str(active_reference), "-o", str(docx_path)],
                input_text=json.dumps(ast, ensure_ascii=False))
            warnings = json.loads((stage / "pandoc.json").read_text(encoding="utf-8"))
            # Pandoc can exit successfully after dropping an image or other
            # unsupported content. Only known localization notices are benign.
            destructive = [item for item in warnings if item.get("verbosity") == "WARNING" and
                           item.get("type") not in {"CouldNotLoadTranslations", "NoTranslation"}]
            if destructive:
                raise RuntimeError("Pandoc reported an export problem:\n" + "\n".join(
                    item.get("pretty", str(item)) for item in destructive))
            if not reference:
                polish_document(docx_path, lang)
            theme = "reference-preserved" if reference else "default"
            expectations = source_expectations(ast)
        if source.suffix.lower() != ".pdf":
            validate_docx(docx_path)
            pdf_path, versions["libreoffice"] = export_pdf(docx_path, stage)
            artifacts = (docx_path, pdf_path)
        if (source_hash != sha256(source) or (reference and reference_hash != sha256(reference)) or
                any(item["sha256"] != sha256(item["path"]) for item in resources)):
            raise RuntimeError("An input changed during rendering; rerun against a stable source.")
        outputs = {}
        for path in artifacts:
            destination = output_dir / path.name
            # Replacing directory entries never follows an existing output
            # symlink/hardlink to another file.
            path.replace(destination)
            outputs[path.suffix[1:]] = {"path": str(destination), "sha256": sha256(destination)}
        (stage / "expectations.json").write_text(
            json.dumps(expectations, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (stage / "expectations.json").replace(output_dir / "expectations.json")
        manifest = {"status": "needs-inspection", "source": {"path": str(source), "sha256": source_hash},
                    "reference": {"path": str(reference), "sha256": reference_hash} if reference else None,
                    "resources": resources, "warnings": warnings,
                    "theme": theme, "language": lang, "versions": versions, "outputs": outputs,
                    "deliver": list(outputs) if output_format == "both" else [output_format]}
        (stage / "render.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (stage / "render.json").replace(output_dir / "render.json")
        return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("--out", type=Path, required=True, help="Output directory, separate from input")
    parser.add_argument("--format", choices=("pdf", "docx", "both"),
                        help="Delivery files; defaults to pdf for PDF input, otherwise both. Word always gets a PDF preview.")
    parser.add_argument("--lang", help="BCP 47 language; overrides Markdown lang metadata")
    parser.add_argument("--reference", type=Path, help="Style reference for NEW Markdown prose only")
    parser.add_argument("--resource", type=Path, action="append", default=[],
                        help="Bind an authoring script, data, template, filter or asset to verification; repeat for each file.")
    args = parser.parse_args()
    try:
        result = render(args.source, args.out, args.format, args.lang, args.reference, args.resource)
    except (ValueError, RuntimeError, OSError, KeyError, ET.ParseError,
            subprocess.TimeoutExpired, zipfile.BadZipFile) as error:
        parser.exit(1, f"Render failed: {error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
