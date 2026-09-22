# Word authoring and editing

## Start

For new prose, use the [runnable document starter](new-document.md). Use this
page for editing, template filling, or native Word features the starter lacks.

Follow a supplied template's instructions. Work on a copy of an existing file
and preserve content and formatting outside the requested changes. When layout
must be preserved, inspect the original pages before editing.

Read the [rendering setup](document-layout.md#rendering-setup), then use the
applicable method below. Keep an existing publishing workflow when appropriate.

## Create with `docx`

Install in the task's authoring directory:

```bash
mkdir -p generated/word-author
cd generated/word-author
npm init -y
npm install --save-exact docx
```

Save the example as `author.cjs`. Pass a font installed on the rendering host
that supports the document's language.

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

Set page size, margins, language and styles for the document. Use native heading
levels, numbering and page-number fields. Keep table/column widths within the
usable page width; enable repeating header rows and row splitting as needed.
Check that generated table-of-contents fields are updated in the final export.

## Edit with Python or fill a template

Run the installation command for the selected library:

```bash
python3 -m pip install --break-system-packages python-docx
python3 -m pip install --break-system-packages docxtpl
```

### `python-docx`

Open the original with `Document("source.docx")` and save edits to a new file.
Target the required runs and check the match count. Text can span multiple runs;
preserve their formatting boundaries. Assigning `paragraph.text` or `cell.text`
replaces all runs and can remove formatting or fields.

Use focused OOXML edits below for features the library's API does not cover.
For legacy `.doc`, convert with a compatible office suite and inspect the
conversion before editing.

### `docxtpl`

Use a template containing placeholders such as `{{ client_name }}`. Keep
placeholder syntax valid within runs and use the library's paragraph/row tags
for repeated blocks.

```python
from docxtpl import DocxTemplate

template = DocxTemplate("template.docx")
template.render({"client_name": "Example Company"}, autoescape=True)
template.save("filled.docx")
```

Check missing/unfilled placeholders, repeated rows, optional sections and long
values. Preserve the template's styles, fields, headers and dimensions.

## Make focused OOXML edits

1. Keep the original unchanged. Inventory ZIP parts and relationships; locate
   the affected content, including headers/footers when needed.
2. Use namespace-aware XML handling. Preserve run formatting, hyperlinks,
   bookmarks, field instructions, whitespace and revision boundaries.
3. Change only the necessary parts and preserve untouched parts byte-for-byte.
   Update relationships and content-type entries when adding or removing parts.
4. Run [the before/after comparison](#compare-before-and-after) with
   `--strict-bytes`. It checks inventories, hashes, references and protected
   features. Validate relevant OOXML schema constraints separately when needed,
   then compare the original and edited rendering.

This example replaces an already-edited XML part. Make and validate the XML
change separately; the example only packages replacements of existing parts.

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

For tracked changes and comments, preserve revision authors/IDs, insertion and
deletion elements, paragraph-mark deletions, comment anchors and their related
parts. Do not silently accept revisions. Validate revision semantics as well as
rendering; an accepted-view PDF cannot establish revision preservation.

## Compare before and after

Required for editing an existing DOCX, including template filling. Keep the
original and edited files at separate paths. Run this standard-library script
after saving the edit; `OFFICE_FILES_DIR` is set in the rendering setup:

```bash
python3 "$OFFICE_FILES_DIR/scripts/compare_docx.py" source.docx edited.docx \
  --out generated/word-comparison.json
```

The report inventories ZIP parts and their hashes, resolves relationship IDs
and targets, and compares headers, footers, images, hyperlinks, comments and
anchors, revision elements/authors/IDs, fields, drawings and bookmarks. It also
reports text and other XML changes. A missing referenced part or broken field
boundary blocks comparison and cannot be waived.

Expected edits initially produce `BLOCKED` too. Read the reported text delta
and investigate each changed part or feature. Fix unintended changes. For each
change required by the request, copy that finding's exact `code`, `part`,
`scope`, `before_sha256` and `after_sha256` into a changes policy and add a
specific reason. The two digests identify that finding's scope; copy them from
the finding, not from the ZIP inventory. For example, an intended body-text
edit uses this shape (replace the example hashes with the actual values):

```json
{
  "schema_version": 1,
  "changes": [
    {
      "code": "text_changed",
      "part": "word/document.xml",
      "scope": "text",
      "before_sha256": "<finding's before_sha256>",
      "after_sha256": "<finding's after_sha256>",
      "reason": "Change the requested revenue figure from 1000 to 1200."
    }
  ]
}
```

Approving the text delta does not approve a removed hyperlink, revision or
field. Any intentional feature removal needs its own matching explanation.
Do not copy every finding into the policy automatically or use an "all changes
approved" reason. Wildcards, stale approvals and unmatched entries are rejected.
The editing agent records these reasons as local review evidence against the
user's already-authorized request; do not ask the user to approve each edit again.

```bash
python3 "$OFFICE_FILES_DIR/scripts/compare_docx.py" source.docx edited.docx \
  --changes generated/word-changes.json --out generated/word-comparison.json
```

Continue only when the report says `PASS` (exit code 0). This checks semantic
XML rather than requiring every library save to retain identical XML bytes:
namespace/attribute serialization and equivalent relationship IDs may change,
and removing an empty `.rels` part is informational. For focused OOXML edits,
add `--strict-bytes` on both comparison runs; each changed existing part then
also needs an exact byte-change approval, so untouched parts stay identical.

Render the edited DOCX and supply
`--docx-comparison generated/word-comparison.json` to the document `inspect`
command below. Inspection binds the report, original, edited file and policy
to their hashes. Keep these files available; any later change requires a new
comparison and inspection. The compared edited DOCX must match the rendered
DOCX exactly. The script does not replace page review or full OOXML schema
validation, and a PDF alone cannot prove that comments or revisions survived.

## Font and language settings

Check installed fonts and character coverage; setting a DOCX font name does not
embed the font. For CJK, use the appropriate regional font and document language.
In OOXML, `w:lang/@w:val` controls Western text and `@w:eastAsia` controls CJK.
For Chinese/English content, set them to `en-US` and `zh-CN` respectively. Inspect
decimal numbers and Latin words for unwanted internal line breaks in the PDF.
For RTL, set paragraph direction and run-level complex-script properties, then
inspect mixed-script text, numbers and punctuation. Retain template fonts unless
the task requires a change.

## Verify and deliver

Run [document verification](document-layout.md#verification) on the finished
DOCX. For edits, include the passing comparison with `--docx-comparison` during
inspection. For matching Word/PDF deliverables, export the PDF from this DOCX
and verify the pair together.

Upload the requested files with `okou web upload-file`; include the editable
DOCX alongside a final PDF. Keep authoring sources, data, assets and QA files
for revisions.
