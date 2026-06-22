"""Tests for media services and updated nodes."""

import os
from unittest.mock import MagicMock, patch

import pytest

from backend.services.media import _is_valid_video_url, split_audio_if_needed
from backend.graph.nodes.resolve_input import resolve_input
from backend.graph.nodes.transcribe import transcribe


class TestUrlValidation:
    def test_youtube_watch(self):
        assert _is_valid_video_url("https://www.youtube.com/watch?v=abc123")

    def test_youtube_short(self):
        assert _is_valid_video_url("https://youtu.be/abc123")

    def test_vimeo(self):
        assert _is_valid_video_url("https://vimeo.com/123456")

    def test_vimeo_player(self):
        assert _is_valid_video_url("https://player.vimeo.com/video/123456")

    def test_invalid_url(self):
        assert not _is_valid_video_url("https://example.com/video")

    def test_random_string(self):
        assert not _is_valid_video_url("not-a-url")


class TestResolveInputUpdated:
    def test_text_still_works(self):
        state = {"job_id": "t1", "input_type": "text", "raw_input": "A" * 100}
        result = resolve_input(state)
        assert result["transcript"] == "A" * 100
        assert "error" not in result

    def test_audio_file_not_found(self):
        state = {"job_id": "t2", "input_type": "audio", "raw_input": "/nonexistent.mp3"}
        result = resolve_input(state)
        assert "error" in result
        assert "not found" in result["error"]

    def test_video_file_not_found(self):
        state = {"job_id": "t3", "input_type": "video", "raw_input": "/nonexistent.mp4"}
        result = resolve_input(state)
        assert "error" in result
        assert "not found" in result["error"]

    @patch("backend.graph.nodes.resolve_input.download_youtube_audio")
    def test_youtube_calls_download(self, mock_dl):
        mock_dl.return_value = "/tmp/audio.mp3"
        state = {
            "job_id": "t4",
            "input_type": "youtube_url",
            "raw_input": "https://youtube.com/watch?v=abc",
        }
        result = resolve_input(state)
        assert result["audio_path"] == "/tmp/audio.mp3"
        assert "error" not in result
        mock_dl.assert_called_once_with("https://youtube.com/watch?v=abc", "t4")

    @patch("backend.graph.nodes.resolve_input.download_youtube_audio", side_effect=ValueError("bad url"))
    def test_youtube_download_failure(self, mock_dl):
        state = {
            "job_id": "t5",
            "input_type": "youtube_url",
            "raw_input": "https://youtube.com/watch?v=abc",
        }
        result = resolve_input(state)
        assert "error" in result
        assert "ValueError" in result["error"]

    def test_audio_file_exists(self, tmp_path):
        audio = tmp_path / "test.mp3"
        audio.write_bytes(b"fake audio data")
        state = {"job_id": "t6", "input_type": "audio", "raw_input": str(audio)}
        result = resolve_input(state)
        assert result["audio_path"] == str(audio)
        assert "error" not in result


class TestTranscribeNode:
    def test_no_audio_path(self):
        result = transcribe({"job_id": "t1"})
        assert result["error"] == "No audio file to transcribe"

    @patch("backend.graph.nodes.transcribe.split_audio_if_needed")
    @patch("backend.graph.nodes.transcribe.Groq")
    @patch("backend.graph.nodes.transcribe.get_settings")
    def test_successful_transcription(self, mock_settings, mock_groq_cls, mock_split, tmp_path):
        # Setup
        audio = tmp_path / "test.mp3"
        audio.write_bytes(b"fake audio")
        mock_split.return_value = [str(audio)]

        mock_settings.return_value = MagicMock(
            groq_api_key="test-key",
            groq_whisper_model="whisper-large-v3-turbo",
        )

        # Mock Groq response
        mock_seg = MagicMock()
        mock_seg.start = 0.0
        mock_seg.end = 5.0
        mock_seg.text = "Hello world"

        mock_response = MagicMock()
        mock_response.text = "Hello world"
        mock_response.segments = [mock_seg]

        mock_client = MagicMock()
        mock_client.audio.transcriptions.create.return_value = mock_response
        mock_groq_cls.return_value = mock_client

        state = {"job_id": "t2", "audio_path": str(audio)}
        result = transcribe(state)

        assert result["transcript"] == "Hello world"
        assert len(result["transcript_segments"]) == 1
        assert result["transcript_segments"][0]["text"] == "Hello world"
        assert "error" not in result


class TestSplitAudio:
    def test_small_file_no_split(self, tmp_path):
        audio = tmp_path / "small.mp3"
        audio.write_bytes(b"x" * 1000)  # 1KB, well under 24MB
        result = split_audio_if_needed(str(audio))
        assert result == [str(audio)]
