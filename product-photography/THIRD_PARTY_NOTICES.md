# Third-party notices and modifications

This product-photography package is an Okou adaptation, not an unmodified import
or an installation of either upstream product. Distribute the package and its
modifications under [Apache-2.0](LICENSE), retaining the third-party terms below.
These notices do not imply endorsement or grant trademark rights.

## SuperCMO

- Source: [SupercmoHQ/superCMO-skills](https://github.com/SupercmoHQ/superCMO-skills/tree/3bf78a423b1ba27a1f500b3b50f806b86cc5bdab).
- Pinned commit: `3bf78a423b1ba27a1f500b3b50f806b86cc5bdab`.
- Material consulted/adapted: `skills/generating-product-photos/SKILL.md`,
  `references/mode-hero.md`, and `references/photographic-craft.md` within that skill.
- Original attribution: **SuperCMO Skills — Copyright (c) 2026 Kshitiz Kumar**.
- License: Apache License 2.0, bundled as [LICENSE](LICENSE).
- Original upstream notice retained verbatim in
  [licenses/SuperCMO-NOTICE.txt](licenses/SuperCMO-NOTICE.txt).
  Its font section describes upstream assets; no fonts, media client, or
  captioning code are redistributed in this package.

## buluslan

- Source: [buluslan/gpt-image2-ecommerce](https://github.com/buluslan/gpt-image2-ecommerce/tree/73abd50bf2b689b5a453f28ddd7b0016415deec6).
- Pinned commit: `73abd50bf2b689b5a453f28ddd7b0016415deec6`.
- Material consulted/adapted: `SKILL.md`, `references/craft.md`,
  `references/scenarios/luxury-atmospherics.json`, and the prompt-export behavior
  of `scripts/imagegen.sh`.
- Original attribution: **Copyright (c) 2026 Buluu@新西楼**.
- License: MIT; original copyright and full terms are retained in
  [licenses/buluslan-MIT.txt](licenses/buluslan-MIT.txt).

## Prominent modification notice

`SKILL.md`, `references/shots-and-craft.md`, and
`references/prompt-framework.md` materially rewrite the consulted instructions:

- Combine purpose-based shot selection with independently selected visual looks.
- Introduce an explicit fictional concept mode and a reference-image identity path.
- Replace the upstream prompt layouts with a new eight-block prompt framework.
- Replace provider/model routing, secret configuration, and upstream execution
  scripts with the active Okou runtime and its user's built-in model setting.
- Replace automatic retries/model fallback and any no-inspection rule with one
  authorized submission, same-job recovery, evidence-based QA, and explicit
  authorization for additional paid attempts.
- Omit category-style bans, promotional introductions, unsupported legal/platform
  compliance assertions, on-model workflows, batch/campaign generation, and
  policy-refusal workarounds.

The schema, examples, QA contract, acceptance cases, and offline tests are new
package-specific work. No upstream executable code or model SDK is shipped.
Do not auto-fetch a newer upstream version at runtime; review a deliberate update
and its licensing before changing these pinned sources. These licenses cover
the referenced source material, not rights to user product assets, brand marks,
or outputs produced under a separate model/provider's terms.
