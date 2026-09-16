# Automation Management

Use this reference when a workflow should run on a schedule or event, or when the user wants to inspect, change, pause, resume, or remove an automatic run path.

## Prepare

1. Resolve the workflow. If none exists and the reusable job is clear, create and verify the workflow first.
2. Read [trigger setup](trigger-setup.md), select the exact automation kind, and collect only that kind's missing fields.
3. List existing automations before adding one. If a materially equivalent automation exists and the user's intent does not resolve whether to replace or duplicate it, ask whether to update, keep both, or disable the old one.
4. Determine enabled versus paused from the request. Recurring or event-driven wording normally authorizes an enabled automation; an explicit draft or paused request does not.

Do not inspect connector authorization during the default setup path. If creation reports a connector or permission failure, stop that blocked action and follow the shared `okou connector --help` diagnosis or permission flow. Do not broaden connector access preemptively.

## Add or Update

Use the exact kind and flags from current help:

```bash
okou workflow automation add <workflow> <kind> <kind-options>
okou workflow automation update <automation-id> <replacement-options>
```

`update` replaces the supported schedule or event-filter configuration without changing the workflow instructions. Some kinds cannot update their binding fields; [trigger setup](trigger-setup.md) identifies those cases. Create a replacement before removing or disabling the old automation, and change the old one only when the user's request authorizes it.

An enabled cron, loop, or event automation keeps running beyond the current conversation until disabled or removed. A `once` automation has one fire time. Explain broad scope plainly before creation when it was not already explicit, such as an inbound-email rule with no filters.

If the user requests a paused setup and `add` creates it enabled, disable the new automation immediately after creation and verify both steps.

## Inspect, Pause, Resume, or Remove

```bash
okou workflow automation list <workflow>
okou workflow automation show <automation-id>
okou workflow automation disable <automation-id>
okou workflow automation enable <automation-id>
okou workflow automation remove <automation-id>
```

Disable preserves settings; remove deletes that one automatic path. Perform only the operation and target explicitly requested. For run-history questions, use `show` for available last/next-run summary. Use separate run/log search tooling only when the user needs fuller history and a known run or workflow context is available.

## Verify Model and Lifecycle

After add, update, enable, disable, or remove, verify with `automation list` and, when the automation still exists, `automation show`. Preserve webhook creation output because its signing secret is shown only once, but do not expose secrets in an ordinary response.

A new automation runs in its automation thread's current model; the model is not independently pinned on the automation. Read the friendly model from the creation result. If absent, inspect the automation or its chat thread before responding. Proactively tell the user which friendly model it will use, and include the model ID only when requested.

Report the workflow name, trigger behavior, enabled or paused state, authorized safety boundary, and natural next step in plain language. Keep IDs, cron expressions, configs, and raw checks internal unless requested.
