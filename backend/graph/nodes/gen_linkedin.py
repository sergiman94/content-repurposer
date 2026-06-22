"""Node 4c: Generate LinkedIn post."""

from backend.graph.nodes._llm_helpers import run_generation
from backend.graph.prompts.linkedin import LINKEDIN_SYSTEM, LINKEDIN_USER
from backend.graph.state import RepurposeState


def gen_linkedin(state: RepurposeState) -> dict:
    """Generate a 200-400 word professional LinkedIn post.

    Reads: analysis, transcript
    Writes: linkedin_post, current_step, token_usage
    """
    return run_generation(
        state,
        system_prompt=LINKEDIN_SYSTEM,
        user_prompt_template=LINKEDIN_USER,
        step_name="gen_linkedin",
        output_key="linkedin_post",
    )
