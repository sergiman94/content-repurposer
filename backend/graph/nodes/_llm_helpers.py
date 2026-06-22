"""Shared helpers for LLM generation nodes."""

from __future__ import annotations

import json

from langchain_groq import ChatGroq

from backend.config import get_settings
from backend.graph.state import RepurposeState

_MAX_TRANSCRIPT_CHARS = 8_000


def run_generation(
    state: RepurposeState,
    system_prompt: str,
    user_prompt_template: str,
    step_name: str,
    output_key: str,
    parse_json: bool = False,
) -> dict:
    """Run a single LLM generation call. Used by all gen_* nodes.

    Args:
        state: Current graph state.
        system_prompt: System message for the LLM.
        user_prompt_template: User message template with {analysis} and {transcript} placeholders.
        step_name: Name for progress tracking (e.g. "gen_blog").
        output_key: State key to write the result to (e.g. "blog_post").
        parse_json: If True, parse response as JSON (for twitter thread).

    Returns:
        State updates dict. Generation failures are NON-FATAL (output_key = None).
    """
    updates: dict = {"current_step": step_name}

    try:
        settings = get_settings()
        llm = ChatGroq(
            model=settings.groq_model,
            api_key=settings.groq_api_key,
            temperature=0.7,
        )

        response = llm.invoke([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt_template.format(
                analysis=json.dumps(state.get("analysis", {}), indent=2),
                transcript=state.get("transcript", "")[:_MAX_TRANSCRIPT_CHARS],
            )},
        ])

        content = response.content.strip()

        if parse_json:
            # Strip markdown fences if present
            if content.startswith("```"):
                content = content.split("\n", 1)[1] if "\n" in content else content[3:]
                if content.endswith("```"):
                    content = content[:-3]
                content = content.strip()
            updates[output_key] = json.loads(content)
        else:
            updates[output_key] = content

        # Track token usage
        usage = response.response_metadata.get("token_usage", {})
        updates["token_usage"] = state.get("token_usage", []) + [{
            "prompt_tokens": usage.get("prompt_tokens", 0),
            "completion_tokens": usage.get("completion_tokens", 0),
            "model": settings.groq_model,
        }]

    except Exception:
        # Non-fatal: set output to None, don't set error
        updates[output_key] = None

    return updates
