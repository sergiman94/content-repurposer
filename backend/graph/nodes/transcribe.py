"""Node 2: Transcribe audio via Groq Whisper API."""

from __future__ import annotations

from groq import Groq

from backend.config import get_settings
from backend.graph.state import RepurposeState
from backend.services.media import split_audio_if_needed


def transcribe(state: RepurposeState) -> dict:
    """Transcribe audio file to text using Groq Whisper.

    Handles files >25MB by splitting into chunks and concatenating.

    Reads: audio_path
    Writes: transcript, transcript_segments, current_step, error
    """
    updates: dict = {"current_step": "transcribe"}
    audio_path = state.get("audio_path")

    if not audio_path:
        updates["error"] = "No audio file to transcribe"
        return updates

    try:
        settings = get_settings()
        client = Groq(api_key=settings.groq_api_key)

        # Split if file exceeds Groq's 25MB limit
        chunks = split_audio_if_needed(audio_path)

        all_text = []
        all_segments = []
        time_offset = 0.0

        for chunk_path in chunks:
            with open(chunk_path, "rb") as f:
                response = client.audio.transcriptions.create(
                    model=settings.groq_whisper_model,
                    file=f,
                    response_format="verbose_json",
                    language="en",
                )

            all_text.append(response.text)

            # Collect segments with time offset for multi-chunk files
            for seg in response.segments or []:
                all_segments.append({
                    "start": round(seg.start + time_offset, 2),
                    "end": round(seg.end + time_offset, 2),
                    "text": seg.text,
                })

            # Advance offset for next chunk
            if response.segments:
                time_offset += response.segments[-1].end

        updates["transcript"] = " ".join(all_text)
        updates["transcript_segments"] = all_segments

    except Exception as e:
        updates["error"] = f"Transcription failed: {type(e).__name__}: {e}"

    return updates
