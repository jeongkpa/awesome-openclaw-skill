# n8n Build Patterns

## Minimal-first patterns

### Webhook test page
- Webhook
- Set / Edit Fields
- Respond to Webhook

Use this for:
- connectivity tests
- HTML landing/test pages
- quick deployment checks

### JSON API stub
- Webhook
- Set / Code
- Respond to Webhook

Use this for:
- contract tests
- fake endpoints
- request/response prototyping

### Scheduled notifier
- Schedule Trigger
- Fetch node (HTTP / Sheets / Gmail / DB)
- Filter / IF
- Notify node

Use this for:
- daily briefings
- periodic checks
- threshold alerts

## Naming conventions

Prefer names that reveal function:
- `Webhook`
- `Set Test Data`
- `Respond to Webhook`
- `Fetch Latest Orders`
- `Filter Important Messages`
- `Send Telegram Alert`

Avoid generic chains of default names when the workflow will live longer than a quick test.

## Validation checklist

Before create/update:
- Node names are unique
- Connections reference real node names
- Trigger type matches intended invocation pattern
- Response node exists for webhook response mode workflows
- Credentials are intentional
- Content type is explicit when serving HTML or JSON APIs
- Activation decision is explicit

## Deployment checklist

For new workflows:
1. Create locally as JSON
2. Validate structure
3. Create remotely
4. Inspect resulting workflow
5. Activate only if needed
6. Test real behavior

For existing workflows:
1. Read current workflow
2. Identify changed nodes only
3. Prefer backup/copy when risk exists
4. Replace/update carefully
5. Re-test trigger/output path

## Practical reliability notes

- Defaults are often the source of runtime failure; set behavior-critical fields explicitly.
- Webhook workflows should be tested with a real HTTP request after activation.
- For browser-facing responses, verify content type and rendering, not just status code.
- For AI workflows, check tool/model/memory wiring after any edit.
