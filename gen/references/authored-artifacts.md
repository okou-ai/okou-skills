# Authored Artifact Generation

Use this reference for `presentation`, `website`, `report`, `docs-design`, `poster`, `dashboard-design`, `mobile-app-design`, and `sprite` when no attached generation template already owns execution.

## Select Sources

Read `okou generate <type> --help` directly and use the current type name, inputs, template/design registry, and output contract. Run the type command without a prompt only when source, template, or design-system discovery is needed. Preserve the user's audience, content, brand, source material, format, and delivery target.

Do not assume these commands generate a complete file. They return a source-selection or authoring packet for the current agent. A packet can select resources, templates, and instructions, but it is not the requested artifact.

## Author and Verify

1. Run the selected `okou generate <type>` command and preserve its complete packet.
2. Follow that packet to author the actual artifact in the workspace. Use every required resource and obey any packet-specific validation or rendering instructions.
3. Inspect the finished artifact with the relevant local checks. Do not present a packet, source directory, or localhost URL as the deliverable.
4. Publish static output with the packet's current `okou host` instructions. Presentations require the presentation artifact kind when current host help or the packet specifies it.
5. Return the hosted URL and summarize material choices such as template, design system, title, slide count, or site slug.

A local file path is implementation state, not a user-accessible result. If the user needs the source bundle as well as the hosted view, deliver it separately only when that serves a distinct need.

For revisions, reuse the existing authored files and accepted choices. Reopen generation help or source discovery only when the requested change affects them or the original packet is unavailable.
