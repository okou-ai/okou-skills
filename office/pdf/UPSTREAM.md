# Upstream attribution

This skill is redistributed from [MiniMax-AI/skills](https://github.com/MiniMax-AI/skills),
created by MiniMax and its contributors.

- Source: [`skills/minimax-pdf`](https://github.com/MiniMax-AI/skills/tree/60aaae52bb2af8162732751a4332f62a5fef518b/skills/minimax-pdf)
- Revision: `60aaae52bb2af8162732751a4332f62a5fef518b`
- License: [MIT](LICENSE), copied from [the upstream license](https://github.com/MiniMax-AI/skills/blob/60aaae52bb2af8162732751a4332f62a5fef518b/LICENSE) with its original copyright notice.

The initial import preserves every upstream file byte-for-byte. This attribution
file and, where absent upstream, a local copy of the repository's MIT license
are distribution additions. Later Okou adaptations are recorded in this
repository's Git history; the pinned upstream revision remains the baseline.

## Okou adaptations

- Distributed as `office/pdf`, with skill names and internal references updated.
- Dependency checks launch Chromium; setup uses supported install arguments and
  reports failures. Rendering does not silently install dependencies.
- Regression coverage checks missing Chromium and the full PDF pipeline.

Report issues specific to the Okou distribution in
[okou-ai/okou-skills](https://github.com/okou-ai/okou-skills/issues). When an issue
also reproduces on the pinned upstream version, include that reproduction when
reporting or contributing a fix to MiniMax-AI/skills.
