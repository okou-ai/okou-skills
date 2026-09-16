# Trigger Setup

Read this after [automation management](automation-management.md). It maps user intent to current `okou workflow automation` kinds and records requirements that are easy to miss. Use `okou workflow automation add --help` and `update --help` for the live flag surface; do not invent a kind or carry forward a retired alias.

## Contents

- [Schedules](#schedules)
- [Chat run finished](#chat-run-finished)
- [Gmail](#gmail)
- [Webhook](#webhook)
- [GitHub](#github)
- [Google Calendar](#google-calendar)
- [Google Forms](#google-forms)
- [Google Meet](#google-meet)
- [Notion](#notion)

## Schedules

### Fixed schedule: `cron`

Collect cadence, wall-clock time, timezone, and business-day assumptions. Convert natural language to cron yourself. If timezone is known from context, use it; otherwise ask when timing matters.

```bash
okou workflow automation add <workflow> cron --expr "0 9 * * *" -z Asia/Shanghai
okou workflow automation update <automation-id> --expr "0 9 * * *" -z Asia/Shanghai
```

### One future run: `once`

Collect the exact date, time, and timezone. Resolve relative wording such as “tomorrow” to a concrete date in the confirmation.

```bash
okou workflow automation add <workflow> once --at "2026-06-10T09:00" -z Asia/Shanghai
okou workflow automation update <automation-id> --at "2026-06-10T09:00" -z Asia/Shanghai
```

### Fixed interval: `loop`

Convert natural language to a supported duration such as `15m`, `1h`, or `90s`.

```bash
okou workflow automation add <workflow> loop --every 15m
okou workflow automation update <automation-id> --every 10m
```

## Chat Run Finished

Kind: `chat-run-finished`.

Collect the user-owned watched web-chat thread, optional terminal statuses, and optional final-output pattern. It watches future runs in that thread, not one run ID. A match starts a new run in the workflow's automation thread; it does not resume the watched run. The enabled automation remains active for later matching completions.

Omit `--run-status` to match all terminal statuses. Supported statuses are `completed`, `failed`, and `cancelled`. `--output-pattern` uses a case-insensitive `*` wildcard against final assistant text; a run without final assistant text cannot match a pattern.

```bash
okou workflow automation add <workflow> chat-run-finished --chat-thread-id <thread-id>
okou workflow automation add <workflow> chat-run-finished --chat-thread-id <thread-id> --run-status completed,failed --output-pattern "*deploy failed*"
```

Current update help does not replace the watched thread, statuses, or output pattern. To change them, add a replacement and remove or disable the old automation only when authorized.

## Gmail

### New message: `gmail-new-message`

Collect only the inbound matching needed: sender, recipient, cc, subject, or body. A rule with no text filters matches all inbound messages, so use it only when the user explicitly requested that scope.

Simple filters use flags such as:

```bash
okou workflow automation add <workflow> gmail-new-message --from-contains "@example.com"
okou workflow automation add <workflow> gmail-new-message --subject-contains "invoice"
```

For complex matching, pass a JSON object through `--config`. It has a top-level `match` object; current fields are `from`, `subject`, `body`, `to`, and `cc`, with `contains`, `containsAny`, `doesNotContain`, and `doesNotContainAny` matchers.

### Label applied: `gmail-label-applied`

Collect the exact label, workflow behavior, allowed side effects, and whether a missing label may be created. Check that the Gmail label exists before adding the automation. Create a missing label only when the request authorizes it.

```bash
okou workflow automation add <workflow> gmail-label-applied --label "Support"
okou workflow automation update <automation-id> --label "Support"
```

## Webhook

Kind: `webhook`.

Ask what will call it, the expected payload, and whether the caller can store and sign with the secret.

```bash
okou workflow automation add <workflow> webhook
```

Preserve creation output because the signing secret is printed only once. Share the webhook URL in the normal response; reveal signing details only when the implementer asks and the destination is appropriate. To replace webhook binding material, create a replacement rather than inventing update flags.

## GitHub

Current kinds include:

- `github-pull-request`
- `github-workflow-run-completed`
- `github-workflow-job-completed`
- `github-pull-request-review-submitted`
- `github-deployment-status-created`
- `github-issue-comment-created`

Collect the repository first, then only the event-specific filters shown by current add help. Examples:

```bash
okou workflow automation add <workflow> github-pull-request --repository vm0-ai/okou --action closed --merged yes --base-branch main
okou workflow automation add <workflow> github-pull-request --repository vm0-ai/okou --action labeled --label triage
okou workflow automation add <workflow> github-workflow-run-completed --repository vm0-ai/okou --workflow Turbo --conclusion failure,timed_out --branch main
```

Use the workflow/job, review-state, deployment, or comment filters from current help for the other kinds. Omitted filters broaden the match, so state that scope before creation when the request did not already establish it. GitHub automations require the workspace GitHub App installation; on an authorization failure use connector diagnosis rather than guessing.

The `github-label-applied` kind is not exposed by current help. For pull-request label events use `github-pull-request --action labeled --label <name>`. Do not claim an issue-label trigger that the current CLI does not expose.

## Google Calendar

Kinds: `google-calendar-event-created`, `google-calendar-event-updated`, and `google-calendar-event-cancelled`.

Collect the calendar. Default to `primary` only when the user's wording clearly means their main calendar.

```bash
okou workflow automation add <workflow> google-calendar-event-created --calendar-id primary
okou workflow automation add <workflow> google-calendar-event-updated --calendar-id primary
okou workflow automation add <workflow> google-calendar-event-cancelled --calendar-id primary
```

Current update help does not change the calendar binding. Create a replacement and remove or disable the old automation only when authorized.

## Google Forms

Kind: `google-forms-response-submitted`.

Ask: “Please open the form's edit page and copy the link from the address bar.”

```bash
okou workflow automation add <workflow> google-forms-response-submitted --form-url "https://docs.google.com/forms/d/<form-id>/edit"
```

Current update help does not change the form binding; use an authorized replacement.

## Google Meet

Kind: `google-meet-transcript-generated`.

```bash
okou workflow automation add <workflow> google-meet-transcript-generated
```

It runs when a meeting organized by the connected user generates a transcript. Do not promise coverage for meetings they do not organize.

## Notion

Kinds and binding inputs:

- `notion-child-page-created` with `--parent-page-url`
- `notion-database-item-created` with `--database-url`
- `notion-page-content-updated` with either `--page-url` or `--database-url`

```bash
okou workflow automation add <workflow> notion-child-page-created --parent-page-url "<notion-page-url>"
okou workflow automation add <workflow> notion-database-item-created --database-url "<notion-database-url>"
okou workflow automation add <workflow> notion-page-content-updated --page-url "<notion-page-url>"
```

Use exactly one supported binding for the chosen kind. Current update help does not replace these bindings; create a replacement and alter the old automation only when authorized.
