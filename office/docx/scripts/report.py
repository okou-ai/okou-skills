#!/usr/bin/env python3
"""Create and validate an editable DOCX from structured content."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

from render_docx import render


CLI = Path(__file__).resolve().parent / "docx.sh"


def record(log, **event):
    if log is not None:
        log.parent.mkdir(parents=True, exist_ok=True)
        with log.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, separators=(",", ":")) + "\n")


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


@contextmanager
def stage(log, name):
    started_at = utc_now()
    start = time.monotonic()
    status = "succeeded"
    record(log, phase=name, event="started", at=started_at)
    try:
        yield
    except BaseException:
        status = "failed"
        raise
    finally:
        record(log, phase=name, event="finished", at=utc_now(), status=status,
               duration_ms=round((time.monotonic() - start) * 1000))


def normalize_images(content, directory, timings):
    blocks = json.loads(content.read_text(encoding="utf-8-sig"))
    if not isinstance(blocks, list):
        return content
    images = [item for item in blocks if isinstance(item, dict) and item.get("type") == "image"
              and isinstance(item.get("path"), str)]
    if not any(Path(item["path"]).suffix.lower() == ".webp" for item in images):
        return content

    with stage(timings, "image_preparation"):
        try:
            from PIL import Image
        except ImportError:
            Image = None
        decoder = shutil.which("dwebp")
        if Image is None and not decoder:
            raise ValueError("WebP input requires Pillow or dwebp for PNG conversion.")
        for index, item in enumerate(images):
            source = (content.parent / item["path"]).resolve()
            if source.suffix.lower() == ".webp":
                target = directory / f"image-{index}.png"
                if Image is not None:
                    with Image.open(source) as picture:
                        picture.save(target, "PNG")
                else:
                    subprocess.run([decoder, str(source), "-o", str(target)],
                                   check=True, timeout=30)
                item["path"] = str(target)
            else:
                item["path"] = str(source)
        normalized = directory / "content.json"
        normalized.write_text(json.dumps(blocks, ensure_ascii=False), encoding="utf-8")
    return normalized


def build(args, cli=CLI):
    docx = args.output.resolve()
    pdf = args.pdf.resolve() if args.pdf else None
    paths = [path.resolve() for path in (args.content, docx, pdf, args.timings) if path is not None]
    if len(set(paths)) != len(paths):
        raise ValueError("Content, DOCX, PDF and timing paths must be distinct.")
    if docx.suffix.lower() != ".docx" or (pdf and pdf.suffix.lower() != ".pdf"):
        raise ValueError("Expected .docx for --output and .pdf for --pdf.")

    docx.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".report-", dir=docx.parent) as tmp_dir:
        temporary = Path(tmp_dir)
        temp_docx = temporary / "report.docx"
        content = normalize_images(args.content.resolve(), temporary, args.timings)
        with stage(args.timings, "docx_create"):
            subprocess.run(["bash", str(cli), "create", "--type", "report",
                            "--content-json", str(content), "--title", args.title,
                            "--page-size", args.page_size, "--page-numbers",
                            "--output", str(temp_docx)], check=True)
        with stage(args.timings, "docx_validate"):
            subprocess.run(["bash", str(cli), "validate", "--input", str(temp_docx),
                            "--business"], check=True)
        temp_docx.replace(docx)
        if pdf:
            with stage(args.timings, "docx_render"):
                render(docx, pdf)
    print(f"Ready: {docx}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    run = subparsers.add_parser("build", help="Create and validate the DOCX, optionally render it")
    run.add_argument("--content", type=Path, required=True)
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--title", required=True)
    run.add_argument("--page-size", choices=("letter", "a4", "legal", "a3"), default="letter")
    run.add_argument("--pdf", type=Path, help="Render the validated DOCX to this PDF")
    run.add_argument("--timings", type=Path, help="Append stage events as JSON Lines")

    mark = subparsers.add_parser("mark", help="Record nearby milestones outside the renderer")
    mark.add_argument("--timings", type=Path, required=True)
    mark.add_argument("phase", choices=("setup", "inputs", "analysis", "upload"))
    mark.add_argument("event", choices=("started", "finished", "failed"))

    args = parser.parse_args()
    try:
        if args.command == "mark":
            record(args.timings, phase=args.phase, event=args.event, at=utc_now())
        else:
            build(args)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
        print(f"Report workflow: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
