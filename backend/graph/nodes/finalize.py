"""Node 5: Assemble final outputs and compute token summary."""

from __future__ import annotations

from datetime import datetime, timezone

from backend.graph.state import RepurposeState


def finalize(state: RepurposeState) -> dict:
    """Mark job as completed or failed, record completion time.

    Reads: error, token_usage
    Writes: current_step, completed_at
    """
    has_error = bool(state.get("error"))
    step = "failed" if has_error else "completed"

    return {
        "current_step": step,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
