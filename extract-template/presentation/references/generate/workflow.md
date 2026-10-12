# Generate a deck from this template

Read the template's `SKILL.md` and `design-system.md` for source-specific rules.
The package is ready to use; no need to extract, install or save the template again.

1. **Outline:** establish purpose, audience, language, page count and each page's message.
2. **Choose layouts:** prefer `layouts/source-index.json`; use
   `library/references/catalog.md` when source layouts do not fit. Follow
   [layout-reuse.md](layout-reuse.md) for adaptation and background selection.
3. **Assemble:** copy `layouts/_shell.html` into the final web directory, resolve
   final asset paths and insert editable content supported by the source material.
   Preserve the source styling and [10px floor](typography-fit.md). Keep the stored
   template and library originals unchanged. Use [runtime hooks](runtime-contract.md)
   when changing structure, navigation or charts.
4. **Run QA:** follow [qa.md](qa.md) with the planned page count. Diagnose reported
   causes, fix them together and rerun on the same final HTML after edits.
5. **Review and deliver:** inspect only QA-designated pages unless a full review was
   requested. Record any required receipt and pass final QA. Follow the QA guide
   for capture staging, requested PPTX checks and one final publication/upload.
