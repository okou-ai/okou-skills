# Scenario A: Creating a New DOCX from Scratch

## Contents

- [When to Use](#when-to-use)
- [Step-by-Step Workflow](#step-by-step-workflow)
- [Document Type Defaults](#document-type-defaults)
- [Content Configuration JSON Format](#content-configuration-json-format)
- [Reusable Report Workflow](#reusable-report-workflow)
- [Complex Elements Guide](#complex-elements-guide)
- [Post-Creation Checklist](#post-creation-checklist)

## When to Use

Use Scenario A when:
- The user has no existing file and wants a brand new document
- The user provides content (text, tables, images) and wants it assembled into a DOCX
- The user specifies a document type (report, letter, memo, academic) or describes a custom layout

Do NOT use when: the user already has a DOCX they want to modify (→ Scenario B) or wants to restyle an existing document (→ Scenario C).

---

## Step-by-Step Workflow

### 1. Determine Document Type

First apply the [entry routing order](../../SKILL.md#routing-order-common--applicable-profile--operation):
resolve the user's requirements/template and select an applicable presentation
profile before using generic defaults here. A structured supplied template goes
to C-2 even when its body content is new. Then infer a generic type if needed:

| Type | Typical Signals |
|------|----------------|
| Report | "report", "analysis", "whitepaper", sections with headings |
| Letter | "letter", "dear", address block, salutation |
| Memo | "memo", "memorandum", To/From/Subject fields |
| Academic (generic only) | "paper", "essay" without a named format or supplied template |
| Named format / thesis template | Use the entry's academic or thesis/template profile, not generic defaults |
| Custom | None of the above, or user specifies exact formatting |

### 2. Gather Content Requirements

Collect from the user:
- Title and subtitle (if any)
- Author / organization
- Section structure (headings and nesting)
- Body content per section
- Tables (headers + rows)
- Images (file paths or placeholders)
- Special elements: TOC, page numbers, watermark, headers/footers

### 3. Select Style Set

For generic direct-C# authoring only, these XML assets are optional starting points:
- Report → `assets/styles/default_styles.xml` or `assets/styles/corporate_styles.xml`
- Academic → `assets/styles/academic_styles.xml`
- Letter / Memo / Custom → `assets/styles/default_styles.xml` (with overrides)

The CLI does **not** load these assets. `--type academic` chooses generic font
defaults, not APA/IEEE selection; no named-format CLI flag exists. For a named
profile, read its actual sample file/method and adapt task-specific C# instead.
Do not copy sample findings, citations, agency details or business data.

### 4. Configure Page Setup

Set `w:sectPr` from the selected profile/template or explicit user requirements;
use the generic suggestions below only when none applies. CLI page size defaults
to Letter, not A4; pass `--page-size a4` explicitly when A4 is selected.

```xml
<w:sectPr>
  <w:pgSz w:w="11906" w:h="16838" />  <!-- A4 -->
  <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"
           w:header="720" w:footer="720" w:gutter="0" />
</w:sectPr>
```

### 5. Build Document Structure

Assemble `word/document.xml` with:
1. `w:body` as root container
2. Paragraphs (`w:p`) with heading styles for section titles
3. Body paragraphs with `Normal` style
4. Tables, images, and other elements as needed
5. Final `w:sectPr` as last child of `w:body`

### 6. Apply Typography Defaults

Set document-level defaults in `styles.xml` under `w:docDefaults`:
```xml
<w:docDefaults>
  <w:rPrDefault>
    <w:rPr>
      <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:eastAsia="SimSun" w:cs="Arial" />
      <w:sz w:val="22" />  <!-- 11pt -->
      <w:szCs w:val="22" />
    </w:rPr>
  </w:rPrDefault>
  <w:pPrDefault>
    <w:pPr>
      <w:spacing w:after="160" w:line="259" w:lineRule="auto" />
    </w:pPr>
  </w:pPrDefault>
</w:docDefaults>
```

### 7. Add Complex Elements

See the Complex Elements Guide section below.

### 8. Run Validation Pipeline

```bash
bash "$SKILL_DIR/scripts/docx.sh" validate --input output.docx --business
```

---

## Document Type Defaults

These are generic authoring suggestions, **not** exact CLI/asset specifications
or named-format requirements. CLI font/heading defaults and XML assets differ;
inspect effective styles when exact values matter. Do not impose generic
14/13/12 pt academic headings on APA's all-12-pt hierarchy or a 12 pt body on
HBR's 11 pt recipe. For a generic memo, use A without a domain recipe;
the CLI's `--type memo` alone does not construct To/From fields or 0.75-inch
margins. Build those explicitly if required.

### Report
| Property | Value |
|----------|-------|
| Body font | Calibri 11pt |
| Heading font | Calibri Light |
| H1 / H2 / H3 / H4 size | 28pt / 24pt / 18pt / 14pt |
| Heading color | #2F5496 (corporate blue) |
| Margins | 1 inch (1440 DXA) all sides |
| Page size | A4 (11906 × 16838 DXA) |
| Line spacing | Single (line="240") |
| Paragraph spacing | 0pt before, 8pt after body |

### Letter
| Property | Value |
|----------|-------|
| Font | Calibri 11pt |
| Page size | Letter (12240 × 15840 DXA) |
| Margins | 1 inch all sides |
| Structure | Date → Address → Salutation → Body → Closing → Signature |
| Line spacing | Single |

### Memo
| Property | Value |
|----------|-------|
| Font | Arial 11pt |
| Page size | Letter |
| Margins | 0.75 inch (1080 DXA) |
| Header | "MEMO" centered, bold, 16pt |
| Fields | To, From, Date, Subject (bold labels, tab-aligned values) |

### Academic
| Property | Value |
|----------|-------|
| Font | Times New Roman 12pt |
| Line spacing | Double (line="480") |
| Margins | 1 inch all sides |
| Page size | Letter |
| Headings | Bold, same font, 14/13/12pt for H1/H2/H3 |
| First line indent | 0.5 inch (720 DXA) |
| Heading color | Black (no color) |

---

## Content Configuration JSON Format

The CLI `create --content-json` option reads an array of content blocks. Save
this example as `content.json`:

```json
[
  { "type": "heading", "text": "Executive Summary", "level": 1 },
  { "type": "paragraph", "text": "Revenue grew 12% year-over-year." },
  { "type": "pagebreak", "text": "" },
  { "type": "heading", "text": "Detailed Analysis", "level": 1 },
  { "type": "paragraph", "text": "North America revenue reached $4.2M, up 15%." }
]
```

Each block requires a case-sensitive `type`:

- `heading` — `text` and optional `level` from 1 to 6 (default: 1).
- `paragraph` — body `text`, including inline source locators.
- `pagebreak` — a page break.
- `table` — `headers` as strings and `rows` as arrays of strings. Each row must
  match the number of headers. Headers repeat and ordinary rows stay together
  across pages. For readability, keep each row short enough to fit a page.
- `list` — `items` as strings and optional boolean `ordered` (default: bullets).
- `image` — PNG or JPEG `path` relative to the JSON file (or absolute),
  `widthPx` and `heightPx` in the image's aspect ratio, `caption`, and optional
  `alt`. The report scales images wider than the page body to fit.

Set the document type, title, author, page size, and margins with CLI options:

```bash
bash "$SKILL_DIR/scripts/docx.sh" create \
  --type report --title "Quarterly Revenue Analysis" --author "Finance Team" \
  --page-size a4 --margins standard \
  --content-json content.json --output report.docx
```

For complex layout or format-specific features, use the [direct C# path](../implementation/authoring.md#project-scaffold).

## Reusable report workflow

After the DOCX setup, write the content once and use this command for a report
with ordinary editable paragraphs, headings, lists, tables and inline images.

```bash
python3 "$SKILL_DIR/scripts/report.py" build \
  --content report.json --title "Report title" --output report.docx \
  --timings timing.jsonl
```

The command publishes the DOCX path after package and business validation.
For a companion PDF or visual review, add `--pdf preview.pdf` and inspect the
actual candidate. Run the separate Writer probe when a conversion fails and
you need to distinguish a candidate problem from a runtime problem. A failed
render leaves the structurally validated DOCX available. If the renderer alone
needed repair, render that file again with `render_docx.py`.

The workflow accepts WebP source images when Pillow or `dwebp` is available.
It creates lossless PNG derivatives in temporary storage and leaves the
source images unchanged. Complete the draft and citation checks before the
build. Regenerate when a specific content or layout issue needs correction.

For measured runs, record `started` and `finished` near each actual boundary
using `report.py mark --timings timing.jsonl <setup|inputs|analysis|upload> <event>`.
The build records creation, validation and requested rendering with monotonic
durations and success/failure. Use one timing file per run. Compute elapsed
times between matching external milestones and keep failed attempts in the log.
Use the platform receipt to measure submission to the first usable file.

---

## Complex Elements Guide

### Table of Contents

Insert a TOC field code. Word will update the actual entries when the file is opened:

```xml
<w:p>
  <w:pPr><w:pStyle w:val="TOCHeading" /></w:pPr>
  <w:r><w:t>Table of Contents</w:t></w:r>
</w:p>
<w:p>
  <w:r>
    <w:fldChar w:fldCharType="begin" />
  </w:r>
  <w:r>
    <w:instrText xml:space="preserve"> TOC \o "1-3" \h \z \u </w:instrText>
  </w:r>
  <w:r>
    <w:fldChar w:fldCharType="separate" />
  </w:r>
  <w:r>
    <w:t>[Table of contents — update to populate]</w:t>
  </w:r>
  <w:r>
    <w:fldChar w:fldCharType="end" />
  </w:r>
</w:p>
```

### Page Numbers in Footer

Add a footer part (`word/footer1.xml`) and reference it in `w:sectPr`:

```xml
<!-- In footer1.xml -->
<w:ftr xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:p>
    <w:pPr><w:jc w:val="center" /></w:pPr>
    <w:r>
      <w:fldChar w:fldCharType="begin" />
    </w:r>
    <w:r>
      <w:instrText>PAGE</w:instrText>
    </w:r>
    <w:r>
      <w:fldChar w:fldCharType="separate" />
    </w:r>
    <w:r><w:t>1</w:t></w:r>
    <w:r>
      <w:fldChar w:fldCharType="end" />
    </w:r>
  </w:p>
</w:ftr>

<!-- In sectPr -->
<w:footerReference w:type="default" r:id="rId8" />
```

### Watermark

Add a header part with a shape behind the text:

```xml
<w:hdr>
  <w:p>
    <w:r>
      <w:pict>
        <v:shape style="position:absolute;margin-left:0;margin-top:0;width:468pt;height:180pt;
                        z-index:-251657216;mso-position-horizontal:center;
                        mso-position-vertical:center"
                 fillcolor="silver" stroked="f">
          <v:textpath style="font-family:'Calibri';font-size:1pt" string="DRAFT" />
        </v:shape>
      </w:pict>
    </w:r>
  </w:p>
</w:hdr>
```

---

## Post-Creation Checklist

1. **Validate** — follow the [validation pipeline](validate.md): `validate --input output.docx --business` runs OpenXML SDK validation on all package parts and the business checks.
2. **Optional subset validation** — add `--xsd "$SKILL_DIR/assets/xsd/wml-subset.xsd"` only for documents intentionally restricted to that subset. Do not remove valid document features to satisfy the subset schema.
3. **Repair as needed** — use `fix-order` only for diagnosed ordering errors and `merge-runs` only when consolidation is needed. Revalidate after repairs.
4. **File size** — confirm images are reasonably sized (compress if > 2MB each)
