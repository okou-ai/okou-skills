#!/usr/bin/env python3
"""Convert a PDF deck with pdf2htmlEX, then use the shared HTML inventory."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen


RELEASE = "v0.18.8.rc1"
APPIMAGE = "pdf2htmlEX-0.18.8.rc1-master-20200630-Ubuntu-focal-x86_64.AppImage"
APPIMAGE_SHA256 = "11de2583a3abce5f141fd7fafb1fea2c67b15886e546d6b7675c600012e6ab8c"
URL = f"https://github.com/pdf2htmlEX/pdf2htmlEX/releases/download/{RELEASE}/{APPIMAGE}"


def converter_path(explicit=None):
    if explicit:
        executable = shutil.which(explicit)
        if not executable:
            raise ValueError(f"Converter is not executable: {explicit}")
        return Path(executable).resolve()
    installed = shutil.which("pdf2htmlEX")
    if installed:
        return Path(installed).resolve()
    if platform.system() != "Linux" or platform.machine() not in ("x86_64", "AMD64"):
        raise ValueError("Install pdf2htmlEX and pass --converter /path/to/pdf2htmlEX on this platform")
    cache = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    cache = (cache / "presentation-extract").resolve()
    target = cache / f"pdf2htmlEX-{APPIMAGE_SHA256[:12]}"
    executable = target / "AppRun"
    if executable.is_file():
        return executable
    cache.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="pdf2htmlEX-", dir=cache) as temporary:
        directory = Path(temporary)
        archive = directory / APPIMAGE
        print(f"Preparing pdf2htmlEX {RELEASE} in {cache}", file=sys.stderr)
        with urlopen(URL, timeout=60) as response, archive.open("wb") as output:
            shutil.copyfileobj(response, output)
        with archive.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        if digest != APPIMAGE_SHA256:
            raise ValueError("pdf2htmlEX download checksum mismatch")
        archive.chmod(0o755)
        subprocess.run([str(archive), "--appimage-extract"], cwd=directory,
                       check=True, stdout=subprocess.DEVNULL)
        # Extract once; running AppRun directly needs neither FUSE nor root.
        (directory / "squashfs-root").rename(target)
    return executable


def prepare(source, work, converter=None):
    started = time.monotonic()
    source, work = source.resolve(), work.resolve()
    with source.open("rb") as stream:
        if b"%PDF-" not in stream.read(1024):
            raise ValueError("--input must be the original PDF deck")
        stream.seek(0)
        source_hash = hashlib.file_digest(stream, "sha256").hexdigest()
    converted, inventory = work / "pdf-html", work / "html"
    for directory in (converted, inventory):
        if directory.exists() and (not directory.is_dir() or any(directory.iterdir())):
            raise ValueError(f"Choose a new work directory; preserving existing output: {directory}")
    executable = converter_path(converter)
    version = subprocess.run([str(executable), "--version"], check=True,
                             capture_output=True, text=True)
    converted.mkdir(parents=True, exist_ok=True)
    html = converted / "source.html"
    # External files change packaging only; keep the converter's visual defaults.
    command = [str(executable), "--dest-dir", str(converted)]
    data = executable.resolve().parent.parent / "local/share/pdf2htmlEX"
    if (data / "manifest").is_file():
        command += ["--data-dir", str(data), "--poppler-data-dir", str(data / "poppler")]
    for resource in ("css", "font", "image", "javascript", "outline"):
        command += [f"--embed-{resource}", "0"]
    command += [str(source), html.name]
    conversion_started = time.monotonic()
    log = converted / "conversion.log"
    with log.open("w") as output:
        subprocess.run(command, check=True, stdout=output, stderr=subprocess.STDOUT)
    converted_seconds = time.monotonic() - conversion_started
    helper = Path(__file__).with_name("inventory-html.py")
    result = subprocess.run([sys.executable, str(helper), "--input", str(html),
                             "--slide-class", "pf", "--stage-class", "pc",
                             "--text-class", "t", "--out", str(inventory)],
                            check=True, capture_output=True, text=True)
    summary = json.loads(result.stdout)
    receipt = {
        "sourceFilename": source.name, "sourcePath": str(source), "sourceSha256": source_hash,
        "converterVersion": (version.stdout + version.stderr).strip(), "command": command,
        "html": str(html), "inventory": summary["inventory"], "pageCount": summary["pageCount"],
        "conversionSeconds": round(converted_seconds, 3),
        "elapsedSeconds": round(time.monotonic() - started, 3),
    }
    (converted / "conversion.json").write_text(json.dumps(receipt, indent=2) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True,
                        help="Extraction work directory outside the saved template")
    parser.add_argument("--converter", help="Existing pdf2htmlEX executable; otherwise reuse or cache it")
    args = parser.parse_args()
    try:
        receipt = prepare(args.input, args.work_dir, args.converter)
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        detail = error.stderr if isinstance(error, subprocess.CalledProcessError) else None
        parser.exit(1, f"PDF preparation failed: {detail or error}\n"
                       f"Inspect {args.work_dir}/pdf-html/conversion.log if present.\n")
    print(json.dumps(receipt))


if __name__ == "__main__":
    main()
