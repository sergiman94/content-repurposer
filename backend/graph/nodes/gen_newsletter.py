"""Node 4d: Generate newsletter section."""

from backend.graph.nodes._llm_helpers import run_generation
from backend.graph.prompts.newsletter import NEWSLETTER_SYSTEM, NEWSLETTER_USER
from backend.graph.state import RepurposeState


def gen_newsletter(state: RepurposeState) -> dict:
    """Generate a 300-word newsletter section.

    Reads: analysis, transcript
    Writes: newsletter_section, current_step, token_usage
    """
    return run_generation(
        state,
        system_prompt=NEWSLETTER_SYSTEM,
        user_prompt_template=NEWSLETTER_USER,
        step_name="gen_newsletter",
        output_key="newsletter_section",
    )
