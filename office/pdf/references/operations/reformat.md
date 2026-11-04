# REFORMAT an existing document

Use only when redesign/reformatting is authorized, not for a simple form fill or
an exact-layout edit. Choose applicable requirements and
[presentation](../common/presentation.md), then check the
[cover/body environment](../implementation/environment.md).

The wrapper parses an existing document to `content.json`, then uses CREATE:

```bash
bash "$SKILL_DIR/scripts/make.sh" reformat \
  --input source.md --title "My Report" --type report --out output.pdf
```

Supported input formats are `.md` `.txt` `.pdf` `.json`. For structured Markdown,
select [content features](../implementation/content.md) from the actual content,
not the filename or visual preset. The wrapper does not enforce the feature QA
or guarantee preservation of every source structure. Parsing PDF text is
best-effort, not lossless layout preservation or source reconstruction.

Compare reconstructed content against the source and apply
[VALIDATE](validate.md) to actual output. This route introduces no general READ,
OCR, signature workflow, PDF-source reconstruction safeguards or new parser
semantics. If exact fidelity is required, establish a capable route instead of
claiming this parser preserves it.
