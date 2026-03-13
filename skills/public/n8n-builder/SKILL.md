---
name: n8n-builder
description: "Build, inspect, validate, test, and safely update n8n workflows using a hybrid approach: n8n-MCP for node/template research and direct n8n API operations for deployment. Use when creating new n8n workflows, modifying existing workflows, selecting the right nodes, researching node properties or template patterns, validating workflow JSON before deployment, building webhook/schedule/AI-agent automations, troubleshooting n8n workflow structure, or wrapping n8n changes in a safer test-first process. Prefer read-only discovery first, then create/update only after the workflow shape is clear."
---

# n8n Builder

Use a two-layer workflow:

1. **Research with n8n-MCP first** for nodes, properties, examples, and templates.
2. **Operate on the actual n8n instance second** using API-backed local n8n tooling.

This skill is for building reliable n8n workflows, not just calling the API blindly.

## Trigger patterns

Use this skill when the user asks for things like:
- "n8n 워크플로우 하나 만들어줘"
- "이 자동화를 n8n으로 옮겨줘"
- "webhook 테스트 workflow 만들어줘"
- "이 workflow 수정해줘"
- "어떤 n8n 노드를 써야 해?"
- "n8n AI agent workflow 설계해줘"
- "템플릿 먼저 찾아보고 비슷하게 만들어줘"

## Core operating rules

- Start with discovery before mutation.
- Prefer read-only steps first: search nodes, inspect docs, search templates, inspect current workflows.
- Do not edit production workflows directly if a copy/test workflow can be used first.
- Validate workflow JSON before create/update.
- Treat defaults as unsafe until confirmed.
- For webhook workflows, verify both activation state and real HTTP response behavior.
- For AI-agent workflows, explicitly inspect required model, credential, and tool nodes rather than assuming defaults.
- Do not silently activate, execute, or overwrite remote workflows unless the user asked for it or the task clearly requires it.

## Environment assumptions

This skill works best when both of these are available:

- **n8n API access**
  - local helper scripts or equivalent API client
  - required: `N8N_API_URL` or `N8N_BASE_URL`
  - required: `N8N_API_KEY`
- **n8n-MCP access**
  - for node docs, template search, validation guidance, and example discovery
  - recommended in read-only mode by default

If only one layer is available:
- With only n8n-MCP: research and design workflows, but do not deploy.
- With only n8n API: work more conservatively and inspect existing workflows before changing anything.

## Recommended workflow

### 1. Clarify the automation goal

Collect the minimum viable spec:
- trigger type: webhook / schedule / manual / form / chat
- inputs
- external services involved
- required outputs
- whether this is test-only or production-bound
- whether activation should happen immediately
- whether the user wants HTML, JSON, email, sheet write, or chat output

If the user asks vaguely, reduce it to a small first version before building.

### 2. Research before building

Use n8n-MCP to answer these questions:
- Which node types fit the task?
- Is there a template close to the requested automation?
- Which properties are required?
- Are there known webhook or AI-agent patterns that should be copied?
- Which node options are behavior-critical and should not be left at defaults?

Good MCP discovery pattern:
- search nodes by task keyword
- inspect the most likely node docs
- search templates by task or node type
- inspect specific properties when auth/body/response behavior matters
- only then draft the workflow JSON

### 3. Prefer the smallest valid workflow

Build the smallest workflow that proves the path end-to-end.
Examples:
- webhook -> set -> respond
- schedule -> fetch -> filter -> notify
- manual trigger -> http request -> set/output
- chat trigger -> AI agent -> tool -> response

Avoid overbuilding on the first pass.

### 4. Validate before deployment

Before create/update:
- validate node assumptions
- validate workflow JSON structure
- verify connections point to real node names
- verify response mode for webhook flows
- verify credentials are referenced intentionally, not implicitly
- verify names are readable enough for future maintenance
- verify time zone / content type / model / operation fields when they affect runtime behavior

### 5. Deploy conservatively

For new workflows:
- create first
- inspect created workflow
- activate only if needed
- test the trigger after activation

For existing workflows:
- inspect current workflow first
- prefer updating a copy or test variant if risk exists
- after update, verify the expected nodes and connections persisted
- re-test the externally visible behavior, not just the stored JSON

### 6. Verify behavior externally

For webhook flows:
- call the public/test URL and verify status code, content type, and body
- for HTML responses, verify the page actually renders in a browser
- for JSON responses, verify the response shape is stable and intentional

For scheduled flows:
- inspect schedule trigger configuration and recent execution behavior

For AI-agent flows:
- verify model node, tool nodes, and memory/tool connections explicitly
- confirm the workflow still makes sense without hidden defaults

## Safe mutation policy

Use this default order of safety:
1. Search templates and docs
2. Read current workflow
3. Draft workflow JSON locally
4. Validate locally / structurally
5. Create a new test workflow
6. Activate only if needed
7. Update an existing workflow only after confirming scope

If the user is touching an important existing workflow, explicitly recommend a backup/copy first.

## Retry and error-handling policy

Retry only transient failures.

Safe retry candidates:
- upstream `server_error`
- temporary network failures
- timeouts
- intermittent MCP server startup issues

Do **not** blindly retry:
- auth failures
- permission failures
- malformed requests
- schema/config validation failures
- obvious wrong endpoint/method usage

Recommended retry policy:
- max 3 attempts
- exponential backoff such as 3s -> 10s -> 25s
- log failing action, workflow id, endpoint, and request context
- if a request id is returned by the upstream provider, keep it in the failure note

## Workflow design heuristics

### Webhook workflows
- Use `Webhook` + `Respond to Webhook` for browser/API-friendly tests.
- Return explicit content type.
- For HTML responses, set `text/html; charset=utf-8`.
- For JSON responses, verify the object shape is intentional and minimal.
- Keep the path simple and memorable for test workflows.
- Test with a real HTTP request after activation.

### Schedule workflows
- Keep time zone explicit.
- Start with one simple branch.
- Avoid hidden side effects on the first version.
- Confirm the trigger schedule matches the user's actual expectation, not a guessed cadence.

### Data transformation workflows
- Prefer `Set`, `Code`, `IF`, and a small number of nodes initially.
- Name nodes clearly by role, not generic defaults.
- Make output shape obvious before adding delivery steps.

### AI workflows
- Confirm node compatibility before mixing agent/model/tool nodes.
- Inspect examples before composing multi-node AI flows.
- Validate tool connections and response behavior after any structural change.
- Be explicit about model selection and required credentials.

## Practical notes from real use

Known practical lesson:
- Some n8n environments accept `PUT` for workflow replacement and explicit activation endpoints more reliably than naive partial-update assumptions. Confirm against the target environment instead of assuming one update method.

Practical lesson for webhook tests:
- A minimal `Webhook -> Set -> Respond to Webhook` workflow is the fastest safe way to verify deployment, activation, and public reachability.

## Files and resources in this skill

Read these bundled references when needed:
- `references/build-patterns.md` — practical workflow-building patterns and safety rules
- `references/mcp-usage.md` — how to use n8n-MCP for node/template research
- `references/live-notes.md` — observations from real n8n Cloud testing
- `references/scripts.md` — helper script usage and examples

Bundled helper scripts:
- `scripts/n8n_safe_ops.py` — safer API operations with retry and method fallbacks
- `scripts/webhook_smoke_test.py` — quick deployed-webhook verification
- `scripts/example-webhook-html.json` — minimal HTML webhook example

Use these scripts/resources as local examples and helpers, not blind deployment artifacts.
