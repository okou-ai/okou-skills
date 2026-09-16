# Trigger Setup

## Contents

- [Requirement mapping](#requirement-mapping)
- [Fixed schedule](#fixed-schedule)
- [One-time scheduled run](#one-time-scheduled-run)
- [Fixed interval](#fixed-interval)
- [Chat run finished](#chat-run-finished)
- [New email](#new-email)
- [Email label](#email-label)
- [Web trigger](#web-trigger)
- [GitHub label](#github-label)
- [Google Calendar event created](#google-calendar-event-created)
- [Google Forms response submitted](#google-forms-response-submitted)

## Requirement Mapping

Map friendly trigger choices to CLI kinds:

- Fixed schedule -> `cron`
- One-time scheduled run -> `once`
- Fixed interval -> `loop`
- Chat run completion -> `chat-run-finished`
- Web trigger -> `webhook`
- New email -> `gmail-new-message`
- Email label -> `gmail-label-applied`
- GitHub label -> `github-label-applied`
- New Google Calendar event -> `google-calendar-event-created`
- New Google Forms response -> `google-forms-response-submitted`

## Fixed Schedule

Ask for cadence, wall-clock time, timezone, and business-day assumptions. Convert
the answer to a cron expression yourself. If the user says "daily" and their
timezone is known from context, use it. If timezone is missing and timing matters,
ask.

Command shape:

```bash
okou workflow trigger add <workflow> cron --expr "0 9 * * *" -z Asia/Shanghai
okou workflow trigger update <trigger-id> --expr "0 9 * * *" -z Asia/Shanghai
```

## One-Time Scheduled Run

Use this when the user wants it to run once at a future time, not recur.

Ask for the exact date, time, and timezone. If the user uses relative wording
such as "tomorrow", resolve it to a concrete date in the final confirmation.

Command shape:

```bash
okou workflow trigger add <workflow> once --at "2026-06-10T09:00" -z Asia/Shanghai
okou workflow trigger update <trigger-id> --at "2026-06-10T09:00" -z UTC
```

## Fixed Interval

Ask for the interval in natural language. Convert it to a CLI duration such as
`15m`, `1h`, or `90s`.

Command shape:

```bash
okou workflow trigger add <workflow> loop --every 15m
okou workflow trigger update <trigger-id> --every 10m
```

## Chat Run Finished

Collect the watched web chat thread, optional terminal statuses, and optional
final-output pattern. This trigger watches future runs in the thread, not one
run ID, and the thread must belong to the automation owner. When a matching run
reaches `completed`, `failed`, or `cancelled`, it starts a new run in the
workflow's automation thread; it does not resume the watched run.

Omit `--run-status` to match all terminal statuses. `--output-pattern` uses a
case-insensitive `*` wildcard against final assistant text; a run without final
assistant text cannot match a pattern.

Command shape:

```bash
okou workflow trigger add <workflow> chat-run-finished --chat-thread-id <thread-id>
okou workflow trigger add <workflow> chat-run-finished --chat-thread-id <thread-id> --run-status completed,failed --output-pattern "*deploy failed*"
```

## New Email

Ask what incoming Gmail messages should match. Supported natural-language fields
are sender, recipient, cc, subject, and body. Avoid matching every inbound email
unless the user explicitly confirms that broad scope.

For simple matching, use flags:

```bash
okou workflow trigger add <workflow> gmail-new-message --from-contains "@example.com"
okou workflow trigger add <workflow> gmail-new-message --subject-contains "invoice"
```

For complex matching, create a temporary config file and pass `--config`. The
config must be a JSON object with a top-level `match` object. Supported fields:
`from`, `subject`, `body`, `to`, `cc`. Supported matchers: `contains`,
`containsAny`, `doesNotContain`, `doesNotContainAny`.

## Email Label

Ask only for missing details:

1. Which exact Gmail label should trigger the workflow?
2. What should happen when that label is applied?
3. What side effects are allowed?
4. If the label does not exist, may it be created?

Before adding the trigger, check whether the Gmail label exists. If it is missing
and the user already allowed creation, create the label first, then add the
trigger. If creation was not approved, stop and ask. This avoids creating a
workflow, failing the trigger bind, then doing a label-creation retry.

Command shape:

```bash
okou workflow trigger add <workflow> gmail-label-applied --label "Support"
okou workflow trigger update <trigger-id> --label "Support"
```

## Web Trigger

Ask who or what will call the webhook, what payload shape they expect to send,
and whether they can store and sign with the webhook secret.

After creating the trigger, preserve the creation output because the signing
secret is printed only once. In the normal user response, share only the webhook
URL and say that signing details are available if they need to wire it up. If the
user is the implementer and asks for details, provide the signing instructions
without exposing the secret to channels where it does not belong.

Command shape:

```bash
okou workflow trigger add <workflow> webhook
```

## GitHub Label

Ask for the GitHub label, whether it should apply to issues, pull requests, or
both, and whether only the user's own label actions should count or anyone's.

Command shape:

```bash
okou workflow trigger add <workflow> github-label-applied --label "triage" --subject both --actor me
okou workflow trigger update <trigger-id> --label "triage" --subject pull-requests --actor anyone
```

GitHub label triggers require the GitHub App installation in the workspace. If
the command fails for authorization, use the GitHub connector doctor flow instead
of guessing.

## Google Calendar Event Created

Ask which calendar should be watched. Default to the primary calendar only when
the user's wording clearly implies their own main calendar.

Command shape:

```bash
okou workflow trigger add <workflow> google-calendar-event-created --calendar-id primary
```

Current CLI behavior does not support updating this trigger kind. If the user
wants to change the calendar, create a replacement trigger and remove/disable the
old one only with user approval.

## Google Forms Response Submitted

Ask for the Google Form link using this exact wording: "Please open the form's
edit page and copy the link from the address bar."

Command shape:

```bash
okou workflow trigger add <workflow> google-forms-response-submitted --form-url "https://docs.google.com/forms/d/<form-id>/edit"
```
