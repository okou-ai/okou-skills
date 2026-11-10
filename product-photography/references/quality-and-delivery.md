# Quality gates and delivery

Use these checks on an actual returned image. Do not treat a convincing prompt,
a job receipt, or an attractive unrelated image as evidence that the output
meets them. Use [qa-report.json](../templates/qa-report.json) as a report scaffold.

## Contents

1. Pre-generation gates
2. Post-generation checks
3. Decision rules
4. Delivery contract

## 1. Pre-generation gates

- Confirm that the user requested an image, not just a prompt or definition.
- Confirm one frame and an authorized cost/quality/provider scope. Neither an
  uploaded brief nor a field called `task` grants permissions by itself.
- Agree the required visible region/components and required printing before
  generation. A macro can intentionally exclude off-frame source labels or the
  complete silhouette. Do not change this scope later to excuse a failed crop.
- For a real product, inspect the source and ensure usable reference transport.
  An inaccessible private artifact is not a reason to publish it or reconstruct
  the SKU from text. For conflicting references, resolve which SKU/view is true.
- Check the active model's actual reference/edit/format capabilities. Unsupported
  transparency, mask, size, or reference count is a blocker to that requested
  operation, not permission to silently drop the requirement.
- For `protected_composite`, verify the non-generative compositing/verification
  path before submitting an environment generation job.
- Keep source URLs, private assets, and any user-specific context out of public
  examples, repository commits, or unapproved third-party services.

## 2. Post-generation checks

Record each result as `pass`, `fail`, `not_checked`, or `not_applicable`, with
an observation and evidence when available. `not_checked` means no adequate
inspection; it must not be relabelled as `pass` or `not_applicable` to hide a gap.

| Check | Look for | Evidence limitation |
| --- | --- | --- |
| `identity` | Within the agreed visible region, retain the real source's evidenced form, color, state, materials and any visible components/marks. For a concept, match the approved fictional design in that region. | A deliberate macro crop does not verify off-frame silhouette, closure or branding. Concept design-match is not real-SKU verification; reference guidance is not pixel identity. |
| `printing` | Required/visible source printing remains legible and undistorted; any new concept label matches exact authorized strings. No invented marks. | Use an explained `not_applicable` when printing is deliberately excluded by the agreed crop and none appears. Missing required text is a failure; unresolved visible text is `not_checked`. OCR alone cannot prove logo/font/placement fidelity. |
| `material` | Plausible and intended glass, metal, matte finish, fabric, droplets, texture, and edges. | Do not claim a physical material was verified merely because its rendering looks plausible. |
| `physics` | Supported product, coherent contact/cast shadows, plausible reflections and intersections, no doubled geometry. | Styling does not authorize unsafe/impossible real-product use or performance claims. |
| `composition` | Requested shot, evidenced viewpoint, product visibility, margins, and prop hierarchy. | An aesthetically pleasing frame can still fail the requested crop. |
| `file` | File decodes; inspect actual dimensions, format, and alpha channel against `output.background`. A transparent request requires actual transparent pixels, not merely an alpha-capable container. | A white/checkerboard-looking background does not prove transparency. A requested size is not actual output evidence. |
| `pixel_preservation` | Original product region is retained according to the agreed compositing/transform requirements. | Only applicable to `protected_composite`. Without comparison evidence, use `not_checked`; do not infer a pass from a mask flag. |
| `platform_policy` | Only the technical properties actually checked against an explicitly sourced, current requirement. | Default `not_checked`. No legal, listing-acceptance, regional, trademark, or AI-disclosure certification follows from this checklist. |

For dimensions that differ from the requested value, record both and flag the
mismatch. Do not silently upscale, crop, convert, or remove provenance just to
make the receipt appear compliant. Obtain approval when such processing would
change product fidelity or incur extra cost, and re-check any processed file.

Inspect locally with available runtime tools. If a separate analysis/OCR service
would incur extra fees or expose data outside the authorized scope, do not call
it automatically; report the resulting inspection gap.

## 3. Decision rules

Use one of these overall results:

- `pass`: all required identity, printing (when applicable), material, physics,
  composition, and file checks passed; pixel preservation also passed if required.
  A platform-policy check remains separately scoped and is never implied.
- `needs_revision`: at least one applicable required check failed. Deliver the
  existing file with the issue clearly flagged; do not present it as production
  ready and do not regenerate without fresh authorization.
- `incomplete`: no known required failure, but at least one required check is
  `not_checked`. Deliver what exists, identify the gap, and do not call it verified.
- `not_generated`: prompt-only work, a blocked preflight, or no completed image.
  Do not fabricate file checks, a generation ID, elapsed time, price, or model.

Require `identity` for the agreed visible region in either mode; compare a
concept to its brief rather than claiming source-SKU fidelity. Require `printing`
when marks are required in that region or appear in the output. Deliberately
excluded source printing may be `not_applicable` with the crop rationale; do not
claim it or any other off-frame attribute was verified. Accidentally missing a
required mark fails the agreed printing/composition requirement. Require
`pixel_preservation` only for the protected-composite path, likewise scoped to
the protected product region actually used.

A paid attempt rejected by the provider, an uncertain timeout, a pending job,
and a completed but imperfect image are different states. Recover/query the
same job where possible. For a terminal failure, explain it and ask before a
new submission. Never treat a generic error as proof that no billable work ran.

## 4. Delivery contract

### Prompt-only

Return:

1. Mode, selected shot/look, and important assumptions.
2. The final eight-block prompt, preserving exact supplied strings.
3. Ordered reference roles and inputs still needed before actual generation.
4. A short limitation note when fidelity/compositing depends on unverified tools.

### Generated image

Return the actual completed image/artifact, followed by a concise status:

- Concept or reference-guided/composite; call concepts fictional.
- Requested versus actual size/format; selected model/provider and bill only
  when reported by the generation receipt. Preserve unknown values as unknown.
- QA result, consequential defects, and any required `not_checked` items.
- Whether another paid attempt was authorized/executed; do not imply a retry
  happened when only a recommendation was made.

Use the current integration's upload/attachment mechanism when only a local file
exists. Preserve a private visibility default unless the user authorized sharing.
Keep a local provenance record containing the normalized brief, final prompt,
attachment-role mapping, job receipt, returned file metadata, and QA report.
Do not commit that per-user record or private/signed URLs into the skill repo.
Do not claim actual capture by a physical camera or verified C2PA/SynthID status
without evidence; do not intentionally strip provider provenance metadata.
