# CREATE a PDF

Use this cover/body pipeline for a new PDF whose requirements it can implement.
Select [manuscript versus visual requirements](../domains/profiles.md) and
[presentation](../common/presentation.md) first; run the applicable
[environment check](../implementation/environment.md).

The implemented pipeline is content → design tokens → cover → body → merge:

```bash
bash "$SKILL_DIR/scripts/make.sh" run \
  --title "Q3 Strategy Review" --type proposal \
  --author "Strategy Team" --date "October 2025" \
  --accent "#2D5F8A" \
  --content content.json --out report.pdf
```

Prepare `content.json` from the actual source using the
[block contract](../implementation/content.md#block-contract) and only its
applicable feature sections. Do not deliver sample/default findings or treat
`--type` as a content-domain or citation validator. Read
[visual presets and overrides](../common/presentation.md#visual-presets-and-overrides)
for supported names and appearance options; do not invent CLI flags.

For Word plus PDF, render the authored DOCX through the
[DOCX route](../../../docx/SKILL.md), rather than separately designing the PDF.
After creating a PDF, follow [VALIDATE](validate.md): successful merging does not
establish content completeness, correct figures or standards compliance.
