#!/usr/bin/env python3
"""Build a new, content-addressed static presentation directory before QA."""
import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
import time
from urllib.parse import quote, unquote, urlsplit, urlunsplit


ATTR = re.compile(r'''(?P<name>[^\s=<>/]+)(?P<eq>\s*=\s*)(?P<value>"[^"]*"|'[^']*'|[^\s>]+)''')
CSS_URL = re.compile(r'''/\*[\s\S]*?\*/|url\(\s*(?:"([^"\n]*)"|'([^'\n]*)'|([^\s)'" ][^)]*?))\s*\)|@import\s+(?:"([^"\n]*)"|'([^'\n]*)')''', re.I)
URL_ATTRIBUTES = {"src", "href", "poster", "data", "xlink:href", "background"}


def digest(data):
    return hashlib.sha256(data).hexdigest()


class Markup(HTMLParser):
    """Patch only URL/style attributes and style text; preserve all other bytes."""
    def __init__(self, text, rewrite_url, rewrite_css):
        super().__init__(convert_charrefs=False)
        self.text, self.rewrite_url, self.rewrite_css = text, rewrite_url, rewrite_css
        self.offsets = [0]
        for match in re.finditer("\n", text):
            self.offsets.append(match.end())
        self.patches, self.in_style = [], False

    def source_offset(self):
        line, column = self.getpos()
        return self.offsets[line - 1] + column

    def handle_starttag(self, tag, attrs):
        if tag == "base" and dict(attrs).get("href"):
            raise ValueError("Use document-relative asset paths; remove the base href before staging")
        start = self.source_offset()
        raw = self.get_starttag_text()
        def replace(match):
            name = match["name"].lower()
            raw_value = match["value"]
            value = html.unescape(raw_value[1:-1] if raw_value[0] in "\"'" else raw_value)
            if name in URL_ATTRIBUTES:
                updated = self.rewrite_url(value)
            elif name in {"style", "fill", "stroke", "filter", "mask", "clip-path", "marker-start", "marker-mid", "marker-end"}:
                updated = self.rewrite_css(value)
            elif name in {"srcset", "imagesrcset"}:
                if "data:" in value:
                    raise ValueError("Use src for inline data images, or file URLs in srcset")
                updated = ", ".join(" ".join([self.rewrite_url(parts[0]), *parts[1:]])
                                    for item in value.split(",") if (parts := item.split()))
            else:
                return match[0]
            if updated == value:
                return match[0]
            return f'{match["name"]}{match["eq"]}"{html.escape(updated, quote=True)}"'
        self.patches.append((start, start + len(raw), ATTR.sub(replace, raw)))
        self.in_style = tag == "style"

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.in_style = False

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False

    def handle_data(self, data):
        if self.in_style:
            start = self.source_offset()
            self.patches.append((start, start + len(data), self.rewrite_css(data)))

    def result(self):
        self.feed(self.text)
        self.close()
        text = self.text
        for start, end, value in reversed(self.patches):
            text = text[:start] + value + text[end:]
        return text


class Bundle:
    def __init__(self, root):
        self.root = root.resolve()
        self.done, self.visiting, self.files = {}, set(), {}

    def url(self, value, source, destination):
        parts = urlsplit(value.strip())
        if not parts.path or parts.scheme or parts.netloc:
            return value
        # Root-relative paths belong to this local site, never the machine root.
        target = ((self.root / unquote(parts.path.lstrip("/"))) if parts.path.startswith("/")
                  else source.parent / unquote(parts.path)).resolve()
        if not target.is_relative_to(self.root):
            raise ValueError(f"Asset escapes --root: {value} in {source}")
        if not target.is_file():
            raise ValueError(f"Missing asset: {value} in {source}")
        mapped = self.asset(target)
        relative = Path(os.path.relpath(mapped, destination.parent)).as_posix()
        return urlunsplit(("", "", quote(relative, safe="/"), parts.query, parts.fragment))

    def css(self, text, source, destination):
        def replace(match):
            if match[0].startswith("/*"):
                return match[0]
            group = next(i for i in range(1, 6) if match[i] is not None)
            value = match[group].strip()
            if "\\" in value:
                raise ValueError(f"Use URL-encoded asset paths instead of CSS escapes in {source}")
            updated = self.url(value, source, destination)
            if updated == value:
                return match[0]
            return f'url("{updated}")' if group <= 3 else f'@import "{updated}"'
        return CSS_URL.sub(replace, text)

    def markup(self, text, source, destination):
        return Markup(text, lambda url: self.url(url, source, destination),
                      lambda css: self.css(css, source, destination)).result()

    def asset(self, source):
        if source in self.done:
            return self.done[source]
        if source in self.visiting:
            raise ValueError(f"Cyclic asset reference: {source}")
        if source.suffix.lower() in {".html", ".htm"}:
            raise ValueError(f"Stage one presentation entry; use external links for other HTML: {source}")
        self.visiting.add(source)
        relative = source.relative_to(self.root)
        data = source.read_bytes()
        if source.suffix.lower() == ".css":
            data = self.css(data.decode("utf-8"), source, relative).encode("utf-8")
        elif source.suffix.lower() == ".svg":
            data = self.markup(data.decode("utf-8"), source, relative).encode("utf-8")
        elif source.suffix.lower() in {".js", ".mjs"}:
            # Installed presentation runtime is inlined. Module graphs/dynamic
            # resource strings need a JS bundler rather than text substitution.
            text = data.decode("utf-8")
            if re.search(r'\b(?:import|export)\s|\bimport\s*\(|\b(?:fetch|Worker)\s*\(|new\s+URL\s*\(', text):
                raise ValueError(f"Bundle JS modules/dynamic assets before staging: {source}")
        stem = re.sub(r"-[0-9a-f]{8,64}$", "", relative.stem)
        destination = relative.with_name(f"{stem}-{digest(data)[:12]}{relative.suffix}")
        if destination in self.files and self.files[destination] != data:
            raise ValueError(f"Asset name collision: {destination}")
        self.files[destination] = data
        self.done[source] = destination
        self.visiting.remove(source)
        return destination


def prepare(source, output, root=None):
    started = time.monotonic()
    source, output = Path(source).resolve(), Path(output).resolve()
    root = Path(root).resolve() if root else source.parent
    if not source.is_relative_to(root) or not source.is_file():
        raise ValueError("The HTML input must be an existing file inside --root")
    if output.exists():
        raise ValueError("Use a new --out directory; existing drafts and bundles are preserved")
    if root.is_relative_to(output):
        raise ValueError("The output must not contain the source tree")
    bundle = Bundle(root)
    raw = source.read_bytes()
    bundle.files[Path("index.html")] = bundle.markup(raw.decode("utf-8"), source, Path("index.html")).encode("utf-8")
    # Build everything in memory first. Only a complete bundle is made visible.
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{output.name}-", dir=output.parent))
    try:
        for relative, data in bundle.files.items():
            target = temporary / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        if output.exists():
            raise ValueError("Output appeared during staging; left it unchanged")
        temporary.rename(output)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    files = [{"file": item.as_posix(), "sha256": digest(data), "bytes": len(data)}
             for item, data in sorted(bundle.files.items())]
    return {"status": "WEB_PREPARED", "input": str(source), "output": str(output),
            "sourceSha256": digest(raw), "files": files,
            "durationSeconds": round(time.monotonic() - started, 3)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True)
    parser.add_argument("--out", required=True, help="New web directory; existing files are never removed")
    parser.add_argument("--root", help="Asset boundary (defaults to the HTML input directory)")
    args = parser.parse_args()
    try:
        print(json.dumps(prepare(args.input, args.out, args.root), indent=2))
    except (ValueError, OSError) as error:
        parser.exit(1, f"prepare-web: {error}\n")


if __name__ == "__main__":
    main()
