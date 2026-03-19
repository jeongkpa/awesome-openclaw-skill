---
name: youtube-to-obsidian
description: Use yt-dlp plus transcript extraction and Obsidian note generation to turn a YouTube URL into a Markdown note, with optional local video download stored in a persistent Obsidian-adjacent folder. Trigger when the user wants to save a YouTube URL into Obsidian, archive a lecture/video link, extract subtitles or a Whisper transcript, generate a basic summary, and store both the note and downloaded media in durable paths instead of temporary directories.
---

# Youtube To Obsidian

Turn a YouTube link into an Obsidian note with metadata, transcript, summary, and optional persistent local video storage.

## Quick start

Use this skill when the user gives a YouTube URL and wants one or more of:
- metadata captured
- transcript captured
- summary generated
- note saved into Obsidian
- video downloaded into a persistent folder

Collect these inputs before running:
- `url` (required)
- `vault_path` (required unless the vault is already known)
- `folder` (optional, default `Ingest/YouTube`)
- `media_folder` (optional, default `Ingest/YouTube Media`)
- `download_media` (optional, default `false`)
- `whisper_model` (optional, default `base`)

## Workflow

1. Validate inputs.
- Confirm the URL is a YouTube watch/share URL.
- Confirm the Obsidian vault path exists.
- Create the target note folder and media folder if missing.

2. Check runtime dependencies.
- Prefer Python `yt_dlp` module.
- If unavailable, fall back to `yt-dlp` CLI if present.
- Prefer existing subtitles first.
- If subtitles are unavailable, fall back to local Whisper CLI if installed.
- Require `ffmpeg` for media/transcription fallback paths.

3. Collect source data.
- Use `yt-dlp` to extract metadata.
- If `download_media=true`, download the video into a durable media folder under the vault.
- Try manual subtitles first.
- Try auto-generated subtitles second.
- If no subtitles exist, extract audio from the downloaded video and transcribe locally with Whisper.

4. Normalize transcript.
- Produce plain text transcript.
- Remove noisy timestamp formatting for the main note body.
- Keep subtitle or transcript text files in a durable work subfolder near the media output.
- Deduplicate repeated adjacent lines.

5. Summarize conservatively.
- Prefer extraction-based summary from the cleaned transcript.
- If transcript quality is poor, do not overstate confidence.
- Produce:
  - one short summary paragraph
  - key points list
  - action items list

6. Save to Obsidian.
- Create a Markdown note with frontmatter.
- Include metadata, source URL, summary, key points, transcript, note path, media path, and transcript file path.
- Return the saved note path and media path.

## Persistent storage rule

Do not leave downloaded media only in `/tmp`.

Default durable paths:
- note folder: `Ingest/YouTube`
- media folder: `Ingest/YouTube Media`

If transcription work files are needed, store them in a hidden work subfolder under the media folder rather than in a temporary system directory.

## Output format

Write the Obsidian note in this structure:
- frontmatter
- title
- source link
- metadata block
- summary
- key points
- action items
- transcript
- video path
- transcript file path

See `references/note-template.md` for the default structure.

## MVP limitations

- Handle single-video URLs only.
- Do not handle playlists yet.
- Prefer subtitles over full audio transcription to save time.
- Keep media download optional.
- Use clear partial-success reporting:
  - metadata only
  - metadata + transcript
  - metadata + transcript + summary
  - full success with Obsidian save + media path

## Failure handling

- If `yt-dlp` is missing, stop with a concrete install hint.
- If subtitles and Whisper are both unavailable, save metadata-only note and report transcript failure.
- If Obsidian path is missing, stop before running expensive downloads.
- If the video is private, region-locked, or members-only, report the exact blocker.
- If Whisper tries to download a very large model, switch to `--whisper-model base` for a faster MVP path.

## Resources

### scripts/
- `youtube_to_obsidian.py`: main pipeline script for metadata extraction, transcript capture, summarization, durable media storage, and note writing.

### references/
- `note-template.md`: default Obsidian note layout and frontmatter schema.
