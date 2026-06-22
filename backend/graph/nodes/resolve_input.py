"""Node 1: Classify input type, download/extract audio if needed."""

from __future__ import annotations

from backend.graph.state import RepurposeState


def resolve_input(state: RepurposeState) -> dict:
    """Resolve raw input into a transcript (text) or audio_path (media).

    Reads: raw_input, input_type
    Writes: audio_path or transcript, current_step, error
    """
    updates: dict = {"current_step": "resolve_input"}
    raw = state["raw_input"]
    input_type = state["input_type"]

    try:
        if input_type == "text":
            if not raw or len(raw.strip()) < 50:
                updates["error"] = "Text input too short (minimum 50 characters)"
                return updates
            updates["transcript"] = raw

        elif input_type in ("youtube_url", "vimeo_url"):
            # Phase 3: download via yt-dlp
            updates["error"] = "YouTube/Vimeo download not yet implemented"

        elif input_type == "video":
            # Phase 3: extract audio via ffmpeg
            updates["error"] = "Video processing not yet implemented"

        elif input_type == "audio":
            # Phase 3: validate audio file exists
            updates["error"] = "Audio processing not yet implemented"

        else:
            updates["error"] = f"Unknown input type: {input_type}"

    except Exception as e:
        updates["error"] = f"Input resolution failed: {type(e).__name__}: {e}"

    return updates
