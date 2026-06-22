# Content Repurposer

## What This Project Is

Content repurposing pipeline that takes long-form content (video, audio, YouTube URL, or raw transcript) and produces a content package: blog post, Twitter/X thread, LinkedIn post, and newsletter section. Built with LangGraph + Groq.

## Key Commands

- `pip install -e ".[all]"` -- Install for development
- `docker-compose up -d` -- Start Redis
- `REPURPOSE_GROQ_API_KEY=gsk_... python run_test.py` -- Test the graph end-to-end with sample transcript
- `uvicorn backend.main:app --reload` -- Start API server
- `celery -A backend.worker.celery_app worker --loglevel=info` -- Start Celery worker
- `ruff check backend/ tests/` -- Lint
- `pytest` -- Run tests

## Architecture

- **LangGraph workflow** (`backend/graph/workflow.py`): the core pipeline
- **State** (`backend/graph/state.py`): `RepurposeState` TypedDict flows through the graph
- **Nodes** (`backend/graph/nodes/`): each node reads/writes specific state keys
- **Prompts** (`backend/graph/prompts/`): one template per output type
- **API** (`backend/api/`): FastAPI REST endpoints
- **Worker** (`backend/worker/`): Celery tasks for async job processing

## Graph Shape

```
resolve_input -> [text: analyze, media: transcribe -> analyze]
analyze -> gen_blog -> gen_twitter -> gen_linkedin -> gen_newsletter -> finalize -> END
```

- Fatal errors (input/transcribe/analyze) skip to finalize
- Generation node failures are non-fatal (other outputs still generated)

## LLM

- Groq (`llama-3.3-70b-versatile`) for content generation
- Groq Whisper (`whisper-large-v3-turbo`) for transcription
- Cost: ~$0.01-0.02 per job

## Implementation Phases

1. Project skeleton + LangGraph workflow (text input only)
2. FastAPI + Celery + Redis (async job processing)
3. Media pipeline (yt-dlp, ffmpeg, Groq Whisper)
4. Next.js frontend
5. Polish (error handling, audio chunking, token tracking)
