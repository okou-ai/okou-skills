"""Small, standard-library-only runtime guards; never install packages."""

import importlib
from pathlib import Path


class DependencyError(RuntimeError):
    """An explicitly selected feature needs an unavailable dependency."""


def require_dependency(name: str):
    """Load a dependency only at feature use, with an explicit setup hint."""
    package = name.split(".", 1)[0]
    setup = {
        "pypdf": "--only fill",
        "reportlab": "--only body --minimal",
        "matplotlib": "--only body",
    }.get(package, "")
    try:
        return importlib.import_module(name)
    except ImportError as exc:
        script = Path(__file__).resolve().with_name("make.sh")
        raise DependencyError(
            f"Cannot load {name}: {exc}. No packages were installed. "
            f"When installation is authorized, use an activated virtual environment "
            f"and run: bash \"{script}\" fix {setup}"
        ) from exc


def require_file(path: str, suffixes=()):
    source = Path(path)
    if not source.is_file():
        raise ValueError(f"File not found or not a regular file: {path}")
    if suffixes and source.suffix.lower() not in suffixes:
        raise ValueError(f"Unsupported file type: {source.suffix}; expected {' / '.join(suffixes)}")
    return source


def require_distinct_output(out_path: str, *inputs: str):
    output = Path(out_path)
    if output.is_dir():
        raise ValueError(f"Output is a directory: {out_path}")
    for source in inputs:
        input_path = Path(source)
        if output.resolve() == input_path.resolve() or (
            output.exists() and input_path.exists() and output.samefile(input_path)
        ):
            raise ValueError("Output must differ from input files")
