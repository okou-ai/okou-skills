#!/usr/bin/env python3
"""Render DOCX with on-demand dependencies; --check never installs packages."""
import argparse
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
from typing import Optional
import zipfile


INSTALL_TIMEOUT = 600


class WriterUnavailableError(RuntimeError):
    """The known-good DOCX probe could not be converted by this runtime."""


def find_soffice() -> Optional[str]:
    executable = shutil.which("soffice") or shutil.which("libreoffice")
    if executable:
        return executable
    candidates = [Path("/Applications/LibreOffice.app/Contents/MacOS/soffice"),
                  Path.home() / "Applications/LibreOffice.app/Contents/MacOS/soffice"]
    if platform.system() == "Windows":
        for variable in ("ProgramFiles", "ProgramFiles(x86)"):
            if os.environ.get(variable):
                directory = Path(os.environ[variable]) / "LibreOffice/program"
                candidates.extend((directory / "soffice.com", directory / "soffice.exe"))
    return next((str(path) for path in candidates if path.is_file()), None)


def render(source: Path, destination: Path, timeout: int = 60) -> None:
    """Convert once. Dependency repair belongs to the preflight, not document errors."""
    soffice = find_soffice()
    if not soffice:
        raise RuntimeError("LibreOffice Writer is missing; no soffice/libreoffice executable was found.")
    with tempfile.TemporaryDirectory(prefix="docx_render_") as directory:
        work = Path(directory)
        completed = subprocess.run(
            [soffice, f"-env:UserInstallation={(work / 'profile').as_uri()}",
             "--headless", "--norestore", "--convert-to", "pdf:writer_pdf_Export",
             "--outdir", str(work), str(source.resolve())],
            capture_output=True, text=True, timeout=timeout,
        )
        pdf = work / f"{source.stem}.pdf"
        if completed.returncode or not pdf.is_file() or not pdf.read_bytes().startswith(b"%PDF-"):
            raise RuntimeError(
                f"Writer did not produce a valid PDF for {source.name} "
                f"(exit {completed.returncode}).\n{completed.stdout}\n{completed.stderr}"
            )
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(pdf, destination)


def check_writer(timeout: int = 60) -> None:
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
        try:
            render(source, Path(directory) / "probe.pdf", timeout)
        except RuntimeError as error:
            # A valid probe distinguishes an unavailable Writer filter from a bad user document.
            # Timeouts, permission errors, etc. propagate rather than triggering installation.
            raise WriterUnavailableError(f"Writer DOCX-to-PDF probe failed: {error}") from error


def install_dependencies(*, writer: bool, pages: bool) -> None:
    """Provision only rendering packages; never invoke the full DOCX/.NET setup."""
    if not writer and not pages:
        return
    system = platform.system()
    commands = []
    if system == "Darwin":
        brew = shutil.which("brew")
        if not brew:
            raise RuntimeError("Automatic rendering setup needs Homebrew on macOS. Install Writer"
                               " (and Poppler for --pages) manually, then use --no-install.")
        if writer:
            commands.append([brew, "install", "--cask", "libreoffice"])
        if pages:
            commands.append([brew, "install", "poppler"])
    elif system == "Linux":
        # Package names differ across distributions; keep plans explicit and shell-free.
        managers = {
            "apt-get": ("libreoffice-writer", "poppler-utils", ["install", "-y", "--no-install-recommends"]),
            "dnf": ("libreoffice-writer", "poppler-utils", ["install", "-y"]),
            "pacman": ("libreoffice-still", "poppler", ["-S", "--noconfirm", "--needed"]),
            "zypper": ("libreoffice-writer", "poppler-tools", ["--non-interactive", "install"]),
            "apk": ("libreoffice-writer", "poppler-utils", ["add", "--no-cache"]),
        }
        manager = next((name for name in managers if shutil.which(name)), None)
        if not manager:
            raise RuntimeError("No supported package manager found. Install LibreOffice Writer"
                               " (and pdftoppm for --pages) manually, then use --no-install.")
        writer_package, pages_package, options = managers[manager]
        packages = ([writer_package] if writer else []) + ([pages_package] if pages else [])
        prefix = []
        if os.geteuid() != 0:
            sudo = shutil.which("sudo")
            if not sudo:
                raise RuntimeError("Installing rendering dependencies requires root or noninteractive"
                                   " sudo. Install them manually, then use --no-install.")
            prefix = [sudo, "-n", "--"]
        if manager == "apt-get":
            commands.append([*prefix, shutil.which(manager), "update"])
        commands.append([*prefix, shutil.which(manager), *options, *packages])
    else:
        raise RuntimeError(f"Automatic rendering setup is not supported on {system}. Install"
                           " LibreOffice Writer (and pdftoppm for --pages) manually; on Windows"
                           " add Poppler's bin directory to PATH. Then use --no-install.")

    needed = ", ".join(name for name, required in (("Writer", writer), ("Poppler", pages)) if required)
    print(f"Installing rendering dependencies: {needed}", file=sys.stderr, flush=True)
    for command in commands:
        try:
            subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                           start_new_session=True,
                           env={**os.environ, "DEBIAN_FRONTEND": "noninteractive",
                                "NONINTERACTIVE": "1", "HOMEBREW_NO_AUTO_UPDATE": "1"},
                           timeout=INSTALL_TIMEOUT)
        except subprocess.CalledProcessError as error:
            raise RuntimeError(
                f"Rendering dependency installation failed (exit {error.returncode}). "
                "Check package/network access and noninteractive sudo permissions. "
                f"No user-document conversion was attempted.\n{(error.stdout or '')[-4000:]}"
            ) from error
        except subprocess.TimeoutExpired as error:
            raise RuntimeError(f"Rendering dependency installation timed out after {INSTALL_TIMEOUT}s;"
                               " package-manager children may still be running and partial changes"
                               " may remain. No user-document conversion was attempted. Check the"
                               " package transaction before retrying; no rollback is implied.") from error
        except OSError as error:
            raise RuntimeError(f"Could not start rendering dependency installer: {error}") from error


def ensure_dependencies(*, pages: bool = False, install: bool = True, timeout: int = 60) -> None:
    writer_error = None
    try:
        check_writer(timeout)
    except WriterUnavailableError as error:
        writer_error = error
    missing_poppler = pages and not shutil.which("pdftoppm")
    if writer_error is None and not missing_poppler:
        return
    if not install:
        problems = ([str(writer_error)] if writer_error else [])
        if missing_poppler:
            problems.append("Poppler's pdftoppm is missing (required by --pages).")
        raise RuntimeError("\n".join(problems) + "\nDependency installation is disabled.")

    if writer_error:
        print(str(writer_error), file=sys.stderr)
    install_dependencies(writer=writer_error is not None, pages=bool(missing_poppler))
    # One installation attempt only. Never replay a failed user-document conversion.
    if writer_error:
        try:
            check_writer(timeout)
        except WriterUnavailableError as error:
            raise RuntimeError(f"Writer is still unavailable after dependency installation; "
                               f"no further installation was attempted.\n{error}") from error
    if pages and not shutil.which("pdftoppm"):
        raise RuntimeError("Poppler installation did not provide pdftoppm on PATH; "
                           "no user-document conversion was attempted.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", type=Path)
    parser.add_argument("--out", type=Path, help="PDF output")
    parser.add_argument("--pages", type=Path, help="Also render page PNGs to this directory (needs Poppler)")
    parser.add_argument("--timeout", type=int, default=60, help="Conversion timeout in seconds (default: 60)")
    parser.add_argument("--check", action="store_true", help="Probe required converters without installing")
    parser.add_argument("--no-install", action="store_true", help="Do not install missing rendering packages")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if not args.check:
        if not args.input or not args.input.is_file() or not args.out:
            parser.error("an existing input DOCX and --out PDF path are required")
        if (args.input.resolve() == args.out.resolve()
                or (args.out.exists() and args.input.samefile(args.out))):
            parser.error("input and output must be different files")
        if args.out.is_dir():
            parser.error("--out must be a PDF file path, not a directory")
        if args.pages is not None and args.pages.exists() and not args.pages.is_dir():
            parser.error("--pages must be a directory path")
    try:
        ensure_dependencies(pages=args.pages is not None,
                            install=not (args.check or args.no_install), timeout=args.timeout)
        if args.check:
            print("LibreOffice Writer: DOCX-to-PDF conversion passed")
            if args.pages is not None:
                print("Poppler: pdftoppm available")
            return
        render(args.input, args.out, args.timeout)
        if args.pages is not None:
            args.pages.mkdir(parents=True, exist_ok=True)
            try:
                subprocess.run(["pdftoppm", "-png", "-r", "120", str(args.out.resolve()),
                                str((args.pages / "page").resolve())], check=True, timeout=args.timeout)
            except (OSError, subprocess.SubprocessError) as error:
                raise RuntimeError(f"PDF rendered to {args.out}, but page rasterization failed: "
                                   f"{error}") from error
        print(f"Rendered: {args.out}")
    except (RuntimeError, OSError, subprocess.SubprocessError) as error:
        print(f"Rendering failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
