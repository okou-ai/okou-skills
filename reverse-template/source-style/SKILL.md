---
name: source-style-template
description: "Publish a document as a template that points back at the source file itself. Use for a resume, receipt, invoice, certificate, offer letter, or any page whose body does not run as one stream, where a style-only reference.docx would drop the entries and the composition that make it what it is."
---

# Keep the source as the template

Reach this branch from check 2 of the router: the source is a form, or an
article whose body does not run as one stream.

The docx and pdf branches ship a style sheet. This branch ships the source file:
later runs open it and follow what they see.

Run every command below from `reverse-template/source-style/`.

## 1. Render the pages

```bash
okou presentation screenshot --input <source.pdf> --out package/pages
```

`okou presentation screenshot` does not read `.docx`. Export a Word source
first, and keep the original as the source file — the PDF only feeds the
renderer:

```bash
sudo apt-get update -qq && sudo apt-get install -y -qq libreoffice-writer
soffice --headless -env:UserInstallation=file:///tmp/lo \
        --convert-to pdf --outdir . <source.docx>
```

Check that every page came out, in order.

## 2. Write the package

Put this in `package/SKILL.md`:

```markdown
---
name: <template-slug>
description: <what this document is, in one line>
---

Follow the source file's own styling. It is the authority for page size,
margins, typography, colour, and the position of every block.

Replace the content, keep the composition:

- <one line per region a new document has to fill>

`pages/` holds the source's rendered pages in order.
```

Name the regions off the rendered pages — a resume's sidebar, contact block,
and experience list; an invoice's party block, line-item table, and totals.
Write nothing the pages do not show, and do not restate measurements: the
source file carries them, and a number copied out of it can only drift.

Add nothing else to `package/` beyond `SKILL.md` and `pages/`. Assets extracted
from a composed source are one-off content, not reusable material.

## 3. Publish

```bash
npx --yes --package="${CLI_PKG_URL}" okou user-template publish \
  --title "<user-visible template name>" \
  --kind document \
  --source <the original .docx or .pdf> \
  --package package
```

`--kind document` takes no `--pages`; the rendered pages ride inside
`--package`. Claim the template exists only after the command succeeds, and
report the specific blocker if it fails.

## Rules

- An article that runs as one stream belongs on the docx or pdf branch, whose
  style sheet stays editable and recomposable. Do not come here to skip that
  work — but do come here whenever check 2 is a close call, because this branch
  keeps everything.
- Do not crop the source's pages into assets. They carry the original's own
  text and data.
- One line of instruction is the deliverable. Everything a new document needs
  is visible in the source.
