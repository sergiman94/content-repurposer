"""LangGraph workflow definition for content repurposing.

Graph shape:
    resolve_input
        |
        |-- (text) ---------> analyze
        |-- (media/URL) ----> transcribe -> analyze
        |-- (error) --------> finalize
        |
    analyze
        |
        |--> gen_blog -> gen_twitter -> gen_linkedin -> gen_newsletter -> finalize -> END
        |-- (error) --> finalize -> END
"""

from langgraph.graph import END, StateGraph

from backend.graph.nodes import (
    analyze,
    finalize,
    gen_blog,
    gen_linkedin,
    gen_newsletter,
    gen_twitter,
    resolve_input,
    transcribe,
)
from backend.graph.state import RepurposeState


def _after_resolve(state: RepurposeState) -> str:
    """Route after resolve_input: skip transcription for text, bail on error."""
    if state.get("error"):
        return "finalize"
    if state["input_type"] == "text":
        return "analyze"
    return "transcribe"


def _check_error(state: RepurposeState) -> str:
    """After transcribe or analyze, check if we should bail."""
    if state.get("error"):
        return "finalize"
    return "continue"


def build_graph() -> StateGraph:
    """Build and compile the content repurposing graph."""
    g = StateGraph(RepurposeState)

    # Register nodes
    g.add_node("resolve_input", resolve_input)
    g.add_node("transcribe", transcribe)
    g.add_node("analyze", analyze)
    g.add_node("gen_blog", gen_blog)
    g.add_node("gen_twitter", gen_twitter)
    g.add_node("gen_linkedin", gen_linkedin)
    g.add_node("gen_newsletter", gen_newsletter)
    g.add_node("finalize", finalize)

    # Entry point
    g.set_entry_point("resolve_input")

    # After input resolution: text goes straight to analyze, media goes to transcribe
    g.add_conditional_edges("resolve_input", _after_resolve, {
        "transcribe": "transcribe",
        "analyze": "analyze",
        "finalize": "finalize",
    })

    # After transcription: check for errors
    g.add_conditional_edges("transcribe", _check_error, {
        "continue": "analyze",
        "finalize": "finalize",
    })

    # After analysis: check for errors, then start generation chain
    g.add_conditional_edges("analyze", _check_error, {
        "continue": "gen_blog",
        "finalize": "finalize",
    })

    # Sequential generation chain (each ~2s on Groq, total ~8-12s)
    g.add_edge("gen_blog", "gen_twitter")
    g.add_edge("gen_twitter", "gen_linkedin")
    g.add_edge("gen_linkedin", "gen_newsletter")
    g.add_edge("gen_newsletter", "finalize")

    # Finalize is terminal
    g.add_edge("finalize", END)

    return g.compile()


# Singleton compiled graph — import this to run jobs
repurpose_graph = build_graph()
