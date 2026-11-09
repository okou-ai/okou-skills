#!/usr/bin/env python3
"""Render DOCX with Writer; --check performs a real conversion, not a version check.
Optional OFFICE_SOFFICE selects an absolute executable; TMPDIR selects temporary workspace.
"""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile
import sys
import os

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from lo_safety import configure_lo_profile, prepare_input, reserve_output


def render(source: Path, destination: Path, timeout: int = 60) -> None:
    """Render only a validated private copy; refuse any existing destination."""
    with reserve_output(destination, source=source) as reservation:
        _render(Path(source), Path(destination), timeout, reservation)


def _render(source: Path, destination: Path, timeout: int, reservation) -> None:
    soffice = os.environ.get("OFFICE_SOFFICE")
    if soffice and (not Path(soffice).is_absolute() or not Path(soffice).is_file() or not os.access(soffice, os.X_OK)):
        raise ValueError("OFFICE_SOFFICE must name an absolute executable file; no fallback attempted")
    soffice = soffice or shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        mac = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")
        if mac.is_file():
            soffice = str(mac)
    if not soffice:
        raise RuntimeError("LibreOffice Writer is missing. Install libreoffice-writer (Linux).")
    with tempfile.TemporaryDirectory(prefix="docx_render_") as directory:
        work = Path(directory)
        copied = prepare_input(source, work / "source")
        output_dir = work / "output"
        output_dir.mkdir()
        profile_uri = configure_lo_profile(work / "profile")
        completed = subprocess.run(
            [soffice, f"-env:UserInstallation={profile_uri}",
             "--headless", "--norestore", "--convert-to", "pdf:writer_pdf_Export",
             "--outdir", str(output_dir), str(copied)],
            capture_output=True, text=True, timeout=timeout,
        )
        pdf = output_dir / f"{copied.stem}.pdf"
        if completed.returncode or not pdf.is_file() or not pdf.read_bytes().startswith(b"%PDF-"):
            raise RuntimeError(
                "Writer did not produce a PDF. Install libreoffice-writer; soffice/core alone "
                f"is insufficient.\n{completed.stdout}\n{completed.stderr}"
            )
        reservation.publish(pdf)


def check_writer() -> None:
    with tempfile.TemporaryDirectory(prefix="writer_check_") as directory:
        source = Path(directory) / "probe.docx"
        with zipfile.ZipFile(source, "w") as package:
            package.writestr("[Content_Types].xml", '''<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>''')
            package.writestr("_rels/.rels", '''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>''')
            package.writestr("word/document.xml", '''<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body><w:p><w:r><w:t>Writer conversion check</w:t></w:r></w:p></w:body></w:document>''')
        render(source, Path(directory) / "probe.pdf")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path)
    parser.add_argument("--out", type=Path, help="PDF output")
    parser.add_argument("--pages", type=Path, help="Also render page PNGs to this directory (Poppler)")
    parser.add_argument("--timeout", type=int, default=60)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        check_writer()
        print("LibreOffice Writer: DOCX-to-PDF conversion passed")
        return
    if not args.input or not args.input.is_file() or not args.out:
        parser.error("an existing input DOCX and --out PDF path are required")
    if args.input.resolve() == args.out.resolve():
        parser.error("input and output must be different files")
    render(args.input, args.out, args.timeout)
    if args.pages:
        # Poppler writes many files: only ever target a NEW directory.
        args.pages.mkdir(parents=True, exist_ok=False)
        subprocess.run(["pdftoppm", "-png", "-r", "120", str(args.out),
                        str(args.pages / "page")], check=True, timeout=args.timeout)
    print(f"Rendered: {args.out}")


if __name__ == "__main__":
    main()
