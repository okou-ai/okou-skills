#!/usr/bin/env python3
"""Render DOCX; --check is read-only and --prepare provisions converters early."""
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
from typing import Optional
import zipfile


INSTALL_TIMEOUT = 600
PROBE_VERSION = 1
PROBE_MAX_AGE = 2 * 60 * 60


def writer_fingerprint() -> Optional[str]:
    """Bounded passive Writer identity: no tree walk, font scan or subprocess.

    Sample fixed installation/registry/package-DB paths and non-secret loader,
    locale, backend and temp-path settings. Unknown layouts/overrides miss safely.
    This is not exhaustive configuration monitoring: discard the explicit task
    receipt after any installation/configuration change, including font changes.
    """
    executable = find_soffice()
    if not executable or any(name in os.environ for name in ("URE_BOOTSTRAP", "UNO_SERVICES", "UNO_TYPES")):
        return None
    try:
        host = Path(executable).resolve(strict=True)
        program, installation = host.parent, host.parent.parent
        registries = [installation / "share/registry", installation / "Resources/registry"]
        markers = [program / "soffice.bin", program / "soffice.exe",
                   *(directory / name for directory in registries for name in ("writer.xcd", "main.xcd"))]
        paths = [Path(executable), host, program, installation / "Info.plist", Path(__file__),
                 *markers, *registries,
                 *(program / name for name in ("bootstraprc", "bootstrap.ini", "fundamentalrc",
                    "fundamental.ini", "services/services.rdb", "types/offapi.rdb",
                    "libmergedlo.so", "libmergedlo.dylib", "mergedlo.dll")),
                 Path("/etc/libreoffice/registry/writer.xcd"), Path("/etc/ld.so.cache"),
                 Path("/var/lib/dpkg/status"), Path("/var/lib/rpm/Packages"),
                 Path("/var/lib/rpm/rpmdb.sqlite"), Path("/usr/lib/sysimage/rpm/rpmdb.sqlite"),
                 Path("/lib/apk/db/installed")]
        entries, present = [], set()
        for path in dict.fromkeys(paths):
            try:
                link = path.lstat()
            except FileNotFoundError:
                entries.append((str(path), "missing"))
                continue
            stat = path.stat()  # Unreadable/dangling targets disable reuse.
            present.add(path)
            entries.append((str(path), str(path.resolve()), link.st_mtime_ns, link.st_ctime_ns,
                            stat.st_mode, stat.st_size, stat.st_mtime_ns, stat.st_ctime_ns,
                            stat.st_dev, stat.st_ino))
        if not any(marker in present for marker in markers):
            return None  # Opaque forwarding scripts/custom installs need a fresh control.
        relevant_environment = ("PATH", "HOME", "TMPDIR", "TEMP", "TMP", "SystemRoot",
                                "LANG", "LC_ALL", "LC_CTYPE", "LC_MESSAGES",
                                "LD_LIBRARY_PATH", "LD_PRELOAD", "DYLD_LIBRARY_PATH",
                                "DYLD_FALLBACK_LIBRARY_PATH", "SAL_USE_VCLPLUGIN",
                                "SAL_DISABLE_OPENCL", "DISPLAY", "WAYLAND_DISPLAY", "XDG_RUNTIME_DIR")
        payload = {"version": PROBE_VERSION, "files": entries,
                   "environment": {name: os.environ.get(name) for name in relevant_environment},
                   "cwd": str(Path.cwd()), "platform": sys.platform,
                   "uid": getattr(os, "geteuid", lambda: None)(),
                   "groups": getattr(os, "getgroups", lambda: [])()}
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    except (OSError, RuntimeError):
        return None


class WriterProbeCache:
    """Explicit, short-lived task receipt; stores only successful capability, not PDFs."""
    def __init__(self, path: Path, session: str):
        self.path = path
        self.session = hashlib.sha256(session.encode()).hexdigest()
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise RuntimeError("--probe-cache must be a regular task-local receipt file, not a symlink")
        if not path.parent.is_dir():
            raise RuntimeError("Create a private task directory before using --probe-cache")

    def invalidate(self):
        self.path.unlink(missing_ok=True)

    def matches(self, fingerprint):
        if fingerprint is None:
            self.invalidate()
            return False
        try:
            receipt = json.loads(self.path.read_text(encoding="utf-8"))
            valid = (receipt.get("version") == PROBE_VERSION and receipt.get("success") is True
                     and receipt.get("session") == self.session
                     and receipt.get("fingerprint") == fingerprint
                     and 0 <= time.time() - receipt["created"] <= PROBE_MAX_AGE)
        except (OSError, ValueError, KeyError, TypeError, AttributeError):
            valid = False
        if not valid:
            self.invalidate()
        return valid

    def save(self, fingerprint):
        if fingerprint is None:
            return
        receipt = {"version": PROBE_VERSION, "success": True, "session": self.session,
                   "fingerprint": fingerprint, "created": time.time()}
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.path.parent,
                                             prefix=".writer-receipt-", delete=False) as stream:
                temporary = Path(stream.name)
                json.dump(receipt, stream)
            os.replace(temporary, self.path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)


def probe_writer(timeout, cache=None):
    fingerprint = writer_fingerprint() if cache is not None else None
    if cache is not None and cache.matches(fingerprint):
        print("Writer capability: reused same-task success receipt", file=sys.stderr)
        return
    try:
        check_writer(timeout)
    except (RuntimeError, OSError, subprocess.SubprocessError):
        if cache is not None:
            cache.invalidate()
        raise
    if cache is not None and fingerprint == writer_fingerprint():
        cache.save(fingerprint)


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


def ensure_dependencies(*, pages: bool = False, install: bool = True, timeout: int = 60,
                        probe_cache=None) -> None:
    writer_error = None
    try:
        probe_writer(timeout, probe_cache)
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
    # Installing anything changes the environment; never stamp an old probe as new.
    if probe_cache is not None:
        probe_cache.invalidate()
    install_dependencies(writer=writer_error is not None, pages=bool(missing_poppler))
    # One installation attempt only. Never replay a failed user-document conversion.
    if writer_error or probe_cache is not None:
        try:
            probe_writer(timeout, probe_cache)
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
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Probe required converters without installing")
    mode.add_argument("--prepare", action="store_true", help="Prepare required converters without a user document")
    parser.add_argument("--no-install", action="store_true", help="Do not install missing rendering packages")
    parser.add_argument("--probe-cache", type=Path, help="Opt-in success receipt in a private directory for THIS task only")
    parser.add_argument("--probe-session", help="Unique task/session token; required with --probe-cache (expires after 2 hours)")
    args = parser.parse_args()
    if (args.probe_cache is None) != (args.probe_session is None):
        parser.error("--probe-cache and --probe-session must be supplied together")
    if args.probe_session is not None and not args.probe_session.strip():
        parser.error("--probe-session must not be empty")
    if args.check and args.probe_cache is not None:
        parser.error("--check is a fresh read-only probe; use --prepare to create/reuse a receipt")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    if args.prepare:
        if args.input is not None or args.out is not None:
            parser.error("--prepare does not accept an input document or --out")
    elif not args.check:
        if not args.input or not args.input.is_file() or not args.out:
            parser.error("an existing input DOCX and --out PDF path are required")
        if (args.input.resolve() == args.out.resolve()
                or (args.out.exists() and args.input.samefile(args.out))):
            parser.error("input and output must be different files")
        if args.out.is_dir():
            parser.error("--out must be a PDF file path, not a directory")
        if args.pages is not None and args.pages.exists() and not args.pages.is_dir():
            parser.error("--pages must be a directory path")
    if args.probe_cache is not None:
        for document in (args.input, args.out):
            if document is not None and (args.probe_cache.resolve() == document.resolve()
                    or (args.probe_cache.exists() and document.exists() and args.probe_cache.samefile(document))):
                parser.error("--probe-cache must not alias the input document or output PDF")
        if args.probe_cache.exists() and args.probe_cache.stat().st_nlink > 1:
            parser.error("--probe-cache must not be a hardlinked file")
    cache = None
    try:
        cache = WriterProbeCache(args.probe_cache, args.probe_session) if args.probe_cache is not None else None
        options = {"probe_cache": cache} if cache is not None else {}
        ensure_dependencies(pages=args.pages is not None,
                            install=not (args.check or args.no_install), timeout=args.timeout, **options)
        if args.check or args.prepare:
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
        if cache is not None:
            cache.invalidate()
        print(f"Rendering failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
