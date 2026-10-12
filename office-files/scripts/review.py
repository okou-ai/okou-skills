#!/usr/bin/env python3
"""Batch-render actual DOCX/PDF files locally, reusing only unchanged renders."""

import argparse
import fcntl
import hashlib
import json
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from office_env import writer_state
from pypdf import PdfReader
from pypdf.errors import PdfReadError


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args, timeout=90):
    return subprocess.run(
        args, check=True, text=True, capture_output=True, timeout=timeout
    )


def environment():
    fonts = []
    if shutil.which("fc-list"):
        for name in sorted(
            set(run(["fc-list", "-f", "%{file}\n"]).stdout.splitlines())
        ):
            path = Path(name)
            fonts.append((name, path.stat().st_size, path.stat().st_mtime_ns))
    versions = {}
    for command in ("soffice", "pdftocairo", "okou"):
        if shutil.which(command):
            result = run([command, "-v" if command == "pdftocairo" else "--version"])
            versions[command] = result.stdout + result.stderr
    return {
        "versions": versions,
        "fonts": fonts,
        "writer": writer_state(),
        "script": digest(__file__),
    }


def render(source, cache, state):
    identity = json.dumps(
        {
            "source": digest(source),
            "format": source.suffix.lower(),
            "environment": state,
        },
        sort_keys=True,
    )
    key = hashlib.sha256(identity.encode()).hexdigest()
    cache.mkdir(parents=True, exist_ok=True)
    with (cache / f"{key}.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        return render_locked(source, cache, state, cache / key)


def render_locked(source, cache, state, directory):
    started = time.monotonic()
    manifest = directory / "render.json"
    if manifest.exists():
        prior = json.loads(manifest.read_text())
        if all(
            Path(p).exists() and digest(p) == expected
            for p, expected in prior["hashes"].items()
        ):
            return {**prior, "source": str(source), "cached": True}
    directory.mkdir(parents=True, exist_ok=True)
    result = {
        "source": str(source),
        "cached": False,
        "hashes": {},
        "visual_review": "required",
    }
    try:
        if source.suffix.lower() == ".docx":
            if not Path("/usr/lib/libreoffice/program/libswlo.so").exists():
                raise RuntimeError(
                    "Writer component missing; run office_env.py once with --install-missing"
                )
            pdf = directory / "source.pdf"
            # A fresh name/profile prevents stale PDFs and same-basename collisions.
            with tempfile.TemporaryDirectory(prefix="office-word-") as tmp:
                root = Path(tmp)
                shutil.copyfile(source, root / "source.docx")
                output = run(
                    [
                        "soffice",
                        f"-env:UserInstallation={(root / 'profile').as_uri()}",
                        "--headless",
                        "--convert-to",
                        "pdf:writer_pdf_Export",
                        "--outdir",
                        tmp,
                        str(root / "source.docx"),
                    ]
                )
                if not (root / "source.pdf").exists():
                    raise RuntimeError(
                        (output.stdout + output.stderr).strip()
                        or "Writer produced no PDF"
                    )
                shutil.copyfile(root / "source.pdf", pdf)
        else:
            pdf = directory / "source.pdf"
            shutil.copyfile(source, pdf)
        reader = PdfReader(pdf)
        sizes = [
            (round(float(p.mediabox.width)), round(float(p.mediabox.height)))
            for p in reader.pages
        ]
        if not sizes:
            raise RuntimeError("PDF has no pages")
        # PDF bytes + render environment are authoritative. Reuse these images
        # even when a requested PDF happens to equal the final Word export.
        image_key = hashlib.sha256(
            (digest(pdf) + json.dumps(state, sort_keys=True)).encode()
        ).hexdigest()
        images = cache / "pages" / image_key
        images.parent.mkdir(parents=True, exist_ok=True)
        with (images.parent / f"{image_key}.lock").open("a") as image_lock:
            fcntl.flock(image_lock, fcntl.LOCK_EX)
            image_manifest = images / "hashes.json"
            valid = False
            if image_manifest.exists():
                hashes = json.loads(image_manifest.read_text())
                valid = len(hashes) == len(sizes) and all(
                    (images / name).exists() and digest(images / name) == value
                    for name, value in hashes.items()
                )
            if not valid:
                images.mkdir(parents=True, exist_ok=True)
                for old in images.glob("*.png"):
                    old.unlink()
                if shutil.which("okou") and len(set(sizes)) == 1:
                    width, height = sizes[0]
                    run(
                        [
                            "okou",
                            "presentation",
                            "screenshot",
                            "--input",
                            str(pdf),
                            "--out",
                            str(images),
                            "--width",
                            str(width * 2),
                            "--height",
                            str(height * 2),
                            "--json",
                        ]
                    )
                else:
                    # The Okou screenshot command fixes all page dimensions. Preserve
                    # mixed portrait/landscape pages (and support non-Okou hosts).
                    run(
                        [
                            "pdftocairo",
                            "-png",
                            "-scale-to",
                            "1600",
                            str(pdf),
                            str(images / "page"),
                        ]
                    )
                pages = list(images.glob("*.png"))
                if len(pages) != len(sizes):
                    raise RuntimeError(
                        "Rendered image count does not match the PDF page count"
                    )
                hashes = {p.name: digest(p) for p in pages}
                image_manifest.write_text(json.dumps(hashes))
            pages = sorted(
                images.glob("*.png"), key=lambda p: int(p.stem.rsplit("-", 1)[-1])
            )
        result.update(
            {
                "pages": len(pages),
                "images": [str(p) for p in pages],
                "rendered_pdf": str(pdf),
            }
        )
        result["hashes"] = {str(p): digest(p) for p in [pdf] + pages}
    except (
        RuntimeError,
        PdfReadError,
        FileNotFoundError,
        subprocess.CalledProcessError,
        subprocess.TimeoutExpired,
    ) as error:
        # Cache failed probes too. Relevant file/environment changes produce a
        # different key; identical failed conversions are not retried in a loop.
        result["error"] = str(error)
        result["visual_review"] = "unverified"
    result["seconds"] = round(time.monotonic() - started, 3)
    manifest.write_text(json.dumps(result, indent=2))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path)
    parser.add_argument("--cache", type=Path, default=Path(".office-cache/review"))
    args = parser.parse_args()
    sources = list(dict.fromkeys(p.resolve() for p in args.files))
    if any(
        p.suffix.lower() not in (".docx", ".pdf") or not p.is_file() for p in sources
    ):
        parser.error("Provide existing DOCX/PDF files")
    state = environment()
    cache = args.cache.resolve()
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda source: render(source, cache, state), sources))
    # Keep this local output internal; rendering is not a visual-review pass.
    print(json.dumps(results, indent=2))
    return int(any("error" in result for result in results))


if __name__ == "__main__":
    raise SystemExit(main())
