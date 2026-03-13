---
name: n8n-builder
description: Build, inspect, validate, and safely update n8n workflows using a hybrid approach: direct n8n API operations plus n8n-MCP documentation/template research. Use when creating new n8n workflows, modifying existing workflows, selecting the right nodes, researching node properties or template patterns, validating workflow JSON before deployment, building webhook/schedule/AI-agent automations, or troubleshooting n8n workflow structure. Prefer read-only discovery first, then create/update only after the workflow shape is clear.
---

# n8n Builder

Use a two-layer workflow:

1. **Research with n8n-MCP first** for nodes, properties, examples, and templates.
2. **Operate on the actual n8n instance second** using the API-backed local n8n tooling.

This skill is for building reliable n8n workflows, not just calling the API blindly.

## Core operating rules

- Start with discovery before mutation.
- Prefer read-only steps first: search nodes, inspect docs, search templates, inspect current workflows.
- Do not edit production workflows directly if a copy/test workflow can be used first.
- Validate workflow JSON before create/update.
- Treat defaults as unsafe until confirmed.
- For webhook workflows, verify both activation state and real HTTP response behavior.
- For AI-agent workflows, explicitly inspect required model, credential, and tool nodes rather than assuming defaults.

## Environment assumptions

This skill works best when both of these are available:

- **n8n API access**
  - local helper scripts or equivalent API client
  - required: `N8N_API_URL` / `N8N_BASE_URL`
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

If the user asks vaguely, reduce it to a small first version before building.

### 2. Research before building

Use n8n-MCP to answer these questions:
- Which node types fit the task?
- Is there a template close to the requested automation?
- Which properties are required?
- Are there known webhook or AI-agent patterns that should be copied?

Good MCP discovery pattern:
- search nodes by task keyword
- inspect the most likely node docs
- search templates by task or node type
- only then draft the workflow JSON

### 3. Prefer the smallest valid workflow

Build the smallest workflow that proves the path end-to-end.
Examples:
- webhook -> set -> respond
- schedule -> fetch -> filter -> notify
- manual trigger -> http request -> set/output

Avoid overbuilding on the first pass.

### 4. Validate before deployment

Before create/update:
- validate node assumptions
- validate workflow JSON structure
- verify connections point to real node names
- verify response mode for webhook flows
- verify credentials are referenced intentionally, not implicitly

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

### 6. Verify behavior externally

For webhook flows:
- call the public/test URL and verify status code, content type, and body

For scheduled flows:
- inspect schedule trigger configuration and recent execution behavior

For AI-agent flows:
- verify model node, tool nodes, and memory/tool connections explicitly

## Safe mutation policy

Use this default order of safety:
1. Search templates and docs
2. Read current workflow
3. Draft workflow JSON locally
4. Validate locally / structurally
5. Create a new test workflow
6. Activate only if needed
7. Update an existing workflow only after confirming scope

Do not silently activate or execute remote workflows unless the user asked for it or the task clearly requires it.

## Workflow design heuristics

### Webhook workflows
- Use `Webhook` + `Respond to Webhook` for browser/API-friendly tests.
- Return explicit content type.
- For HTML responses, set `text/html; charset=utf-8`.
- For JSON responses, verify the object shape is intentional and minimal.
- Keep the path simple and memorable for test workflows.

### Schedule workflows
- Keep time zone explicit.
- Start with one simple branch.
- Avoid hidden side effects on the first version.

### Data transformation workflows
- Prefer `Set`, `Code`, `IF`, and a small number of nodes initially.
- Name nodes clearly by role, not generic defaults.

### AI workflows
- Confirm node compatibility before mixing agent/model/tool nodes.
- Inspect examples before composing multi-node AI flows.
- Validate tool connections and response behavior after any structural change.

## Error handling

When API calls fail:
- distinguish schema/config errors from transport/server errors
- retry only transient failures
- for server errors, log the failing action, workflow id, and request context
- if update semantics differ by environment, inspect supported methods before retrying

Known practical lesson:
- Some n8n environments accept `PUT` for workflow replacement and explicit activation endpoints more reliably than naive partial-update assumptions. Confirm against the target environment instead of assuming one update method.

## Files and resources in this skill

Read these bundled references when needed:
- `references/build-patterns.md` — practical workflow-building patterns and safety rules
- `references/mcp-usage.md` — how to use n8n-MCP for node/template research

Use these scripts/resources as local examples, not blind deployment artifacts.
