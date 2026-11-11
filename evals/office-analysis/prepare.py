#!/usr/bin/env python3
"""Freeze a content-only case and one Office revision without reviewer material."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile


def prepare(repo: Path, ref: str, case: str, output: Path) -> None:
    cases = Path(__file__).resolve().parent / "cases"
    case_dir = cases / case
    if case not in {p.name for p in cases.iterdir() if p.is_dir()}:
        raise ValueError(f"Unknown case: {case}")
    if not (case_dir / "prompt.md").is_file():
        raise ValueError("Case has no prompt.md")
    if output.exists():
        raise ValueError("Output already exists; preserve it and select a fresh path")
    commit = subprocess.check_output(
        ["git", "rev-parse", "--verify", f"{ref}^{{commit}}"],
        cwd=repo, text=True,
    ).strip()
    tracked = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", commit, "--", "office"],
        cwd=repo, text=True,
    ).splitlines()
    guides = [p for p in tracked if p.endswith(".md")]
    if "office/SKILL.md" not in guides:
        raise ValueError("Revision has no Office entry point")

    # Only guidance is needed for this content-only check. Avoid copying scripts,
    # executables, case expectations or an entire repository into the author run.
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=output.parent) as temporary:
        staging = Path(temporary) / "run"
        shutil.copytree(case_dir, staging / "input")
        for name in guides:
            destination = staging / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(subprocess.check_output(
                ["git", "show", f"{commit}:{name}"], cwd=repo,
            ))
        (staging / "request.md").write_text(
            "Use office/SKILL.md and the applicable guidance to complete "
            "input/prompt.md using input/sources/. This is the content-only "
            "stage of an Office authoring task. Save the requested reader-facing "
            "content to answer.md; do not render a native file or install software. "
            "Use the authorized sources and available calculation tools. "
            "Keep any internal workings separate from answer.md.\n",
            encoding="utf-8",
        )
        hashes = {
            p.relative_to(staging).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(staging.rglob("*")) if p.is_file()
        }
        (staging / "manifest.json").write_text(json.dumps({
            "case": case, "skill_commit": commit, "sha256": hashes,
            "mode": "content-only; no native production or rendering",
        }, indent=2) + "\n", encoding="utf-8")
        staging.rename(output)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--case", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    repo = Path(subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True,
    ).strip())
    try:
        prepare(repo, args.ref, args.case, args.out.resolve())
    except ValueError as error:
        parser.error(str(error))
    print(args.out.resolve())


if __name__ == "__main__":
    main()
