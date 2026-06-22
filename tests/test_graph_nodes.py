"""Unit tests for graph nodes (no LLM calls)."""

from backend.graph.nodes.resolve_input import resolve_input
from backend.graph.nodes.finalize import finalize
from backend.graph.nodes.transcribe import transcribe


class TestResolveInput:
    def test_text_input_sets_transcript(self):
        state = {
            "job_id": "test-1",
            "input_type": "text",
            "raw_input": "A" * 100,
        }
        result = resolve_input(state)
        assert result["transcript"] == "A" * 100
        assert result["current_step"] == "resolve_input"
        assert "error" not in result

    def test_text_input_too_short(self):
        state = {
            "job_id": "test-2",
            "input_type": "text",
            "raw_input": "short",
        }
        result = resolve_input(state)
        assert "error" in result
        assert "too short" in result["error"]

    def test_youtube_not_yet_implemented(self):
        state = {
            "job_id": "test-3",
            "input_type": "youtube_url",
            "raw_input": "https://youtube.com/watch?v=abc",
        }
        result = resolve_input(state)
        assert "error" in result
        assert "not yet implemented" in result["error"]

    def test_unknown_input_type(self):
        state = {
            "job_id": "test-4",
            "input_type": "fax",
            "raw_input": "beep boop",
        }
        result = resolve_input(state)
        assert "error" in result
        assert "Unknown" in result["error"]


class TestTranscribe:
    def test_no_audio_path(self):
        state = {"job_id": "test-5"}
        result = transcribe(state)
        assert result["error"] == "No audio file to transcribe"


class TestFinalize:
    def test_completed(self):
        state = {"token_usage": []}
        result = finalize(state)
        assert result["current_step"] == "completed"
        assert result["completed_at"] is not None

    def test_failed(self):
        state = {"error": "something broke", "token_usage": []}
        result = finalize(state)
        assert result["current_step"] == "failed"
