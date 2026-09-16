---
name: workflow-setup
description: Set up and manage durable workflows and automations for reusable, recurring, or event-driven work.
---

# Workflow Setup

Use this skill first for workflow creation or management and for recurring or event-driven intent such as “every morning,” “when an email arrives,” “monitor,” “remind me,” or “keep this in sync.”

## Product Model

- A **workflow** is the reusable definition: name, description, instructions, optional supplementary files, and owning agent. It does not run automatically by itself.
- An **automation** is one trigger attached to one workflow. A workflow can have zero or more automations.
- Enabled recurring and event automations persist beyond this conversation and can start future runs until disabled or removed. A `once` automation fires at one scheduled time.
- Editing what happens means editing the workflow. Editing when or why it starts means managing an automation.

## Route

| Intent                                                         | Command                                              | Read first                                                               |
| -------------------------------------------------------------- | ---------------------------------------------------- | ------------------------------------------------------------------------ |
| Create, save, edit, inspect, copy, or delete a workflow        | The matching `okou workflow` leaf command            | [workflow management](references/workflow-management.md)                 |
| Run a workflow now                                             | `okou workflow view`, then the task's tools          | [workflow management](references/workflow-management.md)                 |
| Add, inspect, update, enable, disable, or remove an automation | The matching `okou workflow automation` leaf command | [automation management](references/automation-management.md)             |
| Choose or configure a schedule/event kind                      | The `add` or `update` automation leaf command        | [trigger setup](references/trigger-setup.md) after automation management |

Use the canonical `automation` commands, not the legacy `trigger` alias. Do not use `/loop`, `CronCreate`, `CronList`, `CronDelete`, or `ScheduleWakeup`. Read the relevant leaf help directly when exact flags matter and reuse help already read for the same CLI version.

## Persistence and Authorization

Persist reusable definitions with `okou workflow create|edit`. Their `SKILL.md` is synthesized from name, description, and instruction. `--dir` uploads supplementary files only and must not contain `SKILL.md`. Creating or editing folders under `~/.codex/skills` or `~/.claude/skills` changes only the current runtime; it does not persist or sync to Okou.

Treat the user's current request as authorization for exactly the workflow and automation mutations it explicitly asks for; do not ask for redundant confirmation. Ask when the target or scope is ambiguous, or when execution would add external, destructive, or paid side effects the user did not authorize. Merely reading this skill, explaining options, or validating documentation never authorizes a live mutation.

After a mutation, verify the workflow or automation through the corresponding view/list/show command. Report the outcome in product language and, for a newly created automation, report the friendly model its automation thread will use.
