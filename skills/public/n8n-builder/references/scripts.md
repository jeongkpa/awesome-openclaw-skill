# Script Reference

## `scripts/n8n_safe_ops.py`

Purpose:
- provide safer n8n API operations
- retry transient failures
- fall back from `PATCH` to `PUT` on workflow update when needed
- fall back on activation/deactivation strategy when endpoints differ

Examples:

```bash
python3 scripts/n8n_safe_ops.py list --limit 10 --pretty
python3 scripts/n8n_safe_ops.py get --id <workflow-id> --pretty
python3 scripts/n8n_safe_ops.py create --file workflow.json --pretty
python3 scripts/n8n_safe_ops.py update --id <workflow-id> --file workflow.json --pretty
python3 scripts/n8n_safe_ops.py activate --id <workflow-id> --pretty
```

Environment:
- `N8N_API_URL` or `N8N_BASE_URL`
- `N8N_API_KEY`

The script also checks `~/.openclaw/skills/n8n/.env` as a convenience source.

## `scripts/webhook_smoke_test.py`

Purpose:
- verify a deployed webhook quickly
- check status code
- check content type
- preview response body

Examples:

```bash
python3 scripts/webhook_smoke_test.py https://example.com/webhook/test
python3 scripts/webhook_smoke_test.py https://example.com/webhook/test --expect-content-type text/html
python3 scripts/webhook_smoke_test.py https://example.com/webhook/test --expect-content-type application/json
```

Use this after activation for webhook workflows.
