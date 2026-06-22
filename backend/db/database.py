"""SQLite database for job persistence."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from backend.config import get_settings

_SCHEMA = """
CREATE TABLE IF NOT EXISTS jobs (
    id TEXT PRIMARY KEY,
    input_type TEXT NOT NULL,
    input_ref TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    error TEXT,
    blog_post TEXT,
    twitter_thread TEXT,
    linkedin_post TEXT,
    newsletter_section TEXT,
    transcript TEXT,
    total_prompt_tokens INTEGER DEFAULT 0,
    total_completion_tokens INTEGER DEFAULT 0,
    estimated_cost_usd REAL DEFAULT 0.0,
    created_at TEXT NOT NULL,
    completed_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_created ON jobs(created_at DESC);
"""


def _db_path() -> str:
    storage = Path(get_settings().storage_dir)
    storage.mkdir(parents=True, exist_ok=True)
    return str(storage / "repurposer.db")


def init_db() -> None:
    with sqlite3.connect(_db_path()) as conn:
        conn.executescript(_SCHEMA)


@contextmanager
def get_conn():
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def create_job(
    job_id: str,
    input_type: str,
    input_ref: str,
    created_at: str,
    transcript: str | None = None,
) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO jobs (id, input_type, input_ref, status, created_at, transcript) "
            "VALUES (?, ?, ?, 'pending', ?, ?)",
            (job_id, input_type, input_ref, created_at, transcript),
        )


def get_job(job_id: str) -> dict | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        if row is None:
            return None
        return dict(row)


def list_jobs(limit: int = 20, offset: int = 0) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, input_type, status, error, created_at, completed_at "
            "FROM jobs ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
        return [dict(r) for r in rows]


def update_job_status(job_id: str, status: str, error: str | None = None) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE jobs SET status = ?, error = ? WHERE id = ?",
            (status, error, job_id),
        )


def update_job_outputs(
    job_id: str,
    status: str,
    blog_post: str | None,
    twitter_thread: list[str] | None,
    linkedin_post: str | None,
    newsletter_section: str | None,
    transcript: str | None,
    total_prompt_tokens: int,
    total_completion_tokens: int,
    estimated_cost_usd: float,
    completed_at: str | None,
    error: str | None = None,
) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE jobs SET status=?, blog_post=?, twitter_thread=?, linkedin_post=?, "
            "newsletter_section=?, transcript=?, total_prompt_tokens=?, "
            "total_completion_tokens=?, estimated_cost_usd=?, completed_at=?, error=? "
            "WHERE id=?",
            (
                status,
                blog_post,
                json.dumps(twitter_thread) if twitter_thread else None,
                linkedin_post,
                newsletter_section,
                transcript,
                total_prompt_tokens,
                total_completion_tokens,
                estimated_cost_usd,
                completed_at,
                error,
                job_id,
            ),
        )


def delete_job(job_id: str) -> bool:
    with get_conn() as conn:
        cursor = conn.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        return cursor.rowcount > 0
