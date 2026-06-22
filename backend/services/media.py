"""Media services: YouTube download, audio extraction, audio splitting."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from backend.config import get_settings


def _uploads_dir() -> Path:
    d = Path(get_settings().storage_dir) / "uploads"
    d.mkdir(parents=True, exist_ok=True)
    return d


def download_youtube_audio(url: str, job_id: str) -> str:
    """Download audio from YouTube/Vimeo via yt-dlp.

    Returns path to the downloaded MP3 file.
    Raises ValueError on invalid URL, RuntimeError on download failure.
    """
    if not _is_valid_video_url(url):
        raise ValueError(f"Invalid video URL: {url}")

    out_dir = _uploads_dir() / job_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_template = str(out_dir / "%(id)s.%(ext)s")

    result = subprocess.run(
        [
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "--audio-quality", "5",
            "--no-playlist",
            "--max-filesize", "500M",
            "-o", out_template,
            url,
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )

    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {result.stderr[:500]}")

    # Find the downloaded file
    mp3_files = list(out_dir.glob("*.mp3"))
    if not mp3_files:
        raise RuntimeError("yt-dlp completed but no MP3 file found")

    return str(mp3_files[0])


def extract_audio_from_video(video_path: str, job_id: str) -> str:
    """Extract audio track from a video file using ffmpeg.

    Returns path to the extracted MP3.
    Raises RuntimeError on ffmpeg failure.
    """
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")

    out_dir = _uploads_dir() / job_id
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = str(out_dir / "extracted_audio.mp3")

    result = subprocess.run(
        [
            "ffmpeg",
            "-i", video_path,
            "-vn",
            "-acodec", "libmp3lame",
            "-q:a", "5",
            "-y",
            output_path,
        ],
        capture_output=True,
        text=True,
        timeout=300,
    )

    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {result.stderr[:500]}")

    if not os.path.isfile(output_path):
        raise RuntimeError("ffmpeg completed but output file not found")

    return output_path


def split_audio_if_needed(audio_path: str, max_size_mb: int = 24) -> list[str]:
    """Split audio into chunks if it exceeds max_size_mb (Groq Whisper limit is 25MB).

    Returns list of chunk paths. If file is small enough, returns [audio_path].
    """
    file_size_mb = os.path.getsize(audio_path) / (1024 * 1024)

    if file_size_mb <= max_size_mb:
        return [audio_path]

    # Get duration via ffprobe
    duration = _get_audio_duration(audio_path)
    if duration <= 0:
        return [audio_path]

    # Calculate chunk count and duration
    num_chunks = int(file_size_mb / max_size_mb) + 1
    chunk_duration = duration / num_chunks

    out_dir = Path(audio_path).parent
    chunks = []

    for i in range(num_chunks):
        start = i * chunk_duration
        chunk_path = str(out_dir / f"chunk_{i:03d}.mp3")

        result = subprocess.run(
            [
                "ffmpeg",
                "-i", audio_path,
                "-ss", str(start),
                "-t", str(chunk_duration),
                "-acodec", "libmp3lame",
                "-q:a", "5",
                "-y",
                chunk_path,
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )

        if result.returncode == 0 and os.path.isfile(chunk_path):
            chunks.append(chunk_path)

    return chunks if chunks else [audio_path]


def _get_audio_duration(audio_path: str) -> float:
    """Get audio duration in seconds via ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v", "quiet",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                audio_path,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return float(result.stdout.strip())
    except (ValueError, subprocess.TimeoutExpired):
        return 0.0


def _is_valid_video_url(url: str) -> bool:
    """Basic validation for YouTube/Vimeo URLs."""
    patterns = [
        r"https?://(www\.)?youtube\.com/watch\?v=",
        r"https?://youtu\.be/",
        r"https?://(www\.)?vimeo\.com/\d+",
        r"https?://player\.vimeo\.com/video/\d+",
    ]
    return any(re.match(p, url) for p in patterns)
