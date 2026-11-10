#!/usr/bin/env python3
"""Okou adaptation of Folio's kit initializer: list or create a fresh local project.

Only the curated bundled catalogue is used. No saved kits, home directory, plugin
commands, automatic font downloads, client-memory writes or installed-skill edits.
"""
import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import shutil
import sys
sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parent.parent
KITS = ROOT / "kits"
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
HEX = re.compile(r"#[0-9a-fA-F]{6}\Z")


def meta(path):
    text = (Path(path) / "KIT.md").read_text(encoding="utf-8")
    match = re.match(r"---\n(.*?)\n---", text, re.S)
    return dict(re.findall(r"^(\w[\w-]*):\s*(.*)$", match.group(1), re.M)) if match else {}


def mark(text):
    """Mark elements carrying demo copy and images requiring user-approved assets."""
    lines = [0]
    for m in re.finditer("\n", text):
        lines.append(m.end())
    changes = {}
    void = {"img", "br", "hr", "meta", "link", "input", "source", "wbr", "area", "base", "embed", "col", "param", "track"}
    skip = {"title", "style", "script", "head"}

    class Samples(HTMLParser):
        stack = []

        def handle_starttag(self, tag, attrs):
            line, col = self.getpos()
            start = lines[line - 1] + col
            raw = self.get_starttag_text()
            node = (tag, start, raw, dict(attrs))
            if tag == "img" and re.search(r"slot|placeholder|portrait", dict(attrs).get("src", ""), re.I):
                changes[start] = raw
            if tag not in void:
                self.stack.append(node)

        def handle_startendtag(self, tag, attrs):
            self.handle_starttag(tag, attrs)
            if tag not in void:
                self.handle_endtag(tag)

        def handle_endtag(self, tag):
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i][0] == tag:
                    del self.stack[i:]
                    break

        def handle_data(self, data):
            if data.strip() and self.stack and self.stack[-1][0] not in skip:
                _, start, raw, _ = self.stack[-1]
                changes[start] = raw

    Samples().feed(text)
    for start, raw in sorted(changes.items(), reverse=True):
        if re.search(r"\bdata-kit-sample(?:[\s=/>]|$)", raw):
            continue
        end = raw.rfind("/>") if raw.endswith("/>") else len(raw) - 1
        replacement = raw[:end] + " data-kit-sample" + raw[end:]
        text = text[:start] + replacement + text[start + len(raw):]
    return text


def swap(text, theme, new):
    """Retain the upstream OKLCH lightness/chroma offsets for palette variants."""
    from palette import hex2rgb, rgb2oklch, lch
    replacements = {}
    for key, old in theme.items():
        base = key.split("-")[0]
        if base not in new:
            continue
        if key == base:
            replacement = new[base]
        else:
            l0, c0, _ = rgb2oklch(hex2rgb(theme[base]))
            l1, c1, _ = rgb2oklch(hex2rgb(old))
            ln, cn, hn = rgb2oklch(hex2rgb(new[base]))
            replacement = lch(max(0, min(1, ln + l1 - l0)), max(0, cn + c1 - c0), hn)
        replacements[old.lower()] = replacement.lower()
    return re.sub(r"#[0-9a-fA-F]{6}\b", lambda m: replacements.get(m[0].lower(), m[0]), text)


def create(args):
    if not SLUG.fullmatch(args.id) or not SLUG.fullmatch(args.name or args.id):
        raise ValueError("Kit id and --name must be lowercase hyphenated slugs")
    kit = KITS / args.id
    if not kit.is_dir() or kit.is_symlink() or not (kit / "KIT.md").is_file():
        raise ValueError(f"Unknown curated kit: {args.id}; run kit.py list")
    new = {k: v for k, v in (("brand", args.brand), ("accent", args.accent)) if v}
    if any(not HEX.fullmatch(v) for v in new.values()):
        raise ValueError("Palette colours must be quoted six-digit hex values, e.g. '#50755b'")
    requested = Path(args.project).absolute()
    if requested.is_symlink():
        raise ValueError("Project destination must not be a symlink")
    dest = requested.resolve()
    if dest == ROOT or dest.is_relative_to(ROOT):
        raise ValueError("Create projects outside the installed skill")
    if dest.exists():
        raise ValueError("Project already exists; choose a fresh directory")
    for source in (kit / "assets", ROOT / "assets" / "fonts"):
        if any(p.is_symlink() for p in source.rglob("*")):
            raise ValueError("Bundled resources must not contain symlinks")
    metadata = meta(kit)
    theme = dict(part.split() for part in metadata.get("theme", "").split(";") if part.strip())
    name = args.name or args.id
    dest.mkdir(parents=True, exist_ok=False)
    try:
        shutil.copytree(kit / "assets", dest / "assets")
        shutil.copytree(ROOT / "assets" / "fonts", dest / "fonts")
        shutil.copy2(ROOT / "assets" / "folio.css", dest / "folio.css")
        text = (kit / "kit.html").read_text(encoding="utf-8").replace('href="kit.css"', f'href="{name}.css"')
        css = (kit / "kit.css").read_text(encoding="utf-8")
        text, css = mark(swap(text, theme, new)), swap(css, theme, new)
        (dest / f"{name}.html").write_text(text, encoding="utf-8")
        (dest / f"{name}.css").write_text(css, encoding="utf-8")
        for svg in (dest / "assets").glob("*.svg"):
            svg.write_text(swap(svg.read_text(encoding="utf-8"), theme, new), encoding="utf-8")
        from document import validate_document
        validate_document(dest / f"{name}.html")
        count = len(re.findall(r"\bdata-kit-sample\b", text))
        (dest / "SLOTS.md").write_text(
            f"# {args.id}: draft content, not a finished deliverable\n\n"
            f"{count} elements carry `data-kit-sample`. Replace/verify every sample, including the fictional company, "
            "statistics, people, prices, contacts, captions, and image/mark slots; only then remove that element's flag. "
            "Do not globally delete flags to pass preflight. Replace the HTML title and metadata too.\n\n"
            "Use licensed assets and preserve their notices in ASSET-LICENSES.md. Bundled Latin fonts and their OFL notices "
            "are under fonts/. For Chinese, add a licensed CJK font and verify glyphs/line breaks. Nothing was downloaded.\n",
            encoding="utf-8")
        print(f"Created {dest / (name + '.html')} ({metadata.get('pages')} pages; {count} sample elements to replace)")
    except Exception:
        shutil.rmtree(dest)
        raise
    return dest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    new = sub.add_parser("new")
    new.add_argument("id")
    new.add_argument("project")
    new.add_argument("--name")
    new.add_argument("--brand")
    new.add_argument("--accent")
    args = parser.parse_args()
    try:
        if args.command == "list":
            print((KITS / "INDEX.md").read_text(encoding="utf-8"))
        else:
            create(args)
    except (ValueError, FileNotFoundError, FileExistsError) as exc:
        parser.exit(1, f"folio kit: {exc}\n")


if __name__ == "__main__":
    main()
