# Connector-Backed Generation

Use this reference for connector-only `text`, `code`, `document`, and `music` requests, and when a user chooses a connector for a media type.

## Discover and Route

Read `okou generate <type> --help` directly. Current connector-only types have no built-in platform pipeline; do not imply that selecting the type itself creates an artifact.

- If the provider is unknown, run `okou generate <type>` without generation input to list available choices. Add `--all` only when unavailable or not-yet-authorized providers matter.
- If the user named a provider, run `okou generate <type> --provider <name>` directly when supported.
- Treat the output as skill-invocation guidance, not as the finished result. Read and follow the selected connector skill, including its provider-specific input mode.

Use `voice` for built-in or connector-backed speech and `music` for connector-backed music; do not invent a generic `audio` command.

## Execute and Deliver

Preserve the user's requested provider, account context, inputs, format, and output destination. Do not substitute a built-in provider or another connector after a failure without the user's direction. If the provider operation submits a job, wait for that same job and use its returned artifact rather than starting over because it is slow.

Connector discovery, account selection, authentication, and Okou permission recovery are owned by `okou connector --help` and its child help. Follow that shared guidance exactly; do not copy provider OAuth scopes into Okou permission requests or broaden connector access from this skill.

Return the actual connector result or artifact URL. If the connector only produced instructions, a plan, or an authoring packet, continue through that packet before claiming completion.
