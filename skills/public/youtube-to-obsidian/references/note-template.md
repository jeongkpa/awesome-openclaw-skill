# Default Obsidian Note Template

```markdown
---
title: {{title}}
source: youtube
url: {{url}}
video_id: {{video_id}}
channel: {{channel}}
published: {{published}}
duration_seconds: {{duration}}
tags:
  - youtube
  - inbox
---

# {{title}}

- URL: {{url}}
- Channel: {{channel}}
- Published: {{published}}
- Duration: {{duration_human}}

## Summary

{{summary}}

## Key Points

{{key_points}}

## Action Items

{{action_items}}

## Transcript

{{transcript}}
```

## Notes

- Keep transcript readable and remove VTT timestamp noise in the main note.
- Prefer subtitle text when available; fall back to Whisper only when needed.
- When Whisper output is noisy, keep the transcript but make the summary conservative and extraction-based rather than pretending high confidence.
