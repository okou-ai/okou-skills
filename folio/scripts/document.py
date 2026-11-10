"""Okou adaptation: local-only loading of trusted, script-free Folio documents.

Not a sandbox for hostile HTML. Review inputs; run rendering in an isolated process
without secrets. File references must stay within the authored project directory.
"""
from contextlib import contextmanager
import base64
from html.parser import HTMLParser
import os
from pathlib import Path
import re
import shutil
from urllib.parse import unquote, urlparse
import xml.etree.ElementTree as ET

MAX_ASSET_BYTES = 32 * 1024 * 1024
MAX_PAGES = 100
URLS = re.compile(r"url\(\s*(?:\"([^\"]*)\"|'([^']*)'|([^\s)]*))\s*\)", re.I)
BLOCKED = {"script", "iframe", "object", "embed", "base", "form", "foreignobject"}


def within(path, root):
    return Path(path).resolve().is_relative_to(Path(root).resolve())


def project_file(value, base, root):
    """Resolve a local resource, rejecting absolute URLs, traversal and symlinks out."""
    parsed = urlparse(value)
    if parsed.scheme or parsed.netloc or value.startswith(("/", "\\")) or "\\" in value:
        raise ValueError(f"Only project-local asset paths are allowed: {value[:100]}")
    result = (base / unquote(parsed.path)).resolve()
    if not within(result, root) or not result.is_file():
        raise ValueError(f"Missing or out-of-project asset: {value[:100]}")
    if result.stat().st_size > MAX_ASSET_BYTES:
        raise ValueError(f"Asset exceeds 32 MiB: {result.name}")
    return result


def output_path(value, root):
    path = Path(value).resolve()
    if not within(path, root) or path == Path(root).resolve():
        raise ValueError("Output must be inside the document project, not its root")
    if within(path, Path(__file__).resolve().parent.parent):
        raise ValueError("Output must not modify the installed Folio skill")
    return path


def validate_document(html):
    html = Path(html).resolve()
    if html.suffix.lower() not in {".html", ".htm"} or not html.is_file():
        raise ValueError("Expected an existing authored .html file")
    root, seen = html.parent, set()

    def resource(value, base):
        if not value or value.startswith("#"):
            return
        if value.startswith("data:"):
            header, separator, payload = value.partition(",")
            if not separator or len(value) > MAX_ASSET_BYTES * 2:
                raise ValueError("Invalid or oversized inline asset")
            mime = header[5:].split(";")[0].lower()
            if mime not in {"image/svg+xml", "image/png", "image/jpeg", "image/webp", "font/woff", "font/woff2", "font/ttf", "application/font-woff"}:
                raise ValueError(f"Unsupported inline asset: {mime}")
            if mime == "image/svg+xml":
                raw = base64.b64decode(payload, validate=True) if ";base64" in header else unquote(payload).encode()
                svg(raw.decode("utf-8"), base)
            return
        path = project_file(value, base, root)
        if path in seen:
            return
        seen.add(path)
        if path.suffix.lower() == ".css":
            css(path.read_text(encoding="utf-8"), path.parent)
        elif path.suffix.lower() == ".svg":
            svg(path.read_text(encoding="utf-8"), path.parent)

    def css(text, base):
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
        # CSS escapes may occur inside keywords/URLs, not just displayed strings.
        def unescape(match):
            if match[1]:
                codepoint = int(match[1], 16)
                return chr(codepoint) if 0 < codepoint <= 0x10ffff and not 0xd800 <= codepoint <= 0xdfff else "\ufffd"
            return match[2] or ""
        text = re.sub(r"\\(?:([0-9a-fA-F]{1,6})(?:\r\n|[ \t\r\n\f])?|([^\r\n\f])|(?:\r\n|[\r\n\f]))", unescape, text)
        for match in URLS.finditer(text):
            resource(next(v for v in match.groups() if v is not None), base)
        for match in re.finditer(r"@import\s+['\"]([^'\"]+)['\"]", text, re.I):
            resource(match.group(1), base)
        if re.search(r"expression\s*\(|-moz-binding", text, re.I):
            raise ValueError("Active CSS is not supported")

    def svg(text, base):
        if re.search(r"<!DOCTYPE|<!ENTITY", text, re.I):
            raise ValueError("SVG entities/DOCTYPE are not supported")
        for node in ET.fromstring(text).iter():
            tag = node.tag.rsplit("}", 1)[-1].lower()
            if tag in BLOCKED:
                raise ValueError(f"Active SVG element is not supported: {tag}")
            for key, val in node.attrib.items():
                attr = key.rsplit("}", 1)[-1].lower()
                if attr.startswith("on"):
                    raise ValueError("SVG event handlers are not supported")
                if attr in {"href", "src"}:
                    resource(val, base)
                if attr == "style" or "url(" in val.lower() or "\\" in val:
                    css(val, base)
            if tag == "style" and node.text:
                css(node.text, base)

    class CheckHTML(HTMLParser):
        in_style = False

        def handle_starttag(self, tag, attrs):
            if tag in BLOCKED:
                raise ValueError(f"Active HTML element is not supported: {tag}")
            a = dict(attrs)
            if tag == "meta" and a.get("http-equiv", "").lower() == "refresh":
                raise ValueError("HTML refresh is not supported")
            if tag == "link" and a.get("rel", "").lower() != "stylesheet":
                raise ValueError("Only stylesheet link elements are supported")
            for key, val in attrs:
                if key.startswith("on") or key in {"srcset", "srcdoc", "ping"}:
                    raise ValueError(f"Active/unsupported HTML attribute: {key}")
                if key in {"src", "href", "xlink:href", "poster"} and val:
                    if tag == "a" and key == "href" and (val.startswith("#") or urlparse(val).scheme in {"http", "https", "mailto", "tel"}):
                        continue
                    resource(val, root)
                if val and (key == "style" or "url(" in val.lower() or "\\" in val):
                    css(val, root)
            if tag == "style":
                self.in_style = True

        handle_startendtag = handle_starttag

        def handle_endtag(self, tag):
            if tag == "style":
                self.in_style = False

        def handle_data(self, data):
            if self.in_style:
                css(data, root)

    if html.stat().st_size > MAX_ASSET_BYTES:
        raise ValueError("HTML exceeds 32 MiB")
    CheckHTML().feed(html.read_text(encoding="utf-8"))
    return html


def add_style(page, css):
    """Inject synchronously: add_style_tag waits on events disabled in no-JS contexts."""
    page.evaluate("""css => { const style = document.createElement('style');
        style.textContent = css; document.head.appendChild(style); }""", css)


@contextmanager
def open_document(html, viewport=None):
    """Fresh browser context; no website JS, credentials, remote assets or downloads."""
    from playwright.sync_api import sync_playwright
    html = validate_document(html)
    with sync_playwright() as pw:
        executable = os.environ.get("FOLIO_CHROMIUM") or shutil.which("chromium")
        browser = pw.chromium.launch(**({"executable_path": executable} if executable else {}))
        context = browser.new_context(java_script_enabled=False, accept_downloads=False,
                                      viewport=viewport or {"width": 1600, "height": 1800})
        blocked = []

        def route_request(route):
            url = route.request.url
            parsed = urlparse(url)
            if parsed.scheme == "file" and not parsed.netloc and within(unquote(parsed.path), html.parent):
                route.continue_()
            elif parsed.scheme == "data":
                route.continue_()
            else:
                blocked.append(parsed.scheme or "unknown")
                route.abort()

        context.route("**/*", route_request)
        try:
            page = context.new_page()
            page.goto(html.as_uri(), wait_until="load", timeout=60000)
            page.evaluate("document.fonts.ready.then(() => true)")
            page.wait_for_function("Array.from(document.images).every(i => i.complete)", timeout=60000)
            broken = page.evaluate("Array.from(document.images).filter(i => !i.naturalWidth).map(i => i.getAttribute('src'))")
            if broken or blocked:
                raise ValueError(f"Broken images or blocked requests: {broken}; blocked schemes: {blocked}")
            count = page.locator(".page").count()
            if not 1 <= count <= MAX_PAGES:
                raise ValueError(f"Expected 1–{MAX_PAGES} .page elements; found {count}")
            yield page
        finally:
            context.close()
            browser.close()
