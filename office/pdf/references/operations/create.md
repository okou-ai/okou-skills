# CREATE a PDF

Use for a new PDF whose requirements the cover/body pipeline can implement.
Select [requirement profiles](../domains/profiles.md) and
[presentation](../common/presentation.md), honoring user templates first.
Set `SKILL_DIR` and `OFFICE` per [the entry point](../../SKILL.md).

Prepare `content.json` from actual sources using the authoritative
[block contract](../implementation/content.md#block-contract) and applicable
feature sections. The author owns evidence, arithmetic, attribution and meaning;
never deliver sample/default findings. Presets control appearance, not domain
expertise, citations or named-standard compliance.

```bash
python3 "$OFFICE" preflight --format pdf
python3 "$OFFICE" create --format pdf --content content.json \
  --title "Report" --out report.pdf
```

Use `create --help` / `tool-help --tool pdf-create` for options and existing
preset names, not invented flags. Preflight checks the environment, not output
quality. For Word plus PDF, render the authored [DOCX](../../../docx/SKILL.md)
instead of designing a second document. Preserve sources and follow
[VALIDATE](validate.md); a successful create/merge receipt is not acceptance.
