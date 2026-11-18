#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Standard-library package safety and source-preserving part replacement."""

import copy
import os
from pathlib import Path
import stat
import tempfile
import xml.etree.ElementTree as ET
import zipfile


class _OriginalNameInfo(zipfile.ZipInfo):
    """Keep raw-record filename encoding/flags when rebuilding its directory."""

    def __init__(self, source: zipfile.ZipInfo):
        for field in zipfile.ZipInfo.__slots__:
            if hasattr(source, field):
                setattr(self, field, getattr(source, field))

    def _encodeFilenameFlags(self):
        # ZipFile reads with UTF-8 or CP437 here (no metadata_encoding override).
        # Its default writer otherwise normalizes non-ASCII CP437 names to UTF-8,
        # disagreeing with the untouched local record and changing member flags.
        encoding = "utf-8" if self.flag_bits & 0x800 else "cp437"
        # Unicode Path extras can change filename; orig_filename retains the
        # header-decoded name of the unchanged local record.
        return self.orig_filename.encode(encoding), self.flag_bits


def safe_member(name: str) -> str:
    """Require a canonical relative ZIP path (also safe on Windows)."""
    if (not name or name.startswith("/") or name.endswith("//") or "\\" in name or "\x00" in name
            or ":" in name or any(p in ("", ".", "..") for p in name.rstrip("/").split("/"))):
        raise ValueError(f"Unsafe package member: {name!r}")
    return name


def checked_members(package: zipfile.ZipFile) -> list[zipfile.ZipInfo]:
    infos = package.infolist()
    seen = set()
    for info in infos:
        safe_member(info.orig_filename)
        safe_member(info.filename)
        # Case collisions cannot be safely unpacked on all supported filesystems.
        key = info.filename.rstrip("/").casefold()
        if key in seen:
            raise ValueError(f"Duplicate/colliding package member: {info.filename!r}")
        seen.add(key)
        if stat.S_ISLNK(info.external_attr >> 16) or info.flag_bits & 1:
            raise ValueError(f"Symlink/encrypted member is unsupported: {info.filename!r}")
    return infos


def validate_xml(data: bytes, name: str) -> None:
    if not name.endswith((".xml", ".rels")):
        raise ValueError(f"Scoped replacements must be XML/rels parts: {name}")
    try:
        ET.fromstring(data)
    except ET.ParseError as exc:
        raise ValueError(f"Invalid replacement XML {name}: {exc}") from exc


def publish_new(temporary: Path, output: Path) -> None:
    """Atomically publish without replacing an existing file, including a symlink."""
    os.link(temporary, output)  # exclusive even if another process creates output


def replace_parts(base: str, replacements: dict[str, str], output: str) -> None:
    """Replace existing XML parts; copy all other local ZIP records verbatim.

    Unlike ZipFile.writestr for every member, raw record copying preserves even
    compression streams, local extra fields, flags and data descriptors. Central
    offsets necessarily change; archive comments and ZipInfo metadata are kept.
    zipfile's central-directory writer is used; no application load/save occurs.
    This is not OOXML dependency/schema validation or a signature repair tool.
    """
    source, target = Path(base).resolve(), Path(output).absolute()
    if target.resolve() == source or os.path.lexists(target):
        raise ValueError("Output must be a new file, never the source or an existing path")
    if not replacements:
        raise ValueError("Supply at least one --part MEMBER=FILE")
    payloads = {}
    for name, filename in replacements.items():
        safe_member(name)
        replacement = Path(filename)
        if replacement.is_symlink() or not replacement.is_file():
            raise ValueError(f"Replacement must be a regular file: {filename}")
        if replacement.resolve() == target.resolve() or replacement.resolve() == source:
            raise ValueError("Replacement/source/output paths must be distinct")
        data = replacement.read_bytes()
        validate_xml(data, name)
        payloads[name] = data

    # Validate before creating any output, including all member names and targets.
    with zipfile.ZipFile(source) as original:
        infos = checked_members(original)
        names = {i.filename for i in infos if not i.is_dir()}
        if not payloads.keys() <= names:
            raise ValueError(f"Replacement parts not present in base: {sorted(payloads.keys() - names)}")
        physical = sorted(infos, key=lambda i: i.header_offset)
        if len({i.header_offset for i in physical}) != len(physical):
            raise ValueError("Overlapping source ZIP member offsets")
        ends = {info.header_offset: (physical[n + 1].header_offset if n + 1 < len(physical)
                                    else original.start_dir)
                for n, info in enumerate(physical)}
        for info in physical:
            if info.header_offset < 0 or ends[info.header_offset] <= info.header_offset:
                raise ValueError("Invalid/overlapping source ZIP member offsets")
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".xlsx-parts-", dir=target.parent)
        os.close(fd)
        temporary = Path(tmp)
        try:
            with source.open("rb") as raw, zipfile.ZipFile(temporary, "w") as result:
                result.comment = original.comment
                for info in infos:
                    if info.filename in payloads:
                        result.writestr(copy.copy(info), payloads[info.filename])
                    else:
                        copied = _OriginalNameInfo(info)
                        # ZipFile has no public API for copying an unchanged local
                        # record. Keep the small private-writer boundary here only.
                        result.fp.seek(result.start_dir)
                        copied.header_offset = result.fp.tell()
                        raw.seek(info.header_offset)
                        remaining = ends[info.header_offset] - info.header_offset
                        while remaining:
                            block = raw.read(min(1024 * 1024, remaining))
                            if not block:
                                raise ValueError("Truncated source ZIP member")
                            result.fp.write(block)
                            remaining -= len(block)
                        result.start_dir = result.fp.tell()
                        result.filelist.append(copied)
                        result.NameToInfo[copied.filename] = copied
                        result._didModify = True
            with zipfile.ZipFile(temporary) as check:
                checked_members(check)
                for name, data in payloads.items():
                    if check.read(name) != data:
                        raise ValueError(f"Replacement verification failed: {name}")
            publish_new(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)


def source_files(directory: Path) -> list[tuple[Path, str]]:
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError(f"Source must be a regular directory: {directory}")
    files = []
    for root, dirs, names in os.walk(directory, followlinks=False):
        for name in dirs + names:
            path = Path(root) / name
            if path.is_symlink():
                raise ValueError(f"Source symlink is not allowed: {path}")
        for name in sorted(names):
            path = Path(root) / name
            if not path.is_file():
                raise ValueError(f"Source is not a regular file: {path}")
            member = safe_member(path.relative_to(directory).as_posix())
            files.append((path, member))
    if len({n.casefold() for _, n in files}) != len(files):
        raise ValueError("Source contains colliding member paths")
    return files


def pack_directory(source: str, output: str) -> int:
    directory, target = Path(source).absolute(), Path(output).absolute()
    if os.path.lexists(target) or target.resolve().is_relative_to(directory.resolve()):
        raise ValueError("Output must be new and outside the source directory")
    files = source_files(directory)
    if "[Content_Types].xml" not in {name for _, name in files}:
        raise ValueError("Missing [Content_Types].xml in source directory")
    for path, name in files:
        if name.endswith((".xml", ".rels")):
            validate_xml(path.read_bytes(), name)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".xlsx-pack-", dir=target.parent)
    os.close(fd)
    temporary = Path(tmp)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as package:
            for path, name in files:
                package.write(path, name)
        publish_new(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
    return len(files)
