# PDF package

Start with [SKILL.md](SKILL.md) for task scope, manuscript/preset selection and
CREATE / FILL / REFORMAT routing. This is part of the single
[Office package](../SKILL.md), not a separate default skill.

Documentation has one owner per responsibility:

- [Common presentation](references/common/presentation.md): visual presets,
  tokens, typography and appearance priorities.
- [Requirement profiles](references/domains/profiles.md): named manuscript
  requirements versus visual-only presets and Word/PDF companions.
- [Operations](references/operations/create.md): task workflows; all operation
  and implementation guides are directly linked from `SKILL.md`.
- [Content contract](references/implementation/content.md): supported block
  fields, feature limits and feature-specific QA.
- [Environment](references/implementation/environment.md): route-specific
  dependencies and setup gates.

Scripts remain under `scripts/` with the same CLI entry points. The palette feeds
cover and body renderers, then `merge.py` combines them; this shared configuration
does not guarantee output consistency without inspection. Form filling bypasses
the cover/body browser pipeline.

MIT license and upstream attribution remain in [LICENSE](LICENSE) and
[UPSTREAM.md](UPSTREAM.md).
