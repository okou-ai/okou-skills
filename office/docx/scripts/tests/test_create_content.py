"""Exercise the standard DOCX creation command after building Docx.Cli."""

from base64 import b64decode
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
from xml.etree import ElementTree as ET
from zipfile import ZipFile


CLI = Path(__file__).resolve().parents[1] / "dotnet/Docx.Cli/bin/Debug/net8.0/Docx.Cli.dll"
NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
}
W = "{" + NS["w"] + "}"
PIXEL_PNG = b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jBtQAAAAASUVORK5CYII="
)


def run(*args, cwd, check=True):
    return subprocess.run(["dotnet", str(CLI), *args], cwd=cwd, check=check, capture_output=True, text=True)


def main():
    with TemporaryDirectory() as directory:
        work = Path(directory)
        source = work / "source with spaces"
        source.mkdir()
        (source / "figure.png").write_bytes(PIXEL_PNG)
        content = source / "content.json"
        output = work / "report.docx"
        blocks = [
            {"type": "heading", "text": "Legacy heading", "level": 2},
            {"type": "paragraph", "text": "Text with a source [S01]"},
            {"type": "table", "headers": ["Item", "Result"], "rows": [["Alpha", "Ready"]]},
            {"type": "list", "items": ["Bullet item"]},
            {"type": "list", "ordered": True, "items": ["First", "Second"]},
            {"type": "list", "ordered": True, "items": ["Restart at one"]},
            {"type": "image", "path": "figure.png", "widthPx": 72, "heightPx": 72,
             "caption": "Editable caption", "alt": "One pixel"},
            {"type": "pagebreak", "text": ""},
        ]
        content.write_text(json.dumps(blocks), encoding="utf-8")
        create = ("create", "--content-json", str(content), "--output", str(output))
        run(*create, cwd=work)
        result = run("validate", "--input", str(output), "--business", "--json", cwd=work)
        assert json.loads(result.stdout)["isValid"], result.stdout

        with ZipFile(output) as document:
            body = ET.fromstring(document.read("word/document.xml")).find("w:body", NS)
            numbering = ET.fromstring(document.read("word/numbering.xml"))
            assert body.find("w:p/w:pPr/w:pStyle", NS).get(W + "val") == "Heading2"
            assert body.find("w:tbl/w:tr/w:trPr/w:tblHeader", NS) is not None
            assert len(body.findall("w:tbl/w:tr/w:trPr/w:cantSplit", NS)) == 2
            ids = [node.get(W + "val") for node in body.findall("w:p/w:pPr/w:numPr/w:numId", NS)]
            assert ids[1] == ids[2] and len(set(ids)) == 3
            formats = [node.get(W + "val") for node in numbering.findall("w:abstractNum/w:lvl/w:numFmt", NS)]
            assert formats == ["bullet", "decimal", "decimal"]
            assert body.find(".//wp:docPr", NS).get("descr") == "One pixel"
            assert body.find("w:p/w:pPr/w:keepNext", NS) is not None
            assert "Editable caption" in [node.text for node in body.findall("w:p/w:r/w:t", NS)]
            assert body.find("w:p/w:r/w:br", NS).get(W + "type") == "page"

        previous = output.read_bytes()
        for bad_block, expected in [
            ({"type": "table", "headers": ["X", "Y"], "rows": [["Too short"]]}, "rows[0]"),
            ({"type": "image", "path": "missing.png", "widthPx": 1, "heightPx": 1}, "missing.png"),
        ]:
            content.write_text(json.dumps([*blocks, bad_block]), encoding="utf-8")
            result = run(*create, cwd=work, check=False)
            assert result.returncode != 0 and "Content block 9" in result.stderr, result.stderr
            assert expected in result.stderr, result.stderr
            assert output.read_bytes() == previous
            assert not list(work.glob(".docx-*.tmp"))


if __name__ == "__main__":
    main()
