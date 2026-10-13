#!/usr/bin/env python3
"""Assemble inspected pdf2htmlEX pages with source notes, then install and verify."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
from html import escape
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from urllib.parse import unquote, urlsplit


HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("pdf_html_inventory", HERE / "inventory-html.py")
INVENTORY = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = INVENTORY
SPEC.loader.exec_module(INVENTORY)


def resource(value, converted):
    if value.startswith(("#", "data:")):
        return value
    url = urlsplit(value)
    if url.scheme or url.netloc:
        raise ValueError(f"Expected local converter resource: {value}")
    file = (converted / unquote(url.path)).resolve()
    if not file.is_relative_to(converted) or not file.is_file():
        raise ValueError(f"Missing or out-of-directory converter resource: {value}")
    return "../assets/pdf-source/" + file.relative_to(converted).as_posix() + (
        f"#{url.fragment}" if url.fragment else "")


def adapt(fragment, layout_id, converted):
    document = INVENTORY.Document(fragment)
    roots = [node for node in document.elements if node.has_class("pf")]
    if document.errors or len(roots) != 1 or roots[0].parent:
        raise ValueError(f"{layout_id}: expected one complete .pf source page")
    root = roots[0]
    changes = []
    for node in document.elements:
        attrs = dict(node.attrs)
        if node is root:
            attrs["class"] += " stage"
            attrs.update({"data-layout": layout_id, "data-source-profile": layout_id})
        if node.has_class("pc"):
            attrs["data-pdf-reference"] = ""
        if node.tag == "script":
            raise ValueError(f"{layout_id}: move converter scripts out of page fragments")
        if node.tag in ("img", "image", "use", "link", "object"):
            for key in ("src", "href", "xlink:href", "data"):
                if attrs.get(key):
                    attrs[key] = resource(attrs[key], converted)
        if attrs != node.attrs:
            opening = "<" + node.tag + "".join(f' {key}="{escape(value, quote=True)}"'
                                                for key, value in attrs.items()) + ">"
            changes.append((node.start, node.opening_end, opening))
    # Reference artwork and fixed chrome remain outside the editable content root.
    changes.append((root.closing_start, root.closing_start,
                    '<div class="fit pdf-content"></div><div class="pdf-chrome"></div>'))
    for start, end, replacement in sorted(changes, reverse=True):
        fragment = fragment[:start] + replacement + fragment[end:]
    return '<section class="slide" data-fit-display="block">' + fragment + '</section>\n'


def assemble(work, package, notes_path):
    started = time.monotonic()
    started_at = datetime.now(timezone.utc).isoformat()
    work, package = work.resolve(), package.resolve()
    if package.exists() and any(package.iterdir()):
        raise ValueError("Choose a new package directory; existing package is preserved")
    notes = json.loads(notes_path.read_text())
    for key in ("name", "title", "designSystem", "qaConfig", "pageRoles"):
        if not notes.get(key):
            raise ValueError(f"Source notes need {key}")
    converted = work / "pdf-html"
    conversion = json.loads((converted / "conversion.json").read_text())
    inspection = json.loads((converted / "inspection.json").read_text())
    inventory = json.loads((work / "html/inventory.json").read_text())
    if inspection["pageCount"] != inventory["pageCount"] or conversion["pageCount"] != inventory["pageCount"]:
        raise ValueError("Conversion, inspection and inventory page counts differ")
    if inspection.get("sourceSha256") != conversion["sourceSha256"]:
        raise ValueError("Inspection must belong to this PDF conversion")
    roles = notes["pageRoles"]
    if any(str(page) not in {str(n) for n in range(1, inventory["pageCount"] + 1)} for page in roles):
        raise ValueError("pageRoles keys must be original one-based page numbers")
    def write(file, contents):
        target = package / file
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(contents if isinstance(contents, str) else json.dumps(contents, indent=2) + "\n")
    # Keep relative CSS/font/image paths unchanged in one asset subtree.
    for file in converted.rglob("*"):
        if file.is_file() and file.suffix.lower() in (".css", ".png", ".jpg", ".jpeg", ".svg", ".woff", ".woff2", ".ttf", ".otf"):
            target = package / "assets/pdf-source" / file.relative_to(converted)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(file, target)
    original = INVENTORY.Document((converted / "source.html").read_text())
    styles = [resource(node.attrs["href"], converted) for node in original.elements
              if node.tag == "link" and "stylesheet" in node.attrs.get("rel", "").split()]
    write("styles/template.css", "\n".join(f'@import url("{url}");' for url in styles) + "\n" +
          '.pf.stage{margin:0;box-shadow:none}.stage>.pc{display:block!important}\n'
          '.pdf-content,.pdf-chrome{position:absolute;inset:0;pointer-events:none}\n'
          '.pdf-content>*,.pdf-chrome>*{pointer-events:auto}\n')
    write("layouts/_shell.html", '<!doctype html><html><head><meta charset="utf-8">'
          '<meta name="viewport" content="width=device-width,initial-scale=1">'
          f'<title>{escape(notes["title"])}</title><link rel="stylesheet" href="../styles/template.css">'
          '</head><body><main class="deck" data-navigation-mode="paged"></main></body></html>\n')
    layouts = []
    for entry, observed in zip(inventory["layouts"], inspection["pages"]):
        number = entry["sourcePages"][0]
        if observed["page"] != number:
            raise ValueError("Inspection page order differs from the original inventory")
        write("layouts/" + entry["file"], adapt((work / "html" / entry["file"]).read_text(), entry["id"], converted))
        layouts.append({"id": entry["id"], "file": entry["file"], "sourcePages": [number],
            "purpose": roles.get(str(number), "Source composition; choose by source preview"),
            "regions": [{"role": "source-composition", "editable": False},
                        {"role": "content", "selector": ".pdf-content", "requiresAdaptation": True},
                        {"role": "chrome", "selector": ".pdf-chrome"}],
            "capacity": {"status": "reference-only; measure selected content after adaptation"},
            "reuse": "reference-only", "observedText": observed["text"],
            "sourceId": observed["sourceId"], "backgrounds": observed["backgrounds"],
            "sourceDimensions": {"width": observed["width"], "height": observed["height"]}})
    first = inspection["pages"][0]
    ratio = (Fraction(str(first["width"])) / Fraction(str(first["height"]))).limit_denominator(10000)
    write("layouts/source-index.json", {"sourceFilename": conversion["sourceFilename"],
          "sourceSha256": conversion["sourceSha256"], "pageCount": len(layouts),
          "sourceAspectRatio": f"{ratio.numerator}:{ratio.denominator}", "layouts": layouts})
    write("tools/qa-config.json", notes["qaConfig"])
    write("design-system.md", notes["designSystem"] + "\n\n"
          "PDF preparation preserved pdf2htmlEX geometry, CSS and original page assets. "
          "Source compositions remain reference-only; computed text visibility alone proves no editable slots. "
          "For selected pages, retain artwork and clear original lettering before adding editable content "
          "in .pdf-content. Fixed footer/logo chrome belongs in sibling .pdf-chrome.\n")
    write("SKILL.md", f'---\nname: {json.dumps(notes["name"])}\ndescription: {json.dumps(notes["title"])}\n---\n\n'
          f'# {notes["title"]}\n\n'
          'Read the [design system](design-system.md), [source index](layouts/source-index.json) '
          'and [generation workflow](references/generate/workflow.md).\n\n'
          'Source pages preserve PDF compositions as references. Adapt selected layouts into editable HTML; '
          'hidden converter glyphs and background lettering need replacement, not text-string substitution. '
          'Prefer the indexed source cover and ending with their main artwork. '
          'Use .pdf-content for content and sibling .pdf-chrome for fixed footer/logo chrome. '
          'Resource paths resolve from layouts/, including source fragments.\n')
    write("layouts/README.md", 'Follow the [template entrypoint](../SKILL.md). Insert selected '
          '[indexed fragments](source-index.json) into [_shell.html](_shell.html); paths resolve from layouts/.\n')
    build_seconds = time.monotonic() - started
    commands = [["node", str(HERE / "install-qa.mjs"), "--package", str(package)],
                ["node", str(HERE.parent / "tools/verify-package.mjs"), "--package", str(package),
                 "--source-pages", str(work / "source-pages")]]
    for command in commands:
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode:
            raise ValueError(result.stdout + result.stderr)
    receipt = {"package": str(package), "status": "PACKAGE_VALID", "pageCount": len(layouts),
               "startedAt": started_at, "finishedAt": datetime.now(timezone.utc).isoformat(),
               "buildSeconds": round(build_seconds, 3),
               "installAndVerifySeconds": round(time.monotonic() - started - build_seconds, 3),
               "elapsedSeconds": round(time.monotonic() - started, 3)}
    (work / "package-build.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ("work-dir", "package", "notes"):
        parser.add_argument("--" + flag, type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(assemble(args.work_dir, args.package, args.notes)))
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"PDF package assembly failed: {error}\n")


if __name__ == "__main__":
    main()
