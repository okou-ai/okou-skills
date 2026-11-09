#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Office mechanical operations; no business inference, AI calls, or installation.

Use `list` for capabilities and `COMMAND --help` for parameters/contracts.
Every execution returns one JSON receipt on stdout (including failures).
Receipts describe executed checks, never business accuracy or visual approval.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from lo_safety import reserve_output

TOOLS = {
    "docx-env": (["bash", str(ROOT / "docx/scripts/env_check.sh")], "SDK/build environment, not candidate validation"),
    "docx-create": (["bash", str(ROOT / "docx/scripts/docx.sh"), "create"], "existing generic DOCX styles and explicit content blocks"),
    "docx-validate": (["bash", str(ROOT / "docx/scripts/docx.sh"), "validate"], "OpenXML SDK package checks; optional general business rules, not domain certification"),
    "docx-render": ([sys.executable, str(ROOT / "docx/scripts/render_docx.py")], "Writer PDF export; optional Poppler page rasterization, not visual inspection"),
    "xlsx-preflight": ([sys.executable, str(ROOT / "xlsx/scripts/libreoffice_recalc.py")], "independent live-formula/empty-cache calculation control, not a candidate pass"),
    "xlsx-formulas": ([sys.executable, str(ROOT / "xlsx/scripts/formula_check.py")], "static cached errors and heuristic references, not formula evaluation"),
    "xlsx-styles": ([sys.executable, str(ROOT / "xlsx/scripts/style_audit.py")], "implemented style/index checks only, not all formatting or finance accuracy"),
    "pdf-env": (["bash", str(ROOT / "pdf/scripts/make.sh"), "check"], "cover/body dependencies including actual Chromium launch"),
    "pdf-create": (["bash", str(ROOT / "pdf/scripts/make.sh"), "run"], "existing palette/cover/body/merge pipeline, not content validation"),
    "pdf-palette": ([sys.executable, str(ROOT / "pdf/scripts/palette.py")], "existing visual token presets, not manuscript compliance"),
}
LIMITS = ["No business, factual, input-semantic, standards, visual or final-usability approval is performed.",
          "User requirements/templates take precedence; no implicit restyling. No original or existing output is overwritten.",
          "No AI, automatic installation, retry, scheduling, or external-link refresh is requested."]


class Unavailable(RuntimeError):
    pass


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(argv, timeout, *, soffice=None):
    """One attempt; terminate only this invocation's process group on timeout."""
    environment = os.environ.copy()
    # Legacy shell pipelines invoke python3: retain the caller's selected venv.
    environment["PATH"] = str(Path(sys.executable).parent) + os.pathsep + environment.get("PATH", "")
    if soffice:
        environment["OFFICE_SOFFICE"] = soffice
    process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=environment,
                               start_new_session=(os.name == "posix"))
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        if os.name == "posix":
            os.killpg(process.pid, signal.SIGKILL)
        else:
            process.kill()
        process.communicate()
        raise RuntimeError(f"Timed out after {timeout}s; no automatic retry")
    return subprocess.CompletedProcess(argv, process.returncode, stdout.decode(errors="replace"),
                                       stderr.decode(errors="replace"))


class Execution:
    def __init__(self, runner=run):
        self.runner = runner
        self.receipt = {"schema_version": 1, "status": "ok", "steps": [], "artifacts": [], "limits": list(LIMITS)}

    def step(self, name, argv, scope, timeout=90, unavailable_codes=()):
        step = {"tool": name, "argv": argv, "scope": scope, "status": "failed"}
        self.receipt["steps"].append(step)
        started = time.monotonic()
        try:
            result = self.runner(argv, timeout)
            step.update(exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr,
                        elapsed_seconds=round(time.monotonic() - started, 3))
            step["status"] = "ok" if result.returncode == 0 else "failed"
            if result.returncode in unavailable_codes:
                step["status"] = "unavailable"
                raise Unavailable(f"{name} unavailable; inspect step output")
            if result.returncode:
                raise RuntimeError(f"{name} failed; inspect step output")
            try:
                step["result"] = json.loads(result.stdout)
            except (ValueError, TypeError):
                pass
            return result
        except FileNotFoundError as exc:
            step.update(status="unavailable", error=str(exc))
            raise Unavailable(str(exc)) from exc
        except Exception as exc:
            step["error"] = str(exc)
            raise

    def tool(self, name, args=(), timeout=90, unavailable_codes=()):
        argv, scope = TOOLS[name]
        return self.step(name, argv + list(args), scope, timeout, unavailable_codes)

    def artifact(self, path):
        self.receipt["artifacts"].append({"path": str(path), "bytes": path.stat().st_size,
                                          "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})


def source_file(value, suffixes):
    path = Path(value).expanduser().resolve()
    if not path.is_file() or path.suffix.lower() not in suffixes:
        raise ValueError(f"Expected an existing {', '.join(suffixes)} file: {path}")
    return path


def fresh_path(value):
    path = Path(value).expanduser().absolute()
    if path.exists() or path.is_symlink():
        raise ValueError(f"Refusing to overwrite existing path: {path}")
    return path


def publish(source, destination):
    """Reuse exclusive owned reservations; failed copies leave no fake output."""
    if not source.is_file() or source.is_symlink() or source.stat().st_size == 0:
        raise ValueError("Generated output must be a nonempty regular file")
    with reserve_output(destination, source=source) as reserved:
        reserved.publish(source)


def cache_snapshot(path):
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    formulas, missing = set(), []
    with zipfile.ZipFile(path) as package:
        for part in package.namelist():
            if part.startswith("xl/worksheets/") and part.endswith(".xml"):
                for cell in ET.fromstring(package.read(part)).iter(f"{ns}c"):
                    if cell.find(f"{ns}f") is not None:
                        key = f"{part}!{cell.get('r')}"
                        formulas.add(key)
                        cache = cell.find(f"{ns}v")
                        # Excel/Calc represent a computed empty string as t="str"
                        # with an existing empty <v/>. Missing <v>, or an empty
                        # numeric cache, is still uncalculated. Never invent caches.
                        if cache is None or (not (cache.text or "").strip() and cell.get("t") != "str"):
                            missing.append(key)
    return formulas, missing


def apply_style(source, target, plan_path):
    """Dispatch author-selected geometry/roles to EXISTING primitives, not inference."""
    try:
        import openpyxl
    except ImportError as exc:
        raise Unavailable("openpyxl missing in this interpreter; see xlsx/requirements-authoring.txt") from exc
    with zipfile.ZipFile(source) as package:
        unsupported = [name for name in package.namelist() if any(
            token in name.lower() for token in ("vbaproject", "activex", "externallinks", "connections.xml", "querytables/", "embeddings/", "pivot", "drawings/", "slicer", "customxml/"))]
        if unsupported:
            raise ValueError(f"Style CLI supports simple XLSX only; use targeted package editing to preserve: {unsupported}")
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if not isinstance(plan, dict) or set(plan) != {"operations"} or not isinstance(plan["operations"], list) or not plan["operations"]:
        raise ValueError('Plan must be {"operations": [explicit primitive operations]}')
    primitives = load_module("office_xlsx_authoring", ROOT / "xlsx/scripts/xlsx_authoring.py")
    workbook = openpyxl.load_workbook(source, keep_links=True)
    allowed = {"style_value": {"cell", "role", "kind"}, "report_band": {"range", "text", "level"},
               "table_header": {"range"}, "report_page": {"range", "orientation", "paper_size"}}
    try:
        for op in plan["operations"]:
            if not isinstance(op, dict):
                raise ValueError("Each operation must be an object")
            name, sheet = op.get("op"), op.get("sheet")
            if name not in allowed or set(op) - (allowed[name] | {"op", "sheet"}):
                raise ValueError(f"Unknown primitive or parameters: {op}")
            ws = workbook[sheet]
            options = {key: value for key, value in op.items() if key not in {"op", "sheet", "cell", "range"}}
            if name == "style_value":
                # A single bounded address, not an implicit whole-sheet operation.
                cell = ws[op["cell"]]
                if not hasattr(cell, "coordinate"):
                    raise ValueError("style_value requires one cell address")
                primitives.style_value(cell, **options)
            else:
                getattr(primitives, name)(ws, op["range"], **options)
        workbook.save(target)
    finally:
        workbook.close()
    return len(plan["operations"])


def execute(args, ex):
    ex.receipt["command"] = args.command
    if args.command == "list":
        ex.receipt["capabilities"] = {name: {"argv": argv, "scope": scope} for name, (argv, scope) in TOOLS.items()}
        ex.receipt["commands"] = ["preflight", "create", "validate", "recalc", "render", "style", "tool-help"]
        ex.receipt["style_primitives"] = ["style_value", "report_band", "table_header", "report_page"]
        return
    if args.command == "tool-help":
        flags = ["--help"]
        argv = TOOLS[args.tool][0]
        if args.tool.startswith("pdf-") and args.tool != "pdf-palette":
            argv = argv[:2]
        ex.step(args.tool, argv + flags, "parameter/usage discovery only")
        return
    if args.command == "preflight":
        if args.format == "xlsx":
            ex.tool("xlsx-preflight", ["--preflight", "--timeout", str(args.timeout)], args.timeout * 2 + 30, (2,))
        elif args.format == "docx":
            ex.tool("docx-env", ["--with-rendering"] if args.rendering else [], args.timeout * 2 + 60,
                    (1,) if not shutil.which("dotnet") else ())
            # env_check reports rendering problems as warnings; require the actual control separately.
            if args.rendering:
                ex.tool("docx-render", ["--check", "--timeout", str(args.timeout)], args.timeout + 30)
        else:
            ex.tool("pdf-env", timeout=args.timeout + 30, unavailable_codes=(2,))
        return
    if args.command == "create":
        content = source_file(args.content, {".json"})
        json.loads(content.read_text(encoding="utf-8"))
        destination = fresh_path(args.out)
        if destination.suffix.lower() != f".{args.format}":
            raise ValueError("Output suffix must match --format")
        with tempfile.TemporaryDirectory(prefix="office_create_") as directory:
            target = Path(directory) / destination.name
            if args.format == "docx":
                if args.type not in {None, "report", "letter", "memo", "academic"}:
                    raise ValueError("DOCX type: report|letter|memo|academic (generic appearance only)")
                ex.tool("docx-create", ["--content-json", str(content), "--title", args.title,
                        "--type", args.type or "report", "--author", args.author,
                        "--page-size", args.page_size, "--output", str(target)], args.timeout + 30)
            else:
                palette = load_module("office_pdf_palette", ROOT / "pdf/scripts/palette.py")
                if args.type is not None and args.type not in palette.PALETTES:
                    raise ValueError("Unknown PDF visual preset; use tool-help --tool pdf-palette")
                ex.tool("pdf-create", ["--content", str(content), "--title", args.title,
                        "--type", args.type or "general", "--author", args.author,
                        "--date", args.date, "--out", str(target)], args.timeout + 30)
            if not target.is_file() or target.stat().st_size == 0:
                raise RuntimeError("Creator produced no nonempty output")
            if ((args.format == "pdf" and not target.read_bytes().startswith(b"%PDF-"))
                    or (args.format == "docx" and not zipfile.is_zipfile(target))):
                raise RuntimeError("Creator output has the wrong file container")
            publish(target, destination)
        ex.artifact(destination)
        return
    source = source_file(args.input, {".xlsx", ".docx", ".pdf"})
    suffix = source.suffix.lower()
    if args.command == "validate":
        if suffix == ".xlsx":
            if args.business:
                raise ValueError("--business is DOCX-only")
            ex.tool("xlsx-formulas", [str(source), "--json"])
            if args.styles:
                ex.tool("xlsx-styles", [str(source), "--json"])
        elif suffix == ".docx":
            if args.styles:
                raise ValueError("--styles is XLSX-only")
            ex.tool("docx-validate", ["--input", str(source), "--json"] + (["--business"] if args.business else []))
        else:
            if args.styles or args.business:
                raise ValueError("No DOCX/XLSX check flags apply to PDF")
            ex.step("pdfinfo", ["pdfinfo", str(source)], "Poppler parses PDF page metadata only; not visual/content/form appearance approval")
        return
    if args.command == "recalc":
        if suffix != ".xlsx":
            raise ValueError("Only non-macro XLSX recalculation is supported")
        destination = fresh_path(args.out)
        if destination.suffix.lower() != ".xlsx":
            raise ValueError("Recalculation output must be .xlsx")
        ex.tool("xlsx-preflight", ["--preflight", "--timeout", str(args.timeout)], args.timeout * 2 + 30, (2,))
        before, _ = cache_snapshot(source)
        with tempfile.TemporaryDirectory(prefix="office_recalc_") as directory:
            target = Path(directory) / destination.name
            ex.tool("xlsx-preflight", [str(source), str(target), "--timeout", str(args.timeout)], args.timeout * 2 + 30, (2,))
            after, missing = cache_snapshot(target)
            if before - after or missing:
                raise RuntimeError(f"Live formula cells lost or formula caches empty: lost={sorted(before-after)}, empty={missing}")
            ex.receipt["steps"].append({"tool": "formula-cache-readback", "status": "ok", "formula_cells": len(after),
                "scope": "Retained input formula addresses and nonempty output caches only; expected business values remain unverified"})
            ex.tool("xlsx-formulas", [str(target), "--json"])
            publish(target, destination)
        ex.artifact(destination)
        ex.receipt["limits"].append("Calc conversion may alter features/styles. Compare before selecting for delivery; no Excel-native or driver-mutation check was performed.")
        return
    if args.command == "style":
        if suffix != ".xlsx":
            raise ValueError("Style primitives accept simple non-macro XLSX only")
        destination = fresh_path(args.out)
        if destination.suffix.lower() != ".xlsx":
            raise ValueError("Style output must be .xlsx")
        plan = source_file(args.plan, {".json"})
        with tempfile.TemporaryDirectory(prefix="office_style_") as directory:
            target = Path(directory) / destination.name
            count = apply_style(source, target, plan)
            ex.receipt["steps"].append({"tool": "xlsx_authoring", "status": "ok", "operations": count,
                "scope": "Explicitly selected finance defaults and coordinates via existing primitives only; no inferred semantics or layout approval"})
            publish(target, destination)
        ex.artifact(destination)
        ex.receipt["limits"].append("Library save invalidates formula caches; recalculate and recheck the exact final file. Advanced package features are not supported by this style CLI.")
        return
    if args.command == "render":
        pages = fresh_path(args.pages) if args.pages else None
        if suffix == ".docx":
            if not args.out:
                raise ValueError("DOCX render requires --out new.pdf")
            destination = fresh_path(args.out)
            if destination.suffix.lower() != ".pdf":
                raise ValueError("DOCX render output must be .pdf")
            with tempfile.TemporaryDirectory(prefix="office_render_") as directory:
                target = Path(directory) / destination.name
                ex.tool("docx-render", [str(source), "--out", str(target), "--timeout", str(args.timeout)], args.timeout + 30)
                if not target.is_file() or not target.read_bytes().startswith(b"%PDF-"):
                    raise RuntimeError("Renderer produced no actual PDF container")
                publish(target, destination)
            ex.artifact(destination)
            source = destination
        elif suffix != ".pdf" or args.out:
            raise ValueError("Render supports DOCX→PDF or PDF→PNG only. XLSX native export is not implemented here.")
        if pages:
            pages.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(prefix="office_pages_", dir=pages.parent) as directory:
                work = Path(directory) / "pages"
                work.mkdir()
                ex.step("pdftoppm", ["pdftoppm", "-png", "-r", "120", str(source), str(work / "page")],
                        "Poppler rasterization only; images have not been visually inspected", args.timeout)
                images = sorted(work.glob("page-*.png"))
                if not images:
                    raise RuntimeError("Renderer produced no page images")
                pages.mkdir()  # exclusive, never merge with stale previews
                for image in images:
                    destination_image = pages / image.name
                    publish(image, destination_image)
                    ex.artifact(destination_image)
        elif suffix == ".pdf":
            raise ValueError("PDF render requires --pages new-directory")
        return
    raise ValueError("Unknown command")


def parser():
    p = Parser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    commands = p.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="Discover executables and their actual scopes (JSON)")
    help_parser = commands.add_parser("tool-help", help="Get an existing tool's detailed usage in a JSON receipt")
    help_parser.add_argument("--tool", choices=sorted(TOOLS), required=True)
    preflight = commands.add_parser("preflight", help="Execute existing environment/control checks, never a candidate pass")
    preflight.add_argument("--format", choices=["docx", "xlsx", "pdf"], required=True)
    preflight.add_argument("--rendering", action="store_true", help="DOCX only: also require an actual Writer conversion control")
    create = commands.add_parser("create", help="Reuse DOCX generic styles or PDF visual-token pipeline; no content invention")
    create.add_argument("--format", choices=["docx", "pdf"], required=True)
    create.add_argument("--content", required=True, help="Existing content-block JSON; see format's content contract")
    create.add_argument("--title", required=True)
    create.add_argument("--type", help="Existing visual preset; not APA/IEEE or standards certification")
    create.add_argument("--author", default="")
    create.add_argument("--date", default="", help="PDF cover date")
    create.add_argument("--page-size", default="letter", choices=["letter", "a4", "legal", "a3"], help="DOCX page size")
    create.add_argument("--out", required=True, help="New output path; existing files are refused")
    validate = commands.add_parser("validate", help="Format-specific static checks; not a general quality certificate")
    validate.add_argument("--input", required=True)
    validate.add_argument("--styles", action="store_true", help="Also run implemented XLSX style audit; select only where relevant")
    validate.add_argument("--business", action="store_true", help="DOCX general business rules, not domain correctness")
    recalc = commands.add_parser("recalc", help="Actual independent Calc control → copy recalculation → cache readback → static scan")
    recalc.add_argument("--input", required=True)
    recalc.add_argument("--out", required=True)
    render = commands.add_parser("render", help="DOCX→PDF and/or PDF→page PNGs; not visual review")
    render.add_argument("--input", required=True)
    render.add_argument("--out", help="New PDF destination (DOCX input only)")
    render.add_argument("--pages", help="New page PNG directory (no stale-image reuse)")
    style = commands.add_parser("style", help="Apply explicit existing financial styling primitives to a simple XLSX copy",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog='''Plan contract (all coordinates/roles selected by the author, never inferred):
{"operations": [
  {"op":"style_value", "sheet":"Sheet", "cell":"B2", "role":"input", "kind":"percent"},
  {"op":"report_band", "sheet":"Sheet", "range":"A1:D1", "text":"Title", "level":"title"},
  {"op":"table_header", "sheet":"Sheet", "range":"A3:D3"},
  {"op":"report_page", "sheet":"Sheet", "range":"A1:D20", "orientation":"landscape"}
]}
style_value roles: input/same_sheet/cross_sheet/external/source/label;
kinds: amount/percent/integer/year/date/text. report_band level: title/section.
report_page accepts optional paper_size (openpyxl code). No data/formula filling.
Supplied templates override defaults. Do not use finance defaults for ordinary tables.
Library save clears caches; recalculate afterward. Unsupported complex packages refused.''')
    style.add_argument("--input", required=True)
    style.add_argument("--out", required=True)
    style.add_argument("--plan", required=True)
    style.add_argument("--use-finance-defaults", action="store_true", required=True,
                       help="Explicitly confirm these defaults were selected, not a supplied house style")
    for sub in (preflight, recalc, render):
        sub.add_argument("--soffice", help="Explicit absolute LibreOffice executable (or set OFFICE_SOFFICE); invalid override fails, no fallback")
    for sub in (preflight, create, recalc, render):
        sub.add_argument("--timeout", type=int, default=60, help="Per-engine time budget in seconds; no automatic retry; TMPDIR controls temporary workspace")
    return p


def main(argv=None, runner=run):
    ex = Execution(runner)
    try:
        args = parser().parse_args(argv)
        override = getattr(args, "soffice", None)
        if override:
            executable = Path(override).expanduser()
            if not executable.is_absolute() or not executable.is_file() or not os.access(executable, os.X_OK):
                raise ValueError("--soffice must be an absolute executable file")
            if args.command == "preflight" and args.format == "pdf":
                raise ValueError("--soffice does not apply to the PDF cover/body pipeline")
            if runner is run:
                ex.runner = lambda command, timeout: run(command, timeout, soffice=str(executable))
            ex.receipt["runtime"] = {"soffice": str(executable), "tmpdir": os.environ.get("TMPDIR")}
        if hasattr(args, "timeout") and args.timeout <= 0:
            raise ValueError("--timeout must be positive")
        if getattr(args, "rendering", False) and args.format != "docx":
            raise ValueError("--rendering is DOCX-only")
        execute(args, ex)
    except Unavailable as exc:
        ex.receipt.update(status="unavailable", error=str(exc))
    except Exception as exc:
        ex.receipt.update(status="failed", error=f"{type(exc).__name__}: {exc}")
    print(json.dumps(ex.receipt, ensure_ascii=False, indent=2))
    return {"ok": 0, "failed": 1, "unavailable": 2}[ex.receipt["status"]]


if __name__ == "__main__":
    sys.exit(main())
