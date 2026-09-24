#!/usr/bin/env python3
"""Install only missing pinned Office dependencies and report setup wall time.

Run once for the chosen route; this does not author or approve any artifact.
Debian/Ubuntu packages are used for Writer/Calc. Other systems receive concrete
missing-dependency errors instead of a guessed installation command.
"""

import argparse
from importlib import metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time


PYTHON_PACKAGES = {
    "document": {"pypandoc_binary": "1.17", "python-docx": "1.2.0", "PyMuPDF": "1.28.2"},
    "spreadsheet": {"openpyxl": "3.1.5", "lxml": "6.1.3", "PyMuPDF": "1.28.2"},
}


def package_version(name):
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def verified_python_versions(packages):
    """Use startup discovery after pip creates a previously absent user site.

    The running interpreter omits a user site that did not exist at startup;
    invalidating metadata caches does not add it to sys.path. A fresh process
    also avoids stale metadata when pip replaces an installed distribution.
    """
    code = """
from importlib import metadata
import json
import sys
versions = {}
for name in json.load(sys.stdin):
    try:
        versions[name] = metadata.version(name)
    except metadata.PackageNotFoundError:
        versions[name] = None
print(json.dumps(versions))
"""
    process = subprocess.run([sys.executable, "-c", code], input=json.dumps(list(packages)),
                             capture_output=True, text=True, timeout=60, check=False)
    if process.returncode:
        raise RuntimeError("Python dependency verification failed in a fresh interpreter "
                           f"(exit {process.returncode})")
    try:
        versions = json.loads(process.stdout)
    except json.JSONDecodeError as error:
        raise RuntimeError("Python dependency verification returned invalid JSON") from error
    if (not isinstance(versions, dict) or set(versions) != set(packages) or
            any(value is not None and not isinstance(value, str) for value in versions.values())):
        raise RuntimeError("Python dependency verification returned invalid versions")
    return versions


def module_installed(package):
    if not shutil.which("dpkg-query"):
        return False
    result = subprocess.run(
        ["dpkg-query", "--show", "--showformat=${Status}", package],
        capture_output=True, text=True, check=False,
    )
    return result.returncode == 0 and result.stdout.strip() == "install ok installed"


def setup(kind, charts, out, plan_only=False):
    started = time.perf_counter()
    packages = dict(PYTHON_PACKAGES[kind])
    if charts:
        if kind != "document":
            raise ValueError("--charts is for document PNG charts; spreadsheet charts are native")
        packages["matplotlib"] = "3.10.8"
    office = "libreoffice-writer" if kind == "document" else "libreoffice-calc"
    missing = [f"{name}=={version}" for name, version in packages.items() if package_version(name) != version]
    office_missing = not module_installed(office)
    report = {
        "kind": kind, "status": "PLANNED", "required_python": packages,
        "python_to_install": missing, "office_module": office,
        "office_module_to_install": office_missing, "steps": [],
    }
    out = Path(out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    def command(name, args, timeout):
        before = time.perf_counter()
        step = {"name": name}
        report["steps"].append(step)
        try:
            process = subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=False)
            step["returncode"] = process.returncode
            if process.returncode:
                # Keep actionable installer output in the local report, not a
                # large successful apt/pip transcript in the model context.
                step["error"] = (process.stderr or process.stdout)[-4000:]
                raise RuntimeError(f"{name} failed; see {out}")
        finally:
            step["seconds"] = round(time.perf_counter() - before, 3)

    try:
        if plan_only:
            return report
        if missing:
            command("python_dependencies", [sys.executable, "-m", "pip", "install", "--break-system-packages", "--quiet", "--disable-pip-version-check", *missing], 300)
        if office_missing:
            if not shutil.which("apt-get") or not shutil.which("dpkg-query"):
                raise RuntimeError(f"Install {office} for this platform; module detection here supports Debian/Ubuntu")
            prefix = [] if hasattr(os, "geteuid") and os.geteuid() == 0 else ["sudo", "-n"]
            if prefix and not shutil.which("sudo"):
                raise RuntimeError(f"Install {office}; no unattended package installer is available")
            command("package_index", [*prefix, "apt-get", "update", "-qq"], 180)
            command("office_module", [*prefix, "apt-get", "install", "-y", "-qq", office], 300)
        verified = verified_python_versions(packages)
        report["verified_python"] = verified
        remaining = [name for name, version in packages.items() if verified[name] != version]
        if remaining or not module_installed(office):
            raise RuntimeError(f"Setup verification failed: Python {remaining}; {office} installed={module_installed(office)}")
        if not (shutil.which("soffice") or shutil.which("libreoffice")):
            raise RuntimeError(f"{office} is installed but the LibreOffice executable is not on PATH")
        report["status"] = "READY"
        return report
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        report["status"] = "FAILED"
        report["error"] = str(error)
        raise
    finally:
        report["total_seconds"] = round(time.perf_counter() - started, 3)
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=PYTHON_PACKAGES)
    parser.add_argument("--charts", action="store_true", help="Include matplotlib for document chart images")
    parser.add_argument("--out", required=True, help="Local setup report JSON")
    parser.add_argument("--plan", action="store_true", help="Report missing packages without installing anything")
    args = parser.parse_args()
    try:
        report = setup(args.kind, args.charts, args.out, args.plan)
        print(json.dumps(report, ensure_ascii=False))
    except (ValueError, OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        parser.exit(1, f"setup_office: {error}\n")


if __name__ == "__main__":
    main()
