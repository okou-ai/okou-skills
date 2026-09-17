"""Style names (w:name values) the pandoc docx writer references, grouped by
what happens when the reference document does not define them.

The grouping is measured, not copied from the documentation: each style was
deleted from pandoc's default reference.docx in turn, a probe document was
converted, and the output was checked for styleIds that are referenced by
<w:pStyle> but never defined. Verified on pandoc 3.5 and 3.11.

Two facts this skill relies on:
  1. Pandoc matches styles by <w:name>, not by <w:styleId>. A Chinese-locale
     Word export with styleId="1" still resolves, as long as w:name is
     "heading 1".
  2. A missing style is a silent failure. Pandoc still writes
     <w:pStyle w:val="Heading1"> but adds no style definition, so the document
     opens fine and the heading quietly renders as Normal.
"""

# Not recreated by pandoc. A dangling reference; Word falls back to Normal.
MUST_EXIST = [
    "Body Text", "First Paragraph", "Compact",
    "Title", "Subtitle", "Author", "Date", "Abstract",
    "heading 1", "heading 2", "heading 3",
    "heading 4", "heading 5", "heading 6",
    "heading 7", "heading 8", "heading 9",
    "Block Text", "Footnote Text",
    "Definition Term", "Definition", "Table Caption",
    "Verbatim Char", "Footnote Reference", "Hyperlink",
    "Table",
]

# Pandoc emits a definition for these when they are absent.
AUTO_INJECTED = [
    "Normal", "Bibliography", "Caption", "Image Caption",
    "Figure", "Captioned Figure", "TOC Heading",
    "Default Paragraph Font", "Body Text Char", "Section Number",
    "Footnote Block Text",
]

# Absent from pandoc's default reference.docx; the writer generates them.
# Customising these means creating a style with the same name by hand.
WRITER_GENERATED = ["Source Code", "AbstractTitle"]

ALL = MUST_EXIST + AUTO_INJECTED + WRITER_GENERATED

PARAGRAPH = [n for n in ALL if n not in
             ("Verbatim Char", "Footnote Reference", "Hyperlink",
              "Default Paragraph Font", "Body Text Char", "Section Number", "Table")]
CHARACTER = ["Default Paragraph Font", "Body Text Char", "Verbatim Char",
             "Footnote Reference", "Hyperlink", "Section Number"]
TABLE = ["Table"]
