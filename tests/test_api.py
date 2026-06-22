"""API route tests (no Celery, no LLM calls)."""

import json
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.db.database import init_db, get_job
from backend.main import app


@pytest.fixture(autouse=True)
def setup_db(tmp_path, monkeypatch):
    """Use a temp SQLite database for each test."""
    monkeypatch.setattr("backend.db.database.get_settings", lambda: type(
        "S", (), {"storage_dir": str(tmp_path)}
    )())
    init_db()
    yield


@pytest.fixture
def client():
    return TestClient(app)


class TestHealth:
    def test_health(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


class TestCreateJob:
    @patch("backend.api.routes_jobs._try_dispatch")
    def test_create_text_job(self, mock_dispatch, client):
        r = client.post("/api/jobs", json={
            "input_type": "text",
            "content": "A" * 100,
        })
        assert r.status_code == 200
        data = r.json()
        assert data["status"] == "pending"
        assert data["job_id"]
        mock_dispatch.assert_called_once_with(data["job_id"])

    @patch("backend.api.routes_jobs._try_dispatch")
    def test_create_url_job(self, mock_dispatch, client):
        r = client.post("/api/jobs", json={
            "input_type": "youtube_url",
            "content": "https://youtube.com/watch?v=abc123",
        })
        assert r.status_code == 200
        assert r.json()["status"] == "pending"

    def test_empty_content_rejected(self, client):
        r = client.post("/api/jobs", json={
            "input_type": "text",
            "content": "",
        })
        assert r.status_code == 422


class TestGetJob:
    @patch("backend.api.routes_jobs._try_dispatch")
    @patch("backend.api.routes_jobs._get_live_status", return_value=None)
    def test_get_existing_job(self, mock_live, mock_dispatch, client):
        # Create a job
        r = client.post("/api/jobs", json={
            "input_type": "text",
            "content": "A" * 100,
        })
        job_id = r.json()["job_id"]

        # Fetch it
        r = client.get(f"/api/jobs/{job_id}")
        assert r.status_code == 200
        data = r.json()
        assert data["job_id"] == job_id
        assert data["status"] == "pending"
        assert data["input_type"] == "text"

    def test_get_missing_job(self, client):
        r = client.get("/api/jobs/nonexistent-id")
        assert r.status_code == 404


class TestListJobs:
    @patch("backend.api.routes_jobs._try_dispatch")
    def test_list_empty(self, mock_dispatch, client):
        r = client.get("/api/jobs")
        assert r.status_code == 200
        assert r.json() == []

    @patch("backend.api.routes_jobs._try_dispatch")
    def test_list_after_create(self, mock_dispatch, client):
        client.post("/api/jobs", json={"input_type": "text", "content": "A" * 100})
        client.post("/api/jobs", json={"input_type": "text", "content": "B" * 100})

        r = client.get("/api/jobs")
        assert r.status_code == 200
        assert len(r.json()) == 2


class TestDeleteJob:
    @patch("backend.api.routes_jobs._try_dispatch")
    def test_delete_existing(self, mock_dispatch, client):
        r = client.post("/api/jobs", json={"input_type": "text", "content": "A" * 100})
        job_id = r.json()["job_id"]

        r = client.delete(f"/api/jobs/{job_id}")
        assert r.status_code == 200

        r = client.get(f"/api/jobs/{job_id}")
        assert r.status_code == 404

    def test_delete_missing(self, client):
        r = client.delete("/api/jobs/nonexistent")
        assert r.status_code == 404
