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
media_path: {{media_path}}
transcript_path: {{transcript_path}}
tags:
  - youtube
  - inbox
---

# {{title}}

- URL: {{url}}
- Channel: {{channel}}
- Published: {{published}}
- Duration: {{duration_human}}
- Video Path: {{media_path}}
- Transcript File: {{transcript_path}}

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
- Prefer durable media storage under the vault instead of temporary system directories.
