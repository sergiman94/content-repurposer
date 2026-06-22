"""LangGraph state schema for the content repurposing workflow."""

from __future__ import annotations

from typing import Literal, TypedDict


class TokenUsage(TypedDict):
    prompt_tokens: int
    completion_tokens: int
    model: str


class RepurposeState(TypedDict, total=False):
    # --- Input (set once at start) ---
    job_id: str
    input_type: Literal["video", "audio", "youtube_url", "vimeo_url", "text"]
    raw_input: str  # URL, file path, or pasted text

    # --- Media pipeline ---
    audio_path: str | None
    transcript: str | None
    transcript_segments: list[dict]  # Whisper segments with timestamps

    # --- Analysis ---
    analysis: dict  # {title, summary, key_points, quotes, themes, tone}

    # --- Generated outputs ---
    blog_post: str | None
    twitter_thread: list[str] | None
    linkedin_post: str | None
    newsletter_section: str | None

    # --- Metadata ---
    current_step: str  # For progress tracking
    error: str | None  # Set on failure; conditional edges check this
    token_usage: list[TokenUsage]  # Appended by each LLM node
    started_at: str
    completed_at: str | None
