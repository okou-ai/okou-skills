"""Check that the probe's headings and body text survived the rendered PDF."""
import re

MARKERS = ["Probe document", "First body paragraph", "Second body paragraph"]
MARKERS += ["Heading " + number for number in ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine")]


def check_rendered_probe(pdf, width, height):
    try:
        import pymupdf
    except ImportError:
        raise RuntimeError("Install the render checker: python3 -m pip install --break-system-packages pymupdf")
    failures = []
    found, visible = set(), set()
    with pymupdf.open(pdf) as document:
        for page in document:
            if abs(page.rect.width - width) > 1 or abs(page.rect.height - height) > 1:
                failures.append(f"page {page.number + 1}: paper size differs from reference")
            words = page.get_text("words")
            tokens = [re.sub(r"[^a-z]", "", word[4].casefold()) for word in words]
            for marker in MARKERS:
                expected = marker.casefold().split()
                for start in range(len(tokens) - len(expected) + 1):
                    if tokens[start:start + len(expected)] != expected:
                        continue
                    found.add(marker)
                    readable = True
                    for word in words[start:start + len(expected)]:
                        area = pymupdf.Rect(word[:4]) & page.rect
                        if area.is_empty:
                            readable = False
                            break
                        pixels = page.get_pixmap(clip=area, colorspace=pymupdf.csGRAY, alpha=False).samples
                        if not pixels or max(pixels) == min(pixels):
                            readable = False
                            break
                    if readable:
                        visible.add(marker)
    for marker in MARKERS:
        if marker not in found:
            failures.append(f"missing rendered text: {marker}")
        elif marker not in visible:
            failures.append(f"no visible ink for: {marker}")
    return failures
