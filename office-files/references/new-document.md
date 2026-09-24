# New Word/PDF prose

Use this route for new prose. Follow a supplied template's entry point; use
[Word](word-authoring.md) or [PDF](pdf-authoring.md) for existing files and native
features. Word and PDF share one content source.

## Set up and write

Set the skill's absolute path in each shell using the variable. Run setup once;
if background tools are available, draft while it installs and confirm success
before preparation.

```bash
export OFFICE_FILES_DIR=/absolute/path/to/office-files
python3 "$OFFICE_FILES_DIR/scripts/setup_office.py" document \
  --out generated/setup-document.json
mkdir -p generated/document
```

Write `generated/document/document.md` directly with the requested content.
[The sample](../assets/document.md) demonstrates syntax, not required sections.
Use semantic headings, lists and tables where useful, and declare the language:

```markdown
---
title: Service access
lang: en-US
---

# Request access

Contact the service owner and state the access you need.
```

Use the purpose, reader, supplied information and required wording to organize
the document. For an ordinary drafting task, write the complete draft without
first producing a separate outline, data model or report configuration. Reuse a
provided outline. Check coverage, names, dates, consistency and actionable steps
against the request. Literal dates or numbers do not require a calculation model.
Keep implementation details and QA notes out of the document.

Read only the additional instructions the content needs:

- **Substantive analysis, conflicting sources or complex rule dependencies:**
  [targeted content checks](content-checks.md). Calculations are only one possible
  trigger; a policy can need deep checks without any arithmetic. Routine sourced
  instructions and straightforward restatements stay on the default route.
- **A requested or useful chart:** [document charts](document-charts.md).
- **Custom appearance:** copy [style settings](../assets/document-style.json) and
  pass `--style`; otherwise use the built-in defaults. Read [editorial
  components](pandoc-authoring.md#optional-editorial-components) only when needed.

## Prepare once the complete draft is ready

Write `generated/document/expectations.json` from the request and source, using
actual required wording or key facts rather than copying checks from the
finished draft. For the access example, if the request specified these terms:

```json
{
  "required_text": ["Service access", "service owner"],
  "same_page": [],
  "not_applicable": {}
}
```

Headings and their opening paragraphs are added automatically. For an additional
required grouping, use `{"first":"Unique lead-in", "second":"Unique body text",
"reason":"Why these belong together"}` in `same_page`. A document without any
applicable groups needs a specific `not_applicable.same_page` reason. Do not
require entire tables or chapters to fit on one page.

```bash
python3 "$OFFICE_FILES_DIR/scripts/prepare_document.py" generated/document/document.md \
  --out generated/document/output --expectations generated/document/expectations.json
```

Add `--content-review independent` when the targeted content checks call for an
independent reviewer. Default prose uses the author's content check. Bind actual
input files, calculation scripts and chart specs with repeated `--resource`
arguments. Keep authored inputs outside `--out`. Use `--reference template.docx`
for a style reference, or `--style style.json` for custom settings. Use
`--table-widths source` only for deliberately authored column proportions.

Preparation creates editable DOCX, PDF, timing, quick checks and `qa/`. Fix
reported blockers; an ambiguity warning calls for checking the intended text,
not automatically rewriting it. Preserve independent checks across revisions.

## Review and deliver

Complete the content check in the existing `qa/review.json` under `content`:
set `status` to `pass` only after checking the complete draft against the request
and sources, retain the required `reviewer`, and add one concise, specific
`observations` note about what was checked. This records the check; it does not
prove every statement. Independent review must actually be performed when
required. Resolve findings before approval.

Open `qa/gallery/overview-*.png`, then every full `page-NNN.png` at readable size
in small batches. For every page, explicitly check all five criteria in
`qa/review.json`: legibility, hierarchy, composition, pagination, and tables or
figures. Add one page-specific observation and explain each warning. Collect
content and layout fixes together, regenerate, and review the final candidate.
Changed content requires a current content check; unchanged passing prose needs
no stylistic rewrite. Keep natural pagination and all requested content.

```bash
python3 "$OFFICE_FILES_DIR/scripts/check_document.py" accept generated/document/output/qa
okou web upload-file -f generated/document/output/document.docx
```

Upload only after `READY_TO_DELIVER`. For final PDF, upload `document.pdf` and
its editable DOCX source. Immediately send the returned download URL(s), then
any requested retrospective. Keep sources and QA files for revisions.

Use [separate rendering and inspection commands](document-layout.md#verification)
only when the preparation command does not cover the task.
