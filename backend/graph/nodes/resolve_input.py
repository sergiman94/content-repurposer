"""Node 1: Classify input type, download/extract audio if needed."""

from __future__ import annotations

import os

from backend.graph.state import RepurposeState
from backend.services.media import download_youtube_audio, extract_audio_from_video


def resolve_input(state: RepurposeState) -> dict:
    """Resolve raw input into a transcript (text) or audio_path (media).

    Reads: raw_input, input_type
    Writes: audio_path or transcript, current_step, error
    """
    updates: dict = {"current_step": "resolve_input"}
    raw = state["raw_input"]
    input_type = state["input_type"]
    job_id = state.get("job_id", "unknown")

    try:
        if input_type == "text":
            if not raw or len(raw.strip()) < 50:
                updates["error"] = "Text input too short (minimum 50 characters)"
                return updates
            updates["transcript"] = raw

        elif input_type in ("youtube_url", "vimeo_url"):
            audio_path = download_youtube_audio(raw, job_id)
            updates["audio_path"] = audio_path

        elif input_type == "video":
            if not os.path.isfile(raw):
                updates["error"] = f"Video file not found: {raw}"
                return updates
            audio_path = extract_audio_from_video(raw, job_id)
            updates["audio_path"] = audio_path

        elif input_type == "audio":
            if not os.path.isfile(raw):
                updates["error"] = f"Audio file not found: {raw}"
                return updates
            updates["audio_path"] = raw

        else:
            updates["error"] = f"Unknown input type: {input_type}"

    except Exception as e:
        updates["error"] = f"Input resolution failed: {type(e).__name__}: {e}"

    return updates
