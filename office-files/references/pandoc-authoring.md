# Pandoc authoring

Use the [runnable document starter](new-document.md) for new prose. Read the
sections below only for optional editorial components or an existing Pandoc
publishing workflow.

## Install

```bash
python3 -m pip install --break-system-packages --quiet pypandoc_binary==1.17 python-docx==1.2.0
```

## Write the Markdown source

Write semantic headings, paragraphs, lists, tables, captions, footnotes and
images. Set `lang` in YAML, such as `zh-CN` or `en-US`, or pass `--lang` during
preparation. Include title, author and date only when supplied or appropriate.

During verification, pass the `.md` file to `render_document.py`.
Use `--format pdf|docx|both` to select delivery files. Use `--reference theme.docx`
only to apply a style reference to new prose.

## Optional editorial components

For new prose without a supplied template, use the bundled editorial theme
and choose components that serve the content:

| Style | Use |
| --- | --- |
| `Deck` | Opening statement that frames the document |
| `Key Takeaway` | A decision-relevant conclusion |
| `Section Lead` | Short introduction to the following section |
| `Pull Quote` | Brief emphasis within the reading flow |
| `Eyebrow` | A supplied series, edition or confidentiality label |
| `Source Note` | Concise source attribution |
| `Keep with Next` | Keep a short lead-in with the content it introduces |

Apply a style with a fenced Div:

```markdown
::: {custom-style="Key Takeaway"}
One conclusion that changes a decision.
:::
```

Use `.metric-grid` for two to four metrics. Keep exactly two rows: values, then
short labels, with interpretation in nearby prose:

```markdown
| 88.3% | 20.2× | 121× |
|------:|------:|-----:|
| usage share | multiplier gap | cost gap |

: {#opening-metrics .metric-grid}
```

Use `# Chapter title {.chapter}` for a deliberate page transition. Keep callouts
selective and avoid a repeated component under every heading. Use a normal
table for records or detailed comparisons.

Use `.chapter` on any heading level only when an explicit page transition serves
the document. For flowing reports, omit it. Keep paragraphs together with
`Keep with Next` when necessary; the generated grouping checks retain those
paragraphs.

In new house-theme documents, retain the renderer's content-based table widths.
Use `--table-widths source` only for deliberately specified Pandoc proportions;
pipe-table separator lengths can otherwise give wide numeric columns and narrow
prose columns. Supplied reference styles and native files are preserved.

The bundled theme uses warm paper, near-black text, an ink-blue accent, serif
display text and sans body text. Match chart colours to it when using this theme;
keep chart labels understandable without colour.

## Existing Pandoc publishing workflows

Invoke Pandoc directly when the source requires its readers, extensions,
citations, filters, templates or output engines. For example:

```bash
PANDOC_BIN="$(python3 -c 'import pypandoc; print(pypandoc.get_pandoc_path())')"
"$PANDOC_BIN" manuscript.md --from markdown --to docx \
  --reference-doc style.docx --citeproc --bibliography references.bib \
  --resource-path .:assets --output authored.docx
```

Use only the options and files needed by the task. During verification, declare
the source, filters, references and assets with `--resource`.

## Verify and deliver

Complete [page verification](document-layout.md#verification) for the Markdown
source or the finished DOCX/PDF from an existing pipeline. For a matching
Word/PDF pair, export the final DOCX to PDF. Check conversion fidelity in the
final pages.

Upload the requested files with `okou web upload-file`; attach the editable
source alongside a final PDF when appropriate. Keep the source, filters, data,
assets and QA files for revisions.

Editorial theme attribution: `nexu-io/open-design` at
`3fb620af423534643677c7c6fae76be088fa770a`, based on `tw93/kami` (MIT).
