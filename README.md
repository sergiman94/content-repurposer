# Content Repurposer

Transform long-form content into a multi-format content package. Upload a video, audio file, YouTube URL, or paste a transcript — get back a blog post, Twitter/X thread, LinkedIn post, and newsletter section.

Built with **LangGraph** + **Groq** (Llama 3.3 70B + Whisper).

## How It Works

```
Input (video/audio/URL/text)
  |
  v
[resolve_input] --> [transcribe] --> [analyze] --> [gen_blog] --> [gen_twitter] --> [gen_linkedin] --> [gen_newsletter] --> [finalize]
  |                    |                |
  text skips here      Groq Whisper     Extracts themes,
                       large-v3-turbo   quotes, structure
```

- **Text input** skips straight to analysis
- **Media/URL input** downloads and transcribes first
- **Analysis** extracts structured JSON (title, key points, quotes, themes)
- **4 generation nodes** run sequentially (~2s each on Groq)
- Generation failures are **non-fatal** — if one output fails, the other 3 still work

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Redis
- ffmpeg (for video/audio processing)
- yt-dlp (for YouTube/Vimeo downloads)

### 1. Backend

```bash
# Clone and install
git clone https://github.com/sergiman94/content-repurposer.git
cd content-repurposer
pip install -e ".[all]"

# Configure
cp .env.example .env
# Edit .env and add your REPURPOSE_GROQ_API_KEY

# Start Redis
docker-compose up -d redis

# Start API
uvicorn backend.main:app --reload

# Start worker (separate terminal)
celery -A backend.worker.celery_app worker --loglevel=info
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

### 3. Or use Docker

```bash
docker-compose up
```

This starts Redis, the API, the Celery worker, and the frontend.

## API

```bash
# Create a job (text)
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{"input_type": "text", "content": "Your transcript here..."}'

# Create a job (YouTube URL)
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{"input_type": "youtube_url", "content": "https://youtube.com/watch?v=..."}'

# Upload a file
curl -X POST http://localhost:8000/api/jobs/upload \
  -F "file=@podcast.mp3" \
  -F "input_type=audio"

# Check status (poll until completed/failed)
curl http://localhost:8000/api/jobs/{job_id}

# Retry a failed job
curl -X POST http://localhost:8000/api/jobs/{job_id}/retry

# List jobs
curl http://localhost:8000/api/jobs

# Delete a job
curl -X DELETE http://localhost:8000/api/jobs/{job_id}
```

## Test

```bash
# Unit tests (no API keys needed)
pytest tests/ -v

# End-to-end with real Groq API
REPURPOSE_GROQ_API_KEY=gsk_... python run_test.py
```

## Tech Stack

| Layer | Technology |
|---|---|
| Agent workflow | LangGraph |
| LLM | Groq (Llama 3.3 70B) |
| Transcription | Groq Whisper (large-v3-turbo) |
| API | FastAPI |
| Task queue | Celery + Redis |
| Database | SQLite |
| Frontend | Next.js 15 + Tailwind CSS |
| Media | yt-dlp + ffmpeg |

## Cost

~$0.01-0.02 per job (Groq pricing). Whisper: $0.111/hour of audio.

## Project Structure

```
content-repurposer/
├── backend/
│   ├── api/            # FastAPI routes + schemas
│   ├── graph/          # LangGraph workflow
│   │   ├── nodes/      # 8 graph nodes
│   │   ├── prompts/    # LLM prompt templates
│   │   ├── state.py    # RepurposeState TypedDict
│   │   └── workflow.py # Graph definition
│   ├── services/       # Media + storage services
│   ├── db/             # SQLite CRUD
│   └── worker/         # Celery tasks
├── frontend/           # Next.js app
│   ├── src/app/        # Pages (home, job, history)
│   ├── src/components/ # UI components
│   └── src/lib/        # API client
└── tests/
```
