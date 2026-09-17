#!/usr/bin/env python3
"""Make pandoc available: use the installed one, or fetch the official portable build.

Usage:
  python3 ensure_pandoc.py                    # check, download to ./vendor if missing
  python3 ensure_pandoc.py --dir /opt/tools   # choose install location
  python3 ensure_pandoc.py --version 3.11     # pin a version (default: latest on GitHub)
  python3 ensure_pandoc.py --check            # check only, never download

The platform and CPU architecture are detected, not hardcoded: macOS ships a .zip
rather than a .tar.gz, and Apple Silicon and Intel Macs use different asset names.
"""
import sys, os, json, shutil, platform, subprocess, tarfile, zipfile, tempfile
import urllib.request, urllib.error

API = "https://api.github.com/repos/jgm/pandoc/releases/latest"
DL = "https://github.com/jgm/pandoc/releases/download/{v}/{asset}"
FALLBACK_VERSION = "3.11"   # used when the latest release cannot be queried


def asset_name(version):
    """Pick the official release asset for this OS and CPU architecture."""
    osname = platform.system()
    arch = platform.machine().lower()
    x86 = arch in ("x86_64", "amd64")
    arm = arch in ("arm64", "aarch64")
    if osname == "Linux":
        if x86:
            return f"pandoc-{version}-linux-amd64.tar.gz"
        if arm:
            return f"pandoc-{version}-linux-arm64.tar.gz"
    elif osname == "Darwin":
        if arm:
            return f"pandoc-{version}-arm64-macOS.zip"
        if x86:
            return f"pandoc-{version}-x86_64-macOS.zip"
    elif osname == "Windows":
        if x86 or arm:      # Windows on ARM runs the x86_64 build
            return f"pandoc-{version}-windows-x86_64.zip"
    raise SystemExit(f"No official portable build for {osname}/{arch}. "
                     f"Install via a package manager, or pick an asset manually at "
                     f"https://github.com/jgm/pandoc/releases")


def latest_version():
    try:
        with urllib.request.urlopen(API, timeout=15) as r:
            return json.load(r)["tag_name"].lstrip("v")
    except Exception as e:
        print(f"  (could not query the latest release: {e}; using {FALLBACK_VERSION})")
        return FALLBACK_VERSION


def find_binary(root):
    exe = "pandoc.exe" if platform.system() == "Windows" else "pandoc"
    for dirpath, _, files in os.walk(root):
        if exe in files:
            p = os.path.join(dirpath, exe)
            if platform.system() != "Windows":
                os.chmod(p, 0o755)
            return p
    return None


def install(dest, version):
    os.makedirs(dest, exist_ok=True)
    name = asset_name(version)
    url = DL.format(v=version, asset=name)
    print(f"  platform {platform.system()}/{platform.machine()} -> {name}")
    print(f"  downloading {url}")
    tmp = tempfile.mkdtemp()
    pkg = os.path.join(tmp, name)
    try:
        urllib.request.urlretrieve(url, pkg)
    except urllib.error.HTTPError as e:
        raise SystemExit(f"Download failed with HTTP {e.code}. Check that version "
                         f"{version} exists, or install via a package manager.")
    except Exception as e:
        raise SystemExit(f"Download failed: {e}\n"
                         f"If github.com is unreachable, fetch {name} on another "
                         f"machine and unpack it here — pandoc is a static binary "
                         f"with no runtime dependencies.")
    if name.endswith(".tar.gz"):
        with tarfile.open(pkg) as t:
            t.extractall(dest)
    else:
        with zipfile.ZipFile(pkg) as z:
            z.extractall(dest)
    shutil.rmtree(tmp, ignore_errors=True)
    b = find_binary(dest)
    if not b:
        raise SystemExit(f"Unpacked, but no pandoc executable was found under {dest}.")
    return b


def main():
    a = sys.argv
    dest = a[a.index("--dir") + 1] if "--dir" in a else os.path.abspath("vendor")
    version = a[a.index("--version") + 1] if "--version" in a else None

    found = shutil.which("pandoc")
    if found:
        v = subprocess.run([found, "--version"], capture_output=True, text=True)
        line = v.stdout.splitlines()[0]
        print(f"OK  installed: {found}")
        print(f"    {line}")
        # Before 2.0 the flag was --reference-docx, and the style set differs.
        num = line.split()[-1].split("-")[0]
        try:
            major = int(num.split(".")[0])
        except ValueError:
            return 0
        if major < 3:
            print(f"    WARNING: this skill targets pandoc 3.x; {num} is older.")
            print(f"    Upgrade before investigating any unexpected behaviour.")
        return 0

    if "--check" in a:
        print("MISSING  pandoc not found. Install it, or drop --check to download "
              "the portable build.")
        return 1

    print("pandoc not found, fetching the official portable build:")
    version = version or latest_version()
    b = install(dest, version)
    v = subprocess.run([b, "--version"], capture_output=True, text=True)
    print(f"\nOK  installed: {b}")
    print(f"    {v.stdout.splitlines()[0]}")
    sep = ";" if platform.system() == "Windows" else ":"
    print(f"\nAdd it to PATH for the current shell:")
    if platform.system() == "Windows":
        print(f'   set PATH={os.path.dirname(b)}{sep}%PATH%')
    else:
        print(f'   export PATH="{os.path.dirname(b)}{sep}$PATH"')
    return 0


if __name__ == "__main__":
    sys.exit(main())
