> This release re-cuts the twelve identity compositions to the official Okou brand: the wordmark uses the Okou logotype outlines (`assets/okou-motion.otf`), the mark uses the official Okou icon contour, and the palette is #242121 / #FAF5F3 / #F8A101. References to Astri below describe the earlier reviewed preset these compositions were refined under.

# Notice

This directory contains project-authored branding-motion work and modified portions of HyperFrames source code.

## Upstream original code

The following upstream code originated in `heygen-com/hyperframes` at commit [`dd0626a55a0d0f24cae1b00bd2c95c0ebfa7a573`](https://github.com/heygen-com/hyperframes/tree/dd0626a55a0d0f24cae1b00bd2c95c0ebfa7a573):

- `registry/components/particle-image-reveal/particle-image-reveal.html`
- `registry/components/svg-stroke-trace/svg-stroke-trace.html`
- `registry/components/logo-sting/logo-sting.html`
- `registry/components/logo-brand-close/logo-brand-close.html`
- `registry/components/titlecard-lockup/titlecard-lockup.html`
- `registry/components/ink-bleed-reveal/ink-bleed-reveal.html`
- `registry/components/slit-scan-reveal/slit-scan-reveal.html`
- `registry/components/svg-mask-reveal/svg-mask-reveal.html`
- `registry/components/facet-morph/facet-morph.html`
- `registry/components/wordmark-tiles/wordmark-tiles.html`
- `registry/components/morph-swap/morph-swap.html`
- `registry/blocks/code-particle-assemble/code-particle-assemble.html`

Upstream copyright notice:

> Copyright 2026 HeyGen, Inc.

The upstream files are licensed under Apache License 2.0. The complete, unmodified license text from the fixed commit is distributed at [`LICENSES/HyperFrames-Apache-2.0.txt`](./HyperFrames-LICENSE.txt). Nothing in this notice changes that license.

## Project modifications

The ten reusable Registry-derived identity components are modified files, not verbatim upstream copies. The project changes include new composition/timeline identities and host wrappers; a reusable variable surface; a bare six-arm mark with no logo background rectangle; individually colored wordmark letters; project-controlled backgrounds; optional supporting-copy controls that default to empty; no-exit terminal holds; local/system typography; and timing/determinism adjustments needed by the HyperFrames host contract. `SOURCES.md` records the change set for each component.

`artifact-flow-story` is project-authored code that adapts the shared-center, transform-only handoff described by `morph-swap` plus four pinned animation Rules. It adds three configured capability stories and does not ship the installed upstream `morph-swap` file as a separate component.

`astri-particle-lockup` is a substantial, Astri-specific modification of `code-particle-assemble`: code tokens are replaced by sampled brand geometry, asynchronous font-ready timeline construction is removed, particle settling is tightened, and the effect hands off to a sharp static lockup. It is documented as a reference composition, not as a reusable template.

`parts-assemble-lockup` is project-authored code. It is inspired by the upstream `logo-assemble-lockup` Blueprint and four upstream Rules, but it does not copy Registry HTML. Its provenance is still recorded so the design lineage is auditable.

The copyright and licensing status of project-authored additions is separate from the upstream copyright stated above. This notice does not claim that HeyGen authored or endorsed the project modifications.

## Material not included

This directory does not copy:

- the Figma mark, `figma.com` copy, or Figma marketing language present in the upstream `logo-outro` example;
- Registry preview MP4 files or poster images;
- Google Fonts stylesheets or other remote font files.

Any GSAP or Three.js script reference retained by an adapted composition is an external runtime dependency, not vendored HyperFrames code. Those dependencies are not relicensed by the HyperFrames Apache-2.0 license or by this notice.

## Trademarks

Apache-2.0 does not grant permission to use trade names, trademarks, service marks, or product names except for reasonable and customary source attribution as described by the license. References to HyperFrames, HeyGen, Figma, and Astri identify source material or the demonstration brand only; they do not grant trademark or brand-use rights, imply endorsement, or authorize reuse of a logo. A downstream user must supply and clear the rights for any replacement brand.

## 2026-09-14 visual refinement

The twelve compositions in this directory refine all twelve identity examples from the recovered Astri library. Changes include the official Okou logotype and icon, two restrained colourways, shared optical geometry, revised entry timing, a continuous wordmark reveal, particles sampled from the real glyphs, and an original/refined comparison player. The Okou logotype face in assets/okou-motion.otf is built from the official Okou brand assets. The recovered originals remain unchanged under ../brand-original/.
