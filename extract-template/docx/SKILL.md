---
name: docx-extract-template
description: "Extract a template skill from a Word document for filling slots, reusing structure and expression, or applying its visual style. Use when asked to extract a Word template, build a reference.docx, apply a company template to Markdown, or set up --reference-doc."
---

# Extract a template package from a docx

Input: one `.docx`. Output: a loadable skill package whose instructions and
resources match the selected reuse scope.

Run every command below from `extract-template/docx/`.

## Choose the reuse scope

Read [`../document-reuse.md`](../document-reuse.md), choose from representative
rendered pages and the user's purpose, then use the matching section below.
For style extraction, continue at [Style extraction](#style-extraction).

## Slot filling

Copy the source to `package/template.docx`. Write `package/SKILL.md` with the
slot map and filling instructions from the shared guide. Locate each slot in
the document's XML and record enough context to distinguish repeated blanks.

Tell the generated skill to edit only those slots in a copy of `template.docx`.
Replace their text inside `<w:t>` while preserving run and paragraph
properties. Slots may use non-text XML such as an underlined `<w:tab/>`.
Record their blank area and how to insert a value while preserving fixed
labels, alignment and underline extent. Replacing a tab outright can move
the text that follows it; verify the filled rendering.

Patch the affected XML entries in the ZIP; preserve all other entries as they
are. Opening and saving through python-docx or LibreOffice can rewrite parts
outside the slots. Render the filled copy and verify the values fit and the
rest of the document is unchanged. Continue at Publish the source package.

## Structure and expression reuse

Copy the source to `package/example.docx`. Write `package/SKILL.md` with the
structure and writing rules from the shared guide, grounded in the source's
actual wording. Include where each kind of new content belongs, what may vary
in length or number, and which passages remain fixed.

Instruct the skill to draft content using those rules and edit a copy of
`example.docx`. Preserve the formatting of each kind of block. Add or remove
repeating items by copying or deleting the matching paragraph, table row or
section as a whole, keeping its formatting and required XML relationships.
Let text reflow and items grow within the recorded layout rules. Render the
result to check the layout, content organization and expression. Continue at
Publish the source package.

## Locate editable text when needed

After choosing the scope, this optional inspector can locate body text runs:

```bash
python3 scripts/inspect_docx.py <source.docx> --slots
```

It does not classify the document or identify which text may change. It lists
runs containing `<w:t>`, so check the rendered pages and XML for gaps without
text, such as underlined tabs. Do not treat a field's cached result as editable
text; Word recomputes it.

## Publish the source package

```bash
node ../scripts/cover-page.mjs --input <the original .docx> --out cover.png
```

```bash
npx --yes --package="${CLI_PKG_URL}" okou user-template publish \
  --title "<user-visible template name>" \
  --kind document \
  --source <the original .docx> \
  --cover cover.png \
  --page-count <pageCount from cover-page.mjs> \
  --package package
```

`--source` and the copy in `package/` are both needed: the first is what a
reader opens, the second is the only one a later run can open. Publish without
`--cover` and `--page-count` only when `cover-page.mjs` failed; report what it
said.

Say the template exists only after the command succeeds, then stop.

## Style extraction

### Prerequisites

```bash
python3 scripts/ensure_pandoc.py --dir ./vendor   # then run the export PATH line it prints
```

### 1. Inspect

```bash
python3 scripts/inspect_docx.py <source.docx>
```

Note the missing required styles, the paper size, and every `REVIEW` line.
`[styles in use]` decides how to extract the visual styles:

- the document uses its own style names: run step 2 with the `--map` it
  prints, after checking which pandoc style each name plays the part of;
- the document is formatted by hand (`Normal` with direct formatting): its
  styles carry nothing. Render it as the inspector says and follow the Style
  extraction steps in `../pdf/SKILL.md` on the render instead of continuing here.
Ignore the exit code.

### 2. Build

```bash
python3 scripts/build_reference.py <source.docx> reference.docx \
        [--map 'Memo Title=Title,Section Head=Heading1,Body Copy=BodyText']
```

Missing styles are filled in. If it prints `ACTION REQUIRED`, set the paper
size in step 3.

### 3. Adjust

Required when step 1 or 2 asked for it; otherwise optional.

```bash
# paper size, and the header values step 1 flagged (left = literal text in the source)
python3 scripts/set_header_footer.py reference.docx --paper A4 \
        --replace "DOC-2026-001=[DOC ID]" --replace "Jane Doe=[OWNER]"

# style values
python3 scripts/set_style.py reference.docx --list
python3 scripts/set_style.py reference.docx "Block Text" --font Georgia --size 10.5 --color 6C757D
python3 scripts/set_style.py reference.docx "Source Code" --create --font Consolas --size 9

# only to change the layout; a multi-column source is already multi-column
python3 scripts/set_header_footer.py reference.docx --columns 2 --column-gap 20

# only for a plain-text header/footer, or to add one; rebuilds the part
python3 scripts/set_header_footer.py reference.docx --footer "Confidential - page " --page-number
```

Style names are the `w:name`, case-insensitive. `set_style.py` options:
`--font --east-asia-font --size --color --bold/--no-bold --italic/--no-italic
--before --after --line --indent --left-indent --align --keep-next`.

### 4. Verify

```bash
python3 scripts/verify_reference.py reference.docx
```

Exit code must be 0. Dangling style → step 2. No paper size → step 3 with
`--paper`.

### 5. Package

```bash
python3 scripts/make_package.py <source.docx> reference.docx <out dir>
```

The output directory name is the skill name; `--name` overrides it. Add
anything the scripts could not read to the package's `Limits`.

### 6. Publish

```bash
node ../scripts/cover-page.mjs --input <source.docx> --out cover.png
```

```bash
npx --yes --package="${CLI_PKG_URL}" okou user-template publish \
  --title "<user-visible template name>" \
  --kind document \
  --source <source.docx> \
  --cover cover.png \
  --page-count <pageCount from cover-page.mjs> \
  --package <out dir>
```

Publish without `--cover` and `--page-count` only when `cover-page.mjs`
failed; report what it said. Say the template exists only after the command
succeeds.

## Rules

- Reproduce the source. Do not correct an inverted hierarchy or a style left
  at a default; the package records it.
- Replace the source's own title, document number, version, owner and date in
  the header and footer with `--replace`; they are copied into every output.
- Change the column layout only when asked.
- Do not edit `w:styleId`. Do not add style names outside pandoc's set.
- Step 4 is mandatory.

## Troubleshooting

| Symptom | Action |
|---|---|
| Headings render like body text | Step 4 names the missing style |
| CJK text falls back to a serif font | The source names no East Asian font. `set_style.py Normal --east-asia-font NAME` fills that slot and leaves the Latin font alone |
| Code blocks will not restyle | `set_style.py reference.docx "Source Code" --create` |
| Output carries the source's number or owner | `set_header_footer.py --replace` |
| Header text sits outside the text area | Step 1 reports the tab stop; rebuild the header with `--header 'left\tright'`, which places it from the margins |
| A docx saved by WPS fails to parse | Re-save it from Word, restart at step 1 |
| A slot-filling template comes back redrawn in a similar style | Its package carries no copy of the source, so there was nothing to edit. Add the file and republish |
| A rendered page drops the text held in content controls | LibreOffice exports those as form fields, whose appearance font carries no CJK. Render with `--convert-to png`, or export the PDF with `ExportFormFields` false |
