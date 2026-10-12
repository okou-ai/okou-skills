#!/usr/bin/env python3
"""Select/reuse an Office Python and probe Writer once per environment state."""

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

PACKAGES = {
    "docx": ["python-docx==1.2.0", "pypdf==6.20.0"],
    "pdf": ["typst==0.15.0", "pypdf==6.20.0", "python-docx==1.2.0"],
    "xlsx": ["openpyxl==3.1.5"],
    "charts": ["matplotlib==3.11.2", "Pillow==12.3.0"],
}
MODULES = {"python-docx": "docx", "Pillow": "PIL"}


def run(args, **kwargs):
    return subprocess.run(args, check=True, text=True, capture_output=True, **kwargs)


def versions(python, packages):
    code = """
import importlib, importlib.metadata, json, sys
versions = {}
for package, module in json.loads(sys.argv[1]).items():
    try:
        importlib.import_module(module)
        versions[package] = importlib.metadata.version(package)
    except ImportError:
        versions[package] = None
print(json.dumps(versions))
"""
    names = {
        p.split("==")[0]: MODULES.get(p.split("==")[0], p.split("==")[0])
        for p in packages
    }
    return json.loads(run([str(python), "-c", code, json.dumps(names)]).stdout)


def writer_state():
    paths = [
        shutil.which("soffice"),
        "/usr/lib/libreoffice/program/libswlo.so",
        "/usr/lib/libreoffice/share/registry/writer.xcd",
    ]
    return [
        (str(p), Path(p).stat().st_mtime_ns, Path(p).stat().st_size)
        for p in paths
        if p and Path(p).exists()
    ]


def probe_writer(python, cache):
    started = time.monotonic()
    state = hashlib.sha256(json.dumps(writer_state()).encode()).hexdigest()
    cached = cache / f"writer-{state}.json"
    if cached.exists():
        return {
            **json.loads(cached.read_text()),
            "cached": True,
            "seconds": round(time.monotonic() - started, 3),
        }
    result = {"available": False, "cached": False}
    if (
        not shutil.which("soffice")
        or not Path("/usr/lib/libreoffice/program/libswlo.so").exists()
    ):
        result["reason"] = "LibreOffice Writer component is missing"
    else:
        with tempfile.TemporaryDirectory(prefix="office-probe-") as tmp:
            path = Path(tmp)
            run(
                [
                    str(python),
                    "-c",
                    "from docx import Document; import sys; d=Document(); d.add_paragraph('Office probe'); d.save(sys.argv[1])",
                    str(path / "probe.docx"),
                ]
            )
            try:
                output = run(
                    [
                        "soffice",
                        f"-env:UserInstallation={(path / 'profile').as_uri()}",
                        "--headless",
                        "--convert-to",
                        "pdf:writer_pdf_Export",
                        "--outdir",
                        tmp,
                        str(path / "probe.docx"),
                    ],
                    timeout=45,
                )
                pdf = path / "probe.pdf"
                result["available"] = pdf.exists() and pdf.read_bytes().startswith(
                    b"%PDF-"
                )
                if not result["available"]:
                    result["reason"] = (output.stdout + output.stderr).strip()
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
                result["reason"] = str(error)
    result["seconds"] = round(time.monotonic() - started, 3)
    cached.write_text(json.dumps(result))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--formats", nargs="+", choices=("docx", "pdf", "xlsx"), required=True
    )
    parser.add_argument("--charts", action="store_true")
    parser.add_argument("--install-missing", action="store_true")
    parser.add_argument("--cache", type=Path, default=Path(".office-cache"))
    args = parser.parse_args()
    args.cache.mkdir(parents=True, exist_ok=True)
    packages = list(
        dict.fromkeys(
            p
            for kind in args.formats + (["charts"] if args.charts else [])
            for p in PACKAGES[kind]
        )
    )
    candidates = [
        Path("/opt/office/bin/python"),
        Path(sys.executable),
        args.cache / "venv/bin/python",
    ]
    available = [(p, versions(p, packages)) for p in candidates if p.exists()]
    python, found = max(
        available, key=lambda item: sum(v is not None for v in item[1].values())
    )
    missing = [p for p in packages if found[p.split("==")[0]] is None]
    if missing and args.install_missing:
        # Never change a shared interpreter or fight externally-managed Python.
        venv = args.cache.resolve() / "venv"
        python = venv / "bin/python"
        if not python.exists():
            run([sys.executable, "-m", "venv", str(venv)])
        found = versions(python, packages)
        missing = [p for p in packages if found[p.split("==")[0]] is None]
        if missing:
            installer = (
                ["uv", "pip", "install", "--python", str(python)]
                if shutil.which("uv")
                else [str(python), "-m", "pip", "install"]
            )
            run(installer + missing)
        found = versions(python, packages)
        missing = [p for p in packages if found[p.split("==")[0]] is None]
    writer = None
    if "docx" in args.formats and not missing:
        # An actual missing component is a reason to install, not to keep probing.
        if (
            args.install_missing
            and not Path("/usr/lib/libreoffice/program/libswlo.so").exists()
            and shutil.which("apt-get")
            and shutil.which("sudo")
        ):
            try:
                run(["sudo", "-n", "apt-get", "update", "-qq"], timeout=120)
                run(
                    [
                        "sudo",
                        "-n",
                        "apt-get",
                        "install",
                        "-y",
                        "-qq",
                        "libreoffice-writer",
                    ],
                    timeout=120,
                )
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as error:
                print(f"Writer installation unavailable: {error}", file=sys.stderr)
        writer = probe_writer(python, args.cache)
    fonts = {}
    if shutil.which("fc-match") and set(args.formats) & {"docx", "pdf"}:
        for name in (
            "Times New Roman",
            "Liberation Serif",
            "Noto Serif CJK SC",
            "Noto Naskh Arabic",
        ):
            fonts[name] = run(["fc-match", "-f", "%{family}", name]).stdout
    print(
        json.dumps(
            {
                "python": str(python.absolute()),
                "versions": found,
                "missing": missing,
                "writer": writer,
                "fonts": fonts,
                "poppler": shutil.which("pdftocairo"),
            },
            indent=2,
        )
    )
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
