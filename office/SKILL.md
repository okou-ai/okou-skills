---
name: office
description: >
  Create, edit, format, convert, or validate Word documents, PDFs, and Excel
  workbooks. Use for file-specific checks of layout, formulas, or form fields.
  For content-only reading, extraction, or summaries, use a reader directly.
license: MIT
---

# Office files

Choose the route for the requested operation and follow its setup and validation
instructions. Load only the references that operation needs.

- [Word](docx/SKILL.md) for DOCX work and DOCX-to-PDF.
- [PDF](pdf/SKILL.md) for standalone PDF work and forms.
- [Excel](xlsx/SKILL.md) for XLSX work.

For deliverables that require developing or revising analytical conclusions,
read [Analysis](references/analysis.md). If an available domain skill covers
the method needed, follow its analytical guidance alongside the selected file
workflow.

When drafting or revising prose, use a professional register that suits the
document type and the reader's expectations. Use standard domain terms and
natural phrasing in the requested language. Before delivery, reread the title,
headings at every level, and key paragraphs in the finished draft. Replace
attention-grabbing questions, slogan-like wording, and drafting labels with
headings and phrasing customary for this type of document. Read the full text
for natural expression in the requested language, paying particular attention
to the wording of domain terms.

Honor the supplied template and limit edits to the requested scope. When
delivering Word and PDF versions of the same document, render the PDF from the
authored DOCX.

## Download the Office package from main

When a fresh source copy is needed, use the helper below instead of the
repository-level codeload archive. It downloads Git metadata and only `office/`
file contents from current `main`, then writes an `office.tar.gz` containing the
complete Office package: this entry point, shared references, DOCX, PDF, XLSX,
and their license/upstream notices. Other skills and Git history are excluded.
Use an existing local package when no refresh is needed.

Requires Git with partial-fetch/sparse-checkout support and Python 3 (standard
library only). No commit SHA is required:

```bash
DEST="./generated/resources"
mkdir -p "$DEST"
curl -fsSL "https://raw.githubusercontent.com/okou-ai/okou-skills/main/office/scripts/download_office.py" \
  -o "$DEST/download_office.py"
python3 "$DEST/download_office.py" --out "$DEST/office.tar.gz"
tar -xzf "$DEST/office.tar.gz" -C "$DEST"
```

Read `$DEST/office/SKILL.md`, select the required format, and follow its setup
and validation instructions. The helper resolves `main` once per download and
reports that SHA for traceability; it does not require or default to a fixed
commit. The archive is source-only: .NET, Python libraries, and rendering
dependencies are still provisioned separately. This source download does not
change the default `office` runtime package.

The format implementations are adapted from MiniMax's MIT-licensed skills.
Each format directory retains its `LICENSE` and `UPSTREAM.md`.
