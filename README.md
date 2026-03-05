# awesome-openclaw-skill

OpenClaw skills collection.

## Included

- `gpters-post-publisher`
  - Automates GPTers 사례글 publishing flow
  - Uses rendered rich-text body insertion (not raw markdown)
  - Adds tag `21기 내삶자동화` and confirms with Enter before publish

## Install (manual)

1. Copy the skill folder to your OpenClaw workspace:

```bash
# from repo root
cp -R skills/public/gpters-post-publisher ~/.openclaw/workspace/skills/public/
```

2. Ensure this file exists:

```bash
~/.openclaw/workspace/skills/public/gpters-post-publisher/SKILL.md
```

3. Restart OpenClaw (or start a new session).

## Notes

- If GPTers login is required, complete login manually and then resume automation.
- Tag input must be finalized with **Enter**. If the tag dropdown is open, close it before publishing.
