# Live Notes from Real Use

These are practical notes observed while wiring a local n8n skill against a real n8n Cloud instance.

## Confirmed working patterns

- Read-only listing of workflows with a simple API client works reliably.
- A minimal webhook -> set -> respond workflow is a good first deployment test.
- `Respond to Webhook` can return HTML successfully when `contentType` is set explicitly.
- Real browser verification of the deployed webhook is useful after activation.

## Confirmed API behavior differences to account for

Do not assume one update strategy blindly.
In the tested environment:
- naive `PATCH /workflows/{id}` returned `405 Method Not Allowed`
- `PUT /workflows/{id}` worked for replacing workflow JSON
- explicit activation endpoint worked reliably

Implication:
- inspect the target environment's accepted methods
- do not hardcode a partial-update assumption in a reusable skill

## Recommended safety approach

- research first with n8n-MCP
- create test workflows before touching important ones
- validate before deployment
- verify the trigger path after activation
