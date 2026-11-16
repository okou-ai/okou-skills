#!/usr/bin/env python3
"""Download the current office/ package from main, not the repository archive."""

import argparse
import gzip
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

REPOSITORY = "https://github.com/okou-ai/okou-skills.git"


def _git(directory, *args):
    return subprocess.run(
        ["git", "-C", str(directory), *args],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
        timeout=180,
    ).stdout.strip()


def download_office(output, *, repository=REPOSITORY):
    """Package current main's office files and return the resolved source SHA."""
    if not shutil.which("git"):
        raise RuntimeError("Git with partial-fetch and sparse-checkout support is required")
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    pending = None
    try:
        with tempfile.TemporaryDirectory(prefix="office-download-") as temporary:
            checkout = Path(temporary) / "repository"
            checkout.mkdir()
            _git(checkout, "init", "--quiet")
            _git(checkout, "remote", "add", "origin", repository)
            # Non-cone patterns omit root files and all other skill directories.
            _git(checkout, "sparse-checkout", "set", "--no-cone", "/office/")
            _git(checkout, "fetch", "--quiet", "--filter=blob:none", "--depth=1",
                 "--no-tags", "origin", "refs/heads/main")
            # Resolve main once so an update during packaging cannot mix versions.
            revision = _git(checkout, "rev-parse", "--verify", "FETCH_HEAD^{commit}")
            _git(checkout, "checkout", "--quiet", "--detach", revision)
            if not (checkout / "office/SKILL.md").is_file():
                raise RuntimeError("Current main has no office/SKILL.md")
            tar_path = Path(temporary) / "office.tar"
            # A commit plus pathspec prefetches unrelated blobs; use the subtree.
            _git(checkout, "archive", "--format=tar", f"--output={tar_path}",
                 "--prefix=office/", f"{revision}:office")
            timestamp = int(_git(checkout, "show", "--no-patch", "--format=%ct", revision))
            with tempfile.NamedTemporaryFile(dir=output.parent, prefix=f".{output.name}.",
                                             suffix=".tmp", delete=False) as destination:
                pending = Path(destination.name)
                with tarfile.open(tar_path) as source, gzip.GzipFile(
                    filename="", mode="wb", fileobj=destination, mtime=0
                ) as compressed, tarfile.open(
                    fileobj=compressed, mode="w|", format=tarfile.PAX_FORMAT,
                    pax_headers={"comment": revision}
                ) as package:
                    for member in source:
                        member.mtime = timestamp
                        member.pax_headers.pop("mtime", None)
                        package.addfile(member, source.extractfile(member) if member.isfile() else None)
            os.replace(pending, output)
            pending = None
    finally:
        if pending is not None:
            pending.unlink(missing_ok=True)
    return {"archive": str(output), "revision": revision, "root": "office/",
            "bytes": output.stat().st_size}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path, help="Output .tar.gz package")
    args = parser.parse_args()
    try:
        result = download_office(args.out)
    except subprocess.CalledProcessError as error:
        print(f"Office download failed: {error.stderr.strip()}", file=sys.stderr)
        return 1
    except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
        print(f"Office download failed: {error}", file=sys.stderr)
        return 1
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
