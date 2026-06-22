"""Node 4b: Generate Twitter/X thread."""

from backend.graph.nodes._llm_helpers import run_generation
from backend.graph.prompts.twitter import TWITTER_SYSTEM, TWITTER_USER
from backend.graph.state import RepurposeState


def gen_twitter(state: RepurposeState) -> dict:
    """Generate an 8-12 tweet thread as a JSON array of strings.

    Reads: analysis, transcript
    Writes: twitter_thread, current_step, token_usage
    """
    return run_generation(
        state,
        system_prompt=TWITTER_SYSTEM,
        user_prompt_template=TWITTER_USER,
        step_name="gen_twitter",
        output_key="twitter_thread",
        parse_json=True,
    )
