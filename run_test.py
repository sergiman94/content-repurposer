#!/usr/bin/env python3
"""Test script: run the LangGraph workflow end-to-end with a text transcript.

Usage:
    REPURPOSE_GROQ_API_KEY=gsk_... python run_test.py
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from backend.graph.state import RepurposeState
from backend.graph.workflow import repurpose_graph

SAMPLE = Path("tests/fixtures/sample_transcript.txt").read_text()


def main():
    print("=" * 60)
    print("Content Repurposer - Test Run")
    print("=" * 60)

    initial_state: RepurposeState = {
        "job_id": "test-001",
        "input_type": "text",
        "raw_input": SAMPLE,
        "current_step": "pending",
        "token_usage": [],
        "started_at": datetime.now(timezone.utc).isoformat(),
    }

    print("\nRunning graph...\n")

    # Stream to see progress
    final_state = {}
    for event in repurpose_graph.stream(initial_state):
        for node_name, update in event.items():
            step = update.get("current_step", node_name)
            print(f"  [{step}] {node_name} completed")
            final_state.update(update)

    print("\n" + "=" * 60)

    if final_state.get("error"):
        print(f"ERROR: {final_state['error']}")
        sys.exit(1)

    # Print results
    print("\nANALYSIS:")
    print(json.dumps(final_state.get("analysis", {}), indent=2)[:500])

    print("\n" + "-" * 40)
    print("BLOG POST (first 300 chars):")
    print((final_state.get("blog_post") or "FAILED")[:300])

    print("\n" + "-" * 40)
    print("TWITTER THREAD:")
    thread = final_state.get("twitter_thread") or []
    for i, tweet in enumerate(thread[:3], 1):
        print(f"  {i}. {tweet[:100]}...")
    if len(thread) > 3:
        print(f"  ... ({len(thread)} tweets total)")

    print("\n" + "-" * 40)
    print("LINKEDIN POST (first 300 chars):")
    print((final_state.get("linkedin_post") or "FAILED")[:300])

    print("\n" + "-" * 40)
    print("NEWSLETTER (first 300 chars):")
    print((final_state.get("newsletter_section") or "FAILED")[:300])

    # Token summary
    print("\n" + "=" * 60)
    usage = final_state.get("token_usage", [])
    total_in = sum(t.get("prompt_tokens", 0) for t in usage)
    total_out = sum(t.get("completion_tokens", 0) for t in usage)
    print(f"TOKENS: {total_in} input + {total_out} output = {total_in + total_out} total")
    print(f"ESTIMATED COST: ${(total_in * 0.59 + total_out * 0.79) / 1_000_000:.4f}")
    print(f"STATUS: {final_state.get('current_step')}")


if __name__ == "__main__":
    main()
