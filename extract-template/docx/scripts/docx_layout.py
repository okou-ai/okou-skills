"""Read the main text flow and inherited styles without rewriting source XML."""
from collections import Counter
from copy import deepcopy
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
NS = {"w": W[1:-1]}
ET.register_namespace("w", W[1:-1])
ET.register_namespace("r", "http://schemas.openxmlformats.org/officeDocument/2006/relationships")


class Styles:
    def __init__(self, xml):
        root = ET.fromstring(xml)
        self.by_id = {s.get(W + "styleId"): s for s in root.findall(W + "style")}
        self.by_name = {}
        self.default = "Normal"
        for sid, style in self.by_id.items():
            name = style.find(W + "name")
            if name is not None:
                self.by_name[name.get(W + "val", "").lower()] = sid
            if style.get(W + "type") == "paragraph" and style.get(W + "default") in ("1", "true"):
                self.default = sid

    def resolve(self, name):
        sid = self.by_name.get(name.lower(), name)
        if sid not in self.by_id:
            raise ValueError(f"Unknown source style: {name!r}")
        return sid

    def property(self, sid, group, name):
        seen = set()
        while sid in self.by_id:
            if sid in seen:
                raise ValueError(f"Cyclic style inheritance at {sid!r}")
            seen.add(sid)
            style = self.by_id[sid]
            value = style.find(f"w:{group}/w:{name}", NS)
            if value is not None:
                return value
            parent = style.find(W + "basedOn")
            sid = parent.get(W + "val") if parent is not None else None
        return None

    def paragraph_style(self, paragraph):
        style = paragraph.find("w:pPr/w:pStyle", NS)
        return style.get(W + "val") if style is not None else self.default

    def name(self, sid):
        style = self.by_id.get(sid)
        name = style.find(W + "name") if style is not None else None
        return name.get(W + "val", sid) if name is not None else sid


def sections(document):
    """Each section ends at its paragraph's sectPr or the body's final sectPr."""
    root = ET.fromstring(document) if isinstance(document, (str, bytes)) else document
    result, paragraphs = [], []

    def walk(node):
        nonlocal paragraphs
        if node.tag in (W + "tbl", W + "txbxContent", W + "sectPrChange"):
            return
        if node.tag == W + "p":
            paragraphs.append(node)
            section = node.find("w:pPr/w:sectPr", NS)
            if section is not None:
                result.append((section, paragraphs))
                paragraphs = []
            return
        if node.tag == W + "sectPr":
            result.append((node, paragraphs))
            paragraphs = []
            return
        for child in node:
            walk(child)

    walk(root.find(W + "body"))
    if paragraphs or not result:
        result.append((ET.Element(W + "sectPr"), paragraphs))
    return result


def text_of(paragraph):
    def text(node):
        if node.tag in (W + "txbxContent", W + "tbl"):
            return ""
        if node.tag == W + "t":
            return node.text or ""
        return "".join(text(child) for child in node)
    return text(paragraph)


def body_candidates(document, styles, mapping=None, section=None):
    counts = Counter()
    excluded = {styles.resolve(name) for name, target in (mapping or {}).items()
                if name != "__body__" and target.lower().replace(" ", "").startswith(("title", "subtitle", "heading"))}
    for number, (_, paragraphs) in enumerate(sections(document), 1):
        if section is not None and number != section:
            continue
        for p in paragraphs:
            sid = styles.paragraph_style(p)
            name = styles.name(sid).lower()
            if sid in excluded or name in ("title", "subtitle", "caption", "toc heading") or name.startswith(("heading ", "list ")):
                continue
            if p.find("w:pPr/w:numPr", NS) is not None or styles.property(sid, "pPr", "numPr") is not None:
                continue
            if p.find("w:pPr/w:framePr", NS) is not None or styles.property(sid, "pPr", "framePr") is not None:
                continue
            outline = p.find("w:pPr/w:outlineLvl", NS)
            if outline is None:
                outline = styles.property(sid, "pPr", "outlineLvl")
            if outline is not None and int(outline.get(W + "val", "9")) < 9:
                continue
            counts[sid] += len("".join(text_of(p).split()))
    return Counter({sid: count for sid, count in counts.items() if count})


def choose_body(document, styles, mapping=None, section=None):
    if section is not None and not 1 <= section <= len(sections(document)):
        raise ValueError(f"--section must be between 1 and {len(sections(document))}")
    explicit = (mapping or {}).get("__body__")
    if explicit:
        sid = styles.resolve(explicit)
        if styles.property(sid, "pPr", "framePr") is not None:
            raise ValueError(f"Body style {explicit!r} inherits framePr; select a flowing body style")
        return sid
    counts = body_candidates(document, styles, mapping, section)
    ranked = counts.most_common()
    if not ranked:
        raise ValueError("No flowing body style found; set --map '__body__=<source style>' after inspecting the source")
    if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        raise ValueError("Body style is ambiguous; set --map '__body__=<source style>'")
    return ranked[0][0]


def choose_section(document, styles, body_sid, requested=None):
    records = sections(document)
    if requested is not None:
        if not 1 <= requested <= len(records):
            raise ValueError(f"--section must be between 1 and {len(records)}")
        return requested
    if len(records) == 1:
        return 1
    scores = [sum(len("".join(text_of(p).split())) for p in paragraphs
                  if styles.paragraph_style(p) == body_sid
                  and p.find("w:pPr/w:framePr", NS) is None)
              for _, paragraphs in records]
    winners = [i + 1 for i, score in enumerate(scores) if score == max(scores)]
    if len(winners) != 1:
        raise ValueError("Body section is ambiguous; inspect the numbered sections and pass --section N")
    return winners[0]


def section_xml(document, number):
    records = sections(document)
    selected = deepcopy(records[number - 1][0])
    # Missing header/footer references inherit by type from preceding sections.
    references = {}
    for section, _ in records[:number]:
        for child in section:
            if child.tag in (W + "headerReference", W + "footerReference"):
                references[(child.tag, child.get(W + "type"))] = child
    for child in list(selected):
        if child.tag in (W + "headerReference", W + "footerReference"):
            selected.remove(child)
    ordered = sorted(references.values(), key=lambda element: element.tag != W + "headerReference")
    for index, child in enumerate(ordered):
        selected.insert(index, deepcopy(child))
    return ET.tostring(selected, encoding="unicode")


def flow_style_issues(styles):
    """Pandoc's prose styles cannot inherit page-anchored frames."""
    targets = ["body text", "first paragraph", "compact", "title", "subtitle"]
    targets += [f"heading {level}" for level in range(1, 10)]
    return [f"{name} inherits framePr; map its body-page role or retain the source layout"
            for name in targets if name in styles.by_name
            and styles.property(styles.by_name[name], "pPr", "framePr") is not None]
