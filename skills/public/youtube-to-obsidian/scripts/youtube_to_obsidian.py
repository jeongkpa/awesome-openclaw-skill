#!/usr/bin/env python3
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Optional


def run(cmd, check=True, capture=True):
    return subprocess.run(cmd, check=check, text=True, capture_output=capture)


def slugify(name: str) -> str:
    name = re.sub(r"[\\/:*?\"<>|]", "-", name)
    name = re.sub(r"\s+", " ", name).strip()
    return name[:180]


def load_yt_dlp():
    try:
        import yt_dlp  # type: ignore
        return yt_dlp
    except Exception:
        return None


def extract_info(url: str):
    yt_dlp = load_yt_dlp()
    if yt_dlp:
        opts = {"skip_download": True, "quiet": True, "no_warnings": True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            return ydl.extract_info(url, download=False)
    if shutil.which("yt-dlp"):
        out = run(["yt-dlp", "--dump-single-json", "--no-warnings", url]).stdout
        return json.loads(out)
    raise RuntimeError("yt-dlp is not installed. Install Python module `yt_dlp` or CLI `yt-dlp`.")


def try_download_subtitles(url: str, outdir: Path) -> Optional[Path]:
    outtmpl = str(outdir / "source")
    candidates = [
        ["yt-dlp", "--skip-download", "--write-subs", "--sub-langs", "all", "-o", outtmpl, url],
        ["yt-dlp", "--skip-download", "--write-auto-subs", "--sub-langs", "all", "-o", outtmpl, url],
    ]
    if not shutil.which("yt-dlp"):
        return None
    for cmd in candidates:
        try:
            run(cmd)
        except subprocess.CalledProcessError:
            continue
        files = sorted(outdir.glob("source*.vtt")) + sorted(outdir.glob("source*.srt"))
        if files:
            return files[0]
    return None


def dedupe_adjacent(lines):
    cleaned = []
    prev = None
    for line in lines:
        if line != prev:
            cleaned.append(line)
        prev = line
    return cleaned


def clean_vtt_or_srt(path: Path) -> str:
    text = path.read_text(errors="ignore")
    lines = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s == "WEBVTT":
            continue
        if re.match(r"^\d+$", s):
            continue
        if "-->" in s:
            continue
        if s.startswith("NOTE"):
            continue
        lines.append(s)
    return "\n".join(dedupe_adjacent(lines)).strip()


def download_video(url: str, outdir: Path, stem: str) -> Path:
    if not shutil.which("yt-dlp"):
        raise RuntimeError("yt-dlp CLI is required for video download.")
    outdir.mkdir(parents=True, exist_ok=True)
    target = outdir / f"{stem}.%(ext)s"
    run(["yt-dlp", "-f", "bv*+ba/b", "--merge-output-format", "mp4", "-o", str(target), url])
    files = sorted([p for p in outdir.glob(f"{stem}.*") if p.suffix.lower() != ".part"])
    if not files:
        raise RuntimeError("Video download failed.")
    preferred = [p for p in files if p.suffix.lower() == ".mp4"]
    return preferred[0] if preferred else files[0]


def extract_audio_from_video(video_path: Path, outdir: Path) -> Path:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg is required for transcription fallback.")
    outdir.mkdir(parents=True, exist_ok=True)
    audio_path = outdir / f"{video_path.stem}.mp3"
    run([
        "ffmpeg", "-y", "-i", str(video_path), "-vn", "-acodec", "mp3", str(audio_path)
    ])
    if not audio_path.exists():
        raise RuntimeError("Audio extraction from video failed.")
    return audio_path


def transcribe_with_whisper(audio_path: Path, outdir: Path, model: str = "base") -> Path:
    if not shutil.which("whisper"):
        raise RuntimeError("Whisper CLI is not installed.")
    print(f"INFO: running whisper transcription with model={model}", file=sys.stderr)
    run([
        "whisper",
        str(audio_path),
        "--model", model,
        "--output_format", "txt",
        "--output_dir", str(outdir),
    ])
    txt = outdir / f"{audio_path.stem}.txt"
    if not txt.exists():
        txts = list(outdir.glob("*.txt"))
        if not txts:
            raise RuntimeError("Whisper transcription failed.")
        txt = txts[0]
    return txt


def normalize_transcript_text(text: str) -> str:
    lines = []
    for raw in text.splitlines():
        s = re.sub(r"\s+", " ", raw).strip()
        if not s:
            continue
        lines.append(s)
    lines = dedupe_adjacent(lines)
    return "\n".join(lines).strip()


def sentence_split(text: str):
    flat = re.sub(r"\s+", " ", text).strip()
    if not flat:
        return []
    parts = re.split(r"(?<=[\.!?다요죠])\s+", flat)
    parts = [p.strip() for p in parts if p.strip()]
    return parts


def score_sentence(sentence: str) -> int:
    score = 0
    if 20 <= len(sentence) <= 140:
        score += 3
    if any(k in sentence for k in ["핵심", "결론", "요약", "중요", "의미", "전망", "이유", "왜냐"]):
        score += 4
    if any(k in sentence for k in ["투자", "AI", "AGI", "미래", "시장", "전략"]):
        score += 2
    if sentence.endswith(("다.", "요.", "죠.", "니다.")):
        score += 1
    if re.search(r"[0-9]{2,}", sentence):
        score += 1
    return score


def build_summary(transcript: str, title: str, channel: str) -> dict:
    normalized = normalize_transcript_text(transcript)
    if not normalized:
        return {
            "summary": f"Transcript unavailable for {title} from {channel}.",
            "key_points": ["Transcript unavailable."],
            "action_items": ["Retry with subtitles enabled or a different Whisper model."],
        }

    sentences = sentence_split(normalized)
    if not sentences:
        sentences = [line for line in normalized.splitlines() if line.strip()]

    ranked = sorted(sentences, key=lambda s: (-score_sentence(s), sentences.index(s)))
    top = ranked[:8]
    summary_sentences = top[:3] if len(top) >= 3 else top
    key_points = top[:6]

    action_candidates = [
        s for s in sentences
        if any(k in s for k in ["해야", "보면", "추천", "준비", "주의", "기억", "필요", "중요"])
    ]
    action_items = action_candidates[:4]
    if not action_items:
        action_items = ["Review the note and refine the summary if the transcript quality is noisy."]

    summary = " ".join(summary_sentences)
    summary = re.sub(r"\s+", " ", summary).strip()
    return {
        "summary": summary,
        "key_points": key_points,
        "action_items": action_items,
    }


def human_duration(seconds: Optional[int]) -> str:
    if not seconds:
        return "unknown"
    h, rem = divmod(int(seconds), 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def write_note(vault_path: Path, folder: str, info: dict, transcript: str, summary: dict, media_path: Optional[Path], transcript_path: Optional[Path]) -> Path:
    target_dir = vault_path / folder
    target_dir.mkdir(parents=True, exist_ok=True)
    title = info.get("title") or "Untitled YouTube Video"
    filename = slugify(title) + ".md"
    note_path = target_dir / filename
    published = info.get("upload_date") or ""
    if len(published) == 8:
        published = f"{published[:4]}-{published[4:6]}-{published[6:8]}"
    media_line = str(media_path) if media_path else ""
    transcript_file_line = str(transcript_path) if transcript_path else ""
    content = textwrap.dedent(f"""
---
title: {title}
source: youtube
url: {info.get('webpage_url') or info.get('original_url') or ''}
video_id: {info.get('id') or ''}
channel: {info.get('channel') or info.get('uploader') or ''}
published: {published}
duration_seconds: {info.get('duration') or ''}
media_path: {media_line}
transcript_path: {transcript_file_line}
tags:
  - youtube
  - inbox
---

# {title}

- URL: {info.get('webpage_url') or info.get('original_url') or ''}
- Channel: {info.get('channel') or info.get('uploader') or ''}
- Published: {published}
- Duration: {human_duration(info.get('duration'))}
- Video Path: {media_line or 'not saved'}
- Transcript File: {transcript_file_line or 'not saved'}

## Summary

{summary['summary']}

## Key Points

{os.linesep.join('- ' + x for x in summary['key_points'])}

## Action Items

{os.linesep.join('- ' + x for x in summary['action_items'])}

## Transcript

{transcript if transcript else 'Transcript unavailable'}
""").strip() + "\n"
    note_path.write_text(content)
    return note_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--vault-path", required=True)
    ap.add_argument("--folder", default="Inbox/YouTube")
    ap.add_argument("--media-folder", default="Ingest/YouTube Media")
    ap.add_argument("--work-dir", default=None)
    ap.add_argument("--download-media", action="store_true")
    ap.add_argument("--whisper-model", default="base")
    args = ap.parse_args()

    vault = Path(args.vault_path).expanduser()
    if not vault.exists():
        raise SystemExit(f"Vault path does not exist: {vault}")

    print("INFO: extracting metadata", file=sys.stderr)
    info = extract_info(args.url)
    title = info.get("title") or "Untitled YouTube Video"
    slug = slugify(title)

    target_note_dir = vault / args.folder
    target_media_dir = vault / args.media_folder
    target_note_dir.mkdir(parents=True, exist_ok=True)
    target_media_dir.mkdir(parents=True, exist_ok=True)

    work_dir = Path(args.work_dir).expanduser() if args.work_dir else (target_media_dir / f".{slug}-work")
    work_dir.mkdir(parents=True, exist_ok=True)

    media_path: Optional[Path] = None
    transcript = ""
    transcript_file_path: Optional[Path] = None

    if args.download_media:
        print("INFO: downloading video", file=sys.stderr)
        media_path = download_video(args.url, target_media_dir, slug)
        print(f"INFO: video downloaded to {media_path}", file=sys.stderr)

    print("INFO: trying subtitle download", file=sys.stderr)
    subtitle_path = try_download_subtitles(args.url, work_dir)
    if subtitle_path:
        print(f"INFO: subtitle found at {subtitle_path}", file=sys.stderr)
        transcript = clean_vtt_or_srt(subtitle_path)
        transcript_file_path = subtitle_path
    else:
        print("INFO: subtitles unavailable, falling back to video/audio + whisper", file=sys.stderr)
        try:
            if media_path is None:
                print("INFO: downloading video for transcription fallback", file=sys.stderr)
                media_path = download_video(args.url, target_media_dir, slug)
                print(f"INFO: video downloaded to {media_path}", file=sys.stderr)
            audio_path = extract_audio_from_video(media_path, work_dir)
            print(f"INFO: audio extracted to {audio_path}", file=sys.stderr)
            txt_path = transcribe_with_whisper(audio_path, work_dir, model=args.whisper_model)
            transcript = normalize_transcript_text(txt_path.read_text(errors="ignore").strip())
            transcript_file_path = txt_path
        except Exception as e:
            transcript = ""
            print(f"WARN: transcript capture failed: {e}", file=sys.stderr)

    print("INFO: generating summary", file=sys.stderr)
    summary = build_summary(transcript, title, info.get("channel", ""))
    print("INFO: writing obsidian note", file=sys.stderr)
    note = write_note(vault, args.folder, info, transcript, summary, media_path, transcript_file_path)

    result = {
        "note_path": str(note),
        "media_path": str(media_path) if media_path else None,
        "transcript_path": str(transcript_file_path) if transcript_file_path else None,
        "title": title,
        "url": info.get("webpage_url") or info.get("original_url"),
        "transcript_available": bool(transcript),
        "summary_available": bool(summary.get("summary")),
        "subtitle_used": bool(subtitle_path),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
