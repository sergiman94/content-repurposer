"""Pydantic request/response models for the API."""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    PENDING = "pending"
    RESOLVE_INPUT = "resolve_input"
    TRANSCRIBE = "transcribe"
    ANALYZE = "analyze"
    GEN_BLOG = "gen_blog"
    GEN_TWITTER = "gen_twitter"
    GEN_LINKEDIN = "gen_linkedin"
    GEN_NEWSLETTER = "gen_newsletter"
    COMPLETED = "completed"
    FAILED = "failed"


class CreateJobRequest(BaseModel):
    input_type: Literal["video", "audio", "youtube_url", "vimeo_url", "text"]
    content: str = Field(
        ...,
        min_length=1,
        description="URL for youtube_url/vimeo_url, raw text for text type.",
    )


class CreateJobResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: str


class JobOutputs(BaseModel):
    blog_post: str | None = None
    twitter_thread: list[str] | None = None
    linkedin_post: str | None = None
    newsletter_section: str | None = None


class TokenSummary(BaseModel):
    total_prompt_tokens: int
    total_completion_tokens: int
    total_tokens: int
    estimated_cost_usd: float


class JobDetailResponse(BaseModel):
    job_id: str
    status: str
    input_type: str
    outputs: JobOutputs | None = None
    error: str | None = None
    token_usage: TokenSummary | None = None
    created_at: str
    completed_at: str | None = None


class JobListItem(BaseModel):
    job_id: str
    input_type: str
    status: str
    error: str | None = None
    created_at: str
    completed_at: str | None = None
