# Using n8n-MCP Effectively

Use n8n-MCP as the research layer before touching the live n8n instance.

## Best order

1. `tools_documentation`
2. `search_templates`
3. `search_nodes`
4. `get_node`
5. `validate_node`
6. `validate_workflow`

## Good research questions

### Find the right trigger
Search for:
- `webhook`
- `schedule`
- `form`
- `chat`
- `gmail trigger`
- `google sheets trigger`

### Find transformation tools
Search for:
- `set`
- `code`
- `if`
- `merge`
- `aggregate`

### Find delivery nodes
Search for:
- `telegram`
- `gmail`
- `slack`
- `google sheets`
- `http request`

## Template-first approach

Before building from scratch, search templates by:
- keyword
- task
- node types

Useful examples:
- webhook processing
- email automation
- data transformation
- ai automation
- api integration

## Why this matters

n8n-MCP reduces guesswork around:
- required properties
- operation names
- version differences
- example configurations
- node compatibility

## Practical strategy

When the user asks for a workflow:
1. search templates for close matches
2. inspect the likely nodes
3. collect only the properties needed for the first version
4. draft JSON
5. validate before deployment

## Safety stance

Use n8n-MCP in read-only mode by default when possible.
Add live n8n API credentials only when workflow create/update/execute is actually needed.
