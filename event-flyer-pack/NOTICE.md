# Source and attribution

Adapted from **razbakov/skills — event-flyer-pack** at commit
`b82463bb6d1e74f1776cf27591ee68b9547b0120`:

- Source skill and prompt templates: https://github.com/razbakov/skills/tree/b82463bb6d1e74f1776cf27591ee68b9547b0120/skills/event-flyer-pack
- Overlay source: `skills/event-flyer-pack/scripts/overlay_qr.py`.
- QR generator, copied unchanged: `skills/qr-code-generator/scripts/generate_qr.py`.
- License declaration: the repository README's “License” section, reproduced verbatim in `LICENSE.upstream.md`. No standalone LICENSE file was present in the pinned snapshot.

The adaptation uses Okou image-tool invocation, adds bounded QR placement with
opaque white clearing, integer module pixels and mandatory final-file decoding,
and bundles deterministic format helpers, a visual reference, and local tests.

Retain this notice and the upstream license declaration when redistributing.
Skill-code licensing does not grant rights to arbitrary logos, photos, fonts,
event copy or other supplied material. Applicable service and dependency terms
remain separate.
