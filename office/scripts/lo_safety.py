"""Conservative OOXML gate and isolated LibreOffice I/O (stdlib only).

Not a sandbox, antivirus, or proof against parser vulnerabilities. Only DOCX/XLSX
are accepted; active content, external resources/updates, ambiguous packages and
oversize XML are refused. Ordinary HTTP(S)/mailto/tel hyperlinks are permitted,
not followed by this helper. Use OS/network isolation for hostile documents.
"""
from contextlib import contextmanager
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
import stat
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
import zipfile


class SafetyError(ValueError):
    """Input or output cannot safely be processed under this policy."""


REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"
CT = "{http://schemas.openxmlformats.org/package/2006/content-types}"
MAX_TOTAL = 256 * 1024 * 1024
MAX_XML = 16 * 1024 * 1024
DANGEROUS = re.compile(
    r"vba|macro|activex|oleobject|externallink|externaldata|attachedtemplate|"
    r"afchunk|altchunk|webextension|querytable|connections|subdocument|richdata", re.I)
# No word boundary: adjacent/split field instructions must not conceal a token.
FIELDS = re.compile(r"DDEAUTO|DDE|INCLUDETEXT|INCLUDEPICTURE|LINK|DATABASE", re.I)
FORMULAS = re.compile(
    r"\b(?:WEBSERVICE|RTD|DDE|CALL|REGISTER(?:\.ID)?|EXEC|SQL\.REQUEST|"
    r"IMAGE|DISPIMG|CUBE[A-Z.]*|STOCKHISTORY|FIELDVALUE)\s*\(|"
    r"\[[^\]]+\][^!\r\n]*!|\|", re.I)


def _xml(data: bytes, name: str):
    if len(data) > MAX_XML:
        raise SafetyError(f"XML exceeds safety limit: {name}")
    try:
        text = data.decode("utf-8-sig")
        if "\x00" in text or re.search(r"<!\s*(?:DOCTYPE|ENTITY)\b", text, re.I):
            raise SafetyError(f"DTD/entities or non-UTF8 XML refused: {name}")
        return ET.fromstring(text)
    except (UnicodeError, ET.ParseError) as exc:
        raise SafetyError(f"Invalid/unsupported XML: {name}") from exc


def _hyperlink(target: str):
    parsed = urlsplit(target)
    if parsed.scheme.lower() not in {"https", "http", "mailto", "tel"}:
        raise SafetyError("Only ordinary HTTP(S), mailto and tel external hyperlinks are allowed")
    if parsed.scheme.lower() in {"http", "https"} and not parsed.netloc:
        raise SafetyError("Malformed external hyperlink")


def validate_ooxml(path) -> None:
    """Fail closed on unsupported/active/update-bearing DOCX/XLSX packages."""
    path = Path(path)
    kind = path.suffix.lower()
    if kind not in {".docx", ".xlsx"}:
        raise SafetyError("Only macro-free .docx and .xlsx inputs are supported")
    try:
        with zipfile.ZipFile(path) as package:
            infos = package.infolist()
            if len(infos) > 10000 or sum(i.file_size for i in infos) > MAX_TOTAL:
                raise SafetyError("OOXML package exceeds safety limits")
            names = set()
            for info in infos:
                name = info.filename
                decoded = unquote(name)
                if (not name or name.startswith("/") or "\\" in decoded
                        or any(p in {".", ".."} for p in decoded.split("/"))
                        or ":" in decoded or "\x00" in decoded
                        or info.flag_bits & 1 or stat.S_ISLNK(info.external_attr >> 16)):
                    raise SafetyError(f"Unsafe ZIP member: {name}")
                if name.casefold() in names:
                    raise SafetyError(f"Duplicate/ambiguous ZIP member: {name}")
                names.add(name.casefold())
                lower = decoded.lower()
                if (DANGEROUS.search(lower) or "/embeddings/" in lower
                        or "/ctrlprops/" in lower or "/dialogsheets/" in lower
                        or lower.endswith((".bin", ".exe", ".dll", ".js"))
                        and "/printersettings/" not in lower):
                    raise SafetyError(f"Active/update-bearing part refused: {name}")
            types = _xml(package.read("[Content_Types].xml"), "[Content_Types].xml")
            if types.tag != CT + "Types":
                raise SafetyError("Invalid OOXML content types")
            expected_part, expected_type = (
                ("/word/document.xml", "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml")
                if kind == ".docx" else
                ("/xl/workbook.xml", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"))
            if not any(e.get("PartName") == expected_part and e.get("ContentType") == expected_type
                       for e in types.findall(CT + "Override")):
                raise SafetyError("Missing macro-free OOXML main content type")
            for element in types:
                if DANGEROUS.search(element.get("ContentType", "")):
                    raise SafetyError("Active/update-bearing content type refused")
            for info in infos:
                name = info.filename
                if not name.lower().endswith((".xml", ".rels", ".vml")):
                    continue
                root = _xml(package.read(info), name)
                if name.lower().endswith(".rels"):
                    if root.tag != REL + "Relationships":
                        raise SafetyError(f"Invalid relationship root: {name}")
                    ids = set()
                    for rel in root:
                        target, mode, reltype = rel.get("Target", ""), rel.get("TargetMode", "Internal"), rel.get("Type", "")
                        rid = rel.get("Id")
                        if (rel.tag != REL + "Relationship" or not target or not reltype
                                or not rid or rid in ids or mode not in {"Internal", "External"}):
                            raise SafetyError(f"Ambiguous relationship: {name}")
                        ids.add(rid)
                        tail = reltype.rsplit("/", 1)[-1].lower()
                        if DANGEROUS.search(reltype) or tail in {"package", "control", "ctrlprop"}:
                            raise SafetyError(f"Active/update relationship refused: {tail}")
                        if mode == "External":
                            if reltype not in {
                                "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
                                "http://purl.oclc.org/ooxml/officeDocument/relationships/hyperlink",
                            }:
                                raise SafetyError(f"External resource/update refused: {tail}")
                            _hyperlink(target)
                        else:
                            decoded = unquote(target)
                            if urlsplit(decoded).scheme or decoded.startswith("//") or "\\" in decoded:
                                raise SafetyError("External target disguised as internal relationship")
                            base = "" if name == "_rels/.rels" else str(PurePosixPath(name).parent.parent)
                            part = posixpath.normpath(decoded.lstrip("/") if decoded.startswith("/")
                                                      else posixpath.join(base, decoded.split("#", 1)[0]))
                            if part.startswith("../") or (tail != "hyperlink" and part.casefold() not in names):
                                raise SafetyError(f"Missing/escaping relationship target: {name}")
                instructions = []
                for element in root.iter():
                    local = element.tag.rsplit("}", 1)[-1].lower()
                    if local in {"ddelink", "ddeitem", "oleobject", "object", "altchunk", "control",
                                 "externalreference", "externalbook", "connection", "querytable", "attachedtemplate"}:
                        raise SafetyError(f"Active XML element refused: {local}")
                    if local == "instrtext":
                        instructions.append("".join(element.itertext()))
                    for key, value in element.attrib.items():
                        attr = key.rsplit("}", 1)[-1].lower()
                        if attr == "instr":
                            instructions.append(value)
                        if attr in {"href", "src"} and value and not value.startswith("#"):
                            raise SafetyError("Inline resource URI refused")
                    if local in {"f", "definedname"} and FORMULAS.search(element.text or ""):
                        raise SafetyError("External/active spreadsheet formula refused")
                if FIELDS.search("".join(instructions)):
                    raise SafetyError("External/active Word field refused")
    except (OSError, KeyError, zipfile.BadZipFile, RuntimeError) as exc:
        raise SafetyError(f"Cannot inspect OOXML package: {exc}") from exc


def prepare_input(source, directory) -> Path:
    """Copy to a NEW private application input, then validate the exact copy."""
    source, directory = Path(source), Path(directory)
    directory.mkdir(parents=True, exist_ok=False)
    copied = directory / ("input" + source.suffix.lower())
    with source.open("rb") as src, copied.open("xb") as dst:
        if not stat.S_ISREG(os.fstat(src.fileno()).st_mode):
            raise SafetyError("Source must be a regular file")
        shutil.copyfileobj(src, dst)
    validate_ooxml(copied)
    return copied


def configure_lo_profile(profile, *, calc_recalculate=False) -> str:
    """Create a NEW isolated profile; return its file URI for UserInstallation."""
    profile = Path(profile).absolute()
    (profile / "user").mkdir(parents=True, exist_ok=False)
    oor = "{http://openoffice.org/2001/registry}"
    root = ET.Element(oor + "items")
    settings = {
        "/org.openoffice.Office.Common/Security/Scripting": {
            "DisableMacrosExecution": "true", "MacroSecurityLevel": "3",
            "DisableActiveContent": "true", "BlockUntrustedRefererLinks": "true",
            "SecureURL": None},
        # Calc ScLkUpdMode LM_NEVER=1; Writer SfxLinkUpdateMode NEVER=2.
        "/org.openoffice.Office.Calc/Content/Update": {"Link": "1"},
        "/org.openoffice.Office.Writer/Content/Update": {"Link": "2", "Field": "false", "Chart": "false"},
    }
    if calc_recalculate:
        settings["/org.openoffice.Office.Calc/Formula/Load"] = {"OOXMLRecalcMode": "0"}
    for path, props in settings.items():
        item = ET.SubElement(root, "item", {oor + "path": path})
        for key, value in props.items():
            prop = ET.SubElement(item, "prop", {oor + "name": key, oor + "op": "fuse"})
            ET.SubElement(prop, "value").text = value
    with (profile / "user/registrymodifications.xcu").open("xb") as stream:
        stream.write(ET.tostring(root, encoding="utf-8", xml_declaration=True))
    return profile.as_uri()


class _Reservation:
    def __init__(self, destination, fd):
        self.path, self.fd, self.published = destination, fd, False
        self.identity = os.fstat(fd)

    def owns_path(self):
        try:
            current = self.path.lstat()
            return (current.st_dev, current.st_ino) == (self.identity.st_dev, self.identity.st_ino)
        except FileNotFoundError:
            return False

    def publish(self, generated) -> None:
        """Copy a new regular generated file only into our exclusively owned fd."""
        generated = Path(generated)
        if generated.is_symlink() or not generated.is_file() or not self.owns_path():
            raise SafetyError("Generated output/reservation is not a new regular file")
        with generated.open("rb") as src, os.fdopen(os.dup(self.fd), "wb") as dst:
            if os.fstat(src.fileno()).st_ino == self.identity.st_ino and os.fstat(src.fileno()).st_dev == self.identity.st_dev:
                raise SafetyError("Cannot publish a reservation onto itself")
            shutil.copyfileobj(src, dst)
            dst.flush()
            os.fsync(dst.fileno())
        if not self.owns_path():
            raise SafetyError("Output reservation changed during publication")
        self.published = True


@contextmanager
def reserve_output(destination, *, source=None):
    """Reserve NEW output with O_EXCL (including symlinks); yield .publish(path).

    Failed work removes only our own placeholder, never another writer's file.
    Existing destinations, including the source and hardlinks to it, are refused.
    """
    destination = Path(destination).absolute()
    if source is not None and destination.resolve() == Path(source).resolve():
        raise SafetyError("Source and destination must be different files")
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    reservation = _Reservation(destination, fd)
    try:
        yield reservation
    finally:
        os.close(fd)
        if not reservation.published and reservation.owns_path():
            reservation.path.unlink()
