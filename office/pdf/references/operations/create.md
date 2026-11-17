# CREATE a PDF

Use this cover/body pipeline for a new PDF whose requirements it can implement.
Use the concise [preset/override catalog](../common/presentation.md); keep script
tokens unless user styles require changes. Consult [requirement profiles](../domains/profiles.md)
only for a named manuscript or Word/PDF companion. Check input existence/type,
prepare content, then use the feature-scoped [environment check](../implementation/environment.md)
once per unchanged session; do not require the optional design reference.

The pipeline renders the body before launching the cover browser. Then it merges
the two PDFs, reopens the candidate, and replaces the output after it passes the
page-count check.

```bash
bash "$SKILL_DIR/scripts/make.sh" run \
  --title "Q3 Strategy Review" --type proposal \
  --author "Strategy Team" --date "October 2025" \
  --content content.json --out report.pdf
```

Prepare `content.json` from the actual source using the
[block contract](../implementation/content.md#block-contract) and only its
applicable feature sections. Do not deliver sample/default findings; preset
selection does not supply content. Do not invent CLI flags.
The `run` command requires `--content`. Use `demo` for sample material.
If a block fails, fix the input or the missing dependency and rerun. The
destination retains its previous contents on failure.

For Word plus PDF, render the authored DOCX through the
[DOCX route](../../../docx/SKILL.md), rather than separately designing the PDF.
After creating a PDF, follow [VALIDATE](validate.md): successful merging does not
establish content completeness, correct figures or standards compliance.
