"""Database layer tests."""

import pytest

from backend.db.database import (
    create_job,
    delete_job,
    get_job,
    init_db,
    list_jobs,
    update_job_outputs,
    update_job_status,
)


@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    monkeypatch.setattr("backend.db.database.get_settings", lambda: type(
        "S", (), {"storage_dir": str(tmp_path)}
    )())
    init_db()
    yield


class TestCRUD:
    def test_create_and_get(self):
        create_job("j1", "text", "inline", "2026-06-22T00:00:00Z", transcript="hello world")
        job = get_job("j1")
        assert job is not None
        assert job["id"] == "j1"
        assert job["input_type"] == "text"
        assert job["transcript"] == "hello world"
        assert job["status"] == "pending"

    def test_get_missing(self):
        assert get_job("nope") is None

    def test_list_jobs(self):
        create_job("j1", "text", "inline", "2026-06-22T00:00:00Z")
        create_job("j2", "audio", "/tmp/a.mp3", "2026-06-22T00:01:00Z")
        jobs = list_jobs()
        assert len(jobs) == 2
        # Most recent first
        assert jobs[0]["id"] == "j2"

    def test_update_status(self):
        create_job("j1", "text", "inline", "2026-06-22T00:00:00Z")
        update_job_status("j1", "running")
        assert get_job("j1")["status"] == "running"

    def test_update_outputs(self):
        create_job("j1", "text", "inline", "2026-06-22T00:00:00Z")
        update_job_outputs(
            job_id="j1",
            status="completed",
            blog_post="# Blog",
            twitter_thread=["tweet1", "tweet2"],
            linkedin_post="LinkedIn post",
            newsletter_section="Newsletter",
            transcript="the transcript",
            total_prompt_tokens=1000,
            total_completion_tokens=500,
            estimated_cost_usd=0.01,
            completed_at="2026-06-22T00:05:00Z",
        )
        job = get_job("j1")
        assert job["status"] == "completed"
        assert job["blog_post"] == "# Blog"
        assert job["total_prompt_tokens"] == 1000
        assert job["estimated_cost_usd"] == 0.01

    def test_delete(self):
        create_job("j1", "text", "inline", "2026-06-22T00:00:00Z")
        assert delete_job("j1") is True
        assert get_job("j1") is None

    def test_delete_missing(self):
        assert delete_job("nope") is False
