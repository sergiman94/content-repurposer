"""Celery tasks for running the LangGraph workflow."""

from __future__ import annotations

from datetime import datetime, timezone

import redis

from backend.config import get_settings
from backend.db.database import get_job, update_job_outputs, update_job_status
from backend.graph.state import RepurposeState
from backend.graph.workflow import repurpose_graph
from backend.services.storage import cleanup_job_files
from backend.worker.celery_app import app

# Groq pricing (Llama 3.3 70B)
_COST_PER_M_INPUT = 0.59
_COST_PER_M_OUTPUT = 0.79


def _redis_client() -> redis.Redis:
    return redis.Redis.from_url(get_settings().redis_url, decode_responses=True)


def _set_progress(r: redis.Redis, job_id: str, step: str) -> None:
    """Push current step to Redis for real-time polling."""
    r.set(f"job:{job_id}:status", step, ex=3600)


@app.task(bind=True, max_retries=1)
def run_repurpose_job(self, job_id: str) -> None:
    """Execute the LangGraph repurpose workflow for a job."""
    r = _redis_client()
    _set_progress(r, job_id, "starting")

    try:
        job = get_job(job_id)
        if not job:
            return

        update_job_status(job_id, "running")

        # Build initial state
        raw_input = job["transcript"] if job["input_type"] == "text" else job["input_ref"]

        initial_state: RepurposeState = {
            "job_id": job_id,
            "input_type": job["input_type"],
            "raw_input": raw_input,
            "current_step": "pending",
            "token_usage": [],
            "started_at": datetime.now(timezone.utc).isoformat(),
        }

        # Stream the graph to get per-node progress
        final_state = dict(initial_state)
        for event in repurpose_graph.stream(initial_state):
            for node_name, update in event.items():
                final_state.update(update)
                step = update.get("current_step", node_name)
                _set_progress(r, job_id, step)

        # Persist results
        _persist_results(job_id, final_state)
        _set_progress(r, job_id, final_state.get("current_step", "completed"))

    except Exception as e:
        update_job_status(job_id, "failed", error=f"{type(e).__name__}: {e}")
        _set_progress(r, job_id, "failed")
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=30)
    finally:
        cleanup_job_files(job_id)


def _persist_results(job_id: str, state: dict) -> None:
    """Write final graph state to SQLite."""
    usage = state.get("token_usage", [])
    total_in = sum(t.get("prompt_tokens", 0) for t in usage)
    total_out = sum(t.get("completion_tokens", 0) for t in usage)
    cost = (total_in * _COST_PER_M_INPUT + total_out * _COST_PER_M_OUTPUT) / 1_000_000

    status = "failed" if state.get("error") else "completed"

    update_job_outputs(
        job_id=job_id,
        status=status,
        blog_post=state.get("blog_post"),
        twitter_thread=state.get("twitter_thread"),
        linkedin_post=state.get("linkedin_post"),
        newsletter_section=state.get("newsletter_section"),
        transcript=state.get("transcript"),
        total_prompt_tokens=total_in,
        total_completion_tokens=total_out,
        estimated_cost_usd=round(cost, 6),
        completed_at=state.get("completed_at"),
        error=state.get("error"),
    )
