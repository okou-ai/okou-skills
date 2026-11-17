# REFORMAT an existing document

Use only when redesign/reformatting is authorized, not for a simple form fill or
an exact-layout edit. First check the input exists and has a supported type.
Choose a supported [preset](../common/presentation.md) once, keeping its script
tokens unless user styles require overrides. Named manuscripts use the conditional
[requirement profiles](../domains/profiles.md), not a mandatory design tutorial.

The wrapper parses an existing document to `content.json`, then uses CREATE:

```bash
bash "$SKILL_DIR/scripts/make.sh" reformat \
  --input source.md --title "My Report" --type report --out output.pdf
```

Supported input formats are `.md` `.markdown` `.txt` `.pdf` `.json`. Parsing text
or JSON alone uses the standard library; only PDF extraction loads `pypdf`.
For independent review before authoring, run `reformat_parse.py --input source.md
--out content.json`, compare its blocks against the source, then use CREATE with
the feature-scoped [environment](../implementation/environment.md). The wrapper
also delays body rendering until parsing succeeds. For structured Markdown,
select [content features](../implementation/content.md) from the actual content,
not the filename or visual preset. The wrapper does not enforce the feature QA
or guarantee preservation of every source structure. Parsing PDF text is
best-effort, not lossless layout preservation or source reconstruction.

Compare reconstructed content against the source and apply
[CREATE/REFORMAT checks in VALIDATE](validate.md#create--reformat) to actual output.
No general READ/OCR/signature workflow is added. If exact fidelity is required,
establish a capable route instead of claiming this parser preserves it.
