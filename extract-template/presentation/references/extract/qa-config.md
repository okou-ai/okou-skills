# Record the source QA configuration

Use during extraction, before installing the generation runtime.

`tools/qa-config.json` records observed source rules. Its shape is:

```json
{
  "minFontSizePx": 10,
  "safeArea": {"left": 0.06, "right": 0.06, "top": 0.14, "bottom": 0.1},
  "layoutSafeAreas": {},
  "requiredChrome": [],
  "allowedFontFallbacks": [],
  "minContrastRatio": 3
}
```

The inset numbers above are an **illustration**. Use the saved source margins,
including any `layoutSafeAreas` keyed by a stage's `data-layout` or
`data-source-profile`. Extraction supplies either a valid global safe area or an
entry for every source profile; package verification rejects missing or invalid rules.
A required chrome rule names `role`, optional `min`/`max`, and optional `layouts`.
Mark only source-required items with `data-chrome="<role>"`; absence in the source
is not a reason to invent a footer, motif or page marker. Fallback font families
must be explicitly approved in design notes before listing them here.
List replacement families (for example `Arial`), not the name of a failed primary
font. When a used webfont fails, the first available family in that text's CSS
font stack must be an approved fallback; approving a later, unused family is insufficient.

The installer embeds this configuration in the shared shell. Source layouts use
the HTML hooks in [runtime-contract.md](../generate/runtime-contract.md), which is
also shipped for later layout adaptation. Saving the template requires the package
check in [SKILL.md](../../SKILL.md); generation QA runs on later completed decks.
