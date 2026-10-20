# Upstream attribution

This skill is redistributed from [MiniMax-AI/skills](https://github.com/MiniMax-AI/skills),
created by MiniMax and its contributors.

- Source: [`skills/minimax-docx`](https://github.com/MiniMax-AI/skills/tree/60aaae52bb2af8162732751a4332f62a5fef518b/skills/minimax-docx)
- Revision: `60aaae52bb2af8162732751a4332f62a5fef518b`
- License: [MIT](LICENSE), copied from [the upstream license](https://github.com/MiniMax-AI/skills/blob/60aaae52bb2af8162732751a4332f62a5fef518b/skills/minimax-docx/LICENSE) with its original copyright notice.

The initial import preserves every upstream file byte-for-byte. This attribution
file and, where absent upstream, a local copy of the repository's MIT license
are distribution additions. Later Okou adaptations are recorded in this
repository's Git history; the pinned upstream revision remains the baseline.

## Okou adaptations

- Distributed as `office/docx`; public skill and .NET project names are `docx`
  and `Docx`, with internal paths and references updated.
- Setup targets the explicit .NET 8 project, and validation uses the OpenXML SDK
  without imposing a different document style. Local XSD imports are bundled.
- Writer readiness is checked through real DOCX-to-PDF conversion. The CLI
  examples and structural/visual validation instructions match the shipped tools.
- Regression coverage exercises creation, invalid packages, template checks,
  11 pt styles, schema failures, and rendering.

Report issues specific to the Okou distribution in
[okou-ai/okou-skills](https://github.com/okou-ai/okou-skills/issues). When an issue
also reproduces on the pinned upstream version, include that reproduction when
reporting or contributing a fix to MiniMax-AI/skills.
