---
name: gen
description: Generate media and authored web artifacts with Okou, or route connector-backed generation.
---

# Gen

Route generation requests to the narrowest current Okou command and load only the execution reference that task needs.

## Template Precedence

An attached generation template takes precedence. Follow its exact commands and resources; do not run `okou generate -h` or list providers unless the template explicitly names type-specific help as a fallback. For any video submission, still honor the applicable preview approval in [video preview](references/video-preview.md).

## Route

| Request                                                                                     | Command                      | Read before execution                                                                       |
| ------------------------------------------------------------------------------------------- | ---------------------------- | ------------------------------------------------------------------------------------------- |
| Image or image edit                                                                         | `okou generate image`        | [direct media](references/direct-media.md)                                                  |
| Generated video                                                                             | `okou generate video`        | [direct media](references/direct-media.md) and [video preview](references/video-preview.md) |
| Talking avatar                                                                              | `okou generate avatar-video` | [direct media](references/direct-media.md)                                                  |
| Speech audio                                                                                | `okou generate voice`        | [direct media](references/direct-media.md)                                                  |
| Presentation, website, report, docs design, poster, dashboard, mobile-app design, or sprite | `okou generate <type>`       | [authored artifacts](references/authored-artifacts.md)                                      |
| Connector-backed text, code, document, or music                                             | `okou generate <type>`       | [connector generation](references/connector-generation.md)                                  |

There is no generic `audio` type: use `voice` for speech or `music` for connector-backed music. If no listed type fits, run `okou generate -h` once and do not claim unsupported capability.

## Command Discipline

- When the type is known, read `okou generate <type> --help` directly before execution and reuse help already read for the same CLI version and context. Do not unconditionally chain root, group, and leaf help.
- Run `okou generate <type>` without generation input only when provider or registry discovery is needed. If the user named a provider, request its guidance directly with `--provider <name>` when that type supports providers.
- Exact flags, models, styles, templates, providers, limits, and result fields come from current CLI help, not examples remembered from this skill.

## Completion Invariants

After submitting a generation command, wait for that same command or durable job to finish and use what it returns. Do not abandon it, switch approaches, or submit another billed job merely because it is slow. A repeat can create and charge for a second result.

A returned authoring or connector-guidance packet is not a finished artifact. Follow the selected reference until the deliverable exists. A direct-media result is a finished server-side artifact; deliver its returned URL and metadata. If generation fails for insufficient credits, run `okou doctor credit` and follow its result rather than assuming a purchase is available.
