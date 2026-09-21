# Word authoring and editing

Choose the authoring route from the required structure and the supplied source.
A DOCX is an editable document package, not a screenshot or a compulsory
Markdown intermediate. A supplied document or template remains the visual
authority; use the shared layout guidance only where it leaves a choice.

| Situation | Route |
| --- | --- |
| New Word document needing explicit styles, sections, tables and fields | `docx` for Node.js is a useful default; `python-docx` is also suitable when its API covers the content. |
| Existing Word with simple, supported edits | Open the original with `python-docx`, edit only the necessary objects, and compare the result. |
| Existing Word with revisions, content controls, unusual fields, embedded objects or complex relationships | Make focused OOXML changes while preserving all untouched package parts. |
| Real reusable template containing placeholders | Use `docxtpl` and the template's existing styles and content skeleton. |
| Semantic prose, citations, equations or conversion between supported formats | Use Pandoc with the relevant readers, extensions, filters, templates and options. |

## New Word with `docx`

Install in a task-local project so the authoring script can resolve its dependency.
Retain `package-lock.json` with the source to reproduce the selected version.

```bash
mkdir -p generated/word-author
cd generated/word-author
npm init -y
npm install --save-exact docx
```

Save this minimal example as `author.cjs` in that directory. Pass an installed
font family appropriate to the actual language; the example does not establish
that any particular font exists on the rendering host.

```javascript
const fs = require("node:fs/promises");
const { Document, Packer, Paragraph, HeadingLevel } = require("docx");

async function main() {
  const [font, output] = process.argv.slice(2);
  if (!font || !output) throw new Error("Usage: node author.cjs FONT OUTPUT.docx");
  const document = new Document({
    styles: {
      default: {
        document: {
          run: { font, size: 22 },
          paragraph: { spacing: { after: 160 } },
        },
      },
    },
    sections: [{
      properties: {},
      children: [
        new Paragraph({ text: "Quarterly review", heading: HeadingLevel.TITLE }),
        new Paragraph({ text: "Findings", heading: HeadingLevel.HEADING_1 }),
        new Paragraph("Replace this example with the approved source content."),
      ],
    }],
  });
  await fs.writeFile(output, await Packer.toBuffer(document));
}
main().catch((error) => { console.error(error); process.exitCode = 1; });
```

Before delivery, set the page size, margins, language and styles for the task.
Use semantic heading levels, numbering definitions and real page-number fields;
do not simulate them with bold text, typed bullets or repeated spaces. Use
paragraphs for paragraphs and explicit line breaks only within a paragraph.
Assign table and column widths in consistent units within the usable page
width. Repeat table headers where appropriate, and allow genuinely tall rows
to continue rather than forcing an entire table onto one page. Keep images at
their aspect ratio and captions with the relevant figure. A generated table of
contents is a field whose updated content must be verified in the final export.

## Python creation and genuine templates

Install only the libraries selected for the job:

```bash
python3 -m pip install --break-system-packages python-docx
python3 -m pip install --break-system-packages docxtpl
```

`python-docx` can create native paragraphs, styles, tables, sections, headers and
footers, or start with `Document("source.docx")`. Check that its API covers the
features that must survive. Assigning `paragraph.text` or `cell.text` replaces
their existing run content and can destroy local formatting or fields; it is
not a general find-and-replace operation. For a supported small edit, target
the intended runs and assert the match count before saving to a new file.
Text may span multiple runs; never flatten the document just to make a phrase
searchable. Some structures are not represented in the high-level API.

Use `docxtpl` when the source actually has placeholders, for example
`{{ client_name }}`. A styled document without placeholders is not a mail-merge
template. Keep placeholder syntax valid in its runs; use the library's explicit
paragraph/row tags for repeated blocks rather than inventing XML replacement.

```python
from docxtpl import DocxTemplate

template = DocxTemplate("template.docx")
template.render({"client_name": "Example Company"}, autoescape=True)
template.save("filled.docx")
```

Check missing/unfilled placeholders, repeated rows, optional sections and
longest realistic values. Preserve logos, headers, numbering, fields and
dimensions supplied by the template. A Pandoc `--reference-doc` supplies styles
and document properties; it does not reproduce this body-content skeleton.

## Focused OOXML changes to existing files

1. Keep the original immutable. Inventory ZIP parts, relationships and affected
   content before editing; inspect headers/footers or other parts when the
   requested text is not in `word/document.xml`.
2. Locate the exact affected paragraphs/runs with namespace-aware XML handling.
   Preserve formatting boundaries, hyperlinks, bookmarks, field instructions,
   whitespace and revision boundaries. Do not merge differently formatted runs
   or rewrite unrelated text to simplify replacement.
3. Change the smallest supported structure. Preserve untouched parts as bytes;
   update relationship IDs and content-type entries when adding/removing parts.
   Do not pretty-print the entire package or silently accept tracked changes.
4. Compare the part inventory and hashes, parsed XML and intended text delta.
   Check referenced IDs/targets, relevant OOXML schema constraints, and the
   original versus edited rendering. XML that parses successfully is not proof
   of a valid Word document or preserved layout.

This self-contained packaging example replaces an already-edited XML part and
copies all other members without modifying their contents. It is not an XML
editor or a schema validator, and it does not handle newly added parts.

```python
from pathlib import Path
from zipfile import ZipFile

changes = {"word/document.xml": Path("edited-document.xml").read_bytes()}
with ZipFile("source.docx") as original, ZipFile("edited.docx", "w") as edited:
    names = original.namelist()
    if len(names) != len(set(names)):
        raise ValueError("Duplicate ZIP member names require investigation")
    if not changes.keys() <= set(names):
        raise ValueError("Replacement part is absent from the original")
    for member in original.infolist():
        data = changes.get(member.filename)
        edited.writestr(member, original.read(member) if data is None else data)
```

Tracked changes and comments need feature-aware handling: revision authors and
IDs, insertion/deletion elements, paragraph-mark deletions, comment anchors,
relationships and comment parts must remain coherent. Deleting visible text is
not equivalent to accepting a revision. Use a validated implementation for the
specific feature and check both revision semantics and rendering; do not claim
redline preservation from the accepted-view PDF alone. Convert legacy `.doc`
with a compatible office suite before DOCX editing and inspect that conversion.

## Pandoc remains a full authoring/conversion option

Use the bundled Pandoc from the shared setup, or an appropriate installed
version. The convenience renderer is not a restriction on Pandoc's ecosystem.
When citations, cross-references, reader extensions or Lua filters are needed,
invoke Pandoc directly with the required options, then verify its finished
DOCX using the shared flow. Retain filters, references and resource files.

```bash
PANDOC_BIN="$(python3 -c 'import pypandoc; print(pypandoc.get_pandoc_path())')"
"$PANDOC_BIN" manuscript.md --from markdown --to docx \
  --reference-doc style.docx --citeproc --bibliography references.bib \
  --resource-path .:assets --output authored.docx
```

Supply only options/resources the task uses. Check feature fidelity instead of
assuming every reader/writer round-trip preserves the input. Existing complex
Word files should not take this route just for a small edit.

## Fonts and final verification

Check actual font availability and script coverage on the rendering host;
setting a font name in DOCX does not embed it. CJK documents need an appropriate
regional face and explicit document language, including Simplified versus
Traditional Chinese when known. RTL needs paragraph direction and run-level
complex-script settings, appropriate fonts and correct mixed-script ordering;
right alignment alone is insufficient. Inspect numbers, punctuation, Latin
identifiers and tables in the final pages. Do not apply blanket font replacement
to a supplied template without a concrete need.

Follow [the shared verification and delivery flow](../SKILL.md) on the actual
finished DOCX. When delivering a matching PDF, export that DOCX; do not create a
separate approximation with another renderer. Keep the native authoring source
and dependencies for revisions. Explain any material differences between the
verified rendering engine and the user's target Word environment.
