"""Test the graph structure (no LLM calls — just validates edges and routing)."""

from unittest.mock import patch
from datetime import datetime, timezone

from backend.graph.workflow import _after_resolve, _check_error


class TestRouting:
    def test_text_skips_transcription(self):
        state = {"input_type": "text"}
        assert _after_resolve(state) == "analyze"

    def test_audio_goes_to_transcribe(self):
        state = {"input_type": "audio"}
        assert _after_resolve(state) == "transcribe"

    def test_youtube_goes_to_transcribe(self):
        state = {"input_type": "youtube_url"}
        assert _after_resolve(state) == "transcribe"

    def test_error_goes_to_finalize(self):
        state = {"input_type": "text", "error": "bad input"}
        assert _after_resolve(state) == "finalize"

    def test_check_error_continues(self):
        state = {}
        assert _check_error(state) == "continue"

    def test_check_error_bails(self):
        state = {"error": "something broke"}
        assert _check_error(state) == "finalize"
