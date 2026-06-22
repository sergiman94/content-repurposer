"""Node 2: Transcribe audio via Groq Whisper API."""

from __future__ import annotations

from backend.graph.state import RepurposeState


def transcribe(state: RepurposeState) -> dict:
    """Transcribe audio file to text using Groq Whisper.

    Reads: audio_path
    Writes: transcript, transcript_segments, current_step, error
    """
    updates: dict = {"current_step": "transcribe"}
    audio_path = state.get("audio_path")

    if not audio_path:
        updates["error"] = "No audio file to transcribe"
        return updates

    try:
        # Phase 3: Groq Whisper integration
        # from groq import Groq
        # client = Groq(api_key=get_settings().groq_api_key)
        # response = client.audio.transcriptions.create(
        #     model="whisper-large-v3-turbo",
        #     file=open(audio_path, "rb"),
        #     response_format="verbose_json",
        # )
        # updates["transcript"] = response.text
        # updates["transcript_segments"] = [...]
        updates["error"] = "Transcription not yet implemented (Phase 3)"

    except Exception as e:
        updates["error"] = f"Transcription failed: {type(e).__name__}: {e}"

    return updates
