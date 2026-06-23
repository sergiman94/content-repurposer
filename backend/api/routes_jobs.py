"""Job API routes."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, UploadFile, Form
from typing import Literal

from backend.api.schemas import (
    CreateJobRequest,
    CreateJobResponse,
    JobDetailResponse,
    JobListItem,
    JobOutputs,
    JobStatus,
    TokenSummary,
)
from backend.db.database import create_job, delete_job, get_job, list_jobs, update_job_status

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


def _try_dispatch(job_id: str) -> None:
    """Dispatch Celery task if worker is available, otherwise log warning."""
    try:
        from backend.worker.tasks import run_repurpose_job

        run_repurpose_job.delay(job_id)
    except Exception:
        # Worker not running — job stays pending, can be retried
        pass


@router.post("", response_model=CreateJobResponse)
async def create_job_endpoint(request: CreateJobRequest):
    """Create a new repurpose job from JSON (text or URL input)."""
    job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    transcript = request.content if request.input_type == "text" else None
    input_ref = "inline" if request.input_type == "text" else request.content

    create_job(
        job_id=job_id,
        input_type=request.input_type,
        input_ref=input_ref,
        created_at=now,
        transcript=transcript,
    )

    _try_dispatch(job_id)

    return CreateJobResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="Job created and queued for processing",
    )


@router.post("/upload", response_model=CreateJobResponse)
async def create_job_upload(
    file: UploadFile,
    input_type: Literal["video", "audio"] = Form(...),
):
    """Create a new repurpose job from file upload (video/audio)."""
    job_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc).isoformat()

    # Save uploaded file
    from backend.services.storage import save_upload

    file_content = await file.read()
    file_path = save_upload(job_id, file.filename or "upload", file_content)

    create_job(
        job_id=job_id,
        input_type=input_type,
        input_ref=file_path,
        created_at=now,
    )

    _try_dispatch(job_id)

    return CreateJobResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="File uploaded and queued for processing",
    )


@router.get("/{job_id}", response_model=JobDetailResponse)
async def get_job_endpoint(job_id: str):
    """Get job status and results."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Check Redis for live progress (faster than SQLite for in-flight jobs)
    live_status = _get_live_status(job_id)
    status = live_status or job["status"]

    # Build outputs if completed
    outputs = None
    token_usage = None
    if status == "completed":
        twitter = None
        if job["twitter_thread"]:
            try:
                twitter = json.loads(job["twitter_thread"])
            except json.JSONDecodeError:
                twitter = None

        outputs = JobOutputs(
            blog_post=job["blog_post"],
            twitter_thread=twitter,
            linkedin_post=job["linkedin_post"],
            newsletter_section=job["newsletter_section"],
        )

        total_tokens = job["total_prompt_tokens"] + job["total_completion_tokens"]
        cost = (
            job["total_prompt_tokens"] * 0.59 + job["total_completion_tokens"] * 0.79
        ) / 1_000_000
        token_usage = TokenSummary(
            total_prompt_tokens=job["total_prompt_tokens"],
            total_completion_tokens=job["total_completion_tokens"],
            total_tokens=total_tokens,
            estimated_cost_usd=round(cost, 6),
        )

    return JobDetailResponse(
        job_id=job["id"],
        status=status,
        input_type=job["input_type"],
        outputs=outputs,
        error=job["error"],
        token_usage=token_usage,
        created_at=job["created_at"],
        completed_at=job["completed_at"],
    )


@router.get("", response_model=list[JobListItem])
async def list_jobs_endpoint(limit: int = 20, offset: int = 0):
    """List recent jobs."""
    jobs = list_jobs(limit=min(limit, 100), offset=offset)
    return [
        JobListItem(
            job_id=j["id"],
            input_type=j["input_type"],
            status=j["status"],
            error=j["error"],
            created_at=j["created_at"],
            completed_at=j["completed_at"],
        )
        for j in jobs
    ]


@router.post("/{job_id}/retry", response_model=CreateJobResponse)
async def retry_job_endpoint(job_id: str):
    """Retry a failed job."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job["status"] not in ("failed",):
        raise HTTPException(status_code=400, detail="Only failed jobs can be retried")

    update_job_status(job_id, "pending", error=None)
    _try_dispatch(job_id)

    return CreateJobResponse(
        job_id=job_id,
        status=JobStatus.PENDING,
        message="Job requeued for processing",
    )


@router.delete("/{job_id}")
async def delete_job_endpoint(job_id: str):
    """Delete a job and its outputs."""
    if not delete_job(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job deleted"}


def _get_live_status(job_id: str) -> str | None:
    """Check Redis for real-time progress. Returns None if Redis unavailable."""
    try:
        import redis

        r = redis.Redis.from_url("redis://localhost:6379/0", decode_responses=True)
        return r.get(f"job:{job_id}:status")
    except Exception:
        return None
