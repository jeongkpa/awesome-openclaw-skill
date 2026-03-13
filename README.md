# awesome-openclaw-skill

OpenClaw skills collection.

## Included

- `gpters-post-publisher`
  - Automates GPTers 사례글 publishing flow
  - Uses rendered rich-text body insertion (not raw markdown)
  - Adds tag `21기 내삶자동화` and confirms publish by final URL

- `n8n-builder`
  - Builds and updates n8n workflows with a safer hybrid flow
  - Uses n8n-MCP first for node docs, template search, and validation guidance
  - Uses direct n8n API operations second for create/update/test work
  - Encourages test-first deployment, explicit validation, and conservative activation
  - Includes a minimal HTML webhook example and real-world API behavior notes

## Install (manual)

1. Copy the skill folder to your OpenClaw workspace:

```bash
# from repo root
cp -R skills/public/<skill-name> ~/.openclaw/workspace/skills/public/
```

Examples:

```bash
cp -R skills/public/gpters-post-publisher ~/.openclaw/workspace/skills/public/
cp -R skills/public/n8n-builder ~/.openclaw/workspace/skills/public/
```

2. Ensure this file exists:

```bash
~/.openclaw/workspace/skills/public/<skill-name>/SKILL.md
```

3. Restart OpenClaw (or start a new session).

## Notes

### gpters-post-publisher
- If GPTers login is required, complete login manually and then resume automation.
- Tag selection may require explicit suggestion selection depending on live editor behavior.

### n8n-builder
- Best used with both n8n API access and n8n-MCP.
- Prefer read-only discovery first, then mutation.
- Do not edit production workflows directly when a test copy is possible.
