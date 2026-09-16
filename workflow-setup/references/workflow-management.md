# Workflow Management

Use this reference when the user wants to create, save, inspect, edit, copy, delete, or manually execute a workflow definition.

## Conversation Contract

Speak in product terms and hide IDs, raw commands, JSON, and verification output unless the user asks for technical or audit detail. Ask only for information needed for the next action. An explicit, resolved request authorizes that requested workflow mutation; ask again only when the target is ambiguous or the change broadens side effects.

## Create or Save

Collect the workflow's job, inputs, deliverable, allowed side effects, and any approval or safety limits. A schedule or connector is not required to save a clear reusable definition.

```bash
okou workflow create <name> --agent <agent-id> --display-name "<display name>" --description "<description>" --instruction "<instructions>"
```

Use `--instruction-file <path>` for longer instructions. Use `--dir <path>` only for supplementary files; it must not contain `SKILL.md`, because Okou synthesizes that file from the workflow metadata and instruction. A workflow created or edited through the CLI is durable. A folder edited only under `~/.codex/skills` or `~/.claude/skills` is runtime-only and does not update the stored workflow.

When saving a completed conversation, turn the actual successful steps into reusable instructions. Confirm the proposed name or behavior only when the request leaves them unclear; do not add an automation unless the user requested automatic execution.

For a built-in template whose job is clear, save and verify the workflow draft first. Do not preflight connectors. Leave it without an automation until the user's request establishes the trigger and any safety-sensitive external actions. When external, destructive, or paid behavior is not authorized, keep the definition in draft/recommend-only mode with an approval gate. An uploaded workflow with an unclear job needs one focused clarification before creation.

## Inspect or Edit

Resolve names under the current agent when possible; if a name is ambiguous, ask the user to choose by friendly name and description.

```bash
okou workflow list
okou workflow list --agent <agent-id>
okou workflow view <workflow>
okou workflow edit <workflow> --instruction-file ./instruction.md
okou workflow edit <workflow> --display-name "<name>" --description "<description>"
```

Use `workflow edit` for changes to what the workflow does. Use automation commands for schedules and event filters; do not imply that editing one changed the other.

## Copy or Delete

Copy only when the user asks to reuse or fork the definition onto another agent:

```bash
okou workflow copy <workflow> --agent <source-agent-id> --to-agent <target-agent-id>
```

Delete only the resolved workflow the user explicitly asked to delete. In non-interactive execution, `-y` acknowledges the CLI prompt; it does not replace user authorization.

```bash
okou workflow delete <workflow> --agent <agent-id> -y
```

Deleting a workflow removes its reusable definition and attached automations. To remove only one automatic path, use automation removal instead.

## Run Now

The current CLI has no `okou workflow run` subcommand. Do not invent it and do not create a persistent or `once` automation merely to simulate a manual run. Resolve and inspect the workflow with `workflow view`, then execute its instructions in the current task using the relevant tools and the user's current authorization. Create a `once` automation only when the user actually asks for future scheduled execution.

## Verify and Report

After create or edit, run:

```bash
okou workflow view <workflow>
```

After copy, inspect the new workflow on the target agent. After deletion, list the relevant agent's workflows when absence must be verified. Keep raw verification internal by default, and tell the user what was saved or changed plus the natural next action.
