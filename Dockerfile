FROM python:3.11-slim

# System deps for yt-dlp and ffmpeg
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install yt-dlp
RUN pip install --no-cache-dir yt-dlp

WORKDIR /app

# Install Python deps
COPY pyproject.toml .
RUN pip install --no-cache-dir ".[all]"

# Copy source
COPY backend/ backend/
COPY tests/ tests/
COPY run_test.py .

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
