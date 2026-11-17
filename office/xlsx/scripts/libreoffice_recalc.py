#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
libreoffice_recalc.py — Tier 2 dynamic formula recalculation via LibreOffice headless.

Loads and exports xlsx files with the LibreOffice Calc engine to refresh formula
caches. Calculation behavior and workbook fidelity are engine-specific; writing
an output file alone does not establish formula correctness or Excel compatibility.

After recalculation, run formula_check.py on the output file to detect runtime errors
(#DIV/0!, #N/A, etc.) that only surface after actual computation.

Usage:
    python3 libreoffice_recalc.py input.xlsx output.xlsx
    python3 libreoffice_recalc.py input.xlsx output.xlsx --timeout 90
    python3 libreoffice_recalc.py --check          # binary/version availability only
    python3 libreoffice_recalc.py --preflight      # independent synthetic formula control

Exit codes:
    0 — output written, availability check passed, or synthetic control actually passed
    2 — LibreOffice binary not found (Tier 2 unavailable; note in report)
    1 — recalculation or synthetic control failed (including missing Calc)

A passing preflight tests only its own small control, not a candidate workbook or
full Excel compatibility. No mode installs software or retries a failed conversion.
"""

import subprocess
import sys
import shutil
import os
import tempfile
import argparse
from decimal import Decimal, InvalidOperation
from pathlib import Path
import posixpath
import signal
import stat
import xml.etree.ElementTree as ET
import zipfile
import hashlib
import json
import time


class CalculationSession:
    """Explicit task-scoped environment evidence; never caches candidate results.

    A receipt is opt-in, valid for at most two hours, and bound to a caller's task
    ID plus bounded executable/install metadata, allowlisted non-secret settings
    and control-script metadata. No recursive scan, environment dump or version
    command forms the fingerprint. Unknown layouts/bootstrap overrides cannot
    reuse capability. Delete receipts after any other dependency/configuration
    change (including fonts). This is local evidence, not exhaustive monitoring,
    a signed attestation or a portable guarantee.
    """
    def __init__(self, receipt_path: str | None = None, task_id: str | None = None):
        if receipt_path and not task_id:
            raise ValueError("A receipt requires an explicit task ID")
        self.receipt_path = Path(receipt_path) if receipt_path else None
        self.task_id = task_id
        self.versions = {}
        self.passed = {}

    def fingerprint(self, soffice: str) -> str | None:
        """Fixed passive samples only; an unknown identity is never a cache key."""
        overrides = ('URE_BOOTSTRAP', 'UNO_SERVICES', 'UNO_TYPES', 'UNO_PATH',
                     'URE_MORE_SERVICES', 'URE_MORE_TYPES', 'BRAND_BASE_DIR',
                     'BRAND_INI_DIR', 'SAL_CONFIGFILE')
        if any(name in os.environ for name in overrides):
            return None  # Do not interpret arbitrary bootstrap/configuration paths.
        try:
            executable = Path(soffice).absolute()
            binary = executable.resolve(strict=True)
            program, installation = binary.parent, binary.parent.parent
            if program.name not in ('program', 'MacOS') or not binary.is_file():
                return None  # Opaque launchers/custom layouts need a fresh control.
            registries = [installation / 'share/registry', installation / 'Resources/registry']
            markers = [program / 'soffice.bin', program / 'soffice.exe',
                       *(directory / name for directory in registries
                         for name in ('calc.xcd', 'main.xcd'))]
            script = Path(__file__).resolve(strict=True)
            paths = [executable, binary, program, installation, script,
                     installation / 'Info.plist', *registries, *markers,
                     *(program / name for name in (
                         'bootstraprc', 'bootstrap.ini', 'fundamentalrc', 'fundamental.ini',
                         'unorc', 'uno.ini', 'services/services.rdb', 'types/offapi.rdb',
                         'libmergedlo.so', 'libmergedlo.dylib', 'mergedlo.dll',
                         'libsclo.so', 'libsclo.dylib', 'sclo.dll',
                         'libscfiltlo.so', 'libscfiltlo.dylib', 'scfiltlo.dll')),
                     Path('/etc/libreoffice/registry/calc.xcd'), Path('/etc/ld.so.cache'),
                     Path('/var/lib/dpkg/status'), Path('/var/lib/rpm/Packages'),
                     Path('/var/lib/rpm/rpmdb.sqlite'), Path('/usr/lib/sysimage/rpm/rpmdb.sqlite'),
                     Path('/lib/apk/db/installed')]
            records, present = [], set()
            for path in dict.fromkeys(paths):
                try:
                    link = path.lstat()
                except FileNotFoundError:
                    records.append((str(path), 'missing'))
                    continue
                # A dangling/uninspectable link is unknown, not a stable missing file.
                is_link = stat.S_ISLNK(link.st_mode)
                target = path.resolve(strict=True) if is_link else path
                info = path.stat() if is_link else link
                present.add(path)
                records.append((str(path), str(target), link.st_mtime_ns, link.st_ctime_ns,
                                info.st_mode, info.st_dev, info.st_ino, info.st_size,
                                info.st_mtime_ns, info.st_ctime_ns))
            if script not in present or not any(marker in present for marker in markers):
                return None
            settings = ('PATH', 'HOME', 'TMPDIR', 'TEMP', 'TMP', 'SystemRoot',
                        'LANG', 'LANGUAGE', 'LC_ALL', 'LC_CTYPE', 'LC_MESSAGES',
                        'LC_NUMERIC', 'LC_TIME', 'LC_MONETARY', 'TZ',
                        'LD_LIBRARY_PATH', 'LD_PRELOAD', 'DYLD_LIBRARY_PATH',
                        'DYLD_FALLBACK_LIBRARY_PATH', 'SAL_USE_VCLPLUGIN',
                        'SAL_DISABLE_OPENCL', 'DISPLAY', 'WAYLAND_DISPLAY', 'XDG_RUNTIME_DIR')
            payload = {'schema': 2, 'task_id': self.task_id, 'paths': records,
                       'environment': {name: os.environ.get(name) for name in settings},
                       'cwd': str(Path.cwd()), 'platform': sys.platform,
                       'uid': getattr(os, 'geteuid', lambda: None)(),
                       'groups': getattr(os, 'getgroups', lambda: [])()}
            return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
        except (OSError, RuntimeError):
            return None

    def _read_receipt(self) -> dict | None:
        if not self.receipt_path or self.receipt_path.is_symlink():
            return None
        try:
            entry = json.loads(self.receipt_path.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            return None
        if (not isinstance(entry, dict) or entry.get('schema') != 1
                or entry.get('status') != 'passed' or entry.get('formula') != CONTROL_FORMULA
                or entry.get('expected') != '42' or not isinstance(entry.get('fingerprint'), str)):
            return None
        return entry

    def load(self, fingerprint: str | None) -> dict | None:
        if fingerprint is None:
            return None
        entry = self.passed.get(fingerprint) or self._read_receipt()
        if entry is None:
            return None
        if not isinstance(entry, dict) or not isinstance(entry.get('checked_at'), (int, float)):
            return None
        if (entry.get('schema') != 1 or entry.get('fingerprint') != fingerprint
                or entry.get('task_id') != self.task_id or entry.get('status') != 'passed'
                or not 0 <= time.time() - entry.get('checked_at', 0) <= 7200
                or entry.get('formula') != CONTROL_FORMULA or entry.get('expected') != '42'):
            return None
        self.versions[fingerprint] = entry.get('version', 'unknown')
        return entry

    def version(self, soffice: str) -> str:
        # Ordinary candidate conversion does not need a capability fingerprint.
        # Version metadata is process/session-local and never certifies Calc.
        if self.receipt_path:
            fingerprint = self.fingerprint(soffice)
            if self.load(fingerprint):
                return self.versions[fingerprint]
        try:
            executable = Path(soffice).absolute()
            binary = executable.resolve(strict=True)
            link, info = executable.lstat(), binary.stat()
            key = ('version', str(executable), str(binary), link.st_mtime_ns, link.st_ctime_ns,
                   info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
        except (OSError, RuntimeError):
            # Even an unavailable version label may be reused within this session;
            # this key is never accepted by load()/record() as capability evidence.
            key = ('version-uninspectable', soffice)
        if key not in self.versions:
            self.versions[key] = get_libreoffice_version(soffice)
        return self.versions[key]

    def record(self, fingerprint: str | None, version: str) -> None:
        if fingerprint is None:
            return
        entry = {'schema': 1, 'status': 'passed', 'task_id': self.task_id,
                 'fingerprint': fingerprint, 'checked_at': time.time(), 'version': version,
                 'formula': CONTROL_FORMULA, 'expected': '42'}
        self.passed[fingerprint] = entry
        if self.receipt_path:
            if os.path.lexists(self.receipt_path) and self._read_receipt() is None:
                raise ValueError("Receipt must be a new path or a recognized control receipt; refusing overwrite")
            self.receipt_path.parent.mkdir(parents=True, exist_ok=True)
            # Explicit receipt only; never a global home-directory cache.
            fd, temporary = tempfile.mkstemp(prefix='.calc-receipt-', dir=self.receipt_path.parent)
            try:
                with os.fdopen(fd, 'w', encoding='utf-8') as stream:
                    json.dump(entry, stream, indent=2)
                os.replace(temporary, self.receipt_path)
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)

    def invalidate(self) -> None:
        self.versions.clear()
        self.passed.clear()
        entry = self._read_receipt()
        if entry and entry.get('task_id') == self.task_id:
            self.receipt_path.unlink(missing_ok=True)


# ── LibreOffice discovery ───────────────────────────────────────────────────

def find_soffice() -> str | None:
    """
    Locate the soffice (LibreOffice) binary.

    Search order:
      1. macOS application bundle (default install location)
      2. PATH lookup for 'soffice'
      3. PATH lookup for 'libreoffice' (common on Linux)
    """
    candidates = [
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",  # macOS
        "soffice",     # Linux / macOS if on PATH
        "libreoffice", # alternative Linux name
    ]
    for c in candidates:
        # shutil.which handles PATH lookup; also check absolute paths directly
        found = shutil.which(c)
        if found:
            return found
        if os.path.isfile(c) and os.access(c, os.X_OK):
            return c
    return None


def _run_soffice(cmd: list[str], timeout: int) -> subprocess.CompletedProcess:
    """Run once; reap the child and stop only this invocation's POSIX process group.

    A separate session prevents a timeout from leaving soffice.bin using a profile
    about to be deleted. Never scan for or kill other LibreOffice instances. On
    non-POSIX systems only the directly owned child can be killed with the stdlib.
    """
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=(os.name == "posix"),
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
        return subprocess.CompletedProcess(cmd, process.returncode, stdout, stderr)
    finally:
        try:
            if os.name == "posix":
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass  # The owned group already exited.
            elif process.poll() is None:
                process.kill()
        finally:
            process.wait()
            if process.stdout is not None:
                process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()


def get_libreoffice_version(soffice: str) -> str:
    """Return the version, or 'unknown'; this is not a formula evaluation test."""
    try:
        with tempfile.TemporaryDirectory(prefix="xlsx_lo_version_") as tmpdir:
            profile = (Path(tmpdir) / "profile").as_uri()
            result = _run_soffice(
                [soffice, f"-env:UserInstallation={profile}", "--headless", "--version"],
                timeout=10,
            )
        return result.stdout.decode(errors="replace").strip()
    except Exception:
        return "unknown"


def calc_component_diagnostic(soffice: str) -> str:
    """Give a read-only hint for a recognized split-package installation layout.

    Missing registry evidence is a diagnostic, not an alternative to the actual
    formula control. Unknown layouts make no claim about Calc availability.
    """
    program = Path(soffice).resolve().parent
    registry = program.parent / "share" / "registry"
    if (program.name == "program"
            and (registry / "main.xcd").is_file()
            and not (registry / "calc.xcd").is_file()):
        return (
            f"Calc component appears missing: {registry / 'calc.xcd'} is absent "
            "in this LibreOffice registry layout. Core/Writer/Impress alone cannot "
            "recalculate XLSX formulas. On Debian/Ubuntu the component is packaged "
            "as libreoffice-calc (or libreoffice-calc-nogui). No installation was "
            "attempted; obtain authorization under the environment's software policy "
            "before adding components."
        )
    return ""


# ── Recalculation ───────────────────────────────────────────────────────────

def recalculate(input_path: str, output_path: str, timeout: int = 60,
                session: CalculationSession | None = None) -> tuple[bool, str]:
    """Always execute this candidate; invalidate environment evidence on failure."""
    session = session or CalculationSession()
    if session.receipt_path:
        for candidate in (Path(input_path), Path(output_path)):
            if (session.receipt_path.resolve() == candidate.resolve()
                    or (session.receipt_path.exists() and candidate.exists()
                        and os.path.samefile(session.receipt_path, candidate))):
                return False, "Receipt must be distinct from candidate input/output; no files changed."
    try:
        result = _recalculate(input_path, output_path, timeout, session)
    except Exception:
        session.invalidate()
        raise
    if not result[0]:
        session.invalidate()
    return result


def _recalculate(
    input_path: str,
    output_path: str,
    timeout: int,
    session: CalculationSession,
) -> tuple[bool, str]:
    """
    Run LibreOffice headless recalculation on input_path, write result to output_path.

    Returns:
        (success: bool, message: str)

    The message explains what happened (success or failure reason).
    """
    if (Path(input_path).resolve() == Path(output_path).resolve()
            or (Path(output_path).exists() and os.path.samefile(input_path, output_path))):
        return False, "Input and output must be distinct; the source is never overwritten."
    soffice = find_soffice()
    if not soffice:
        return False, (
            "LibreOffice not found. Tier 2 validation is unavailable in this environment. "
            "LibreOffice with the Calc component is required. No installation was attempted; "
            "obtain authorization under the environment's software policy before adding software."
        )

    version = session.version(soffice)

    # Work on a copy in a temp directory to avoid side effects on the source file.
    # LibreOffice writes the output using the same filename stem in --outdir.
    with tempfile.TemporaryDirectory(prefix="xlsx_recalc_") as tmpdir:
        # Never convert onto the input: soffice can exit 0 after refusing an overwrite.
        source_dir = Path(tmpdir) / "source"
        output_dir = Path(tmpdir) / "output"
        source_dir.mkdir()
        output_dir.mkdir()
        profile = Path(tmpdir) / "profile"
        (profile / "user").mkdir(parents=True)
        # Calc otherwise trusts Excel's cached values. RecalcMode 0 = ALWAYS.
        (profile / "user/registrymodifications.xcu").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>'
            '<oor:items xmlns:oor="http://openoffice.org/2001/registry">'
            '<item oor:path="/org.openoffice.Office.Calc/Formula/Load">'
            '<prop oor:name="OOXMLRecalcMode" oor:op="fuse"><value>0</value></prop>'
            '</item></oor:items>',
            encoding="utf-8",
        )
        tmp_input = str(source_dir / os.path.basename(input_path))
        shutil.copy(input_path, tmp_input)

        cmd = [
            soffice,
            f"-env:UserInstallation={profile.as_uri()}",
            "--headless",
            "--norestore",           # do not attempt to restore crashed sessions
            "--infilter=Calc MS Excel 2007 XML",
            "--convert-to", "xlsx",
            "--outdir", str(output_dir),
            tmp_input,
        ]

        try:
            result = _run_soffice(cmd, timeout=timeout)
        except subprocess.TimeoutExpired:
            return False, (
                f"LibreOffice timed out after {timeout}s. "
                "The file may be too large or contain constructs that cause LibreOffice to hang. "
                "Try increasing --timeout or simplify the file."
            )
        except FileNotFoundError:
            return False, f"LibreOffice binary not executable: {soffice}"

        if result.returncode != 0:
            stderr = result.stderr.decode(errors="replace").strip()
            stdout = result.stdout.decode(errors="replace").strip()
            diagnostic = calc_component_diagnostic(soffice)
            return False, (
                f"LibreOffice exited with code {result.returncode}.\n"
                f"stderr: {stderr}\n"
                f"stdout: {stdout}"
                + (f"\n{diagnostic}" if diagnostic else "")
            )

        # Only a newly created output in the separate output directory is success.
        stem = os.path.splitext(os.path.basename(tmp_input))[0]
        tmp_output = str(output_dir / (stem + ".xlsx"))

        if not os.path.isfile(tmp_output):
            stdout = result.stdout.decode(errors="replace").strip()
            stderr = result.stderr.decode(errors="replace").strip()
            diagnostic = calc_component_diagnostic(soffice)
            return False, (
                "LibreOffice exited 0 but produced no recalculated workbook. "
                "LibreOffice Calc and its XLSX filters are required, not just the core binary. "
                "No installation was attempted.\n"
                f"stdout: {stdout}\nstderr: {stderr}"
                + (f"\n{diagnostic}" if diagnostic else "")
            )

        # Copy recalculated file to final destination
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        shutil.copy(tmp_output, output_path)

    return True, f"Recalculation complete. LibreOffice {version}. Output: {output_path}"


# ── Independent synthetic control ──────────────────────────────────────────

S = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
P = "{http://schemas.openxmlformats.org/package/2006/relationships}"
CONTROL_FORMULA = "SUM(A1:B1)"
CONTROL_EXPECTED = Decimal(42)


def _write_preflight_workbook(path: Path) -> None:
    """Build a complete minimal package from scratch, without starters or libraries.

    The only formula cache is EMPTY. Copying this input can never satisfy the
    expected nonzero result; an engine must compute 19 + 23 and retain the formula.
    """
    content_types = ET.Element(
        "Types", xmlns="http://schemas.openxmlformats.org/package/2006/content-types",
    )
    ET.SubElement(content_types, "Default", Extension="rels",
                  ContentType="application/vnd.openxmlformats-package.relationships+xml")
    ET.SubElement(content_types, "Default", Extension="xml", ContentType="application/xml")
    for part, kind in (
        ("/xl/workbook.xml", "sheet.main"),
        ("/xl/worksheets/sheet1.xml", "worksheet"),
    ):
        ET.SubElement(content_types, "Override", PartName=part,
                      ContentType=f"application/vnd.openxmlformats-officedocument.spreadsheetml.{kind}+xml")

    root_rels = ET.Element(f"{P}Relationships")
    ET.SubElement(root_rels, f"{P}Relationship", Id="rId1",
                  Type=f"{R[1:-1]}/officeDocument", Target="xl/workbook.xml")
    workbook = ET.Element(f"{S}workbook")
    sheets = ET.SubElement(workbook, f"{S}sheets")
    ET.SubElement(sheets, f"{S}sheet", name="Preflight", sheetId="1", attrib={f"{R}id": "rId1"})
    ET.SubElement(workbook, f"{S}calcPr", calcMode="auto", fullCalcOnLoad="1", forceFullCalc="1")
    workbook_rels = ET.Element(f"{P}Relationships")
    ET.SubElement(workbook_rels, f"{P}Relationship", Id="rId1",
                  Type=f"{R[1:-1]}/worksheet", Target="worksheets/sheet1.xml")
    worksheet = ET.Element(f"{S}worksheet")
    data = ET.SubElement(worksheet, f"{S}sheetData")
    row = ET.SubElement(data, f"{S}row", r="1")
    for address, value in (("A1", "19"), ("B1", "23")):
        cell = ET.SubElement(row, f"{S}c", r=address)
        ET.SubElement(cell, f"{S}v").text = value
    formula_cell = ET.SubElement(row, f"{S}c", r="C1")
    ET.SubElement(formula_cell, f"{S}f").text = CONTROL_FORMULA
    ET.SubElement(formula_cell, f"{S}v")  # intentionally no cached answer

    parts = {
        "[Content_Types].xml": content_types,
        "_rels/.rels": root_rels,
        "xl/workbook.xml": workbook,
        "xl/_rels/workbook.xml.rels": workbook_rels,
        "xl/worksheets/sheet1.xml": worksheet,
    }
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as package:
        for name, root in parts.items():
            package.writestr(name, ET.tostring(root, encoding="utf-8", xml_declaration=True))


def _verify_preflight_output(path: Path) -> None:
    """Reopen the produced OOXML; require the expected live formula AND its cache."""
    with zipfile.ZipFile(path) as package:
        types_namespace = "{http://schemas.openxmlformats.org/package/2006/content-types}"
        content_types = ET.fromstring(package.read("[Content_Types].xml"))
        if content_types.tag != f"{types_namespace}Types":
            raise ValueError("Output has no OOXML content types")
        overrides = {item.get("PartName"): item.get("ContentType")
                     for item in content_types.findall(f"{types_namespace}Override")}
        prefix = "application/vnd.openxmlformats-officedocument.spreadsheetml."
        if overrides.get("/xl/workbook.xml") != f"{prefix}sheet.main+xml":
            raise ValueError("Output lost the XLSX workbook content type")
        root_rels = ET.fromstring(package.read("_rels/.rels"))
        if root_rels.tag != f"{P}Relationships" or not any(
            rel.get("Type") == f"{R[1:-1]}/officeDocument"
            and rel.get("TargetMode") != "External"
            and rel.get("Target", "").lstrip("/") == "xl/workbook.xml"
            for rel in root_rels.findall(f"{P}Relationship")
        ):
            raise ValueError("Output lost the internal OOXML workbook relationship")
        workbook = ET.fromstring(package.read("xl/workbook.xml"))
        if workbook.tag != f"{S}workbook":
            raise ValueError("Output has no OOXML workbook root")
        sheet = workbook.find(f"{S}sheets/{S}sheet[@name='Preflight']")
        if sheet is None:
            raise ValueError("Output lost the Preflight worksheet")
        rels = ET.fromstring(package.read("xl/_rels/workbook.xml.rels"))
        if rels.tag != f"{P}Relationships":
            raise ValueError("Output has no OOXML workbook relationships")
        relationship = next((rel for rel in rels.findall(f"{P}Relationship")
                             if rel.get("Id") == sheet.get(f"{R}id")), None)
        if (relationship is None or relationship.get("TargetMode") == "External"
                or relationship.get("Type") != f"{R[1:-1]}/worksheet"):
            raise ValueError("Output lost the internal Preflight worksheet relationship")
        target = relationship.get("Target", "")
        part = posixpath.normpath(target.lstrip("/") if target.startswith("/")
                                  else posixpath.join("xl", target))
        if not target or part.startswith("../") or "\\" in part:
            raise ValueError("Output has an invalid Preflight worksheet target")
        if overrides.get(f"/{part}") != f"{prefix}worksheet+xml":
            raise ValueError("Output lost the Preflight worksheet content type")
        worksheet = ET.fromstring(package.read(part))
        if worksheet.tag != f"{S}worksheet":
            raise ValueError("Output has no OOXML worksheet root")
        cell = worksheet.find(f"{S}sheetData/{S}row/{S}c[@r='C1']")
        if cell is None:
            raise ValueError("Output lost Preflight!C1")
        formula = cell.find(f"{S}f")
        if formula is None or (formula.text or "").strip() != CONTROL_FORMULA:
            raise ValueError(f"Output lost the live formula {CONTROL_FORMULA!r} at Preflight!C1")
        cache = cell.find(f"{S}v")
        text = "" if cache is None else (cache.text or "").strip()
        if cell.get("t", "n") != "n" or not text:
            raise ValueError(f"Preflight!C1 needs a numeric cache of {CONTROL_EXPECTED}; "
                             f"found type={cell.get('t', 'n')!r}, cache={text!r}")
        try:
            value = Decimal(text)
        except InvalidOperation as exc:
            raise ValueError(f"Preflight!C1 has a nonnumeric cache: {text!r}") from exc
        if not value.is_finite() or value != CONTROL_EXPECTED:
            raise ValueError(f"Preflight!C1 expected cache {CONTROL_EXPECTED}, found {text!r}")


def preflight(timeout: int = 60, session: CalculationSession | None = None) -> tuple[int, str]:
    """Run one independent control through recalculate(), never a candidate workbook.

    Returns CLI status 0 only after reopening the new output and checking its live
    formula and nonzero numeric cache, 2 for no binary, or 1 for a failed control.
    """
    session = session or CalculationSession()
    soffice = find_soffice()
    if not soffice:
        session.invalidate()
        return 2, ("Preflight unavailable: LibreOffice binary not found. Calc is required. "
                   "No installation or conversion was attempted.")
    fingerprint = session.fingerprint(soffice)
    if fingerprint is None:
        session.invalidate()
    if session.load(fingerprint):
        return 0, ("Preflight REUSED: same-task, unchanged-environment successful control receipt. "
                   "No new control or candidate was executed; candidate calculation remains required when impacted.")
    try:
        with tempfile.TemporaryDirectory(prefix="xlsx_preflight_") as tmpdir:
            source = Path(tmpdir) / "control.xlsx"
            output = Path(tmpdir) / "recalculated.xlsx"
            _write_preflight_workbook(source)
            before = source.read_bytes()
            success, message = recalculate(str(source), str(output), timeout=timeout, session=session)
            if not success:
                session.invalidate()
                return 1, f"Preflight FAILED: independent formula control failed.\n{message}"
            if source.read_bytes() != before:
                raise ValueError("The synthetic source workbook was modified")
            _verify_preflight_output(output)
            if fingerprint is not None:
                if session.fingerprint(soffice) != fingerprint:
                    raise ValueError("Calculation environment changed during the control; receipt not reusable")
                session.record(fingerprint, session.version(soffice))
    except (OSError, ValueError, KeyError, ET.ParseError, zipfile.BadZipFile, RuntimeError) as exc:
        session.invalidate()
        return 1, f"Preflight FAILED: independent formula control could not be verified: {exc}"
    return 0, (f"Preflight PASSED: reopened synthetic output; Preflight!C1 retains "
               f"{CONTROL_FORMULA} with numeric cached value {CONTROL_EXPECTED} "
               "(input cache was empty). Only this independent control passed; "
               "no candidate workbook was validated.")


# ── CLI ─────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="LibreOffice headless formula recalculation for xlsx files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic recalculation
  python3 libreoffice_recalc.py report.xlsx report_recalc.xlsx

  # With extended timeout for large files
  python3 libreoffice_recalc.py big_model.xlsx big_model_recalc.xlsx --timeout 120

  # Binary/version availability only; does not test formula calculation
  python3 libreoffice_recalc.py --check

  # Independent synthetic formula control, with no candidate input
  python3 libreoffice_recalc.py --preflight --timeout 60

  # Candidate recalculation followed by a formula-error scan
  python3 libreoffice_recalc.py input.xlsx /tmp/recalc.xlsx && \\
    python3 formula_check.py /tmp/recalc.xlsx
""",
    )
    parser.add_argument("input", nargs="?", help="Input xlsx file path")
    parser.add_argument("output", nargs="?", help="Output xlsx file path (recalculated)")
    parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        metavar="SECONDS",
        help="Maximum time to wait for LibreOffice (default: 60)",
    )
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument(
        "--check",
        action="store_true",
        help="Binary/version availability only; does not test Calc or any workbook",
    )
    modes.add_argument(
        "--preflight",
        action="store_true",
        help="Run an independent synthetic formula control and verify the new output cache/formula",
    )

    parser.add_argument("--receipt", help="Explicit same-task preflight receipt JSON; never caches candidates")
    parser.add_argument("--task-id", help="Task identifier required with --receipt; reuse only in this task")
    args = parser.parse_args()
    if args.receipt and not args.task_id:
        parser.error("--receipt requires --task-id")
    if args.receipt and any(Path(args.receipt).resolve() == Path(p).resolve()
                            for p in (args.input, args.output) if p):
        parser.error("Receipt must be distinct from candidate input/output")
    session = CalculationSession(args.receipt, args.task_id)

    # ── --check mode ─────────────────────────────────────────────────────────
    if args.check:
        soffice = find_soffice()
        if soffice:
            version = get_libreoffice_version(soffice)
            print(f"LibreOffice available: {soffice}")
            print(f"Version: {version}")
            print("Availability-only: no formula or workbook was tested. Use --preflight for a control.")
            diagnostic = calc_component_diagnostic(soffice)
            if diagnostic:
                print(f"WARNING: {diagnostic}")
            sys.exit(0)
        else:
            print("LibreOffice NOT available.")
            print("Availability-only: Tier 2 requires LibreOffice with Calc. No installation was attempted.")
            sys.exit(2)

    # ── --preflight mode ─────────────────────────────────────────────────────
    if args.preflight:
        if args.input or args.output:
            print("ERROR: --preflight accepts no candidate paths; it creates its own synthetic control.")
            sys.exit(1)
        code, message = preflight(timeout=args.timeout, session=session)
        print(message)
        sys.exit(code)

    # ── Recalculation mode ────────────────────────────────────────────────────
    if not args.input or not args.output:
        parser.print_help()
        sys.exit(1)

    if not os.path.isfile(args.input):
        print(f"ERROR: Input file not found: {args.input}")
        sys.exit(1)

    print(f"Input  : {args.input}")
    print(f"Output : {args.output}")
    print(f"Timeout: {args.timeout}s")
    print()

    success, message = recalculate(args.input, args.output, timeout=args.timeout, session=session)

    if success:
        print(f"OK: {message}")
        print()
        print("Next step: run formula_check.py on the recalculated file to detect runtime errors:")
        print(f"  python3 formula_check.py {args.output}")
        sys.exit(0)
    else:
        # Distinguish "not installed" (exit 2) from "failed" (exit 1)
        if "not found" in message.lower() or "not available" in message.lower():
            print(f"SKIP (Tier 2 unavailable): {message}")
            sys.exit(2)
        else:
            print(f"ERROR: {message}")
            sys.exit(1)


if __name__ == "__main__":
    main()
