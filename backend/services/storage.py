"""Local file storage (S3-ready interface)."""

from __future__ import annotations

from pathlib import Path

from backend.config import get_settings


def _uploads_dir() -> Path:
    d = Path(get_settings().storage_dir) / "uploads"
    d.mkdir(parents=True, exist_ok=True)
    return d


def save_upload(job_id: str, filename: str, content: bytes) -> str:
    """Save uploaded file, return local path."""
    job_dir = _uploads_dir() / job_id
    job_dir.mkdir(parents=True, exist_ok=True)
    dest = job_dir / filename
    dest.write_bytes(content)
    return str(dest)


def cleanup_job_files(job_id: str) -> None:
    """Delete intermediate files for a job."""
    import shutil

    job_dir = _uploads_dir() / job_id
    if job_dir.exists():
        shutil.rmtree(job_dir)
