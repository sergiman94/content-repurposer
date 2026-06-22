"""Node 3: Analyze transcript - extract themes, key points, quotes, structure."""

from __future__ import annotations

import json

from langchain_groq import ChatGroq

from backend.config import get_settings
from backend.graph.prompts.analyze import ANALYZE_SYSTEM, ANALYZE_USER
from backend.graph.state import RepurposeState

# Truncate transcript to stay within context limits
_MAX_TRANSCRIPT_CHARS = 12_000


def analyze(state: RepurposeState) -> dict:
    """Analyze transcript and extract structured content summary.

    Reads: transcript
    Writes: analysis, current_step, token_usage, error
    """
    updates: dict = {"current_step": "analyze"}
    transcript = state.get("transcript", "")

    if not transcript or len(transcript.strip()) < 50:
        updates["error"] = "Transcript too short or empty to analyze"
        return updates

    try:
        settings = get_settings()
        llm = ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            temperature=0.3,
        )

        response = llm.invoke([
            {"role": "system", "content": ANALYZE_SYSTEM},
            {"role": "user", "content": ANALYZE_USER.format(
                transcript=transcript[:_MAX_TRANSCRIPT_CHARS]
            )},
        ])

        # Parse structured JSON from LLM response
        raw = response.content.strip()
        # Strip markdown fences if the LLM added them
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3]
            raw = raw.strip()

        analysis = json.loads(raw)
        updates["analysis"] = analysis

        # Track token usage
        usage = response.response_metadata.get("token_usage", {})
        updates["token_usage"] = state.get("token_usage", []) + [{
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "model": settings.groq_model,
        }]

    except json.JSONDecodeError:
        updates["error"] = "Analysis LLM returned invalid JSON"
    except Exception as e:
        updates["error"] = f"Analysis failed: {type(e).__name__}: {e}"

    return updates
